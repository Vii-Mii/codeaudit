from __future__ import annotations

import re
from collections.abc import Mapping

_NOREPLY = re.compile(r"^(?:\d+\+)?(?P<login>[^@]+)@users\.noreply\.github\.com$", re.IGNORECASE)


class IdentityResolver:
    """Maps a commit author to a stable developer id, or None for bots."""

    def __init__(self, aliases: Mapping[str, str] | None = None) -> None:
        # Keys are lowercase emails; values are the canonical developer id.
        self._aliases = {k.lower(): v for k, v in (aliases or {}).items()}

    def resolve(self, name: str, email: str) -> str | None:
        email = email.strip().lower()
        if "[bot]" in name.lower() or "[bot]" in email:
            return None
        if email in self._aliases:
            return self._aliases[email]
        match = _NOREPLY.match(email)
        if match:
            return match.group("login").lower()
        return email or name.strip().lower()
