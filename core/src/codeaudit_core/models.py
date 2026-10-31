from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FileChange:
    path: str
    added: int
    deleted: int


@dataclass(frozen=True)
class Commit:
    sha: str
    author_name: str
    author_email: str
    authored_at: datetime
    parent_count: int
    files: tuple[FileChange, ...]
    repo: str = ""
    # Set when per-file paths are unavailable (API mode); overrides extension detection.
    language: str | None = None

    @property
    def is_merge(self) -> bool:
        return self.parent_count > 1
