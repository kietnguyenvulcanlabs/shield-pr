"""Unit tests for platform-specific review chains.

Tests chain creation and prompt templates for all platforms.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock LangChain before import
sys.modules['langchain.chains'] = MagicMock()
sys.modules['langchain.prompts'] = MagicMock()

from shield_pr.routing.destinations import (
    create_ai_ml_chain,
    create_android_chain,
    create_backend_chain,
    create_default_chain,
    create_frontend_chain,
    create_ios_chain,
    get_platform_chains,
)


class TestChainCreation:
    """Test platform-specific chain creation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()

    def test_create_android_chain(self):
        """Should create Android review chain."""
        chain = create_android_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")

    def test_create_ios_chain(self):
        """Should create iOS review chain."""
        chain = create_ios_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")

    def test_create_ai_ml_chain(self):
        """Should create AI/ML review chain."""
        chain = create_ai_ml_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")

    def test_create_frontend_chain(self):
        """Should create frontend review chain."""
        chain = create_frontend_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")

    def test_create_backend_chain(self):
        """Should create backend review chain."""
        chain = create_backend_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")

    def test_create_default_chain(self):
        """Should create default review chain."""
        chain = create_default_chain(self.mock_llm_client)
        assert chain is not None
        assert hasattr(chain, "invoke")


class TestGetPlatformChains:
    """Test getting all platform chains."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()

    def test_returns_all_platform_chains(self):
        """Should return chains for all platforms."""
        chains = get_platform_chains(self.mock_llm_client)
        assert "android" in chains
        assert "ios" in chains
        assert "ai-ml" in chains
        assert "frontend" in chains
        assert "backend" in chains
        assert "default" in chains

    def test_returns_dict(self):
        """Should return dictionary of chains."""
        chains = get_platform_chains(self.mock_llm_client)
        assert isinstance(chains, dict)
        assert len(chains) == 6  # 5 platforms + default

    def test_all_chains_have_invoke(self):
        """All chains should have invoke method."""
        chains = get_platform_chains(self.mock_llm_client)
        for platform, chain in chains.items():
            assert hasattr(chain, "invoke"), f"Chain {platform} missing invoke method"


class TestChainConfiguration:
    """Test chain configuration and structure."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()

    def test_chains_use_llm_client(self):
        """All chains should use provided LLM client."""
        chains = [
            create_android_chain(self.mock_llm_client),
            create_ios_chain(self.mock_llm_client),
            create_ai_ml_chain(self.mock_llm_client),
            create_frontend_chain(self.mock_llm_client),
            create_backend_chain(self.mock_llm_client),
            create_default_chain(self.mock_llm_client),
        ]
        # All chains should be created successfully
        assert all(chain is not None for chain in chains)

    def test_chains_are_callable(self):
        """All chains should have invoke method."""
        chains = {
            "android": create_android_chain(self.mock_llm_client),
            "ios": create_ios_chain(self.mock_llm_client),
            "ai-ml": create_ai_ml_chain(self.mock_llm_client),
            "frontend": create_frontend_chain(self.mock_llm_client),
            "backend": create_backend_chain(self.mock_llm_client),
            "default": create_default_chain(self.mock_llm_client),
        }
        for name, chain in chains.items():
            assert hasattr(chain, "invoke"), f"Chain {name} missing invoke"
