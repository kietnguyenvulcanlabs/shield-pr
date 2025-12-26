"""Tests for SynthesisChain (deduplication and prioritization)."""

import pytest
from shield_pr.chains.synthesis_chain import SynthesisChain
from shield_pr.models.finding import Finding
from shield_pr.models.review_result import ReviewResult


class TestSynthesisChainDeduplication:
    """Tests for finding deduplication logic."""

    def test_deduplicate_no_duplicates(self):
        """Test deduplication with no duplicate findings."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="HIGH",
                category="security",
                file_path="app.py",
                line_number=10,
                description="SQL injection vulnerability",
                suggestion="Use parameterized queries"
            ),
            Finding(
                severity="MEDIUM",
                category="performance",
                file_path="utils.py",
                line_number=50,
                description="Inefficient loop",
                suggestion="Use list comprehension"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        assert len(deduplicated) == 2
        assert deduplicated[0].severity == "HIGH"
        assert deduplicated[1].severity == "MEDIUM"

    def test_deduplicate_exact_duplicates(self):
        """Test deduplication removes exact duplicate findings."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="HIGH",
                category="security",
                file_path="app.py",
                description="SQL injection in user query",
                suggestion="Fix it"
            ),
            Finding(
                severity="MEDIUM",
                category="security",
                file_path="app.py",
                description="SQL injection in user query",
                suggestion="Fix it now"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        # Should keep higher severity one
        assert len(deduplicated) == 1
        assert deduplicated[0].severity == "HIGH"

    def test_deduplicate_similar_descriptions(self):
        """Test deduplication detects similar descriptions (>80% similarity)."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="LOW",
                category="maintainability",
                file_path="main.py",
                description="This function is too long and should be refactored",
                suggestion="Split function"
            ),
            Finding(
                severity="MEDIUM",
                category="maintainability",
                file_path="main.py",
                description="This function is too long and should be broken down",
                suggestion="Split function"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        # Should keep MEDIUM (higher severity)
        assert len(deduplicated) == 1
        assert deduplicated[0].severity == "MEDIUM"

    def test_deduplicate_nearby_line_numbers(self):
        """Test deduplication detects findings within 5 lines."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="HIGH",
                category="memory-leak",
                file_path="service.py",
                line_number=100,
                description="Context leaked",
                suggestion="Use WeakReference"
            ),
            Finding(
                severity="LOW",
                category="memory-leak",
                file_path="service.py",
                line_number=103,
                description="Different issue",
                suggestion="Fix it"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        # Within 5 lines, same category and file - should deduplicate
        assert len(deduplicated) == 1
        assert deduplicated[0].severity == "HIGH"

    def test_deduplicate_different_categories(self):
        """Test deduplication keeps findings with different categories."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="HIGH",
                category="security",
                file_path="app.py",
                description="Issue found",
                suggestion="Fix"
            ),
            Finding(
                severity="HIGH",
                category="performance",
                file_path="app.py",
                description="Issue found",
                suggestion="Fix"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        # Different categories - should keep both
        assert len(deduplicated) == 2

    def test_deduplicate_different_files(self):
        """Test deduplication keeps findings from different files."""
        chain = SynthesisChain()

        findings = [
            Finding(
                severity="MEDIUM",
                category="style",
                file_path="file1.py",
                description="Same issue",
                suggestion="Fix"
            ),
            Finding(
                severity="MEDIUM",
                category="style",
                file_path="file2.py",
                description="Same issue",
                suggestion="Fix"
            )
        ]

        deduplicated = chain._deduplicate(findings)

        # Different files - should keep both
        assert len(deduplicated) == 2

    def test_deduplicate_empty_list(self):
        """Test deduplication handles empty list."""
        chain = SynthesisChain()

        deduplicated = chain._deduplicate([])

        assert deduplicated == []


class TestSynthesisChainSimilarityDetection:
    """Tests for similarity detection between findings."""

    def test_are_similar_same_category_file_description(self):
        """Test similarity with matching category, file, and description."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="HIGH",
            category="security",
            file_path="app.py",
            description="SQL injection vulnerability detected",
            suggestion="Fix it"
        )
        finding2 = Finding(
            severity="MEDIUM",
            category="security",
            file_path="app.py",
            description="SQL injection vulnerability detected",
            suggestion="Fix now"
        )

        assert chain._are_similar(finding1, finding2) is True

    def test_are_similar_different_category(self):
        """Test findings with different categories are not similar."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="HIGH",
            category="security",
            file_path="app.py",
            description="Issue",
            suggestion="Fix"
        )
        finding2 = Finding(
            severity="HIGH",
            category="performance",
            file_path="app.py",
            description="Issue",
            suggestion="Fix"
        )

        assert chain._are_similar(finding1, finding2) is False

    def test_are_similar_different_file(self):
        """Test findings from different files are not similar."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="MEDIUM",
            category="style",
            file_path="file1.py",
            description="Issue",
            suggestion="Fix"
        )
        finding2 = Finding(
            severity="MEDIUM",
            category="style",
            file_path="file2.py",
            description="Issue",
            suggestion="Fix"
        )

        assert chain._are_similar(finding1, finding2) is False

    def test_are_similar_low_description_similarity(self):
        """Test findings with dissimilar descriptions are not similar."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="LOW",
            category="test",
            file_path="app.py",
            description="This is a completely different description about testing",
            suggestion="Fix"
        )
        finding2 = Finding(
            severity="LOW",
            category="test",
            file_path="app.py",
            description="Another unrelated issue with performance",
            suggestion="Fix"
        )

        assert chain._are_similar(finding1, finding2) is False

    def test_are_similar_within_line_threshold(self):
        """Test findings within 5 lines are considered similar."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="HIGH",
            category="memory",
            file_path="service.py",
            line_number=100,
            description="Memory leak",
            suggestion="Fix"
        )
        finding2 = Finding(
            severity="MEDIUM",
            category="memory",
            file_path="service.py",
            line_number=105,
            description="Different description",
            suggestion="Fix"
        )

        assert chain._are_similar(finding1, finding2) is True

    def test_are_similar_beyond_line_threshold(self):
        """Test findings beyond 5 lines with different descriptions are not similar."""
        chain = SynthesisChain()

        finding1 = Finding(
            severity="HIGH",
            category="memory",
            file_path="service.py",
            line_number=100,
            description="Memory leak here",
            suggestion="Fix"
        )
        finding2 = Finding(
            severity="MEDIUM",
            category="memory",
            file_path="service.py",
            line_number=110,
            description="Different issue there",
            suggestion="Fix"
        )

        # 10 lines apart and different descriptions
        assert chain._are_similar(finding1, finding2) is False


