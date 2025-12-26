"""
Unit tests for PRFetcher.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from shield_pr.git.pr_fetcher import PRFetcher, PRMetadata
from shield_pr.core.errors import ValidationError


class TestPRFetcher:
    """Test PRFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create PRFetcher instance."""
        return PRFetcher(token=None)

    def test_parse_github_url(self, fetcher):
        """Test parsing GitHub URL."""
        url = "https://github.com/org/repo/pull/123"
        metadata = fetcher.parse_url(url)
        assert metadata.platform == "github"
        assert metadata.owner == "org"
        assert metadata.repo == "repo"
        assert metadata.pr_number == 123

    def test_parse_gitlab_url(self, fetcher):
        """Test parsing GitLab URL."""
        url = "https://gitlab.com/org/repo/-/merge_requests/456"
        metadata = fetcher.parse_url(url)
        assert metadata.platform == "gitlab"
        assert metadata.owner == "org"
        assert metadata.repo == "repo"
        assert metadata.pr_number == 456

    def test_parse_invalid_url(self, fetcher):
        """Test parsing invalid URL raises error."""
        with pytest.raises(ValidationError):
            fetcher.parse_url("https://example.com/not-a-pr")

    def test_init_with_token(self):
        """Test initialization with token."""
        fetcher = PRFetcher(token="test-token")
        assert fetcher.token == "test-token"
        assert "Authorization" in fetcher.session.headers

    def test_init_without_token(self):
        """Test initialization without token."""
        fetcher = PRFetcher()
        assert fetcher.token is None
        assert "Authorization" not in fetcher.session.headers

    @patch('shield_pr.git.pr_fetcher.requests.Session.get')
    def test_make_request_success(self, mock_get, fetcher):
        """Test successful HTTP request."""
        mock_response = MagicMock()
        mock_response.text = "diff content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = fetcher._make_request("http://example.com")
        assert response.text == "diff content"

    @patch('shield_pr.git.pr_fetcher.requests.Session.get')
    def test_make_request_with_headers(self, mock_get, fetcher):
        """Test HTTP request with custom headers."""
        mock_response = MagicMock()
        mock_response.text = "response"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetcher._make_request("http://example.com", headers={"X-Custom": "value"})
        mock_get.assert_called_once()

    @patch('shield_pr.git.pr_fetcher.requests.Session.get')
    def test_make_request_failure(self, mock_get, fetcher):
        """Test HTTP request failure."""
        mock_get.side_effect = Exception("Network error")
        with pytest.raises(Exception):  # APIError wraps this
            fetcher._make_request("http://example.com")
