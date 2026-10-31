from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

import httpx
import pytest

from app.github import GitHubClient, RateLimited, UserNotFound

SINCE = datetime(2026, 1, 1, tzinfo=UTC)
UNTIL = datetime(2026, 12, 31, tzinfo=UTC)


def _node(oid: str, added: int, deleted: int, parents: int = 1) -> dict:
    return {
        "oid": oid,
        "additions": added,
        "deletions": deleted,
        "authoredDate": "2026-03-01T12:00:00Z",
        "parents": {"totalCount": parents},
    }


def _handler(request: httpx.Request) -> httpx.Response:
    payload = json.loads(request.content)
    variables = payload["variables"]
    if "contributionsCollection" in payload["query"]:
        if variables["login"] == "ghost":
            return httpx.Response(
                200, json={"data": {"user": None}, "errors": [{"type": "NOT_FOUND"}]}
            )
        if variables["login"] == "busy":
            return httpx.Response(403, json={})
        repos = [
            {"nameWithOwner": "octo/app", "isFork": False, "primaryLanguage": {"name": "Go"}},
            {"nameWithOwner": "octo/fork", "isFork": True, "primaryLanguage": None},
        ]
        return httpx.Response(
            200,
            json={
                "data": {
                    "user": {
                        "id": "U1",
                        "contributionsCollection": {
                            "commitContributionsByRepository": [{"repository": r} for r in repos]
                        },
                    }
                }
            },
        )

    assert variables["name"] == "app", "forks must not be queried"
    if variables["cursor"] is None:
        nodes, page = (
            [_node("a", 10, 1), _node("m", 99, 99, parents=2)],
            {
                "hasNextPage": True,
                "endCursor": "c1",
            },
        )
    else:
        nodes, page = [_node("b", 5, 0)], {"hasNextPage": False, "endCursor": None}
    history = {"pageInfo": page, "nodes": nodes}
    return httpx.Response(
        200,
        json={"data": {"repository": {"defaultBranchRef": {"target": {"history": history}}}}},
    )


def _run(coro):
    return asyncio.run(coro)


async def _commits(login: str):
    client = GitHubClient("token", transport=httpx.MockTransport(_handler))
    try:
        return await client.user_commits(login, SINCE, UNTIL)
    finally:
        await client.aclose()


def test_user_commits_paginates_and_skips_forks() -> None:
    commits = _run(_commits("octo"))

    assert [c.sha for c in commits] == ["a", "m", "b"]
    assert all(c.repo == "octo/app" and c.language == "Go" for c in commits)
    assert commits[1].is_merge


def test_unknown_user_raises() -> None:
    with pytest.raises(UserNotFound):
        _run(_commits("ghost"))


def test_rate_limit_raises() -> None:
    with pytest.raises(RateLimited):
        _run(_commits("busy"))
