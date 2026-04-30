"""CLI command: envault template — render a template file using vault variables."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .vault import load_vault
from .template import render_template_file, TemplateMissingVariableError


@click.command("template")
@click.argument("template_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Write rendered output to this file (default: print to stdout).",
)
@click.option(
    "--password", "-p",
    prompt=True,
    hide_input=True,
    help="Vault password.",
)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Project directory containing the vault.",
)
@click.option(
    "--strict/--no-strict",
    default=True,
    show_default=True,
    help="Fail on undefined placeholders (--strict) or leave them unchanged (--no-strict).",
)
def template_cmd(
    template_file: Path,
    output: Path | None,
    password: str,
    project_dir: Path,
    strict: bool,
) -> None:
    """Render TEMPLATE_FILE by substituting {{ VAR }} placeholders from the vault."""
    try:
        variables = load_vault(project_dir, password)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading vault: {exc}", err=True)
        sys.exit(1)

    try:
        rendered = render_template_file(template_file, variables, output, strict=strict)
    except TemplateMissingVariableError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output is None:
        click.echo(rendered, nl=False)
    else:
        click.echo(f"Rendered template written to {output}")
