"""Tests for platform-specific review chains."""

from unittest.mock import MagicMock, patch
import pytest
from langchain.chains import LLMChain
from shield_pr.chains.platforms.android_chain import AndroidReviewChain
from shield_pr.chains.platforms.ios_chain import IOSReviewChain
from shield_pr.chains.platforms.ai_ml_chain import AiMlReviewChain
from shield_pr.chains.platforms.frontend_chain import FrontendReviewChain
from shield_pr.chains.platforms.backend_chain import BackendReviewChain


class TestAndroidReviewChain:
    """Tests for Android-specific review chain."""

    def test_android_chain_initialization(self):
        """Test AndroidReviewChain initialization."""
        llm_client = MagicMock()
        chain = AndroidReviewChain(llm_client, depth="standard")

        assert chain.platform == "android"
        assert chain.llm == llm_client
        assert chain.depth == "standard"
        assert chain.stages is not None

    def test_android_chain_builds_correct_stages(self):
        """Test AndroidReviewChain builds expected stages."""
        llm_client = MagicMock()
        chain = AndroidReviewChain(llm_client, depth="standard")

        # Android should have these stages
        assert "architecture" in chain.stages
        assert "platform_issues" in chain.stages
        assert "tests" in chain.stages
        assert "improvements" in chain.stages

        # All stages should be LLMChain instances
        for stage in chain.stages.values():
            assert isinstance(stage, LLMChain)

    def test_android_chain_stage_output_keys(self):
        """Test AndroidReviewChain stages have correct output keys."""
        llm_client = MagicMock()
        chain = AndroidReviewChain(llm_client, depth="standard")

        assert chain.stages["architecture"].output_key == "architecture_result"
        assert chain.stages["platform_issues"].output_key == "platform_issues_result"
        assert chain.stages["tests"].output_key == "tests_result"
        assert chain.stages["improvements"].output_key == "improvements_result"

    def test_android_chain_inherits_from_base(self):
        """Test AndroidReviewChain properly inherits BaseReviewChain methods."""
        llm_client = MagicMock()
        chain = AndroidReviewChain(llm_client, depth="quick")

        # Should have BaseReviewChain methods
        assert hasattr(chain, "execute")
        assert hasattr(chain, "_select_stages_by_depth")
        assert hasattr(chain, "_execute_stages")
        assert hasattr(chain, "_parse_result")


class TestIOSReviewChain:
    """Tests for iOS-specific review chain."""

    def test_ios_chain_initialization(self):
        """Test IOSReviewChain initialization."""
        llm_client = MagicMock()
        chain = IOSReviewChain(llm_client, depth="deep")

        assert chain.platform == "ios"
        assert chain.llm == llm_client
        assert chain.depth == "deep"

    def test_ios_chain_builds_correct_stages(self):
        """Test IOSReviewChain builds expected stages."""
        llm_client = MagicMock()
        chain = IOSReviewChain(llm_client, depth="standard")

        assert "architecture" in chain.stages
        assert "platform_issues" in chain.stages
        assert "tests" in chain.stages
        assert "improvements" in chain.stages

        for stage in chain.stages.values():
            assert isinstance(stage, LLMChain)

    def test_ios_chain_default_depth(self):
        """Test IOSReviewChain uses default depth."""
        llm_client = MagicMock()
        chain = IOSReviewChain(llm_client)

        assert chain.depth == "standard"


class TestAiMlReviewChain:
    """Tests for AI/ML-specific review chain."""

    def test_ai_ml_chain_initialization(self):
        """Test AiMlReviewChain initialization."""
        llm_client = MagicMock()
        chain = AiMlReviewChain(llm_client, depth="standard")

        assert chain.platform == "ai-ml"
        assert chain.llm == llm_client

    def test_ai_ml_chain_builds_correct_stages(self):
        """Test AiMlReviewChain builds expected stages."""
        llm_client = MagicMock()
        chain = AiMlReviewChain(llm_client, depth="standard")

        assert "architecture" in chain.stages
        assert "platform_issues" in chain.stages
        assert "tests" in chain.stages
        assert "improvements" in chain.stages

        for stage in chain.stages.values():
            assert isinstance(stage, LLMChain)


class TestFrontendReviewChain:
    """Tests for Frontend-specific review chain."""

    def test_frontend_chain_initialization(self):
        """Test FrontendReviewChain initialization."""
        llm_client = MagicMock()
        chain = FrontendReviewChain(llm_client, depth="quick")

        assert chain.platform == "frontend"
        assert chain.depth == "quick"

    def test_frontend_chain_builds_correct_stages(self):
        """Test FrontendReviewChain builds expected stages."""
        llm_client = MagicMock()
        chain = FrontendReviewChain(llm_client, depth="standard")

        assert "architecture" in chain.stages
        assert "platform_issues" in chain.stages
        assert "tests" in chain.stages
        assert "improvements" in chain.stages

        for stage in chain.stages.values():
            assert isinstance(stage, LLMChain)


