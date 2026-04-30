"""CLI command for rotating the vault password."""

import click
from envault.rotate import rotate_password, RotationError


@click.command("rotate")
@click.argument("project_dir", default=".", type=click.Path(exists=True))
@click.option(
    "--old-password",
    prompt="Current vault password",
    hide_input=True,
    help="Existing password used to decrypt the vault.",
)
@click.option(
    "--new-password",
    prompt="New vault password",
    hide_input=True,
    confirmation_prompt="Confirm new vault password",
    help="New password to re-encrypt the vault under.",
)
def rotate_cmd(project_dir: str, old_password: str, new_password: str) -> None:
    """Rotate the encryption password for a vault.

    All secrets are decrypted with the current password and immediately
    re-encrypted under the new password.  The operation is atomic from the
    perspective of the vault file — either all variables are migrated or
    none are.
    """
    if old_password == new_password:
        raise click.ClickException(
            "New password must differ from the current password."
        )

    try:
        count = rotate_password(
            project_dir,
            old_password=old_password,
            new_password=new_password,
        )
    except RotationError as exc:
        raise click.ClickException(str(exc)) from exc

    click.secho(
        f"\u2714 Password rotated successfully. {count} variable(s) re-encrypted.",
        fg="green",
    )
