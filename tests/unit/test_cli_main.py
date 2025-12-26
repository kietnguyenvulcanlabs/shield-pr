"""Unit tests for main CLI command group."""

import os
from unittest.mock import MagicMock, patch

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


class TestMainCommand:
    """Test main CLI command group."""

    def test_main_help(self, runner):
        """Test main command shows help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AI-powered code review assistant" in result.output
        assert "--config" in result.output
        assert "--debug" in result.output

    def test_main_with_debug_flag(self, runner):
        """Test debug flag enables debug mode."""
        with patch("shield_pr.cli.setup_logger") as mock_setup:
            mock_setup.return_value = (MagicMock(), MagicMock())
            result = runner.invoke(main, ["--debug", "version"])
            assert result.exit_code == 0
            mock_setup.assert_called_once_with(debug=True)

    def test_main_with_config_file(self, runner, temp_config_file):
        """Test loading config from file."""
        result = runner.invoke(main, ["--config", temp_config_file, "version"])
        assert result.exit_code == 0

    def test_main_config_error_handling(self, runner):
        """Test config error handling for non-exempt commands."""
        with patch("shield_pr.cli.load_config") as mock_load:
            mock_load.side_effect = ConfigError("Config error")
            result = runner.invoke(main, ["review", "test.py"])
            assert result.exit_code == 1

    def test_main_without_debug_flag(self, runner):
        """Test main without debug flag."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
