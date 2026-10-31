import { AUTHOR, LINKS, REPO } from "../lib";
import { ExternalLink, GitHubIcon, HeartIcon } from "./Icons";

const COLUMNS = [
  {
    title: "Project",
    links: [
      { label: "GitHub", href: LINKS.repo },
      { label: "Contribute", href: LINKS.contribute },
      { label: "License", href: LINKS.license },
    ],
  },
  {
    title: "Feedback",
    links: [
      { label: "Report a bug", href: LINKS.bug },
      { label: "Request a feature", href: LINKS.feature },
      { label: "Open issues", href: LINKS.issues },
    ],
  },
];

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-top">
        <div className="footer-brand">
          <span className="brand">
            <span className="brand-mark" aria-hidden />
            codeaudit
          </span>
          <p className="muted">The code you ship, at a glance. Free and open source.</p>
          <div className="footer-cta">
            <ExternalLink className="btn" href={LINKS.repo}>
              <GitHubIcon />
              {REPO}
            </ExternalLink>
            <ExternalLink className="btn btn-support" href={LINKS.sponsor}>
              <HeartIcon />
              Sponsor
            </ExternalLink>
          </div>
        </div>
        <nav className="footer-cols" aria-label="Footer">
          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h4>{col.title}</h4>
              <ul>
                {col.links.map((l) => (
                  <li key={l.label}>
                    <ExternalLink href={l.href}>{l.label}</ExternalLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </div>
      <div className="footer-bottom">
        <span>
          Built by <ExternalLink href={AUTHOR.url}>{AUTHOR.name}</ExternalLink> · open source under
          Apache-2.0
        </span>
        <span>Lines of code measure activity, not productivity or quality.</span>
      </div>
    </footer>
  );
}
