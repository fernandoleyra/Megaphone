---
name: megaphone-digest
description: Generate a weekly traction digest for a software project - GitHub stars delta, recent commits, posts shipped, and the single highest-leverage next action. Use this skill whenever the user asks for a "weekly digest", "how's my project doing", "track my stars", "megaphone digest", "give me a status update on my repo", "what should I do next for distribution", or anything where they want a quick read on momentum and a clear next move. Trigger especially when the user is in a regular Monday/Friday review rhythm and needs a lightweight pulse-check rather than a deep-dive.
---

# megaphone-digest

A short, honest pulse-check on the project's distribution. Reads stars, social activity, and the launch plan; compares to last week; recommends *one* next action. The goal is to keep the user moving without overwhelming them.

The digest persists to `.megaphone/metrics/<date>.md` so the user has a record of momentum (or lack of it) over time.

## Preamble: project resolution & bash hygiene

This skill operates inside a single project root and reads `.megaphone/profile.json` from there. Before doing anything:

1. **Resolve the target project.** If the cwd already looks like a project (`.git/`, `package.json`, etc.) and contains `.megaphone/profile.json`, use it. Otherwise, follow the resolution flow from `megaphone-init` §0b — confirm `<basename>` for cwd, or pick from memory candidates / paste a path. Never assume `$HOME` is the project.
2. **Exit-zero probes.** When checking for files that may not exist, wrap probes in `sh -c '...; exit 0'` and use `[ -e "<path>" ]` guards. Never let a missing file produce a visible red error block on first run.
3. **Absolute paths after resolution.** Once the target is known, use absolute paths for every Read/Write and prefix Bash with `cd "<path>" && ...`.

## Workflow

### 1. Load context

- Read `.megaphone/profile.json`. Required.
- Read the most recent file in `.megaphone/metrics/`, if any — that's the previous digest, used for delta math.
- Read `.megaphone/launch/launch-plan.md`, if present — to know whether the user is pre-launch, mid-launch, or post-launch.

### 2. Pull current metrics

**GitHub stars + activity** (always)
- Use `gh repo view <repo> --json stargazerCount,forkCount,issuesCount,createdAt,pushedAt` if `gh` CLI is installed.
- Else, use the GitHub REST API via `curl`: `curl -s https://api.github.com/repos/<owner>/<repo>` and parse `stargazers_count`, `forks_count`, `open_issues_count`.
- If neither works (no network, private repo without auth), report what we can read locally from git and note the gap.

**Recent commits** (always)
- `git log --since="7 days ago" --pretty=format:"%h %s" --no-merges`
- `git log --since="7 days ago" --shortstat --no-merges` for size

**Posts drafted this week** (if `.megaphone/posts/` exists)
- Count files in `.megaphone/posts/` modified in the last 7 days.

**Posts actually published this week** (if `.megaphone/published/` exists)
- Read every `.megaphone/published/<date>.jsonl` file from the last 7 days. Each line is a JSON record written by `megaphone-publish` with `{platform, url, ok, published_at, ...}`.
- Count `ok: true` lines per platform; surface the URL of the top engagement (when known) or the most recent post per platform.
- This is what tells the user "you actually shipped 3 posts this week" vs "you drafted 5 but published 0" — a much more honest signal than just counting drafts.

**Launch progress** (if `.megaphone/launch/launch-plan.md` exists)
- Count completed checkboxes (`- [x]`) vs total. Surface the next 3 unchecked items.

### 3. Compute deltas

Compare to the previous digest, if one exists:

- Stars delta (and 7-day rate)
- Forks / issues delta
- Commit count delta (was the user more or less active than last week?)
- Posts shipped delta

If there's no previous digest, just report current values and call it baseline week.

### 4. Pick one next action

This is the most important part of the skill. The temptation is to give the user a list of 8 things; resist it. Pick **one** action based on the data:

Decision rules (in priority order):

1. If a launch is within 14 days and the launch plan has unchecked tasks in the current phase → recommend the highest-impact unchecked task in that phase.
2. If stars-per-week dropped 50%+ from last week and there hasn't been a build-in-public post in 14+ days → recommend `megaphone-post`.
3. If `.megaphone/outreach/venues.json` doesn't exist or hasn't been refreshed in 30+ days → recommend `megaphone-outreach`.
4. If commit activity is healthy but no posts have been written in 14+ days → recommend `megaphone-post`.
5. If `.megaphone/assets/` is missing the README hero or the dev.to intro → recommend `megaphone-assets`.
6. If everything is being done and metrics are growing → recommend "stay the course; ship the next feature."
7. If everything is being done and metrics are flat → suggest a different angle: a new niche, a different platform, a deeper dev.to post that swings for HN.

### 5. Write the digest

Save to `.megaphone/metrics/<YYYY-MM-DD>.md`:

```markdown
# Megaphone digest — <YYYY-MM-DD>

**Project:** <name>
**Phase:** <pre-launch | warm-up | launching | post-launch | maintenance>

## This week

- ⭐ Stars: <current> (<+/- delta> vs last week)
- 🍴 Forks: <current> (<delta>)
- 📝 Commits: <count> (<delta>)
- 📣 Posts drafted: <count>
- 🚀 Posts published: <count> across <platforms>

## What shipped

- <commit subject>
- <commit subject>
…

## Launch plan progress (if applicable)

- <X of Y tasks completed in current phase>
- Next 3 tasks: <list>

## Suggested next action

**<one specific action, in plain language>**

<2-sentence reasoning. Tie it to the data you just showed.>

`<corresponding skill invocation, if any>`

## Notes

<Anything notable from the data: a stargazer spike, a sudden flurry of issues, a post that seems to have landed, etc.>
```

### 6. Show the user

Paste the digest into the conversation (it's short — pasting back is fine here, unlike with assets/posts which can be long). End with the next-action recommendation as a question rather than a directive: "Want me to <action>?"

## Honesty rules

- **Don't fabricate metrics.** If you couldn't pull stars, say so. "Couldn't reach the GitHub API; here's what I can see locally."
- **Don't celebrate noise.** A 1-star delta isn't a win, it's a signal we don't have signal yet. Treat early metrics with appropriate humility.
- **Don't recommend the same action two weeks in a row** unless the user explicitly didn't try it. Repeated identical recommendations means the recommendation is wrong.
- **Don't lie about momentum.** If stars are flat for 4 weeks straight, the digest should say so honestly and suggest a different angle, not optimistic hand-waving.

## Edge cases

- **No `.megaphone/` at all** — say so. "Megaphone hasn't been initialized for this repo. Want me to set it up first? (`/megaphone-init`)"
- **No metrics history yet** — call it "baseline week", report current values without deltas.
- **GitHub API rate-limited** — note it; offer to retry with auth (`gh auth login`).
- **Private repo, no `gh` CLI** — fall back to local git data only; tell the user once that to get full metrics they need to authenticate or make the repo public.
- **Project hasn't shipped anything in weeks AND no posts AND no launch plan** — be direct: "There's not much to digest yet. Probably worth either shipping a small thing this week or running `/megaphone-outreach` if you're getting close to ready." Don't invent metrics to make it look like progress.
