"""Rename a variable key within a vault, preserving its value and tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.tags import get_tags, set_tag, remove_tag


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    value_preserved: bool
    tags_migrated: int

    def __str__(self) -> str:
        parts = [f"Renamed '{self.old_key}' -> '{self.new_key}'"]
        if self.tags_migrated:
            parts.append(f"({self.tags_migrated} tag(s) migrated)")
        return " ".join(parts)


def rename_variable(
    project_dir: str,
    password: str,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Rename *old_key* to *new_key* inside the vault for *project_dir*.

    Raises
    ------
    RenameError
        If *old_key* does not exist, *new_key* already exists (and
        *overwrite* is False), or the two names are identical.
    """
    if old_key == new_key:
        raise RenameError(f"Old and new key are identical: '{old_key}'")

    variables = load_vault(project_dir, password)

    if old_key not in variables:
        raise RenameError(f"Key not found in vault: '{old_key}'")

    if new_key in variables and not overwrite:
        raise RenameError(
            f"Key '{new_key}' already exists. Use --overwrite to replace it."
        )

    value = variables.pop(old_key)
    variables[new_key] = value
    save_vault(project_dir, password, variables)

    # Migrate tags: copy tags from old key to new key, then remove old entry.
    existing_tags: dict[str, list[str]] = get_tags(project_dir)
    old_tag_list: list[str] = existing_tags.get(old_key, [])
    for tag in old_tag_list:
        set_tag(project_dir, new_key, tag)
    if old_key in existing_tags:
        remove_tag(project_dir, old_key, None)  # remove entire key entry

    return RenameResult(
        old_key=old_key,
        new_key=new_key,
        value_preserved=True,
        tags_migrated=len(old_tag_list),
    )
