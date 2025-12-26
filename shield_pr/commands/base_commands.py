"""
Base CLI commands - init, version, platforms.
"""

import click
from rich.console import Console


def init() -> None:
    """Initialize configuration file with interactive prompts."""
    console = Console()
    console.print("[bold cyan]Code Review Assistant - Configuration Setup[/bold cyan]")
    console.print()

    # TODO: Implement interactive config creation
    console.print("[yellow]Interactive configuration not yet implemented[/yellow]")
    console.print()
    console.print("For now, set these environment variables:")
    console.print("  export CRA_API_KEY='your-gemini-api-key'")
    console.print("  export CRA_MODEL='gemini-1.5-pro'  # optional")
    console.print()


def platforms() -> None:
    """List supported platforms and their detection patterns."""
    console = Console()
    console.print("[bold cyan]Supported Platforms[/bold cyan]")
    console.print()

    platforms_info = {
        "android": "Kotlin/Java Android applications",
        "ios": "Swift/Objective-C iOS applications",
        "ai-ml": "Python ML/AI models and pipelines",
        "frontend": "React/Vue/Angular web applications",
        "backend": "Node.js/Python/Go backend services",
    }

    for platform, desc in platforms_info.items():
        console.print(f"  [bold]{platform}[/bold]: {desc}")

    console.print()


def version() -> None:
    """Show version information."""
    console = Console()
    console.print("[bold cyan]Code Review Assistant[/bold cyan]")
    console.print("Version: 0.1.0")
    console.print("LangChain + Gemini 1.5 Pro")
