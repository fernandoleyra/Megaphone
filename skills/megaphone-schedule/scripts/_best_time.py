"""Best-time-to-post recommendations.

Two layers of intelligence (in priority order):

1. **User's own history** — if the repo has `.megaphone/published/*.jsonl` with
   engagement annotations (added by `megaphone-digest`), we surface the
   actually-best windows from that data. Highest-confidence answer.

2. **2026 industry research baseline** — per-platform best windows pulled from
   the research in `references/best-time-data.md`. Lower confidence but works
   on day one with no history.

Audience tuning: an audience hint (`indie-dev`, `b2b`, `general`) shifts the
recommendation. `indie-dev` skews earlier in the week and earlier in the
morning ET; `b2b` favors midweek midmornings; `general` uses the platform
default.

This module returns a recommendation, not a hard answer. Always label it with
the source ("based on industry research" vs "based on your own posts")."""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Optional

# Per-platform default windows (24h ET, Tue–Thu unless noted)
# Each tuple is (day-of-week-name, hour, minute, label)
_DEFAULT_WINDOWS = {
    "bluesky":  [("Tue", 9, 0,  "Tue 9:00 ET"),  ("Wed", 9, 0, "Wed 9:00 ET"),  ("Thu", 9, 0, "Thu 9:00 ET")],
    "linkedin": [("Wed", 10, 0, "Wed 10:00 ET"), ("Tue", 10, 0,"Tue 10:00 ET"), ("Thu", 10, 0,"Thu 10:00 ET")],
    "devto":    [("Tue", 8, 0,  "Tue 8:00 ET"),  ("Thu", 8, 0, "Thu 8:00 ET")],
    "reddit":   [("Tue", 7, 0,  "Tue 7:00 ET"),  ("Wed", 7, 0, "Wed 7:00 ET"),  ("Thu", 7, 0, "Thu 7:00 ET")],
    "mastodon": [("Tue", 9, 30, "Tue 9:30 ET"),  ("Thu", 9, 30,"Thu 9:30 ET")],
    "x":        [("Tue", 8, 0,  "Tue 8:00 ET"),  ("Wed", 8, 0, "Wed 8:00 ET"),  ("Thu", 8, 0, "Thu 8:00 ET")],
    "hashnode": [("Tue", 10, 0, "Tue 10:00 ET"), ("Thu", 10, 0,"Thu 10:00 ET")],
}

_AUDIENCE_SHIFT = {
    "indie-dev": -1,    # one hour earlier — devs are at their desks earlier
    "b2b":       0,
    "general":   1,     # one hour later — broader audience peaks midmorning
}

_DOW_NAME_TO_NUM = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def suggest(
    platform: str,
    *,
    audience: str = "indie-dev",
    now: Optional[_dt.datetime] = None,
    history_dir: Optional[Path] = None,
) -> dict:
    """Return {when_iso, label, source, confidence} for the next best post time."""
    now = now or _dt.datetime.now().astimezone()
    platform = platform.lower()

    user_pick = _from_history(platform, history_dir) if history_dir else None
    if user_pick:
        target = _next_match(now, user_pick["dow"], user_pick["hour"], user_pick["minute"])
        return {
            "when_iso": target.isoformat(),
            "label": user_pick["label"],
            "source": f"your own past {platform} engagement",
            "confidence": "high",
        }

    windows = _DEFAULT_WINDOWS.get(platform)
    if not windows:
        return {
            "when_iso": (now + _dt.timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
            "label": f"Tomorrow 10:00 (no specific data for {platform})",
            "source": "fallback",
            "confidence": "low",
        }

    shift = _AUDIENCE_SHIFT.get(audience, 0)
    candidates = []
    for dow_name, h, m, label in windows:
        target = _next_match(now, _DOW_NAME_TO_NUM[dow_name], h + shift, m)
        candidates.append((target, label))
    target, label = min(candidates, key=lambda c: c[0])
    return {
        "when_iso": target.isoformat(),
        "label": label,
        "source": f"2026 industry research for {platform}",
        "confidence": "medium",
    }


def _next_match(now: _dt.datetime, dow: int, hour: int, minute: int) -> _dt.datetime:
    """Return the next datetime > now where weekday() == dow at hour:minute."""
    days_ahead = (dow - now.weekday()) % 7
    candidate = (now + _dt.timedelta(days=days_ahead)).replace(
        hour=hour % 24, minute=minute, second=0, microsecond=0
    )
    if candidate <= now:
        candidate = candidate + _dt.timedelta(days=7)
    return candidate


def _from_history(platform: str, history_dir: Path) -> Optional[dict]:
    """If we have engagement-annotated history, return the median best window.

    Expected format in published/*.jsonl: each line is the publish record.
    Optional `engagement` field with `views`, `likes`, etc. is added later
    by megaphone-digest. We only consider posts with `ok: true` and an
    `engagement.score` field."""
    if not history_dir or not history_dir.exists():
        return None
    rows = []
    for jsonl in sorted(history_dir.glob("*.jsonl")):
        for line in jsonl.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("platform") != platform:
                continue
            if not row.get("ok"):
                continue
            score = row.get("engagement", {}).get("score") if isinstance(row.get("engagement"), dict) else None
            if score is None:
                continue
            try:
                ts = _dt.datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            rows.append((ts.astimezone(), score))
    if len(rows) < 5:
        return None  # not enough signal yet
    # Group by (dow, hour) and average the score.
    buckets: dict[tuple[int, int], list[float]] = {}
    for ts, score in rows:
        buckets.setdefault((ts.weekday(), ts.hour), []).append(score)
    best = max(buckets.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
    (dow, hour), scores = best
    return {
        "dow": dow,
        "hour": hour,
        "minute": 0,
        "label": f"DOW {dow} at {hour:02d}:00 (your top window across {len(rows)} posts)",
    }
