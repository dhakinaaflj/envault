"""Tests for envault.lint module."""

from __future__ import annotations

import pytest
from envault.lint import lint_variables, format_lint_result, LintIssue, LintResult


# ---------------------------------------------------------------------------
# LintResult helpers
# ---------------------------------------------------------------------------

def test_lint_result_empty_has_no_errors():
    r = LintResult()
    assert not r.has_errors
    assert not r.has_warnings


def test_lint_result_add_error():
    r = LintResult()
    r.add("BAD", "error", "something wrong")
    assert r.has_errors
    assert not r.has_warnings


def test_lint_result_add_warning():
    r = LintResult()
    r.add("KEY", "warning", "heads up")
    assert not r.has_errors
    assert r.has_warnings


# ---------------------------------------------------------------------------
# lint_variables
# ---------------------------------------------------------------------------

def test_valid_variables_produce_no_issues():
    result = lint_variables({"DB_HOST": "localhost", "PORT": "5432"})
    assert result.issues == []


def test_lowercase_key_produces_warning():
    result = lint_variables({"db_host": "localhost"})
    assert any(i.severity == "warning" and "db_host" in i.key for i in result.issues)


def test_invalid_key_starting_with_digit_produces_error():
    result = lint_variables({"1BAD": "value"})
    assert any(i.severity == "error" and i.key == "1BAD" for i in result.issues)


def test_empty_value_produces_warning():
    result = lint_variables({"KEY": ""})
    assert any(i.severity == "warning" and "empty" in i.message.lower() for i in result.issues)


def test_empty_value_warning_can_be_disabled():
    result = lint_variables({"KEY": ""}, warn_empty=False)
    assert not any("empty" in i.message.lower() for i in result.issues)


def test_long_value_produces_warning():
    result = lint_variables({"KEY": "x" * 300}, warn_long_value=100)
    assert any("exceeds" in i.message for i in result.issues)


def test_long_value_disabled_when_zero():
    result = lint_variables({"KEY": "x" * 300}, warn_long_value=0)
    assert not any("exceeds" in i.message for i in result.issues)


def test_required_missing_key_produces_error():
    result = lint_variables({"A": "1"}, required_keys=["B"])
    assert any(i.key == "B" and i.severity == "error" for i in result.issues)


def test_required_present_key_no_issue():
    result = lint_variables({"A": "1"}, required_keys=["A"])
    assert not any(i.key == "A" and "missing" in i.message for i in result.issues)


# ---------------------------------------------------------------------------
# format_lint_result
# ---------------------------------------------------------------------------

def test_format_no_issues_returns_ok():
    result = LintResult()
    output = format_lint_result(result)
    assert "No issues" in output


def test_format_includes_severity_label():
    result = LintResult()
    result.add("KEY", "error", "bad key")
    output = format_lint_result(result)
    assert "ERROR" in output
    assert "bad key" in output


def test_format_summary_counts():
    result = LintResult()
    result.add("A", "error", "e1")
    result.add("B", "warning", "w1")
    result.add("C", "warning", "w2")
    output = format_lint_result(result)
    assert "1 error" in output
    assert "2 warning" in output
