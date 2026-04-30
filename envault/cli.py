"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.vault import load_vault, save_vault, vault_path_for
from envault.cli_rotate import rotate_cmd
from envault.cli_diff import diff_cmd
from envault.cli_tags import tags_cmd
from envault.cli_template import template_cmd
from envault.cli_lint import lint_cmd
from envault.cli_search import search_cmd


@click.group()
def cli() -> None:
    """envault — encrypted .env manager with team-sharing support."""


@cli.command("init")
@click.option("--project-dir", default=".", show_default=True)
@click.password_option("--password", prompt="Vault password")
def init_vault(project_dir: str, password: str) -> None:
    """Initialise a new vault in the project directory."""
    path = vault_path_for(project_dir)
    if path.exists():
        raise click.ClickException(f"Vault already exists at {path}")
    save_vault(project_dir, password, {})
    click.echo(f"Vault initialised at {path}")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--project-dir", default=".", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def set_var(key: str, value: str, project_dir: str, password: str) -> None:
    """Set or update a variable in the vault."""
    try:
        variables = load_vault(project_dir, password)
    except FileNotFoundError:
        variables = {}
    variables[key] = value
    save_vault(project_dir, password, variables)
    click.echo(f"Set {key}")


@cli.command("list")
@click.option("--project-dir", default=".", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def list_vars(project_dir: str, password: str) -> None:
    """List all variable keys stored in the vault."""
    try:
        variables = load_vault(project_dir, password)
    except FileNotFoundError:
        raise click.ClickException("No vault found. Run `envault init` first.")
    if not variables:
        click.echo("Vault is empty.")
        return
    for key in sorted(variables):
        click.echo(key)


cli.add_command(rotate_cmd, "rotate")
cli.add_command(diff_cmd, "diff")
cli.add_command(tags_cmd, "tags")
cli.add_command(template_cmd, "template")
cli.add_command(lint_cmd, "lint")
cli.add_command(search_cmd, "search")


if __name__ == "__main__":
    cli()
