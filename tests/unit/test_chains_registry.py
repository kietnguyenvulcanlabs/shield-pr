"""Tests for chain registry and get_chain factory."""

import pytest
from unittest.mock import MagicMock
from shield_pr.chains import (
    get_chain,
    CHAIN_REGISTRY,
    AndroidReviewChain,
    IOSReviewChain,
    AiMlReviewChain,
    FrontendReviewChain,
    BackendReviewChain,
)


class TestChainRegistry:
    """Tests for CHAIN_REGISTRY configuration."""

    def test_registry_contains_all_platforms(self):
        """Test registry includes all supported platforms."""
        expected_platforms = ["android", "ios", "ai-ml", "frontend", "backend"]

        for platform in expected_platforms:
            assert platform in CHAIN_REGISTRY

    def test_registry_maps_to_correct_classes(self):
        """Test registry maps platform names to correct chain classes."""
        assert CHAIN_REGISTRY["android"] == AndroidReviewChain
        assert CHAIN_REGISTRY["ios"] == IOSReviewChain
        assert CHAIN_REGISTRY["ai-ml"] == AiMlReviewChain
        assert CHAIN_REGISTRY["frontend"] == FrontendReviewChain
        assert CHAIN_REGISTRY["backend"] == BackendReviewChain

    def test_registry_has_exactly_five_platforms(self):
        """Test registry contains exactly 5 platforms."""
        assert len(CHAIN_REGISTRY) == 5


class TestGetChainFactory:
    """Tests for get_chain factory function."""

    def test_get_chain_android(self):
        """Test get_chain returns AndroidReviewChain for 'android'."""
        llm_client = MagicMock()
        chain = get_chain("android", llm_client, depth="standard")

        assert isinstance(chain, AndroidReviewChain)
        assert chain.platform == "android"
        assert chain.depth == "standard"

    def test_get_chain_ios(self):
        """Test get_chain returns IOSReviewChain for 'ios'."""
        llm_client = MagicMock()
        chain = get_chain("ios", llm_client, depth="deep")

        assert isinstance(chain, IOSReviewChain)
        assert chain.platform == "ios"
        assert chain.depth == "deep"

    def test_get_chain_ai_ml(self):
        """Test get_chain returns AiMlReviewChain for 'ai-ml'."""
        llm_client = MagicMock()
        chain = get_chain("ai-ml", llm_client, depth="quick")

        assert isinstance(chain, AiMlReviewChain)
        assert chain.platform == "ai-ml"
        assert chain.depth == "quick"

    def test_get_chain_frontend(self):
        """Test get_chain returns FrontendReviewChain for 'frontend'."""
        llm_client = MagicMock()
        chain = get_chain("frontend", llm_client)

        assert isinstance(chain, FrontendReviewChain)
        assert chain.platform == "frontend"

    def test_get_chain_backend(self):
        """Test get_chain returns BackendReviewChain for 'backend'."""
        llm_client = MagicMock()
        chain = get_chain("backend", llm_client)

        assert isinstance(chain, BackendReviewChain)
        assert chain.platform == "backend"

    def test_get_chain_case_insensitive(self):
        """Test get_chain is case-insensitive."""
        llm_client = MagicMock()

        chain_lower = get_chain("android", llm_client)
        chain_upper = get_chain("ANDROID", llm_client)
        chain_mixed = get_chain("Android", llm_client)

        assert isinstance(chain_lower, AndroidReviewChain)
        assert isinstance(chain_upper, AndroidReviewChain)
        assert isinstance(chain_mixed, AndroidReviewChain)

    def test_get_chain_unsupported_platform_raises_error(self):
        """Test get_chain raises ValueError for unsupported platform."""
        llm_client = MagicMock()

        with pytest.raises(ValueError, match="Unsupported platform: unsupported"):
            get_chain("unsupported", llm_client)

    def test_get_chain_error_lists_supported_platforms(self):
        """Test error message lists all supported platforms."""
        llm_client = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            get_chain("invalid", llm_client)

        error_message = str(exc_info.value)
        assert "android" in error_message
        assert "ios" in error_message
        assert "ai-ml" in error_message
        assert "frontend" in error_message
        assert "backend" in error_message

    def test_get_chain_default_depth(self):
        """Test get_chain uses default depth when not specified."""
        llm_client = MagicMock()
        chain = get_chain("android", llm_client)

        assert chain.depth == "standard"

    def test_get_chain_with_all_depth_levels(self):
        """Test get_chain works with all depth levels."""
        llm_client = MagicMock()

        for depth in ["quick", "standard", "deep"]:
            chain = get_chain("android", llm_client, depth=depth)
            assert chain.depth == depth

    def test_get_chain_passes_llm_client(self):
        """Test get_chain correctly passes LLM client to chain."""
        llm_client = MagicMock()
        chain = get_chain("ios", llm_client)

        assert chain.llm == llm_client

    def test_get_chain_initializes_stages(self):
        """Test get_chain returns fully initialized chain with stages."""
        llm_client = MagicMock()
        chain = get_chain("frontend", llm_client)

        assert chain.stages is not None
        assert len(chain.stages) > 0
        assert "architecture" in chain.stages

    def test_get_chain_all_platforms_integration(self):
        """Test get_chain works for all registered platforms."""
        llm_client = MagicMock()

        for platform in CHAIN_REGISTRY.keys():
            chain = get_chain(platform, llm_client, depth="standard")

            # Verify chain is properly initialized
            assert chain is not None
            assert chain.platform == platform
            assert chain.depth == "standard"
            assert chain.llm == llm_client
            assert hasattr(chain, "execute")
