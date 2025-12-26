"""Universal quality review chain for cross-platform analysis."""

from typing import Any, Dict, List
from langchain.chains import LLMChain  # type: ignore
from shield_pr.chains.base import BaseReviewChain
from shield_pr.chains.prompts.universal_prompts import UNIVERSAL_PROMPTS


class UniversalReviewChain(BaseReviewChain):
    """Universal review chain for cross-platform quality analysis.

    Analyzes:
    - Security vulnerabilities (OWASP Top 10)
    - Code readability and maintainability
    - Best practices (DRY, SOLID, error handling)
    - Resource management
    - Code smells

    This chain complements platform-specific chains with universal concerns.
    """

    def __init__(self, llm_client: Any, depth: str = "standard") -> None:
        """Initialize Universal review chain.

        Args:
            llm_client: LLM client for chain execution
            depth: Review depth (quick, standard, deep)
        """
        super().__init__(llm_client, depth, platform="universal")

    def _build_stages(self) -> Dict[str, LLMChain]:
        """Build universal review stages.

        Returns:
            Dictionary mapping stage names to LLMChain instances
        """
        return {
            "security": self._security_stage(),
            "readability": self._readability_stage(),
            "best_practices": self._best_practices_stage(),
        }

    def _security_stage(self) -> LLMChain:
        """Create security analysis stage.

        Analyzes OWASP Top 10, secrets, injection vulnerabilities.

        Returns:
            LLMChain for security review
        """
        return LLMChain(
            llm=self.llm,
            prompt=UNIVERSAL_PROMPTS["security"],
            output_key="security_result",
        )

    def _readability_stage(self) -> LLMChain:
        """Create readability analysis stage.

        Analyzes naming, complexity, documentation, organization.

        Returns:
            LLMChain for readability review
        """
        return LLMChain(
            llm=self.llm,
            prompt=UNIVERSAL_PROMPTS["readability"],
            output_key="readability_result",
        )

    def _best_practices_stage(self) -> LLMChain:
        """Create best practices analysis stage.

        Analyzes DRY, SOLID, error handling, resource management.

        Returns:
            LLMChain for best practices review
        """
        return LLMChain(
            llm=self.llm,
            prompt=UNIVERSAL_PROMPTS["best_practices"],
            output_key="best_practices_result",
        )

    def _select_stages_by_depth(self) -> List[str]:
        """Override depth selection for universal chain.

        Universal chain has different stage structure.

        Returns:
            List of stage names based on depth
        """
        if self.depth == "quick":
            return ["security"]
        elif self.depth == "standard":
            return ["security", "readability"]
        else:  # deep
            return ["security", "readability", "best_practices"]
