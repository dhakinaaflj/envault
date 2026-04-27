"""CLI entry point for envault using Click."""

import sys
from pathlib import Path

import click

from envault.vault import load_vault, save_vault, vault_path_for


@click.group()
def cli():
    """envault — encrypt and manage per-project .env files."""


@cli.command("init")
@click.password_option(prompt="Vault password", help="Password to encrypt the vault.")
def init_vault(password: str):
    """Initialise an empty vault in the current directory."""
    path = vault_path_for(Path.cwd())
    if path.exists():
        click.echo(f"Vault already exists at {path}", err=True)
        sys.exit(1)
    save_vault(path, {}, password)
    click.echo(f"Vault initialised at {path}")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Vault password", help="Password to unlock the vault.")
def set_var(key: str, value: str, password: str):
    """Set an environment variable in the vault."""
    path = vault_path_for(Path.cwd())
    try:
        data = load_vault(path, password)
    except FileNotFoundError:
        click.echo("No vault found. Run `envault init` first.", err=True)
        sys.exit(1)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    data[key] = value
    save_vault(path, data, password)
    click.echo(f"Set {key}")


@cli.command("list")
@click.password_option(prompt="Vault password", confirmation_prompt=False,
                       help="Password to unlock the vault.")
def list_vars(password: str):
    """List all keys stored in the vault."""
    path = vault_path_for(Path.cwd())
    try:
        data = load_vault(path, password)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    if not data:
        click.echo("Vault is empty.")
    else:
        for key in sorted(data):
            click.echo(key)


if __name__ == "__main__":
    cli()
