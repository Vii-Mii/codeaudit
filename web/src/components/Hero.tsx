import { useState } from "react";
import { cardUrl, type CardTheme } from "../api";
import { LARGE_COMMIT_LINES, LINKS, getRecent, num } from "../lib";
import { ExternalLink, GitHubIcon, HeartIcon } from "./Icons";
import { SearchForm } from "./SearchForm";

const EXAMPLES = ["torvalds", "gaearon", "sindresorhus", "tiangolo"];

const FEATURES = [
  {
    title: "Real line counts",
    body: "Lines added, deleted and net across every repository you pushed to, not just commit counts.",
  },
  {
    title: "Focused filters",
    body: "Slice by period, repository and language, and skip bulk commits like lockfiles or vendored code.",
  },
  {
    title: "A card worth showing",
    body: "A clean SVG card for your GitHub profile README, in five themes, refreshed automatically.",
  },
];

const STEPS = [
  {
    title: "Enter a username",
    body: "Type any GitHub login. No sign-in, no tokens, nothing to install.",
  },
  {
    title: "Slice the data",
    body: "Pick a period, narrow to repositories or languages, and skip bulk commits.",
  },
  {
    title: "Share the card",
    body: "Copy a Markdown or HTML snippet and paste it into your profile README.",
  },
];

const CAPABILITIES = [
  { title: "Lines added and deleted", body: "Totals and net change, with exact numbers on hover." },
  { title: "Activity heatmap", body: "Every day in your range, shaded by how many lines changed." },
  { title: "Streaks", body: "Longest and current streaks, plus your single biggest day." },
  { title: "Language mix", body: "Where your changes actually land, as a share of lines." },
  { title: "Weekly rhythm", body: "Which day of the week you write the most code." },
  { title: "Export", body: "Download the daily numbers as CSV or JSON." },
];

const FAQ = [
  {
    q: "Do I need to sign in?",
    a: "No. Enter a username and the stats load straight away. There is nothing to connect.",
  },
  {
    q: "What gets counted?",
    a: "Public contributions on default branches. Line counts are per-commit totals from the GitHub API, so file-level exclusions are not applied.",
  },
  {
    q: "Are private repositories included?",
    a: "No. Only public contributions are counted.",
  },
  {
    q: "What does “skip bulk commits” do?",
    a: `It leaves out commits over ${num(LARGE_COMMIT_LINES)} changed lines, which are usually generated files, vendored code or lockfile changes.`,
  },
  {
    q: "Are lines of code a good measure of a developer?",
    a: "No. They measure activity, not productivity or quality. Treat the numbers as a mirror, not a scoreboard.",
  },
  {
    q: "Is it free?",
    a: "Yes, and it is open source under the Apache-2.0 license.",
  },
];

function CardPreview({ login, theme }: { login: string; theme: CardTheme }) {
  const [failed, setFailed] = useState(false);
  return (
    <figure className="preview">
      {failed ? (
        <p className="muted small">Preview unavailable right now.</p>
      ) : (
        <img
          src={cardUrl(login, theme)}
          alt={`${theme} CodeAudit card for ${login}`}
          width={480}
          loading="lazy"
          onError={() => setFailed(true)}
        />
      )}
      <figcaption className="preview-label">{theme}</figcaption>
    </figure>
  );
}

export function Hero({ onSearch }: { onSearch: (login: string) => void }) {
  const recent = getRecent();
  const suggestions = recent.length ? recent : EXAMPLES;

  return (
    <>
      <section className="hero">
        <span className="eyebrow">Open source · Free forever</span>
        <h1>
          The code you ship,
          <br />
          <span className="gradient-text">at a glance.</span>
        </h1>
        <p className="lede">
          Lines written, languages, streaks and rhythm for any GitHub profile. No sign-up needed.
        </p>
        <SearchForm onSearch={onSearch} autoFocus />
        <div className="suggestions">
          <span className="muted">{recent.length ? "Recent" : "Try"}</span>
          {suggestions.map((login) => (
            <button key={login} className="chip" onClick={() => onSearch(login)}>
              {login}
            </button>
          ))}
        </div>

        <div className="features">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature">
              <h3>{f.title}</h3>
              <p className="muted">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <header className="section-head">
          <span className="section-eyebrow">How it works</span>
          <h2>From username to README in three steps.</h2>
        </header>
        <ol className="steps">
          {STEPS.map((s) => (
            <li key={s.title} className="step">
              <h3>{s.title}</h3>
              <p className="muted">{s.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="section">
        <header className="section-head">
          <span className="section-eyebrow">What you get</span>
          <h2>Everything about your output, nothing you have to configure.</h2>
        </header>
        <div className="caps">
          {CAPABILITIES.map((c) => (
            <div key={c.title} className="cap">
              <h3>{c.title}</h3>
              <p className="muted">{c.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <header className="section-head">
          <span className="section-eyebrow">README card</span>
          <h2>A small card that looks right on any profile.</h2>
          <p>Five themes, one line of Markdown. It stays current without you touching it.</p>
        </header>
        <div className="previews">
          <CardPreview login={EXAMPLES[0]} theme="ink" />
          <CardPreview login={EXAMPLES[0]} theme="carbon" />
        </div>
      </section>

      <section className="section">
        <header className="section-head">
          <span className="section-eyebrow">Questions</span>
          <h2>Good to know.</h2>
        </header>
        <div className="faq">
          {FAQ.map((item) => (
            <details key={item.q}>
              <summary>{item.q}</summary>
              <p>{item.a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="oss">
          <div className="oss-text">
            <span className="section-eyebrow">Open source</span>
            <h2>Built in the open.</h2>
            <p className="muted">
              Free and licensed under <ExternalLink href={LINKS.license}>Apache-2.0</ExternalLink>. Read the code,
              self-host it, or help shape what comes next.
            </p>
          </div>
          <div className="oss-actions">
            <ExternalLink className="btn btn-primary" href={LINKS.repo}>
              <GitHubIcon />
              Star on GitHub
            </ExternalLink>
            <ExternalLink className="btn" href={LINKS.contribute}>
              Contribute
            </ExternalLink>
            <ExternalLink className="btn" href={LINKS.issues}>
              Open issues
            </ExternalLink>
            <ExternalLink className="btn btn-support" href={LINKS.sponsor}>
              <HeartIcon />
              Support
            </ExternalLink>
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>
          Audit your own code<span className="gradient-text">.</span>
        </h2>
        <p className="muted">Enter a GitHub username and see the last year in a few seconds.</p>
        <button className="btn btn-primary" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          Search a profile ↑
        </button>
      </section>
    </>
  );
}