from __future__ import annotations

from html import escape
from typing import Literal

from app.schemas import UserStats

Theme = Literal["ink", "sand", "carbon", "ember", "nebula"]

DEFAULT_THEME: Theme = "ink"

WIDTH, HEIGHT, PAD = 480, 232, 24
_THEMES: dict[str, dict[str, str]] = {
    # Light: crisp white, black type, electric blue to violet accent.
    "ink": {
        "bg1": "#ffffff",
        "bg2": "#f7f7f5",
        "fg": "#0a0a0a",
        "muted": "#6e6e69",
        "border": "#e6e6e1",
        "track": "#ecece8",
        "a1": "#2563eb",
        "a2": "#7c3aed",
    },
    # Light: warm paper with a terracotta to amber accent.
    "sand": {
        "bg1": "#f7f2ea",
        "bg2": "#efe7da",
        "fg": "#26211b",
        "muted": "#8a7e6c",
        "border": "#dfd3bd",
        "track": "#e8dec9",
        "a1": "#c2410c",
        "a2": "#e08a1e",
    },
    # Dark: neutral charcoal with a lime to green accent.
    "carbon": {
        "bg1": "#0b0b0c",
        "bg2": "#151516",
        "fg": "#ececec",
        "muted": "#8a8a8a",
        "border": "#262628",
        "track": "#202022",
        "a1": "#a3e635",
        "a2": "#4ade80",
    },
    # Dark: warm black with an orange to rose accent.
    "ember": {
        "bg1": "#120c09",
        "bg2": "#1d1410",
        "fg": "#f5e9df",
        "muted": "#a08c7c",
        "border": "#34261d",
        "track": "#2a1e17",
        "a1": "#fb923c",
        "a2": "#f43f5e",
    },
    # Dark: deep indigo with a violet to cyan accent.
    "nebula": {
        "bg1": "#0c0a1c",
        "bg2": "#17143a",
        "fg": "#ebe9ff",
        "muted": "#8e8ab8",
        "border": "#2a2660",
        "track": "#1f1b4a",
        "a1": "#8b5cf6",
        "a2": "#22d3ee",
    },
}
_LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "Kotlin": "#A97BFF",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "C": "#555555",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Swift": "#F05138",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
}
_FALLBACK_COLORS = ("#8b949e", "#a371f7", "#3fb950", "#d29922")
# SVGs loaded through <img> cannot fetch web fonts, so this falls back to the
# system monospace when JetBrains Mono is not installed on the viewer's machine.
_FONT = (
    "font-family:'JetBrains Mono','SF Mono',ui-monospace,SFMono-Regular,"
    "Menlo,Consolas,'Liberation Mono',monospace"
)


def _compact(n: int) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    for limit, suffix in ((1_000_000, "M"), (1_000, "k")):
        if n >= limit:
            return f"{sign}{n / limit:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{sign}{n}"


def _trim(text: str, limit: int) -> str:
    """Monospace text is wide, so shorten long names instead of overflowing."""
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _style(c: dict[str, str], animate: bool) -> str:
    # Opt-in: rasterizers and link previews snapshot at t=0 and would show a blank card.
    motion = (
        ".f{animation:f .7s ease-out}"
        ".d{stroke-dasharray:1;animation:d 1.6s ease-out}"
        ".k{animation:k 1.1s steps(1) infinite}"
        "@keyframes f{from{opacity:0}}"
        "@keyframes d{from{stroke-dashoffset:1}}"
        "@keyframes k{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.f,.d,.k{animation:none}}"
        if animate
        else ""
    )
    return (
        "<style>"
        f"text{{{_FONT};fill:{c['fg']}}}"
        f".m{{fill:{c['muted']}}}"
        f".a{{fill:{c['a1']}}}"
        ".t{font-size:15px;font-weight:600;letter-spacing:-.03em}"
        ".s{font-size:10.5px}"
        ".l{font-size:9px;font-weight:500;letter-spacing:.1em}"
        ".v{font-size:15px;font-weight:600;letter-spacing:-.04em}"
        ".h{font-size:27px;font-weight:700;letter-spacing:-.06em}"
        f"{motion}</style>"
    )


def _frame(theme: Theme, height: int, body: str, animate: bool = False) -> str:
    c = _THEMES[theme]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="CodeAudit card">'
        f"{_style(c, animate)}<defs>"
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["bg1"]}"/><stop offset="1" stop-color="{c["bg2"]}"/>'
        "</linearGradient>"
        # userSpaceOnUse so a flat (zero-height) sparkline still gets a stroke.
        f'<linearGradient id="ac" gradientUnits="userSpaceOnUse" x1="{PAD}" y1="0" '
        f'x2="{WIDTH - PAD}" y2="0">'
        f'<stop offset="0" stop-color="{c["a1"]}"/><stop offset="1" stop-color="{c["a2"]}"/>'
        "</linearGradient>"
        '<linearGradient id="ht" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{c["a1"]}"/><stop offset="1" stop-color="{c["a2"]}"/>'
        "</linearGradient>"
        '<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c["a1"]}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{c["a1"]}" stop-opacity="0"/>'
        "</linearGradient></defs>"
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="8" '
        f'fill="url(#bg)" stroke="{c["border"]}"/>'
        f"{body}</svg>"
    )


