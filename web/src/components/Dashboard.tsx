import { useState, type ReactNode } from "react";
import type { UserStats } from "../api";
import { compact, download, formatDate, num, signed, signedCompact, type ViewState } from "../lib";
import { HeatLegend, Heatmap, LanguageBars, WeekdayChart } from "./Charts";
import { Embed } from "./Embed";
import { FilterBar } from "./FilterBar";
import { RepoTable } from "./RepoTable";

interface Props {
  stats: UserStats;
  view: ViewState;
  loading: boolean;
  error: string | null;
  onChange: (patch: Partial<ViewState>) => void;
}

export function Dashboard({ stats, view, loading, error, onChange }: Props) {
  const { total, insights } = stats;

  return (
    <div className={`dashboard ${loading ? "busy" : ""}`}>
      <Profile stats={stats} />
      <FilterBar stats={stats} view={view} onChange={onChange} />
      {error && <p className="notice error">{error}</p>}

      {total.commits === 0 ? (
        <div className="empty">
          <h3>No commits found</h3>
          <p className="muted">
            Nothing matched for this period and filters. Try a longer period or reset filters. Only public
            contributions on default branches are counted.
          </p>
        </div>
      ) : (
        <>
          <section className="tiles">
            <Tile label="Lines added" value={`+${compact(total.added)}`} exact={num(total.added)} tone="add" />
            <Tile label="Lines deleted" value={`−${compact(total.deleted)}`} exact={num(total.deleted)} tone="del" />
            <Tile label="Net lines" value={signedCompact(total.net)} exact={signed(total.net)} />
            <Tile
              label="Commits"
              value={num(total.commits)}
              hint={`~${num(insights.avg_lines_per_commit)} lines per commit`}
            />
          </section>

          <Panel title="Activity" aside={<HeatLegend />}>
            <Heatmap days={stats.by_day} since={stats.since} until={stats.until} />
          </Panel>

          <section className="insights">
            <Insight label="Active days" value={num(insights.active_days)} />
            <Insight label="Longest streak" value={`${insights.longest_streak}d`} />
            <Insight
              label="Current streak"
              value={`${insights.current_streak}d`}
              hint={insights.current_streak > 0 ? "Keep it going" : undefined}
            />
            <Insight
              label="Biggest day"
              value={insights.busiest_day ? formatDate(insights.busiest_day.date, false) : "—"}
              hint={
                insights.busiest_day
                  ? `${compact(insights.busiest_day.added + insights.busiest_day.deleted)} lines changed`
                  : undefined
              }
            />
          </section>

          <div className="grid-2">
            <Panel title="Languages">
              <LanguageBars rows={stats.by_language} />
            </Panel>
            <Panel title="Weekly rhythm">
              <WeekdayChart days={insights.by_weekday} />
            </Panel>
          </div>

          <Panel title="Repositories" aside={<span className="muted small">{stats.by_repo.length}</span>}>
            <RepoTable rows={stats.by_repo} onFocus={(repo) => onChange({ repos: [repo] })} />
          </Panel>

          <Panel title="README card" aside={<span className="muted small">Show it off</span>}>
            <Embed login={stats.login} />
          </Panel>
        </>
      )}
    </div>
  );
}

function Profile({ stats }: { stats: UserStats }) {
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function exportCsv() {
    const rows = [
      "date,added,deleted,net,commits",
      ...stats.by_day.map((d) => `${d.date},${d.added},${d.deleted},${d.net},${d.commits}`),
    ];
    download(`${stats.login}-${stats.since}-${stats.until}.csv`, rows.join("\n"), "text/csv");
  }

  function exportJson() {
    download(`${stats.login}-${stats.since}-${stats.until}.json`, JSON.stringify(stats, null, 2), "application/json");
  }

  return (
    <section className="profile">
      <img
        className="avatar"
        src={`https://github.com/${encodeURIComponent(stats.login)}.png?size=128`}
        alt=""
        width={56}
        height={56}
      />
      <div className="profile-text">
        <h2>
          <a href={`https://github.com/${stats.login}`} target="_blank" rel="noreferrer">
            {stats.login}
          </a>
        </h2>
        <p className="muted small">
          {formatDate(stats.since)} – {formatDate(stats.until)}
          <span className="badge" title="Per-commit totals from the GitHub API. File-level exclusions are not applied.">
            fast mode
          </span>
        </p>
      </div>
      <div className="profile-actions">
        <button className="btn" onClick={copyLink}>
          {copied ? "Copied ✓" : "Copy link"}
        </button>
        <button className="btn" onClick={exportCsv}>
          CSV
        </button>
        <button className="btn" onClick={exportJson}>
          JSON
        </button>
      </div>
    </section>
  );
}

function Panel({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <section className="panel">
      <header className="panel-head">
        <h3>{title}</h3>
        {aside}
      </header>
      {children}
    </section>
  );
}

function Tile({
  label,
  value,
  exact,
  hint,
  tone,
}: {
  label: string;
  value: string;
  exact?: string;
  hint?: string;
  tone?: "add" | "del";
}) {
  return (
    <div className="tile" title={exact}>
      <span className="tile-label">{label}</span>
      <strong className={`tile-value ${tone ?? ""}`}>{value}</strong>
      {hint && <span className="muted small">{hint}</span>}
    </div>
  );
}

function Insight({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="insight">
      <span className="tile-label">{label}</span>
      <strong>{value}</strong>
      {hint && <span className="muted small">{hint}</span>}
    </div>
  );
}
