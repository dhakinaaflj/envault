"""Main CLI entry point for envault."""

import click

from envault.vault import load_vault, save_vault
from envault.cli_rotate import rotate_cmd
from envault.cli_diff import diff_cmd


@click.group()
def cli() -> None:
    """envault — encrypted .env manager with team-sharing support."""


@cli.command("init")
@click.argument("project_dir", default=".", type=click.Path(file_okay=False))
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def init_vault(project_dir: str, password: str) -> None:
    """Initialise a new empty vault in PROJECT_DIR."""
    save_vault(project_dir, password, {})
    click.echo(f"Vault initialised in {project_dir}")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--project-dir", default=".", type=click.Path(file_okay=False))
@click.option("--password", prompt=True, hide_input=True)
def set_var(key: str, value: str, project_dir: str, password: str) -> None:
    """Set a variable KEY=VALUE in the vault."""
    try:
        data = load_vault(project_dir, password)
    except FileNotFoundError:
        data = {}
    data[key] = value
    save_vault(project_dir, password, data)
    click.echo(f"Set {key}")


@cli.command("list")
@click.option("--project-dir", default=".", type=click.Path(file_okay=False))
@click.option("--password", prompt=True, hide_input=True)
def list_vars(project_dir: str, password: str) -> None:
    """List all keys stored in the vault."""
    try:
        data = load_vault(project_dir, password)
    except FileNotFoundError:
        click.echo("No vault found.")
        return
    if not data:
        click.echo("(empty vault)")
        return
    for key in sorted(data):
        click.echo(key)


cli.add_command(rotate_cmd, name="rotate")
cli.add_command(diff_cmd, name="diff")


if __name__ == "__main__":
    cli()
