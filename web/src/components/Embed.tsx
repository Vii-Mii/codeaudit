import { useState } from "react";
import { CARD_THEMES, cardUrl, type CardTheme } from "../api";

type Format = "markdown" | "html";

export function Embed({ login }: { login: string }) {
  const [theme, setTheme] = useState<CardTheme>("carbon");
  const [format, setFormat] = useState<Format>("markdown");
  const [copied, setCopied] = useState(false);

  const src = cardUrl(login, theme);
  const page = `${window.location.origin}${window.location.pathname}?u=${encodeURIComponent(login)}`;
  const snippet =
    format === "markdown"
      ? `[![${login}'s code activity](${src})](${page})`
      : `<a href="${page}"><img src="${src}" alt="${login}'s code activity" width="480" /></a>`;

  async function copy() {
    await navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="embed">
      <div className="embed-preview">
        <img key={src} src={src} alt={`CodeAudit card for ${login}`} width={480} />
      </div>
      <div className="embed-controls">
        <div className="swatches" role="radiogroup" aria-label="Card theme">
          {CARD_THEMES.map((t) => (
            <button
              key={t}
              role="radio"
              aria-checked={theme === t}
              className={`swatch sw-${t} ${theme === t ? "on" : ""}`}
              onClick={() => setTheme(t)}
              title={t}
            >
              <span className="sr-only">{t}</span>
            </button>
          ))}
          <span className="muted small theme-name">{theme}</span>
        </div>
        <div className="segmented small">
          {(["markdown", "html"] as const).map((f) => (
            <button key={f} className={format === f ? "on" : ""} onClick={() => setFormat(f)}>
              {f === "markdown" ? "Markdown" : "HTML"}
            </button>
          ))}
        </div>
      </div>
      <div className="snippet">
        <code>{snippet}</code>
        <button className="btn" onClick={copy}>
          {copied ? "Copied ✓" : "Copy"}
        </button>
      </div>
      <p className="muted small">
        Paste into the README of a repository named <code>{login}/{login}</code> to show it on your profile.
      </p>
    </div>
  );
}