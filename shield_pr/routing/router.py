"""Review router for directing code to platform-specific chains."""

from typing import Dict, Optional

from ..core.llm_client import LLMClient
from ..utils.logger import logger
from .destinations import get_platform_chains


class ReviewRouter:
    """Routes code to appropriate platform-specific review chain."""

    def __init__(self, llm_client: LLMClient):
        """Initialize review router.

        Args:
            llm_client: LLM client for executing chains
        """
        self.llm_client = llm_client
        self.chains = get_platform_chains(llm_client)
        logger.debug(f"Initialized router with {len(self.chains)} chains")

    def route(
        self, platform: Optional[str], code: str, file_path: str = ""
    ) -> Dict[str, str]:
        """Route code to appropriate platform chain.

        Args:
            platform: Detected platform name
            code: Code content to review
            file_path: Optional file path for logging

        Returns:
            Dictionary with review results
        """
        # Select appropriate chain
        chain_name = platform if platform in self.chains else "default"
        chain = self.chains[chain_name]

        logger.info(f"Routing {file_path or 'code'} to {chain_name} chain")

        try:
            # Execute chain
            result = chain.invoke({"code": code})

            # Extract text from result
            if isinstance(result, dict):
                review_text = result.get("text", str(result))
            else:
                review_text = str(result)

            return {
                "platform": chain_name,
                "file": file_path,
                "review": review_text,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Chain execution failed: {e}")
            return {
                "platform": chain_name,
                "file": file_path,
                "review": "",
                "status": "error",
                "error": str(e),
            }

    def route_batch(
        self, files: Dict[str, str], platforms: Dict[str, Optional[str]]
    ) -> list[Dict[str, str]]:
        """Route multiple files to appropriate chains.

        Args:
            files: Dictionary mapping file paths to code content
            platforms: Dictionary mapping file paths to platform names

        Returns:
            List of review results
        """
        results = []
        for file_path, code in files.items():
            platform = platforms.get(file_path)
            result = self.route(platform, code, file_path)
            results.append(result)
        return results

    def get_available_chains(self) -> list[str]:
        """Get list of available review chains.

        Returns:
            List of chain names
        """
        return list(self.chains.keys())
