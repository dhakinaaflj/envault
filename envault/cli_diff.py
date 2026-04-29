"""CLI command for diffing two vaults."""

import click

from envault.diff import diff_vaults, format_diff


@click.command("diff")
@click.argument("project_a", type=click.Path(exists=True, file_okay=False))
@click.argument("project_b", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--password-a",
    prompt="Password for project A",
    hide_input=True,
    help="Decryption password for vault A.",
)
@click.option(
    "--password-b",
    prompt="Password for project B",
    hide_input=True,
    help="Decryption password for vault B.",
)
@click.option(
    "--show-unchanged",
    is_flag=True,
    default=False,
    help="Also display keys that are identical in both vaults.",
)
def diff_cmd(
    project_a: str,
    project_b: str,
    password_a: str,
    password_b: str,
    show_unchanged: bool,
) -> None:
    """Show differences between two encrypted vaults."""
    try:
        entries = diff_vaults(project_a, password_a, project_b, password_b)
        output = format_diff(entries, show_unchanged=show_unchanged)
        click.echo(output)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
