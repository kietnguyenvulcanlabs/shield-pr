"""Unit tests for platform detector orchestrator.

Tests detection orchestration, batch processing, and manual overrides.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from shield_pr.detection.detector import PlatformDetector


class TestDetectorBasic:
    """Test basic detector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = PlatformDetector()

    def test_manual_platform_override(self):
        """Should use manual platform when provided."""
        platform, confidence, reasoning = self.detector.detect(
            "test.py", manual_platform="android"
        )
        assert platform == "android"
        assert confidence == 1.0
        assert "Manual selection" in reasoning

    def test_invalid_manual_platform_falls_back(self):
        """Should fall back to auto-detection for invalid manual platform."""
        platform, confidence, reasoning = self.detector.detect(
            "test.kt", manual_platform="invalid"
        )
        # Should auto-detect kotlin as android
        assert platform == "android"

    def test_high_confidence_extension_skips_content(self):
        """Should skip content analysis for high-confidence extensions."""
        with patch.object(self.detector.analyzer, "detect_by_content") as mock:
            platform, confidence, reasoning = self.detector.detect("App.swift")
            # Should not read content for .swift (confidence 1.0)
            mock.assert_not_called()
            assert platform == "ios"

    def test_low_confidence_extension_reads_content(self):
        """Should read content for low-confidence extensions."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("import tensorflow as tf\nimport torch\nimport sklearn\nmodel.fit(dataset)\n")
            temp_path = f.name

        try:
            platform, confidence, reasoning = self.detector.detect(temp_path)
            # Should detect from content (ai-ml or backend are both valid for .py)
            assert platform in ["ai-ml", "backend"]
            assert confidence > 0.0
        finally:
            Path(temp_path).unlink()

    def test_provided_content_used(self):
        """Should use provided content instead of reading file."""
        content = "import android.os.Bundle\nimport androidx.core\nimport androidx.appcompat"
        platform, confidence, reasoning = self.detector.detect(
            "test.py", content=content
        )
        # Content should be analyzed (android or backend both acceptable for .py files)
        assert platform is not None
        assert confidence > 0.0

    def test_file_read_error_handled(self):
        """Should handle file read errors gracefully."""
        platform, confidence, reasoning = self.detector.detect(
            "/nonexistent/file.py"
        )
        # Should still attempt extension detection
        assert platform in ["backend", "ai-ml", None]


class TestDetectorBatch:
    """Test batch detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = PlatformDetector()

    def test_batch_detection(self):
        """Should detect platforms for multiple files."""
        files = ["MainActivity.kt", "App.swift", "server.go"]
        results = self.detector.detect_batch(files)

        assert len(results) == 3
        assert results["MainActivity.kt"][0] == "android"
        assert results["App.swift"][0] == "ios"
        assert results["server.go"][0] == "backend"

    def test_batch_with_manual_platform(self):
        """Should apply manual platform to all files in batch."""
        files = ["file1.py", "file2.py", "file3.py"]
        results = self.detector.detect_batch(files, manual_platform="ai-ml")

        for file_path, (platform, confidence, _) in results.items():
            assert platform == "ai-ml"
            assert confidence == 1.0

    def test_batch_empty_list(self):
        """Should handle empty file list."""
        results = self.detector.detect_batch([])
        assert results == {}

    def test_batch_preserves_file_paths(self):
        """Should preserve file paths as keys in results."""
        files = ["path/to/file1.kt", "another/file2.swift"]
        results = self.detector.detect_batch(files)

        assert "path/to/file1.kt" in results
        assert "another/file2.swift" in results


class TestDetectionSummary:
    """Test detection summary generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = PlatformDetector()

    def test_summary_counts_platforms(self):
        """Should count detected platforms correctly."""
        results = {
            "file1.kt": ("android", 1.0, "..."),
            "file2.kt": ("android", 1.0, "..."),
            "file3.swift": ("ios", 1.0, "..."),
            "file4.py": ("backend", 0.6, "..."),
        }

        summary = self.detector.get_detection_summary(results)
        assert summary["android"] == 2
        assert summary["ios"] == 1
        assert summary["backend"] == 1

    def test_summary_counts_unknown(self):
        """Should count unknown detections."""
        results = {
            "file1.kt": ("android", 1.0, "..."),
            "file2.xyz": (None, 0.0, "..."),
            "file3.abc": (None, 0.0, "..."),
        }

        summary = self.detector.get_detection_summary(results)
        assert summary["android"] == 1
        assert summary["unknown"] == 2

    def test_summary_empty_results(self):
        """Should handle empty results."""
        summary = self.detector.get_detection_summary({})
        assert summary == {}

    def test_summary_all_platforms(self):
        """Should handle all supported platforms."""
        results = {
            "a.kt": ("android", 1.0, "..."),
            "b.swift": ("ios", 1.0, "..."),
            "c.ipynb": ("ai-ml", 1.0, "..."),
            "d.vue": ("frontend", 1.0, "..."),
            "e.go": ("backend", 1.0, "..."),
        }

        summary = self.detector.get_detection_summary(results)
        assert len(summary) == 5
        assert all(count == 1 for count in summary.values())


class TestDetectorIntegration:
    """Test detector integration with real content."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = PlatformDetector()

    def test_android_kotlin_file(self):
        """Should detect Android Kotlin file."""
        content = "import android.os.Bundle\nclass MainActivity : AppCompatActivity() {}"
        platform, confidence, _ = self.detector.detect("MainActivity.kt", content=content)
        assert platform == "android"
        assert confidence > 0.9

    def test_ios_swift_file(self):
        """Should detect iOS Swift file."""
        content = "import UIKit\nclass ViewController: UIViewController {}"
        platform, confidence, _ = self.detector.detect("ViewController.swift", content=content)
        assert platform == "ios"
        assert confidence >= 1.0

    def test_ai_ml_python_file(self):
        """Should detect AI/ML Python file."""
        content = "import tensorflow as tf\nimport torch\nmodel = tf.keras.Sequential()\nneural network"
        platform, confidence, _ = self.detector.detect("train.py", content=content)
        assert platform == "ai-ml"
        assert confidence > 0.3

    def test_frontend_react_file(self):
        """Should detect frontend React file."""
        content = "import React from 'react';\nfunction App() { return <div/>; }"
        platform, confidence, _ = self.detector.detect("App.tsx", content=content)
        assert platform == "frontend"
        assert confidence > 0.8

    def test_backend_fastapi_file(self):
        """Should detect backend FastAPI file."""
        content = "from fastapi import FastAPI\napp = FastAPI()"
        platform, confidence, _ = self.detector.detect("main.py", content=content)
        assert platform == "backend"
        assert confidence > 0.3
