"""Unit tests for LLM client asynchronous invoke method."""

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


class TestLLMClientAsyncInvoke:
    """Test asynchronous invoke method."""

    @pytest.mark.asyncio
    async def test_ainvoke_success(self, api_config):
        """Test successful async LLM invocation."""
        mock_llm = MagicMock()
        mock_response = MagicMock(content="Async response")

        async def mock_ainvoke(prompt):
            return mock_response

        mock_llm.ainvoke = mock_ainvoke

        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                response = await client.ainvoke("Test prompt")
                assert response == "Async response"

    @pytest.mark.asyncio
    async def test_ainvoke_empty_prompt(self, api_config):
        """Test async invoke with empty prompt."""
        mock_llm = MagicMock()
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(ValueError, match="Prompt cannot be empty"):
                    await client.ainvoke("")

    @pytest.mark.asyncio
    async def test_ainvoke_whitespace_prompt(self, api_config):
        """Test async invoke with whitespace-only prompt."""
        mock_llm = MagicMock()
        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(ValueError, match="Prompt cannot be empty"):
                    await client.ainvoke("   ")

    @pytest.mark.asyncio
    async def test_ainvoke_non_string_content(self, api_config):
        """Test async invoke with non-string response content."""
        mock_llm = MagicMock()
        mock_response = MagicMock(content={"dict": "content"})

        async def mock_ainvoke(prompt):
            return mock_response

        mock_llm.ainvoke = mock_ainvoke

        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(APIError, match="not a string"):
                    await client.ainvoke("Test prompt")

    @pytest.mark.asyncio
    async def test_ainvoke_rate_limit_error(self, api_config):
        """Test async invoke handles rate limit errors."""
        mock_llm = MagicMock()

        async def mock_ainvoke(prompt):
            raise Exception("Rate limit exceeded")

        mock_llm.ainvoke = mock_ainvoke

        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(RateLimitError):
                    await client.ainvoke("Test prompt")

    @pytest.mark.asyncio
    async def test_ainvoke_generic_error(self, api_config):
        """Test async invoke handles generic errors."""
        mock_llm = MagicMock()

        async def mock_ainvoke(prompt):
            raise Exception("Generic API error")

        mock_llm.ainvoke = mock_ainvoke

        with patch("shield_pr.core.llm_client.ChatGoogleGenerativeAI", return_value=mock_llm):
            with patch("shield_pr.core.llm_client.setup_cache"):
                client = LLMClient(api_config)
                with pytest.raises(APIError):
                    await client.ainvoke("Test prompt")
