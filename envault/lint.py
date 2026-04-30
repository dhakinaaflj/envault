"""Lint/validate vault variables against a set of rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class LintIssue:
    key: str
    severity: str  # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        icon = "✖" if self.severity == "error" else "⚠"
        return f"  {icon} [{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def add(self, key: str, severity: str, message: str) -> None:
        self.issues.append(LintIssue(key=key, severity=severity, message=message))


_VALID_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_EMPTY_VALUE_KEYS_WARN = True


def lint_variables(
    variables: dict[str, str],
    *,
    warn_empty: bool = True,
    warn_lowercase_key: bool = True,
    error_invalid_key: bool = True,
    warn_long_value: int = 0,
    required_keys: Optional[List[str]] = None,
) -> LintResult:
    """Run lint checks on a dict of env variables."""
    result = LintResult()

    for key, value in variables.items():
        if error_invalid_key and not _VALID_KEY_RE.match(key):
            result.add(key, "error", "Key must be uppercase letters, digits, and underscores, starting with a letter.")
        elif warn_lowercase_key and key != key.upper():
            result.add(key, "warning", "Key contains lowercase letters.")

        if warn_empty and value.strip() == "":
            result.add(key, "warning", "Value is empty.")

        if warn_long_value and len(value) > warn_long_value:
            result.add(key, "warning", f"Value exceeds {warn_long_value} characters ({len(value)}).")

    if required_keys:
        for rk in required_keys:
            if rk not in variables:
                result.add(rk, "error", "Required key is missing from vault.")

    return result


def format_lint_result(result: LintResult) -> str:
    """Return a human-readable summary of lint results."""
    if not result.issues:
        return "✔ No issues found."
    lines = []
    for issue in result.issues:
        lines.append(str(issue))
    summary_parts = []
    errors = sum(1 for i in result.issues if i.severity == "error")
    warnings = sum(1 for i in result.issues if i.severity == "warning")
    if errors:
        summary_parts.append(f"{errors} error(s)")
    if warnings:
        summary_parts.append(f"{warnings} warning(s)")
    lines.append("\n" + ", ".join(summary_parts) + " found.")
    return "\n".join(lines)
