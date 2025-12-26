"""
File filtering for git diff operations.
"""

from pathlib import Path
from typing import Iterable, Optional

from shield_pr.core.errors import FilterError
from shield_pr.git.filter_patterns import default_ignore_patterns
from shield_pr.git.filter_matcher import PatternMatcher


class DiffFilter:
    """
    Filter files based on patterns and attributes.

    Supports:
    - Gitignore-style patterns
    - File size limits
    - Binary file detection
    """

    def __init__(
        self,
        ignore_patterns: Optional[list[str]] = None,
        max_file_size: int = 100_000,
        respect_gitignore: bool = True
    ):
        """
        Initialize diff filter.

        Args:
            ignore_patterns: List of glob patterns to ignore.
            max_file_size: Maximum file size in bytes (0 = no limit).
            respect_gitignore: Whether to read .gitignore.
        """
        self.ignore_patterns = ignore_patterns or default_ignore_patterns.copy()
        self.max_file_size = max_file_size
        self.respect_gitignore = respect_gitignore
        self._matcher: Optional[PatternMatcher] = None

    def should_ignore(self, file_path: str, repo_root: Path) -> bool:
        """Check if file should be ignored."""
        if self._matcher is None:
            self._matcher = PatternMatcher(
                self.ignore_patterns,
                self.respect_gitignore,
                repo_root
            )
        return self._matcher.matches(file_path)

    def is_too_large(self, file_path: str, repo_root: Path) -> bool:
        """Check if file exceeds size limit."""
        if self.max_file_size == 0:
            return False

        full_path = repo_root / file_path
        if not full_path.exists():
            return False

        try:
            return full_path.stat().st_size > self.max_file_size
        except OSError:
            return False

    def is_binary_file(self, file_path: str, repo_root: Path) -> bool:
        """Check if file is binary."""
        full_path = repo_root / file_path
        if not full_path.exists():
            return False

        try:
            with open(full_path, 'rb') as f:
                chunk = f.read(8192)
                return b'\x00' in chunk
        except (OSError, IOError):
            return False

    def filter_files(self, files: Iterable[str], repo_root: Path) -> list[str]:
        """Filter list of files."""
        filtered = []

        for file_path in files:
            if self.should_ignore(file_path, repo_root):
                continue
            if self.is_too_large(file_path, repo_root):
                continue
            if self.is_binary_file(file_path, repo_root):
                continue
            filtered.append(file_path)

        return filtered
