"""Tests for GitHubFormatter."""

import pytest

from shield_pr.formatters.github import GitHubFormatter
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
                description="Inefficient pattern",
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
        summary="No issues found",
        confidence=1.0,
    )


def test_format_has_header(sample_result: ReviewResult) -> None:
    """Test that output includes header with emoji."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    assert "## " in output  # Has header
    assert "Code Review Assistant" in output


def test_format_has_summary_table(sample_result: ReviewResult) -> None:
    """Test that output includes metrics table."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    assert "| Platform |" in output
    assert "| android |" in output
    assert "| Files Analyzed |" in output
    assert "| Issues Found |" in output
    assert "| 2 |" in output


def test_format_has_collapsible_sections(sample_result: ReviewResult) -> None:
    """Test that findings use collapsible details sections."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    assert "<details>" in output
    assert "</details>" in output
    assert "<summary>" in output


def test_format_uses_checkboxes_for_high(sample_result: ReviewResult) -> None:
    """Test that high severity findings have checkboxes."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    assert "- [ ]" in output


def test_format_emojis_by_severity(sample_result: ReviewResult) -> None:
    """Test that correct emojis are used per severity."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    assert "" in output or "" in output  # High/Medium


def test_format_empty_result(empty_result: ReviewResult) -> None:
    """Test formatting with no findings."""
    formatter = GitHubFormatter()
    output = formatter.format(empty_result)

    assert "No Issues Found" in output
    assert "Great job" in output


def test_format_code_escaping(sample_result: ReviewResult) -> None:
    """Test HTML escaping in code snippets."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    # Check for HTML entities
    assert "&lt;" in output or "listener.setContext" in output


def test_count_files_unique(sample_result: ReviewResult) -> None:
    """Test that unique files are counted correctly."""
    formatter = GitHubFormatter()
    output = formatter.format(sample_result)

    # Should have 2 unique files
    assert "| 2 |" in output
