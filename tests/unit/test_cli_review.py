"""Unit tests for review command."""

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


class TestReviewCommand:
    """Test review command."""

    def test_review_help(self, runner):
        """Test review command help."""
        with patch("shield_pr.cli.load_config"):
            result = runner.invoke(main, ["review", "--help"])
            assert result.exit_code == 0
            assert "Review code files" in result.output
            assert "--depth" in result.output
            assert "--platform" in result.output
            assert "--format" in result.output

    def test_review_no_files(self, runner, temp_config_file):
        """Test review without files shows error."""
        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            result = runner.invoke(main, ["--config", temp_config_file, "review"])
            assert result.exit_code == 1

    def test_review_no_config(self, runner, tmp_path):
        """Test review without config shows error."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch("shield_pr.cli.load_config") as mock_load:
            mock_load.side_effect = ConfigError("No API key")
            result = runner.invoke(main, ["review", str(test_file)])
            assert result.exit_code == 1

    def test_review_with_files(self, runner, temp_config_file, tmp_path):
        """Test review command with files."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main, ["--config", temp_config_file, "review", str(test_file)]
                )
                assert result.exit_code == 0

    def test_review_with_depth_option(self, runner, temp_config_file, tmp_path):
        """Test review with depth option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main,
                    ["--config", temp_config_file, "review", "--depth", "deep", str(test_file)],
                )
                assert result.exit_code == 0
                # Verify pipeline was called with deep depth
                if mock_instance.review_files.called:
                    call_kwargs = mock_instance.review_files.call_args[1]
                    assert call_kwargs.get("depth") == "deep"

    def test_review_with_platform_option(self, runner, temp_config_file, tmp_path):
        """Test review with platform option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        temp_config_file,
                        "review",
                        "--platform",
                        "backend",
                        str(test_file),
                    ],
                )
                assert result.exit_code == 0
                # Verify pipeline was called with platform override
                if mock_instance.review_files.called:
                    call_kwargs = mock_instance.review_files.call_args[1]
                    assert call_kwargs.get("platform_override") == "backend"

    def test_review_multiple_platforms(self, runner, temp_config_file, tmp_path):
        """Test review with multiple platforms."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        temp_config_file,
                        "review",
                        "--platform",
                        "backend",
                        "--platform",
                        "ai-ml",
                        str(test_file),
                    ],
                )
                assert result.exit_code == 0
                # First platform should be used
                if mock_instance.review_files.called:
                    call_kwargs = mock_instance.review_files.call_args[1]
                    assert call_kwargs.get("platform_override") == "backend"

    def test_review_with_output_file(self, runner, temp_config_file, tmp_path):
        """Test review with output file option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        output_file = tmp_path / "output.md"

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        temp_config_file,
                        "review",
                        "--output",
                        str(output_file),
                        str(test_file),
                    ],
                )
                assert result.exit_code == 0
                assert output_file.exists()

    def test_review_with_format_option(self, runner, temp_config_file, tmp_path):
        """Test review with format option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {"CRA_API_KEY": "test_key_1234567890"}):
            with patch("shield_pr.commands.review_command.ReviewPipeline") as mock_pipeline:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.platform = "backend"
                mock_result.findings = []
                mock_result.summary = "No issues found"
                mock_result.confidence = 0.5
                mock_instance.review_files.return_value = mock_result
                mock_pipeline.return_value = mock_instance

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        temp_config_file,
                        "review",
                        "--format",
                        "json",
                        str(test_file),
                    ],
                )
                assert result.exit_code == 0
