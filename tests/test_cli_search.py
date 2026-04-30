"""Tests for the search CLI command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_search import search_cmd
from envault.vault import save_vault


PASSWORD = "cli-search-pass"


@pytest.fixture()
def project_dir(tmp_path):
    variables = {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "topsecret",
        "DEBUG": "false",
    }
    save_vault(str(tmp_path), PASSWORD, variables)
    return str(tmp_path)


def _run(project_dir, *args):
    runner = CliRunner()
    return runner.invoke(
        search_cmd,
        ["--project-dir", project_dir, "--password", PASSWORD, *args],
        catch_exceptions=False,
    )


def test_search_cmd_finds_by_key(project_dir):
    result = _run(project_dir, "--key", "*KEY*")
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.output


def test_search_cmd_finds_by_value(project_dir):
    result = _run(project_dir, "--value", "*localhost*")
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_search_cmd_no_results_message(project_dir):
    result = _run(project_dir, "--key", "NONEXISTENT_*")
    assert result.exit_code == 0
    assert "No matching" in result.output


def test_search_cmd_requires_pattern(project_dir):
    runner = CliRunner()
    result = runner.invoke(
        search_cmd,
        ["--project-dir", project_dir, "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "at least" in result.output.lower() or "at least" in str(result.exception).lower()


def test_search_cmd_regex_flag(project_dir):
    result = _run(project_dir, "--key", r"^DEBUG$", "--regex")
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_search_cmd_shows_match_source(project_dir):
    result = _run(project_dir, "--key", "SECRET_KEY")
    assert result.exit_code == 0
    assert "[key]" in result.output
