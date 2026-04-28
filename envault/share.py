"""Share module for envault.

Handles team-sharing functionality: exporting encrypted vault bundles
that can be shared with teammates, and importing them with a new password.
"""

import json
import base64
import os
from typing import Optional

from envault.crypto import derive_key, encrypt, decrypt
from envault.vault import load_vault, save_vault


# Bundle format version for forward compatibility
BUNDLE_VERSION = 1


def export_bundle(vault_path: str, password: str, output_path: Optional[str] = None) -> str:
    """Export an encrypted vault as a shareable bundle.

    The bundle is a base64-encoded JSON structure containing all vault entries
    re-encrypted under the same password. Recipients can import the bundle
    and re-encrypt it with their own password.

    Args:
        vault_path: Path to the .envault file to export.
        password: The current vault password for decryption.
        output_path: Optional file path to write the bundle to.
                     If None, returns the bundle string without writing.

    Returns:
        The bundle as a base64-encoded string.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If the password is incorrect or the vault is corrupted.
    """
    # Load and decrypt all entries from the vault
    entries = load_vault(vault_path, password)

    # Build the bundle payload
    payload = {
        "version": BUNDLE_VERSION,
        "entries": entries,  # plaintext key/value pairs
    }

    # Serialize and encrypt the entire payload so the bundle itself is encrypted
    payload_json = json.dumps(payload)
    encrypted_payload = encrypt(payload_json, password)

    bundle = {
        "envault_bundle": True,
        "version": BUNDLE_VERSION,
        "data": encrypted_payload,
    }

    bundle_json = json.dumps(bundle)
    bundle_b64 = base64.b64encode(bundle_json.encode("utf-8")).decode("utf-8")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(bundle_b64)
            f.write("\n")

    return bundle_b64


def import_bundle(
    bundle_str: str,
    source_password: str,
    target_vault_path: str,
    target_password: str,
    overwrite: bool = False,
) -> dict:
    """Import a shared bundle into a local vault.

    Decrypts the bundle using the source password (shared by the sender),
    then re-encrypts all entries into the target vault using the target password.

    Args:
        bundle_str: The base64-encoded bundle string.
        source_password: The password used to encrypt the bundle.
        target_vault_path: Path where the local vault file will be written.
        target_password: The password to use for the new local vault.
        overwrite: If False and target vault already exists, raises FileExistsError.

    Returns:
        A dict of the imported key/value pairs.

    Raises:
        FileExistsError: If target vault exists and overwrite is False.
        ValueError: If the bundle is malformed or the source password is wrong.
    """
    if not overwrite and os.path.exists(target_vault_path):
        raise FileExistsError(
            f"Vault already exists at '{target_vault_path}'. "
            "Use overwrite=True to replace it."
        )

    # Decode the bundle
    try:
        bundle_json = base64.b64decode(bundle_str.strip()).decode("utf-8")
        bundle = json.loads(bundle_json)
    except Exception as exc:
        raise ValueError(f"Malformed bundle: could not decode base64/JSON. ({exc})") from exc

    if not bundle.get("envault_bundle"):
        raise ValueError("Not a valid envault bundle.")

    if bundle.get("version") != BUNDLE_VERSION:
        raise ValueError(
            f"Unsupported bundle version: {bundle.get('version')}. "
            f"Expected version {BUNDLE_VERSION}."
        )

    # Decrypt the payload using the source password
    try:
        payload_json = decrypt(bundle["data"], source_password)
        payload = json.loads(payload_json)
    except Exception as exc:
        raise ValueError(
            f"Failed to decrypt bundle. Check the source password. ({exc})"
        ) from exc

    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        raise ValueError("Bundle payload has unexpected format for 'entries'.")

    # Save all entries into the target vault with the target password
    save_vault(target_vault_path, entries, target_password)

    return entries