class TestSynthesisChainPrioritization:
    """Tests for finding prioritization logic."""

    def test_prioritize_by_severity(self):
        """Test findings are sorted by severity (HIGH > MEDIUM > LOW)."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="LOW", category="a", file_path="x.py", description="1", suggestion="F"),
            Finding(severity="HIGH", category="b", file_path="y.py", description="2", suggestion="F"),
            Finding(severity="MEDIUM", category="c", file_path="z.py", description="3", suggestion="F"),
        ]

        prioritized = chain._prioritize(findings)

        assert prioritized[0].severity == "HIGH"
        assert prioritized[1].severity == "MEDIUM"
        assert prioritized[2].severity == "LOW"

    def test_prioritize_by_category_within_severity(self):
        """Test findings with same severity are sorted by category."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="HIGH", category="z-category", file_path="a.py", description="1", suggestion="F"),
            Finding(severity="HIGH", category="a-category", file_path="b.py", description="2", suggestion="F"),
            Finding(severity="HIGH", category="m-category", file_path="c.py", description="3", suggestion="F"),
        ]

        prioritized = chain._prioritize(findings)

        assert prioritized[0].category == "a-category"
        assert prioritized[1].category == "m-category"
        assert prioritized[2].category == "z-category"

    def test_prioritize_by_file_path_within_category(self):
        """Test findings with same severity and category sorted by file path."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="MEDIUM", category="perf", file_path="z.py", description="1", suggestion="F"),
            Finding(severity="MEDIUM", category="perf", file_path="a.py", description="2", suggestion="F"),
            Finding(severity="MEDIUM", category="perf", file_path="m.py", description="3", suggestion="F"),
        ]

        prioritized = chain._prioritize(findings)

        assert prioritized[0].file_path == "a.py"
        assert prioritized[1].file_path == "m.py"
        assert prioritized[2].file_path == "z.py"

    def test_prioritize_empty_list(self):
        """Test prioritization handles empty list."""
        chain = SynthesisChain()

        prioritized = chain._prioritize([])

        assert prioritized == []


class TestSynthesisChainSummaryGeneration:
    """Tests for comprehensive summary generation."""

    def test_generate_summary_no_findings(self):
        """Test summary with no findings."""
        chain = SynthesisChain()

        summary = chain._generate_summary([], "android")

        assert "Android code review" in summary
        assert "No issues found" in summary

    def test_generate_summary_with_severity_counts(self):
        """Test summary includes severity breakdown."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="HIGH", category="sec", file_path="a.py", description="1", suggestion="F"),
            Finding(severity="HIGH", category="sec", file_path="a.py", description="2", suggestion="F"),
            Finding(severity="MEDIUM", category="perf", file_path="b.py", description="3", suggestion="F"),
            Finding(severity="LOW", category="style", file_path="c.py", description="4", suggestion="F"),
        ]

        summary = chain._generate_summary(findings, "ios")

        assert "ios code review" in summary.lower()
        assert "2 high severity" in summary
        assert "1 medium severity" in summary
        assert "1 low severity" in summary

    def test_generate_summary_with_top_categories(self):
        """Test summary includes top 3 categories."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="HIGH", category="security", file_path="a.py", description="1", suggestion="F"),
            Finding(severity="HIGH", category="security", file_path="a.py", description="2", suggestion="F"),
            Finding(severity="MEDIUM", category="security", file_path="a.py", description="3", suggestion="F"),
            Finding(severity="MEDIUM", category="performance", file_path="b.py", description="4", suggestion="F"),
            Finding(severity="LOW", category="performance", file_path="b.py", description="5", suggestion="F"),
            Finding(severity="LOW", category="style", file_path="c.py", description="6", suggestion="F"),
        ]

        summary = chain._generate_summary(findings, "frontend")

        assert "Main areas:" in summary
        assert "security (3)" in summary
        assert "performance (2)" in summary
        assert "style (1)" in summary

    def test_generate_summary_platform_capitalized(self):
        """Test summary capitalizes platform name."""
        chain = SynthesisChain()

        findings = [
            Finding(severity="LOW", category="test", file_path="x.py", description="1", suggestion="F")
        ]

        summary = chain._generate_summary(findings, "backend")

        assert "Backend code review" in summary


class TestSynthesisChainIntegration:
    """Integration tests for full synthesis workflow."""

    def test_synthesize_combines_findings(self):
        """Test synthesize combines platform and universal findings."""
        chain = SynthesisChain()

        platform_result = ReviewResult(
            platform="android",
            findings=[
                Finding(severity="HIGH", category="lifecycle", file_path="Activity.kt", description="Leak", suggestion="Fix")
            ],
            summary="Platform review",
            confidence=0.9
        )

        universal_result = ReviewResult(
            platform="universal",
            findings=[
                Finding(severity="MEDIUM", category="naming", file_path="Activity.kt", description="Bad name", suggestion="Rename")
            ],
            summary="Universal review",
            confidence=0.85
        )

        result = chain.synthesize(platform_result, universal_result)

        assert result.platform == "android"
        assert len(result.findings) == 2
        assert result.confidence == 0.85  # Min of both

    def test_synthesize_deduplicates_findings(self):
        """Test synthesize removes duplicate findings from both sources."""
        chain = SynthesisChain()

        duplicate_finding = Finding(
            severity="HIGH",
            category="security",
            file_path="app.py",
            description="SQL injection vulnerability",
            suggestion="Use parameterized queries"
        )

        platform_result = ReviewResult(
            platform="backend",
            findings=[duplicate_finding],
            summary="Platform",
            confidence=0.9
        )

        universal_result = ReviewResult(
            platform="universal",
            findings=[duplicate_finding],
            summary="Universal",
            confidence=0.9
        )

        result = chain.synthesize(platform_result, universal_result)

        assert len(result.findings) == 1

    def test_synthesize_prioritizes_findings(self):
        """Test synthesize prioritizes combined findings."""
        chain = SynthesisChain()

        platform_result = ReviewResult(
            platform="ios",
            findings=[
                Finding(severity="LOW", category="style", file_path="a.swift", description="1", suggestion="F"),
                Finding(severity="HIGH", category="memory", file_path="b.swift", description="2", suggestion="F"),
            ],
            summary="Platform",
            confidence=0.9
        )

        universal_result = ReviewResult(
            platform="universal",
            findings=[
                Finding(severity="MEDIUM", category="testing", file_path="c.swift", description="3", suggestion="F")
            ],
            summary="Universal",
            confidence=0.85
        )

        result = chain.synthesize(platform_result, universal_result)

        # Should be prioritized: HIGH, MEDIUM, LOW
        assert result.findings[0].severity == "HIGH"
        assert result.findings[1].severity == "MEDIUM"
        assert result.findings[2].severity == "LOW"

    def test_synthesize_generates_comprehensive_summary(self):
        """Test synthesize generates comprehensive summary."""
        chain = SynthesisChain()

        platform_result = ReviewResult(
            platform="frontend",
            findings=[
                Finding(severity="HIGH", category="security", file_path="app.js", description="XSS", suggestion="F"),
                Finding(severity="MEDIUM", category="performance", file_path="app.js", description="Slow", suggestion="F"),
            ],
            summary="Platform",
            confidence=0.9
        )

        universal_result = ReviewResult(
            platform="universal",
            findings=[
                Finding(severity="LOW", category="style", file_path="utils.js", description="Format", suggestion="F")
            ],
            summary="Universal",
            confidence=0.85
        )

        result = chain.synthesize(platform_result, universal_result)

        assert "Frontend code review" in result.summary
        assert "1 high severity" in result.summary
        assert "1 medium severity" in result.summary
        assert "1 low severity" in result.summary

    def test_synthesize_uses_minimum_confidence(self):
        """Test synthesize uses minimum confidence from both sources."""
        chain = SynthesisChain()

        platform_result = ReviewResult(
            platform="android",
            findings=[],
            summary="Test",
            confidence=0.95
        )

        universal_result = ReviewResult(
            platform="universal",
            findings=[],
            summary="Test",
            confidence=0.75
        )

        result = chain.synthesize(platform_result, universal_result)

        assert result.confidence == 0.75  # Lower of the two
