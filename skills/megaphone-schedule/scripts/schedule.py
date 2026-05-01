#!/usr/bin/env python3
"""Megaphone scheduler.

Three models:
  - one-off:  add  --platform X --file F --at "..."
  - cadence:  add-cadence --cron "0 10 * * 5" --folder D --platform X
  - sequence: add-sequence --file launch.json

Subcommands:
  init                     Create .megaphone/schedule/ scaffolding.
  add                      Schedule a one-off post.
  add-cadence              Define a recurring cadence.
  pause-cadence <id>       Stop a cadence (keeps history).
  resume-cadence <id>      Re-enable a paused cadence.
  add-sequence             Import a launch sequence JSON.
  remove <id>              Cancel one queued item.
  remove-sequence <name>   Cancel everything from a sequence.
  list                     Pretty-print queue + cadences + sequences.
  next [duration]          Show items due in the next 1d / 7d / 30d.
  calendar                 ASCII week view, one row per day.
  suggest-time             Print recommended time for a platform.
  run-due                  Fire any items whose `at` has elapsed."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import _best_time  # noqa: E402
import _cron  # noqa: E402
import _when  # noqa: E402

PLUGIN_ROOT_HINT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(_HERE))
PUBLISH_SCRIPT = Path(PLUGIN_ROOT_HINT) / "skills" / "megaphone-publish" / "scripts" / "publish.py"

SUPPORTED_PLATFORMS = ("bluesky", "devto", "linkedin", "reddit", "mastodon", "x", "hashnode")


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def schedule_dir(cwd: Optional[str] = None) -> Path:
    base = Path(cwd or os.getcwd())
    return base / ".megaphone" / "schedule"


def queue_path(cwd: Optional[str] = None) -> Path:
    return schedule_dir(cwd) / "queue.json"


def cadences_path(cwd: Optional[str] = None) -> Path:
    return schedule_dir(cwd) / "cadences.json"


def sequences_dir(cwd: Optional[str] = None) -> Path:
    return schedule_dir(cwd) / "sequences"


def log_path(cwd: Optional[str] = None) -> Path:
    return schedule_dir(cwd) / "log.jsonl"


def published_dir(cwd: Optional[str] = None) -> Path:
    return Path(cwd or os.getcwd()) / ".megaphone" / "published"


def _read_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {p} is not valid JSON: {e}")


def _write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str))


def _append_log(cwd: Optional[str], record: dict) -> None:
    p = log_path(cwd)
    p.parent.mkdir(parents=True, exist_ok=True)
    record = dict(record, ts=_now().isoformat())
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _now() -> _dt.datetime:
    return _dt.datetime.now().astimezone()


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_init(args) -> None:
    sd = schedule_dir(args.cwd)
    sd.mkdir(parents=True, exist_ok=True)
    sequences_dir(args.cwd).mkdir(exist_ok=True)
    if not queue_path(args.cwd).exists():
        _write_json(queue_path(args.cwd), [])
    if not cadences_path(args.cwd).exists():
        _write_json(cadences_path(args.cwd), [])
    print(json.dumps({"ok": True, "schedule_dir": str(sd)}))


def cmd_add(args) -> None:
    if not args.file or not Path(args.file).exists():
        sys.exit(f"ERROR: --file {args.file!r} does not exist.")
    when = _when.parse_when(args.at)
    if when.tzinfo is None:
        when = when.astimezone()
    queue = _read_json(queue_path(args.cwd), [])
    item = {
        "id": _new_id(),
        "platform": args.platform,
        "file": args.file,
        "at": when.isoformat(),
        "status": "pending",
        "attempts": 0,
        "url": None,
        "error": None,
        "source": args.source or "manual",
        "created_at": _now().isoformat(),
        "completed_at": None,
    }
    queue.append(item)
    _write_json(queue_path(args.cwd), queue)
    _append_log(args.cwd, {"event": "add", "id": item["id"], "platform": args.platform, "at": item["at"]})
    print(json.dumps({"ok": True, "added": item}, indent=2))


def cmd_add_cadence(args) -> None:
    try:
        expr = _cron.parse(args.cron)
    except ValueError as e:
        sys.exit(f"ERROR: bad cron expression: {e}")
    folder = Path(args.folder)
    if not folder.exists():
        sys.exit(f"ERROR: --folder {args.folder!r} does not exist.")
    cadences = _read_json(cadences_path(args.cwd), [])
    next_fire = expr.next_fire(_now())
    cadence = {
        "id": _new_id(),
        "label": args.label or f"{args.platform} from {folder.name}",
        "cron": args.cron,
        "folder": str(folder),
        "platform": args.platform,
        "next_fire": next_fire.isoformat() if next_fire else None,
        "last_fire": None,
        "consumed": [],
        "paused": False,
        "created_at": _now().isoformat(),
    }
    cadences.append(cadence)
    _write_json(cadences_path(args.cwd), cadences)
    _append_log(args.cwd, {"event": "add-cadence", "id": cadence["id"], "label": cadence["label"]})
    print(json.dumps({"ok": True, "cadence": cadence}, indent=2))


def cmd_pause_cadence(args) -> None:
    cadences = _read_json(cadences_path(args.cwd), [])
    for c in cadences:
        if c["id"] == args.id:
            c["paused"] = True
    _write_json(cadences_path(args.cwd), cadences)
    print(json.dumps({"ok": True, "paused": args.id}))


def cmd_resume_cadence(args) -> None:
    cadences = _read_json(cadences_path(args.cwd), [])
    for c in cadences:
        if c["id"] == args.id:
            c["paused"] = False
            try:
                c["next_fire"] = _cron.parse(c["cron"]).next_fire(_now()).isoformat()
            except Exception:
                pass
    _write_json(cadences_path(args.cwd), cadences)
    print(json.dumps({"ok": True, "resumed": args.id}))


def cmd_add_sequence(args) -> None:
    src = Path(args.file)
    if not src.exists():
        sys.exit(f"ERROR: sequence file not found: {src}")
    spec = _read_json(src, None)
    if not isinstance(spec, dict) or "name" not in spec or "items" not in spec:
        sys.exit("ERROR: sequence JSON must have 'name' and 'items'.")
    anchor = _dt.date.fromisoformat(spec["anchor_date"])
    tzname = spec.get("timezone")
    items_added = []
    queue = _read_json(queue_path(args.cwd), [])
    for entry in spec["items"]:
        platform = entry["platform"]
        if platform not in SUPPORTED_PLATFORMS:
            sys.exit(f"ERROR: sequence item references unsupported platform '{platform}'.")
        h, _, mm = entry["offset"].partition(":")
        offset = _dt.timedelta(hours=int(h), minutes=int(mm or 0))
        when = _dt.datetime.combine(anchor, _dt.time(0, 0), tzinfo=_now().tzinfo) + offset
        item = {
            "id": _new_id(),
            "platform": platform,
            "file": entry["file"],
            "at": when.isoformat(),
            "status": "pending",
            "attempts": 0,
            "url": None,
            "error": None,
            "source": f"sequence:{spec['name']}",
            "created_at": _now().isoformat(),
            "completed_at": None,
        }
        queue.append(item)
        items_added.append(item)
    _write_json(queue_path(args.cwd), queue)
    saved = sequences_dir(args.cwd) / f"{spec['name']}.json"
    _write_json(saved, spec)
    _append_log(args.cwd, {"event": "add-sequence", "name": spec["name"], "count": len(items_added)})
    print(json.dumps({"ok": True, "name": spec["name"], "items_added": len(items_added)}, indent=2))


def cmd_remove(args) -> None:
    queue = _read_json(queue_path(args.cwd), [])
    found = None
    for item in queue:
        if item["id"] == args.id and item["status"] == "pending":
            item["status"] = "cancelled"
            item["completed_at"] = _now().isoformat()
            found = item
    _write_json(queue_path(args.cwd), queue)
    if found:
        _append_log(args.cwd, {"event": "remove", "id": args.id})
    print(json.dumps({"ok": found is not None, "id": args.id}))


def cmd_remove_sequence(args) -> None:
    queue = _read_json(queue_path(args.cwd), [])
    cancelled = 0
    for item in queue:
        if item.get("source") == f"sequence:{args.name}" and item["status"] == "pending":
            item["status"] = "cancelled"
            item["completed_at"] = _now().isoformat()
            cancelled += 1
    _write_json(queue_path(args.cwd), queue)
    _append_log(args.cwd, {"event": "remove-sequence", "name": args.name, "cancelled": cancelled})
    print(json.dumps({"ok": True, "name": args.name, "cancelled": cancelled}))


def cmd_list(args) -> None:
    queue = _read_json(queue_path(args.cwd), [])
    cadences = _read_json(cadences_path(args.cwd), [])
    pending = [q for q in queue if q["status"] == "pending"]
    pending.sort(key=lambda x: x["at"])
    print("=== Pending queue ===")
    if not pending:
        print("(none)")
    for q in pending:
        print(f"  [{q['id'][:8]}] {q['at']}  {q['platform']:10s}  {q['file']}  source={q['source']}")
    print()
    print("=== Cadences ===")
    if not cadences:
        print("(none)")
    for c in cadences:
        flag = " (paused)" if c.get("paused") else ""
        print(f"  [{c['id'][:8]}] {c['cron']}  {c['platform']:10s}  {c['folder']}  next={c.get('next_fire')}{flag}")


def cmd_next(args) -> None:
    days = _parse_duration_days(args.duration)
    queue = _read_json(queue_path(args.cwd), [])
    cadences = _read_json(cadences_path(args.cwd), [])
    cutoff = _now() + _dt.timedelta(days=days)
    upcoming = []
    for q in queue:
        if q["status"] != "pending":
            continue
        try:
            at = _dt.datetime.fromisoformat(q["at"])
        except ValueError:
            continue
        if at <= cutoff:
            upcoming.append(("queue", at, q))
    for c in cadences:
        if c.get("paused") or not c.get("next_fire"):
            continue
        try:
            nf = _dt.datetime.fromisoformat(c["next_fire"])
        except ValueError:
            continue
        # Project the next few cadence fires within the window.
        expr = _cron.parse(c["cron"])
        cur = nf
        while cur <= cutoff and cur <= _now() + _dt.timedelta(days=days):
            upcoming.append(("cadence", cur, c))
            nxt = expr.next_fire(cur)
            if not nxt or nxt == cur:
                break
            cur = nxt
    upcoming.sort(key=lambda x: x[1])
    print(f"=== Next {days} day(s) ===")
    if not upcoming:
        print("(nothing scheduled)")
    for kind, when, item in upcoming:
        if kind == "queue":
            print(f"  {when.isoformat()}  [{item['id'][:8]}] {item['platform']:10s} {item['file']}")
        else:
            print(f"  {when.isoformat()}  [cadence {item['id'][:8]}] {item['platform']:10s} {item['folder']}")


def cmd_calendar(args) -> None:
    queue = _read_json(queue_path(args.cwd), [])
    today = _now().date()
    print(f"=== 7-day calendar from {today.isoformat()} ===")
    for d in range(7):
        day = today + _dt.timedelta(days=d)
        items = []
        for q in queue:
            if q["status"] != "pending":
                continue
            try:
                at = _dt.datetime.fromisoformat(q["at"])
            except ValueError:
                continue
            if at.date() == day:
                items.append((at, q))
        items.sort(key=lambda x: x[0])
        line = f"  {day.strftime('%a %m-%d')}  "
        if not items:
            line += "—"
        else:
            line += "  ".join(f"{at.strftime('%H:%M')} {q['platform']}" for at, q in items)
        print(line)


def cmd_suggest_time(args) -> None:
    rec = _best_time.suggest(
        args.platform,
        audience=args.audience,
        history_dir=published_dir(args.cwd),
    )
    print(json.dumps(rec, indent=2))


def cmd_run_due(args) -> None:
    """Fire cadences and queue items whose time has come.

    Catch-up policy: if a cadence missed multiple fires (e.g. laptop offline
    for 3 days), only the most recent missed fire is generated, then
    next_fire is advanced to the next future slot. This avoids the
    'apologize-then-spam' anti-pattern."""
    cwd = args.cwd
    fired_summary = {"cadence_fires": 0, "queue_attempts": 0, "queue_published": 0, "queue_failed": 0}
    now = _now()

    # 1. Cadences → generate queue items.
    cadences = _read_json(cadences_path(cwd), [])
    queue = _read_json(queue_path(cwd), [])
    for c in cadences:
        if c.get("paused"):
            continue
        nf_raw = c.get("next_fire")
        if not nf_raw:
            continue
        try:
            nf = _dt.datetime.fromisoformat(nf_raw)
        except ValueError:
            continue
        if nf > now:
            continue  # not due yet
        # Catch-up: jump to the most recent missed fire only.
        expr = _cron.parse(c["cron"])
        latest_missed = nf
        cur = nf
        while True:
            nxt = expr.next_fire(cur)
            if not nxt or nxt > now:
                break
            latest_missed = nxt
            cur = nxt
        # Pop next unconsumed file from cadence folder.
        candidate_file = _next_unconsumed_file(c)
        if candidate_file is not None:
            queue.append({
                "id": _new_id(),
                "platform": c["platform"],
                "file": str(candidate_file),
                "at": latest_missed.isoformat(),
                "status": "pending",
                "attempts": 0,
                "url": None,
                "error": None,
                "source": f"cadence:{c['id']}",
                "created_at": now.isoformat(),
                "completed_at": None,
            })
            c["consumed"].append(str(candidate_file))
            fired_summary["cadence_fires"] += 1
        c["last_fire"] = latest_missed.isoformat()
        next_fire = expr.next_fire(now)
        c["next_fire"] = next_fire.isoformat() if next_fire else None
    _write_json(cadences_path(cwd), cadences)

    # 2. Queue → publish items whose `at` ≤ now.
    for item in queue:
        if item["status"] != "pending":
            continue
        try:
            at = _dt.datetime.fromisoformat(item["at"])
        except ValueError:
            item["status"] = "failed"
            item["error"] = "bad timestamp"
            item["completed_at"] = now.isoformat()
            fired_summary["queue_failed"] += 1
            continue
        if at > now:
            continue
        if not Path(item["file"]).exists():
            item["status"] = "failed"
            item["error"] = f"draft file missing: {item['file']}"
            item["completed_at"] = now.isoformat()
            fired_summary["queue_failed"] += 1
            continue
        fired_summary["queue_attempts"] += 1
        result = _invoke_publish(item["platform"], item["file"])
        item["attempts"] += 1
        if result["ok"]:
            item["status"] = "done"
            item["url"] = result.get("url")
            item["completed_at"] = now.isoformat()
            fired_summary["queue_published"] += 1
        else:
            err_type = result.get("error_type")
            if err_type == "rate_limit" and item["attempts"] < 4:
                # Push out by retry_after (capped) and try next pass.
                wait = min(int(result.get("retry_after") or 60), 60 * 60)
                item["at"] = (now + _dt.timedelta(seconds=wait)).isoformat()
                # status stays pending; we'll get it next run.
            elif err_type in ("network", "unknown") and item["attempts"] < 4:
                # Exponential backoff: 5min × 2^(attempts-1), capped at 6h.
                backoff_min = min(5 * (2 ** (item["attempts"] - 1)), 360)
                item["at"] = (now + _dt.timedelta(minutes=backoff_min)).isoformat()
            else:
                item["status"] = "failed"
                item["error"] = f"{err_type}: {result.get('error_message', '')[:200]}"
                item["completed_at"] = now.isoformat()
                fired_summary["queue_failed"] += 1
            _append_log(cwd, {"event": "publish_failed", "id": item["id"], "error": item.get("error")})
    _write_json(queue_path(cwd), queue)
    print(json.dumps({"ok": True, "summary": fired_summary, "as_of": now.isoformat()}))


def _next_unconsumed_file(cadence: dict) -> Optional[Path]:
    folder = Path(cadence["folder"])
    if not folder.exists():
        return None
    consumed = set(cadence.get("consumed", []))
    candidates = sorted(p for p in folder.glob("*.md") if str(p) not in consumed and p.is_file())
    return candidates[0] if candidates else None


def _invoke_publish(platform: str, file: str) -> dict:
    """Run megaphone-publish/publish.py and return a parsed result dict.

    The publish script prints one JSON line on stdout (the publish record).
    We capture and parse it; on parse failure, treat as unknown error."""
    if platform not in SUPPORTED_PLATFORMS:
        return {"ok": False, "error_type": "unknown", "error_message": f"unsupported platform '{platform}'"}
    if not PUBLISH_SCRIPT.exists():
        return {"ok": False, "error_type": "unknown", "error_message": f"publish.py not found at {PUBLISH_SCRIPT}"}
    try:
        proc = subprocess.run(
            [sys.executable, str(PUBLISH_SCRIPT), "--platform", platform, "--file", file],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error_type": "network", "error_message": "publish.py timed out"}
    out = (proc.stdout or "").strip().splitlines()
    last = out[-1] if out else ""
    try:
        return json.loads(last)
    except json.JSONDecodeError:
        return {"ok": False, "error_type": "unknown", "error_message": (proc.stderr or last)[:300]}


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------

def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _parse_duration_days(s: str) -> int:
    s = (s or "7d").strip().lower()
    if s.endswith("d"):
        return int(s[:-1])
    if s.endswith("w"):
        return int(s[:-1]) * 7
    return int(s)


def main() -> None:
    p = argparse.ArgumentParser(description="Megaphone scheduler")
    p.add_argument("--cwd", help="Repo path to operate on (default: current dir)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    a = sub.add_parser("add")
    a.add_argument("--platform", required=True, choices=SUPPORTED_PLATFORMS)
    a.add_argument("--file", required=True)
    a.add_argument("--at", required=True, help="ISO timestamp or natural ('tomorrow 10am')")
    a.add_argument("--source", default="manual")
    a.set_defaults(func=cmd_add)

    ac = sub.add_parser("add-cadence")
    ac.add_argument("--cron", required=True)
    ac.add_argument("--folder", required=True)
    ac.add_argument("--platform", required=True, choices=SUPPORTED_PLATFORMS)
    ac.add_argument("--label")
    ac.set_defaults(func=cmd_add_cadence)

    pc = sub.add_parser("pause-cadence")
    pc.add_argument("id")
    pc.set_defaults(func=cmd_pause_cadence)

    rc = sub.add_parser("resume-cadence")
    rc.add_argument("id")
    rc.set_defaults(func=cmd_resume_cadence)

    seq = sub.add_parser("add-sequence")
    seq.add_argument("--file", required=True)
    seq.set_defaults(func=cmd_add_sequence)

    rm = sub.add_parser("remove")
    rm.add_argument("id")
    rm.set_defaults(func=cmd_remove)

    rms = sub.add_parser("remove-sequence")
    rms.add_argument("name")
    rms.set_defaults(func=cmd_remove_sequence)

    sub.add_parser("list").set_defaults(func=cmd_list)

    nx = sub.add_parser("next")
    nx.add_argument("duration", nargs="?", default="7d")
    nx.set_defaults(func=cmd_next)

    sub.add_parser("calendar").set_defaults(func=cmd_calendar)

    st = sub.add_parser("suggest-time")
    st.add_argument("--platform", required=True)
    st.add_argument("--audience", default="indie-dev", choices=["indie-dev", "b2b", "general"])
    st.set_defaults(func=cmd_suggest_time)

    sub.add_parser("run-due").set_defaults(func=cmd_run_due)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
