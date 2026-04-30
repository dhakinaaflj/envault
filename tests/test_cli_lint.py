"""Integration tests for the lint CLI command."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.vault import save_vault
from envault.cli_lint import lint_cmd


PASSWORD = "test-lint-pass"


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _make_vault(project_dir, variables, password=PASSWORD):
    save_vault(project_dir, variables, password)


def test_lint_clean_vault_shows_no_issues(project_dir):
    _make_vault(project_dir, {"DB_HOST": "localhost", "PORT": "5432"})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_lint_empty_value_shows_warning(project_dir):
    _make_vault(project_dir, {"KEY": ""})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "warning" in result.output.lower()


def test_lint_invalid_key_shows_error(project_dir):
    _make_vault(project_dir, {"1BAD": "val"})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", PASSWORD])
    assert "ERROR" in result.output


def test_lint_strict_exits_nonzero_on_error(project_dir):
    _make_vault(project_dir, {"1BAD": "val"})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", PASSWORD, "--strict"])
    assert result.exit_code == 1


def test_lint_strict_exits_zero_when_clean(project_dir):
    _make_vault(project_dir, {"DB_HOST": "localhost"})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", PASSWORD, "--strict"])
    assert result.exit_code == 0


def test_lint_require_missing_key_shows_error(project_dir):
    _make_vault(project_dir, {"DB_HOST": "localhost"})
    runner = CliRunner()
    result = runner.invoke(
        lint_cmd,
        ["-p", project_dir, "--password", PASSWORD, "--require", "SECRET_KEY"],
    )
    assert "SECRET_KEY" in result.output
    assert "ERROR" in result.output


def test_lint_wrong_password_exits_with_error(project_dir):
    _make_vault(project_dir, {"A": "1"})
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["-p", project_dir, "--password", "wrongpass"])
    assert result.exit_code == 1
