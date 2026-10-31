from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from app.card import _compact, render_card, render_error
from app.main import app, get_cache, get_optional_github
from app.schemas import (
    DayTotals,
    Facets,
    Filters,
    Insights,
    NamedTotals,
    TotalsOut,
    UserStats,
)
from app.stats import TTLCache
from tests.conftest import FakeGitHub


def _stats(language: str = "Python") -> UserStats:
    zero = TotalsOut(added=0, deleted=0, net=0, commits=0)
    return UserStats(
        login="octo",
        since=date(2025, 11, 1),
        until=date(2026, 10, 31),
        generated_at=datetime(2026, 10, 31, tzinfo=UTC),
        filters=Filters(),
        facets=Facets(repos=[], languages=[language, "Go"]),
        total=TotalsOut(added=12_345, deleted=2_000, net=10_345, commits=321),
        insights=Insights(
            active_days=120,
            longest_streak=14,
            current_streak=3,
            avg_lines_per_commit=44,
            busiest_day=None,
            by_weekday=[zero] * 7,
        ),
        by_language=[
            NamedTotals(name=language, added=9000, deleted=1000, net=8000, commits=200),
            NamedTotals(name="Go", added=3345, deleted=1000, net=2345, commits=121),
        ],
        by_repo=[],
        by_day=[
            DayTotals(date=date(2026, 1, 5), added=500, deleted=20, net=480, commits=4),
            DayTotals(date=date(2026, 6, 1), added=50, deleted=2, net=48, commits=1),
        ],
    )


def test_compact() -> None:
    assert [_compact(n) for n in (0, 999, 1000, 12_345, -2_500, 3_400_000)] == [
        "0",
        "999",
        "1k",
        "12.3k",
        "-2.5k",
        "3.4M",
    ]


def test_render_card_is_valid_svg_and_escapes_text() -> None:
    for theme in ("light", "dark", "midnight", "sunset"):
        svg = render_card(_stats(language="<script>alert(1)</script>"), theme)
        root = ET.fromstring(svg)

        assert root.tag.endswith("svg")
        assert "<script>" not in svg
        assert "+12.3k" in svg and "321" in svg and "14d" in svg
        assert "@keyframes" not in svg

    assert "@keyframes" in render_card(_stats(), animate=True)


def test_render_error_is_valid_svg() -> None:
    ET.fromstring(render_error("GitHub user 'x' not found & more"))


def test_card_endpoint(fake: FakeGitHub) -> None:
    response = TestClient(app).get("/api/v1/users/octo/card.svg?theme=dark")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert "max-age=3600" in response.headers["cache-control"]
    assert "default-src 'none'" in response.headers["content-security-policy"]
    ET.fromstring(response.text)


def test_card_endpoint_renders_errors_as_svg(fake: FakeGitHub) -> None:
    response = TestClient(app).get("/api/v1/users/ghost/card.svg")

    assert response.status_code == 200
    assert "not found" in response.text
    assert "max-age=300" in response.headers["cache-control"]


def test_card_without_token_renders_error() -> None:
    app.dependency_overrides[get_optional_github] = lambda: None
    app.dependency_overrides[get_cache] = lambda: TTLCache(60)
    try:
        response = TestClient(app).get("/api/v1/users/octo/card.svg")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "not configured" in response.text


def test_card_rejects_bad_theme(fake: FakeGitHub) -> None:
    assert TestClient(app).get("/api/v1/users/octo/card.svg?theme=pink").status_code == 422
