"""CLI command for searching vault variables."""

from __future__ import annotations

import click

from envault.search import search_vault


@click.command("search")
@click.option("--key", "-k", default=None, help="Glob or regex pattern to match against keys.")
@click.option("--value", "-v", default=None, help="Glob or regex pattern to match against values.")
@click.option("--regex", "-r", is_flag=True, default=False, help="Treat patterns as regular expressions.")
@click.option("--project-dir", default=".", show_default=True, help="Path to the project directory.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def search_cmd(
    key: str | None,
    value: str | None,
    regex: bool,
    project_dir: str,
    password: str,
) -> None:
    """Search vault variables by key or value pattern."""
    if key is None and value is None:
        raise click.UsageError("Provide at least --key or --value pattern.")

    try:
        summary = search_vault(
            project_dir,
            password,
            key_pattern=key,
            value_pattern=value,
            use_regex=regex,
        )
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    if summary.total == 0:
        click.echo("No matching variables found.")
        return

    click.echo(f"Found {summary.total} matching variable(s):\n")
    for result in summary.results:
        tag = click.style(f"[{result.matched_on}]", fg="cyan")
        click.echo(f"  {click.style(result.key, bold=True)}={result.value}  {tag}")
