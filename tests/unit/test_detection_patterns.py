"""Unit tests for platform detection patterns.

Tests pattern definitions, platform validation, and pattern retrieval.
"""

import re

import pytest

from shield_pr.detection.patterns import (
    CONFIDENCE_THRESHOLDS,
    EXTENSION_WEIGHTS,
    IMPORT_PATTERNS,
    KEYWORD_PATTERNS,
    PLATFORM_PATTERNS,
    get_platform_pattern,
    get_supported_platforms,
    is_valid_platform,
)


class TestPlatformPatterns:
    """Test platform pattern definitions."""

    def test_all_platforms_have_required_keys(self):
        """Should have extensions, keywords, imports, files for each platform."""
        required_keys = {"extensions", "keywords", "imports", "files"}
        for platform, patterns in PLATFORM_PATTERNS.items():
            assert required_keys.issubset(
                patterns.keys()
            ), f"Platform {platform} missing required keys"

    def test_android_patterns(self):
        """Should have correct Android patterns."""
        android = PLATFORM_PATTERNS["android"]
        assert ".kt" in android["extensions"]
        assert "android" in android["keywords"]
        assert "AndroidManifest.xml" in android["files"]

    def test_ios_patterns(self):
        """Should have correct iOS patterns."""
        ios = PLATFORM_PATTERNS["ios"]
        assert ".swift" in ios["extensions"]
        assert "UIKit" in ios["imports"]
        assert "Podfile" in ios["files"]

    def test_ai_ml_patterns(self):
        """Should have correct AI/ML patterns."""
        ai_ml = PLATFORM_PATTERNS["ai-ml"]
        assert ".ipynb" in ai_ml["extensions"]
        assert "tensorflow" in ai_ml["keywords"]

    def test_frontend_patterns(self):
        """Should have correct frontend patterns."""
        frontend = PLATFORM_PATTERNS["frontend"]
        assert ".tsx" in frontend["extensions"]
        assert "react" in frontend["keywords"]

    def test_backend_patterns(self):
        """Should have correct backend patterns."""
        backend = PLATFORM_PATTERNS["backend"]
        assert ".go" in backend["extensions"]
        assert "fastapi" in backend["keywords"]


class TestConfidenceThresholds:
    """Test confidence threshold definitions."""

    def test_all_thresholds_defined(self):
        """Should have all required confidence thresholds."""
        required = {
            "extension_high",
            "extension_medium",
            "extension_low",
            "content_high",
            "content_medium",
            "content_low",
            "manual",
        }
        assert set(CONFIDENCE_THRESHOLDS.keys()) == required

    def test_threshold_ranges(self):
        """Should have thresholds in valid range [0, 1]."""
        for name, value in CONFIDENCE_THRESHOLDS.items():
            assert 0.0 <= value <= 1.0, f"Threshold {name} out of range: {value}"

    def test_manual_threshold_highest(self):
        """Manual selection should have highest confidence."""
        assert CONFIDENCE_THRESHOLDS["manual"] == 1.0


class TestExtensionWeights:
    """Test extension weight definitions."""

    def test_unique_extensions_high_weight(self):
        """Unique extensions should have high confidence weights."""
        assert EXTENSION_WEIGHTS[".kt"]["android"] == 1.0
        assert EXTENSION_WEIGHTS[".swift"]["ios"] == 1.0
        assert EXTENSION_WEIGHTS[".vue"]["frontend"] == 1.0

    def test_ambiguous_extensions_multiple_platforms(self):
        """Ambiguous extensions should map to multiple platforms."""
        assert len(EXTENSION_WEIGHTS[".py"]) >= 2
        assert len(EXTENSION_WEIGHTS[".js"]) >= 2

    def test_ambiguous_extensions_low_weight(self):
        """Ambiguous extensions should have lower weights."""
        for platform, weight in EXTENSION_WEIGHTS[".py"].items():
            assert weight <= 0.5

    def test_all_weights_in_range(self):
        """All weights should be in [0, 1] range."""
        for ext, platforms in EXTENSION_WEIGHTS.items():
            for platform, weight in platforms.items():
                assert 0.0 <= weight <= 1.0


class TestPatternRegex:
    """Test regex pattern validity."""

    def test_keyword_patterns_valid_regex(self):
        """Keyword patterns should be valid regex strings."""
        for platform, pattern in KEYWORD_PATTERNS.items():
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid keyword regex for {platform}: {e}")

    def test_import_patterns_valid_regex(self):
        """Import patterns should be valid regex strings."""
        for platform, pattern in IMPORT_PATTERNS.items():
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid import regex for {platform}: {e}")

    def test_all_platforms_have_patterns(self):
        """Should have keyword and import patterns for all platforms."""
        platforms = set(PLATFORM_PATTERNS.keys())
        assert set(KEYWORD_PATTERNS.keys()) == platforms
        assert set(IMPORT_PATTERNS.keys()) == platforms


class TestPlatformFunctions:
    """Test platform utility functions."""

    def test_get_platform_pattern_valid(self):
        """Should return pattern dict for valid platform."""
        result = get_platform_pattern("android")
        assert isinstance(result, dict)
        assert "extensions" in result

    def test_get_platform_pattern_invalid_raises_error(self):
        """Should raise KeyError for invalid platform."""
        with pytest.raises(KeyError):
            get_platform_pattern("invalid-platform")

    def test_get_supported_platforms_returns_list(self):
        """Should return list of all platforms."""
        result = get_supported_platforms()
        assert isinstance(result, list)
        expected = ["android", "ios", "ai-ml", "frontend", "backend"]
        assert set(result) == set(expected)

    def test_is_valid_platform_accepts_valid(self):
        """Should return True for valid platforms."""
        valid = ["android", "ios", "ai-ml", "frontend", "backend"]
        for platform in valid:
            assert is_valid_platform(platform) is True

    def test_is_valid_platform_rejects_invalid(self):
        """Should return False for invalid platforms."""
        invalid = ["", "invalid", "web", "Android", "IOS"]
        for platform in invalid:
            assert is_valid_platform(platform) is False

    def test_is_valid_platform_case_sensitive(self):
        """Should be case-sensitive."""
        assert is_valid_platform("android") is True
        assert is_valid_platform("Android") is False
