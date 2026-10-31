export interface Totals {
  added: number;
  deleted: number;
  net: number;
  commits: number;
}

export interface NamedTotals extends Totals {
  name: string;
}

export interface DayTotals extends Totals {
  date: string;
}

export interface Insights {
  active_days: number;
  longest_streak: number;
  current_streak: number;
  avg_lines_per_commit: number;
  busiest_day: DayTotals | null;
  by_weekday: Totals[];
}

export interface UserStats {
  login: string;
  mode: "fast";
  since: string;
  until: string;
  generated_at: string;
  filters: { repos: string[]; languages: string[]; max_commit_lines: number | null };
  facets: { repos: string[]; languages: string[] };
  total: Totals;
  insights: Insights;
  by_language: NamedTotals[];
  by_repo: NamedTotals[];
  by_day: DayTotals[];
}

export interface StatsQuery {
  since?: string;
  until?: string;
  repos: string[];
  languages: string[];
  maxCommitLines?: number;
}

export const GITHUB_LOGIN = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/;

export const CARD_THEMES = ["ink", "sand", "carbon", "ember", "nebula"] as const;
export type CardTheme = (typeof CARD_THEMES)[number];

const API_URL = import.meta.env.VITE_API_URL ?? "";

export function cardUrl(login: string, theme: CardTheme = "ink"): string {
  const base = API_URL || window.location.origin;
  return `${base}/api/v1/users/${encodeURIComponent(login)}/card.svg?theme=${theme}`;
}

export async function fetchUserStats(
  login: string,
  query: StatsQuery,
  signal?: AbortSignal,
): Promise<UserStats> {
  const params = new URLSearchParams();
  if (query.since) params.set("since", query.since);
  if (query.until) params.set("until", query.until);
  query.repos.forEach((r) => params.append("repo", r));
  query.languages.forEach((l) => params.append("language", l));
  if (query.maxCommitLines) params.set("max_commit_lines", String(query.maxCommitLines));

  const response = await fetch(
    `${API_URL}/api/v1/users/${encodeURIComponent(login)}/stats?${params}`,
    { signal },
  );
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : null;
    throw new Error(detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}
