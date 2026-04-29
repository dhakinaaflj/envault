"""CLI-level tests for the diff command."""

import pytest
from click.testing import CliRunner

from envault.cli_diff import diff_cmd
from envault.vault import save_vault


PASSWORD = "cli-diff-pw"


@pytest.fixture()
def two_vaults(tmp_path):
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    save_vault(str(dir_a), PASSWORD, {"DB_URL": "postgres://old", "SHARED": "same"})
    save_vault(str(dir_b), PASSWORD, {"DB_URL": "postgres://new", "SHARED": "same", "NEW_KEY": "hi"})
    return str(dir_a), str(dir_b)


def test_diff_cmd_shows_changed(two_vaults):
    dir_a, dir_b = two_vaults
    runner = CliRunner()
    result = runner.invoke(
        diff_cmd,
        [dir_a, dir_b, "--password-a", PASSWORD, "--password-b", PASSWORD],
    )
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "~" in result.output


def test_diff_cmd_shows_added(two_vaults):
    dir_a, dir_b = two_vaults
    runner = CliRunner()
    result = runner.invoke(
        diff_cmd,
        [dir_a, dir_b, "--password-a", PASSWORD, "--password-b", PASSWORD],
    )
    assert "NEW_KEY" in result.output
    assert "+" in result.output


def test_diff_cmd_hides_unchanged_by_default(two_vaults):
    dir_a, dir_b = two_vaults
    runner = CliRunner()
    result = runner.invoke(
        diff_cmd,
        [dir_a, dir_b, "--password-a", PASSWORD, "--password-b", PASSWORD],
    )
    assert "SHARED" not in result.output


def test_diff_cmd_show_unchanged_flag(two_vaults):
    dir_a, dir_b = two_vaults
    runner = CliRunner()
    result = runner.invoke(
        diff_cmd,
        [
            dir_a, dir_b,
            "--password-a", PASSWORD,
            "--password-b", PASSWORD,
            "--show-unchanged",
        ],
    )
    assert "SHARED" in result.output


def test_diff_cmd_wrong_password_fails(two_vaults):
    dir_a, dir_b = two_vaults
    runner = CliRunner()
    result = runner.invoke(
        diff_cmd,
        [dir_a, dir_b, "--password-a", "wrong", "--password-b", PASSWORD],
    )
    assert result.exit_code != 0
