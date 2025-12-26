"""Synthesis chain for aggregating and prioritizing findings."""

from typing import List
from difflib import SequenceMatcher
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class SynthesisChain:
    """Aggregates platform + universal findings, prioritizes, deduplicates.

    Provides final consolidated review results by:
    1. Deduplicating similar findings
    2. Prioritizing by severity (HIGH > MEDIUM > LOW)
    3. Grouping by category
    4. Generating comprehensive summary
    """

    SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    def synthesize(
        self, platform_result: ReviewResult, universal_result: ReviewResult
    ) -> ReviewResult:
        """Synthesize platform and universal results.

        Args:
            platform_result: Platform-specific review results
            universal_result: Universal quality review results

        Returns:
            Consolidated ReviewResult
        """
        # Combine findings from both sources
        all_findings = platform_result.findings + universal_result.findings

        # Deduplicate similar findings
        deduplicated = self._deduplicate(all_findings)

        # Prioritize by severity and category
        prioritized = self._prioritize(deduplicated)

        # Generate comprehensive summary
        summary = self._generate_summary(prioritized, platform_result.platform)

        # Calculate combined confidence
        confidence = min(platform_result.confidence, universal_result.confidence)

        return ReviewResult(
            platform=platform_result.platform,
            findings=prioritized,
            summary=summary,
            confidence=confidence,
        )

    def _deduplicate(self, findings: List[Finding]) -> List[Finding]:
        """Deduplicate similar findings using fuzzy matching.

        Args:
            findings: List of findings to deduplicate

        Returns:
            Deduplicated list of findings
        """
        if not findings:
            return []

        deduplicated: List[Finding] = []
        seen: List[Finding] = []

        for finding in findings:
            # Check if this finding is similar to any we've seen
            is_duplicate = False
            for seen_finding in seen:
                if self._are_similar(finding, seen_finding):
                    is_duplicate = True
                    # Keep the higher severity one
                    if self.SEVERITY_ORDER[finding.severity] < self.SEVERITY_ORDER[
                        seen_finding.severity
                    ]:
                        # Replace with higher severity
                        idx = deduplicated.index(seen_finding)
                        deduplicated[idx] = finding
                        seen[seen.index(seen_finding)] = finding
                    break

            if not is_duplicate:
                deduplicated.append(finding)
                seen.append(finding)

        return deduplicated

    def _are_similar(self, finding1: Finding, finding2: Finding) -> bool:
        """Check if two findings are similar enough to be considered duplicates.

        Args:
            finding1: First finding
            finding2: Second finding

        Returns:
            True if findings are similar
        """
        # Same category and file
        if finding1.category != finding2.category:
            return False

        if finding1.file_path != finding2.file_path:
            return False

        # Similar descriptions (>0.8 similarity)
        desc_similarity = SequenceMatcher(
            None, finding1.description, finding2.description
        ).ratio()

        if desc_similarity > 0.8:
            return True

        # Similar line numbers (within 5 lines)
        if finding1.line_number and finding2.line_number:
            if abs(finding1.line_number - finding2.line_number) <= 5:
                return True

        return False

    def _prioritize(self, findings: List[Finding]) -> List[Finding]:
        """Prioritize findings by severity, then category.

        Args:
            findings: List of findings to prioritize

        Returns:
            Sorted list of findings
        """
        return sorted(
            findings,
            key=lambda f: (self.SEVERITY_ORDER[f.severity], f.category, f.file_path),
        )

    def _generate_summary(self, findings: List[Finding], platform: str) -> str:
        """Generate comprehensive summary from findings.

        Args:
            findings: List of findings
            platform: Platform name

        Returns:
            Summary text
        """
        if not findings:
            return f"{platform.capitalize()} code review: No issues found. Code looks good!"

        # Count by severity
        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")
        low = sum(1 for f in findings if f.severity == "LOW")

        # Count by category
        categories: dict[str, int] = {}
        for finding in findings:
            categories[finding.category] = categories.get(finding.category, 0) + 1

        # Build summary
        summary_parts = [f"{platform.capitalize()} code review:"]

        # Severity breakdown
        severity_parts = []
        if high > 0:
            severity_parts.append(f"{high} high severity")
        if medium > 0:
            severity_parts.append(f"{medium} medium severity")
        if low > 0:
            severity_parts.append(f"{low} low severity")

        if severity_parts:
            summary_parts.append(f"Found {', '.join(severity_parts)} issue(s).")

        # Top categories
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[
            :3
        ]
        if top_categories:
            cat_list = ", ".join([f"{cat} ({count})" for cat, count in top_categories])
            summary_parts.append(f"Main areas: {cat_list}.")

        return " ".join(summary_parts)
