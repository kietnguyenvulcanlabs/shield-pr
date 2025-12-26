"""
Review PR command for pull/merge requests.
"""

import click
from pathlib import Path

from shield_pr.git.repository import GitRepository
from shield_pr.git.pr_fetcher import PRFetcher
from shield_pr.git.filters import DiffFilter
from shield_pr.git.diff_parser import DiffParser
from shield_pr.core.errors import GitOperationError, APIError, ValidationError


@click.command('pr')
@click.option(
    '--branch',
    default='main',
    help='Base branch to compare (default: main)'
)
@click.option(
    '--url',
    default=None,
    help='GitHub/GitLab PR URL to review'
)
@click.option(
    '--max-size',
    default=100,
    help='Max file size in KB (default: 100)',
    type=int
)
@click.pass_context
def review_pr(
    ctx: click.Context,
    branch: str,
    url: str | None,
    max_size: int
) -> None:
    """
    Review pull request changes.

    Examples:
        cra pr --branch main           # Compare current branch to main
        cra pr --url <github-url>      # Review GitHub PR via URL
    """
    config = ctx.obj['config']

    try:
        diff_filter = DiffFilter(
            max_file_size=max_size * 1024,
            respect_gitignore=True
        )

        if url:
            # Fetch PR from URL
            click.echo(f"Fetching PR: {url}")

            token = getattr(config, 'github_token', None) or getattr(config, 'gitlab_token', None)
            fetcher = PRFetcher(token=token)

            # Get PR info
            try:
                info = fetcher.get_pr_info(url)
                click.echo(f"\nPR: {info.get('title', 'N/A')}")
                click.echo(f"Author: {info.get('author', 'N/A')}")
                click.echo(f"Changes: +{info.get('additions', 0)} -{info.get('deletions', 0)}")
                click.echo(f"Files: {info.get('changed_files', 0)}\n")
            except APIError:
                click.echo(click.style("Could not fetch PR info (auth may be required)", fg="yellow"))

            # Fetch diff
            diff_text = fetcher.fetch_pr_diff(url)

            # Parse diff
            parser = DiffParser()
            parsed = parser.parse(diff_text)

            if not parsed:
                click.echo(click.style("No files found in PR diff.", fg="yellow"))
                return

            # Extract file paths
            files = {d.file_path: d for d in parsed}
            file_paths = list(files.keys())

        else:
            # Compare branches locally
            repo = GitRepository()
            current_branch = repo.current_branch

            click.echo(f"Comparing {current_branch} -> {branch}")
            file_changes = repo.get_branch_diff(branch)
            file_paths = list(file_changes.keys())

        if not file_paths:
            click.echo(click.style("No changes found to review.", fg="yellow"))
            return

        # Filter files
        repo_root = Path.cwd()  # Or repo.root if GitRepository available
        filtered_paths = diff_filter.filter_files(file_paths, repo_root)

        if not filtered_paths:
            click.echo(click.style("No files to review after filtering.", fg="yellow"))
            return

        click.echo(f"\nFiles to review: {len(filtered_paths)}\n")
        for path in filtered_paths[:20]:  # Show first 20
            click.echo(f"  - {path}")

        if len(filtered_paths) > 20:
            click.echo(f"  ... and {len(filtered_paths) - 20} more")

        # TODO: Integrate with review pipeline
        click.echo(f"\nReview pipeline integration pending...")

    except (GitOperationError, APIError, ValidationError) as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        raise click.Abort()
