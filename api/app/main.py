from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.card import Theme, render_card, render_error
from app.config import settings
from app.github import GitHubClient, GitHubError, RateLimited, UserNotFound
from app.schemas import Filters, UserStats
from app.stats import TTLCache, user_stats

GITHUB_LOGIN = r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$"
# GitHub's contributionsCollection rejects ranges longer than one year.
MAX_RANGE_DAYS = 364
MAX_FILTER_VALUES = 50


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.github = GitHubClient(settings.github_token) if settings.github_token else None
    app.state.cache = TTLCache(settings.cache_ttl_seconds, max_items=256)
    yield
    if app.state.github is not None:
        await app.state.github.aclose()


app = FastAPI(title="CodeAudit API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_optional_github(request: Request) -> GitHubClient | None:
    return getattr(request.app.state, "github", None)


def get_github(
    client: Annotated[GitHubClient | None, Depends(get_optional_github)],
) -> GitHubClient:
    if client is None:
        raise HTTPException(503, "GitHub token is not configured on this server")
    return client


def get_cache(request: Request) -> TTLCache:
    return request.app.state.cache


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/users/{login}/stats", response_model=UserStats)
async def get_user_stats(
    login: Annotated[str, Path(pattern=GITHUB_LOGIN)],
    client: Annotated[GitHubClient, Depends(get_github)],
    cache: Annotated[TTLCache, Depends(get_cache)],
    since: date | None = None,
    until: date | None = None,
    repo: Annotated[list[str] | None, Query(description="owner/name, repeatable")] = None,
    language: Annotated[list[str] | None, Query(description="repeatable")] = None,
    max_commit_lines: Annotated[int | None, Query(ge=1)] = None,
) -> UserStats:
    repos, languages = repo or [], language or []
    if len(repos) > MAX_FILTER_VALUES or len(languages) > MAX_FILTER_VALUES:
        raise HTTPException(422, f"at most {MAX_FILTER_VALUES} values per filter")
    filters = Filters(repos=repos, languages=languages, max_commit_lines=max_commit_lines)
    return await _load_stats(client, cache, login, since, until, filters)


@app.get("/api/v1/users/{login}/card.svg", response_class=Response)
async def get_user_card(
    login: Annotated[str, Path(pattern=GITHUB_LOGIN)],
    client: Annotated[GitHubClient | None, Depends(get_optional_github)],
    cache: Annotated[TTLCache, Depends(get_cache)],
    theme: Theme = "light",
    animate: bool = False,
) -> Response:
    try:
        stats = await _load_stats(get_github(client), cache, login, None, None)
    except HTTPException as exc:
        # Always 200: image proxies like GitHub's camo hide non-200 responses entirely.
        return _svg(render_error(str(exc.detail), theme), max_age=300)
    return _svg(render_card(stats, theme, animate), max_age=settings.cache_ttl_seconds)


def _svg(content: str, max_age: int) -> Response:
    return Response(
        content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": f"public, max-age={max_age}",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'",
        },
    )


async def _load_stats(
    client: GitHubClient,
    cache: TTLCache,
    login: str,
    since: date | None,
    until: date | None,
    filters: Filters | None = None,
) -> UserStats:
    until = until or datetime.now(UTC).date()
    since = since or until - timedelta(days=MAX_RANGE_DAYS)
    if since > until:
        raise HTTPException(422, "since must not be after until")
    if (until - since).days > MAX_RANGE_DAYS:
        raise HTTPException(422, "date range must be at most one year")

    try:
        return await user_stats(client, cache, login, since, until, filters)
    except UserNotFound:
        raise HTTPException(404, f"GitHub user '{login}' not found") from None
    except RateLimited:
        raise HTTPException(429, "GitHub rate limit reached, try again later") from None
    except GitHubError:
        raise HTTPException(502, "GitHub API request failed") from None
