"""Tests for JSONFormatter."""

import json

import pytest

from shield_pr.formatters.json_formatter import JSONFormatter
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
        ],
        summary="Found 1 issue",
        confidence=0.92,
    )


def test_format_valid_json(sample_result: ReviewResult) -> None:
    """Test that output is valid JSON."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    # Should not raise exception
    data = json.loads(output)
    assert data is not None


def test_format_includes_platform(sample_result: ReviewResult) -> None:
    """Test that platform is included."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    assert data["platform"] == "android"


def test_format_includes_confidence(sample_result: ReviewResult) -> None:
    """Test that confidence is included."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    assert data["confidence"] == 0.92


def test_format_includes_findings(sample_result: ReviewResult) -> None:
    """Test that findings array is included."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    assert len(data["findings"]) == 1


def test_format_finding_fields(sample_result: ReviewResult) -> None:
    """Test that all finding fields are serialized."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    finding = data["findings"][0]

    assert finding["severity"] == "HIGH"
    assert finding["category"] == "security"
    assert finding["file_path"] == "MainActivity.kt"
    assert finding["line_number"] == 25
    assert finding["description"] == "Memory leak"
    assert finding["suggestion"] == "Use WeakReference"
    assert finding["code_snippet"] == "listener.setContext(this)"


def test_format_includes_metadata(sample_result: ReviewResult) -> None:
    """Test that metadata section is included."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    data = json.loads(output)
    assert "metadata" in data
    assert "timestamp" in data["metadata"]
    assert "version" in data["metadata"]
    assert "tool" in data["metadata"]


def test_format_empty_result() -> None:
    """Test formatting with no findings."""
    result = ReviewResult(
        platform="ios",
        findings=[],
        summary="No issues",
        confidence=1.0,
    )

    formatter = JSONFormatter()
    output = formatter.format(result)

    data = json.loads(output)
    assert data["findings"] == []
    assert data["platform"] == "ios"


def test_format_indented_output(sample_result: ReviewResult) -> None:
    """Test that output is properly indented."""
    formatter = JSONFormatter()
    output = formatter.format(sample_result)

    # Check for indentation (2 spaces)
    assert "\n  " in output or "\n    " in output
