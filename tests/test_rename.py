"""Tests for envault.rename."""

from __future__ import annotations

import pytest

from envault.vault import save_vault, load_vault
from envault.tags import set_tag, get_tags
from envault.rename import rename_variable, RenameError


PASSWORD = "test-secret"


@pytest.fixture()
def project_dir(tmp_path):
    variables = {"OLD_KEY": "hello", "EXISTING": "world"}
    save_vault(str(tmp_path), PASSWORD, variables)
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Basic rename
# ---------------------------------------------------------------------------

def test_rename_moves_value(project_dir):
    rename_variable(project_dir, PASSWORD, "OLD_KEY", "NEW_KEY")
    variables = load_vault(project_dir, PASSWORD)
    assert "NEW_KEY" in variables
    assert variables["NEW_KEY"] == "hello"
    assert "OLD_KEY" not in variables


def test_rename_result_fields(project_dir):
    result = rename_variable(project_dir, PASSWORD, "OLD_KEY", "NEW_KEY")
    assert result.old_key == "OLD_KEY"
    assert result.new_key == "NEW_KEY"
    assert result.value_preserved is True


def test_rename_result_str(project_dir):
    result = rename_variable(project_dir, PASSWORD, "OLD_KEY", "NEW_KEY")
    assert "OLD_KEY" in str(result)
    assert "NEW_KEY" in str(result)


# ---------------------------------------------------------------------------
# Tag migration
# ---------------------------------------------------------------------------

def test_rename_migrates_tags(project_dir):
    set_tag(project_dir, "OLD_KEY", "production")
    result = rename_variable(project_dir, PASSWORD, "OLD_KEY", "NEW_KEY")
    tags = get_tags(project_dir)
    assert "production" in tags.get("NEW_KEY", [])
    assert result.tags_migrated == 1


def test_rename_no_tags_migrated_when_none(project_dir):
    result = rename_variable(project_dir, PASSWORD, "OLD_KEY", "NEW_KEY")
    assert result.tags_migrated == 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_rename_same_key_raises(project_dir):
    with pytest.raises(RenameError, match="identical"):
        rename_variable(project_dir, PASSWORD, "OLD_KEY", "OLD_KEY")


def test_rename_missing_key_raises(project_dir):
    with pytest.raises(RenameError, match="not found"):
        rename_variable(project_dir, PASSWORD, "GHOST", "NEW_KEY")


def test_rename_existing_new_key_raises_without_overwrite(project_dir):
    with pytest.raises(RenameError, match="already exists"):
        rename_variable(project_dir, PASSWORD, "OLD_KEY", "EXISTING")


def test_rename_existing_new_key_allowed_with_overwrite(project_dir):
    rename_variable(project_dir, PASSWORD, "OLD_KEY", "EXISTING", overwrite=True)
    variables = load_vault(project_dir, PASSWORD)
    assert variables["EXISTING"] == "hello"
    assert "OLD_KEY" not in variables


def test_rename_wrong_password_raises(project_dir):
    from envault.crypto import DecryptionError
    with pytest.raises(Exception):
        rename_variable(project_dir, "wrong-password", "OLD_KEY", "NEW_KEY")
