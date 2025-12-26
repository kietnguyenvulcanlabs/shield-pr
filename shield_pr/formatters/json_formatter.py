"""JSON formatter for code review results."""

import json
from datetime import datetime
from typing import Any

from shield_pr.formatters.base import BaseFormatter
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class JSONFormatter(BaseFormatter):
    """Format review results as JSON.

    Provides machine-readable output for CI/CD integration
    and programmatic consumption.
    """

    def format(self, result: ReviewResult) -> str:
        """Transform ReviewResult to JSON format.

        Args:
            result: ReviewResult containing findings and metadata

        Returns:
            Formatted JSON string with metadata
        """
        data = {
            "platform": result.platform,
            "confidence": result.confidence,
            "findings": [self._serialize_finding(f) for f in result.findings],
            "summary": result.summary,
            "metadata": self._build_metadata(),
        }
        return json.dumps(data, indent=2)

    def _serialize_finding(self, finding: Finding) -> dict[str, Any]:
        """Serialize finding to dict for JSON output.

        Args:
            finding: Finding object

        Returns:
            Dictionary representation of finding
        """
        return {
            "severity": finding.severity,
            "category": finding.category,
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "description": finding.description,
            "suggestion": finding.suggestion,
            "code_snippet": finding.code_snippet,
        }

    def _build_metadata(self) -> dict[str, Any]:
        """Build metadata section for JSON output.

        Returns:
            Dictionary with metadata fields
        """
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "0.1.0",
            "tool": "shield-pr",
        }
