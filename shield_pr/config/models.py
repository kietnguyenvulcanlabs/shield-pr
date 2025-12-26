"""Pydantic configuration models for validation and type safety.

Defines configuration schemas with validation rules, default values,
and type hints for the code review assistant.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from .defaults import (
    DEFAULT_API_MODEL,
    DEFAULT_API_PROVIDER,
    DEFAULT_FOCUS_AREAS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PLATFORMS,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_MAX_WAIT,
    DEFAULT_RETRY_MIN_WAIT,
    DEFAULT_REVIEW_DEPTH,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
)


class APIConfig(BaseModel):
    """API provider configuration with credentials and parameters."""

    provider: str = Field(default=DEFAULT_API_PROVIDER)
    model: str = Field(default=DEFAULT_API_MODEL)
    api_key: str = Field(..., min_length=10, description="API key for LLM provider")
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=1.0)
    max_tokens: int = Field(default=DEFAULT_MAX_TOKENS, ge=100, le=8192)
    timeout: int = Field(default=DEFAULT_TIMEOUT, ge=5, le=120)
    retry_attempts: int = Field(default=DEFAULT_RETRY_ATTEMPTS, ge=1, le=5)
    retry_min_wait: int = Field(default=DEFAULT_RETRY_MIN_WAIT, ge=1, le=30)
    retry_max_wait: int = Field(default=DEFAULT_RETRY_MAX_WAIT, ge=2, le=60)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Ensure API key is not a placeholder."""
        if v in ("", "your-api-key-here", "xxx", "placeholder"):
            raise ValueError("Invalid API key: must be a real key")
        return v

    @field_validator("retry_max_wait")
    @classmethod
    def validate_retry_waits(cls, v: int, info: ValidationInfo) -> int:
        """Ensure max wait is greater than min wait."""
        min_wait = info.data.get("retry_min_wait", DEFAULT_RETRY_MIN_WAIT)
        if v <= min_wait:
            raise ValueError("retry_max_wait must be greater than retry_min_wait")
        return v


class ReviewConfig(BaseModel):
    """Review process configuration."""

    depth: str = Field(default=DEFAULT_REVIEW_DEPTH, pattern="^(quick|standard|deep)$")
    platforms: List[str] = Field(default_factory=lambda: DEFAULT_PLATFORMS.copy())
    focus_areas: List[str] = Field(default_factory=lambda: DEFAULT_FOCUS_AREAS.copy())

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: List[str]) -> List[str]:
        """Validate platform names."""
        valid_platforms = {"android", "ios", "ai-ml", "frontend", "backend"}
        invalid = set(v) - valid_platforms
        if invalid:
            raise ValueError(f"Invalid platforms: {invalid}. Valid: {valid_platforms}")
        return v

    @field_validator("focus_areas")
    @classmethod
    def validate_focus_areas(cls, v: List[str]) -> List[str]:
        """Ensure focus areas are not empty."""
        if not v:
            raise ValueError("At least one focus area required")
        return v


class OutputConfig(BaseModel):
    """Output formatting configuration."""

    format: str = Field(
        default=DEFAULT_OUTPUT_FORMAT, pattern="^(markdown|json|github|gitlab|slack)$"
    )
    file: Optional[str] = Field(default=None)


class Config(BaseModel):
    """Root configuration model combining all sub-configurations."""

    api: APIConfig
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    model_config = {"extra": "forbid"}  # Reject unknown fields
