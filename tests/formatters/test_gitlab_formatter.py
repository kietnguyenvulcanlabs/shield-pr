"""Tests for GitLabFormatter."""

import pytest

from shield_pr.formatters.gitlab import GitLabFormatter
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
                description="Memory leak",
                suggestion="Use WeakReference",
                code_snippet="listener.setContext(this)",
            ),
            Finding(
                severity="MEDIUM",
                category="performance",
                file_path="Adapter.kt",
                line_number=10,
                description="Slow adapter",
                suggestion="Use ViewHolder",
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
        summary="No issues",
        confidence=1.0,
    )


def test_format_has_header(sample_result: ReviewResult) -> None:
    """Test that output includes header."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert "## " in output  # Has header
    assert "Code Review Assistant" in output


def test_format_has_summary_table(sample_result: ReviewResult) -> None:
    """Test that output includes metrics table."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert "| Platform |" in output
    assert "| android |" in output
    assert "| Issues Found |" in output


def test_format_uses_gitlab_emojis(sample_result: ReviewResult) -> None:
    """Test that GitLab-flavored emojis are used."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert ":red_circle:" in output
    assert ":yellow_circle:" in output


def test_format_has_checkboxes_for_high(sample_result: ReviewResult) -> None:
    """Test that high severity has checkboxes."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert "- [ ]" in output


def test_format_empty_result(empty_result: ReviewResult) -> None:
    """Test formatting with no findings."""
    formatter = GitLabFormatter()
    output = formatter.format(empty_result)

    assert "No Issues Found" in output
    assert "Great job" in output


def test_format_has_footer(sample_result: ReviewResult) -> None:
    """Test that footer is included."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert "---" in output
    assert "Code Review Assistant" in output


def test_format_includes_file_location(sample_result: ReviewResult) -> None:
    """Test that file locations are formatted."""
    formatter = GitLabFormatter()
    output = formatter.format(sample_result)

    assert "MainActivity.kt:25" in output
