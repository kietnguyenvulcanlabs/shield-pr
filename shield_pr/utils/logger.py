"""Rich console logger with API key masking for secure logging.

Provides styled console output using Rich library with automatic
sensitive data masking to prevent accidental credential exposure.
"""

import logging
import re
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


# Custom theme for code review assistant
CRA_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "debug": "dim",
    }
)


def mask_api_key(text: str) -> str:
    """Mask API keys in text for secure logging.

    Replaces API keys with asterisks to prevent exposure in logs.
    Detects patterns like: AIza..., sk-..., etc.

    Args:
        text: Text that may contain API keys

    Returns:
        Text with API keys masked
    """
    # Pattern for Google API keys (AIza... with at least 10 more chars)
    text = re.sub(r"AIza[A-Za-z0-9_-]{10,}", "AIza***", text)

    # Pattern for OpenAI-style keys (sk-... with at least 10 more chars)
    text = re.sub(r"sk-[A-Za-z0-9]{10,}", "sk-***", text)

    # Pattern for generic long alphanumeric keys (40+ chars)
    text = re.sub(r"\b([A-Za-z0-9]{40,})\b", "***", text)

    # Pattern for bearer tokens (at least 10 chars after Bearer)
    text = re.sub(r"Bearer\s+[A-Za-z0-9_-]{10,}", "Bearer ***", text, flags=re.IGNORECASE)

    return text


class MaskingFormatter(logging.Formatter):
    """Log formatter that masks sensitive data."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with API key masking."""
        original = super().format(record)
        return mask_api_key(original)


def setup_logger(
    name: str = "cra",
    level: int = logging.INFO,
    debug: bool = False,
) -> tuple[logging.Logger, Console]:
    """Set up Rich logger with masking and styling.

    Args:
        name: Logger name
        level: Logging level (default INFO)
        debug: Enable debug mode with file logging

    Returns:
        Tuple of (logger, console) for direct use
    """
    # Create console with custom theme
    console = Console(theme=CRA_THEME)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else level)
    logger.handlers.clear()  # Remove existing handlers

    # Rich console handler with masking
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=debug,
        markup=True,
    )
    console_handler.setFormatter(MaskingFormatter("%(message)s"))
    logger.addHandler(console_handler)

    # File handler for debug mode
    if debug:
        file_handler = logging.FileHandler("cra_debug.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            MaskingFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

    return logger, console


# Global logger instance
logger, console = setup_logger()
