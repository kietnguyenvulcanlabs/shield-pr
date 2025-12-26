"""
Helper functions for PR operations.
"""

import re
from typing import Optional
from urllib.parse import urlparse
from dataclasses import dataclass

from shield_pr.core.errors import ValidationError


@dataclass
class PRMetadata:
    """Metadata for a pull request."""
    platform: str  # 'github' or 'gitlab'
    owner: str
    repo: str
    pr_number: int
    title: str = ""
    url: str = ""


# URL patterns
GITHUB_PATTERN = re.compile(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)')
GITLAB_PATTERN = re.compile(r'gitlab\.com/([^/]+)/([^/]+)/-/merge_requests/(\d+)')


def parse_pr_url(url: str) -> PRMetadata:
    """
    Parse PR URL to extract metadata.

    Args:
        url: PR URL (GitHub or GitLab).

    Returns:
        PRMetadata object.

    Raises:
        ValidationError: If URL is invalid.
    """
    parsed = urlparse(url)

    # GitHub
    github_match = GITHUB_PATTERN.search(url)
    if github_match:
        return PRMetadata(
            platform='github',
            owner=github_match.group(1),
            repo=github_match.group(2),
            pr_number=int(github_match.group(3)),
            url=url
        )

    # GitLab
    gitlab_match = GITLAB_PATTERN.search(url)
    if gitlab_match:
        return PRMetadata(
            platform='gitlab',
            owner=gitlab_match.group(1),
            repo=gitlab_match.group(2),
            pr_number=int(gitlab_match.group(3)),
            url=url
        )

    raise ValidationError(f"Invalid PR URL: {url}")
