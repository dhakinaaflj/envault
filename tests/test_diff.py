"""Tests for envault.diff module."""

import os
import pytest

from envault.diff import (
    DiffEntry,
    diff_dicts,
    diff_vaults,
    format_diff,
)
from envault.vault import save_vault


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASSWORD = "test-secret-42"


@pytest.fixture()
def vault_pair(tmp_path):
    dir_a = tmp_path / "proj_a"
    dir_b = tmp_path / "proj_b"
    dir_a.mkdir()
    dir_b.mkdir()
    return str(dir_a), str(dir_b)


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_added_key():
    entries = diff_dicts({}, {"NEW": "value"})
    assert len(entries) == 1
    assert entries[0].status == "added"
    assert entries[0].key == "NEW"
    assert entries[0].new_value == "value"


def test_removed_key():
    entries = diff_dicts({"OLD": "val"}, {})
    assert len(entries) == 1
    assert entries[0].status == "removed"
    assert entries[0].old_value == "val"


def test_changed_key():
    entries = diff_dicts({"K": "old"}, {"K": "new"})
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].old_value == "old"
    assert entries[0].new_value == "new"


def test_unchanged_key_excluded_by_default():
    entries = diff_dicts({"K": "same"}, {"K": "same"})
    assert entries == []


def test_unchanged_key_included_when_requested():
    entries = diff_dicts({"K": "same"}, {"K": "same"}, show_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_keys_sorted():
    entries = diff_dicts({}, {"Z": "1", "A": "2", "M": "3"})
    keys = [e.key for e in entries]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# format_diff
# ---------------------------------------------------------------------------

def test_format_diff_no_diff():
    result = format_diff([])
    assert result == "(no differences)"


def test_format_diff_shows_added():
    entries = [DiffEntry(key="FOO", status="added", new_value="bar")]
    assert format_diff(entries).startswith("+")


def test_format_diff_shows_removed():
    entries = [DiffEntry(key="FOO", status="removed", old_value="bar")]
    assert format_diff(entries).startswith("-")


def test_format_diff_shows_changed():
    entries = [DiffEntry(key="FOO", status="changed", old_value="a", new_value="b")]
    assert format_diff(entries).startswith("~")


# ---------------------------------------------------------------------------
# diff_vaults (integration)
# ---------------------------------------------------------------------------

def test_diff_vaults_detects_added(vault_pair):
    dir_a, dir_b = vault_pair
    save_vault(dir_a, PASSWORD, {"SHARED": "same"})
    save_vault(dir_b, PASSWORD, {"SHARED": "same", "EXTRA": "new"})
    entries = diff_vaults(dir_a, PASSWORD, dir_b, PASSWORD)
    statuses = {e.key: e.status for e in entries}
    assert statuses["EXTRA"] == "added"
    assert "SHARED" not in statuses


def test_diff_vaults_detects_changed(vault_pair):
    dir_a, dir_b = vault_pair
    save_vault(dir_a, PASSWORD, {"KEY": "old"})
    save_vault(dir_b, PASSWORD, {"KEY": "new"})
    entries = diff_vaults(dir_a, PASSWORD, dir_b, PASSWORD)
    assert entries[0].status == "changed"
