"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.vault import load_vault, save_vault, vault_path_for
from envault.cli_rotate import rotate_cmd
from envault.cli_diff import diff_cmd
from envault.cli_tags import tags_cmd
from envault.cli_template import template_cmd
from envault.cli_lint import lint_cmd


@click.group()
def cli() -> None:
    """envault — encrypted per-project .env manager."""


@cli.command("init")
@click.option("--project", "-p", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def init_vault(project: str, password: str) -> None:
    """Initialise a new empty vault for a project."""
    path = vault_path_for(project)
    if path.exists():
        click.echo(f"Vault already exists at {path}")
        return
    save_vault(project, {}, password)
    click.echo(f"Vault initialised at {path}")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--project", "-p", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set_var(key: str, value: str, project: str, password: str) -> None:
    """Set a variable in the vault."""
    variables = load_vault(project, password)
    variables[key] = value
    save_vault(project, variables, password)
    click.echo(f"Set {key}")


@cli.command("list")
@click.option("--project", "-p", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def list_vars(project: str, password: str) -> None:
    """List all variable keys in the vault."""
    variables = load_vault(project, password)
    if not variables:
        click.echo("(empty vault)")
        return
    for key in sorted(variables):
        click.echo(key)


cli.add_command(rotate_cmd, "rotate")
cli.add_command(diff_cmd, "diff")
cli.add_command(tags_cmd, "tags")
cli.add_command(template_cmd, "template")
cli.add_command(lint_cmd, "lint")


if __name__ == "__main__":
    cli()
