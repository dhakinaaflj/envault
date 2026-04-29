"""Audit log for tracking vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = ".envault_audit.json"


def audit_log_path(project_dir: Optional[str] = None) -> Path:
    """Return the path to the audit log for the given project directory."""
    base = Path(project_dir) if project_dir else Path.cwd()
    return base / AUDIT_FILENAME


def _load_log(log_path: Path) -> list:
    """Load existing audit entries from disk."""
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def record_event(
    action: str,
    key: Optional[str] = None,
    user: Optional[str] = None,
    project_dir: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    """Append an audit event and return the entry."""
    log_path = audit_log_path(project_dir)
    entries = _load_log(log_path)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user": user or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    }
    if key is not None:
        entry["key"] = key
    if extra:
        entry.update(extra)

    entries.append(entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)

    return entry


def read_log(project_dir: Optional[str] = None) -> list:
    """Return all audit entries for the project."""
    return _load_log(audit_log_path(project_dir))


def format_log(entries: list) -> str:
    """Format audit entries as a human-readable string."""
    if not entries:
        return "No audit entries found."
    lines = []
    for e in entries:
        key_part = f"  key={e['key']}" if "key" in e else ""
        lines.append(f"[{e['timestamp']}] {e['action']} by {e['user']}{key_part}")
    return "\n".join(lines)
