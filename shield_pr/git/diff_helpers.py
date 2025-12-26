"""
Helper functions for git diff operations.
"""

from typing import Optional
from git.diff import Diff

from shield_pr.git.models import FileChange


def decode_change_type(diff: Diff) -> str:
    """
    Decode Git diff change type to single character.

    Returns:
        'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed)
    """
    if diff.new_file:
        return 'A'
    elif diff.deleted_file:
        return 'D'
    elif diff.renamed_file:
        return 'R'
    else:
        return 'M'


def get_file_changes_from_diffs(diffs: list[Diff]) -> dict[str, FileChange]:
    """
    Convert GitPython diffs to FileChange objects.

    Args:
        diffs: List of Diff objects from GitPython.

    Returns:
        Dict mapping file paths to FileChange objects.
    """
    result = {}

    for diff in diffs:
        change_type = decode_change_type(diff)
        path = diff.b_path or diff.a_path or ""
        file_change = FileChange(
            path=path,
            change_type=change_type,
            old_path=diff.a_path if diff.a_path != diff.b_path else None,
            patch=diff.diff.decode('utf-8') if diff.diff and isinstance(diff.diff, bytes) else (diff.diff or "")
        )
        result[file_change.path] = file_change

    return result
