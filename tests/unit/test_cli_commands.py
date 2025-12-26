"""Unit tests for CLI subcommands (init, version, platforms)."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from shield_pr.cli import main


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


class TestInitCommand:
    """Test init command."""

    def test_init_command(self, runner):
        """Test init displays setup instructions."""
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert "Configuration Setup" in result.output
        assert "CRA_API_KEY" in result.output

    def test_init_no_config_required(self, runner):
        """Test init doesn't require existing config."""
        with patch("shield_pr.cli.load_config") as mock_load:
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0
            mock_load.assert_not_called()

    def test_init_shows_environment_variables(self, runner):
        """Test init shows required env vars."""
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert "export CRA_API_KEY" in result.output
        assert "export CRA_MODEL" in result.output


class TestPlatformsCommand:
    """Test platforms command."""

    def test_platforms_command(self, runner):
        """Test platforms list display."""
        result = runner.invoke(main, ["platforms"])
        assert result.exit_code == 0
        assert "Supported Platforms" in result.output
        assert "android" in result.output
        assert "ios" in result.output
        assert "ai-ml" in result.output
        assert "frontend" in result.output
        assert "backend" in result.output

    def test_platforms_no_config_required(self, runner):
        """Test platforms doesn't require config."""
        with patch("shield_pr.cli.load_config") as mock_load:
            result = runner.invoke(main, ["platforms"])
            assert result.exit_code == 0
            mock_load.assert_not_called()

    def test_platforms_descriptions(self, runner):
        """Test platforms shows descriptions."""
        result = runner.invoke(main, ["platforms"])
        assert result.exit_code == 0
        assert "Kotlin/Java" in result.output
        assert "Swift/Objective-C" in result.output


class TestVersionCommand:
    """Test version command."""

    def test_version_command(self, runner):
        """Test version displays correct info."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "Code Review Assistant" in result.output
        assert "0.1.0" in result.output
        assert "Gemini" in result.output

    def test_version_no_config_required(self, runner):
        """Test version doesn't require config."""
        with patch("shield_pr.cli.load_config") as mock_load:
            result = runner.invoke(main, ["version"])
            assert result.exit_code == 0
            mock_load.assert_not_called()

    def test_version_shows_langchain(self, runner):
        """Test version mentions LangChain."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "LangChain" in result.output
