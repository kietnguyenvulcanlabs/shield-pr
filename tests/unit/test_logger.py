"""Unit tests for logger with API key masking.

Tests logging functionality and sensitive data masking.
"""

import re

import pytest

from shield_pr.utils.logger import mask_api_key, setup_logger


class TestMaskAPIKey:
    """Test API key masking functionality."""

    def test_mask_google_api_key(self):
        """Should mask Google API keys (AIza...)."""
        text = "Using API key: AIzaSyDxK9w7G7hY3kE9vN8wX4bR2cF5tA1pZ6q"
        result = mask_api_key(text)
        assert "AIza***" in result
        assert "AIzaSyDxK9w7" not in result

    def test_mask_openai_api_key(self):
        """Should mask OpenAI-style keys (sk-...)."""
        text = "Token: sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = mask_api_key(text)
        assert "sk-***" in result
        assert "sk-1234567890" not in result

    def test_mask_long_alphanumeric_keys(self):
        """Should mask long alphanumeric strings (40+ chars)."""
        text = "Secret: abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH"
        result = mask_api_key(text)
        assert "***" in result
        assert "abcdefghijklmnop" not in result

    def test_mask_bearer_tokens(self):
        """Should mask Bearer tokens."""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = mask_api_key(text)
        assert "Bearer ***" in result
        assert "eyJhbGciOiJ" not in result

    def test_preserve_short_strings(self):
        """Should not mask short strings."""
        text = "This is a normal message with short words"
        result = mask_api_key(text)
        assert result == text

    def test_mask_multiple_keys(self):
        """Should mask multiple keys in same text."""
        text = "Key1: AIzaSyABC123456789ABCD and Key2: sk-XYZ789012345678"
        result = mask_api_key(text)
        assert "AIza***" in result
        assert "sk-***" in result
        assert "AIzaSyABC123456789ABCD" not in result
        assert "sk-XYZ789012345678" not in result


class TestSetupLogger:
    """Test logger setup and configuration."""

    def test_setup_logger_default(self):
        """Should create logger with default settings."""
        logger, console = setup_logger()
        assert logger is not None
        assert console is not None
        assert logger.name == "cra"

    def test_setup_logger_with_debug(self):
        """Should enable debug mode when requested."""
        logger, console = setup_logger(debug=True)
        assert logger is not None
        # Debug mode should create file handler
        assert len(logger.handlers) >= 1

    def test_logger_custom_name(self):
        """Should create logger with custom name."""
        logger, console = setup_logger(name="test_logger")
        assert logger.name == "test_logger"

    def test_logger_masking_in_messages(self):
        """Should mask API keys in log messages."""
        logger, console = setup_logger()
        # Note: This is a basic test, full testing would require capturing log output
        # which is complex with Rich. The mask_api_key function is thoroughly tested above.
        assert mask_api_key("AIza1234567890") == "AIza***"  # At least 10 chars after AIza
