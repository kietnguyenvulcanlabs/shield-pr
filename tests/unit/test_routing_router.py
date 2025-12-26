"""Unit tests for review router.

Tests routing logic, batch processing, and chain selection.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock LangChain before import
sys.modules['langchain.chains'] = MagicMock()
sys.modules['langchain.prompts'] = MagicMock()

from shield_pr.routing.router import ReviewRouter


class TestRouterInitialization:
    """Test router initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()

    def test_router_initializes(self):
        """Should initialize router with LLM client."""
        router = ReviewRouter(self.mock_llm_client)
        assert router is not None
        assert router.llm_client == self.mock_llm_client

    def test_router_loads_chains(self):
        """Should load all platform chains on init."""
        router = ReviewRouter(self.mock_llm_client)
        assert len(router.chains) == 6  # 5 platforms + default


class TestRouteToChain:
    """Test routing code to appropriate chains."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()
        self.router = ReviewRouter(self.mock_llm_client)

        # Mock chain invoke to return predictable results
        for chain in self.router.chains.values():
            chain.invoke = Mock(return_value={"text": "Mock review"})

    def test_route_android_code(self):
        """Should route to android chain for android platform."""
        result = self.router.route("android", "code here", "test.kt")
        assert result["platform"] == "android"
        assert result["status"] == "success"

    def test_route_ios_code(self):
        """Should route to ios chain for ios platform."""
        result = self.router.route("ios", "code here", "test.swift")
        assert result["platform"] == "ios"
        assert result["status"] == "success"

    def test_route_ai_ml_code(self):
        """Should route to ai-ml chain for ai-ml platform."""
        result = self.router.route("ai-ml", "code here", "train.py")
        assert result["platform"] == "ai-ml"
        assert result["status"] == "success"

    def test_route_frontend_code(self):
        """Should route to frontend chain for frontend platform."""
        result = self.router.route("frontend", "code here", "App.tsx")
        assert result["platform"] == "frontend"
        assert result["status"] == "success"

    def test_route_backend_code(self):
        """Should route to backend chain for backend platform."""
        result = self.router.route("backend", "code here", "api.py")
        assert result["platform"] == "backend"
        assert result["status"] == "success"

    def test_route_unknown_platform_uses_default(self):
        """Should use default chain for unknown platform."""
        result = self.router.route("unknown", "code here", "test.xyz")
        assert result["platform"] == "default"
        assert result["status"] == "success"

    def test_route_none_platform_uses_default(self):
        """Should use default chain when platform is None."""
        result = self.router.route(None, "code here", "test.xyz")
        assert result["platform"] == "default"
        assert result["status"] == "success"


class TestRouteResult:
    """Test route result structure."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()
        self.router = ReviewRouter(self.mock_llm_client)

        for chain in self.router.chains.values():
            chain.invoke = Mock(return_value={"text": "Review result"})

    def test_result_contains_platform(self):
        """Result should contain platform name."""
        result = self.router.route("android", "code", "test.kt")
        assert "platform" in result

    def test_result_contains_file(self):
        """Result should contain file path."""
        result = self.router.route("android", "code", "test.kt")
        assert result["file"] == "test.kt"

    def test_result_contains_review(self):
        """Result should contain review text."""
        result = self.router.route("android", "code", "test.kt")
        assert "review" in result
        assert result["review"] == "Review result"

    def test_result_contains_status(self):
        """Result should contain status."""
        result = self.router.route("android", "code", "test.kt")
        assert result["status"] == "success"


class TestRouteError:
    """Test error handling in routing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()
        self.router = ReviewRouter(self.mock_llm_client)

    def test_chain_error_returns_error_result(self):
        """Should return error result when chain fails."""
        # Mock chain to raise exception
        for chain in self.router.chains.values():
            chain.invoke = Mock(side_effect=Exception("Chain failed"))

        result = self.router.route("android", "code", "test.kt")
        assert result["status"] == "error"
        assert "error" in result


class TestRouteBatch:
    """Test batch routing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()
        self.router = ReviewRouter(self.mock_llm_client)

        for chain in self.router.chains.values():
            chain.invoke = Mock(return_value={"text": "Review"})

    def test_route_batch_multiple_files(self):
        """Should route multiple files."""
        files = {"file1.kt": "code1", "file2.swift": "code2"}
        platforms = {"file1.kt": "android", "file2.swift": "ios"}

        results = self.router.route_batch(files, platforms)
        assert len(results) == 2

    def test_route_batch_preserves_platforms(self):
        """Should use correct platform for each file."""
        files = {"file1.kt": "code1", "file2.py": "code2"}
        platforms = {"file1.kt": "android", "file2.py": "ai-ml"}

        results = self.router.route_batch(files, platforms)
        assert results[0]["platform"] == "android"
        assert results[1]["platform"] == "ai-ml"

    def test_route_batch_empty(self):
        """Should handle empty batch."""
        results = self.router.route_batch({}, {})
        assert results == []


class TestGetAvailableChains:
    """Test getting available chains."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.llm = MagicMock()
        self.router = ReviewRouter(self.mock_llm_client)

    def test_get_available_chains_returns_list(self):
        """Should return list of chain names."""
        chains = self.router.get_available_chains()
        assert isinstance(chains, list)

    def test_get_available_chains_contains_all_platforms(self):
        """Should contain all platform chains."""
        chains = self.router.get_available_chains()
        assert "android" in chains
        assert "ios" in chains
        assert "ai-ml" in chains
        assert "frontend" in chains
        assert "backend" in chains
        assert "default" in chains
