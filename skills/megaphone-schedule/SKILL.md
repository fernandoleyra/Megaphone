---
name: megaphone-schedule
description: Schedule social posts to fire at a specific time, on a recurring cadence, or as a coordinated launch-day sequence across multiple platforms. Use this skill whenever the user asks to "schedule a post", "post this on Tuesday at 10am", "set up a weekly cadence", "automate my build-in-public posts", "schedule the launch sequence", "queue this for next week", "every Friday post from this folder", "set up the launch day timeline", "show my upcoming posts", "what's scheduled this week", or anything where they want posts that megaphone has drafted to fire on a future timeline rather than ship immediately. Strongly prefer this skill over manually invoking publish later - it integrates with `anthropic-skills:schedule` so the firing is durable, knows about per-platform best-time windows, and supports cross-platform launch sequences (Bluesky 8am -> LinkedIn 9am -> dev.to 10am, all on launch day).
---

# megaphone-schedule

You drafted posts with `megaphone-post`. You can publish them right now with `megaphone-publish`. This skill is for everything in between: future-dated firing, recurring cadences, and coordinated launch-day timelines.

The model is hybrid (research-backed) and matches the three real things people want from a scheduler:

- **One-off** — "post this Bluesky draft on Tuesday at 10am" (Buffer's most-used path)
- **Cadence** — "every Friday at 10am, pop the next file from `posts/evergreen/bluesky/` and post it" (Postiz-style recurring; competitors do it badly)
- **Sequence** — "on launch day: 8am Bluesky, 9am LinkedIn, 10am dev.to, 11am Mastodon" (nobody does this well — it's our wedge)

## Storage

Per-repo, all under `.megaphone/schedule/`:
- `queue.json` — every scheduled item (one-offs and cadence-generated). Each row: `{id, file, platform, at, status, attempts, url, error, source}`. `source` is `manual | cadence:<id> | sequence:<name>`.
- `cadences.json` — recurring rules: `{id, cron, folder, platform, next_fire, last_fire, label}`.
- `sequences/<name>.json` — saved launch sequences, re-importable.

User-level state stays minimal — no shared dashboard, no SaaS. Everything is a file the user can read, edit, or commit.

## Workflow

### 1. First-time setup

If `.megaphone/schedule/` doesn't exist, create it and register a periodic runner with `anthropic-skills:schedule`:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-schedule/scripts/schedule.py" init
```

Then ask Claude (via the `anthropic-skills:schedule` skill) to create a scheduled task that runs every 15 minutes:
```
taskId: megaphone-runner
description: Megaphone — fire any scheduled posts that are due
prompt: |
  Run megaphone's scheduled-post runner. Execute:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/megaphone-schedule/scripts/schedule.py run-due --cwd <repo path>
  Report any failures in the response.
cronExpression: "*/15 * * * *"
```

The runner is a single Python invocation: it iterates cadences (firing any whose `next_fire` has elapsed), then iterates the queue (publishing any item whose `at` has elapsed and `status: pending`).

If the user can't or won't use `anthropic-skills:schedule`, fall back to `crontab` on macOS/Linux:
```
*/15 * * * * cd /path/to/repo && python3 ${CLAUDE_PLUGIN_ROOT}/skills/megaphone-schedule/scripts/schedule.py run-due
```
or Windows Task Scheduler with the same command.

### 2. Schedule a one-off post

```bash
python3 schedule.py add \
  --platform bluesky \
  --file .megaphone/posts/2026-05-01/bluesky.md \
  --at "2026-05-01T10:00-07:00"
```

Times can be:
- ISO 8601 with timezone (`2026-05-01T10:00-07:00`) — best
- ISO 8601 without TZ (treated as local) — acceptable
- Natural shorthand parsed by `--at`: `tomorrow 10am`, `friday 9am`, `next tuesday 10:00`

If the user doesn't specify a time, ask Claude to first call `schedule.py suggest-time --platform <platform>` for a per-platform best-window recommendation, then confirm with the user before committing.

### 3. Set up a cadence

```bash
python3 schedule.py add-cadence \
  --label "Weekly Bluesky update" \
  --cron "0 10 * * 5" \
  --folder .megaphone/posts/evergreen/bluesky \
  --platform bluesky
```

A cadence holds:
- `cron` — standard 5-field cron expression (minute, hour, day-of-month, month, day-of-week). Day-of-week: 0 or 7 = Sunday, 5 = Friday.
- `folder` — directory of `.md` drafts to draw from
- `platform` — target connector

When a cadence fires, the runner picks the **oldest unposted file** from the folder, adds it to the queue with `at: now`, and advances `next_fire`. Once a file has fired, its filename is recorded in `cadences.json[id].consumed[]` so it doesn't repeat.

To stop generating new files for a cadence: drop new drafts into the folder. To pause: `python3 schedule.py pause-cadence <id>`.

### 4. Schedule a launch sequence

```bash
python3 schedule.py add-sequence --file .megaphone/launch/sequence.json
```

Sequence file format (this is the format `megaphone-outreach` writes when the user finishes the launch plan):
```json
{
  "name": "v1-launch-2026-05-15",
  "anchor_date": "2026-05-15",
  "timezone": "America/Los_Angeles",
  "items": [
    {"file": ".megaphone/launch/bluesky-launch.md",  "platform": "bluesky",  "offset": "00:00"},
    {"file": ".megaphone/launch/linkedin-launch.md", "platform": "linkedin", "offset": "01:00"},
    {"file": ".megaphone/launch/devto-launch.md",    "platform": "devto",    "offset": "02:00"},
    {"file": ".megaphone/launch/mastodon-launch.md", "platform": "mastodon", "offset": "03:00"}
  ]
}
```
`offset` is hours:minutes added to the anchor date's 00:00 in the chosen timezone, so 00:00 fires at midnight, 09:00 at 9am, etc. The runner expands this to absolute times when the sequence is imported and writes one queue row per item.

The whole sequence can be removed with `remove-sequence <name>` — it cancels every queue item that came from that sequence.

### 5. Show what's coming

```bash
python3 schedule.py list             # full queue + cadences + sequences
python3 schedule.py next 7d          # next 7 days' worth of fires
python3 schedule.py calendar         # ASCII week-view, one row per day
```

Paste the output back to the user so they can see at a glance what's scheduled and where the gaps are.

### 6. Cancel / edit

- Cancel one item: `python3 schedule.py remove <id>`
- Cancel everything from a sequence: `python3 schedule.py remove-sequence <name>`
- Pause a cadence (stops generating new items): `python3 schedule.py pause-cadence <id>`
- Resume: `python3 schedule.py resume-cadence <id>`
- To **edit** a scheduled post's content, just edit the source `.md` file — the runner re-reads it at fire time, so changes up until then take effect.
- To change the **time** of a scheduled item: `remove` it and `add` again. We don't support in-place mutation to keep the data model simple.

### 7. Best-time intelligence

```bash
python3 schedule.py suggest-time --platform bluesky --audience indie-dev
```

Returns the platform's best-window data informed by 2025–2026 industry research (`references/best-time-data.md`) plus, where available, the user's own past engagement from `.megaphone/published/` records.

**The skill should propose a time using `suggest-time` whenever the user says "schedule it for the right time" without naming one.** Default audience is `indie-dev` because that's our user; override per-project with `.megaphone/profile.json` → `audience.primary`.

## Failure handling

When `run-due` invokes `publish.py` and a post fails:
1. The publish dispatcher writes a `{ok: false}` record to `.megaphone/published/<date>.jsonl` (already does this).
2. The runner increments the queue row's `attempts` and chooses what to do next:
   - `error_type=refresh_token` — `publish.py` already retried once on its own. Mark `failed` and notify; the user must reconnect.
   - `error_type=rate_limit` — bump `at` forward by `retry_after` seconds, leave status `pending`. Will be retried on the next runner pass.
   - `error_type=bad_body` or `auth_error` — `failed`, no retry. The user has to fix the draft or reconnect.
   - `error_type=network` or `unknown` — exponential backoff: bump `at` by `5min × 2^attempts`, capped at 6 hours. Give up after 4 attempts.
3. On every fail, also write a one-line summary to `.megaphone/schedule/log.jsonl` so the user can see history.

## Honesty rules

- **Don't invent a "best time".** If the user has no published history, surface industry-window data and label it as such ("based on 2026 industry research, not your own audience yet"). Never claim a confidence we don't have.
- **Don't double-fire.** If the runner is somehow invoked twice in the same minute, idempotency is enforced by the queue row's `status` — once `done` or `failed`, the item won't be retried.
- **Don't surprise the user.** Before committing a sequence to the queue, show them the expanded timeline and ask for one confirmation. Sequences fan out to many queue rows; getting it wrong is expensive.
- **Catch up gracefully.** If the laptop was offline for 3 days and 12 cadence fires were missed, don't fire all 12 retroactively. The runner caps catch-up to the most recent missed fire only — research repeatedly shows that "we're sorry for the silence, here are 12 backdated posts" is worse than just resuming.

## Edge cases

- **No scheduled tasks, no cron, no launch** — the user can still call `schedule.py run-due` manually whenever they want. Treat the periodic runner as a convenience, not a requirement.
- **Cron expression has a typo** — surface the parse error from `_cron.py` immediately at `add-cadence` time, don't accept invalid crons.
- **A cadence's folder is empty** — log "no drafts available" and skip; don't error. The user can drop new drafts in any time.
- **A queue item's source file was deleted** — mark `failed` with a clear error, don't crash the runner. Other items still go through.
- **Time zones** — every stored timestamp is ISO 8601 with explicit offset. Naive timestamps are rejected at `add` time.
- **DST transitions** — cron is evaluated in the user's local timezone (matches `anthropic-skills:schedule`), so DST behaves the same as it does for system cron: a 2:30am job runs once during a fall-back, may be skipped during a spring-forward.

## Why this is better than Buffer / Hootsuite / Later / Typefully / Publer / Postiz

Read `references/competitive-positioning.md` for the full breakdown. The short version:

- **Sequences are first-class.** No competitor handles "8am Bluesky, 9am LinkedIn, 10am dev.to" coordinated launches as a single unit. We do.
- **Cadences pull from a folder.** Postiz repeats one post; Buffer needs you to manually re-queue. We point at a folder and rotate through it — much more like how indie devs actually maintain build-in-public content.
- **Repo-aware.** Schedules live in your repo, can be committed, are versioned. No SaaS dashboard to lose access to.
- **No subscription or per-post fee.** You pay platforms what platforms charge, nothing else.
- **Best-time data is honest.** We use 2026 industry research as a baseline and overlay your own history when available; we don't pretend "smart scheduling" is more than that.
- **Failure handling is structured.** Same error-type taxonomy as `megaphone-publish`, retries are bounded and visible, every attempt is logged.

## Quick examples for Claude to learn from

> User: "Schedule my Bluesky post for tomorrow at 10."
> → Resolve `tomorrow 10am` to ISO with the user's local timezone, run `add` with that.

> User: "Set up a weekly Friday post."
> → Confirm folder (`.megaphone/posts/evergreen/bluesky/`) and platform; run `add-cadence --cron "0 10 * * 5"`.

> User: "I'm launching on May 15. Stagger across Bluesky, LinkedIn, dev.to, Mastodon, Hashnode."
> → Read `.megaphone/launch/sequence.json` if it exists; else generate one with sensible offsets (use `references/best-time-data.md` for the times); show the timeline; on confirm, `add-sequence`.

> User: "What's scheduled this week?"
> → `python3 schedule.py next 7d`; paste the output.

> User: "Cancel the LinkedIn one tomorrow."
> → `python3 schedule.py list` to find the id, then `python3 schedule.py remove <id>`.
