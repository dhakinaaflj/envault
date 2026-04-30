"""CLI command for linting vault variables."""

from __future__ import annotations

import sys
import click

from envault.vault import load_vault
from envault.lint import lint_variables, format_lint_result


@click.command("lint")
@click.option("--project", "-p", default=".", show_default=True, help="Path to project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--warn-empty/--no-warn-empty", default=True, show_default=True, help="Warn on empty values.")
@click.option("--warn-long", default=0, show_default=True, help="Warn when value exceeds N chars (0=off).")
@click.option("--require", "required_keys", multiple=True, metavar="KEY", help="Keys that must be present.")
@click.option("--strict", is_flag=True, default=False, help="Exit with code 1 if any errors are found.")
def lint_cmd(
    project: str,
    password: str,
    warn_empty: bool,
    warn_long: int,
    required_keys: tuple[str, ...],
    strict: bool,
) -> None:
    """Lint vault variables for common issues."""
    try:
        variables = load_vault(project, password)
    except Exception as exc:
        click.echo(f"Error loading vault: {exc}", err=True)
        sys.exit(1)

    result = lint_variables(
        variables,
        warn_empty=warn_empty,
        warn_long_value=warn_long,
        required_keys=list(required_keys) if required_keys else None,
    )

    output = format_lint_result(result)
    click.echo(output)

    if strict and result.has_errors:
        sys.exit(1)
