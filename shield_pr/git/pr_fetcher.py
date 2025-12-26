"""
Pull request fetcher for GitHub and GitLab APIs.
"""

from typing import Optional

import requests

from shield_pr.core.errors import APIError
from shield_pr.git.pr_helpers import parse_pr_url, PRMetadata, GITHUB_PATTERN, GITLAB_PATTERN


class PRFetcher:
    """
    Fetch PR diffs from GitHub/GitLab APIs.

    Supports:
    - GitHub: https://github.com/org/repo/pull/123
    - GitLab: https://gitlab.com/org/repo/-/merge_requests/123
    """

    GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    GITLAB_API = "https://gitlab.com/api/v4/projects/{owner}%2F{repo}/merge_requests/{number}"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize PR fetcher.

        Args:
            token: Optional API token for authentication.
        """
        self.token = token
        self.session = requests.Session()
        self.timeout = 30

        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})

    def parse_url(self, url: str) -> PRMetadata:
        """Parse PR URL to extract metadata."""
        return parse_pr_url(url)

    def fetch_pr_diff(self, url: str) -> str:
        """Fetch PR diff from GitHub/GitLab API."""
        metadata = self.parse_url(url)

        if metadata.platform == 'github':
            return self._fetch_github_diff(metadata)
        else:
            return self._fetch_gitlab_diff(metadata)

    def _fetch_github_diff(self, metadata: PRMetadata) -> str:
        """Fetch diff from GitHub API."""
        api_url = self.GITHUB_API.format(
            owner=metadata.owner,
            repo=metadata.repo,
            number=metadata.pr_number
        )

        headers = {'Accept': 'application/vnd.github.v3.diff'}
        response = self._make_request(api_url, headers=headers)
        return response.text

    def _fetch_gitlab_diff(self, metadata: PRMetadata) -> str:
        """Fetch diff from GitLab API."""
        api_url = self.GITLAB_API.format(
            owner=metadata.owner,
            repo=metadata.repo,
            number=metadata.pr_number
        )

        response = self._make_request(api_url)
        data = response.json()

        # GitLab returns diffs as array of objects
        diffs = []
        for change in data.get('changes', []):
            diff = change.get('diff', '')
            if diff:
                new_path = change.get('new_path', '')
                old_path = change.get('old_path', '')
                diffs.append(f"--- a/{old_path}\n+++ b/{new_path}\n{diff}")

        return '\n'.join(diffs)

    def _make_request(self, url: str, headers: Optional[dict[str, str]] = None) -> requests.Response:
        """Make HTTP request with error handling."""
        req_headers = {}
        if headers:
            req_headers.update(headers)

        try:
            response = self.session.get(url, headers=req_headers, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch PR: {e}")

    def get_pr_info(self, url: str) -> dict[str, str | int]:
        """Fetch PR metadata (title, author, etc.)."""
        from shield_pr.git.pr_info import get_pr_info
        return get_pr_info(self, url)
