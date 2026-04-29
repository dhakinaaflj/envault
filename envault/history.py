"""Vault history: snapshot and list previous versions of vault variables."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

HISTORY_DIR = ".envault_history"


def history_dir_for(project_dir: str | Path) -> Path:
    """Return the history directory for the given project."""
    return Path(project_dir) / HISTORY_DIR


def snapshot_path(project_dir: str | Path, label: str | None = None) -> Path:
    """Return a timestamped snapshot file path inside the history directory."""
    ts = int(time.time())
    name = f"{ts}_{label}.json" if label else f"{ts}.json"
    return history_dir_for(project_dir) / name


def save_snapshot(
    project_dir: str | Path,
    variables: dict[str, str],
    label: str | None = None,
) -> Path:
    """Persist a snapshot of *variables* to the history directory.

    Returns the path of the created snapshot file.
    """
    hist_dir = history_dir_for(project_dir)
    hist_dir.mkdir(parents=True, exist_ok=True)

    path = snapshot_path(project_dir, label)
    payload: dict[str, Any] = {
        "timestamp": int(time.time()),
        "label": label,
        "variables": variables,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def list_snapshots(project_dir: str | Path) -> list[dict[str, Any]]:
    """Return all snapshots sorted oldest-first.

    Each entry contains ``timestamp``, ``label``, ``path`` (str), and
    ``variable_count``.
    """
    hist_dir = history_dir_for(project_dir)
    if not hist_dir.exists():
        return []

    entries: list[dict[str, Any]] = []
    for f in sorted(hist_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        entries.append(
            {
                "timestamp": data.get("timestamp", 0),
                "label": data.get("label"),
                "path": str(f),
                "variable_count": len(data.get("variables", {})),
            }
        )
    return entries


def load_snapshot(snapshot_file: str | Path) -> dict[str, str]:
    """Load and return the variables stored in *snapshot_file*."""
    data = json.loads(Path(snapshot_file).read_text())
    return data.get("variables", {})
