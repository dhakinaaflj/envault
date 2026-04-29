"""Tests for envault.merge — vault merging with conflict resolution."""

import os
import pytest

from envault.vault import save_vault, load_vault
from envault.merge import merge_vaults, MergeConflictError, MergeResult


PASSWORD_A = "password-alpha"
PASSWORD_B = "password-beta"


@pytest.fixture()
def vault_pair(tmp_path):
    base = str(tmp_path / "base.vault")
    source = str(tmp_path / "source.vault")
    save_vault(base, PASSWORD_A, {"KEY1": "value1", "SHARED": "base-value"})
    save_vault(source, PASSWORD_B, {"KEY2": "value2", "SHARED": "source-value"})
    return base, source


def test_merge_adds_new_keys(vault_pair):
    base, source = vault_pair
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="ours")
    assert "KEY2" in result.added
    data = load_vault(base, PASSWORD_A)
    assert data["KEY2"] == "value2"


def test_merge_skips_identical_keys(tmp_path):
    base = str(tmp_path / "base.vault")
    source = str(tmp_path / "source.vault")
    save_vault(base, PASSWORD_A, {"KEY": "same"})
    save_vault(source, PASSWORD_B, {"KEY": "same"})
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="ours")
    assert "KEY" in result.skipped
    assert result.total_changes == 0


def test_merge_strategy_ours_keeps_base_value(vault_pair):
    base, source = vault_pair
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="ours")
    data = load_vault(base, PASSWORD_A)
    assert data["SHARED"] == "base-value"
    assert "SHARED" in result.conflicts


def test_merge_strategy_theirs_overwrites(vault_pair):
    base, source = vault_pair
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="theirs")
    data = load_vault(base, PASSWORD_A)
    assert data["SHARED"] == "source-value"
    assert "SHARED" in result.overwritten


def test_merge_strategy_error_raises_on_conflict(vault_pair):
    base, source = vault_pair
    with pytest.raises(MergeConflictError) as exc_info:
        merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="error")
    assert "SHARED" in exc_info.value.keys


def test_merge_strategy_error_no_conflict_succeeds(tmp_path):
    base = str(tmp_path / "base.vault")
    source = str(tmp_path / "source.vault")
    save_vault(base, PASSWORD_A, {"A": "1"})
    save_vault(source, PASSWORD_B, {"B": "2"})
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="error")
    assert result.added == ["B"]
    assert result.conflicts == []


def test_merge_result_total_changes(vault_pair):
    base, source = vault_pair
    result = merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="theirs")
    # KEY2 added, SHARED overwritten
    assert result.total_changes == 2


def test_merge_base_vault_unchanged_on_conflict_error(vault_pair):
    base, source = vault_pair
    original = load_vault(base, PASSWORD_A)
    try:
        merge_vaults(base, PASSWORD_A, source, PASSWORD_B, strategy="error")
    except MergeConflictError:
        pass
    assert load_vault(base, PASSWORD_A) == original
