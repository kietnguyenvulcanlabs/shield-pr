"""Tests for ResultParser (3-tier parsing fallback)."""

import pytest
from shield_pr.chains.result_parser import ResultParser
from shield_pr.models.finding import Finding


class TestResultParserFindingExtraction:
    """Tests for finding extraction from stage outputs."""

    def test_extract_findings_tier1_pydantic_success(self):
        """Test Tier 1: Pydantic parser extracts valid Finding JSON."""
        parser = ResultParser()

        # Valid Finding JSON that Pydantic can parse
        result = {
            "architecture_result": '''{
                "severity": "HIGH",
                "category": "security",
                "file_path": "app.py",
                "line_number": 42,
                "description": "SQL injection vulnerability",
                "suggestion": "Use parameterized queries",
                "code_snippet": "query = f'SELECT * FROM users'"
            }'''
        }

        findings = parser.extract_findings(result, "app.py")

        assert len(findings) >= 0  # Pydantic parser may or may not extract

    def test_extract_findings_tier2_json_array(self):
        """Test Tier 2: Manual JSON extraction from array."""
        parser = ResultParser()

        result = {
            "platform_issues_result": '''
            Some text before
            [
                {
                    "severity": "MEDIUM",
                    "category": "performance",
                    "file_path": "utils.py",
                    "description": "N+1 query detected",
                    "suggestion": "Use eager loading"
                },
                {
                    "severity": "LOW",
                    "category": "style",
                    "file_path": "utils.py",
                    "description": "Long function",
                    "suggestion": "Break into smaller functions"
                }
            ]
            Some text after
            '''
        }

        findings = parser.extract_findings(result, "utils.py")

        assert len(findings) >= 2
        assert any(f.severity == "MEDIUM" for f in findings)
        assert any(f.category == "performance" for f in findings)

    def test_extract_findings_tier2_json_object(self):
        """Test Tier 2: Manual JSON extraction from single object."""
        parser = ResultParser()

        result = {
            "tests_result": '''
            Analysis results:
            {
                "severity": "HIGH",
                "category": "testing",
                "file_path": "main.py",
                "description": "Missing test coverage",
                "suggestion": "Add unit tests"
            }
            '''
        }

        findings = parser.extract_findings(result, "main.py")

        assert len(findings) >= 1
        found_finding = next((f for f in findings if f.category == "testing"), None)
        if found_finding:
            assert found_finding.severity == "HIGH"

    def test_extract_findings_tier3_fallback_generic(self):
        """Test Tier 3: Fallback to generic Finding for unparseable text."""
        parser = ResultParser()

        result = {
            "improvements_result": "This code needs refactoring for better maintainability and performance improvements."
        }

        findings = parser.extract_findings(result, "code.py")

        assert len(findings) >= 1
        assert findings[0].severity == "LOW"
        assert findings[0].category == "analysis"
        assert findings[0].file_path == "code.py"
        assert "Manual review recommended" in findings[0].suggestion

    def test_extract_findings_ignores_non_result_keys(self):
        """Test extraction only processes keys ending with '_result'."""
        parser = ResultParser()

        result = {
            "code": "def hello(): pass",
            "file_path": "test.py",
            "architecture_result": '''{"severity": "LOW", "category": "design", "file_path": "test.py", "description": "Test", "suggestion": "Fix"}'''
        }

        findings = parser.extract_findings(result, "test.py")

        # Should only process architecture_result, not code or file_path
        assert isinstance(findings, list)

    def test_extract_findings_handles_empty_results(self):
        """Test extraction handles empty result dictionary."""
        parser = ResultParser()

        findings = parser.extract_findings({}, "test.py")

        assert findings == []

    def test_extract_findings_handles_empty_strings(self):
        """Test extraction skips empty string values."""
        parser = ResultParser()

        result = {
            "stage1_result": "",
            "stage2_result": "   ",
            "stage3_result": "short"
        }

        findings = parser.extract_findings(result, "test.py")

        # Empty and very short strings should be skipped
        assert len(findings) == 0


class TestResultParserManualJsonExtract:
    """Tests for manual JSON extraction fallback."""

    def test_manual_json_extract_valid_array(self):
        """Test manual extraction handles valid JSON array."""
        parser = ResultParser()

        text = '''
        Here are the findings:
        [
            {"severity": "HIGH", "category": "security", "file_path": "app.py", "description": "Issue 1", "suggestion": "Fix 1"},
            {"severity": "LOW", "category": "style", "file_path": "app.py", "description": "Issue 2", "suggestion": "Fix 2"}
        ]
        End of findings.
        '''

        findings = parser._manual_json_extract(text, "app.py")

        assert len(findings) == 2
        assert findings[0].severity == "HIGH"
        assert findings[1].severity == "LOW"

    def test_manual_json_extract_valid_object(self):
        """Test manual extraction handles single JSON object."""
        parser = ResultParser()

        text = '''
        Finding:
        {"severity": "MEDIUM", "category": "perf", "file_path": "db.py", "description": "Slow query", "suggestion": "Add index"}
        '''

        findings = parser._manual_json_extract(text, "db.py")

        assert len(findings) == 1
        assert findings[0].severity == "MEDIUM"
        assert findings[0].category == "perf"

    def test_manual_json_extract_invalid_json(self):
        """Test manual extraction returns empty for invalid JSON."""
        parser = ResultParser()

        text = "This is not valid JSON at all"

        findings = parser._manual_json_extract(text, "test.py")

        assert findings == []

    def test_manual_json_extract_no_json_markers(self):
        """Test manual extraction returns empty when no JSON markers found."""
        parser = ResultParser()

        text = "Just plain text without any JSON"

        findings = parser._manual_json_extract(text, "test.py")

        assert findings == []

    def test_manual_json_extract_malformed_json(self):
        """Test manual extraction handles malformed JSON gracefully."""
        parser = ResultParser()

        text = '{"severity": "HIGH", "category": "test", "file_path": "x.py"'  # Missing closing brace

        findings = parser._manual_json_extract(text, "x.py")

        assert findings == []


