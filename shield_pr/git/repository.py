"""
Git repository wrapper using GitPython.

Handles repository operations: staged changes, branch diffs, and file content extraction.
"""

from pathlib import Path
from typing import Optional

from git import Repo, GitCommandError, InvalidGitRepositoryError

from shield_pr.core.errors import GitOperationError
from shield_pr.git.models import FileChange
from shield_pr.git.diff_helpers import get_file_changes_from_diffs


class GitRepository:
    """
    Wrapper around GitPython for repository operations.

    Supports:
    - Staged changes retrieval (git diff --cached)
    - Branch comparison (git diff base..head)
    - File content extraction
    """

    def __init__(self, path: str = "."):
        """
        Initialize repository wrapper.

        Args:
            path: Path to repository. Searches parent dirs if not found.

        Raises:
            GitOperationError: If not a git repository.
        """
        try:
            self.repo = Repo(path, search_parent_directories=True)
            self.root = Path(self.repo.working_dir)
        except InvalidGitRepositoryError as e:
            raise GitOperationError(f"Not a git repository: {path}") from e
        except Exception as e:
            raise GitOperationError(f"Failed to open repository: {e}") from e

    @property
    def current_branch(self) -> str:
        """Get current branch name."""
        try:
            return self.repo.active_branch.name
        except (TypeError, AttributeError):
            # Detached HEAD state
            return self.repo.head.commit.hexsha[:8]

    @property
    def is_dirty(self) -> bool:
        """Check if working directory has uncommitted changes."""
        return self.repo.is_dirty()

    def get_staged_files(self) -> dict[str, FileChange]:
        """
        Get staged changes (git diff --cached).

        Returns:
            Dict mapping file paths to FileChange objects.

        Raises:
            GitOperationError: If git operation fails.
        """
        try:
            diffs = self.repo.index.diff('HEAD', create_patch=True, R=True)
            return get_file_changes_from_diffs(diffs)
        except GitCommandError as e:
            raise GitOperationError(f"Failed to get staged files: {e}")

    def get_branch_diff(self, base_branch: str, head_branch: Optional[str] = None) -> dict[str, FileChange]:
        """
        Get diff between base branch and current/head branch.

        Args:
            base_branch: Base branch to compare against.
            head_branch: Head branch (default: current branch).

        Returns:
            Dict mapping file paths to FileChange objects.

        Raises:
            GitOperationError: If git operation fails.
        """
        try:
            base_commit = self.repo.commit(base_branch)
            head_commit = self.repo.commit(head_branch) if head_branch else self.repo.head.commit

            diffs = base_commit.diff(head_commit, create_patch=True, R=True)
            return get_file_changes_from_diffs(diffs)
        except GitCommandError as e:
            raise GitOperationError(f"Failed to get branch diff: {e}")
        except ValueError as e:
            raise GitOperationError(f"Invalid branch: {e}")

    def get_file_content(self, file_path: str, ref: str = "HEAD") -> str:
        """
        Get file content at a specific ref.

        Args:
            file_path: Relative path to file.
            ref: Git ref (commit, branch, tag).

        Returns:
            File content as string.

        Raises:
            GitOperationError: If file not found or read fails.
        """
        try:
            tree = self.repo.commit(ref).tree
            full_path = file_path.lstrip('/')

            parts = full_path.split('/')
            obj = tree
            for part in parts:
                obj = obj[part]

            data = obj.data_stream.read()
            if isinstance(data, bytes):
                return data.decode('utf-8')
            return str(data)
        except KeyError:
            raise GitOperationError(f"File not found: {file_path}")
        except (GitCommandError, ValueError) as e:
            raise GitOperationError(f"Failed to read file: {e}")

    def get_current_file_content(self, file_path: str) -> str:
        """
        Get current file content from working directory.

        Args:
            file_path: Relative path to file.

        Returns:
            File content as string.
        """
        full_path = self.root / file_path
        if not full_path.exists():
            raise GitOperationError(f"File not found: {file_path}")
        return full_path.read_text(encoding='utf-8')

    def is_binary(self, file_path: str) -> bool:
        """
        Check if file is binary by examining git attributes.

        Args:
            file_path: Relative path to file.

        Returns:
            True if file is binary.
        """
        try:
            full_path = self.root / file_path
            if not full_path.exists():
                return False

            # Check first few bytes for null (common binary indicator)
            with open(full_path, 'rb') as f:
                chunk = f.read(8192)
                return b'\x00' in chunk
        except (OSError, IOError):
            return False

    def get_tracked_files(self) -> list[str]:
        """
        Get list of all tracked files in repository.

        Returns:
            List of relative file paths.
        """
        from git.objects import Blob

        result: list[str] = []
        try:
            for item in self.repo.head.commit.tree.traverse():
                if hasattr(item, 'type') and getattr(item, 'type', None) == 'blob':
                    if hasattr(item, 'path'):
                        result.append(str(getattr(item, 'path', '')))
        except Exception:
            pass
        return result
