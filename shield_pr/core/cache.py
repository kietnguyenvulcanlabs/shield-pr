"""LangChain cache configuration for token efficiency.

Implements InMemoryCache with future extensibility for Redis or disk caching.
"""

from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

from ..utils.logger import logger


def setup_cache(cache_type: str = "memory") -> None:
    """Configure LangChain caching layer.

    Args:
        cache_type: Type of cache to use ('memory', 'redis', 'disk')
                   Currently only 'memory' is implemented

    Raises:
        ValueError: If cache_type is not supported
    """
    if cache_type == "memory":
        cache = InMemoryCache()
        set_llm_cache(cache)
        logger.debug("Initialized InMemoryCache for LLM responses")
    else:
        raise ValueError(f"Unsupported cache type: {cache_type}")


def clear_cache() -> None:
    """Clear the current LLM cache."""
    set_llm_cache(None)
    setup_cache()  # Reinitialize
    logger.debug("Cleared LLM cache")
