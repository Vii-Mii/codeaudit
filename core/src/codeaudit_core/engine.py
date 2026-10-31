from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date

from codeaudit_core.filters import is_excluded
from codeaudit_core.identity import IdentityResolver
from codeaudit_core.languages import detect_language
from codeaudit_core.models import Commit


@dataclass
class Totals:
    added: int = 0
    deleted: int = 0
    commits: int = 0

    @property
    def net(self) -> int:
        return self.added - self.deleted


@dataclass
class Report:
    total: Totals = field(default_factory=Totals)
    by_author: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    by_language: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    by_repo: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    by_day: dict[date, Totals] = field(default_factory=lambda: defaultdict(Totals))


def analyze(
    commits: Iterable[Commit],
    resolver: IdentityResolver | None = None,
    ignore: Iterable[str] = (),
) -> Report:
    resolver = resolver or IdentityResolver()
    ignore = tuple(ignore)
    report = Report()

    for commit in commits:
        if commit.is_merge:
            continue
        author = resolver.resolve(commit.author_name, commit.author_email)
        if author is None:
            continue

        languages_seen: set[str] = set()
        buckets = [report.total, report.by_author[author], report.by_day[commit.authored_at.date()]]
        if commit.repo:
            buckets.append(report.by_repo[commit.repo])
        for change in commit.files:
            if change.path and is_excluded(change.path, ignore):
                continue
            language = commit.language or detect_language(change.path)
            lang_totals = report.by_language[language]
            lang_totals.added += change.added
            lang_totals.deleted += change.deleted
            if language not in languages_seen:
                languages_seen.add(language)
                lang_totals.commits += 1
            for bucket in buckets:
                bucket.added += change.added
                bucket.deleted += change.deleted

        for bucket in buckets:
            bucket.commits += 1

    return report
