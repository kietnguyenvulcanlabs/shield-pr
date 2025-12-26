"""Click CLI entry point for code review assistant.

Provides main command group with global options and subcommands
for review operations, initialization, and platform management.
"""

import sys
from typing import Optional

import click
from rich.console import Console

from shield_pr.config.loader import load_config
from shield_pr.core.errors import CRAError, ConfigError
from shield_pr.utils.logger import logger, setup_logger


class CLIContext:
    """Shared context object for CLI commands."""

    def __init__(self) -> None:
        self.config: Optional["Config"] = None  # type: ignore[name-defined]
        self.debug = False
        self.console = Console()


pass_context = click.make_pass_decorator(CLIContext, ensure=True)


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file (default: ~/.config/shield-pr/config.yaml)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging",
)
@click.pass_context
def main(ctx: click.Context, config: Optional[str], debug: bool) -> None:
    """AI-powered code review assistant CLI.

    Analyze code with platform-specific review chains using Gemini LLM.
    Supports Android, iOS, AI/ML, Frontend, and Backend platforms.
    """
    cli_ctx = CLIContext()
    cli_ctx.debug = debug
    ctx.obj = cli_ctx

    if debug:
        global logger
        logger, cli_ctx.console = setup_logger(debug=True)
        logger.debug("Debug mode enabled")

    if ctx.invoked_subcommand not in ["init", "version", "platforms"]:
        try:
            cli_ctx.config = load_config(config, require_api_key=False)
            logger.debug("Configuration loaded successfully")
        except ConfigError as e:
            if "--help" not in sys.argv:
                logger.error(f"Configuration error: {e}")
                logger.info(
                    "Run 'cra init' to create a config file or set CRA_API_KEY environment variable"
                )
                sys.exit(1)


# Register commands
from shield_pr.commands.base_commands import init as init_fn, platforms, version
from shield_pr.commands.review_command import review

main.command("init")(init_fn)
main.command("platforms")(platforms)
main.command("version")(version)
main.command("review")(review)

from shield_pr.commands.review_diff import review_diff
from shield_pr.commands.review_pr import review_pr

main.add_command(review_diff)
main.add_command(review_pr)


if __name__ == "__main__":
    try:
        main()
    except CRAError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)
