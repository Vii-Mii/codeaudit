from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from codeaudit_core import Commit, FileChange

from app.github import RateLimited, UserNotFound
from app.main import app, get_cache, get_optional_github
from app.stats import TTLCache


class FakeGitHub:
    def __init__(self) -> None:
        self.calls = 0

    async def user_commits(self, login, since, until):
        self.calls += 1
        if login == "ghost":
            raise UserNotFound(login)
        if login == "busy":
            raise RateLimited("limit")
        return [
            Commit(
                sha=sha,
                author_name=login,
                author_email=login,
                authored_at=datetime(2026, 3, day, tzinfo=UTC),
                parent_count=1,
                files=(FileChange(path="", added=added, deleted=1),),
                repo=repo,
                language=lang,
            )
            for sha, day, added, repo, lang in [
                ("a", 1, 10, "octo/app", "Go"),
                ("b", 2, 30, "octo/web", "TypeScript"),
                ("c", 2, 5, "octo/app", "Go"),
            ]
        ]


@pytest.fixture
def fake() -> Iterator[FakeGitHub]:
    fake = FakeGitHub()
    cache = TTLCache(ttl_seconds=60)
    app.dependency_overrides[get_optional_github] = lambda: fake
    app.dependency_overrides[get_cache] = lambda: cache
    yield fake
    app.dependency_overrides.clear()
