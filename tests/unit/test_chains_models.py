"""Tests for chain models (Finding and ReviewResult)."""

import pytest
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class TestFinding:
    """Tests for Finding model."""

    def test_finding_creation(self):
        """Test basic Finding creation."""
        finding = Finding(
            severity="HIGH",
            category="security",
            file_path="test.py",
            line_number=42,
            description="SQL injection vulnerability",
            suggestion="Use parameterized queries",
            code_snippet="query = f'SELECT * FROM users WHERE id = {user_id}'"
        )

        assert finding.severity == "HIGH"
        assert finding.category == "security"
        assert finding.file_path == "test.py"
        assert finding.line_number == 42
        assert "SQL injection" in finding.description

    def test_finding_without_optional_fields(self):
        """Test Finding creation without optional fields."""
        finding = Finding(
            severity="MEDIUM",
            category="performance",
            file_path="app.py",
            description="N+1 query detected",
            suggestion="Use eager loading"
        )

        assert finding.line_number is None
        assert finding.code_snippet is None


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_review_result_creation(self):
        """Test basic ReviewResult creation."""
        finding = Finding(
            severity="HIGH",
            category="memory-leak",
            file_path="MainActivity.kt",
            description="Context leaked",
            suggestion="Use WeakReference"
        )

        result = ReviewResult(
            platform="android",
            findings=[finding],
            summary="Found 1 high severity issue",
            confidence=0.95
        )

        assert result.platform == "android"
        assert len(result.findings) == 1
        assert result.findings[0].severity == "HIGH"
        assert result.confidence == 0.95

    def test_review_result_empty_findings(self):
        """Test ReviewResult with no findings."""
        result = ReviewResult(
            platform="ios",
            findings=[],
            summary="No issues found",
            confidence=0.85
        )

        assert len(result.findings) == 0
        assert "No issues" in result.summary

    def test_review_result_confidence_validation(self):
        """Test confidence validation (0.0-1.0)."""
        with pytest.raises(Exception):  # Pydantic validation error
            ReviewResult(
                platform="frontend",
                findings=[],
                summary="Test",
                confidence=1.5  # Invalid: > 1.0
            )
