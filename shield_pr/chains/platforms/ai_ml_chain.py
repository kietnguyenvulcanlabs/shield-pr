"""AI/ML-specific review chain implementation."""

from typing import Any, Dict
from langchain.chains import LLMChain  # type: ignore
from shield_pr.chains.base import BaseReviewChain
from shield_pr.chains.prompts.ai_ml_prompts import AI_ML_PROMPTS


class AiMlReviewChain(BaseReviewChain):
    """Review chain specialized for AI/ML code analysis.

    Analyzes:
    - Model architecture and design patterns
    - Data validation and preprocessing
    - Model performance and training issues
    - GPU and memory optimization
    - Bias and fairness considerations
    - Reproducibility and experiment tracking
    - Test coverage and quality
    """

    def __init__(self, llm_client: Any, depth: str = "standard") -> None:
        """Initialize AI/ML review chain.

        Args:
            llm_client: LLM client for chain execution
            depth: Review depth (quick, standard, deep)
        """
        super().__init__(llm_client, depth, platform="ai-ml")

    def _build_stages(self) -> Dict[str, LLMChain]:
        """Build AI/ML-specific review stages.

        Returns:
            Dictionary mapping stage names to LLMChain instances
        """
        return {
            "architecture": self._arch_stage(),
            "platform_issues": self._platform_issues_stage(),
            "tests": self._test_coverage_stage(),
            "improvements": self._improvement_stage(),
        }

    def _arch_stage(self) -> LLMChain:
        """Create architecture analysis stage.

        Returns:
            LLMChain for architecture review
        """
        return LLMChain(
            llm=self.llm,
            prompt=AI_ML_PROMPTS["architecture"],
            output_key="architecture_result",
        )

    def _platform_issues_stage(self) -> LLMChain:
        """Create AI/ML-specific issues stage.

        Analyzes data validation, model performance, GPU/memory, bias, reproducibility.

        Returns:
            LLMChain for platform-specific analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=AI_ML_PROMPTS["platform_issues"],
            output_key="platform_issues_result",
        )

    def _test_coverage_stage(self) -> LLMChain:
        """Create test coverage analysis stage.

        Returns:
            LLMChain for test analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=AI_ML_PROMPTS["tests"],
            output_key="tests_result",
        )

    def _improvement_stage(self) -> LLMChain:
        """Create improvement suggestions stage.

        Returns:
            LLMChain for improvement analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=AI_ML_PROMPTS["improvements"],
            output_key="improvements_result",
        )
