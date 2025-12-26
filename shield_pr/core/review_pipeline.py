"""Review pipeline for orchestrating code review operations.

Coordinates file reading, platform detection, chain execution,
and result synthesis for complete code review workflow.
"""

from typing import Any, Dict, List, Optional

from shield_pr.config.models import Config
from shield_pr.core.errors import ReviewError
from shield_pr.core.llm_client import LLMClient
from shield_pr.detection.detector import PlatformDetector
from shield_pr.models.review_result import ReviewResult
from shield_pr.chains import get_chain, UniversalReviewChain, SynthesisChain
from shield_pr.utils.file_reader import FileReader
from shield_pr.utils.logger import logger


class ReviewPipeline:
    """Orchestrates complete code review workflow.

    Pipeline stages:
    1. File reading - Load file contents
    2. Platform detection - Identify platform for each file
    3. Chain execution - Run platform-specific and universal reviews
    4. Synthesis - Combine and deduplicate findings
    5. Aggregation - Combine multi-file results
    """

    def __init__(self, config: Config):
        """Initialize review pipeline.

        Args:
            config: Configuration with API and review settings
        """
        self.config = config
        self.llm_client = LLMClient(config.api)
        self.detector = PlatformDetector()
        self.file_reader = FileReader()
        self.synthesis_chain = SynthesisChain()

    def review_files(
        self,
        file_paths: List[str],
        platform_override: Optional[str] = None,
        depth: Optional[str] = None,
    ) -> ReviewResult:
        """Review multiple files and aggregate results.

        Args:
            file_paths: List of file paths to review
            platform_override: Optional platform override for all files
            depth: Review depth (defaults to config)

        Returns:
            Aggregated ReviewResult

        Raises:
            ReviewError: If review fails
        """
        if not file_paths:
            raise ReviewError("No files provided for review")

        depth = depth or self.config.review.depth

        logger.info(f"Starting review of {len(file_paths)} file(s) at depth '{depth}'")

        # Read all files
        file_contents = self.file_reader.read_files(file_paths)

        # Filter out failed reads
        valid_files = {
            path: content
            for path, content in file_contents.items()
            if content is not None
        }

        if not valid_files:
            raise ReviewError("No valid files could be read")

        logger.info(f"Successfully read {len(valid_files)}/{len(file_paths)} files")

        # Review each file
        all_findings = []
        platforms_found = set()

        for file_path, content in valid_files.items():
            try:
                result = self._review_single_file(
                    file_path, content, platform_override, depth
                )
                all_findings.extend(result.findings)
                if result.platform:
                    platforms_found.add(result.platform)
            except ReviewError as e:
                logger.warning(f"Failed to review {file_path}: {e}")
                # Continue with other files
                all_findings.append(
                    self._create_error_finding(file_path, str(e))
                )

        # Aggregate results
        return self._aggregate_results(
            all_findings,
            list(platforms_found) or ["unknown"],
            len(valid_files),
        )

    def review_diff(
        self,
        file_changes: Dict[str, str],
        platform_override: Optional[str] = None,
        depth: Optional[str] = None,
    ) -> ReviewResult:
        """Review git diff changes.

        Args:
            file_changes: Dictionary mapping file paths to diff patches
            platform_override: Optional platform override
            depth: Review depth (defaults to config)

        Returns:
            ReviewResult with findings from diff review

        Raises:
            ReviewError: If review fails
        """
        if not file_changes:
            raise ReviewError("No file changes provided for review")

        depth = depth or self.config.review.depth

        logger.info(f"Starting diff review of {len(file_changes)} file(s) at depth '{depth}'")

        all_findings = []
        platforms_found = set()
        files_reviewed = 0

        for file_path, patch in file_changes.items():
            try:
                # Detect platform from file path
                platform, _, _ = self.detector.detect(
                    file_path, manual_platform=platform_override
                )

                if not platform:
                    logger.debug(f"Could not detect platform for {file_path}, skipping")
                    continue

                platforms_found.add(platform)

                # Review the diff patch
                result = self._review_diff_content(
                    file_path, patch, platform, depth
                )
                all_findings.extend(result.findings)
                files_reviewed += 1

            except ReviewError as e:
                logger.warning(f"Failed to review diff for {file_path}: {e}")
                all_findings.append(
                    self._create_error_finding(file_path, str(e))
                )

        logger.info(f"Successfully reviewed {files_reviewed}/{len(file_changes)} files")

        return self._aggregate_results(
            all_findings,
            list(platforms_found) or ["unknown"],
            files_reviewed,
        )

    def _review_single_file(
        self,
        file_path: str,
        content: str,
        platform_override: Optional[str],
        depth: str,
    ) -> ReviewResult:
        """Review a single file with full content.

        Args:
            file_path: Path to file
            content: File content
            platform_override: Platform override
            depth: Review depth

        Returns:
            ReviewResult for this file
        """
        # Detect platform
        platform, confidence, _ = self.detector.detect(
            file_path, content, manual_platform=platform_override
        )

        if not platform:
            platform = "backend"  # Default fallback
            logger.debug(f"Using default platform 'backend' for {file_path}")

        logger.debug(f"Reviewing {file_path} as {platform} (confidence: {confidence:.2%})")

        # Get platform chain
        platform_chain = get_chain(platform, self.llm_client, depth)

        # Execute platform review
        platform_result = platform_chain.execute(content, file_path)

        # Execute universal review (for cross-cutting concerns)
        universal_chain = UniversalReviewChain(self.llm_client, depth)
        universal_result = universal_chain.execute(content, file_path)

        # Synthesize results
        final_result = self.synthesis_chain.synthesize(
            platform_result, universal_result
        )

        return final_result

    def _review_diff_content(
        self,
        file_path: str,
        patch: str,
        platform: str,
        depth: str,
    ) -> ReviewResult:
        """Review a diff patch for a file.

        Args:
            file_path: Path to file
            patch: Git diff patch
            platform: Detected platform
            depth: Review depth

        Returns:
            ReviewResult for this diff
        """
        logger.debug(f"Reviewing diff for {file_path} as {platform}")

        # Create a specialized prompt for diff review
        diff_context = self._create_diff_context(patch, file_path)

        # Get platform chain
        platform_chain = get_chain(platform, self.llm_client, depth)

        # Execute review with diff context
        platform_result = platform_chain.execute(diff_context, file_path)

        # Execute universal review
        universal_chain = UniversalReviewChain(self.llm_client, depth)
        universal_result = universal_chain.execute(diff_context, file_path)

        # Synthesize results
        final_result = self.synthesis_chain.synthesize(
            platform_result, universal_result
        )

        return final_result

    def _create_diff_context(self, patch: str, file_path: str) -> str:
        """Create review context from diff patch.

        Args:
            patch: Git diff patch
            file_path: File path

        Returns:
            Formatted context for review
        """
        return f"""File: {file_path}

Changes to review:
```diff
{patch}
```

Please review the above changes for:
- Security vulnerabilities
- Code quality issues
- Bugs or logic errors
- Performance concerns
- Best practices violations
"""
        # Fallback placeholder if chains don't support diff format
        return patch

    def _aggregate_results(
        self,
        findings: List[Any],
        platforms: List[str],
        files_count: int,
    ) -> ReviewResult:
        """Aggregate findings from multiple files.

        Args:
            findings: All findings from all files
            platforms: List of platforms found
            files_count: Number of files reviewed

        Returns:
            Aggregated ReviewResult
        """
        # Sort by severity and file
        from shield_pr.chains.synthesis_chain import SynthesisChain

        synthesis = SynthesisChain()
        prioritized = synthesis._prioritize(findings)

        # Generate summary
        summary = self._generate_aggregate_summary(
            prioritized, platforms, files_count
        )

        # Calculate overall confidence
        confidence = self._calculate_aggregate_confidence(findings, files_count)

        # Determine primary platform
        primary_platform = platforms[0] if platforms else "unknown"

        return ReviewResult(
            platform=primary_platform,
            findings=prioritized,
            summary=summary,
            confidence=confidence,
        )

    def _generate_aggregate_summary(
        self,
        findings: List[Any],
        platforms: List[str],
        files_count: int,
    ) -> str:
        """Generate summary for multi-file review.

        Args:
            findings: All findings
            platforms: Platforms found
            files_count: Number of files

        Returns:
            Summary text
        """
        if not findings:
            return f"Reviewed {files_count} file(s) across {len(set(platforms))} platform(s). No issues found."

        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")
        low = sum(1 for f in findings if f.severity == "LOW")

        parts = [f"Reviewed {files_count} file(s)."]

        severity_parts = []
        if high > 0:
            severity_parts.append(f"{high} high")
        if medium > 0:
            severity_parts.append(f"{medium} medium")
        if low > 0:
            severity_parts.append(f"{low} low")

        if severity_parts:
            parts.append(f"Found {', '.join(severity_parts)} severity issue(s).")

        if platforms:
            platforms_str = ", ".join(set(platforms))
            parts.append(f"Platforms: {platforms_str}")

        return " ".join(parts)

    def _calculate_aggregate_confidence(self, findings: List[Any], files_count: int) -> float:
        """Calculate confidence for aggregated results.

        Args:
            findings: All findings
            files_count: Number of files

        Returns:
            Confidence score
        """
        if not findings or files_count == 0:
            return 0.5

        # Base confidence on findings per file ratio
        # More files with findings = higher confidence in review
        base = min(len(findings) / files_count / 2, 1.0)

        return round(base, 2)

    def _create_error_finding(self, file_path: str, error: str) -> Any:
        """Create a finding for review errors.

        Args:
            file_path: File that failed
            error: Error message

        Returns:
            Finding object
        """
        from shield_pr.models.finding import Finding

        return Finding(
            severity="LOW",
            category="review",
            file_path=file_path,
            line_number=None,
            description=f"Could not review file: {error}",
            suggestion="Check file format and try again.",
        )
