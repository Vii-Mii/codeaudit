# codeaudit-core

Pure-Python engine with no web or database dependency. It turns `git log --numstat` data
into per-author, per-language and per-day totals. See [docs/METRICS.md](../docs/METRICS.md)
for the exact rules.

```python
from codeaudit_core import analyze, read_repo

report = analyze(read_repo("/path/to/repo"))
print(report.total.added, report.by_author)
```
