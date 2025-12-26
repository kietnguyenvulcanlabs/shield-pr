"""
Main review command.
"""

import sys
from typing import Optional

import click

from shield_pr.formatters import get_formatter
from shield_pr.formatters.rich_renderer import RichRenderer
from shield_pr.core.review_pipeline import ReviewPipeline
from shield_pr.utils.logger import logger


@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--depth",
    type=click.Choice(["quick", "standard", "deep"]),
    default="standard",
    help="Review depth level",
)
@click.option(
    "--platform",
    type=click.Choice(["android", "ios", "ai-ml", "frontend", "backend"]),
    multiple=True,
    help="Platform to review for (auto-detect if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "json", "github", "gitlab", "slack"]),
    default="markdown",
    help="Output format",
)
@click.pass_context
def review(
    ctx: click.Context,
    files: tuple[str, ...],
    depth: str,
    platform: tuple[str, ...],
    output: Optional[str],
    format: str,
) -> None:
    """Review code files with AI analysis.

    Examples:
        shield-pr review src/main.py
        shield-pr review --platform android app/src/**/*.kt
        shield-pr review --depth deep --format json api/*.py
    """
    cli_ctx = ctx.obj
    if not cli_ctx.config:
        logger.error("Configuration required. Set CRA_API_KEY or run 'shield-pr init'.")
        sys.exit(1)

    if not files:
        logger.error("No files specified")
        sys.exit(1)

    # Determine platform override
    platform_override = platform[0] if platform else None

    try:
        # Create pipeline and review
        pipeline = ReviewPipeline(cli_ctx.config)
        result = pipeline.review_files(
            list(files),
            platform_override=platform_override,
            depth=depth,
        )

        # Format and output
        formatter = get_formatter(format)
        output_text = formatter.format(result)

        if output:
            with open(output, "w") as f:
                f.write(output_text)
            cli_ctx.console.print(f"[green]Results written to {output}[/green]")
        elif format == "json" or not sys.stdout.isatty():
            click.echo(output_text)
        else:
            RichRenderer(cli_ctx.console).render(result)

    except Exception as e:
        logger.error(f"Review failed: {e}")
        if cli_ctx.debug:
            raise
        sys.exit(1)
