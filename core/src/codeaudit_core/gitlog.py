from __future__ import annotations

import subprocess
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from codeaudit_core.models import Commit, FileChange

_RECORD_SEP = "\x1e"
_FIELD_SEP = "\x1f"
_PRETTY = (
    f"--pretty=format:{_RECORD_SEP}%H{_FIELD_SEP}%an{_FIELD_SEP}%ae{_FIELD_SEP}%aI{_FIELD_SEP}%P"
)


def parse_git_log(text: str) -> Iterator[Commit]:
    """Parse output of `git log --numstat` produced with this module's format."""
    for record in text.split(_RECORD_SEP):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        sha, name, email, date, parents = header.split(_FIELD_SEP)
        files = []
        for line in body.splitlines():
            if not line.strip():
                continue
            added, deleted, path = line.split("\t", 2)
            if added == "-" or deleted == "-":  # binary file
                continue
            files.append(FileChange(path=path, added=int(added), deleted=int(deleted)))
        yield Commit(
            sha=sha,
            author_name=name,
            author_email=email,
            authored_at=datetime.fromisoformat(date),
            parent_count=len(parents.split()),
            files=tuple(files),
        )


def read_repo(
    repo_path: str | Path, since: str | None = None, until: str | None = None
) -> list[Commit]:
    """Read commit history from a local clone."""
    path = Path(repo_path)
    if not (path / ".git").exists() and not (path / "HEAD").exists():
        raise ValueError(f"not a git repository: {path}")
    cmd = ["git", "-C", str(path), "log", "--numstat", "--no-renames", _PRETTY]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)  # noqa: S603
    return list(parse_git_log(result.stdout))
