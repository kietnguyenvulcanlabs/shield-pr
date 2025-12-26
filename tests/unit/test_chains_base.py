"""Tests for BaseReviewChain (depth selection and stage execution)."""

from unittest.mock import MagicMock, patch
import pytest
from shield_pr.chains.base import BaseReviewChain
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult
from shield_pr.core.errors import ReviewError


class ConcreteReviewChain(BaseReviewChain):
    """Concrete implementation for testing."""

    def _build_stages(self):
        """Build test stages."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"text": "Test output"}

        return {
            "architecture": mock_chain,
            "platform_issues": mock_chain,
            "tests": mock_chain,
            "improvements": mock_chain,
            "security_audit": mock_chain,
            "performance": mock_chain,
        }


class TestBaseReviewChainDepthSelection:
    """Tests for depth-based stage selection."""

    def test_quick_depth_stages(self):
        """Test quick depth selects minimal stages."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        stages = chain._select_stages_by_depth()

        assert stages == ["architecture", "improvements"]
        assert len(stages) == 2

    def test_standard_depth_stages(self):
        """Test standard depth selects moderate stages."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="standard", platform="test")

        stages = chain._select_stages_by_depth()

        assert stages == ["architecture", "platform_issues", "tests", "improvements"]
        assert len(stages) == 4

    def test_deep_depth_stages(self):
        """Test deep depth selects all stages."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="deep", platform="test")

        stages = chain._select_stages_by_depth()

        expected = [
            "architecture",
            "platform_issues",
            "tests",
            "improvements",
            "security_audit",
            "performance",
        ]
        assert stages == expected
        assert len(stages) == 6

    def test_invalid_depth_defaults_to_standard(self):
        """Test invalid depth falls back to standard."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="invalid", platform="test")

        stages = chain._select_stages_by_depth()

        assert stages == ["architecture", "platform_issues", "tests", "improvements"]


class TestBaseReviewChainStageExecution:
    """Tests for stage execution logic."""

    def test_execute_stages_calls_all_selected(self):
        """Test all selected stages are executed."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        active_stages = ["architecture", "improvements"]
        result = chain._execute_stages(active_stages, "code", "test.py")

        # Both stages should be invoked
        assert chain.stages["architecture"].invoke.call_count == 1
        assert chain.stages["improvements"].invoke.call_count == 1

        # Other stages should not be invoked
        assert chain.stages["platform_issues"].invoke.call_count == 0

    def test_execute_stages_builds_context(self):
        """Test stages receive accumulated context."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        # Mock different outputs for each stage
        arch_output = {"text": "Architecture analysis"}
        imp_output = {"text": "Improvements"}

        chain.stages["architecture"].invoke.return_value = arch_output
        chain.stages["improvements"].invoke.return_value = imp_output

        active_stages = ["architecture", "improvements"]
        result = chain._execute_stages(active_stages, "code", "test.py")

        # Check context accumulation
        assert "code" in result
        assert "file_path" in result
        assert "architecture_result" in result
        assert "improvements_result" in result
        assert result["architecture_result"] == "Architecture analysis"

    def test_execute_stages_skips_missing_stages(self):
        """Test execution skips stages not in registry."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="standard", platform="test")

        active_stages = ["architecture", "nonexistent_stage", "improvements"]
        result = chain._execute_stages(active_stages, "code", "test.py")

        # Should complete without error
        assert "architecture_result" in result
        assert "improvements_result" in result
        assert "nonexistent_stage_result" not in result


class TestBaseReviewChainIntegration:
    """Integration tests for full chain execution."""

    @patch("shield_pr.chains.base.ResultParser")
    def test_execute_full_workflow(self, mock_parser_class):
        """Test complete execute workflow."""
        # Setup mocks
        llm_client = MagicMock()
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Mock parser methods
        finding = Finding(
            severity="HIGH",
            category="security",
            file_path="test.py",
            description="Issue found",
            suggestion="Fix it",
        )
        mock_parser.extract_findings.return_value = [finding]
        mock_parser.generate_summary.return_value = "Found 1 issue"
        mock_parser.calculate_confidence.return_value = 0.85

        # Create chain
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        # Execute
        result = chain.execute("test code", "test.py")

        # Verify result structure
        assert isinstance(result, ReviewResult)
        assert result.platform == "test"
        assert len(result.findings) == 1
        assert result.findings[0].severity == "HIGH"
        assert result.summary == "Found 1 issue"
        assert result.confidence == 0.85

    def test_execute_handles_errors(self):
        """Test execute handles chain errors gracefully."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        # Make stage execution fail
        chain.stages["architecture"].invoke.side_effect = Exception("LLM error")

        with pytest.raises(ReviewError, match="Chain execution failed"):
            chain.execute("test code", "test.py")

    @patch("shield_pr.chains.base.ResultParser")
    def test_execute_with_different_depths(self, mock_parser_class):
        """Test execute works with all depth levels."""
        llm_client = MagicMock()
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        mock_parser.extract_findings.return_value = []
        mock_parser.generate_summary.return_value = "No issues"
        mock_parser.calculate_confidence.return_value = 0.9

        for depth in ["quick", "standard", "deep"]:
            chain = ConcreteReviewChain(llm_client, depth=depth, platform="test")
            result = chain.execute("code", "test.py")

            assert isinstance(result, ReviewResult)
            assert result.platform == "test"


class TestBaseReviewChainInitialization:
    """Tests for chain initialization."""

    def test_init_sets_attributes(self):
        """Test initialization sets all attributes correctly."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="deep", platform="android")

        assert chain.llm == llm_client
        assert chain.depth == "deep"
        assert chain.platform == "android"
        assert chain.stages is not None
        assert chain.parser is not None

    def test_init_default_depth(self):
        """Test initialization uses standard depth by default."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, platform="ios")

        assert chain.depth == "standard"

    def test_init_builds_stages(self):
        """Test initialization calls _build_stages."""
        llm_client = MagicMock()
        chain = ConcreteReviewChain(llm_client, depth="quick", platform="test")

        # Verify stages were built
        assert "architecture" in chain.stages
        assert "improvements" in chain.stages
        assert len(chain.stages) == 6  # All test stages
