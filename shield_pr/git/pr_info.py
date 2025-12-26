"""
PR info fetching from GitHub/GitLab APIs.
"""

import requests
from typing import TYPE_CHECKING

from shield_pr.core.errors import APIError

if TYPE_CHECKING:
    from shield_pr.git.pr_fetcher import PRFetcher
    from shield_pr.git.pr_helpers import PRMetadata


def get_pr_info(fetcher: "PRFetcher", url: str) -> dict[str, str | int]:
    """
    Fetch PR metadata (title, author, etc.).

    Args:
        fetcher: PRFetcher instance.
        url: PR URL.

    Returns:
        Dict with PR metadata.
    """
    metadata = fetcher.parse_url(url)

    if metadata.platform == 'github':
        return _get_github_info(fetcher, metadata)
    else:
        return _get_gitlab_info(fetcher, metadata)


def _get_github_info(fetcher: PRFetcher, metadata: PRMetadata) -> dict[str, str | int]:
    """Fetch PR info from GitHub API."""
    api_url = fetcher.GITHUB_API.format(
        owner=metadata.owner,
        repo=metadata.repo,
        number=metadata.pr_number
    )

    response = fetcher._make_request(api_url)
    data = response.json()

    return {
        'title': data.get('title', ''),
        'author': data.get('user', {}).get('login', ''),
        'state': data.get('state', ''),
        'additions': data.get('additions', 0),
        'deletions': data.get('deletions', 0),
        'changed_files': data.get('changed_files', 0),
    }


def _get_gitlab_info(fetcher: PRFetcher, metadata: PRMetadata) -> dict[str, str | int]:
    """Fetch MR info from GitLab API."""
    api_url = fetcher.GITLAB_API.format(
        owner=metadata.owner,
        repo=metadata.repo,
        number=metadata.pr_number
    )

    response = fetcher._make_request(api_url)
    data = response.json()

    return {
        'title': data.get('title', ''),
        'author': data.get('author', {}).get('username', ''),
        'state': data.get('state', ''),
        'additions': data.get('additions', 0),
        'deletions': data.get('deletions', 0),
        'changed_files': data.get('changes_count', 0),
    }
