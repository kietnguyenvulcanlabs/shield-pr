"""Unit tests for CLI context object."""

import pytest

from shield_pr.cli import CLIContext
from shield_pr.config.models import APIConfig, Config


class TestCLIContext:
    """Test CLI context object."""

    def test_init_default_values(self):
        """Test context initializes with correct defaults."""
        ctx = CLIContext()
        assert ctx.config is None
        assert ctx.debug is False
        assert ctx.console is not None

    def test_config_assignment(self):
        """Test config can be assigned."""
        ctx = CLIContext()
        config = Config(api=APIConfig(api_key="test_key_1234567890"))
        ctx.config = config
        assert ctx.config == config

    def test_debug_flag_assignment(self):
        """Test debug flag can be set."""
        ctx = CLIContext()
        ctx.debug = True
        assert ctx.debug is True

    def test_console_is_available(self):
        """Test console object is initialized."""
        ctx = CLIContext()
        assert hasattr(ctx.console, "print")
