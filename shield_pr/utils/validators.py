"""Input validation utilities for file paths, models, and review configs.

Provides validation functions with clear error messages for user inputs.
"""

import os
import re
from pathlib import Path
from typing import List

from ..core.errors import ValidationError


def validate_file_path(path: str, must_exist: bool = True) -> Path:
    """Validate file or directory path.

    Args:
        path: File or directory path to validate
        must_exist: Whether path must already exist (default True)

    Returns:
        Validated Path object

    Raises:
        ValidationError: If path is invalid or doesn't exist
    """
    if not path or not path.strip():
        raise ValidationError("Path cannot be empty")

    try:
        p = Path(path).expanduser().resolve()
    except Exception as e:
        raise ValidationError(f"Invalid path '{path}': {e}")

    if must_exist and not p.exists():
        raise ValidationError(f"Path does not exist: {p}")

    return p


def validate_model_name(model: str) -> str:
    """Validate LLM model name.

    Args:
        model: Model identifier (e.g., 'gemini-1.5-pro')

    Returns:
        Validated model name

    Raises:
        ValidationError: If model name is invalid
    """
    if not model or not model.strip():
        raise ValidationError("Model name cannot be empty")

    # Trim whitespace first
    model = model.strip()

    # Basic pattern: lowercase, numbers, hyphens, dots
    if not re.match(r"^[a-z0-9\-\.]+$", model):
        raise ValidationError(
            f"Invalid model name '{model}': must contain only lowercase letters, "
            "numbers, hyphens, and dots"
        )

    return model


def validate_review_depth(depth: str) -> str:
    """Validate review depth level.

    Args:
        depth: Review depth ('quick', 'standard', or 'deep')

    Returns:
        Validated depth level

    Raises:
        ValidationError: If depth is not valid
    """
    valid_depths = {"quick", "standard", "deep"}
    depth = depth.lower().strip()

    if depth not in valid_depths:
        raise ValidationError(
            f"Invalid review depth '{depth}': must be one of {valid_depths}"
        )

    return depth


def validate_platforms(platforms: List[str]) -> List[str]:
    """Validate platform selections.

    Args:
        platforms: List of platform names

    Returns:
        Validated and normalized platform names

    Raises:
        ValidationError: If any platform is invalid
    """
    valid_platforms = {"android", "ios", "ai-ml", "frontend", "backend"}
    normalized = [p.lower().strip() for p in platforms]

    invalid = set(normalized) - valid_platforms
    if invalid:
        raise ValidationError(
            f"Invalid platforms {invalid}: valid options are {valid_platforms}"
        )

    return normalized


def validate_output_format(format: str) -> str:
    """Validate output format.

    Args:
        format: Output format name

    Returns:
        Validated format

    Raises:
        ValidationError: If format is not supported
    """
    valid_formats = {"markdown", "json", "github", "gitlab", "slack"}
    format = format.lower().strip()

    if format not in valid_formats:
        raise ValidationError(
            f"Invalid output format '{format}': must be one of {valid_formats}"
        )

    return format