class TestBackendReviewChain:
    """Tests for Backend-specific review chain."""

    def test_backend_chain_initialization(self):
        """Test BackendReviewChain initialization."""
        llm_client = MagicMock()
        chain = BackendReviewChain(llm_client, depth="deep")

        assert chain.platform == "backend"
        assert chain.depth == "deep"

    def test_backend_chain_builds_correct_stages(self):
        """Test BackendReviewChain builds expected stages."""
        llm_client = MagicMock()
        chain = BackendReviewChain(llm_client, depth="standard")

        assert "architecture" in chain.stages
        assert "platform_issues" in chain.stages
        assert "tests" in chain.stages
        assert "improvements" in chain.stages

        for stage in chain.stages.values():
            assert isinstance(stage, LLMChain)


class TestPlatformChainsMockLLM:
    """Tests for platform chains with mocked LLM execution."""

    @patch("shield_pr.chains.base.ResultParser")
    def test_android_chain_execute_with_mock_llm(self, mock_parser_class):
        """Test AndroidReviewChain execute with mocked LLM."""
        # Setup mocks
        llm_client = MagicMock()
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Mock parser outputs
        from shield_pr.models.finding import Finding
        from shield_pr.models.review_result import ReviewResult

        finding = Finding(
            severity="HIGH",
            category="memory-leak",
            file_path="MainActivity.kt",
            description="Context leaked",
            suggestion="Use WeakReference"
        )
        mock_parser.extract_findings.return_value = [finding]
        mock_parser.generate_summary.return_value = "Found 1 issue"
        mock_parser.calculate_confidence.return_value = 0.9

        # Create and execute chain
        chain = AndroidReviewChain(llm_client, depth="quick")

        # Mock stage outputs
        for stage in chain.stages.values():
            stage.invoke = MagicMock(return_value={"text": "Mock output"})

        result = chain.execute("code", "MainActivity.kt")

        assert isinstance(result, ReviewResult)
        assert result.platform == "android"
        assert len(result.findings) == 1
        assert result.findings[0].severity == "HIGH"

    @patch("shield_pr.chains.base.ResultParser")
    def test_ios_chain_execute_with_mock_llm(self, mock_parser_class):
        """Test IOSReviewChain execute with mocked LLM."""
        llm_client = MagicMock()
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        from shield_pr.models.review_result import ReviewResult

        mock_parser.extract_findings.return_value = []
        mock_parser.generate_summary.return_value = "No issues found"
        mock_parser.calculate_confidence.return_value = 0.95

        chain = IOSReviewChain(llm_client, depth="standard")

        for stage in chain.stages.values():
            stage.invoke = MagicMock(return_value={"text": "Clean code"})

        result = chain.execute("code", "ViewController.swift")

        assert isinstance(result, ReviewResult)
        assert result.platform == "ios"
        assert len(result.findings) == 0

    @patch("shield_pr.chains.base.ResultParser")
    def test_frontend_chain_execute_with_mock_llm(self, mock_parser_class):
        """Test FrontendReviewChain execute with mocked LLM."""
        llm_client = MagicMock()
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        from shield_pr.models.finding import Finding
        from shield_pr.models.review_result import ReviewResult

        findings = [
            Finding(severity="MEDIUM", category="performance", file_path="app.js", description="Slow", suggestion="Optimize"),
            Finding(severity="LOW", category="style", file_path="app.js", description="Format", suggestion="Fix")
        ]
        mock_parser.extract_findings.return_value = findings
        mock_parser.generate_summary.return_value = "Found 2 issues"
        mock_parser.calculate_confidence.return_value = 0.85

        chain = FrontendReviewChain(llm_client, depth="deep")

        for stage in chain.stages.values():
            stage.invoke = MagicMock(return_value={"text": "Analysis output"})

        result = chain.execute("code", "app.js")

        assert result.platform == "frontend"
        assert len(result.findings) == 2

    def test_all_platforms_support_depth_levels(self):
        """Test all platform chains support all depth levels."""
        llm_client = MagicMock()
        platforms = [
            AndroidReviewChain,
            IOSReviewChain,
            AiMlReviewChain,
            FrontendReviewChain,
            BackendReviewChain
        ]

        for platform_class in platforms:
            for depth in ["quick", "standard", "deep"]:
                chain = platform_class(llm_client, depth=depth)
                assert chain.depth == depth

                # Verify stage selection works
                selected_stages = chain._select_stages_by_depth()
                assert isinstance(selected_stages, list)
                assert len(selected_stages) > 0
