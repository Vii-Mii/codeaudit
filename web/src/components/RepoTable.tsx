import { useState } from "react";
import type { NamedTotals } from "../api";
import { num } from "../lib";

type SortKey = "name" | "added" | "deleted" | "net" | "commits";

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: "name", label: "Repository" },
  { key: "added", label: "Added" },
  { key: "deleted", label: "Deleted" },
  { key: "net", label: "Net" },
  { key: "commits", label: "Commits" },
];

const PAGE = 10;

export function RepoTable({ rows, onFocus }: { rows: NamedTotals[]; onFocus: (repo: string) => void }) {
  const [sort, setSort] = useState<{ key: SortKey; desc: boolean }>({ key: "added", desc: true });
  const [expanded, setExpanded] = useState(false);

  const sorted = [...rows].sort((a, b) => {
    const cmp = sort.key === "name" ? a.name.localeCompare(b.name) : a[sort.key] - b[sort.key];
    return sort.desc ? -cmp : cmp;
  });
  const visible = expanded ? sorted : sorted.slice(0, PAGE);
  const peak = Math.max(1, ...rows.map((r) => r.added + r.deleted));

  return (
    <>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {COLUMNS.map((c) => (
                <th key={c.key} aria-sort={sort.key === c.key ? (sort.desc ? "descending" : "ascending") : "none"}>
                  <button
                    onClick={() =>
                      setSort((s) => ({ key: c.key, desc: s.key === c.key ? !s.desc : c.key !== "name" }))
                    }
                  >
                    {c.label}
                    <span className="sort">{sort.key === c.key ? (sort.desc ? "↓" : "↑") : ""}</span>
                  </button>
                </th>
              ))}
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {visible.map((r) => (
              <tr key={r.name}>
                <td>
                  <a href={`https://github.com/${r.name}`} target="_blank" rel="noreferrer">
                    <span className="repo-owner">{r.name.split("/")[0]}/</span>
                    {r.name.split("/")[1]}
                  </a>
                  <span className="mini-bar" style={{ width: `${((r.added + r.deleted) / peak) * 100}%` }} />
                </td>
                <td className="add tabular">+{num(r.added)}</td>
                <td className="del tabular">−{num(r.deleted)}</td>
                <td className="tabular">{num(r.net)}</td>
                <td className="tabular">{num(r.commits)}</td>
                <td>
                  <button className="icon-btn small" title="Focus on this repository" onClick={() => onFocus(r.name)}>
                    ⌖
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > PAGE && (
        <button className="btn-link show-more" onClick={() => setExpanded((e) => !e)}>
          {expanded ? "Show less" : `Show all ${rows.length} repositories`}
        </button>
      )}
    </>
  );
}
