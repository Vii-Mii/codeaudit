# CodeAudit

Open-source measurement of the code written by a GitHub user or organisation: lines added,
deleted and net, broken down by developer, language, repository and time.

> Lines of code measure activity, not productivity or quality. See [docs/METRICS.md](docs/METRICS.md).

## Layout

| Path | Purpose |
|---|---|
| `core/` | Pure-Python calculation engine (no web or DB dependency) |
| `api/` | FastAPI service |
| `web/` | React + Vite frontend |
| `docs/` | Metric specification and design notes |

## Develop

```bash
git clone https://github.com/Vii-Mii/codeaudit.git && cd codeaudit
python3 -m venv .venv && source .venv/bin/activate
pip install -e "core[dev]" -e "api[dev]"
pytest core api
uvicorn app.main:app --reload --app-dir api
```

Full stack (API, Postgres, Redis):

```bash
echo "CODEAUDIT_GITHUB_TOKEN=<fine-grained token, public read-only>" > .env
docker compose up --build
curl "http://localhost:8000/api/v1/users/<login>/stats?since=2026-01-01"
```

API docs are served at `http://localhost:8000/docs`.

Profile card for a GitHub README:

```markdown
[![CodeAudit stats](https://<api-host>/api/v1/users/<login>/card.svg?theme=carbon)](https://<web-host>/?u=<login>)
```
[![CodeAudit stats](https://codeaudit-api.onrender.com/api/v1/users/Vii-Mii/card.svg?theme=carbon)](https://codeaudit-omega.vercel.app/?u=Vii-Mii)

## Roadmap

1. Core engine and metric spec. Done.
2. API: public user stats via the GitHub API with caching. Done (in-memory cache).
   Next: Redis/Postgres persistence, background sync, per-IP rate limiting.
3. Web: minimal dashboard and shareable SVG profile card. Done.
4. GitHub OAuth, then a GitHub App for organisations.
5. Blame-based surviving lines, incremental sync, CLI and GitHub Action.

## License

Copyright 2026 [Vijayaraj](https://github.com/Vii-Mii).

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
