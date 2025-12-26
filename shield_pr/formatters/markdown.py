"""Markdown formatter for code review results."""

from shield_pr.formatters.base import BaseFormatter
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class MarkdownFormatter(BaseFormatter):
    """Format review results as Markdown.

    Default formatter with clean, readable output structure.
    """

    def format(self, result: ReviewResult) -> str:
        """Transform ReviewResult to Markdown format.

        Args:
            result: ReviewResult containing findings and metadata

        Returns:
            Formatted Markdown string
        """
        groups = self._group_by_severity(result)
        sections = [
            self._header(result),
            self._findings_section(groups["HIGH"], "High Priority", "🔴"),
            self._findings_section(groups["MEDIUM"], "Medium Priority", "🟡"),
            self._findings_section(groups["LOW"], "Low Priority", "🟢"),
            self._summary(result),
        ]
        return "\n\n".join(filter(None, sections))

    def _header(self, result: ReviewResult) -> str:
        """Generate header section.

        Args:
            result: ReviewResult with metadata

        Returns:
            Header Markdown string
        """
        confidence_pct = result.confidence * 100
        return (
            f"# Code Review Results\n\n"
            f"**Platform**: {result.platform} | "
            f"**Confidence**: {confidence_pct:.0f}%"
        )

    def _findings_section(
        self,
        findings: list[Finding],
        title: str,
        emoji: str = ""
    ) -> str:
        """Generate findings section by severity.

        Args:
            findings: List of findings to format
            title: Section title
            emoji: Optional emoji prefix

        Returns:
            Findings section Markdown string or empty if no findings
        """
        if not findings:
            return ""

        emoji_prefix = f"{emoji} " if emoji else ""
        lines = [f"## {emoji_prefix}{title} Issues ({len(findings)})"]

        for finding in findings:
            location = self._format_location(finding)
            lines.append(
                f"- **[{finding.category}]** {location} - {finding.description}"
            )
            if finding.suggestion:
                lines.append(f"  **Suggestion**: {finding.suggestion}")
            if finding.code_snippet:
                snippet = self._format_code_snippet(finding.code_snippet)
                lines.append(f"  ```\n{snippet}\n  ```")

        return "\n".join(lines)

    def _format_location(self, finding: Finding) -> str:
        """Format file location with line number.

        Args:
            finding: Finding object

        Returns:
            Formatted location string
        """
        if finding.line_number:
            return f"`{finding.file_path}:{finding.line_number}`"
        return f"`{finding.file_path}`"

    def _format_code_snippet(self, snippet: str) -> str:
        """Format code snippet with proper indentation.

        Args:
            snippet: Raw code snippet

        Returns:
            Indented snippet for Markdown code block
        """
        lines = snippet.strip().split("\n")
        return "\n  ".join(lines)

    def _summary(self, result: ReviewResult) -> str:
        """Generate summary section.

        Args:
            result: ReviewResult with findings

        Returns:
            Summary Markdown string
        """
        counts = self._count_by_severity(result)
        total = len(result.findings)

        if total == 0:
            return "## Summary\n\nNo issues found. Code looks good!"

        parts = [f"## Summary\n\nFound {total} issue"]
        if total > 1:
            parts.append("s")

        details = []
        if counts["HIGH"]:
            details.append(f"{counts['HIGH']} high")
        if counts["MEDIUM"]:
            details.append(f"{counts['MEDIUM']} medium")
        if counts["LOW"]:
            details.append(f"{counts['LOW']} low")

        if details:
            parts.append(": " + ", ".join(details))

        parts.append(".")
        if result.summary:
            parts.append(f"\n\n{result.summary}")

        return "".join(parts)
