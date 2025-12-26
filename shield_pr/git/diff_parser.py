"""
Parse unified diff format into structured changes.
"""

import re
from typing import Optional

from shield_pr.git.models import ParsedDiff, DiffChange


class DiffParser:
    """
    Parse unified diff format into structured data.

    Handles:
    - Extracting added/removed/context lines
    - Line number tracking
    - Multi-hunk diffs
    """

    # Unified diff hunk header pattern
    HUNK_PATTERN = re.compile(r'^@@ -(\d+),?\d* \+(\d+),?\d* @@')

    def __init__(self) -> None:
        """Initialize diff parser."""
        self.reset()

    def reset(self) -> None:
        """Reset parser state."""
        self.current_line = 0
        self.old_line = 0
        self.in_hunk = False

    def parse(self, diff_text: str) -> list["ParsedDiff"]:
        """
        Parse diff text into structured changes.

        Args:
            diff_text: Unified diff format text.

        Returns:
            List of ParsedDiff objects.
        """
        self.reset()

        if not diff_text or not diff_text.strip():
            return []

        results = []
        current_diff = None
        lines = diff_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # File headers
            if line.startswith('---'):
                if current_diff and current_diff.added:
                    results.append(current_diff)
                current_diff = ParsedDiff(
                    file_path="",
                    added=[],
                    removed=[],
                    context=[],
                    old_file=line[4:].strip()
                )
            elif line.startswith('+++'):
                if current_diff:
                    # Extract file path from +++ line
                    # Handle: +++ b/path/to/file or +++ /dev/null
                    path = line[4:].strip()
                    if path.startswith('b/'):
                        path = path[2:]
                    current_diff.new_file = path
                    current_diff.file_path = path

            # Hunk header
            elif self.HUNK_PATTERN.match(line):
                self._parse_hunk_header(line)
                self.in_hunk = True

            # Diff content
            elif self.in_hunk and current_diff:
                self._parse_diff_line(line, current_diff)

            i += 1

        # Append last diff
        if current_diff and current_diff.file_path:
            results.append(current_diff)

        return results

    def parse_single_file(self, diff_text: str) -> "ParsedDiff | None":
        """
        Parse diff for a single file.

        Args:
            diff_text: Unified diff format text.

        Returns:
            ParsedDiff object or None if parsing fails.
        """
        results = self.parse(diff_text)
        return results[0] if results else None

    def extract_changes(self, diff_text: str) -> dict[str, list[tuple[int, str] | str]]:
        """
        Parse unified diff, extract added/modified lines.

        Args:
            diff_text: Unified diff format text.

        Returns:
            Dict with 'added', 'removed', 'modified' lists.
        """
        parsed = self.parse(diff_text)
        if not parsed:
            return {"added": [], "removed": [], "modified": []}

        result: dict[str, list[tuple[int, str] | str]] = {"added": [], "removed": [], "modified": []}

        for diff in parsed:
            for change in diff.added:
                result["added"].append((change.line_number, change.content))

            for change in diff.removed:
                result["removed"].append(change.content)

            # Track modified (added + removed at same location)
            for change in diff.context:
                if any(c.line_number == change.line_number for c in diff.added):
                    result["modified"].append(str(change.line_number))

        return result

    def _parse_hunk_header(self, line: str) -> None:
        """
        Parse hunk header to set line numbers.

        Args:
            line: Hunk header line (e.g., "@@ -10,5 +10,7 @@").
        """
        match = self.HUNK_PATTERN.match(line)
        if match:
            self.old_line = int(match.group(1))
            self.current_line = int(match.group(2))

    def _parse_diff_line(self, line: str, diff: ParsedDiff) -> None:
        """
        Parse a single diff line and update parsed diff.

        Args:
            line: Diff line content.
            diff: ParsedDiff to update.
        """
        if not line:
            return

        if line.startswith('+') and not line.startswith('+++'):
            # Added line
            diff.added.append(DiffChange(
                line_number=self.current_line,
                content=line[1:],
                change_type='added'
            ))
            self.current_line += 1

        elif line.startswith('-') and not line.startswith('---'):
            # Removed line
            diff.removed.append(DiffChange(
                line_number=self.old_line,
                content=line[1:],
                change_type='removed'
            ))
            self.old_line += 1

        else:
            # Context line
            diff.context.append(DiffChange(
                line_number=self.current_line,
                content=line[1:] if line.startswith(' ') else line,
                change_type='context'
            ))
            self.current_line += 1
            self.old_line += 1
