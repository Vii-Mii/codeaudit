import { useEffect, useRef, useState } from "react";
import type { UserStats } from "../api";
import { LARGE_COMMIT_LINES, PERIODS, num, type ViewState } from "../lib";

interface Props {
  stats: UserStats;
  view: ViewState;
  onChange: (patch: Partial<ViewState>) => void;
}

export function FilterBar({ stats, view, onChange }: Props) {
  const active = view.repos.length > 0 || view.languages.length > 0 || view.skipLarge;

  return (
    <div className="filterbar">
      <div className="segmented" role="tablist" aria-label="Period">
        {PERIODS.map((p) => (
          <button
            key={p.id}
            role="tab"
            aria-selected={view.period === p.id}
            className={view.period === p.id ? "on" : ""}
            onClick={() =>
              onChange(
                p.id === "custom"
                  ? { period: p.id, since: view.since || stats.since, until: view.until || stats.until }
                  : { period: p.id },
              )
            }
          >
            {p.label}
          </button>
        ))}
      </div>

      {view.period === "custom" && (
        <div className="dates">
          <input
            type="date"
            value={view.since}
            max={view.until || undefined}
            onChange={(e) => onChange({ since: e.target.value })}
            aria-label="From"
          />
          <span className="muted">→</span>
          <input
            type="date"
            value={view.until}
            min={view.since || undefined}
            onChange={(e) => onChange({ until: e.target.value })}
            aria-label="To"
          />
        </div>
      )}

      <MultiSelect
        label="Repositories"
        options={stats.facets.repos}
        selected={view.repos}
        onChange={(repos) => onChange({ repos })}
      />
      <MultiSelect
        label="Languages"
        options={stats.facets.languages}
        selected={view.languages}
        onChange={(languages) => onChange({ languages })}
      />

      <label
        className="switch"
        title={`Excludes commits over ${num(LARGE_COMMIT_LINES)} changed lines, usually generated, vendored or lockfile changes.`}
      >
        <input
          type="checkbox"
          checked={view.skipLarge}
          onChange={(e) => onChange({ skipLarge: e.target.checked })}
        />
        <span className="switch-track" aria-hidden>
          <span className="switch-thumb" />
        </span>
        Skip bulk commits
      </label>

      {active && (
        <button
          className="btn-link"
          onClick={() => onChange({ repos: [], languages: [], skipLarge: false })}
        >
          Reset
        </button>
      )}
    </div>
  );
}

interface MultiSelectProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (values: string[]) => void;
}

function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const ref = useRef<HTMLDetailsElement>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) ref.current.open = false;
    };
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, []);

  const all = [...selected.filter((s) => !options.includes(s)), ...options];
  const visible = all.filter((o) => o.toLowerCase().includes(query.toLowerCase()));
  const toggle = (value: string) =>
    onChange(selected.includes(value) ? selected.filter((s) => s !== value) : [...selected, value]);

  return (
    <details className="select" ref={ref}>
      <summary className={selected.length ? "chip chip-active" : "chip"}>
        {label}
        {selected.length > 0 && <span className="count">{selected.length}</span>}
        <span className="caret" aria-hidden>
          ▾
        </span>
      </summary>
      <div className="menu">
        {all.length > 6 && (
          <input
            className="menu-search"
            placeholder={`Search ${label.toLowerCase()}…`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        )}
        <ul>
          {visible.map((o) => (
            <li key={o}>
              <label>
                <input type="checkbox" checked={selected.includes(o)} onChange={() => toggle(o)} />
                <span>{o}</span>
              </label>
            </li>
          ))}
          {visible.length === 0 && <li className="muted menu-empty">No matches</li>}
        </ul>
        {selected.length > 0 && (
          <button className="btn-link menu-clear" onClick={() => onChange([])}>
            Clear selection
          </button>
        )}
      </div>
    </details>
  );
}
