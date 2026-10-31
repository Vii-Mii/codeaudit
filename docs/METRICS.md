# Metric specification

Every number the product shows must be explained here. Changing a rule is a breaking change
to published numbers and must be noted in the changelog.

## Definitions

- **Added / deleted**: line counts from `git log --numstat --no-renames`, per file per commit.
- **Net**: `added - deleted`.
- **Commits**: non-merge commits by a non-bot author, within the requested time range.
- **Attribution**: the commit author (not committer). The date is the author date.

## What is excluded

| Rule | Detail |
|---|---|
| Merge commits | Commits with more than one parent are skipped. |
| Bots | Author name or email containing `[bot]`. |
| Binary files | `numstat` reports `-`; the file is skipped. |
| Vendored directories | `node_modules`, `vendor`, `third_party`, `dist`, `build`, `.venv`, `venv`, `__pycache__`, `Pods`. |
| Lockfiles | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, `composer.lock`, `Pipfile.lock`. |
| Generated files | `*.min.js`, `*.min.css`, `*.map`, `*.pb.go`, `*_pb2.py`, `*_pb2_grpc.py`, `*.snap`. |
| User patterns | Extra glob patterns supplied by the caller. |

## Identity

1. Bots resolve to no identity and are dropped.
2. An explicit email alias map wins.
3. GitHub noreply addresses (`123+login@users.noreply.github.com`) resolve to `login`.
4. Otherwise the lowercased email is the developer id.

## Language

Detected from the file extension or well-known file name. Unknown files are `Other`.

## Modes

### Fast (hosted API, `mode: "fast"`)

Uses the GitHub GraphQL API without cloning.

- Repositories: those listed in the user's `contributionsCollection` for the range (up to 100),
  excluding forks. Only public contributions are visible to the server token.
- Commits: authored by the user on each repository's default branch, up to 1,000 per repository.
- Line counts are per-commit totals, so file-level exclusions (lockfiles, vendored, generated)
  cannot be applied. Numbers can be inflated by such files.
- Language is the repository's primary language, applied to the whole commit.
- Range is at most one year (a GitHub API limit).

### Accurate (local clone)

Uses `git log --numstat` on a clone and applies every rule on this page.

## Planned

- `Co-authored-by` trailer attribution.
- Surviving lines via `git blame` on the default branch.
- `.gitattributes` `linguist-generated` / `linguist-vendored` support.
- Fork-aware history so inherited commits are not credited to the forker.

## Limitations

Lines of code are a measure of activity, not productivity or quality. Do not use them to rank
or evaluate people.
