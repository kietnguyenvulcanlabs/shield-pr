"""
Pattern matching for file filtering.
"""

from fnmatch import fnmatch
from pathlib import Path
from typing import Optional


class PatternMatcher:
    """Match file paths against glob patterns."""

    def __init__(
        self,
        patterns: list[str],
        respect_gitignore: bool,
        repo_root: Path
    ):
        """Initialize pattern matcher."""
        self.patterns = patterns.copy()
        self.respect_gitignore = respect_gitignore
        self.repo_root = repo_root
        self._gitignore_patterns: list[str] = []

        if respect_gitignore:
            self._load_gitignore()

    def matches(self, file_path: str) -> bool:
        """Check if file path matches any pattern."""
        # Check user patterns
        for pattern in self.patterns:
            if self._match_pattern(file_path, pattern):
                return True

        # Check gitignore
        for pattern in self._gitignore_patterns:
            if self._match_pattern(file_path, pattern):
                return True

        return False

    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """Match file path against single pattern."""
        if pattern.endswith('/'):
            pattern = pattern + '**'

        if pattern.startswith('!'):
            return False

        parts = file_path.split('/')
        pattern_parts = pattern.split('/')

        for i in range(len(parts) - len(pattern_parts) + 1):
            subpath = '/'.join(parts[i:])
            if fnmatch(subpath, pattern) or fnmatch('/'.join(parts[i:]), pattern):
                return True

        return fnmatch(file_path, pattern)

    def _load_gitignore(self) -> None:
        """Load patterns from .gitignore."""
        gitignore_path = self.repo_root / '.gitignore'
        self._gitignore_patterns = []

        if not gitignore_path.exists():
            return

        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self._gitignore_patterns.append(line)
        except OSError:
            pass
