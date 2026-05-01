"""Minimal 5-field cron parser + matcher + next-fire calculator.

Stdlib only. Handles the cron subset every shell user knows:

  field        allowed values
  -----        ---------------
  minute       0-59     * , - /
  hour         0-23     * , - /
  day-of-month 1-31     * , - /
  month        1-12     * , - /  (or jan,feb,…)
  day-of-week  0-7      * , - /  (0 and 7 = sunday; or sun,mon,…)

Examples:
    *  *  *  *  *           every minute
    0  10 *  *  5           Fridays at 10:00
    */15 *  *  *  *         every 15 minutes
    0  9  *  *  1-5         weekdays at 9:00
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import List, Optional

_MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_DOW_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronExpr:
    minute: List[int]
    hour: List[int]
    dom: List[int]
    month: List[int]
    dow: List[int]  # 0..6, sunday=0

    def matches(self, dt: _dt.datetime) -> bool:
        if dt.minute not in self.minute:
            return False
        if dt.hour not in self.hour:
            return False
        if dt.month not in self.month:
            return False
        # cron weirdness: when both dom and dow are restricted, posix cron uses
        # OR (either matches). We follow that.
        dom_ok = dt.day in self.dom
        dow_ok = (dt.weekday() + 1) % 7 in self.dow  # python weekday(): Mon=0; cron: sun=0
        # Default-restrictedness: a field is "restricted" if it's not the full set
        full_dom = set(range(1, 32))
        full_dow = set(range(0, 7))
        dom_restricted = set(self.dom) != full_dom
        dow_restricted = set(self.dow) != full_dow
        if dom_restricted and dow_restricted:
            if not (dom_ok or dow_ok):
                return False
        else:
            if dom_restricted and not dom_ok:
                return False
            if dow_restricted and not dow_ok:
                return False
        return True

    def next_fire(self, after: _dt.datetime, *, horizon_days: int = 366) -> Optional[_dt.datetime]:
        """Return the next datetime > `after` that matches this cron expression.

        Searches up to `horizon_days` days ahead and gives up if nothing matches
        (rare; only happens with impossible expressions like Feb 30)."""
        # Step minute-by-minute; for cron with sparse minutes we still finish
        # quickly because we increment to the next candidate minute set member.
        candidate = (after + _dt.timedelta(minutes=1)).replace(second=0, microsecond=0)
        end = after + _dt.timedelta(days=horizon_days)
        # Sort minute set for fast skipping.
        minutes_sorted = sorted(self.minute)
        while candidate <= end:
            if self.matches(candidate):
                return candidate
            # Skip to next valid minute in the same hour, else next hour.
            next_min = next((m for m in minutes_sorted if m > candidate.minute), None)
            if next_min is not None:
                candidate = candidate.replace(minute=next_min)
            else:
                candidate = (candidate + _dt.timedelta(hours=1)).replace(minute=minutes_sorted[0])
        return None


def parse(expr: str) -> CronExpr:
    parts = expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Cron expression must have 5 fields, got {len(parts)}: {expr!r}")
    minute, hour, dom, month, dow = parts
    return CronExpr(
        minute=_field(minute, 0, 59),
        hour=_field(hour, 0, 23),
        dom=_field(dom, 1, 31),
        month=_field(month, 1, 12, names=_MONTH_NAMES),
        dow=_field(_normalize_dow(dow), 0, 6, names=_DOW_NAMES),
    )


def _normalize_dow(value: str) -> str:
    """Cron allows 0 and 7 to mean Sunday. Map 7 → 0 before parsing."""
    out = []
    for tok in value.split(","):
        out.append(tok.replace("7", "0") if tok.strip() in ("7",) else tok)
    return ",".join(out)


def _field(value: str, lo: int, hi: int, *, names: Optional[dict] = None) -> List[int]:
    out: set[int] = set()
    for token in value.split(","):
        token = token.strip().lower()
        if not token:
            raise ValueError(f"Empty subfield in cron value: {value!r}")
        step = 1
        if "/" in token:
            base, step_str = token.split("/", 1)
            try:
                step = int(step_str)
            except ValueError:
                raise ValueError(f"Bad step in cron token {token!r}")
            token = base or "*"
        if token == "*":
            start, end = lo, hi
        elif "-" in token:
            a, b = token.split("-", 1)
            start = _resolve_one(a, lo, hi, names)
            end = _resolve_one(b, lo, hi, names)
        else:
            v = _resolve_one(token, lo, hi, names)
            start = end = v
        if start > end:
            raise ValueError(f"Range start > end in cron token {token!r}")
        for v in range(start, end + 1, step):
            if v < lo or v > hi:
                raise ValueError(f"Cron value {v} out of range [{lo},{hi}] in {value!r}")
            out.add(v)
    return sorted(out)


def _resolve_one(token: str, lo: int, hi: int, names: Optional[dict]) -> int:
    token = token.strip().lower()
    if names and token in names:
        return names[token]
    try:
        v = int(token)
    except ValueError:
        raise ValueError(f"Bad cron token {token!r}")
    if v < lo or v > hi:
        raise ValueError(f"Value {v} out of range [{lo},{hi}]")
    return v
