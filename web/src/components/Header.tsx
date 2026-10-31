import { LINKS, REPO } from "../lib";
import { ExternalLink, GitHubIcon, HeartIcon, StarIcon } from "./Icons";
import { SearchForm } from "./SearchForm";

interface Props {
  login: string;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onHome: () => void;
  onSearch: (login: string) => void;
}

export function Header({ login, theme, onToggleTheme, onHome, onSearch }: Props) {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <button className="brand" onClick={onHome} aria-label="Home">
          <span className="brand-mark" aria-hidden />
          codeaudit
        </button>
        {login && <SearchForm key={login} onSearch={onSearch} initial={login} size="sm" />}
        <div className="topbar-actions">
          <ExternalLink className="gh-link" href={LINKS.repo} title={`Star ${REPO} on GitHub`}>
            <GitHubIcon />
            <span className="gh-name">{REPO}</span>
            <span className="gh-star">
              <StarIcon />
              Star
            </span>
          </ExternalLink>
          <ExternalLink className="btn btn-support" href={LINKS.sponsor} title="Support codeaudit">
            <HeartIcon />
            <span className="support-label">Support</span>
          </ExternalLink>
          <button
            className="icon-btn"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            title="Toggle theme"
          >
            {theme === "dark" ? "☀" : "☾"}
          </button>
        </div>
      </div>
    </header>
  );
}
