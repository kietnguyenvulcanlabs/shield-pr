"""Base formatter class for output formatting."""

from abc import ABC, abstractmethod
from typing import Dict, List

from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class BaseFormatter(ABC):
    """Abstract base class for all output formatters.

    Provides common helper methods for grouping and processing findings.
    Subclasses must implement the format() method.
    """

    @abstractmethod
    def format(self, result: ReviewResult) -> str:
        """Transform ReviewResult to target format.

        Args:
            result: ReviewResult object containing findings and metadata

        Returns:
            Formatted string in the target format
        """
        pass

    def _group_by_severity(self, result: ReviewResult) -> Dict[str, List[Finding]]:
        """Group findings by severity level.

        Args:
            result: ReviewResult containing findings

        Returns:
            Dictionary with severity levels as keys and finding lists as values
        """
        groups: Dict[str, List[Finding]] = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
        }
        for finding in result.findings:
            if finding.severity in groups:
                groups[finding.severity].append(finding)
        return groups

    def _count_by_severity(self, result: ReviewResult) -> Dict[str, int]:
        """Count findings by severity level.

        Args:
            result: ReviewResult containing findings

        Returns:
            Dictionary with severity counts
        """
        groups = self._group_by_severity(result)
        return {
            "HIGH": len(groups["HIGH"]),
            "MEDIUM": len(groups["MEDIUM"]),
            "LOW": len(groups["LOW"]),
        }

    def _group_by_category(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by category.

        Args:
            findings: List of findings to group

        Returns:
            Dictionary with categories as keys and finding lists as values
        """
        groups: Dict[str, List[Finding]] = {}
        for finding in findings:
            if finding.category not in groups:
                groups[finding.category] = []
            groups[finding.category].append(finding)
        return groups

    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Markdown output.

        Args:
            text: Text to escape

        Returns:
            Escaped text safe for Markdown rendering
        """
        # Only escape code blocks and inline code
        special_chars = ["\\", "`", "*", "_", "[", "]", "(", ")"]
        result = text
        for char in special_chars:
            result = result.replace(char, f"\\{char}")
        return result

    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        """Truncate text to max length with ellipsis.

        Args:
            text: Text to truncate
            max_length: Maximum length before truncation

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
