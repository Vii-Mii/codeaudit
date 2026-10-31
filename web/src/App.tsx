import { useCallback, useEffect, useState } from "react";
import { fetchUserStats, type UserStats } from "./api";
import { Dashboard } from "./components/Dashboard";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { DEFAULT_VIEW, LARGE_COMMIT_LINES, pushRecent, rangeFor, readView, writeView, type ViewState } from "./lib";

type SiteTheme = "light" | "dark";

function initialTheme(): SiteTheme {
  const saved = localStorage.getItem("codeaudit:theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [theme, setTheme] = useState<SiteTheme>(initialTheme);
  const [view, setView] = useState<ViewState>(readView);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("codeaudit:theme", theme);
  }, [theme]);

  useEffect(() => writeView(view), [view]);

  const range = rangeFor(view);
  const requestKey = JSON.stringify([view.login, range, view.repos, view.languages, view.skipLarge]);

  useEffect(() => {
    if (!view.login) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    fetchUserStats(
      view.login,
      {
        ...range,
        repos: view.repos,
        languages: view.languages,
        maxCommitLines: view.skipLarge ? LARGE_COMMIT_LINES : undefined,
      },
      controller.signal,
    )
      .then((s) => {
        setStats(s);
        pushRecent(s.login);
      })
      .catch((e: Error) => {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
    // requestKey captures every input that changes the request.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  const search = useCallback((login: string) => {
    setStats(null);
    setError(null);
    setView((v) => ({ ...DEFAULT_VIEW, login, period: v.period === "custom" ? DEFAULT_VIEW.period : v.period }));
    window.scrollTo({ top: 0 });
  }, []);

  const change = useCallback((patch: Partial<ViewState>) => setView((v) => ({ ...v, ...patch })), []);

  return (
    <>
      <div className={`progress ${loading ? "on" : ""}`} aria-hidden />
      <Header
        login={view.login}
        theme={theme}
        onToggleTheme={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
        onHome={() => {
          setStats(null);
          setError(null);
          setView(DEFAULT_VIEW);
        }}
        onSearch={search}
      />
      <main>
        {!view.login ? (
          <Hero onSearch={search} />
        ) : stats && stats.login.toLowerCase() === view.login.toLowerCase() ? (
          <Dashboard stats={stats} view={view} loading={loading} error={error} onChange={change} />
        ) : error ? (
          <div className="empty">
            <h3>Something went wrong</h3>
            <p className="muted">{error}</p>
          </div>
        ) : (
          <Skeleton login={view.login} />
        )}
      </main>
      <Footer />
    </>
  );
}

function Skeleton({ login }: { login: string }) {
  return (
    <div className="dashboard" aria-busy>
      <p className="muted loading-note">
        Crunching commits for <strong className="fg">{login}</strong>. The first load can take a few seconds.
      </p>
      <div className="tiles">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="tile skeleton" />
        ))}
      </div>
      <div className="panel skeleton tall" />
      <div className="grid-2">
        <div className="panel skeleton tall" />
        <div className="panel skeleton tall" />
      </div>
    </div>
  );
}
