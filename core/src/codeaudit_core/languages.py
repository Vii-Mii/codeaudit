from __future__ import annotations

from pathlib import PurePosixPath

_BY_EXTENSION = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".sh": "Shell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".md": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
}

_BY_NAME = {"Dockerfile": "Dockerfile", "Makefile": "Makefile"}


def detect_language(path: str) -> str:
    p = PurePosixPath(path)
    return _BY_NAME.get(p.name) or _BY_EXTENSION.get(p.suffix.lower(), "Other")
