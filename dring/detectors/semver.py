"""Semantic version — major.minor.patch with optional prerelease/build."""

import re

NAME = "semver"
_RE = re.compile(
    r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def detect(s):
    m = _RE.match(s.strip())
    if not m:
        return None
    major, minor, patch, pre, build = m.groups()
    details = {"major": int(major), "minor": int(minor), "patch": int(patch)}
    if pre:
        details["prerelease"] = pre
    if build:
        details["build"] = build
    return {
        "type": NAME,
        "confidence": 0.5,
        "summary": f"semantic version {major}.{minor}.{patch}"
        + (f"-{pre}" if pre else "") + (" (prerelease)" if pre else ""),
        "details": details,
    }
