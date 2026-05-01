"""Natural-language time parsing for megaphone-schedule's --at flag.

Supports:
  - ISO 8601 with timezone: 2026-05-01T10:00-07:00
  - ISO 8601 naive (treated as local): 2026-05-01T10:00
  - "today" / "tomorrow" optionally with "at HH[:MM][am|pm]"
  - "monday".."sunday" / "next monday" — next occurrence
  - "in N (minute|hour|day|week)s"
  - Bare "10am", "10:30pm", "14:00" — today if still future, else tomorrow

Returns a timezone-aware datetime in the user's local zone. Naive inputs
are localized to the system's tzinfo via astimezone()."""

from __future__ import annotations

import datetime as _dt
import re
from typing import Optional


_DOW = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6}


def parse_when(text: str, *, now: Optional[_dt.datetime] = None) -> _dt.datetime:
    s = text.strip().lower()
    if not s:
        raise ValueError("Empty time expression.")
    now = now or _dt.datetime.now().astimezone()

    # ISO first
    iso = _try_iso(text)
    if iso is not None:
        return _ensure_tz(iso, now.tzinfo)

    # "in N <unit>"
    m = re.match(r"in\s+(\d+)\s+(minute|min|hour|hr|day|week)s?$", s)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        delta = {
            "minute": _dt.timedelta(minutes=n),
            "min": _dt.timedelta(minutes=n),
            "hour": _dt.timedelta(hours=n),
            "hr": _dt.timedelta(hours=n),
            "day": _dt.timedelta(days=n),
            "week": _dt.timedelta(weeks=n),
        }[unit]
        return now + delta

    # "today" / "tomorrow" [at] [TIME]
    m = re.match(r"(today|tomorrow)(?:\s+(?:at\s+)?(.+))?$", s)
    if m:
        base = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if m.group(1) == "tomorrow":
            base = base + _dt.timedelta(days=1)
        if m.group(2):
            base = _apply_time(base, m.group(2))
        return base

    # "[next] <weekday>" [at] [TIME]
    m = re.match(r"(?:(next)\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s+(?:at\s+)?(.+))?$", s)
    if m:
        target_dow = _DOW[m.group(2)]
        days_ahead = (target_dow - now.weekday()) % 7
        if days_ahead == 0 and m.group(1) == "next":
            days_ahead = 7
        elif days_ahead == 0:
            days_ahead = 7  # always interpret "monday" as the next monday, not today
        base = (now + _dt.timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
        if m.group(3):
            base = _apply_time(base, m.group(3))
        return base

    # Bare time → today (or tomorrow if past)
    try:
        base = _apply_time(now.replace(second=0, microsecond=0), s)
        if base <= now:
            base = base + _dt.timedelta(days=1)
        return base
    except ValueError:
        pass

    raise ValueError(f"Could not parse time expression: {text!r}")


def _apply_time(base: _dt.datetime, time_text: str) -> _dt.datetime:
    """Replace base's H:M with parsed time."""
    s = time_text.strip().lower().replace(" ", "")
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?(am|pm)?$", s)
    if not m:
        raise ValueError(f"Could not parse time fragment: {time_text!r}")
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    suffix = m.group(3)
    if suffix == "pm" and hour < 12:
        hour += 12
    if suffix == "am" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Time out of range: {time_text!r}")
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _try_iso(text: str) -> Optional[_dt.datetime]:
    try:
        return _dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def _ensure_tz(dt: _dt.datetime, tz) -> _dt.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz) if tz else dt.astimezone()
    return dt
