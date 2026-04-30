"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.search import SearchResult, SearchSummary, _matches, search_vault
from envault.vault import save_vault


PASSWORD = "search-test-secret"


@pytest.fixture()
def project_dir(tmp_path):
    variables = {
        "DATABASE_URL": "postgres://localhost/mydb",
        "REDIS_HOST": "localhost",
        "SECRET_KEY": "supersecret",
        "API_KEY": "abc123",
        "DEBUG": "true",
    }
    save_vault(str(tmp_path), PASSWORD, variables)
    return str(tmp_path)


# --- _matches helper ---

def test_matches_glob_key():
    assert _matches("DATABASE_URL", "DATABASE_*", use_regex=False)


def test_matches_glob_no_match():
    assert not _matches("SECRET_KEY", "DATABASE_*", use_regex=False)


def test_matches_regex_key():
    assert _matches("API_KEY", r"API_.*", use_regex=True)


def test_matches_regex_no_match():
    assert not _matches("DEBUG", r"^API", use_regex=True)


# --- search_vault ---

def test_search_raises_without_patterns(project_dir):
    with pytest.raises(ValueError, match="At least one"):
        search_vault(project_dir, PASSWORD)


def test_search_by_key_glob(project_dir):
    summary = search_vault(project_dir, PASSWORD, key_pattern="*KEY*")
    assert set(summary.keys()) == {"SECRET_KEY", "API_KEY"}
    assert all(r.matched_on == "key" for r in summary.results)


def test_search_by_value_glob(project_dir):
    summary = search_vault(project_dir, PASSWORD, value_pattern="localhost*")
    assert set(summary.keys()) == {"REDIS_HOST"}
    assert summary.results[0].matched_on == "value"


def test_search_by_key_regex(project_dir):
    summary = search_vault(project_dir, PASSWORD, key_pattern=r"^(DEBUG|REDIS_HOST)$", use_regex=True)
    assert set(summary.keys()) == {"DEBUG", "REDIS_HOST"}


def test_search_by_value_regex(project_dir):
    summary = search_vault(project_dir, PASSWORD, value_pattern=r"\d+", use_regex=True)
    # abc123 and postgres://localhost/mydb both contain digits
    assert "API_KEY" in summary.keys()


def test_search_key_takes_priority_over_value(project_dir):
    # DATABASE_URL key matches *DATABASE* and value contains 'localhost'
    summary = search_vault(
        project_dir, PASSWORD, key_pattern="*DATABASE*", value_pattern="*localhost*"
    )
    db_result = next(r for r in summary.results if r.key == "DATABASE_URL")
    assert db_result.matched_on == "key"


def test_search_no_results(project_dir):
    summary = search_vault(project_dir, PASSWORD, key_pattern="NONEXISTENT_*")
    assert summary.total == 0
    assert summary.keys() == []


def test_search_summary_total(project_dir):
    summary = search_vault(project_dir, PASSWORD, key_pattern="*_KEY")
    assert summary.total == len(summary.results)


# --- SearchResult str ---

def test_search_result_str():
    r = SearchResult(key="FOO", value="bar", matched_on="key")
    assert "FOO=bar" in str(r)
    assert "key" in str(r)
