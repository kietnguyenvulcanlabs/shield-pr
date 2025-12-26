"""File reader utility for code review operations."""

from pathlib import Path
from typing import Dict, Optional

from shield_pr.utils.logger import logger


class FileReader:
    """Read and prepare file contents for review.

    Handles:
    - Reading file contents with encoding fallback
    - Truncating large files
    - Extracting relevant code sections
    """

    DEFAULT_MAX_SIZE = 100 * 1024  # 100KB default
    ENCODINGS = ["utf-8", "latin-1", "cp1252"]

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        """Initialize file reader.

        Args:
            max_size: Maximum file size in bytes
        """
        self.max_size = max_size

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file content with encoding fallback.

        Args:
            file_path: Path to the file

        Returns:
            File content or None if read fails
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        if not path.is_file():
            logger.warning(f"Not a file: {file_path}")
            return None

        # Check file size
        try:
            file_size = path.stat().st_size
            if file_size > self.max_size:
                logger.info(
                    f"File {file_path} ({file_size} bytes) exceeds "
                    f"max size ({self.max_size}), will truncate"
                )
        except OSError as e:
            logger.warning(f"Cannot get file size: {e}")
            return None

        # Try different encodings
        for encoding in self.ENCODINGS:
            try:
                content = path.read_text(encoding=encoding, errors="ignore")

                # Truncate if too large
                if len(content.encode("utf-8")) > self.max_size:
                    content = self._truncate_content(content, file_path)

                logger.debug(f"Read {file_path} with encoding {encoding}")
                return content

            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Failed to read {file_path} with {encoding}: {e}")
                continue

        logger.error(f"Failed to read {file_path} with any encoding")
        return None

    def read_files(self, file_paths: list[str]) -> Dict[str, Optional[str]]:
        """Read multiple files.

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping file paths to contents
        """
        results: Dict[str, Optional[str]] = {}

        for file_path in file_paths:
            results[file_path] = self.read_file(file_path)

        return results

    def _truncate_content(self, content: str, file_path: str) -> str:
        """Truncate content to max size while preserving structure.

        Args:
            content: Full file content
            file_path: Path to file (for logging)

        Returns:
            Truncated content with truncation marker
        """
        target_size = self.max_size - 200  # Leave room for marker

        # Try to truncate at line boundary
        lines = content.split("\n")
        truncated = []
        current_size = 0

        for line in lines:
            line_size = len(line.encode("utf-8")) + 1  # +1 for newline

            if current_size + line_size > target_size:
                break

            truncated.append(line)
            current_size += line_size

        result = "\n".join(truncated)
        marker = f"\n\n[... File truncated at {current_size} bytes ...]\n"

        logger.info(f"Truncated {file_path} from {len(content)} to {current_size} bytes")
        return result + marker

    def read_diff_hunks(
        self, file_path: str, line_numbers: list[int], context_lines: int = 5
    ) -> str:
        """Read specific sections of a file based on line numbers.

        Args:
            file_path: Path to the file
            line_numbers: List of line numbers to extract
            context_lines: Number of context lines around each line

        Returns:
            Extracted content with context
        """
        content = self.read_file(file_path)
        if not content:
            return ""

        lines = content.split("\n")
        if not lines:
            return ""

        # Build ranges around each line number
        ranges = []
        for line_num in line_numbers:
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            ranges.append((start, end))

        # Merge overlapping ranges
        merged = self._merge_ranges(ranges)

        # Extract lines
        result_lines = []
        for start, end in merged:
            result_lines.extend(lines[start:end])
            result_lines.append("...")  # Separator between ranges

        return "\n".join(result_lines)

    def _merge_ranges(self, ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Merge overlapping or adjacent ranges.

        Args:
            ranges: List of (start, end) tuples

        Returns:
            Merged list of ranges
        """
        if not ranges:
            return []

        # Sort by start
        sorted_ranges = sorted(ranges, key=lambda r: r[0])

        merged = [sorted_ranges[0]]

        for current in sorted_ranges[1:]:
            prev = merged[-1]

            # If current overlaps or is adjacent to prev
            if current[0] <= prev[1] + 1:
                # Merge
                merged[-1] = (prev[0], max(prev[1], current[1]))
            else:
                merged.append(current)

        return merged
