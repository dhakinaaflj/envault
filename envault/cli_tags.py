"""CLI commands for managing variable tags."""

from __future__ import annotations

import click

from .vault import load_vault, save_vault
from .tags import set_tag, remove_tag, filter_by_tag, all_tags, get_tags


@click.group("tags")
def tags_cmd() -> None:
    """Manage tags for vault variables."""


@tags_cmd.command("add")
@click.argument("var_name")
@click.argument("tag")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def add_tag(var_name: str, tag: str, project: str, password: str) -> None:
    """Add TAG to VAR_NAME."""
    variables = load_vault(project, password)
    if var_name not in variables:
        raise click.ClickException(f"Variable '{var_name}' not found in vault.")
    variables = set_tag(variables, var_name, tag)
    save_vault(project, password, variables)
    click.echo(f"Tagged '{var_name}' with '{tag}'.")


@tags_cmd.command("remove")
@click.argument("var_name")
@click.argument("tag")
@click.option("--project", default=".", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def remove_tag_cmd(var_name: str, tag: str, project: str, password: str) -> None:
    """Remove TAG from VAR_NAME."""
    variables = load_vault(project, password)
    variables = remove_tag(variables, var_name, tag)
    save_vault(project, password, variables)
    click.echo(f"Removed tag '{tag}' from '{var_name}'.")


@tags_cmd.command("list")
@click.option("--project", default=".", show_default=True)
@click.option("--filter", "tag_filter", default=None, help="Show only vars with this tag.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def list_tags(project: str, tag_filter: str | None, password: str) -> None:
    """List variables and their tags."""
    variables = load_vault(project, password)
    if tag_filter:
        subset = filter_by_tag(variables, tag_filter)
        if not subset:
            click.echo(f"No variables tagged '{tag_filter}'.")
            return
        for name in sorted(subset):
            click.echo(name)
        return

    tags_map = get_tags(variables)
    names = [k for k in variables if k != "__tags__"]
    if not names:
        click.echo("Vault is empty.")
        return
    for name in sorted(names):
        tag_list = tags_map.get(name, [])
        tag_str = ", ".join(tag_list) if tag_list else "(none)"
        click.echo(f"{name}: {tag_str}")
