"""Tests for envault/audit.py"""

import json
import pytest
from pathlib import Path

from envault.audit import (
    audit_log_path,
    record_event,
    read_log,
    format_log,
    AUDIT_FILENAME,
)


@pytest.fixture
def tmp_project(tmp_path):
    return str(tmp_path)


def test_audit_log_path_uses_project_dir(tmp_project):
    path = audit_log_path(tmp_project)
    assert path == Path(tmp_project) / AUDIT_FILENAME


def test_record_event_creates_file(tmp_project):
    record_event("init", project_dir=tmp_project)
    log_path = audit_log_path(tmp_project)
    assert log_path.exists()


def test_record_event_returns_entry(tmp_project):
    entry = record_event("set", key="DB_URL", project_dir=tmp_project)
    assert entry["action"] == "set"
    assert entry["key"] == "DB_URL"
    assert "timestamp" in entry
    assert "user" in entry


def test_record_multiple_events_appends(tmp_project):
    record_event("init", project_dir=tmp_project)
    record_event("set", key="FOO", project_dir=tmp_project)
    record_event("export", project_dir=tmp_project)
    entries = read_log(tmp_project)
    assert len(entries) == 3
    assert entries[0]["action"] == "init"
    assert entries[1]["key"] == "FOO"
    assert entries[2]["action"] == "export"


def test_read_log_empty_when_no_file(tmp_project):
    entries = read_log(tmp_project)
    assert entries == []


def test_read_log_returns_list_on_corrupt_file(tmp_project):
    log_path = audit_log_path(tmp_project)
    log_path.write_text("not valid json", encoding="utf-8")
    entries = read_log(tmp_project)
    assert entries == []


def test_format_log_empty():
    result = format_log([])
    assert "No audit entries" in result


def test_format_log_includes_action_and_user(tmp_project):
    record_event("delete", key="SECRET", user="alice", project_dir=tmp_project)
    entries = read_log(tmp_project)
    output = format_log(entries)
    assert "delete" in output
    assert "alice" in output
    assert "SECRET" in output


def test_record_event_with_extra(tmp_project):
    entry = record_event("import", extra={"source": "bundle.enc"}, project_dir=tmp_project)
    assert entry["source"] == "bundle.enc"
    saved = read_log(tmp_project)
    assert saved[0]["source"] == "bundle.enc"
