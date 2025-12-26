"""
Data models for git operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FileChange:
    """Represents a file changed in git."""
    path: str
    change_type: str  # 'A', 'M', 'D', 'R'
    old_path: Optional[str] = None  # For renames
    patch: str = ""


@dataclass
class DiffChange:
    """Represents a single line change in a diff."""
    line_number: int
    content: str
    change_type: str  # 'added', 'removed', 'context'


@dataclass
class ParsedDiff:
    """Result of parsing a unified diff."""
    file_path: str
    added: list[DiffChange]
    removed: list[DiffChange]
    context: list[DiffChange]
    old_file: Optional[str] = None
    new_file: Optional[str] = None
