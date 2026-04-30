"""Tests for envault.template and envault.cli_template."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.template import (
    render_template,
    render_template_file,
    TemplateMissingVariableError,
)
from envault.cli_template import template_cmd
from envault.vault import save_vault


# ---------------------------------------------------------------------------
# Unit tests for render_template
# ---------------------------------------------------------------------------

def test_render_simple_substitution():
    result = render_template("Hello, {{ NAME }}!", {"NAME": "World"})
    assert result == "Hello, World!"


def test_render_multiple_placeholders():
    tmpl = "{{ HOST }}:{{ PORT }}/{{ DB }}"
    result = render_template(tmpl, {"HOST": "localhost", "PORT": "5432", "DB": "mydb"})
    assert result == "localhost:5432/mydb"


def test_render_whitespace_in_placeholder():
    result = render_template("{{  KEY  }}", {"KEY": "value"})
    assert result == "value"


def test_render_missing_key_strict_raises():
    with pytest.raises(TemplateMissingVariableError) as exc_info:
        render_template("{{ MISSING }}", {}, strict=True)
    assert exc_info.value.key == "MISSING"


def test_render_missing_key_non_strict_leaves_placeholder():
    result = render_template("{{ MISSING }}", {}, strict=False)
    assert result == "{{ MISSING }}"


def test_render_no_placeholders_unchanged():
    text = "no placeholders here"
    assert render_template(text, {"X": "y"}) == text


# ---------------------------------------------------------------------------
# Unit tests for render_template_file
# ---------------------------------------------------------------------------

def test_render_template_file_returns_string(tmp_path: Path):
    tpl = tmp_path / "app.conf.tpl"
    tpl.write_text("db={{ DB_URL }}")
    result = render_template_file(tpl, {"DB_URL": "sqlite:///db.sqlite3"})
    assert result == "db=sqlite:///db.sqlite3"


def test_render_template_file_writes_output(tmp_path: Path):
    tpl = tmp_path / "tpl.txt"
    tpl.write_text("key={{ KEY }}")
    out = tmp_path / "out.txt"
    render_template_file(tpl, {"KEY": "secret"}, out)
    assert out.read_text() == "key=secret"


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_dir(tmp_path: Path):
    save_vault(tmp_path, "pass123", {"API_KEY": "abc", "HOST": "localhost"})
    return tmp_path


def test_cli_template_stdout(vault_dir: Path, tmp_path: Path):
    tpl = tmp_path / "cfg.tpl"
    tpl.write_text("host={{ HOST }} key={{ API_KEY }}")
    runner = CliRunner()
    result = runner.invoke(
        template_cmd,
        [str(tpl), "--password", "pass123", "--project-dir", str(vault_dir)],
    )
    assert result.exit_code == 0
    assert "localhost" in result.output
    assert "abc" in result.output


def test_cli_template_writes_file(vault_dir: Path, tmp_path: Path):
    tpl = tmp_path / "cfg.tpl"
    tpl.write_text("{{ HOST }}")
    out = tmp_path / "cfg.txt"
    runner = CliRunner()
    result = runner.invoke(
        template_cmd,
        [str(tpl), "--output", str(out), "--password", "pass123", "--project-dir", str(vault_dir)],
    )
    assert result.exit_code == 0
    assert out.read_text() == "localhost"


def test_cli_template_missing_var_exits_nonzero(vault_dir: Path, tmp_path: Path):
    tpl = tmp_path / "bad.tpl"
    tpl.write_text("{{ UNDEFINED_VAR }}")
    runner = CliRunner()
    result = runner.invoke(
        template_cmd,
        [str(tpl), "--password", "pass123", "--project-dir", str(vault_dir)],
    )
    assert result.exit_code != 0
    assert "UNDEFINED_VAR" in result.output
