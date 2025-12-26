"""
Main review command.
"""

import sys
from typing import Optional

import click

from shield_pr.config.loader import load_config
from shield_pr.formatters import get_formatter
from shield_pr.formatters.rich_renderer import RichRenderer
from shield_pr.models.review_result import ReviewResult
from shield_pr.models.finding import Finding
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
    output: str | None,
    format: str,
) -> None:
    """Review code files with AI analysis.

    Examples:
        cra review src/main.py
        cra review --platform android app/src/**/*.kt
        cra review --depth deep --format json api/*.py
    """
    cli_ctx = ctx.obj
    if not cli_ctx.config:
        logger.error("Configuration required. Run 'cra init' first.")
        sys.exit(1)

    if not files:
        logger.error("No files specified")
        sys.exit(1)

    formatter = get_formatter(format)

    # TODO: Implement actual review logic with chain execution
    mock_result = ReviewResult(
        platform=platform[0] if platform else "backend",
        findings=[
            Finding(
                severity="HIGH",
                category="security",
                file_path=files[0],
                line_number=42,
                description="Example finding - review not yet implemented",
                suggestion="Implement chain execution to generate real findings",
            )
        ],
        summary=f"Review placeholder for {len(files)} file(s)",
        confidence=0.5,
    )

    output_text = formatter.format(mock_result)

    if output:
        with open(output, "w") as f:
            f.write(output_text)
        cli_ctx.console.print(f"[green]Results written to {output}[/green]")
    elif format == "json" or not sys.stdout.isatty():
        click.echo(output_text)
    else:
        RichRenderer().render(mock_result)
