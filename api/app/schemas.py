from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class TotalsOut(BaseModel):
    added: int
    deleted: int
    net: int
    commits: int


class NamedTotals(TotalsOut):
    name: str


class DayTotals(TotalsOut):
    date: date


class Insights(BaseModel):
    active_days: int
    longest_streak: int
    current_streak: int
    avg_lines_per_commit: int
    busiest_day: DayTotals | None
    # Monday first, always 7 entries.
    by_weekday: list[TotalsOut]


class Facets(BaseModel):
    """Every repository and language in the period, before filters, to populate filter menus."""

    repos: list[str]
    languages: list[str]


class Filters(BaseModel):
    repos: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    max_commit_lines: int | None = None


class UserStats(BaseModel):
    login: str
    mode: Literal["fast"] = "fast"
    since: date
    until: date
    generated_at: datetime
    filters: Filters
    facets: Facets
    total: TotalsOut
    insights: Insights
    by_language: list[NamedTotals]
    by_repo: list[NamedTotals]
    by_day: list[DayTotals]
