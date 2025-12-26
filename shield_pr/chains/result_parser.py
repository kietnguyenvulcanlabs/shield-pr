"""Parse chain results into structured findings."""

import re
from typing import Any, Dict, List, Literal

from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class ResultParser:
    """Parse LLM chain outputs into structured findings.

    Extracts severity, category, description, and suggestions from
    chain stage outputs and consolidates into ReviewResult.
    """

    # Patterns for extracting findings from LLM output
    SEVERITY_PATTERN = re.compile(r"\b(HIGH|MEDIUM|LOW)\b", re.IGNORECASE)
    CATEGORY_PATTERN = re.compile(
        r"\b(security|performance|bug|best.practice|code.smell|"
        r"maintainability|error.handling|architecture|documentation)\b",
        re.IGNORECASE,
    )
    LINE_NUMBER_PATTERN = re.compile(r"line\s+(\d+)", re.IGNORECASE)
    CODE_SNIPPET_PATTERN = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)

    def extract_findings(self, result: Dict[str, Any], file_path: str) -> List[Finding]:
        """Extract findings from chain execution results.

        Args:
            result: Dictionary containing all stage outputs
            file_path: Path to the reviewed file

        Returns:
            List of Finding objects
        """
        findings: List[Finding] = []

        # Process each stage output
        for stage_name, stage_output in result.items():
            if not stage_name.endswith("_result"):
                continue

            # Get text output
            text = stage_output.get("text", "") if isinstance(stage_output, dict) else str(stage_output)

            # Extract findings from this stage
            stage_findings = self._parse_stage_output(text, stage_name, file_path)
            findings.extend(stage_findings)

        # If no findings extracted, create a generic one
        if not findings:
            findings.append(
                Finding(
                    severity="LOW",
                    category="review",
                    file_path=file_path,
                    line_number=None,
                    description="Code review completed. No specific issues found.",
                    suggestion="Continue following best practices.",
                )
            )

        return findings

    def _parse_stage_output(self, text: str, stage_name: str, file_path: str) -> List[Finding]:
        """Parse findings from a single stage output.

        Args:
            text: Stage output text
            stage_name: Name of the stage (e.g., "security_result")
            file_path: Path to the reviewed file

        Returns:
            List of Finding objects from this stage
        """
        findings: List[Finding] = []

        # Split by common delimiters to find individual findings
        # Common patterns: "- Issue:", "1.", "•", or newlines with indicators
        segments = self._split_into_segments(text)

        for segment in segments:
            finding = self._parse_finding_segment(segment, stage_name, file_path)
            if finding:
                findings.append(finding)

        return findings

    def _split_into_segments(self, text: str) -> List[str]:
        """Split text into potential finding segments.

        Args:
            text: Full stage output text

        Returns:
            List of text segments, each potentially containing a finding
        """
        segments: List[str] = []

        # Try various delimiters
        delimiters = [
            r"\n\s*-\s+",  # Bullet points
            r"\n\s*\d+\.\s+",  # Numbered lists
            r"\n\s*•\s+",  # Bullet points with •
            r"\n\s*[*]\s+",  # Bullet points with *
            r"(?=\b[HIGH|MEDIUM|LOW]\b)",  # Severity markers
        ]

        for delimiter in delimiters:
            parts = re.split(delimiter, text)
            if len(parts) > 1:
                segments = parts
                break

        # If no delimiters found, treat whole text as one segment
        if not segments:
            segments = [text]

        return [s.strip() for s in segments if s.strip()]

    def _parse_finding_segment(self, segment: str, stage_name: str, file_path: str) -> Finding | None:
        """Parse a single finding from a text segment.

        Args:
            segment: Text segment potentially containing a finding
            stage_name: Name of the source stage
            file_path: Path to the reviewed file

        Returns:
            Finding object or None if parsing fails
        """
        # Extract severity
        severity = self._extract_severity(segment)

        # Extract category from stage name or content
        category = self._extract_category(segment, stage_name)

        # Extract line number
        line_number = self._extract_line_number(segment)

        # Extract code snippet
        code_snippet = self._extract_code_snippet(segment)

        # Extract description (main text without structured parts)
        description = self._extract_description(segment)

        # Extract suggestion
        suggestion = self._extract_suggestion(segment)

        if not description:
            return None

        return Finding(
            severity=severity,
            category=category,
            file_path=file_path,
            line_number=line_number,
            description=description,
            suggestion=suggestion,
            code_snippet=code_snippet,
        )

    def _extract_severity(self, text: str) -> Literal["HIGH", "MEDIUM", "LOW"]:
        """Extract severity level from text.

        Args:
            text: Text to search

        Returns:
            Severity level (HIGH, MEDIUM, or LOW as default)
        """
        match = self.SEVERITY_PATTERN.search(text)
        if match:
            severity = match.group(1).upper()
            if severity in ("HIGH", "MEDIUM", "LOW"):
                return severity  # type: ignore[return-value]
        return "LOW"

    def _extract_category(self, text: str, stage_name: str) -> str:
        """Extract category from text or stage name.

        Args:
            text: Text to search
            stage_name: Source stage name

        Returns:
            Category name
        """
        # Try to extract from text first
        match = self.CATEGORY_PATTERN.search(text)
        if match:
            return match.group(1).replace(".", " ").lower()

        # Fall back to stage name
        base_name = stage_name.replace("_result", "").replace("_", " ")
        return base_name.lower()

    def _extract_line_number(self, text: str) -> int | None:
        """Extract line number from text.

        Args:
            text: Text to search

        Returns:
            Line number or None
        """
        match = self.LINE_NUMBER_PATTERN.search(text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def _extract_code_snippet(self, text: str) -> str | None:
        """Extract code snippet from text.

        Args:
            text: Text to search

        Returns:
            Code snippet or None
        """
        match = self.CODE_SNIPPET_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_description(self, text: str) -> str:
        """Extract main description from text.

        Args:
            text: Text to extract from

        Returns:
            Description text
        """
        # Remove code blocks and common prefixes
        cleaned = self.CODE_SNIPPET_PATTERN.sub("", text)

        # Remove common suggestion prefixes
        suggestion_prefixes = [
            r"Suggestion:.*",
            r"Recommendation:.*",
            r"Fix:.*",
            r"Solution:.*",
        ]

        for prefix in suggestion_prefixes:
            cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

        return cleaned.strip()

    def _extract_suggestion(self, text: str) -> str | None:
        """Extract suggestion from text.

        Args:
            text: Text to search

        Returns:
            Suggestion text or None
        """
        # Look for suggestion patterns
        patterns = [
            r"Suggestion:\s*(.*?)(?:\n|$)",
            r"Recommendation:\s*(.*?)(?:\n|$)",
            r"Fix:\s*(.*?)(?:\n|$)",
            r"Solution:\s*(.*?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                suggestion = match.group(1).strip()
                if suggestion and len(suggestion) > 5:
                    return suggestion

        return None

    def generate_summary(self, findings: List[Finding]) -> str:
        """Generate summary from findings.

        Args:
            findings: List of findings

        Returns:
            Summary text
        """
        if not findings:
            return "Code review completed. No issues found."

        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")
        low = sum(1 for f in findings if f.severity == "LOW")

        parts = []
        if high > 0:
            parts.append(f"{high} high severity")
        if medium > 0:
            parts.append(f"{medium} medium severity")
        if low > 0:
            parts.append(f"{low} low severity")

        if parts:
            return f"Found {', '.join(parts)} issue(s)."
        return "Code review completed."

    def calculate_confidence(
        self, result: Dict[str, Any], depth: str, depth_stages: Dict[str, List[str]]
    ) -> float:
        """Calculate overall confidence score.

        Args:
            result: Chain execution results
            depth: Review depth used
            depth_stages: Available stages for each depth

        Returns:
            Confidence score between 0.0 and 1.0
        """
        expected_stages = depth_stages.get(depth, depth_stages["standard"])
        completed_stages = sum(
            1 for name in result.keys() if name.endswith("_result") and result.get(name)
        )

        if not expected_stages:
            return 0.5

        # Base confidence on stage completion
        stage_ratio = completed_stages / len(expected_stages) if expected_stages else 0.5

        # Boost confidence for deeper reviews
        depth_multiplier = {"quick": 0.8, "standard": 1.0, "deep": 1.1}
        multiplier = depth_multiplier.get(depth, 1.0)

        confidence = min(stage_ratio * multiplier, 1.0)
        return round(confidence, 2)
