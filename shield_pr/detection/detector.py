"""Platform detector orchestrator.

Coordinates extension-based, content-based, and LLM-based detection.
"""

from pathlib import Path
from typing import Optional, Tuple

from ..utils.logger import logger
from .confidence import calculate_confidence, should_use_llm_fallback
from .file_analyzer import FileAnalyzer
from .patterns import is_valid_platform


class PlatformDetector:
    """Main platform detection orchestrator."""

    def __init__(self) -> None:
        """Initialize platform detector."""
        self.analyzer = FileAnalyzer()

    def detect(
        self,
        file_path: str,
        content: Optional[str] = None,
        manual_platform: Optional[str] = None,
    ) -> Tuple[Optional[str], float, str]:
        """Detect platform for a file.

        Args:
            file_path: Path to the file
            content: Optional file content (reads from disk if not provided)
            manual_platform: Manual platform override from CLI

        Returns:
            Tuple of (platform, confidence, reasoning)
        """
        # Manual override takes precedence
        if manual_platform:
            if is_valid_platform(manual_platform):
                logger.debug(f"Using manual platform: {manual_platform}")
                return (manual_platform, 1.0, "Manual selection via --platform flag")
            else:
                logger.warning(f"Invalid manual platform: {manual_platform}")
                # Continue with auto-detection

        # Extension-based detection
        ext_platform, ext_confidence = self.analyzer.detect_by_extension(file_path)
        logger.debug(
            f"Extension detection: platform={ext_platform}, "
            f"confidence={ext_confidence:.2%}"
        )

        # Content-based detection
        content_platform: Optional[str] = None
        content_confidence = 0.0

        if content:
            content_platform, content_confidence = self.analyzer.detect_by_content(
                content
            )
            logger.debug(
                f"Content detection: platform={content_platform}, "
                f"confidence={content_confidence:.2%}"
            )
        elif ext_confidence < 0.8:
            # Read file for content analysis if extension is ambiguous
            try:
                file_content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                content_platform, content_confidence = (
                    self.analyzer.detect_by_content(file_content)
                )
                logger.debug(
                    f"Content detection: platform={content_platform}, "
                    f"confidence={content_confidence:.2%}"
                )
            except Exception as e:
                logger.debug(f"Failed to read file for content analysis: {e}")

        # Calculate final result
        platform, confidence, reasoning = calculate_confidence(
            ext_platform, ext_confidence, content_platform, content_confidence
        )

        logger.info(
            f"Detection result for {Path(file_path).name}: "
            f"platform={platform}, confidence={confidence:.2%}"
        )
        logger.debug(f"Reasoning: {reasoning}")

        return (platform, confidence, reasoning)

    def detect_batch(
        self, files: list[str], manual_platform: Optional[str] = None
    ) -> dict[str, Tuple[Optional[str], float, str]]:
        """Detect platforms for multiple files.

        Args:
            files: List of file paths
            manual_platform: Optional manual platform override

        Returns:
            Dictionary mapping file paths to detection results
        """
        results = {}
        for file_path in files:
            results[file_path] = self.detect(file_path, manual_platform=manual_platform)
        return results

    def get_detection_summary(
        self, results: dict[str, Tuple[Optional[str], float, str]]
    ) -> dict[str, int]:
        """Get summary of detection results.

        Args:
            results: Detection results from detect_batch

        Returns:
            Dictionary with platform counts
        """
        summary: dict[str, int] = {}
        for _, (platform, _, _) in results.items():
            if platform:
                summary[platform] = summary.get(platform, 0) + 1
            else:
                summary["unknown"] = summary.get("unknown", 0) + 1
        return summary
