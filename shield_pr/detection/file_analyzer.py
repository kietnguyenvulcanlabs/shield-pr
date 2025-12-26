"""File analyzer for platform detection.

Analyzes file extensions and content to determine platform.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from .patterns import (
    EXTENSION_WEIGHTS,
    IMPORT_PATTERNS,
    KEYWORD_PATTERNS,
    PLATFORM_PATTERNS,
)


class FileAnalyzer:
    """Analyzes files for platform detection."""

    def __init__(self) -> None:
        """Initialize file analyzer."""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        self.keyword_regex = {
            platform: re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for platform, pattern in KEYWORD_PATTERNS.items()
        }
        self.import_regex = {
            platform: re.compile(pattern, re.MULTILINE)
            for platform, pattern in IMPORT_PATTERNS.items()
        }

    def detect_by_extension(self, file_path: str) -> Tuple[Optional[str], float]:
        """Detect platform from file extension.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (platform, confidence) or (None, 0.0) if unknown
        """
        ext = Path(file_path).suffix.lower()
        if not ext:
            return (None, 0.0)

        if ext not in EXTENSION_WEIGHTS:
            return (None, 0.0)

        weights = EXTENSION_WEIGHTS[ext]
        if len(weights) == 1:
            # Unique extension, high confidence
            platform = list(weights.keys())[0]
            return (platform, weights[platform])

        # Multiple platforms, return highest weight
        platform_tuple = max(weights.items(), key=lambda x: x[1])
        return (platform_tuple[0], platform_tuple[1])

    def detect_by_content(self, content: str) -> Tuple[Optional[str], float]:
        """Detect platform from file content.

        Args:
            content: File content as string

        Returns:
            Tuple of (platform, confidence) or (None, 0.0) if unknown
        """
        if not content or not content.strip():
            return (None, 0.0)

        # Limit analysis to first 500 lines for performance
        lines = content.split("\n")[:500]
        limited_content = "\n".join(lines)

        scores: Dict[str, float] = {}

        # Analyze imports (40% weight)
        import_scores = self._analyze_imports(limited_content)
        for platform, score in import_scores.items():
            scores[platform] = scores.get(platform, 0.0) + score * 0.4

        # Analyze keywords (40% weight)
        keyword_scores = self._analyze_keywords(limited_content)
        for platform, score in keyword_scores.items():
            scores[platform] = scores.get(platform, 0.0) + score * 0.4

        # Analyze config files mentioned (20% weight)
        config_scores = self._analyze_config_mentions(limited_content)
        for platform, score in config_scores.items():
            scores[platform] = scores.get(platform, 0.0) + score * 0.2

        if not scores:
            return (None, 0.0)

        # Return platform with highest score
        platform_tuple = max(scores.items(), key=lambda x: x[1])
        return (platform_tuple[0], min(platform_tuple[1], 1.0))  # Cap at 1.0

    def _analyze_imports(self, content: str) -> Dict[str, float]:
        """Analyze import statements for platform detection.

        Args:
            content: File content

        Returns:
            Dictionary of platform scores
        """
        scores: Dict[str, float] = {}
        for platform, pattern in self.import_regex.items():
            matches = pattern.findall(content)
            if matches:
                # Score based on number of matches (cap at 1.0)
                scores[platform] = min(len(matches) * 0.2, 1.0)
        return scores

    def _analyze_keywords(self, content: str) -> Dict[str, float]:
        """Analyze keywords for platform detection.

        Args:
            content: File content

        Returns:
            Dictionary of platform scores
        """
        scores: Dict[str, float] = {}
        for platform, pattern in self.keyword_regex.items():
            matches = pattern.findall(content)
            if matches:
                # Score based on number of unique matches (cap at 1.0)
                unique_matches = len(set(matches))
                scores[platform] = min(unique_matches * 0.15, 1.0)
        return scores

    def _analyze_config_mentions(self, content: str) -> Dict[str, float]:
        """Analyze mentions of config files for platform detection.

        Args:
            content: File content

        Returns:
            Dictionary of platform scores
        """
        scores: Dict[str, float] = {}
        content_lower = content.lower()

        for platform, patterns in PLATFORM_PATTERNS.items():
            config_files = patterns.get("files", [])
            matches = 0
            for config_file in config_files:
                if config_file.lower() in content_lower:
                    matches += 1

            if matches > 0:
                scores[platform] = min(matches * 0.3, 1.0)

        return scores

    def get_file_info(self, file_path: str, content: Optional[str] = None) -> Dict[str, str]:
        """Get file information for logging.

        Args:
            file_path: Path to file
            content: Optional file content

        Returns:
            Dictionary with file info
        """
        path = Path(file_path)
        info = {
            "name": path.name,
            "extension": path.suffix,
            "size": str(path.stat().st_size) if path.exists() else "unknown",
        }

        if content:
            info["lines"] = str(len(content.split("\n")))

        return info
