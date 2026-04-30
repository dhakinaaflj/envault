"""Tests for envault.tags module."""

from __future__ import annotations

import json
import pytest

from envault.tags import (
    TAGS_KEY,
    all_tags,
    filter_by_tag,
    get_tags,
    remove_tag,
    set_tag,
)


@pytest.fixture()
def variables() -> dict:
    return {"DB_URL": "postgres://localhost", "SECRET": "s3cr3t", "PORT": "5432"}


# ---------------------------------------------------------------------------
# get_tags
# ---------------------------------------------------------------------------

def test_get_tags_empty_returns_empty_dict(variables):
    assert get_tags(variables) == {}


def test_get_tags_returns_stored_mapping(variables):
    variables[TAGS_KEY] = json.dumps({"DB_URL": ["infra"]})
    assert get_tags(variables) == {"DB_URL": ["infra"]}


def test_get_tags_invalid_json_returns_empty(variables):
    variables[TAGS_KEY] = "not-json"
    assert get_tags(variables) == {}


# ---------------------------------------------------------------------------
# set_tag
# ---------------------------------------------------------------------------

def test_set_tag_adds_tag(variables):
    updated = set_tag(variables, "DB_URL", "infra")
    assert "infra" in get_tags(updated).get("DB_URL", [])


def test_set_tag_does_not_duplicate(variables):
    updated = set_tag(variables, "DB_URL", "infra")
    updated = set_tag(updated, "DB_URL", "infra")
    assert get_tags(updated)["DB_URL"].count("infra") == 1


def test_set_tag_does_not_mutate_original(variables):
    original = dict(variables)
    set_tag(variables, "DB_URL", "infra")
    assert variables == original


# ---------------------------------------------------------------------------
# remove_tag
# ---------------------------------------------------------------------------

def test_remove_tag_removes_existing_tag(variables):
    updated = set_tag(variables, "SECRET", "sensitive")
    updated = remove_tag(updated, "SECRET", "sensitive")
    assert "sensitive" not in get_tags(updated).get("SECRET", [])


def test_remove_tag_noop_when_tag_absent(variables):
    # Should not raise
    updated = remove_tag(variables, "PORT", "nonexistent")
    assert get_tags(updated).get("PORT", []) == []


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_returns_matching_vars(variables):
    updated = set_tag(variables, "DB_URL", "infra")
    updated = set_tag(updated, "PORT", "infra")
    result = filter_by_tag(updated, "infra")
    assert set(result.keys()) == {"DB_URL", "PORT"}


def test_filter_by_tag_excludes_tags_key(variables):
    updated = set_tag(variables, "DB_URL", "infra")
    result = filter_by_tag(updated, "infra")
    assert TAGS_KEY not in result


def test_filter_by_tag_empty_when_no_match(variables):
    assert filter_by_tag(variables, "nonexistent") == {}


# ---------------------------------------------------------------------------
# all_tags
# ---------------------------------------------------------------------------

def test_all_tags_returns_sorted_unique(variables):
    updated = set_tag(variables, "DB_URL", "infra")
    updated = set_tag(updated, "SECRET", "sensitive")
    updated = set_tag(updated, "PORT", "infra")
    assert all_tags(updated) == ["infra", "sensitive"]


def test_all_tags_empty_vault():
    assert all_tags({}) == []
