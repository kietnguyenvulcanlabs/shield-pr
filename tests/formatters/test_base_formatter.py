"""Tests for BaseFormatter."""

import pytest

from shield_pr.formatters.base import BaseFormatter
from shield_pr.models.review_result import ReviewResult
from shield_pr.models.finding import Finding


class ConcreteFormatter(BaseFormatter):
    """Concrete implementation for testing."""

    def format(self, result: ReviewResult) -> str:
        return "test output"


@pytest.fixture
def sample_result() -> ReviewResult:
    """Create sample ReviewResult for testing."""
    return ReviewResult(
        platform="android",
        findings=[
            Finding(
                severity="HIGH",
                category="security",
                file_path="MainActivity.kt",
                line_number=25,
                description="Memory leak detected",
                suggestion="Use WeakReference",
            ),
            Finding(
                severity="MEDIUM",
                category="performance",
                file_path="Adapter.kt",
                line_number=10,
                description="Inefficient RecyclerView pattern",
                suggestion="Use ViewHolder pattern",
            ),
            Finding(
                severity="LOW",
                category="style",
                file_path="Utils.kt",
                description="Long function",
                suggestion="Split into smaller functions",
            ),
        ],
        summary="Found 3 issues",
        confidence=0.92,
    )


@pytest.fixture
def empty_result() -> ReviewResult:
    """Create empty ReviewResult for testing."""
    return ReviewResult(
        platform="ios",
        findings=[],
        summary="No issues found",
        confidence=1.0,
    )


def test_group_by_severity(sample_result: ReviewResult) -> None:
    """Test grouping findings by severity."""
    formatter = ConcreteFormatter()
    groups = formatter._group_by_severity(sample_result)

    assert len(groups["HIGH"]) == 1
    assert len(groups["MEDIUM"]) == 1
    assert len(groups["LOW"]) == 1

    assert groups["HIGH"][0].category == "security"
    assert groups["MEDIUM"][0].category == "performance"
    assert groups["LOW"][0].category == "style"


def test_group_by_severity_empty(empty_result: ReviewResult) -> None:
    """Test grouping with no findings."""
    formatter = ConcreteFormatter()
    groups = formatter._group_by_severity(empty_result)

    assert len(groups["HIGH"]) == 0
    assert len(groups["MEDIUM"]) == 0
    assert len(groups["LOW"]) == 0


def test_count_by_severity(sample_result: ReviewResult) -> None:
    """Test counting findings by severity."""
    formatter = ConcreteFormatter()
    counts = formatter._count_by_severity(sample_result)

    assert counts["HIGH"] == 1
    assert counts["MEDIUM"] == 1
    assert counts["LOW"] == 1


def test_count_by_severity_empty(empty_result: ReviewResult) -> None:
    """Test counting with no findings."""
    formatter = ConcreteFormatter()
    counts = formatter._count_by_severity(empty_result)

    assert counts["HIGH"] == 0
    assert counts["MEDIUM"] == 0
    assert counts["LOW"] == 0


def test_group_by_category(sample_result: ReviewResult) -> None:
    """Test grouping findings by category."""
    formatter = ConcreteFormatter()
    findings = sample_result.findings
    groups = formatter._group_by_category(findings)

    assert len(groups) == 3
    assert "security" in groups
    assert "performance" in groups
    assert "style" in groups
    assert len(groups["security"]) == 1


def test_truncate_text_short() -> None:
    """Test truncation of short text."""
    formatter = ConcreteFormatter()
    text = "Short text"
    result = formatter._truncate_text(text, 20)

    assert result == text


def test_truncate_text_long() -> None:
    """Test truncation of long text."""
    formatter = ConcreteFormatter()
    text = "This is a very long text that should be truncated"
    result = formatter._truncate_text(text, 20)

    assert len(result) == 20
    assert result.endswith("...")


def test_format_abstract_method() -> None:
    """Test that format is abstract and must be implemented."""
    with pytest.raises(TypeError):
        # Can't instantiate abstract class
        BaseFormatter()
