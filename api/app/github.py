from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import httpx
from codeaudit_core import Commit, FileChange

GRAPHQL_URL = "https://api.github.com/graphql"
MAX_REPOS = 100
MAX_COMMITS_PER_REPO = 1000


class GitHubError(Exception):
    pass


class UserNotFound(GitHubError):
    pass


class RateLimited(GitHubError):
    pass


_CONTRIBUTED_REPOS = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    id
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner isFork primaryLanguage { name } }
      }
    }
  }
}
"""

_HISTORY = """
query($owner: String!, $name: String!, $author: ID!, $since: GitTimestamp!,
      $until: GitTimestamp!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 100, after: $cursor, author: {id: $author},
                  since: $since, until: $until) {
            pageInfo { hasNextPage endCursor }
            nodes { oid additions deletions authoredDate parents { totalCount } }
          }
        }
      }
    }
  }
}
"""


class GitHubClient:
    def __init__(
        self,
        token: str,
        transport: httpx.AsyncBaseTransport | None = None,
        concurrency: int = 5,
    ) -> None:
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}", "User-Agent": "codeaudit"},
            timeout=30,
            transport=transport,
        )
        self._semaphore = asyncio.Semaphore(concurrency)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        async with self._semaphore:
            response = await self._http.post(
                GRAPHQL_URL, json={"query": query, "variables": variables}
            )
        if response.status_code in (403, 429):
            raise RateLimited("GitHub rate limit reached")
        if response.status_code >= 400:
            raise GitHubError(f"GitHub API returned {response.status_code}")
        body = response.json()
        errors = body.get("errors") or []
        types = {error.get("type") for error in errors}
        if "NOT_FOUND" in types:
            raise UserNotFound(variables.get("login", ""))
        if "RATE_LIMITED" in types:
            raise RateLimited("GitHub rate limit reached")
        if errors:
            raise GitHubError("GitHub GraphQL query failed")
        return body["data"]

    async def user_commits(self, login: str, since: datetime, until: datetime) -> list[Commit]:
        """Non-merge-filtered commits by `login` on the default branch of repos they pushed to."""
        data = await self._query(
            _CONTRIBUTED_REPOS,
            {"login": login, "from": since.isoformat(), "to": until.isoformat()},
        )
        user = data.get("user")
        if user is None:
            raise UserNotFound(login)
        contributions = user["contributionsCollection"]["commitContributionsByRepository"]
        repos = [c["repository"] for c in contributions if not c["repository"]["isFork"]]
        batches = await asyncio.gather(
            *(
                self._repo_commits(repo, user["id"], login, since, until)
                for repo in repos[:MAX_REPOS]
            )
        )
        return [commit for batch in batches for commit in batch]

    async def _repo_commits(
        self,
        repo: dict[str, Any],
        author_id: str,
        login: str,
        since: datetime,
        until: datetime,
    ) -> list[Commit]:
        name_with_owner = repo["nameWithOwner"]
        owner, name = name_with_owner.split("/", 1)
        language = (repo.get("primaryLanguage") or {}).get("name") or "Other"
        commits: list[Commit] = []
        cursor = None
        while len(commits) < MAX_COMMITS_PER_REPO:
            data = await self._query(
                _HISTORY,
                {
                    "owner": owner,
                    "name": name,
                    "author": author_id,
                    "since": since.isoformat(),
                    "until": until.isoformat(),
                    "cursor": cursor,
                },
            )
            ref = (data.get("repository") or {}).get("defaultBranchRef")
            if not ref:
                break
            history = ref["target"]["history"]
            commits.extend(
                Commit(
                    sha=node["oid"],
                    author_name=login,
                    author_email=login,
                    authored_at=datetime.fromisoformat(node["authoredDate"]),
                    parent_count=node["parents"]["totalCount"],
                    files=(
                        FileChange(path="", added=node["additions"], deleted=node["deletions"]),
                    ),
                    repo=name_with_owner,
                    language=language,
                )
                for node in history["nodes"]
            )
            if not history["pageInfo"]["hasNextPage"]:
                break
            cursor = history["pageInfo"]["endCursor"]
        return commits
