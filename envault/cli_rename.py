"""CLI command for renaming a vault variable."""

from __future__ import annotations

import click

from envault.rename import rename_variable, RenameError
from envault.audit import record_event


@click.command("rename")
@click.argument("old_key")
@click.argument("new_key")
@click.option(
    "--project-dir",
    default=".",
    show_default=True,
    help="Path to the project directory containing the vault.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Allow overwriting an existing key with the new name.",
)
@click.password_option(
    "--password",
    prompt="Vault password",
    confirmation_prompt=False,
    help="Password used to decrypt the vault.",
)
def rename_cmd(
    old_key: str,
    new_key: str,
    project_dir: str,
    overwrite: bool,
    password: str,
) -> None:
    """Rename OLD_KEY to NEW_KEY inside the vault.

    Tags associated with OLD_KEY are automatically migrated to NEW_KEY.
    """
    try:
        result = rename_variable(
            project_dir,
            password,
            old_key,
            new_key,
            overwrite=overwrite,
        )
    except RenameError as exc:
        raise click.ClickException(str(exc)) from exc

    record_event(
        project_dir,
        "rename",
        {"old_key": old_key, "new_key": new_key, "overwrite": overwrite},
    )
    click.echo(str(result))
