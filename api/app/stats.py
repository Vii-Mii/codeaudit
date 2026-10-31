from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from datetime import time as dtime
from typing import Any

from codeaudit_core import Commit, Totals, analyze

from app.github import GitHubClient
from app.schemas import (
    DayTotals,
    Facets,
    Filters,
    Insights,
    NamedTotals,
    TotalsOut,
    UserStats,
)


class TTLCache:
    def __init__(self, ttl_seconds: int, max_items: int = 1024) -> None:
        self._ttl = ttl_seconds
        self._max = max_items
        self._items: OrderedDict[tuple, tuple[float, Any]] = OrderedDict()

    def get(self, key: tuple) -> Any | None:
        item = self._items.get(key)
        if item is None or item[0] < time.monotonic():
            self._items.pop(key, None)
            return None
        self._items.move_to_end(key)
        return item[1]

    def set(self, key: tuple, value: Any) -> None:
        self._items[key] = (time.monotonic() + self._ttl, value)
        self._items.move_to_end(key)
        while len(self._items) > self._max:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()


def _churn(t: Totals) -> int:
    return t.added + t.deleted


def _totals(t: Totals) -> dict[str, int]:
    return {"added": t.added, "deleted": t.deleted, "net": t.net, "commits": t.commits}


def _ranked(breakdown: dict[str, Totals]) -> list[NamedTotals]:
    rows = sorted(breakdown.items(), key=lambda kv: _churn(kv[1]), reverse=True)
    return [NamedTotals(name=name, **_totals(t)) for name, t in rows]


def filter_commits(commits: Sequence[Commit], filters: Filters) -> list[Commit]:
    repos = {r.lower() for r in filters.repos}
    languages = {lang.lower() for lang in filters.languages}
    limit = filters.max_commit_lines
    return [
        c
        for c in commits
        if (not repos or c.repo.lower() in repos)
        and (not languages or (c.language or "").lower() in languages)
        and (limit is None or sum(f.added + f.deleted for f in c.files) <= limit)
    ]


def _insights(report_total: Totals, by_day: dict[date, Totals], until: date) -> Insights:
    active = sorted(d for d, t in by_day.items() if t.commits)
    longest = run = 0
    previous: date | None = None
    for day in active:
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    # A streak still counts as current if the last active day was today or yesterday.
    current = run if active and (until - active[-1]).days <= 1 else 0

    weekdays = [Totals() for _ in range(7)]
    for day, t in by_day.items():
        w = weekdays[day.weekday()]
        w.added += t.added
        w.deleted += t.deleted
        w.commits += t.commits

    busiest = max(by_day.items(), key=lambda kv: _churn(kv[1]), default=None)
    commits = report_total.commits
    return Insights(
        active_days=len(active),
        longest_streak=longest,
        current_streak=current,
        avg_lines_per_commit=_churn(report_total) // commits if commits else 0,
        busiest_day=DayTotals(date=busiest[0], **_totals(busiest[1])) if busiest else None,
        by_weekday=[TotalsOut(**_totals(t)) for t in weekdays],
    )


async def user_stats(
    client: GitHubClient,
    cache: TTLCache,
    login: str,
    since: date,
    until: date,
    filters: Filters | None = None,
) -> UserStats:
    filters = filters or Filters()
    # Cache raw commits so changing filters never costs another GitHub round trip.
    key = (login.lower(), since, until)
    commits = cache.get(key)
    if commits is None:
        commits = await client.user_commits(
            login,
            datetime.combine(since, dtime.min, tzinfo=UTC),
            datetime.combine(until, dtime.max.replace(microsecond=0), tzinfo=UTC),
        )
        cache.set(key, commits)

    unfiltered = analyze(commits)
    report = analyze(filter_commits(commits, filters))
    return UserStats(
        login=login,
        since=since,
        until=until,
        generated_at=datetime.now(UTC),
        filters=filters,
        facets=Facets(
            repos=[r.name for r in _ranked(unfiltered.by_repo)],
            languages=[lang.name for lang in _ranked(unfiltered.by_language)],
        ),
        total=TotalsOut(**_totals(report.total)),
        insights=_insights(report.total, report.by_day, until),
        by_language=_ranked(report.by_language),
        by_repo=_ranked(report.by_repo),
        by_day=[DayTotals(date=d, **_totals(t)) for d, t in sorted(report.by_day.items())],
    )
