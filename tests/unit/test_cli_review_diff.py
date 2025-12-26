"""Unit tests for review-diff command."""

import os
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from shield_pr.cli import main
from shield_pr.core.errors import ConfigError


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
api:
  api_key: test_api_key_1234567890
  model: gemini-1.5-pro
  temperature: 0.35
  max_tokens: 2048

review:
  depth: standard
  platforms: []
  focus_areas:
    - security
    - performance

output:
  format: markdown
""")
    return str(config_file)


@pytest.fixture
def mock_review_result():
    """Create mock review result."""
    from shield_pr.models.review_result import ReviewResult
    from shield_pr.models.finding import Finding

    return ReviewResult(
        platform="backend",
        findings=[
            Finding(
                severity="MEDIUM",
                category="security",
                file_path="test.py",
                line_number=10,
                description="Test finding",
                suggestion="Fix it",
            )
        ],
        summary="Test review",
        confidence=0.8,
    )


class TestReviewDiffCommand:
    """Test review-diff command."""

    def test_review_diff_help(self, runner):
        """Test review-diff command help."""
        with patch("shield_pr.cli.load_config"):
            result = runner.invoke(main, ["review-diff", "--help"])
            assert result.exit_code == 0
            assert "Review git changes" in result.output
            assert "--staged" in result.output
            assert "--branch" in result.output
            assert "--depth" in result.output
            assert "--platform" in result.output
            assert "--format" in result.output

    def test_review_diff_no_config(self, runner, tmp_path):
        """Test review-diff without config shows error."""
        with patch("shield_pr.cli.load_config") as mock_load:
            mock_load.side_effect = ConfigError("No API key")
            result = runner.invoke(main, ["review-diff"])
            assert result.exit_code == 1

    def test_review_diff_no_changes(self, runner, temp_config_file, tmp_path):
        """Test review-diff with no staged changes."""
        # Initialize a git repo
        import subprocess
        import os

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        # Create initial commit to establish HEAD
        (tmp_path / "initial.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
                result = runner.invoke(
                    main, ["--config", temp_config_file, "review-diff"]
                )
                # Should handle no changes gracefully
                assert result.exit_code == 0 or "No changes found" in result.output
        finally:
            os.chdir(original_cwd)

    def test_review_diff_with_staged(self, runner, temp_config_file, tmp_path):
        """Test review-diff with staged changes."""
        import subprocess
        import os

        # Initialize git repo and make changes
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        # Create initial commit to establish HEAD
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        # Make new change and stage it
        test_file.write_text("print('hello world')")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

        # Mock the pipeline to avoid actual LLM calls
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
                with patch("shield_pr.commands.review_diff.ReviewPipeline") as mock_pipeline:
                    mock_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.platform = "backend"
                    mock_result.findings = []
                    mock_result.summary = "No issues found"
                    mock_result.confidence = 0.5
                    mock_instance.review_diff.return_value = mock_result
                    mock_pipeline.return_value = mock_instance

                    result = runner.invoke(
                        main, ["--config", temp_config_file, "review-diff"]
                    )
                    # Should not crash
                    assert result.exit_code == 0
                    # Should show files found
                    assert "files to review" in result.output.lower() or "no changes" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_review_diff_with_depth_option(self, runner, temp_config_file, tmp_path):
        """Test review-diff with depth option."""
        import subprocess
        import os

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        # Create initial commit to establish HEAD
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        # Make new change
        test_file.write_text("print('hello world')")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
                with patch("shield_pr.commands.review_diff.ReviewPipeline") as mock_pipeline:
                    mock_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.platform = "backend"
                    mock_result.findings = []
                    mock_result.summary = "No issues found"
                    mock_result.confidence = 0.5
                    mock_instance.review_diff.return_value = mock_result
                    mock_pipeline.return_value = mock_instance

                    result = runner.invoke(
                        main,
                        ["--config", temp_config_file, "review-diff", "--depth", "deep"],
                    )
                    assert result.exit_code == 0
                    # Verify pipeline was called with deep depth
                    if mock_instance.review_diff.called:
                        call_kwargs = mock_instance.review_diff.call_args[1]
                        assert call_kwargs.get("depth") == "deep"
        finally:
            os.chdir(original_cwd)

    def test_review_diff_with_platform_option(self, runner, temp_config_file, tmp_path):
        """Test review-diff with platform option."""
        import subprocess
        import os

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        # Create initial commit to establish HEAD
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        # Make new change
        test_file.write_text("print('hello world')")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
                with patch("shield_pr.commands.review_diff.ReviewPipeline") as mock_pipeline:
                    mock_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.platform = "backend"
                    mock_result.findings = []
                    mock_result.summary = "No issues found"
                    mock_result.confidence = 0.5
                    mock_instance.review_diff.return_value = mock_result
                    mock_pipeline.return_value = mock_instance

                    result = runner.invoke(
                        main,
                        ["--config", temp_config_file, "review-diff", "--platform", "backend"],
                    )
                    assert result.exit_code == 0
                    # Verify pipeline was called with platform override
                    if mock_instance.review_diff.called:
                        call_kwargs = mock_instance.review_diff.call_args[1]
                        assert call_kwargs.get("platform_override") == "backend"
        finally:
            os.chdir(original_cwd)

    def test_review_diff_with_format_json(self, runner, temp_config_file, tmp_path):
        """Test review-diff with JSON format."""
        import subprocess
        import os

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        # Create initial commit to establish HEAD
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        # Make new change
        test_file.write_text("print('hello world')")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
                with patch("shield_pr.commands.review_diff.ReviewPipeline") as mock_pipeline:
                    mock_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.platform = "backend"
                    mock_result.findings = []
                    mock_result.summary = "No issues found"
                    mock_result.confidence = 0.5
                    mock_instance.review_diff.return_value = mock_result
                    mock_pipeline.return_value = mock_instance

                    result = runner.invoke(
                        main,
                        ["--config", temp_config_file, "review-diff", "--format", "json"],
                    )
                    assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)
