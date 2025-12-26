"""Unit tests for input validators.

Tests validation logic for file paths, model names, and review configs.
"""

import tempfile
from pathlib import Path

import pytest

from shield_pr.core.errors import ValidationError
from shield_pr.utils.validators import (
    validate_file_path,
    validate_model_name,
    validate_output_format,
    validate_platforms,
    validate_review_depth,
)


class TestValidateFilePath:
    """Test file path validation."""

    def test_valid_existing_file(self):
        """Should validate existing file successfully."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            result = validate_file_path(temp_path, must_exist=True)
            assert isinstance(result, Path)
            assert result.exists()
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file_when_required(self):
        """Should raise error for nonexistent file when must_exist=True."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_file_path("/tmp/nonexistent-file.txt", must_exist=True)

    def test_nonexistent_file_when_not_required(self):
        """Should accept nonexistent file when must_exist=False."""
        result = validate_file_path("/tmp/future-file.txt", must_exist=False)
        assert isinstance(result, Path)

    def test_empty_path(self):
        """Should raise error for empty path."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_path("")

    def test_whitespace_only_path(self):
        """Should raise error for whitespace-only path."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_path("   ")

    def test_expand_user_path(self):
        """Should expand ~ in path."""
        result = validate_file_path("~/test.txt", must_exist=False)
        assert "~" not in str(result)


class TestValidateModelName:
    """Test model name validation."""

    def test_valid_model_names(self):
        """Should accept valid model names."""
        valid_names = [
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            "claude-3-opus",
            "gpt-4",
        ]
        for name in valid_names:
            assert validate_model_name(name) == name

    def test_empty_model_name(self):
        """Should raise error for empty model name."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_model_name("")

    def test_invalid_characters(self):
        """Should raise error for invalid characters."""
        with pytest.raises(ValidationError, match="Invalid model name"):
            validate_model_name("Model_With_Uppercase")

    def test_whitespace_trimming(self):
        """Should trim whitespace from model name."""
        result = validate_model_name("  gemini-1.5-pro  ")
        assert result == "gemini-1.5-pro"


class TestValidateReviewDepth:
    """Test review depth validation."""

    def test_valid_depths(self):
        """Should accept valid depth values."""
        for depth in ["quick", "standard", "deep"]:
            assert validate_review_depth(depth) == depth

    def test_case_insensitive(self):
        """Should handle case-insensitive depth values."""
        assert validate_review_depth("QUICK") == "quick"
        assert validate_review_depth("Standard") == "standard"

    def test_invalid_depth(self):
        """Should raise error for invalid depth."""
        with pytest.raises(ValidationError, match="Invalid review depth"):
            validate_review_depth("ultra-deep")

    def test_whitespace_handling(self):
        """Should handle whitespace in depth values."""
        assert validate_review_depth("  standard  ") == "standard"


class TestValidatePlatforms:
    """Test platform validation."""

    def test_valid_platforms(self):
        """Should accept valid platform names."""
        platforms = ["android", "ios", "backend"]
        result = validate_platforms(platforms)
        assert result == platforms

    def test_case_normalization(self):
        """Should normalize platform names to lowercase."""
        platforms = ["Android", "IOS", "Backend"]
        result = validate_platforms(platforms)
        assert result == ["android", "ios", "backend"]

    def test_invalid_platform(self):
        """Should raise error for invalid platform."""
        with pytest.raises(ValidationError, match="Invalid platforms"):
            validate_platforms(["android", "windows"])

    def test_whitespace_trimming(self):
        """Should trim whitespace from platform names."""
        platforms = ["  android  ", "ios  "]
        result = validate_platforms(platforms)
        assert result == ["android", "ios"]

    def test_all_valid_platforms(self):
        """Should accept all valid platform combinations."""
        all_platforms = ["android", "ios", "ai-ml", "frontend", "backend"]
        result = validate_platforms(all_platforms)
        assert result == all_platforms


class TestValidateOutputFormat:
    """Test output format validation."""

    def test_valid_formats(self):
        """Should accept valid output formats."""
        formats = ["markdown", "json", "github", "gitlab", "slack"]
        for fmt in formats:
            assert validate_output_format(fmt) == fmt

    def test_case_normalization(self):
        """Should normalize format to lowercase."""
        assert validate_output_format("MARKDOWN") == "markdown"
        assert validate_output_format("Json") == "json"

    def test_invalid_format(self):
        """Should raise error for invalid format."""
        with pytest.raises(ValidationError, match="Invalid output format"):
            validate_output_format("xml")

    def test_whitespace_trimming(self):
        """Should trim whitespace from format."""
        assert validate_output_format("  json  ") == "json"
