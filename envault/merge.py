"""Merge two vaults, combining or overwriting variables with conflict resolution."""

from dataclasses import dataclass, field
from typing import Dict, List, Literal

from envault.vault import load_vault, save_vault

ConflictStrategy = Literal["ours", "theirs", "error"]


@dataclass
class MergeResult:
    added: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.overwritten)


class MergeConflictError(Exception):
    """Raised when a conflict is encountered and strategy is 'error'."""

    def __init__(self, keys: List[str]):
        self.keys = keys
        super().__init__(
            f"Merge conflict on keys: {', '.join(keys)}. "
            "Use --strategy ours|theirs to resolve."
        )


def merge_vaults(
    base_path: str,
    base_password: str,
    source_path: str,
    source_password: str,
    strategy: ConflictStrategy = "error",
) -> MergeResult:
    """Merge variables from source vault into base vault.

    Args:
        base_path: Path to the vault that will receive merged values.
        base_password: Password for the base vault.
        source_path: Path to the vault supplying new values.
        source_password: Password for the source vault.
        strategy: How to handle key conflicts — 'ours', 'theirs', or 'error'.

    Returns:
        MergeResult summarising what changed.

    Raises:
        MergeConflictError: If strategy is 'error' and conflicts exist.
    """
    base_data: Dict[str, str] = load_vault(base_path, base_password)
    source_data: Dict[str, str] = load_vault(source_path, source_password)

    result = MergeResult()
    merged = dict(base_data)

    conflict_keys = [
        k for k in source_data if k in base_data and base_data[k] != source_data[k]
    ]

    if conflict_keys and strategy == "error":
        raise MergeConflictError(conflict_keys)

    for key, value in source_data.items():
        if key not in base_data:
            merged[key] = value
            result.added.append(key)
        elif base_data[key] == value:
            result.skipped.append(key)
        else:
            result.conflicts.append(key)
            if strategy == "theirs":
                merged[key] = value
                result.overwritten.append(key)
            else:  # strategy == "ours"
                result.skipped.append(key)

    save_vault(base_path, base_password, merged)
    return result
