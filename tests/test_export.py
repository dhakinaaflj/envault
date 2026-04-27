"""Tests for envault.export module."""

import os
import pytest

from envault.export import export_env, import_env
from envault.vault import save_vault


PROJECT = "test_export_project"
PASSWORD = "export-secret-123"


@pytest.fixture(autouse=True)
def cleanup_vault(tmp_path, monkeypatch):
    """Redirect vault storage to a temp directory."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield


def test_export_returns_env_format():
    save_vault(PROJECT, PASSWORD, {"API_KEY": "abc123", "DEBUG": "true"})
    content = export_env(PROJECT, PASSWORD)
    assert "API_KEY=abc123" in content
    assert "DEBUG=true" in content


def test_export_writes_file(tmp_path):
    save_vault(PROJECT, PASSWORD, {"HOST": "localhost", "PORT": "5432"})
    out_file = tmp_path / "output.env"
    export_env(PROJECT, PASSWORD, output_path=str(out_file))
    assert out_file.exists()
    text = out_file.read_text()
    assert "HOST=localhost" in text
    assert "PORT=5432" in text


def test_export_quotes_values_with_spaces():
    save_vault(PROJECT, PASSWORD, {"GREETING": "hello world"})
    content = export_env(PROJECT, PASSWORD)
    assert 'GREETING="hello world"' in content


def test_export_empty_vault():
    save_vault(PROJECT, PASSWORD, {})
    content = export_env(PROJECT, PASSWORD)
    assert content == ""


def test_import_adds_variables(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_URL=postgres://localhost/mydb\nSECRET=hunter2\n")
    result = import_env(PROJECT, PASSWORD, str(env_file))
    assert "DB_URL" in result["added"]
    assert "SECRET" in result["added"]
    assert result["skipped"] == []


def test_import_skips_existing_by_default(tmp_path):
    save_vault(PROJECT, PASSWORD, {"EXISTING_KEY": "original"})
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING_KEY=new_value\nNEW_KEY=hello\n")
    result = import_env(PROJECT, PASSWORD, str(env_file))
    assert "EXISTING_KEY" in result["skipped"]
    assert "NEW_KEY" in result["added"]


def test_import_overwrites_when_flag_set(tmp_path):
    save_vault(PROJECT, PASSWORD, {"KEY": "old"})
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new\n")
    result = import_env(PROJECT, PASSWORD, str(env_file), overwrite=True)
    assert "KEY" in result["added"]
    assert result["skipped"] == []


def test_import_ignores_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# This is a comment\n\nVALID=yes\n")
    result = import_env(PROJECT, PASSWORD, str(env_file))
    assert result["added"] == ["VALID"]


def test_import_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        import_env(PROJECT, PASSWORD, "/nonexistent/path/.env")
