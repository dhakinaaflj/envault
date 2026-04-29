"""Diff support for comparing vault state across versions or environments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from envault.vault import load_vault


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __str__(self) -> str:
        if self.status == "added":
            return f"+ {self.key}={self.new_value}"
        elif self.status == "removed":
            return f"- {self.key}={self.old_value}"
        elif self.status == "changed":
            return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"
        else:
            return f"  {self.key}={self.new_value}"


def diff_vaults(
    project_dir_a: str,
    password_a: str,
    project_dir_b: str,
    password_b: str,
) -> List[DiffEntry]:
    """Compare two vaults and return a list of DiffEntry objects."""
    vars_a: Dict[str, str] = load_vault(project_dir_a, password_a)
    vars_b: Dict[str, str] = load_vault(project_dir_b, password_b)
    return diff_dicts(vars_a, vars_b)


def diff_dicts(
    old: Dict[str, str],
    new: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Pure diff of two key-value dicts. Returns sorted list of DiffEntry."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(old) | set(new))

    for key in all_keys:
        if key in old and key not in new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(
                DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key])
            )
        elif show_unchanged:
            entries.append(DiffEntry(key=key, status="unchanged", new_value=new[key]))

    return entries


def format_diff(entries: List[DiffEntry], show_unchanged: bool = False) -> str:
    """Render diff entries as a human-readable string."""
    lines = []
    for entry in entries:
        if entry.status == "unchanged" and not show_unchanged:
            continue
        lines.append(str(entry))
    if not lines:
        return "(no differences)"
    return "\n".join(lines)
