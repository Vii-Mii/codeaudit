export const LARGE_COMMIT_LINES = 5000;

// Override with VITE_GITHUB_REPO ("owner/name") and VITE_SPONSOR_URL at build time.
export const REPO: string = import.meta.env.VITE_GITHUB_REPO || "Vii-Mii/codeaudit";
export const AUTHOR = { name: "Vijayaraj", url: "https://github.com/Vii-Mii" };
const REPO_URL = `https://github.com/${REPO}`;

export const LINKS = {
  repo: REPO_URL,
  issues: `${REPO_URL}/issues`,
  bug: `${REPO_URL}/issues/new?labels=bug`,
  feature: `${REPO_URL}/issues/new?labels=enhancement`,
  contribute: `${REPO_URL}/blob/main/CONTRIBUTING.md`,
  license: `${REPO_URL}/blob/main/LICENSE`,
  sponsor: (import.meta.env.VITE_SPONSOR_URL as string | undefined) || `https://github.com/sponsors/${REPO.split("/")[0]}`,
};

export type Period = "30d" | "90d" | "180d" | "365d" | "ytd" | "custom";

export const PERIODS: { id: Period; label: string }[] = [
  { id: "30d", label: "30D" },
  { id: "90d", label: "90D" },
  { id: "180d", label: "6M" },
  { id: "365d", label: "1Y" },
  { id: "ytd", label: "YTD" },
  { id: "custom", label: "Custom" },
];

const PERIOD_DAYS: Partial<Record<Period, number>> = {
  "30d": 29,
  "90d": 89,
  "180d": 179,
  "365d": 364,
};

export interface ViewState {
  login: string;
  period: Period;
  since: string;
  until: string;
  repos: string[];
  languages: string[];
  skipLarge: boolean;
}

export const DEFAULT_VIEW: ViewState = {
  login: "",
  period: "365d",
  since: "",
  until: "",
  repos: [],
  languages: [],
  skipLarge: false,
};

export function isoDate(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function parseDate(s: string): Date {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function addDays(d: Date, n: number): Date {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

export function rangeFor(view: ViewState): { since?: string; until?: string } {
  const today = new Date();
  if (view.period === "custom") {
    return { since: view.since || undefined, until: view.until || undefined };
  }
  if (view.period === "ytd") {
    return { since: isoDate(new Date(today.getFullYear(), 0, 1)), until: isoDate(today) };
  }
  return { since: isoDate(addDays(today, -PERIOD_DAYS[view.period]!)), until: isoDate(today) };
}

export function readView(): ViewState {
  const p = new URLSearchParams(window.location.search);
  const period = p.get("p") as Period | null;
  return {
    login: p.get("u") ?? "",
    period: period && PERIODS.some((x) => x.id === period) ? period : DEFAULT_VIEW.period,
    since: p.get("since") ?? "",
    until: p.get("until") ?? "",
    repos: p.getAll("repo"),
    languages: p.getAll("lang"),
    skipLarge: p.get("skip") === "1",
  };
}

export function writeView(view: ViewState): void {
  const p = new URLSearchParams();
  if (view.login) p.set("u", view.login);
  if (view.period !== DEFAULT_VIEW.period) p.set("p", view.period);
  if (view.period === "custom") {
    if (view.since) p.set("since", view.since);
    if (view.until) p.set("until", view.until);
  }
  view.repos.forEach((r) => p.append("repo", r));
  view.languages.forEach((l) => p.append("lang", l));
  if (view.skipLarge) p.set("skip", "1");
  const qs = p.toString();
  window.history.replaceState(null, "", qs ? `?${qs}` : window.location.pathname);
}

export const num = new Intl.NumberFormat().format;
const compactFmt = new Intl.NumberFormat(undefined, {
  notation: "compact",
  maximumFractionDigits: 1,
});
export const compact = (n: number) => compactFmt.format(n);
export const signed = (n: number) => (n > 0 ? `+${num(n)}` : n < 0 ? `−${num(-n)}` : "0");
export const signedCompact = (n: number) =>
  n > 0 ? `+${compact(n)}` : n < 0 ? `−${compact(-n)}` : "0";

export function formatDate(iso: string, withYear = true): string {
  return parseDate(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    ...(withYear ? { year: "numeric" } : {}),
  });
}

const LANGUAGE_COLORS: Record<string, string> = {
  Python: "#3572A5",
  JavaScript: "#f1e05a",
  TypeScript: "#3178c6",
  Go: "#00ADD8",
  Rust: "#dea584",
  Java: "#b07219",
  Kotlin: "#A97BFF",
  Ruby: "#701516",
  PHP: "#4F5D95",
  C: "#555555",
  "C++": "#f34b7d",
  "C#": "#178600",
  Swift: "#F05138",
  Shell: "#89e051",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Vue: "#41b883",
  Dart: "#00B4AB",
  Jupyter: "#DA5B0B",
  "Jupyter Notebook": "#DA5B0B",
};
const FALLBACK = ["#8b949e", "#a371f7", "#3fb950", "#d29922", "#f778ba"];

export function languageColor(name: string, index = 0): string {
  return LANGUAGE_COLORS[name] ?? FALLBACK[index % FALLBACK.length];
}

export function download(filename: string, content: string, type: string): void {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const RECENT_KEY = "codeaudit:recent";

export function getRecent(): string[] {
  try {
    const value = JSON.parse(localStorage.getItem(RECENT_KEY) ?? "[]");
    return Array.isArray(value) ? value.filter((v) => typeof v === "string").slice(0, 6) : [];
  } catch {
    return [];
  }
}

export function pushRecent(login: string): void {
  const next = [login, ...getRecent().filter((l) => l.toLowerCase() !== login.toLowerCase())];
  localStorage.setItem(RECENT_KEY, JSON.stringify(next.slice(0, 6)));
}
