import { useState, type FormEvent } from "react";
import { GITHUB_LOGIN } from "../api";

interface Props {
  onSearch: (login: string) => void;
  initial?: string;
  size?: "lg" | "sm";
  autoFocus?: boolean;
}

export function SearchForm({ onSearch, initial = "", size = "lg", autoFocus }: Props) {
  const [value, setValue] = useState(initial);
  const [invalid, setInvalid] = useState(false);

  function submit(event: FormEvent) {
    event.preventDefault();
    const login = value.trim().replace(/^@/, "").replace(/^https?:\/\/github\.com\//, "");
    if (!GITHUB_LOGIN.test(login)) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    onSearch(login);
  }

  return (
    <form className={`search search-${size} ${invalid ? "invalid" : ""}`} onSubmit={submit}>
      <span className="search-prefix">github.com/</span>
      <input
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          setInvalid(false);
        }}
        placeholder="username"
        aria-label="GitHub username"
        aria-invalid={invalid}
        autoFocus={autoFocus}
        spellCheck={false}
        autoCapitalize="off"
        autoComplete="off"
      />
      <button className="btn btn-primary" type="submit">
        {size === "lg" ? "Analyze" : "Go"}
        <span aria-hidden>→</span>
      </button>
    </form>
  );
}
