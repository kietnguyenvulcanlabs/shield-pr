"""Rich terminal renderer for code review results."""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class RichRenderer:
    """Render review results using Rich library for terminal output.

    Provides colorful, formatted output with tables, syntax highlighting,
    and progress indicators. Falls back to plain text for non-TTY outputs.
    """

    SEVERITY_COLORS = {
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "cyan",
    }

    SEVERITY_ICONS = {
        "HIGH": "",
        "MEDIUM": "",
        "LOW": "",
    }

    def __init__(self, console: Optional[Console] = None):
        """Initialize renderer.

        Args:
            console: Optional Rich console instance (creates new if None)
        """
        self.console = console or Console()

    def render(self, result: ReviewResult) -> None:
        """Render review result to terminal.

        Args:
            result: ReviewResult to render
        """
        if not sys.stdout.isatty():
            self._render_plain(result)
            return

        self.console.print()
        self._render_header(result)
        self.console.print()
        self._render_summary_table(result)
        self.console.print()
        self._render_findings(result)
        self.console.print()

    def _render_header(self, result: ReviewResult) -> None:
        """Render header panel.

        Args:
            result: ReviewResult with metadata
        """
        confidence_pct = int(result.confidence * 100)
        header_text = (
            f"[bold cyan]Code Review Results[/bold cyan]\n\n"
            f"Platform: [bold]{result.platform}[/bold] | "
            f"Confidence: [bold]{confidence_pct}%[/bold]"
        )
        self.console.print(Panel(header_text, border_style="cyan"))

    def _render_summary_table(self, result: ReviewResult) -> None:
        """Render summary table with metrics.

        Args:
            result: ReviewResult with findings
        """
        counts = self._count_by_severity(result)
        total = len(result.findings)

        table = Table(title="Review Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Issues", str(total))
        table.add_row("High Priority", str(counts["HIGH"]))
        table.add_row("Medium Priority", str(counts["MEDIUM"]))
        table.add_row("Low Priority", str(counts["LOW"]))
        table.add_row("Unique Files", str(self._count_files(result)))

        self.console.print(table)

    def _render_findings(self, result: ReviewResult) -> None:
        """Render all findings grouped by severity.

        Args:
            result: ReviewResult with findings
        """
        groups = self._group_by_severity(result)

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            findings = groups[severity]
            if findings:
                self._render_severity_section(severity, findings)

        if not result.findings:
            self.console.print(
                Panel("[bold green]No issues found![/bold green]", border_style="green")
            )

    def _render_severity_section(
        self, severity: str, findings: list[Finding]
    ) -> None:
        """Render findings for a severity level.

        Args:
            severity: Severity level (HIGH, MEDIUM, LOW)
            findings: List of findings for this severity
        """
        color = self.SEVERITY_COLORS[severity]
        icon = self.SEVERITY_ICONS.get(severity, "")

        for i, finding in enumerate(findings, 1):
            # Header for each finding
            location = self._format_location(finding)
            header = Text()
            header.append(f"{i}. ", style=color)
            header.append(f"[{finding.category}]", style="bold")
            header.append(f" {location}")
            header.append(f" - {finding.description}")

            self.console.print(header)

            # Suggestion
            if finding.suggestion:
                self.console.print(f"   Suggestion: {finding.suggestion}")

            # Code snippet with syntax highlighting
            if finding.code_snippet:
                self._render_code_snippet(finding.code_snippet)

            self.console.print()

    def _render_code_snippet(self, snippet: str) -> None:
        """Render code snippet with syntax highlighting.

        Args:
            snippet: Code snippet to render
        """
        # Detect language from file extension or default to python
        syntax = Syntax(snippet.strip(), "python", line_numbers=True, word_wrap=True)
        self.console.print(syntax)

    def _format_location(self, finding: Finding) -> str:
        """Format file location for display.

        Args:
            finding: Finding object

        Returns:
            Formatted location string
        """
        if finding.line_number:
            return f"`{finding.file_path}:{finding.line_number}`"
        return f"`{finding.file_path}`"

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

    def _count_by_severity(self, result: ReviewResult) -> dict[str, int]:
        """Count findings by severity.

        Args:
            result: ReviewResult with findings

        Returns:
            Dictionary with severity counts
        """
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in result.findings:
            if finding.severity in counts:
                counts[finding.severity] += 1
        return counts

    def _group_by_severity(self, result: ReviewResult) -> dict[str, list[Finding]]:
        """Group findings by severity.

        Args:
            result: ReviewResult with findings

        Returns:
            Dictionary with severity as keys and finding lists as values
        """
        groups: dict[str, list[Finding]] = {"HIGH": [], "MEDIUM": [], "LOW": []}
        for finding in result.findings:
            if finding.severity in groups:
                groups[finding.severity].append(finding)
        return groups

    def _render_plain(self, result: ReviewResult) -> None:
        """Render plain text for non-TTY outputs.

        Args:
            result: ReviewResult to render
        """
        print(f"Code Review Results")
        print(f"Platform: {result.platform}")
        print(f"Confidence: {result.confidence:.0%}")
        print()

        for finding in result.findings:
            location = self._format_location(finding)
            print(f"[{finding.severity}] {finding.category}: {location}")
            print(f"  {finding.description}")
            if finding.suggestion:
                print(f"  Suggestion: {finding.suggestion}")
            print()

    def render_progress(self, message: str = "Analyzing code...") -> Progress:
        """Create a progress spinner for long operations.

        Args:
            message: Progress message to display

        Returns:
            Rich Progress object
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )
        return progress
