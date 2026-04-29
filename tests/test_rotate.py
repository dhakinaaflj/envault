"""Tests for envault.rotate and the rotate CLI command."""

import pytest
from click.testing import CliRunner

from envault.vault import save_vault, load_vault
from envault.rotate import rotate_password, RotationError
from envault.cli_rotate import rotate_cmd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_dir(tmp_path):
    """A temp directory with a pre-populated vault."""
    secrets = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/dev"}
    save_vault(str(tmp_path), secrets, "old-pass")
    return tmp_path


# ---------------------------------------------------------------------------
# Unit tests for rotate_password()
# ---------------------------------------------------------------------------

def test_rotate_returns_variable_count(vault_dir):
    count = rotate_password(str(vault_dir), "old-pass", "new-pass")
    assert count == 2


def test_rotate_new_password_decrypts_correctly(vault_dir):
    rotate_password(str(vault_dir), "old-pass", "new-pass")
    secrets = load_vault(str(vault_dir), "new-pass")
    assert secrets["API_KEY"] == "abc123"
    assert secrets["DB_URL"] == "postgres://localhost/dev"


def test_rotate_old_password_no_longer_works(vault_dir):
    rotate_password(str(vault_dir), "old-pass", "new-pass")
    with pytest.raises((ValueError, Exception)):
        load_vault(str(vault_dir), "old-pass")


def test_rotate_wrong_old_password_raises(vault_dir):
    with pytest.raises(RotationError, match="Could not open vault"):
        rotate_password(str(vault_dir), "wrong-pass", "new-pass")


def test_rotate_same_password_raises(vault_dir):
    with pytest.raises(RotationError, match="different"):
        rotate_password(str(vault_dir), "old-pass", "old-pass")


def test_rotate_mismatched_confirm_raises(vault_dir):
    with pytest.raises(RotationError, match="confirmation"):
        rotate_password(
            str(vault_dir), "old-pass", "new-pass", confirm_password="typo"
        )


def test_rotate_missing_vault_raises(tmp_path):
    with pytest.raises(RotationError):
        rotate_password(str(tmp_path), "old-pass", "new-pass")


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

def test_cli_rotate_success(vault_dir):
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        [str(vault_dir), "--old-password", "old-pass", "--new-password", "new-pass"],
    )
    assert result.exit_code == 0
    assert "re-encrypted" in result.output


def test_cli_rotate_bad_password_exits_nonzero(vault_dir):
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        [str(vault_dir), "--old-password", "bad", "--new-password", "new-pass"],
    )
    assert result.exit_code != 0
