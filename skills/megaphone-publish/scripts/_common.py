"""Shared helpers used by the dispatcher, auth helper, and connectors.

Stdlib only — no external dependencies. Keep it that way; this skill must
work on any machine with a recent Python 3."""

from __future__ import annotations

import json
import os
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CRED_DIR = Path(os.path.expanduser("~/.megaphone/credentials"))
USER_STATE_DIR = Path(os.path.expanduser("~/.megaphone"))


def repo_megaphone_dir() -> Path:
    """The .megaphone/ directory in the current repo (cwd)."""
    return Path.cwd() / ".megaphone"


def published_log_path(date: str) -> Path:
    p = repo_megaphone_dir() / "published"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{date}.jsonl"


# ---------------------------------------------------------------------------
# Credential vault — JSON files at ~/.megaphone/credentials/<platform>.json,
# chmod 0600. Not encrypted; this matches what gh/aws/etc. ship by default
# and avoids forcing a passphrase on the user. v2 may add OS-keychain.
# ---------------------------------------------------------------------------

def _ensure_secure_dir(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    try:
        d.chmod(0o700)
    except (OSError, PermissionError):
        pass  # Windows / network drive — best effort only.


def cred_path(platform: str) -> Path:
    _ensure_secure_dir(CRED_DIR)
    return CRED_DIR / f"{platform}.json"


def load_credentials(platform: str) -> Optional[dict]:
    p = cred_path(platform)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def save_credentials(platform: str, data: dict) -> None:
    p = cred_path(platform)
    p.write_text(json.dumps(data, indent=2))
    try:
        p.chmod(0o600)
    except (OSError, PermissionError):
        pass


def delete_credentials(platform: str) -> bool:
    p = cred_path(platform)
    if p.exists():
        p.unlink()
        return True
    return False


# ---------------------------------------------------------------------------
# Per-repo overrides — .megaphone/overrides/<platform>.json
# ---------------------------------------------------------------------------

def load_overrides(platform: str) -> dict:
    p = repo_megaphone_dir() / "overrides" / f"{platform}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        # Surface the error so the dispatcher can refuse rather than silently ignoring.
        raise ValueError(f"Override file {p} is not valid JSON: {e}")


# ---------------------------------------------------------------------------
# Connector result type
# ---------------------------------------------------------------------------

@dataclass
class PostResult:
    ok: bool
    url: Optional[str] = None
    error_type: Optional[str] = None  # 'refresh_token' | 'bad_body' | 'rate_limit' | 'auth_error' | 'network' | 'unknown'
    error_message: Optional[str] = None
    retry_after: Optional[int] = None  # seconds, if rate_limit
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "url": self.url,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "retry_after": self.retry_after,
        }


# ---------------------------------------------------------------------------
# Draft loading — strip the comment header that megaphone-post writes,
# leaving the actual post body.
# ---------------------------------------------------------------------------

def load_draft(file_path: str) -> str:
    """Load a draft body, stripping the optional megaphone-post comment header.

    To get YAML frontmatter for platforms that need it (title, tags,
    subreddit), use load_draft_with_meta instead."""
    body, _ = load_draft_with_meta(file_path)
    return body


def load_draft_with_meta(file_path: str) -> tuple[str, dict]:
    """Returns (body, metadata).

    Metadata is parsed from a YAML-ish frontmatter block at the top of the
    file (between two `---` lines). The parser handles the small subset of
    YAML used in practice: flat key:value, lists with `[a, b]`, and quoted
    strings. We avoid pulling in pyyaml to keep the skill stdlib-only."""
    text = Path(file_path).read_text()

    # Drop leading HTML comment header (megaphone-post writes one) AND blanks.
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "":
            i += 1
            continue
        if s.startswith("<!--") and s.endswith("-->"):
            i += 1
            continue
        break

    meta: dict = {}
    # Frontmatter?
    if i < len(lines) and lines[i].strip() == "---":
        j = i + 1
        while j < len(lines) and lines[j].strip() != "---":
            j += 1
        if j < len(lines):
            for raw in lines[i + 1 : j]:
                if ":" not in raw:
                    continue
                key, _, value = raw.partition(":")
                meta[key.strip()] = _coerce(value.strip())
            i = j + 1

    body = "\n".join(lines[i:]).strip()
    return body, meta


def _coerce(value: str):
    if not value:
        return ""
    # List form: [a, b, "c d"]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        parts = []
        for part in _split_top_level(inner, ","):
            part = part.strip()
            if part.startswith('"') and part.endswith('"'):
                part = part[1:-1]
            elif part.startswith("'") and part.endswith("'"):
                part = part[1:-1]
            parts.append(part)
        return [p for p in parts if p]
    # Quoted string
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    # Booleans / numbers / fallthrough
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _split_top_level(s: str, sep: str) -> list[str]:
    out, buf, depth = [], [], 0
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


# ---------------------------------------------------------------------------
# Tiny output helpers (so output formatting is consistent across scripts)
# ---------------------------------------------------------------------------

def emit(obj: Any) -> None:
    """Print a JSON line for machine-readable output."""
    print(json.dumps(obj, ensure_ascii=False))


def info(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)
