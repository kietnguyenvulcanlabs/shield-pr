"""Unit tests for LLM client initialization."""

from unittest.mock import patch

import pytest

from shield_pr.config.models import APIConfig
from shield_pr.core.errors import APIError
from shield_pr.core.llm_client import LLMClient


@pytest.fixture
def api_config():
    """Provide test API configuration."""
    return APIConfig(
        api_key="test_api_key_1234567890",
        model="gemini-1.5-pro",
        temperature=0.35,
        max_tokens=2048,
        timeout=30,
        retry_attempts=3,
        retry_min_wait=2,
        retry_max_wait=10,
    )


class TestLLMClientInit:
    """Test LLM client initialization."""

    def test_init_success(self, api_config):
        """Test successful client initialization."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI"):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                assert client.config == api_config

    def test_init_with_config_parameters(self, api_config):
        """Test initialization uses config parameters."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI") as mock_chat:
            with patch("shield_pr.core.llm_client.setup_cache"):
                LLMClient(api_config)
                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["model"] == "gemini-1.5-pro"
                assert call_kwargs["google_api_key"] == "test_api_key_1234567890"
                assert call_kwargs["temperature"] == 0.35
                assert call_kwargs["max_tokens"] == 2048
                assert call_kwargs["timeout"] == 30

    def test_init_failure(self, api_config):
        """Test initialization failure handling."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI") as mock_chat:
            mock_chat.side_effect = Exception("API initialization failed")
            with patch("shield_pr.core.llm_client.setup_cache"):
                with pytest.raises(APIError, match="Failed to initialize"):
                    LLMClient(api_config)

    def test_init_sets_up_cache(self, api_config):
        """Test initialization sets up caching."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI"):
            with patch("shield_pr.core.llm_client.setup_cache") as mock_cache:
                LLMClient(api_config)
                mock_cache.assert_called_once()
