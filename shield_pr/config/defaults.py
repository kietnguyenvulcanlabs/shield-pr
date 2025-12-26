"""Default configuration values for code review assistant.

Defines baseline configuration values that are used when no user
configuration is provided or as fallbacks for missing values.
"""

# API Configuration Defaults
DEFAULT_API_PROVIDER = "google"
DEFAULT_API_MODEL = "gemini-1.5-pro"
DEFAULT_TEMPERATURE = 0.35
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_MIN_WAIT = 2  # seconds
DEFAULT_RETRY_MAX_WAIT = 10  # seconds

# Review Configuration Defaults
DEFAULT_REVIEW_DEPTH = "standard"
DEFAULT_FOCUS_AREAS: list[str] = ["security", "performance", "maintainability"]
DEFAULT_PLATFORMS: list[str] = []  # Empty = auto-detect

# Output Configuration Defaults
DEFAULT_OUTPUT_FORMAT = "markdown"
DEFAULT_OUTPUT_FILE = None  # None = stdout

# Config File Location
DEFAULT_CONFIG_PATH = "~/.config/shield-pr/config.yaml"
