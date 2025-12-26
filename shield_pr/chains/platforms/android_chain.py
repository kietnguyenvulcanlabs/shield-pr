"""Android-specific review chain implementation."""

from typing import Any, Dict
from langchain.chains import LLMChain  # type: ignore
from shield_pr.chains.base import BaseReviewChain
from shield_pr.chains.prompts.android_prompts import ANDROID_PROMPTS


class AndroidReviewChain(BaseReviewChain):
    """Review chain specialized for Android code analysis.

    Analyzes:
    - Architecture patterns (MVVM, MVI, dependency injection)
    - Lifecycle violations and state management
    - Memory leaks (context references, listeners)
    - ANR risks (main thread operations)
    - Permission handling
    - Jetpack Compose best practices
    - Test coverage and quality
    """

    def __init__(self, llm_client: Any, depth: str = "standard") -> None:
        """Initialize Android review chain.

        Args:
            llm_client: LLM client for chain execution
            depth: Review depth (quick, standard, deep)
        """
        super().__init__(llm_client, depth, platform="android")

    def _build_stages(self) -> Dict[str, LLMChain]:
        """Build Android-specific review stages.

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
            prompt=ANDROID_PROMPTS["architecture"],
            output_key="architecture_result",
        )

    def _platform_issues_stage(self) -> LLMChain:
        """Create Android-specific issues stage.

        Analyzes lifecycle, memory leaks, ANR, permissions, Jetpack Compose.

        Returns:
            LLMChain for platform-specific analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=ANDROID_PROMPTS["platform_issues"],
            output_key="platform_issues_result",
        )

    def _test_coverage_stage(self) -> LLMChain:
        """Create test coverage analysis stage.

        Returns:
            LLMChain for test analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=ANDROID_PROMPTS["tests"],
            output_key="tests_result",
        )

    def _improvement_stage(self) -> LLMChain:
        """Create improvement suggestions stage.

        Returns:
            LLMChain for improvement analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=ANDROID_PROMPTS["improvements"],
            output_key="improvements_result",
        )
