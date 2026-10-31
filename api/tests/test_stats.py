from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import FakeGitHub


def test_user_stats(fake: FakeGitHub) -> None:
    client = TestClient(app)
    url = "/api/v1/users/octo/stats?since=2026-01-01&until=2026-06-30"
    body = client.get(url).json()

    assert body["total"] == {"added": 45, "deleted": 3, "net": 42, "commits": 3}
    assert [r["name"] for r in body["by_repo"]] == ["octo/web", "octo/app"]
    assert body["by_language"][1] == {
        "name": "Go",
        "added": 15,
        "deleted": 2,
        "net": 13,
        "commits": 2,
    }
    assert [d["date"] for d in body["by_day"]] == ["2026-03-01", "2026-03-02"]
    assert body["facets"] == {"repos": ["octo/web", "octo/app"], "languages": ["TypeScript", "Go"]}

    insights = body["insights"]
    assert insights["active_days"] == 2
    assert insights["longest_streak"] == 2
    assert insights["current_streak"] == 0
    assert insights["avg_lines_per_commit"] == 16
    assert insights["busiest_day"]["date"] == "2026-03-02"
    # 2026-03-01 is a Sunday, 2026-03-02 a Monday.
    assert [w["commits"] for w in insights["by_weekday"]] == [2, 0, 0, 0, 0, 0, 1]

    client.get(url)
    assert fake.calls == 1, "second request must be served from cache"


@pytest.mark.parametrize(
    ("query", "added", "commits"),
    [
        ("repo=octo/app", 15, 2),
        ("repo=OCTO/WEB&repo=octo/app", 45, 3),
        ("language=typescript", 30, 1),
        ("max_commit_lines=20", 15, 2),
        ("repo=octo/app&language=TypeScript", 0, 0),
    ],
)
def test_user_stats_filters(fake: FakeGitHub, query: str, added: int, commits: int) -> None:
    body = TestClient(app).get(f"/api/v1/users/octo/stats?{query}").json()

    assert body["total"]["added"] == added
    assert body["total"]["commits"] == commits
    assert len(body["facets"]["repos"]) == 2, "facets ignore filters"


def test_filters_reuse_cached_commits(fake: FakeGitHub) -> None:
    client = TestClient(app)
    client.get("/api/v1/users/octo/stats")
    client.get("/api/v1/users/octo/stats?language=Go")
    assert fake.calls == 1


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/api/v1/users/ghost/stats", 404),
        ("/api/v1/users/busy/stats", 429),
        ("/api/v1/users/bad_login!/stats", 422),
        ("/api/v1/users/octo/stats?since=2026-05-01&until=2026-01-01", 422),
        ("/api/v1/users/octo/stats?since=2024-01-01&until=2026-01-01", 422),
        ("/api/v1/users/octo/stats?max_commit_lines=0", 422),
        ("/api/v1/users/octo/stats?" + "&".join(f"repo=a/{i}" for i in range(51)), 422),
    ],
)
def test_user_stats_errors(fake: FakeGitHub, path: str, status: int) -> None:
    assert TestClient(app).get(path).status_code == status


def test_missing_token_returns_503() -> None:
    with TestClient(app) as client:
        assert client.get("/api/v1/users/octo/stats").status_code == 503
