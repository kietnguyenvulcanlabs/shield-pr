"""Unit tests for LLM client synchronous invoke method."""

from unittest.mock import MagicMock, patch

import pytest

from shield_pr.config.models import APIConfig
from shield_pr.core.errors import APIError, RateLimitError
from shield_pr.core.llm_client import LLMClient


@pytest.fixture
def api_config():
    """Provide test API configuration."""
    return APIConfig(
        api_key="test_api_key_1234567890",
        model="gemini-1.5-pro",
        temperature=0.35,
        max_tokens=2048,
    )


@pytest.fixture
def mock_llm():
    """Provide mock LLM instance."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Test response")
    return mock


class TestLLMClientInvoke:
    """Test synchronous invoke method."""

    def test_invoke_success(self, api_config, mock_llm):
        """Test successful LLM invocation."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                response = client.invoke("Test prompt")
                assert response == "Test response"
                mock_llm.invoke.assert_called_once_with("Test prompt")

    def test_invoke_empty_prompt(self, api_config, mock_llm):
        """Test invoke with empty prompt."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(ValueError, match="Prompt cannot be empty"):
                    client.invoke("")

    def test_invoke_whitespace_prompt(self, api_config, mock_llm):
        """Test invoke with whitespace-only prompt."""
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(ValueError, match="Prompt cannot be empty"):
                    client.invoke("   ")

    def test_invoke_invalid_response(self, api_config, mock_llm):
        """Test invoke with invalid response."""
        mock_llm.invoke.return_value = None
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(APIError, match="Invalid response"):
                    client.invoke("Test prompt")

    def test_invoke_non_string_content(self, api_config, mock_llm):
        """Test invoke with non-string response content."""
        mock_llm.invoke.return_value = MagicMock(content=["list", "content"])
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(APIError, match="not a string"):
                    client.invoke("Test prompt")

    def test_invoke_rate_limit_error(self, api_config, mock_llm):
        """Test invoke handles rate limit errors."""
        mock_llm.invoke.side_effect = Exception("Rate limit exceeded")
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                    client.invoke("Test prompt")

    def test_invoke_quota_error(self, api_config, mock_llm):
        """Test invoke handles quota errors."""
        mock_llm.invoke.side_effect = Exception("Quota exceeded")
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(RateLimitError):
                    client.invoke("Test prompt")

    def test_invoke_429_error(self, api_config, mock_llm):
        """Test invoke handles 429 status errors."""
        mock_llm.invoke.side_effect = Exception("HTTP 429 error")
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(RateLimitError):
                    client.invoke("Test prompt")

    def test_invoke_generic_error(self, api_config, mock_llm):
        """Test invoke handles generic errors."""
        mock_llm.invoke.side_effect = Exception("Generic API error")
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(APIError, match="LLM call failed"):
                    client.invoke("Test prompt")
