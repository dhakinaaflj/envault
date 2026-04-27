"""Vault file management: read, write, and parse encrypted .env vault files."""

import json
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"


def load_vault(vault_path: Path, password: str) -> Dict[str, str]:
    """Load and decrypt a vault file, returning a dict of env vars."""
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    token = vault_path.read_text(encoding="utf-8").strip()
    if not token:
        raise ValueError("Vault file is empty.")

    plaintext = decrypt(token, password)
    try:
        data = json.loads(plaintext)
    except json.JSONDecodeError as exc:
        raise ValueError("Vault contents are not valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("Vault must contain a JSON object.")

    return data


def save_vault(vault_path: Path, env_vars: Dict[str, str], password: str) -> None:
    """Encrypt and save a dict of env vars to a vault file."""
    plaintext = json.dumps(env_vars, indent=2)
    token = encrypt(plaintext, password)
    vault_path.write_text(token + "\n", encoding="utf-8")


def vault_path_for(project_dir: Path) -> Path:
    """Return the default vault file path for a given project directory."""
    return project_dir / DEFAULT_VAULT_FILE
