"""Unit tests for configuration loader.

Tests YAML loading, env var precedence, merging logic, and validation.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from shield_pr.config.loader import load_config, load_env_overrides, load_yaml_config, merge_configs
from shield_pr.core.errors import ConfigError


class TestLoadYAMLConfig:
    """Test YAML configuration loading."""

    def test_load_valid_yaml(self):
        """Should load valid YAML file successfully."""
        config_data = {
            "api": {"api_key": "test-key-12345", "model": "gemini-1.5-pro"},
            "review": {"depth": "standard"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            result = load_yaml_config(temp_path)
            assert result["api"]["api_key"] == "test-key-12345"
            assert result["api"]["model"] == "gemini-1.5-pro"
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Should return empty dict for nonexistent file."""
        result = load_yaml_config("/tmp/nonexistent-config.yaml")
        assert result == {}

    def test_load_invalid_yaml(self):
        """Should raise ConfigError for invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken")
            temp_path = f.name

        try:
            with pytest.raises(ConfigError, match="Invalid YAML"):
                load_yaml_config(temp_path)
        finally:
            os.unlink(temp_path)


class TestLoadEnvOverrides:
    """Test environment variable loading."""

    def test_load_api_key_from_env(self, monkeypatch):
        """Should load API key from CRA_API_KEY env var."""
        monkeypatch.setenv("CRA_API_KEY", "env-api-key-12345")
        result = load_env_overrides()
        assert result["api"]["api_key"] == "env-api-key-12345"

    def test_load_model_from_env(self, monkeypatch):
        """Should load model from CRA_MODEL env var."""
        monkeypatch.setenv("CRA_MODEL", "gemini-2.0-flash")
        result = load_env_overrides()
        assert result["api"]["model"] == "gemini-2.0-flash"

    def test_load_numeric_values(self, monkeypatch):
        """Should convert numeric env vars to correct types."""
        monkeypatch.setenv("CRA_MAX_TOKENS", "4096")
        monkeypatch.setenv("CRA_TEMPERATURE", "0.5")
        result = load_env_overrides()
        assert result["api"]["max_tokens"] == 4096
        assert result["api"]["temperature"] == 0.5

    def test_load_list_values(self, monkeypatch):
        """Should split comma-separated values into lists."""
        monkeypatch.setenv("CRA_PLATFORMS", "android,ios,backend")
        monkeypatch.setenv("CRA_FOCUS_AREAS", "security, performance")
        result = load_env_overrides()
        assert result["review"]["platforms"] == ["android", "ios", "backend"]
        assert result["review"]["focus_areas"] == ["security", "performance"]


class TestMergeConfigs:
    """Test configuration merging logic."""

    def test_merge_flat_dicts(self):
        """Should merge flat dictionaries correctly."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_configs(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Should deep merge nested dictionaries."""
        base = {"api": {"model": "gemini-1.5-pro", "temperature": 0.3}}
        override = {"api": {"temperature": 0.5}}
        result = merge_configs(base, override)
        assert result["api"]["model"] == "gemini-1.5-pro"
        assert result["api"]["temperature"] == 0.5

    def test_ignore_empty_overrides(self):
        """Should not override with empty values."""
        base = {"api": {"model": "gemini-1.5-pro"}}
        override = {"api": {"model": ""}}
        result = merge_configs(base, override)
        assert result["api"]["model"] == "gemini-1.5-pro"


class TestLoadConfig:
    """Test full configuration loading with validation."""

    def test_load_with_env_api_key(self, monkeypatch):
        """Should load config successfully with API key from env."""
        monkeypatch.setenv("CRA_API_KEY", "test-key-1234567890")
        config = load_config(require_api_key=True)
        assert config.api.api_key == "test-key-1234567890"

    def test_load_without_api_key_when_not_required(self, monkeypatch):
        """Should load without API key when not required."""
        # Clear any existing API key env var
        monkeypatch.delenv("CRA_API_KEY", raising=False)
        with pytest.raises(ConfigError, match="API key required"):
            load_config(require_api_key=True)

    def test_env_overrides_yaml(self, monkeypatch):
        """Env vars should override YAML values."""
        config_data = {"api": {"api_key": "yaml-key-12345", "model": "gemini-1.5-pro"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            monkeypatch.setenv("CRA_MODEL", "gemini-2.0-flash")
            config = load_config(config_path=temp_path, require_api_key=False)
            assert config.api.api_key == "yaml-key-12345"
            assert config.api.model == "gemini-2.0-flash"  # Env override
        finally:
            os.unlink(temp_path)

    def test_validation_error_handling(self, monkeypatch):
        """Should provide clear validation error messages."""
        monkeypatch.setenv("CRA_API_KEY", "short")  # Too short (< 10 chars)
        with pytest.raises(ConfigError, match="validation failed"):
            load_config()
