import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from codeaudit_core import Commit, FileChange, IdentityResolver, analyze, read_repo
from codeaudit_core.filters import is_excluded


def _commit(repo: Path, name: str, email: str, date: str, message: str) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": name,
        "GIT_AUTHOR_EMAIL": email,
        "GIT_AUTHOR_DATE": date,
        "GIT_COMMITTER_NAME": name,
        "GIT_COMMITTER_EMAIL": email,
        "GIT_COMMITTER_DATE": date,
    }
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True, env=env)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "a.py").write_text("1\n2\n3\n")
    (tmp_path / "package-lock.json").write_text("x\n" * 100)
    _commit(tmp_path, "Alice", "alice@example.com", "2026-01-01T10:00:00+00:00", "alice 1")

    (tmp_path / "a.py").write_text("1\n2\nthree\n")
    (tmp_path / "b.js").write_text("x\ny\n")
    _commit(
        tmp_path, "Bob", "12345+bob@users.noreply.github.com", "2026-01-02T10:00:00+00:00", "bob 1"
    )

    (tmp_path / "c.py").write_text("bump\n" * 7)
    _commit(
        tmp_path,
        "dependabot[bot]",
        "49699333+dependabot[bot]@users.noreply.github.com",
        "2026-01-03T10:00:00+00:00",
        "bot",
    )
    return tmp_path


def test_analyze_counts_authors_languages_and_skips_bots_and_lockfiles(repo: Path) -> None:
    report = analyze(read_repo(repo))

    assert set(report.by_author) == {"alice@example.com", "bob"}
    assert report.by_author["alice@example.com"].added == 3
    assert report.by_author["bob"].added == 3  # 1 changed line + 2 new in b.js
    assert report.by_author["bob"].deleted == 1
    assert report.total.added == 6
    assert report.by_language["Python"].added == 4
    assert report.by_language["JavaScript"].added == 2
    assert "JSON" not in report.by_language


def test_alias_merges_identities(repo: Path) -> None:
    resolver = IdentityResolver({"alice@example.com": "bob"})
    report = analyze(read_repo(repo), resolver)

    assert set(report.by_author) == {"bob"}
    assert report.by_author["bob"].commits == 2


def test_extra_ignore_patterns(repo: Path) -> None:
    report = analyze(read_repo(repo), ignore=["*.js"])
    assert "JavaScript" not in report.by_language


def test_language_hint_and_repo_breakdown() -> None:
    commits = [
        Commit(
            sha=sha,
            author_name="octo",
            author_email="octo",
            authored_at=datetime(2026, 1, 1, tzinfo=UTC),
            parent_count=parents,
            files=(FileChange(path="", added=10, deleted=2),),
            repo="octo/app",
            language="Go",
        )
        for sha, parents in [("a", 1), ("b", 1), ("m", 2)]
    ]
    report = analyze(commits)

    assert report.by_repo["octo/app"].added == 20
    assert report.by_repo["octo/app"].commits == 2
    assert report.by_language["Go"].net == 16


@pytest.mark.parametrize(
    ("path", "excluded"),
    [
        ("src/app.py", False),
        ("node_modules/x/index.js", True),
        ("web/static/app.min.js", True),
        ("yarn.lock", True),
        ("proto/foo_pb2.py", True),
        ("dist", False),
    ],
)
def test_is_excluded(path: str, excluded: bool) -> None:
    assert is_excluded(path) is excluded
