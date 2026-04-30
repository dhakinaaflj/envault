"""Search and filter vault variables by key pattern or value pattern."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault


@dataclass
class SearchResult:
    key: str
    value: str
    matched_on: str  # 'key' | 'value'

    def __str__(self) -> str:
        return f"{self.key}={self.value}  (matched on {self.matched_on})"


@dataclass
class SearchSummary:
    results: List[SearchResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    def keys(self) -> List[str]:
        return [r.key for r in self.results]


def search_vault(
    project_dir: str,
    password: str,
    *,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    use_regex: bool = False,
) -> SearchSummary:
    """Search vault variables by key glob/regex or value glob/regex.

    At least one of key_pattern or value_pattern must be provided.
    """
    if key_pattern is None and value_pattern is None:
        raise ValueError("At least one of key_pattern or value_pattern must be provided.")

    variables: Dict[str, str] = load_vault(project_dir, password)
    summary = SearchSummary()

    for key, value in variables.items():
        matched_on: Optional[str] = None

        if key_pattern is not None:
            if _matches(key, key_pattern, use_regex):
                matched_on = "key"

        if matched_on is None and value_pattern is not None:
            if _matches(value, value_pattern, use_regex):
                matched_on = "value"

        if matched_on is not None:
            summary.results.append(SearchResult(key=key, value=value, matched_on=matched_on))

    return summary


def _matches(text: str, pattern: str, use_regex: bool) -> bool:
    if use_regex:
        return bool(re.search(pattern, text))
    return fnmatch.fnmatch(text, pattern)
