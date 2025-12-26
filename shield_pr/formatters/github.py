"""GitHub PR comment formatter for code review results."""

from shield_pr.formatters.base import BaseFormatter
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class GitHubFormatter(BaseFormatter):
    """Format review results for GitHub PR comments.

    Uses GitHub-flavored Markdown with tables, checkboxes,
    and collapsible sections.
    """

    def format(self, result: ReviewResult) -> str:
        """Transform ReviewResult to GitHub PR comment format.

        Args:
            result: ReviewResult containing findings and metadata

        Returns:
            Formatted GitHub PR comment Markdown
        """
        sections = [
            self._header(result),
            self._summary_table(result),
            self._findings_sections(result),
            self._footer(result),
        ]
        return "\n\n".join(filter(None, sections))

    def _header(self, result: ReviewResult) -> str:
        """Generate header with review badge.

        Args:
            result: ReviewResult with metadata

        Returns:
            Header Markdown string
        """
        return "## 🔍 Code Review Assistant"

    def _summary_table(self, result: ReviewResult) -> str:
        """Generate summary table with key metrics.

        Args:
            result: ReviewResult with metadata

        Returns:
            Summary table Markdown
        """
        counts = self._count_by_severity(result)
        total = len(result.findings)
        confidence_pct = result.confidence * 100

        return (
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Platform | {result.platform} |\n"
            f"| Files Analyzed | {self._count_files(result)} |\n"
            f"| Issues Found | {total} |\n"
            f"| Confidence | {confidence_pct:.0f}% |\n"
            f"| 🔴 High | {counts['HIGH']} |\n"
            f"| 🟡 Medium | {counts['MEDIUM']} |\n"
            f"| 🟢 Low | {counts['LOW']} |"
        )

    def _count_files(self, result: ReviewResult) -> int:
        """Count unique files in findings.

        Args:
            result: ReviewResult with findings

        Returns:
            Number of unique files
        """
        files = set()
        for finding in result.findings:
            files.add(finding.file_path)
        return len(files)

    def _findings_sections(self, result: ReviewResult) -> str:
        """Generate collapsible findings sections by severity.

        Args:
            result: ReviewResult with findings

        Returns:
            Collapsible sections Markdown
        """
        groups = self._group_by_severity(result)
        sections = []

        if groups["HIGH"]:
            sections.append(self._collapsible_section(
                "🔴 High Priority",
                groups["HIGH"],
                "HIGH"
            ))

        if groups["MEDIUM"]:
            sections.append(self._collapsible_section(
                "🟡 Medium Priority",
                groups["MEDIUM"],
                "MEDIUM"
            ))

        if groups["LOW"]:
            sections.append(self._collapsible_section(
                "🟢 Low Priority",
                groups["LOW"],
                "LOW"
            ))

        if not sections:
            return "### ✅ No Issues Found\n\nGreat job! No issues detected."

        return "\n\n".join(sections)

    def _collapsible_section(
        self,
        title: str,
        findings: list[Finding],
        severity: str
    ) -> str:
        """Generate collapsible details section.

        Args:
            title: Section title
            findings: List of findings
            severity: Severity level for styling

        Returns:
            Collapsible section Markdown
        """
        emoji = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"

        lines = [f"<details><summary>{title} ({len(findings)})</summary>\n"]

        for finding in findings:
            location = self._format_location(finding)
            checkbox = "- [ ]" if severity == "HIGH" else "-"

            lines.append(
                f"{checkbox} **{emoji} {finding.category}**: {finding.description}"
            )
            lines.append(f"  <br>📍 {location}")

            if finding.suggestion:
                lines.append(f"  <br>💡 {finding.suggestion}")

            if finding.code_snippet:
                lines.append(f"  <br>```")
                lines.append(f"  {self._escape_code(finding.code_snippet)}")
                lines.append(f"  ```")

            lines.append("")

        lines.append("</details>")
        return "\n".join(lines)

    def _format_location(self, finding: Finding) -> str:
        """Format GitHub code reference with link.

        Args:
            finding: Finding object

        Returns:
            Formatted location with potential link
        """
        if finding.line_number:
            return f"`{finding.file_path}:{finding.line_number}`"
        return f"`{finding.file_path}`"

    def _escape_code(self, code: str) -> str:
        """Escape code for HTML rendering in GitHub.

        Args:
            code: Raw code snippet

        Returns:
            HTML-escaped code
        """
        return code.replace("<", "&lt;").replace(">", "&gt;")

    def _footer(self, result: ReviewResult) -> str:
        """Generate footer with summary.

        Args:
            result: ReviewResult with summary

        Returns:
            Footer Markdown string
        """
        if not result.summary:
            return ""

        return f"---\n\n**Summary**: {result.summary}"
