from __future__ import annotations

from collections.abc import Iterable
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

VENDORED_DIRS = frozenset(
    {
        "node_modules",
        "vendor",
        "third_party",
        "dist",
        "build",
        ".venv",
        "venv",
        "__pycache__",
        "Pods",
    }
)

LOCKFILES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "uv.lock",
        "Pipfile.lock",
        "Cargo.lock",
        "go.sum",
        "Gemfile.lock",
        "composer.lock",
    }
)

GENERATED_SUFFIXES = (
    ".min.js",
    ".min.css",
    ".map",
    ".pb.go",
    "_pb2.py",
    "_pb2_grpc.py",
    ".snap",
)


def is_excluded(path: str, extra_patterns: Iterable[str] = ()) -> bool:
    """Return True if a file must not count towards authored code."""
    parts = PurePosixPath(path).parts
    name = parts[-1] if parts else path
    if name in LOCKFILES or name.endswith(GENERATED_SUFFIXES):
        return True
    if any(part in VENDORED_DIRS for part in parts[:-1]):
        return True
    return any(fnmatchcase(path, pattern) for pattern in extra_patterns)
