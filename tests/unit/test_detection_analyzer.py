"""Unit tests for file analyzer - extension and content detection.

Tests extension-based and content-based platform detection.
"""

from shield_pr.detection.file_analyzer import FileAnalyzer


class TestExtensionDetection:
    """Test extension-based platform detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FileAnalyzer()

    def test_detect_kotlin_android(self):
        """Should detect Android from .kt extension."""
        platform, confidence = self.analyzer.detect_by_extension("MainActivity.kt")
        assert platform == "android"
        assert confidence == 1.0

    def test_detect_swift_ios(self):
        """Should detect iOS from .swift extension."""
        platform, confidence = self.analyzer.detect_by_extension("ViewController.swift")
        assert platform == "ios"
        assert confidence == 1.0

    def test_detect_vue_frontend(self):
        """Should detect frontend from .vue extension."""
        platform, confidence = self.analyzer.detect_by_extension("App.vue")
        assert platform == "frontend"
        assert confidence == 1.0

    def test_detect_go_backend(self):
        """Should detect backend from .go extension."""
        platform, confidence = self.analyzer.detect_by_extension("server.go")
        assert platform == "backend"
        assert confidence == 0.9

    def test_detect_ipynb_ai_ml(self):
        """Should detect AI/ML from .ipynb extension."""
        platform, confidence = self.analyzer.detect_by_extension("notebook.ipynb")
        assert platform == "ai-ml"
        assert confidence == 0.95

    def test_ambiguous_python_extension(self):
        """Should return lower confidence for ambiguous .py extension."""
        platform, confidence = self.analyzer.detect_by_extension("script.py")
        assert platform in ["backend", "ai-ml"]
        assert confidence <= 0.5

    def test_ambiguous_javascript_extension(self):
        """Should return lower confidence for ambiguous .js extension."""
        platform, confidence = self.analyzer.detect_by_extension("app.js")
        assert platform in ["frontend", "backend"]
        assert confidence <= 0.5

    def test_unknown_extension(self):
        """Should return None for unknown extension."""
        platform, confidence = self.analyzer.detect_by_extension("file.xyz")
        assert platform is None
        assert confidence == 0.0

    def test_no_extension(self):
        """Should return None for file without extension."""
        platform, confidence = self.analyzer.detect_by_extension("Makefile")
        assert platform is None
        assert confidence == 0.0

    def test_case_insensitive_extension(self):
        """Should handle uppercase extensions."""
        platform, confidence = self.analyzer.detect_by_extension("File.KT")
        assert platform == "android"


class TestContentDetection:
    """Test content-based platform detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FileAnalyzer()

    def test_detect_android_from_imports(self):
        """Should detect Android from Android imports."""
        content = """import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
}
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "android"
        assert confidence > 0.2

    def test_detect_ios_from_imports(self):
        """Should detect iOS from UIKit imports."""
        content = """import UIKit
import SwiftUI

class ViewController: UIViewController {
}
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "ios"
        assert confidence > 0.25

    def test_detect_ai_ml_from_imports(self):
        """Should detect AI/ML from ML library imports."""
        content = """import tensorflow as tf
import torch
import numpy as np

model = tf.keras.Sequential()
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "ai-ml"
        assert confidence > 0.3

    def test_detect_frontend_from_react(self):
        """Should detect frontend from React code."""
        content = """import React, { useState, useEffect } from 'react';

function Component() {
    const [state, setState] = useState(null);
}
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "frontend"
        assert confidence > 0.3

    def test_detect_backend_from_fastapi(self):
        """Should detect backend from FastAPI code."""
        content = """from fastapi import FastAPI

app = FastAPI()

@app.get("/endpoint")
def handler():
    pass
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "backend"
        assert confidence > 0.3

    def test_empty_content(self):
        """Should return None for empty content."""
        platform, confidence = self.analyzer.detect_by_content("")
        assert platform is None
        assert confidence == 0.0

    def test_whitespace_only_content(self):
        """Should return None for whitespace-only content."""
        platform, confidence = self.analyzer.detect_by_content("   \n\n  \t  ")
        assert platform is None
        assert confidence == 0.0

    def test_combined_signals_boost_confidence(self):
        """Should combine imports, keywords, and config mentions."""
        content = """import tensorflow as tf
import torch
import numpy as np

# Train neural network model
model = tf.keras.Sequential()
dataset = load_data()
"""
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "ai-ml"
        assert confidence > 0.5

    def test_config_file_mentions(self):
        """Should boost confidence when config files mentioned."""
        content = """
        // Reference to package.json and tsconfig.json
        import React from 'react';
        """
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "frontend"

    def test_performance_limit_large_files(self):
        """Should limit analysis to first 500 lines."""
        lines = ["import tensorflow as tf"] + ["# comment"] * 999
        content = "\n".join(lines)
        platform, confidence = self.analyzer.detect_by_content(content)
        assert platform == "ai-ml"
