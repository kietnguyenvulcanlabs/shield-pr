"""Backend-specific review chain implementation."""

from typing import Any, Dict
from langchain.chains import LLMChain  # type: ignore
from shield_pr.chains.base import BaseReviewChain
from shield_pr.chains.prompts.backend_prompts import BACKEND_PROMPTS


class BackendReviewChain(BaseReviewChain):
    """Review chain specialized for Backend code analysis.

    Analyzes:
    - Layered architecture and dependency injection
    - Security (SQL injection, auth, CSRF)
    - Database optimization and query patterns
    - Error handling and logging
    - Rate limiting and API throttling
    - Test coverage and quality
    """

    def __init__(self, llm_client: Any, depth: str = "standard") -> None:
        """Initialize Backend review chain.

        Args:
            llm_client: LLM client for chain execution
            depth: Review depth (quick, standard, deep)
        """
        super().__init__(llm_client, depth, platform="backend")

    def _build_stages(self) -> Dict[str, LLMChain]:
        """Build Backend-specific review stages.

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
            prompt=BACKEND_PROMPTS["architecture"],
            output_key="architecture_result",
        )

    def _platform_issues_stage(self) -> LLMChain:
        """Create Backend-specific issues stage.

        Analyzes security, database, error handling, rate limiting, concurrency.

        Returns:
            LLMChain for platform-specific analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=BACKEND_PROMPTS["platform_issues"],
            output_key="platform_issues_result",
        )

    def _test_coverage_stage(self) -> LLMChain:
        """Create test coverage analysis stage.

        Returns:
            LLMChain for test analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=BACKEND_PROMPTS["tests"],
            output_key="tests_result",
        )

    def _improvement_stage(self) -> LLMChain:
        """Create improvement suggestions stage.

        Returns:
            LLMChain for improvement analysis
        """
        return LLMChain(
            llm=self.llm,
            prompt=BACKEND_PROMPTS["improvements"],
            output_key="improvements_result",
        )
