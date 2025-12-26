"""
Unit tests for DiffParser.
"""

import pytest

from shield_pr.git.diff_parser import DiffParser
from shield_pr.git.models import ParsedDiff, DiffChange


class TestDiffParser:
    """Test DiffParser class."""

    @pytest.fixture
    def parser(self):
        """Create DiffParser instance."""
        return DiffParser()

    @pytest.fixture
    def sample_diff(self):
        """Sample unified diff text."""
        return """--- a/file.py
+++ b/file.py
@@ -1,5 +1,5 @@
 def hello():
-    print("old")
+    print("new")
     return True
+    # new comment
"""

    def test_parse_empty_diff(self, parser):
        """Test parsing empty diff."""
        result = parser.parse("")
        assert result == []

    def test_parse_single_file(self, parser, sample_diff):
        """Test parsing single file diff."""
        result = parser.parse(sample_diff)
        assert len(result) == 1
        assert result[0].file_path == "file.py"

    def test_parse_additions(self, parser, sample_diff):
        """Test detecting added lines."""
        result = parser.parse(sample_diff)
        assert len(result[0].added) == 2
        assert result[0].added[0].content == '    print("new")'
        assert result[0].added[1].content == '    # new comment'

    def test_parse_removals(self, parser, sample_diff):
        """Test detecting removed lines."""
        result = parser.parse(sample_diff)
        assert len(result[0].removed) == 1
        assert result[0].removed[0].content == '    print("old")'

    def test_parse_context(self, parser, sample_diff):
        """Test detecting context lines."""
        result = parser.parse(sample_diff)
        assert len(result[0].context) >= 2

    def test_extract_changes(self, parser, sample_diff):
        """Test extract_changes method."""
        changes = parser.extract_changes(sample_diff)
        assert "added" in changes
        assert "removed" in changes
        assert len(changes["added"]) == 2
        assert len(changes["removed"]) == 1

    def test_parse_single_file_method(self, parser, sample_diff):
        """Test parse_single_file method."""
        result = parser.parse_single_file(sample_diff)
        assert result is not None
        assert result.file_path == "file.py"

    def test_parse_single_file_empty(self, parser):
        """Test parse_single_file with empty input."""
        result = parser.parse_single_file("")
        assert result is None