def _sparkline(stats: UserStats, top: int, bottom: int) -> tuple[str, str]:
    weeks = [0] * max((stats.until - stats.since).days // 7 + 1, 2)
    for day in stats.by_day:
        i = (day.date - stats.since).days // 7
        if 0 <= i < len(weeks):
            weeks[i] += day.added + day.deleted
    peak = max(weeks) or 1
    step = (WIDTH - 2 * PAD) / (len(weeks) - 1)
    # sqrt scale keeps one huge week from flattening the rest.
    points = [
        (PAD + i * step, bottom - 2 - (v / peak) ** 0.5 * (bottom - top - 4))
        for i, v in enumerate(weeks)
    ]
    line = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(points, points[1:], strict=False):
        mid = (x0 + x1) / 2
        line += f"C{mid:.1f},{y0:.1f} {mid:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    area = f"{line}L{points[-1][0]:.1f},{bottom}L{PAD},{bottom}Z"
    return line, area


def render_card(stats: UserStats, theme: Theme = DEFAULT_THEME, animate: bool = False) -> str:
    c = _THEMES[theme]
    t, insights = stats.total, stats.insights
    right = WIDTH - PAD
    line, area = _sparkline(stats, top=74, bottom=130)
    parts = [
        '<g class="f">',
        f'<text x="{PAD}" y="38" class="t"><tspan class="m">@</tspan>'
        f"{escape(_trim(stats.login, 22))}</text>",
        f'<text x="{PAD}" y="56" class="s m">{stats.since:%b %Y} – {stats.until:%b %Y}</text>',
        f'<text x="{right}" y="42" class="h" text-anchor="end" style="fill:url(#ht)">'
        f"+{_compact(t.added)}</text>",
        f'<text x="{right}" y="58" class="s m" text-anchor="end">lines written</text>',
        "</g>",
        f'<path d="{area}" fill="url(#ar)" class="f"/>',
        f'<path d="{line}" fill="none" stroke="url(#ac)" stroke-width="1.75" '
        'stroke-linecap="round" pathLength="1" class="d"/>',
        '<g class="f">',
    ]

    column = (WIDTH - 2 * PAD) / 4
    net = f"+{_compact(t.net)}" if t.net >= 0 else _compact(t.net)
    for i, (label, value) in enumerate(
        (
            ("COMMITS", _compact(t.commits)),
            ("NET LINES", net),
            ("ACTIVE DAYS", str(insights.active_days)),
            ("BEST STREAK", f"{insights.longest_streak}d"),
        )
    ):
        x = PAD + i * column
        parts.append(f'<text x="{x:.0f}" y="158" class="l m">{label}</text>')
        parts.append(f'<text x="{x:.0f}" y="178" class="v">{value}</text>')

    bar_y, bar_width = 194, WIDTH - 2 * PAD
    languages = [lang for lang in stats.by_language if lang.added + lang.deleted > 0][:4]
    churn = sum(lang.added + lang.deleted for lang in stats.by_language) or 1
    parts.append(
        f'<clipPath id="lb"><rect x="{PAD}" y="{bar_y}" width="{bar_width}" height="4" rx="2"/>'
        f'</clipPath><g clip-path="url(#lb)">'
        f'<rect x="{PAD}" y="{bar_y}" width="{bar_width}" height="4" fill="{c["track"]}"/>'
    )
    x = float(PAD)
    legend = []
    for i, lang in enumerate(languages):
        share = (lang.added + lang.deleted) / churn
        color = _LANGUAGE_COLORS.get(lang.name, _FALLBACK_COLORS[i % len(_FALLBACK_COLORS)])
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{share * bar_width:.1f}" height="4" '
            f'fill="{color}"/>'
        )
        x += share * bar_width
        lx = PAD + i * column
        legend.append(
            f'<rect x="{lx:.1f}" y="{bar_y + 19}" width="7" height="7" rx="2" fill="{color}"/>'
        )
        legend.append(
            f'<text x="{lx + 12:.1f}" y="{bar_y + 26}" class="s">{escape(_trim(lang.name, 8))} '
            f'<tspan class="m">{share:.0%}</tspan></text>'
        )
    parts.append("</g>")
    parts.extend(legend)
    parts.append("</g>")
    return _frame(theme, HEIGHT, "".join(parts), animate)


def render_error(message: str, theme: Theme = DEFAULT_THEME) -> str:
    body = (
        f'<text x="{PAD}" y="38" class="t" style="fill:url(#ht)">codeaudit</text>'
        f'<text x="{PAD}" y="62" class="s m">{escape(_trim(message, 60))}</text>'
    )
    return _frame(theme, 88, body)