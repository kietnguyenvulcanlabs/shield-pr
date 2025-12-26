"""Gemini LLM client with retry logic and caching.

Provides abstraction layer over LangChain's Gemini integration with
exponential backoff, rate limiting handling, and token tracking.
"""

from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config.models import APIConfig
from ..core.errors import APIError, RateLimitError
from ..utils.logger import logger
from .cache import setup_cache


class LLMClient:
    """LLM client wrapper with retry logic and error handling."""

    def __init__(self, config: APIConfig):
        """Initialize LLM client with configuration.

        Args:
            config: API configuration with credentials and parameters
        """
        self.config = config

        # Set up caching
        setup_cache()

        # Initialize Gemini client
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=config.model,
                google_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
            )
            logger.debug(f"Initialized Gemini client with model {config.model}")
        except Exception as e:
            raise APIError(f"Failed to initialize LLM client: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
        reraise=True,
    )
    def invoke(self, prompt: str) -> str:
        """Execute LLM call with retry logic.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            LLM response content as string

        Raises:
            APIError: If LLM call fails after retries
            RateLimitError: If rate limit is exceeded
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            logger.debug(f"Invoking LLM with {len(prompt)} chars")
            response = self.llm.invoke(prompt)

            if not response or not hasattr(response, "content"):
                raise APIError("Invalid response from LLM")

            content = response.content
            if isinstance(content, str):
                logger.debug(f"Received response: {len(content)} chars")
                return content
            raise APIError("Response content is not a string")

        except Exception as e:
            error_msg = str(e).lower()

            # Check for rate limiting
            if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry with backoff")
                raise RateLimitError(f"Rate limit exceeded: {e}")

            # Generic API error
            logger.error(f"LLM invocation failed: {e}")
            raise APIError(f"LLM call failed: {e}")

    async def ainvoke(self, prompt: str) -> str:
        """Async version of invoke.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            LLM response content as string

        Raises:
            APIError: If LLM call fails after retries
            RateLimitError: If rate limit is exceeded
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            logger.debug(f"Async invoking LLM with {len(prompt)} chars")
            response = await self.llm.ainvoke(prompt)

            if not response or not hasattr(response, "content"):
                raise APIError("Invalid response from LLM")

            content = response.content
            if isinstance(content, str):
                logger.debug(f"Received async response: {len(content)} chars")
                return content
            raise APIError("Response content is not a string")

        except Exception as e:
            error_msg = str(e).lower()

            if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry with backoff")
                raise RateLimitError(f"Rate limit exceeded: {e}")

            logger.error(f"Async LLM invocation failed: {e}")
            raise APIError(f"Async LLM call failed: {e}")
