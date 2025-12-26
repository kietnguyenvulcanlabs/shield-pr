"""Tests for SlackFormatter."""

import json

import pytest

from shield_pr.formatters.slack import SlackFormatter
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


def test_format_valid_json(sample_result: ReviewResult) -> None:
    """Test that output is valid JSON with blocks."""
    formatter = SlackFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    assert "blocks" in data
    assert isinstance(data["blocks"], list)


def test_format_has_header_block(sample_result: ReviewResult) -> None:
    """Test that header block is included."""
    formatter = SlackFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    blocks = data["blocks"]

    assert blocks[0]["type"] == "header"
    assert "Code Review Results" in blocks[0]["text"]["text"]


def test_format_has_summary_fields(sample_result: ReviewResult) -> None:
    """Test that summary section has fields."""
    formatter = SlackFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    blocks = data["blocks"]

    # Find section block with fields
    section_blocks = [b for b in blocks if b.get("type") == "section"]
    assert len(section_blocks) > 0

    summary = next((b for b in section_blocks if "fields" in b), None)
    assert summary is not None
    assert len(summary["fields"]) > 0


def test_format_includes_platform(sample_result: ReviewResult) -> None:
    """Test that platform is in summary fields."""
    formatter = SlackFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    output_str = json.dumps(data)

    assert "android" in output_str


def test_format_uses_divider_blocks(sample_result: ReviewResult) -> None:
    """Test that divider blocks are used."""
    formatter = SlackFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    blocks = data["blocks"]

    dividers = [b for b in blocks if b.get("type") == "divider"]
    assert len(dividers) > 0


def test_format_empty_result(empty_result: ReviewResult) -> None:
    """Test formatting with no findings."""
    formatter = SlackFormatter()
    output = formatter.format(empty_result)

    data = json.loads(output)
    output_str = json.dumps(data)

    assert "No issues found" in output_str or "white_check_mark" in output_str


def test_format_truncates_long_text() -> None:
    """Test that long text is truncated for Slack limits."""
    formatter = SlackFormatter()

    long_desc = "x" * 200
    result = ReviewResult(
        platform="backend",
        findings=[
            Finding(
                severity="HIGH",
                category="test",
                file_path="test.py",
                line_number=1,
                description=long_desc,
                suggestion=long_desc,
            )
        ],
        summary="Test",
        confidence=1.0,
    )

    output = formatter.format(result)
    data = json.loads(output)

    # Should truncate to fit within Slack limits
    for block in data["blocks"]:
        block_str = json.dumps(block)
        # Each block should be reasonable size
        assert len(block_str) < 3000


def test_format_respects_max_blocks() -> None:
    """Test that output respects Slack's 50 block limit."""
    formatter = SlackFormatter()

    # Create result with many findings
    findings = [
        Finding(
            severity="HIGH",
            category="security",
            file_path=f"file{i}.py",
            line_number=i,
            description=f"Issue {i}",
            suggestion="Fix it",
        )
        for i in range(100)
    ]

    result = ReviewResult(
        platform="backend",
        findings=findings,
        summary="Many issues",
        confidence=1.0,
    )

    output = formatter.format(result)
    data = json.loads(output)

    # Should not exceed 50 blocks
    assert len(data["blocks"]) <= 50
