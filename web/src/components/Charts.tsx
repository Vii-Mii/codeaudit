import type { DayTotals, NamedTotals, Totals } from "../api";
import { addDays, formatDate, isoDate, languageColor, num, parseDate } from "../lib";

const LEVELS = 5;

export function Heatmap({ days, since, until }: { days: DayTotals[]; since: string; until: string }) {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const start = parseDate(since);
  const end = parseDate(until);
  // Align the first column to Monday so rows are weekdays.
  const first = addDays(start, -((start.getDay() + 6) % 7));
  const peak = Math.max(1, ...days.map((d) => d.added + d.deleted));

  const cells = [];
  for (let d = first; d <= end; d = addDays(d, 1)) {
    const iso = isoDate(d);
    const day = byDate.get(iso);
    const churn = day ? day.added + day.deleted : 0;
    const level = churn === 0 ? 0 : Math.min(LEVELS - 1, Math.ceil(Math.sqrt(churn / peak) * (LEVELS - 1)));
    cells.push(
      <span
        key={iso}
        className={`cell l${level}`}
        style={d < start ? { visibility: "hidden" } : undefined}
        title={
          day
            ? `${formatDate(iso)} · +${num(day.added)} −${num(day.deleted)} · ${day.commits} commit${day.commits === 1 ? "" : "s"}`
            : `${formatDate(iso)} · no activity`
        }
      />,
    );
  }

  return (
    <div className="heatmap-wrap">
      <div className="heatmap">{cells}</div>
    </div>
  );
}

export function HeatLegend() {
  return (
    <span className="heat-legend muted">
      Less
      {Array.from({ length: LEVELS }, (_, i) => (
        <span key={i} className={`cell l${i}`} />
      ))}
      More
    </span>
  );
}

export function LanguageBars({ rows }: { rows: NamedTotals[] }) {
  const churn = rows.reduce((s, r) => s + r.added + r.deleted, 0) || 1;
  return (
    <ul className="langs">
      {rows.slice(0, 8).map((r, i) => {
        const share = (r.added + r.deleted) / churn;
        const color = languageColor(r.name, i);
        return (
          <li key={r.name}>
            <span className="lang-name">
              <span className="dot" style={{ background: color }} />
              {r.name}
            </span>
            <span className="track">
              <span className="fill" style={{ width: `${Math.max(share * 100, 1)}%`, background: color }} />
            </span>
            <span className="muted tabular">{(share * 100).toFixed(share < 0.1 ? 1 : 0)}%</span>
          </li>
        );
      })}
    </ul>
  );
}

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export function WeekdayChart({ days }: { days: Totals[] }) {
  const values = days.map((d) => d.added + d.deleted);
  const peak = Math.max(1, ...values);
  const top = values.indexOf(Math.max(...values));
  return (
    <div>
      <div className="weekdays">
        {days.map((d, i) => (
          <div
            key={WEEKDAYS[i]}
            className="weekday"
            title={`${WEEKDAYS[i]} · +${num(d.added)} −${num(d.deleted)} · ${d.commits} commits`}
          >
            <div className="weekday-bar">
              <div className={i === top ? "on" : ""} style={{ height: `${Math.max((values[i] / peak) * 100, 3)}%` }} />
            </div>
            <span className="muted">{WEEKDAYS[i][0]}</span>
          </div>
        ))}
      </div>
      {values[top] > 0 && (
        <p className="muted small">
          Most productive on <strong className="fg">{WEEKDAYS[top]}s</strong>
        </p>
      )}
    </div>
  );
}
