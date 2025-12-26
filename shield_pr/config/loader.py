"""Configuration loader with YAML file and environment variable support.

Implements configuration precedence: ENV vars > YAML file > defaults
Provides secure loading with validation and error handling.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from ..core.errors import ConfigError
from .defaults import DEFAULT_CONFIG_PATH
from .models import APIConfig, Config, OutputConfig, ReviewConfig


def load_yaml_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file (default: ~/.config/shield-pr/config.yaml)

    Returns:
        Dictionary with configuration values from YAML

    Raises:
        ConfigError: If file cannot be read or parsed
    """
    path = Path(config_path or DEFAULT_CONFIG_PATH).expanduser()

    if not path.exists():
        return {}  # Return empty dict if config file doesn't exist

    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to read config from {path}: {e}")


def load_env_overrides() -> Dict[str, Any]:
    """Load configuration overrides from environment variables.

    Environment variables follow pattern: CRA_<SECTION>_<KEY>
    Examples:
        CRA_API_KEY -> api.api_key
        CRA_MODEL -> api.model
        CRA_MAX_TOKENS -> api.max_tokens

    Returns:
        Dictionary with nested configuration from env vars
    """
    config: Dict[str, Any] = {"api": {}, "review": {}, "output": {}}

    # API configuration env vars
    if api_key := os.getenv("CRA_API_KEY"):
        config["api"]["api_key"] = api_key
    if model := os.getenv("CRA_MODEL"):
        config["api"]["model"] = model
    if max_tokens := os.getenv("CRA_MAX_TOKENS"):
        config["api"]["max_tokens"] = int(max_tokens)
    if temperature := os.getenv("CRA_TEMPERATURE"):
        config["api"]["temperature"] = float(temperature)
    if timeout := os.getenv("CRA_TIMEOUT"):
        config["api"]["timeout"] = int(timeout)

    # Review configuration env vars
    if depth := os.getenv("CRA_DEPTH"):
        config["review"]["depth"] = depth
    if platforms := os.getenv("CRA_PLATFORMS"):
        config["review"]["platforms"] = [p.strip() for p in platforms.split(",")]
    if focus_areas := os.getenv("CRA_FOCUS_AREAS"):
        config["review"]["focus_areas"] = [a.strip() for a in focus_areas.split(",")]

    # Output configuration env vars
    if output_format := os.getenv("CRA_OUTPUT_FORMAT"):
        config["output"]["format"] = output_format
    if output_file := os.getenv("CRA_OUTPUT_FILE"):
        config["output"]["file"] = output_file

    return config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two configuration dictionaries.

    Args:
        base: Base configuration
        override: Override configuration (takes precedence)

    Returns:
        Merged configuration dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        elif value:  # Only override if value is not empty
            result[key] = value

    return result


def load_config(config_path: Optional[str] = None, require_api_key: bool = True) -> Config:
    """Load and validate configuration from all sources.

    Configuration precedence (highest to lowest):
    1. Environment variables
    2. YAML configuration file
    3. Default values

    Args:
        config_path: Optional custom config file path
        require_api_key: Whether to require API key (default True)

    Returns:
        Validated Config object

    Raises:
        ConfigError: If configuration is invalid or API key is missing
    """
    try:
        # Load from all sources
        yaml_config = load_yaml_config(config_path)
        env_config = load_env_overrides()

        # Merge configs with precedence
        merged = merge_configs(yaml_config, env_config)

        # Validate API key presence
        if require_api_key and not merged.get("api", {}).get("api_key"):
            raise ConfigError(
                "API key required. Set CRA_API_KEY environment variable "
                "or add 'api.api_key' to config file"
            )

        # Validate with Pydantic
        config = Config(**merged)
        return config

    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            msg = error["msg"]
            error_messages.append(f"  - {field}: {msg}")

        raise ConfigError(
            f"Configuration validation failed:\n" + "\n".join(error_messages)
        )
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load configuration: {e}")
