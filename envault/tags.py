"""Tag support for envault variables — group and filter vars by tag."""

from __future__ import annotations

from typing import Dict, List, Set

TAGS_KEY = "__tags__"


def get_tags(variables: Dict[str, str]) -> Dict[str, List[str]]:
    """Return the tags mapping stored inside a variables dict.

    The tags are stored under the reserved key ``__tags__`` as a
    JSON-serialisable dict of ``{var_name: [tag, ...]}``.  If no tags
    have been set the function returns an empty dict.
    """
    import json

    raw = variables.get(TAGS_KEY, "{}")
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def set_tag(variables: Dict[str, str], var_name: str, tag: str) -> Dict[str, str]:
    """Add *tag* to *var_name* in *variables* and return the updated dict."""
    import json

    tags = get_tags(variables)
    existing: Set[str] = set(tags.get(var_name, []))
    existing.add(tag)
    tags[var_name] = sorted(existing)
    variables = dict(variables)
    variables[TAGS_KEY] = json.dumps(tags)
    return variables


def remove_tag(variables: Dict[str, str], var_name: str, tag: str) -> Dict[str, str]:
    """Remove *tag* from *var_name*.  No-op if the tag is not present."""
    import json

    tags = get_tags(variables)
    existing: Set[str] = set(tags.get(var_name, []))
    existing.discard(tag)
    tags[var_name] = sorted(existing)
    variables = dict(variables)
    variables[TAGS_KEY] = json.dumps(tags)
    return variables


def filter_by_tag(variables: Dict[str, str], tag: str) -> Dict[str, str]:
    """Return a subset of *variables* whose keys carry *tag*.

    The ``__tags__`` bookkeeping key is never included in the result.
    """
    tags = get_tags(variables)
    return {
        k: v
        for k, v in variables.items()
        if k != TAGS_KEY and tag in tags.get(k, [])
    }


def all_tags(variables: Dict[str, str]) -> List[str]:
    """Return a sorted list of every unique tag used across all variables."""
    tags = get_tags(variables)
    unique: Set[str] = set()
    for tag_list in tags.values():
        unique.update(tag_list)
    return sorted(unique)
