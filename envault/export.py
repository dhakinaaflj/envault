"""Export and import utilities for envault vault files."""

import json
import os
from typing import Optional

from envault.vault import load_vault, save_vault


def export_env(project: str, password: str, output_path: Optional[str] = None) -> str:
    """Export decrypted vault contents as a .env file.

    Args:
        project: The project name whose vault to export.
        password: The password to decrypt the vault.
        output_path: Optional path to write the .env file. If None, returns the content.

    Returns:
        The .env file content as a string.
    """
    variables = load_vault(project, password)

    lines = []
    for key, value in sorted(variables.items()):
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")

    content = "\n".join(lines)
    if lines:
        content += "\n"

    if output_path:
        with open(output_path, "w") as f:
            f.write(content)

    return content


def import_env(project: str, password: str, env_path: str, overwrite: bool = False) -> dict:
    """Import variables from a .env file into a vault.

    Args:
        project: The project name to import into.
        password: The password to encrypt the vault.
        env_path: Path to the .env file to import.
        overwrite: If True, overwrite existing keys. If False, skip them.

    Returns:
        A dict with 'added' and 'skipped' lists of key names.
    """
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env file not found: {env_path}")

    parsed = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                parsed[key] = value

    # Try to load existing vault; start fresh if it doesn't exist
    try:
        existing = load_vault(project, password)
    except (FileNotFoundError, Exception):
        existing = {}

    added = []
    skipped = []
    for key, value in parsed.items():
        if key in existing and not overwrite:
            skipped.append(key)
        else:
            existing[key] = value
            added.append(key)

    save_vault(project, password, existing)
    return {"added": added, "skipped": skipped}
