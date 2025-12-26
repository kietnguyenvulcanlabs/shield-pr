"""
Unit tests for DiffFilter.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from shield_pr.git.filters import DiffFilter
from shield_pr.git.filter_patterns import default_ignore_patterns


class TestDiffFilter:
    """Test DiffFilter class."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory with test files."""
        # Create some test files
        (tmp_path / "test.py").write_text("# python file")
        (tmp_path / "node_modules" / "lib.js").parent.mkdir(parents=True)
        (tmp_path / "node_modules" / "lib.js").write_text("javascript")
        (tmp_path / "dist" / "build.js").parent.mkdir(parents=True)
        (tmp_path / "dist" / "build.js").write_text("compiled")

        # Create large file
        (tmp_path / "large.py").write_bytes(b"x" * 200_000)

        # Create binary file
        (tmp_path / "binary.bin").write_bytes(b'\x00\x01\x02')

        return tmp_path

    def test_default_ignore_patterns(self):
        """Test default ignore patterns include common items."""
        assert 'node_modules/' in default_ignore_patterns
        assert '__pycache__/' in default_ignore_patterns
        assert '*.pyc' in default_ignore_patterns
        assert 'dist/' in default_ignore_patterns

    def test_should_ignore_node_modules(self, temp_dir):
        """Test node_modules is ignored by default."""
        filter_obj = DiffFilter()
        assert filter_obj.should_ignore("node_modules/lib.js", temp_dir) is True

    def test_should_ignore_dist(self, temp_dir):
        """Test dist directory is ignored."""
        filter_obj = DiffFilter()
        assert filter_obj.should_ignore("dist/build.js", temp_dir) is True

    def test_should_not_ignore_python(self, temp_dir):
        """Test Python files are not ignored."""
        filter_obj = DiffFilter()
        assert filter_obj.should_ignore("test.py", temp_dir) is False

    def test_is_too_large(self, temp_dir):
        """Test file size filtering."""
        filter_obj = DiffFilter(max_file_size=100_000)  # 100KB
        assert filter_obj.is_too_large("large.py", temp_dir) is True
        assert filter_obj.is_too_large("test.py", temp_dir) is False

    def test_is_binary_file(self, temp_dir):
        """Test binary file detection."""
        filter_obj = DiffFilter()
        assert filter_obj.is_binary_file("binary.bin", temp_dir) is True
        assert filter_obj.is_binary_file("test.py", temp_dir) is False

    def test_filter_files(self, temp_dir):
        """Test filtering multiple files."""
        filter_obj = DiffFilter(max_file_size=100_000)

        files = [
            "test.py",
            "node_modules/lib.js",
            "dist/build.js",
            "large.py",
            "binary.bin",
        ]

        filtered = filter_obj.filter_files(files, temp_dir)

        # Only test.py should pass all filters
        assert filtered == ["test.py"]

    def test_custom_ignore_patterns(self, temp_dir):
        """Test custom ignore patterns."""
        filter_obj = DiffFilter(ignore_patterns=["*.py"])
        assert filter_obj.should_ignore("test.py", temp_dir) is True

    def test_no_size_limit(self, temp_dir):
        """Test with no size limit."""
        filter_obj = DiffFilter(max_file_size=0)
        assert filter_obj.is_too_large("large.py", temp_dir) is False
