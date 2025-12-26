"""
Review diff command for staged changes.
"""

import click
from pathlib import Path

from shield_pr.git.repository import GitRepository
from shield_pr.git.filters import DiffFilter
from shield_pr.core.errors import GitOperationError


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
@click.pass_context
def review_diff(
    ctx: click.Context,
    staged: bool,
    branch: str | None,
    max_size: int,
    include_binary: bool
) -> None:
    """
    Review git changes.

    Examples:
        cra review-diff              # Review staged changes
        cra review-diff --branch main  # Compare with main branch
    """
    config = ctx.obj.config

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

        # TODO: Integrate with review pipeline
        # This will be completed after pipeline integration
        click.echo(f"\nReview pipeline integration pending...")

    except GitOperationError as e:
        click.echo(click.style(f"Git error: {e}", fg="red"), err=True)
        raise click.Abort()


def _format_change_type(change_type: str) -> str:
    """Format change type with emoji."""
    types = {
        'A': click.style('A', fg='green'),    # Added
        'M': click.style('M', fg='yellow'),   # Modified
        'D': click.style('D', fg='red'),      # Deleted
        'R': click.style('R', fg='blue'),     # Renamed
    }
    return types.get(change_type, change_type)
