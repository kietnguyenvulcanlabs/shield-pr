"""Unit tests for cache configuration."""

from unittest.mock import MagicMock, patch

import pytest

from shield_pr.core.cache import clear_cache, setup_cache


class TestSetupCache:
    """Test cache setup functionality."""

    def test_setup_cache_memory(self):
        """Test setting up in-memory cache."""
        with patch("shield_pr.core.cache.InMemoryCache") as mock_cache_cls:
            with patch("shield_pr.core.cache.set_llm_cache") as mock_set:
                mock_cache = MagicMock()
                mock_cache_cls.return_value = mock_cache
                setup_cache("memory")
                mock_cache_cls.assert_called_once()
                mock_set.assert_called_once_with(mock_cache)

    def test_setup_cache_default(self):
        """Test default cache type is memory."""
        with patch("shield_pr.core.cache.InMemoryCache"):
            with patch("shield_pr.core.cache.set_llm_cache") as mock_set:
                setup_cache()
                mock_set.assert_called_once()

    def test_setup_cache_unsupported_type(self):
        """Test unsupported cache type raises error."""
        with pytest.raises(ValueError, match="Unsupported cache type"):
            setup_cache("redis")

    def test_setup_cache_invalid_type(self):
        """Test invalid cache type raises error."""
        with pytest.raises(ValueError, match="Unsupported cache type"):
            setup_cache("invalid_cache")


class TestClearCache:
    """Test cache clearing functionality."""

    def test_clear_cache(self):
        """Test clearing and reinitializing cache."""
        with patch("shield_pr.core.cache.set_llm_cache") as mock_set:
            with patch("shield_pr.core.cache.setup_cache") as mock_setup:
                clear_cache()
                assert mock_set.call_count == 1
                mock_set.assert_called_with(None)
                mock_setup.assert_called_once()

    def test_clear_cache_calls_setup(self):
        """Test clear cache reinitializes with setup."""
        with patch("shield_pr.core.cache.InMemoryCache"):
            with patch("shield_pr.core.cache.set_llm_cache"):
                with patch("shield_pr.core.cache.setup_cache") as mock_setup:
                    clear_cache()
                    mock_setup.assert_called_once()
