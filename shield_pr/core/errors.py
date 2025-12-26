"""Custom exception classes for code review assistant.

Defines domain-specific exceptions for configuration, API, and validation errors.
All exceptions inherit from CRAError base class for easy catching.
"""


class CRAError(Exception):
    """Base exception for all code review assistant errors."""

    pass


class ConfigError(CRAError):
    """Raised when configuration loading or validation fails.

    Examples:
        - Missing API key
        - Invalid YAML syntax
        - Schema validation failures
    """

    pass


class APIError(CRAError):
    """Raised when API calls to LLM provider fail.

    Examples:
        - Network timeouts
        - Invalid API responses
        - Authentication failures
    """

    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded.

    This is a specific type of APIError that can trigger
    exponential backoff retry logic.
    """

    pass


class ValidationError(CRAError):
    """Raised when input validation fails.

    Examples:
        - Invalid file paths
        - Malformed review configurations
        - Invalid platform selections
    """

    pass


class FileProcessingError(CRAError):
    """Raised when file operations fail.

    Examples:
        - File not found
        - Permission denied
        - Invalid file format
    """

    pass


class ReviewError(CRAError):
    """Raised when code review chain execution fails.

    Examples:
        - LLM API failures during review
        - Parsing failures
        - Chain execution errors
    """

    pass


class GitOperationError(CRAError):
    """Raised when git operations fail.

    Examples:
        - Not a git repository
        - Invalid branch names
        - Git command failures
    """

    pass


class FilterError(CRAError):
    """Raised when file filtering operations fail.

    Examples:
        - Invalid filter patterns
        - Gitignore parsing failures
    """

    pass
