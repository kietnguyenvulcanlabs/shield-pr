"""Tests for MarkdownFormatter."""

import pytest

from shield_pr.formatters.markdown import MarkdownFormatter
from shield_pr.models.review_result import ReviewResult
from shield_pr.models.finding import Finding


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
                code_snippet="listener.setContext(this)",
            ),
            Finding(
                severity="MEDIUM",
                category="performance",
                file_path="Adapter.kt",
                line_number=10,
                description="Inefficient RecyclerView pattern",
                suggestion="Use ViewHolder pattern",
            ),
        ],
        summary="Found 2 issues",
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


def test_format_has_header(sample_result: ReviewResult) -> None:
    """Test that output includes header."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_result)

    assert "# Code Review Results" in output
    assert "android" in output
    assert "92%" in output


def test_format_has_severity_sections(sample_result: ReviewResult) -> None:
    """Test that output includes severity sections."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_result)

    assert "High Priority Issues" in output
    assert "Medium Priority Issues" in output


def test_format_includes_finding_details(sample_result: ReviewResult) -> None:
    """Test that findings include all details."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_result)

    assert "security" in output
    assert "MainActivity.kt:25" in output
    assert "Memory leak detected" in output
    assert "WeakReference" in output


def test_format_includes_code_snippet(sample_result: ReviewResult) -> None:
    """Test that code snippets are included."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_result)

    assert "listener.setContext(this)" in output
    assert "```" in output


def test_format_empty_result(empty_result: ReviewResult) -> None:
    """Test formatting with no findings."""
    formatter = MarkdownFormatter()
    output = formatter.format(empty_result)

    assert "# Code Review Results" in output
    assert "No issues found" in output
    # Check for "good" without case-sensitive assertion
    assert "good" in output.lower() or "looks good" in output.lower()


def test_format_summary_section(sample_result: ReviewResult) -> None:
    """Test summary section is generated."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_result)

    assert "## Summary" in output
    assert "Found 2 issues" in output


def test_format_location_with_line_number() -> None:
    """Test file location formatting with line number."""
    formatter = MarkdownFormatter()
    finding = Finding(
        severity="HIGH",
        category="test",
        file_path="test.py",
        line_number=42,
        description="Test",
        suggestion="Fix it",
    )

    result = ReviewResult(
        platform="backend",
        findings=[finding],
        summary="Test",
        confidence=1.0,
    )

    output = formatter.format(result)
    assert "test.py:42" in output


def test_format_location_without_line_number() -> None:
    """Test file location formatting without line number."""
    formatter = MarkdownFormatter()
    finding = Finding(
        severity="HIGH",
        category="test",
        file_path="test.py",
        line_number=None,
        description="Test",
        suggestion="Fix it",
    )

    result = ReviewResult(
        platform="backend",
        findings=[finding],
        summary="Test",
        confidence=1.0,
    )

    output = formatter.format(result)
    assert "`test.py`" in output
