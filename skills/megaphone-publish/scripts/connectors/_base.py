"""Connector interface.

Each connector module exports:
  - publish(draft: str, credentials: dict, overrides: dict) -> PostResult
  - connect(prompt: callable) -> dict   # interactive auth, returns creds dict

Optional:
  - refresh(credentials: dict) -> dict | None
        Return updated creds on success, None if user must re-auth.

The dispatcher imports connectors by name at runtime."""

from __future__ import annotations

import os
import sys

# Make the parent scripts/ directory importable regardless of how Python was
# invoked.  This lets connector modules just `from _common import ...`.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from _common import PostResult  # noqa: E402,F401  (used by connectors)


def stdin_prompt(question: str, *, secret: bool = False) -> str:
    """Prompt the user from a script. Used by `connect()` flows."""
    if secret:
        try:
            import getpass

            return getpass.getpass(question).strip()
        except Exception:
            pass
    return input(question).strip()
