"""Base review chain abstract class."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from langchain.chains import LLMChain  # type: ignore
from shield_pr.models.review_result import ReviewResult
from shield_pr.core.errors import ReviewError
from shield_pr.chains.result_parser import ResultParser  # type: ignore


class BaseReviewChain(ABC):
    """Abstract base class for platform-specific review chains.

    Implements depth-based stage selection and sequential chain execution.
    Subclasses must implement _build_stages() to define platform-specific logic.
    """

    DEPTH_STAGES = {
        "quick": ["architecture", "improvements"],
        "standard": ["architecture", "platform_issues", "tests", "improvements"],
        "deep": [
            "architecture",
            "platform_issues",
            "tests",
            "improvements",
            "security_audit",
            "performance",
        ],
    }

    def __init__(self, llm_client: Any, depth: str = "standard", platform: str = "unknown") -> None:
        """Initialize review chain.

        Args:
            llm_client: LLM client for chain execution
            depth: Review depth (quick, standard, deep)
            platform: Platform name for this chain
        """
        self.llm = llm_client
        self.depth = depth
        self.platform = platform
        self.stages = self._build_stages()
        self.parser = ResultParser()

    @abstractmethod
    def _build_stages(self) -> Dict[str, LLMChain]:
        """Build platform-specific review stages.

        Returns:
            Dictionary mapping stage names to LLMChain instances
        """
        pass

    def execute(self, code: str, file_path: str) -> ReviewResult:
        """Execute review chain with depth-based stage selection.

        Args:
            code: Source code to review
            file_path: Path to the file being reviewed

        Returns:
            ReviewResult containing findings and summary
        """
        try:
            active_stages = self._select_stages_by_depth()
            result = self._execute_stages(active_stages, code, file_path)
            return self._parse_result(result, file_path)
        except Exception as e:
            raise ReviewError(f"Chain execution failed: {str(e)}") from e

    def _select_stages_by_depth(self) -> List[str]:
        """Select stages based on review depth.

        Returns:
            List of stage names to execute
        """
        return self.DEPTH_STAGES.get(self.depth, self.DEPTH_STAGES["standard"])

    def _execute_stages(
        self, active_stages: List[str], code: str, file_path: str
    ) -> Dict[str, Any]:
        """Execute selected stages sequentially.

        Args:
            active_stages: List of stage names to execute
            code: Source code to review
            file_path: Path to the file being reviewed

        Returns:
            Dictionary containing stage outputs
        """
        context = {"code": code, "file_path": file_path}

        for stage_name in active_stages:
            if stage_name not in self.stages:
                continue

            stage = self.stages[stage_name]
            output = stage.invoke(context)

            # Add stage output to context for next stages
            context[f"{stage_name}_result"] = output.get("text", "")

        return context

    def _parse_result(
        self, result: Dict[str, Any], file_path: str
    ) -> ReviewResult:
        """Parse stage outputs into structured ReviewResult.

        Args:
            result: Dictionary containing all stage outputs
            file_path: Path to the reviewed file

        Returns:
            Structured ReviewResult object
        """
        findings = self.parser.extract_findings(result, file_path)
        summary = self.parser.generate_summary(findings)
        confidence = self.parser.calculate_confidence(
            result, self.depth, self.DEPTH_STAGES
        )

        return ReviewResult(
            platform=self.platform,
            findings=findings,
            summary=summary,
            confidence=confidence,
        )
