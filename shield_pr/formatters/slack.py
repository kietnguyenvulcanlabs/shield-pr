"""Slack message formatter for code review results."""

import json
from typing import Any

from shield_pr.formatters.base import BaseFormatter
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


# Type aliases for block kit structures
Block = dict[str, Any]
BlockList = list[Block]


class SlackFormatter(BaseFormatter):
    """Format review results as Slack Block Kit message.

    Produces JSON output compatible with Slack webhook API.
    Handles Slack's 50 block limit by truncating if needed.
    """

    MAX_BLOCKS = 50
    MAX_FINDINGS = 20  # Limit to avoid block overflow

    def format(self, result: ReviewResult) -> str:
        """Transform ReviewResult to Slack Block Kit JSON.

        Args:
            result: ReviewResult containing findings and metadata

        Returns:
            JSON string with Slack Block Kit structure
        """
        blocks = self._build_blocks(result)
        return json.dumps({"blocks": blocks}, indent=2)

    def _build_blocks(self, result: ReviewResult) -> BlockList:
        """Build complete block structure.

        Args:
            result: ReviewResult with findings

        Returns:
            List of Slack blocks
        """
        blocks = [
            self._header_block(),
            self._divider_block(),
            self._summary_section(result),
            self._divider_block(),
        ]

        # Add findings (limited to prevent overflow)
        findings_blocks = self._findings_blocks(result)
        blocks.extend(findings_blocks[: self.MAX_BLOCKS - len(blocks)])

        # Add footer if space allows
        if len(blocks) < self.MAX_BLOCKS:
            blocks.append(self._footer_block(result))

        return blocks

    def _header_block(self) -> Block:
        """Create header block.

        Returns:
            Header block dict
        """
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔍 Code Review Results",
                "emoji": True,
            },
        }

    def _divider_block(self) -> Block:
        """Create divider block.

        Returns:
            Divider block dict
        """
        return {"type": "divider"}

    def _summary_section(self, result: ReviewResult) -> Block:
        """Create summary section with metrics.

        Args:
            result: ReviewResult with metadata

        Returns:
            Summary section block dict
        """
        counts = self._count_by_severity(result)
        total = len(result.findings)
        confidence_pct = int(result.confidence * 100)

        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Platform:*\n{result.platform}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Confidence:*\n{confidence_pct}%",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Total Issues:*\n{total}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Severity:*\n:{self._severity_emoji(counts)}:",
                },
            ],
        }

    def _severity_emoji(self, counts: dict[str, int]) -> str:
        """Get emoji representing highest severity.

        Args:
            counts: Severity counts dict

        Returns:
            Emoji name for Slack
        """
        if counts.get("HIGH", 0) > 0:
            return "red_circle"
        if counts.get("MEDIUM", 0) > 0:
            return "yellow_circle"
        if counts.get("LOW", 0) > 0:
            return "green_circle"
        return "white_check_mark"

    def _findings_blocks(self, result: ReviewResult) -> BlockList:
        """Create blocks for findings by severity.

        Args:
            result: ReviewResult with findings

        Returns:
            List of finding section blocks
        """
        groups = self._group_by_severity(result)
        blocks = []

        # Add findings for each severity level
        for severity, findings, emoji in [
            ("HIGH", groups["HIGH"], "🔴"),
            ("MEDIUM", groups["MEDIUM"], "🟡"),
            ("LOW", groups["LOW"], "🟢"),
        ]:
            if findings:
                blocks.extend(
                    self._severity_section(findings[: self.MAX_FINDINGS], emoji)
                )

        # No findings case
        if not blocks:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *No issues found!* Code looks good.",
                    },
                }
            )

        return blocks

    def _severity_section(
        self, findings: list[Finding], emoji: str
    ) -> BlockList:
        """Create section for severity level.

        Args:
            findings: List of findings for this severity
            emoji: Emoji for severity level

        Returns:
            List of blocks for this severity
        """
        blocks = []

        # Header
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{len(findings)} {self._get_severity_label(findings)}*",
                },
            }
        )

        # Individual findings
        for finding in findings[:5]:  # Limit to 5 per severity for space
            location = self._format_location(finding)
            text = (
                f"• *{finding.category}* in {location}\n"
                f"_{self._truncate_text(finding.description, 100)}_"
            )

            if finding.suggestion:
                text += f"\n💡 {self._truncate_text(finding.suggestion, 80)}"

            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text},
                }
            )

        return blocks

    def _get_severity_label(self, findings: list[Finding]) -> str:
        """Get severity label from first finding.

        Args:
            findings: List of findings

        Returns:
            Severity label string
        """
        if not findings:
            return "Issues"
        severity = findings[0].severity
        return {
            "HIGH": "High Priority Issues",
            "MEDIUM": "Medium Priority Issues",
            "LOW": "Low Priority Issues",
        }.get(severity, "Issues")

    def _format_location(self, finding: Finding) -> str:
        """Format file location for Slack.

        Args:
            finding: Finding object

        Returns:
            Formatted location string
        """
        if finding.line_number:
            return f"`{finding.file_path}:{finding.line_number}`"
        return f"`{finding.file_path}`"

    def _footer_block(self, result: ReviewResult) -> Block:
        """Create footer block.

        Args:
            result: ReviewResult with summary

        Returns:
            Footer block dict
        """
        text = "*Code Review Assistant*"

        if result.summary:
            text = f"{result.summary}\n{text}"

        return {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": text,
                }
            ],
        }
