"""Unit tests for envault.vault module."""

import pytest
from pathlib import Path
from envault.vault import load_vault, save_vault, vault_path_for


PASSWORD = "vault-test-pass"
ENV_VARS = {"DB_HOST": "localhost", "API_KEY": "secret123"}


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / ".envault"
    save_vault(path, ENV_VARS, PASSWORD)
    loaded = load_vault(path, PASSWORD)
    assert loaded == ENV_VARS


def test_save_creates_file(tmp_path):
    path = tmp_path / ".envault"
    save_vault(path, {}, PASSWORD)
    assert path.exists()
    assert path.stat().st_size > 0


def test_load_missing_file_raises(tmp_path):
    path = tmp_path / ".envault"
    with pytest.raises(FileNotFoundError):
        load_vault(path, PASSWORD)


def test_load_wrong_password_raises(tmp_path):
    path = tmp_path / ".envault"
    save_vault(path, ENV_VARS, PASSWORD)
    with pytest.raises(ValueError):
        load_vault(path, "wrong-password")


def test_load_empty_file_raises(tmp_path):
    path = tmp_path / ".envault"
    path.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_vault(path, PASSWORD)


def test_vault_path_for_returns_correct_path(tmp_path):
    expected = tmp_path / ".envault"
    assert vault_path_for(tmp_path) == expected


def test_overwrite_existing_vault(tmp_path):
    path = tmp_path / ".envault"
    save_vault(path, ENV_VARS, PASSWORD)
    updated = {"NEW_KEY": "new_value"}
    save_vault(path, updated, PASSWORD)
    loaded = load_vault(path, PASSWORD)
    assert loaded == updated


def test_save_and_load_empty_dict(tmp_path):
    """Verify that an empty dict can be saved and loaded without data loss."""
    path = tmp_path / ".envault"
    save_vault(path, {}, PASSWORD)
    loaded = load_vault(path, PASSWORD)
    assert loaded == {}


def test_load_corrupted_file_raises(tmp_path):
    """Verify that a corrupted (non-empty, invalid) vault file raises ValueError."""
    path = tmp_path / ".envault"
    path.write_bytes(b"this is not valid encrypted data")
    with pytest.raises(ValueError):
        load_vault(path, PASSWORD)
