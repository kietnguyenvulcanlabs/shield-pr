"""Output formatters for code review results.

This module provides formatters for transforming ReviewResult objects
into various output formats including Markdown, GitHub, GitLab, Slack, and JSON.
"""

from shield_pr.formatters.base import BaseFormatter
from shield_pr.formatters.markdown import MarkdownFormatter
from shield_pr.formatters.github import GitHubFormatter
from shield_pr.formatters.gitlab import GitLabFormatter
from shield_pr.formatters.slack import SlackFormatter
from shield_pr.formatters.json_formatter import JSONFormatter
from shield_pr.formatters.rich_renderer import RichRenderer

__all__ = [
    "BaseFormatter",
    "MarkdownFormatter",
    "GitHubFormatter",
    "GitLabFormatter",
    "SlackFormatter",
    "JSONFormatter",
    "RichRenderer",
]


def get_formatter(format_type: str = "markdown") -> BaseFormatter:
    """Factory function to get formatter by type.

    Args:
        format_type: Type of formatter (markdown, github, gitlab, slack, json)

    Returns:
        Formatter instance for the specified type

    Raises:
        ValueError: If format_type is not supported
    """
    formatters = {
        "markdown": MarkdownFormatter,
        "github": GitHubFormatter,
        "gitlab": GitLabFormatter,
        "slack": SlackFormatter,
        "json": JSONFormatter,
    }

    formatter_class = formatters.get(format_type.lower())
    if formatter_class is None:
        raise ValueError(
            f"Unsupported format: {format_type}. "
            f"Supported formats: {', '.join(formatters.keys())}"
        )

    return formatter_class()  # type: ignore[abstract]