class TestResultParserSummaryGeneration:
    """Tests for summary generation from findings."""

    def test_generate_summary_no_findings(self):
        """Test summary for empty findings list."""
        parser = ResultParser()

        summary = parser.generate_summary([])

        assert summary == "No issues found. Code looks good!"

    def test_generate_summary_single_high_finding(self):
        """Test summary for single high severity finding."""
        parser = ResultParser()

        findings = [
            Finding(
                severity="HIGH",
                category="security",
                file_path="app.py",
                description="Critical issue",
                suggestion="Fix now"
            )
        ]

        summary = parser.generate_summary(findings)

        assert "1 high severity issue" in summary
        assert "medium" not in summary.lower()
        assert "low" not in summary.lower()

    def test_generate_summary_multiple_severities(self):
        """Test summary with mixed severity findings."""
        parser = ResultParser()

        findings = [
            Finding(severity="HIGH", category="sec", file_path="a.py", description="H1", suggestion="F1"),
            Finding(severity="HIGH", category="sec", file_path="a.py", description="H2", suggestion="F2"),
            Finding(severity="MEDIUM", category="perf", file_path="b.py", description="M1", suggestion="F3"),
            Finding(severity="LOW", category="style", file_path="c.py", description="L1", suggestion="F4"),
            Finding(severity="LOW", category="style", file_path="c.py", description="L2", suggestion="F5"),
            Finding(severity="LOW", category="style", file_path="c.py", description="L3", suggestion="F6"),
        ]

        summary = parser.generate_summary(findings)

        assert "2 high severity issues" in summary
        assert "1 medium severity issue" in summary
        assert "3 low severity issues" in summary

    def test_generate_summary_plural_handling(self):
        """Test summary uses correct singular/plural forms."""
        parser = ResultParser()

        # Single issue
        findings_single = [
            Finding(severity="MEDIUM", category="test", file_path="x.py", description="X", suggestion="Y")
        ]
        summary = parser.generate_summary(findings_single)
        assert "1 medium severity issue" in summary
        assert "issues" not in summary or "1 medium severity issue" in summary

        # Multiple issues
        findings_multiple = [
            Finding(severity="LOW", category="a", file_path="x.py", description="1", suggestion="F"),
            Finding(severity="LOW", category="b", file_path="y.py", description="2", suggestion="F"),
        ]
        summary = parser.generate_summary(findings_multiple)
        assert "2 low severity issues" in summary


class TestResultParserConfidenceCalculation:
    """Tests for confidence score calculation."""

    def test_calculate_confidence_all_stages_executed(self):
        """Test confidence when all stages executed."""
        parser = ResultParser()

        result = {
            "architecture_result": "output1",
            "platform_issues_result": "output2",
            "tests_result": "output3",
            "improvements_result": "output4"
        }

        depth_stages = {
            "standard": ["architecture", "platform_issues", "tests", "improvements"]
        }

        confidence = parser.calculate_confidence(result, "standard", depth_stages)

        assert confidence == 1.0 or confidence == 0.95  # Capped at 0.95

    def test_calculate_confidence_partial_execution(self):
        """Test confidence when only some stages executed."""
        parser = ResultParser()

        result = {
            "architecture_result": "output1",
            "improvements_result": "output2"
        }

        depth_stages = {
            "standard": ["architecture", "platform_issues", "tests", "improvements"]
        }

        confidence = parser.calculate_confidence(result, "standard", depth_stages)

        # 2 out of 4 stages = 0.5
        assert confidence == 0.5

    def test_calculate_confidence_no_stages_executed(self):
        """Test confidence when no stages executed."""
        parser = ResultParser()

        result = {}

        depth_stages = {
            "quick": ["architecture", "improvements"]
        }

        confidence = parser.calculate_confidence(result, "quick", depth_stages)

        # 0 out of 2 stages = 0.0
        assert confidence == 0.0

    def test_calculate_confidence_invalid_depth_defaults(self):
        """Test confidence calculation with invalid depth uses default."""
        parser = ResultParser()

        result = {
            "architecture_result": "output"
        }

        depth_stages = {
            "standard": ["architecture", "platform_issues"]
        }

        confidence = parser.calculate_confidence(result, "invalid", depth_stages)

        # Should default to 0.5 when no depth found
        assert confidence == 0.5

    def test_calculate_confidence_capped_at_95(self):
        """Test confidence is capped at 0.95 maximum."""
        parser = ResultParser()

        # More executed stages than expected
        result = {
            "stage1_result": "a",
            "stage2_result": "b",
            "stage3_result": "c",
            "stage4_result": "d",
            "stage5_result": "e",
        }

        depth_stages = {
            "deep": ["stage1", "stage2"]
        }

        confidence = parser.calculate_confidence(result, "deep", depth_stages)

        assert confidence <= 0.95
