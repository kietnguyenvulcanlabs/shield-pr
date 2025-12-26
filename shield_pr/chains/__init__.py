"""Review chain implementations."""

from typing import Any
from shield_pr.chains.base import BaseReviewChain
from shield_pr.chains.platforms.android_chain import AndroidReviewChain
from shield_pr.chains.platforms.ios_chain import IOSReviewChain
from shield_pr.chains.platforms.ai_ml_chain import AiMlReviewChain
from shield_pr.chains.platforms.frontend_chain import FrontendReviewChain
from shield_pr.chains.platforms.backend_chain import BackendReviewChain
from shield_pr.chains.universal_chain import UniversalReviewChain
from shield_pr.chains.synthesis_chain import SynthesisChain


# Chain registry for factory pattern
CHAIN_REGISTRY = {
    "android": AndroidReviewChain,
    "ios": IOSReviewChain,
    "ai-ml": AiMlReviewChain,
    "frontend": FrontendReviewChain,
    "backend": BackendReviewChain,
}


def get_chain(platform: str, llm_client: Any, depth: str = "standard") -> BaseReviewChain:
    """Get review chain for specified platform.

    Args:
        platform: Platform name (android, ios, ai-ml, frontend, backend)
        llm_client: LLM client for chain execution
        depth: Review depth (quick, standard, deep)

    Returns:
        Platform-specific review chain instance

    Raises:
        ValueError: If platform is not supported
    """
    chain_class = CHAIN_REGISTRY.get(platform.lower())
    if not chain_class:
        raise ValueError(
            f"Unsupported platform: {platform}. "
            f"Supported platforms: {', '.join(CHAIN_REGISTRY.keys())}"
        )
    # Type ignore needed because chain_class is a class type from registry
    return chain_class(llm_client, depth)  # type: ignore[abstract]


__all__ = [
    "BaseReviewChain",
    "AndroidReviewChain",
    "IOSReviewChain",
    "AiMlReviewChain",
    "FrontendReviewChain",
    "BackendReviewChain",
    "UniversalReviewChain",
    "SynthesisChain",
    "CHAIN_REGISTRY",
    "get_chain",
]
