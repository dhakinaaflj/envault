"""Tests for envault.history — snapshot and listing functionality."""

import json
import time
from pathlib import Path

import pytest

from envault.history import (
    history_dir_for,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "myproject"


def test_history_dir_uses_project_dir(project_dir: Path) -> None:
    hist = history_dir_for(project_dir)
    assert hist == project_dir / ".envault_history"


def test_save_snapshot_creates_file(project_dir: Path) -> None:
    path = save_snapshot(project_dir, {"KEY": "value"})
    assert path.exists()
    assert path.suffix == ".json"


def test_save_snapshot_stores_variables(project_dir: Path) -> None:
    variables = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    path = save_snapshot(project_dir, variables)
    data = json.loads(path.read_text())
    assert data["variables"] == variables


def test_save_snapshot_stores_label(project_dir: Path) -> None:
    path = save_snapshot(project_dir, {"X": "1"}, label="before-deploy")
    assert "before-deploy" in path.name
    data = json.loads(path.read_text())
    assert data["label"] == "before-deploy"


def test_save_snapshot_timestamp_is_recent(project_dir: Path) -> None:
    before = int(time.time())
    path = save_snapshot(project_dir, {"A": "b"})
    after = int(time.time())
    data = json.loads(path.read_text())
    assert before <= data["timestamp"] <= after


def test_list_snapshots_empty_when_no_history(project_dir: Path) -> None:
    assert list_snapshots(project_dir) == []


def test_list_snapshots_returns_all_entries(project_dir: Path) -> None:
    save_snapshot(project_dir, {"A": "1"})
    save_snapshot(project_dir, {"A": "2", "B": "3"})
    snapshots = list_snapshots(project_dir)
    assert len(snapshots) == 2


def test_list_snapshots_sorted_oldest_first(project_dir: Path) -> None:
    p1 = save_snapshot(project_dir, {"A": "1"})
    time.sleep(0.01)
    p2 = save_snapshot(project_dir, {"A": "2"})
    snapshots = list_snapshots(project_dir)
    assert snapshots[0]["path"] == str(p1)
    assert snapshots[1]["path"] == str(p2)


def test_list_snapshots_includes_variable_count(project_dir: Path) -> None:
    save_snapshot(project_dir, {"X": "1", "Y": "2", "Z": "3"})
    snapshots = list_snapshots(project_dir)
    assert snapshots[0]["variable_count"] == 3


def test_load_snapshot_returns_variables(project_dir: Path) -> None:
    variables = {"SECRET": "abc123", "PORT": "8080"}
    path = save_snapshot(project_dir, variables)
    loaded = load_snapshot(path)
    assert loaded == variables
