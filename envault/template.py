"""Template rendering: substitute vault variables into template files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


class TemplateMissingVariableError(Exception):
    """Raised when a required variable is not found in the vault."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Template references undefined variable: {key!r}")


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(
    template_text: str,
    variables: Dict[str, str],
    *,
    strict: bool = True,
) -> str:
    """Replace ``{{ VAR }}`` placeholders with values from *variables*.

    Parameters
    ----------
    template_text:
        Raw template string containing ``{{ KEY }}`` placeholders.
    variables:
        Mapping of variable names to their plaintext values.
    strict:
        When *True* (default) raise :exc:`TemplateMissingVariableError` for
        any placeholder whose key is absent from *variables*.  When *False*
        leave unresolved placeholders unchanged.
    """

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in variables:
            return variables[key]
        if strict:
            raise TemplateMissingVariableError(key)
        return match.group(0)  # leave placeholder as-is

    return _PLACEHOLDER_RE.sub(_replace, template_text)


def render_template_file(
    template_path: Path,
    variables: Dict[str, str],
    output_path: Optional[Path] = None,
    *,
    strict: bool = True,
) -> str:
    """Read *template_path*, render it, optionally write to *output_path*.

    Returns the rendered string in all cases.
    """
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, variables, strict=strict)
    if output_path is not None:
        output_path.write_text(rendered, encoding="utf-8")
    return rendered
