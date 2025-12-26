"""
Git integration module for code review assistant.
"""

from shield_pr.git.repository import GitRepository
from shield_pr.git.diff_parser import DiffParser
from shield_pr.git.filters import DiffFilter
from shield_pr.git.filter_patterns import default_ignore_patterns
from shield_pr.git.models import FileChange, DiffChange, ParsedDiff
from shield_pr.git.pr_helpers import PRMetadata
from shield_pr.git.pr_fetcher import PRFetcher

__all__ = [
    'GitRepository',
    'DiffParser',
    'ParsedDiff',
    'PRFetcher',
    'PRMetadata',
    'DiffFilter',
    'default_ignore_patterns',
    'FileChange',
    'DiffChange',
]
