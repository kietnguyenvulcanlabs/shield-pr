"""
Review diff command for staged changes.
"""

import sys
from typing import Optional

import click

from shield_pr.formatters import get_formatter
from shield_pr.formatters.rich_renderer import RichRenderer
from shield_pr.git.repository import GitRepository
from shield_pr.git.filters import DiffFilter
from shield_pr.core.errors import GitOperationError
from shield_pr.core.review_pipeline import ReviewPipeline
from shield_pr.utils.logger import logger


@click.command('review-diff')
@click.option(
    '--staged',
    is_flag=True,
    help='Review staged changes (default)'
)
@click.option(
    '--branch',
    default=None,
    help='Compare against specific branch'
)
@click.option(
    '--max-size',
    default=100,
    help='Max file size in KB (default: 100)',
    type=int
)
@click.option(
    '--include-binary',
    is_flag=True,
    help='Include binary files'
)
@click.option(
    '--depth',
    type=click.Choice(['quick', 'standard', 'deep']),
    default='standard',
    help='Review depth level'
)
@click.option(
    '--platform',
    type=click.Choice(['android', 'ios', 'ai-ml', 'frontend', 'backend']),
    multiple=True,
    help='Platform to review for (auto-detect if not specified)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file (default: stdout)'
)
@click.option(
    '--format',
    '-f',
    type=click.Choice(['markdown', 'json', 'github', 'gitlab', 'slack']),
    default='markdown',
    help='Output format'
)
@click.pass_context
def review_diff(
    ctx: click.Context,
    staged: bool,
    branch: Optional[str],
    max_size: int,
    include_binary: bool,
    depth: str,
    platform: tuple[str, ...],
    output: Optional[str],
    format: str,
) -> None:
    """
    Review git changes.

    Examples:
        shield-pr review-diff                  # Review staged changes
        shield-pr review-diff --branch main    # Compare with main branch
        shield-pr review-diff --depth deep     # Deep review of changes
    """
    cli_ctx = ctx.obj
    if not cli_ctx.config:
        logger.error("Configuration required. Set CRA_API_KEY or run 'shield-pr init'.")
        sys.exit(1)

    try:
        repo = GitRepository()
        diff_filter = DiffFilter(
            max_file_size=max_size * 1024,
            respect_gitignore=True
        )

        # Get files to review
        if branch:
            click.echo(f"Comparing against branch: {branch}")
            files = repo.get_branch_diff(branch)
        else:
            click.echo("Reviewing staged changes...")
            files = repo.get_staged_files()

        if not files:
            click.echo(click.style("No changes found to review.", fg="yellow"))
            return

        # Filter files
        repo_root = repo.root
        filtered_paths = diff_filter.filter_files(files.keys(), repo_root)

        if not filtered_paths:
            click.echo(click.style("No files to review after filtering.", fg="yellow"))
            return

        click.echo(f"Found {len(filtered_paths)} files to review:\n")
        for path in filtered_paths:
            file_change = files[path]
            change_type = _format_change_type(file_change.change_type)
            click.echo(f"  {change_type} {path}")

        click.echo()

        # Prepare patches for review
        file_patches = {}
        for path in filtered_paths:
            file_change = files[path]
            # Skip deleted files for content review
            if file_change.change_type == 'D':
                continue
            file_patches[path] = file_change.patch

        if not file_patches:
            click.echo(click.style("No content changes to review.", fg="yellow"))
            return

        # Determine platform override
        platform_override = platform[0] if platform else None

        # Create pipeline and review
        pipeline = ReviewPipeline(cli_ctx.config)
        result = pipeline.review_diff(
            file_patches,
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

    except GitOperationError as e:
        click.echo(click.style(f"Git error: {e}", fg="red"), err=True)
        raise click.Abort()
    except Exception as e:
        logger.error(f"Review failed: {e}")
        if cli_ctx.debug:
            raise
        sys.exit(1)


def _format_change_type(change_type: str) -> str:
    """Format change type with emoji."""
    types = {
        'A': click.style('A', fg='green'),    # Added
        'M': click.style('M', fg='yellow'),   # Modified
        'D': click.style('D', fg='red'),      # Deleted
        'R': click.style('R', fg='blue'),     # Renamed
    }
    return types.get(change_type, change_type)
