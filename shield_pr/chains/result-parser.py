"""Result parser for extracting findings from LLM outputs."""

from typing import List, Dict, Any
import json
from langchain.output_parsers import PydanticOutputParser  # type: ignore
from shield_pr.models.finding import Finding


class ResultParser:
    """Parses LLM outputs into structured Finding objects.

    Implements 3-tier fallback:
    1. Pydantic strict parsing
    2. Manual JSON extraction with regex
    3. Generic Finding with raw output
    """

    def __init__(self) -> None:
        """Initialize parser with Pydantic output parser."""
        self.parser = PydanticOutputParser(pydantic_object=Finding)

    def extract_findings(
        self, result: Dict[str, Any], file_path: str
    ) -> List[Finding]:
        """Extract findings from stage outputs.

        Args:
            result: Dictionary containing stage outputs
            file_path: Path to the reviewed file

        Returns:
            List of Finding objects
        """
        findings = []

        # Try to parse findings from each stage result
        for key, value in result.items():
            if not key.endswith("_result"):
                continue

            try:
                # Tier 1: Try Pydantic parser first
                parsed = self.parser.parse(value)
                if isinstance(parsed, Finding):
                    findings.append(parsed)
            except Exception:
                # Tier 2: Fallback to manual JSON extraction
                try:
                    findings.extend(self._manual_json_extract(value, file_path))
                except Exception:
                    # Tier 3: Create generic finding from raw output
                    if value and isinstance(value, str) and len(value) > 10:
                        findings.append(
                            Finding(
                                severity="LOW",
                                category="analysis",
                                file_path=file_path,
                                description=value[:500],
                                suggestion="Manual review recommended",
                            )
                        )

        return findings

    def _manual_json_extract(self, text: str, file_path: str) -> List[Finding]:
        """Manually extract findings from JSON text.

        Args:
            text: Text potentially containing JSON
            file_path: Path to the reviewed file

        Returns:
            List of Finding objects
        """
        findings = []

        try:
            # Try to find JSON array or object in text
            start = text.find("[")
            if start == -1:
                start = text.find("{")
            if start != -1:
                end = text.rfind("]" if text[start] == "[" else "}")
                if end != -1:
                    json_str = text[start : end + 1]
                    data = json.loads(json_str)

                    if isinstance(data, list):
                        for item in data:
                            findings.append(Finding(**item))
                    elif isinstance(data, dict):
                        findings.append(Finding(**data))
        except Exception:
            pass

        return findings

    def generate_summary(self, findings: List[Finding]) -> str:
        """Generate summary from findings.

        Args:
            findings: List of findings

        Returns:
            Summary text
        """
        if not findings:
            return "No issues found. Code looks good!"

        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")
        low = sum(1 for f in findings if f.severity == "LOW")

        parts = []
        if high > 0:
            parts.append(f"{high} high severity issue{'s' if high > 1 else ''}")
        if medium > 0:
            parts.append(f"{medium} medium severity issue{'s' if medium > 1 else ''}")
        if low > 0:
            parts.append(f"{low} low severity issue{'s' if low > 1 else ''}")

        return f"Found {', '.join(parts)}"

    def calculate_confidence(
        self, result: Dict[str, Any], depth: str, depth_stages: Dict[str, List[str]]
    ) -> float:
        """Calculate confidence score for the review.

        Args:
            result: Dictionary containing stage outputs
            depth: Review depth level
            depth_stages: Mapping of depth levels to stage lists

        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence on number of stages executed
        total_stages = len(depth_stages.get(depth, []))
        executed_stages = sum(1 for key in result.keys() if key.endswith("_result"))

        if total_stages == 0:
            return 0.5

        return min(0.95, executed_stages / total_stages)
