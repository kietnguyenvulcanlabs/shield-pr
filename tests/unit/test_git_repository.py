"""
Unit tests for GitRepository.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from shield_pr.git.repository import GitRepository
from shield_pr.core.errors import GitOperationError
from shield_pr.git.models import FileChange


@pytest.fixture
def mock_repo():
    """Mock GitPython Repo object."""
    mock = MagicMock()
    mock.working_dir = "/fake/repo"
    mock.active_branch.name = "main"
    mock.is_dirty.return_value = False
    return mock


@pytest.fixture
def mock_diff():
    """Mock GitPython Diff object."""
    diff = MagicMock()
    diff.a_path = "file.py"
    diff.b_path = "file.py"
    diff.diff = b"@@ -1,1 +1,2 @@\n-old line\n+new line"
    diff.new_file = False
    diff.deleted_file = False
    diff.renamed_file = False
    return diff


class TestGitRepository:
    """Test GitRepository class."""

    def test_init_success(self, mock_repo):
        """Test successful initialization."""
        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository("/fake/path")
            assert repo.root == Path("/fake/repo")

    def test_init_not_git_repo(self):
        """Test initialization fails when not a git repo."""
        with patch('shield_pr.git.repository.Repo', side_effect=Exception("Not a repo")):
            with pytest.raises(GitOperationError):
                GitRepository("/fake/path")

    def test_current_branch(self, mock_repo):
        """Test getting current branch name."""
        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            assert repo.current_branch == "main"

    def test_is_dirty(self, mock_repo):
        """Test checking if repo is dirty."""
        mock_repo.is_dirty.return_value = True
        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            assert repo.is_dirty is True

    def test_get_staged_files_empty(self, mock_repo):
        """Test getting staged files when none exist."""
        mock_repo.index.diff.return_value = []
        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            files = repo.get_staged_files()
            assert files == {}

    def test_get_current_file_content(self, mock_repo, tmp_path):
        """Test getting current file content."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            repo.root = tmp_path
            content = repo.get_current_file_content("test.py")
            assert content == "print('hello')"

    def test_get_current_file_not_found(self, mock_repo):
        """Test getting non-existent file raises error."""
        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            with pytest.raises(GitOperationError):
                repo.get_current_file_content("nonexistent.py")

    def test_is_binary_file(self, mock_repo, tmp_path):
        """Test binary file detection."""
        # Create binary file
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03')

        # Create text file
        text_file = tmp_path / "text.txt"
        text_file.write_text("plain text")

        with patch('shield_pr.git.repository.Repo', return_value=mock_repo):
            repo = GitRepository()
            repo.root = tmp_path
            assert repo.is_binary("binary.bin") is True
            assert repo.is_binary("text.txt") is False
