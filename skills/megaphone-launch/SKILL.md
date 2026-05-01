---
name: megaphone-launch
description: Build a phased launch plan for a software project - pick channels (Product Hunt, Hacker News Show HN, BetaList, Peerlist, DevHunt, dev.to, Indie Hackers, etc.), schedule pre-launch tasks across a 30/14/6/0-day cadence, and generate the assets and submission copy each channel needs. Use this skill whenever the user asks to "plan my launch", "30-day launch plan", "I'm launching on Product Hunt", "make me a launch checklist", "where should I launch", "help me prepare for launch", or anything where they have a specific or rough launch date and need a coordinated multi-channel campaign. Trigger even if they don't say "megaphone" - this is the right skill any time someone with a project is trying to organize a launch across multiple platforms.
---

# megaphone-launch

A successful indie launch is rarely a single event — it's a sequence. A solo Product Hunt drop without warm-up almost always underperforms. This skill builds the dated multi-channel ramp around the user's launch date and generates the submission copy each platform expects.

The plan goes into `.megaphone/launch-plan.md` so the user can re-open it across sessions and check tasks off.

## Workflow

### 1. Load context

- Read `.megaphone/profile.json`. If missing, say so and run `megaphone-init` first.
- Read `.megaphone/assets/` if it exists — you'll reuse the tagline, hook, and README hero. If assets are missing, note that you'll generate placeholders and recommend `megaphone-assets` afterward.
- Read `references/launch-channels.md` for current platform rules and timing windows. Always cross-check this file rather than relying on memory — channel rules change.

### 2. Gather launch parameters

Use one AskUserQuestion call with the parameters the profile didn't already capture:

- **Launch date** — exact date if they have one; "next month" or "in ~6 weeks" works too. Default to 30 days out if they say "soon."
- **Channels** — multi-select from: Product Hunt, Hacker News Show HN, BetaList, Peerlist Launchpad, DevHunt, TinyLaunch, Open Launch, Smol Launch, Indie Hackers, dev.to, Reddit (specify subreddit), Bluesky, LinkedIn, X. Recommend a starter set based on the project's audience:
  - Developer tools → Product Hunt + Show HN + DevHunt + Peerlist + dev.to
  - End-user app → Product Hunt + BetaList + Reddit (relevant sub) + Indie Hackers
  - SaaS / business tool → Product Hunt + BetaList + Peerlist + LinkedIn + Indie Hackers
  - Open-source library → Show HN + dev.to + relevant awesome-list submissions + Reddit (r/programming or specific language sub)
- **Existing audience** — "Do you already have followers somewhere (X, Bluesky, mailing list, Discord)?" — drives whether the plan starts with a warm-up or assumes cold start.
- **Time budget** — "How many hours/week can you spend on this?" — caps how many channels we plan for. Two channels done well > seven half-launched.

### 3. Build the dated plan

Use the **30/14/6/0** cadence. For each channel, slot tasks at the right milestone. The result is a single ordered checklist by date.

**Day -30 to -15 (foundation phase)**
- Confirm the README hero is in place; add a screenshot/GIF if missing
- Reserve handles on every channel that needs an account (Product Hunt, BetaList, Peerlist, DevHunt, dev.to, Indie Hackers)
- Submit to BetaList (typically 4-week wait for feature)
- Begin a build-in-public cadence on whichever social platforms the user has the most existing presence on (`megaphone-post` will draft these)
- Identify 5–10 awesome-lists, subreddits, or Discord communities to engage with (use `megaphone-discover`)
- Reach out to 3–5 people in the user's network who might be willing to amplify on launch day — draft the outreach DM

**Day -14 to -7 (asset phase)**
- Finalize hero image / GIF
- Lock the Product Hunt tagline + description (≤60 chars + ≤260 chars)
- Lock the Show HN title (format: "Show HN: <project> – <one-liner>")
- Write the dev.to / Indie Hackers / Peerlist longer-form launch post drafts (≥800 words for dev.to, conversational for IH)
- Schedule social posts for launch day across Bluesky / LinkedIn / X (warm hook 2 days before, the launch post on the day, follow-ups every few hours during the launch window)
- If launching on Product Hunt: confirm the launch is set for Tuesday or Wednesday at 12:01 AM PST; this gives the full 24-hour window. Avoid Mondays and Fridays.

**Day -6 to -1 (warm-up phase)**
- Tease the launch on social with a sneak peek (screenshot or short demo) 4 days out
- Submit to Peerlist Launchpad and DevHunt for the launch week (each has its own submission window)
- Last-minute README polish — typos, broken links, dependency versions
- Final README screenshot pass; demo GIF smoke test
- Pre-write the first 3 comment replies the user is likely to need on PH ("how is this different from X", "what's the pricing", "why open source")

**Launch day (Day 0)**
- 12:01 AM PST: Product Hunt post goes live
- 7 AM PST: Show HN submission with the agreed title
- 8 AM PST (Tuesday/Wednesday is best): primary social posts go out (Bluesky, LinkedIn, X)
- Submit to: TinyLaunch, Open Launch, Smol Launch, Indie Hackers, dev.to (all single submissions)
- Reply to every comment within an hour for the first 8 hours
- DM the 3–5 amplifiers from the foundation phase
- Mid-day social update with current traction ("we just hit X stars / Y upvotes, thanks everyone")
- End-of-day thank-you post + screenshot of where the project landed

**Day +1 to +7 (cooldown phase)**
- Write a "what happened on launch day" recap post for dev.to / LinkedIn / X
- Follow up with anyone who left thoughtful PH comments — DM thanks
- Submit to any awesome-lists where the project clearly belongs (use `megaphone-discover`)
- Run `megaphone-digest` to capture before/after metrics

### 4. Generate the submission copy each chosen channel needs

For each channel the user picked, generate the exact text/asset bundle and save it under `.megaphone/launch/<channel>/`. Use the formats in `references/launch-channels.md` — do not rely on memory for character limits or required fields.

Examples:
- Product Hunt → `producthunt.md` with: tagline (≤60), description (≤260), 4–6 gallery images list, maker comment, topics
- Show HN → `show-hn.md` with: title (format: "Show HN: <project> – <one-liner>"), comment text, target time
- BetaList → `betalist.md` with: tagline, description, screenshots
- dev.to → `devto-launch.md` with: title, intro, body, tags, canonical URL setting
- Peerlist → `peerlist.md` with: project description, problem/solution, demo URL
- Reddit → `reddit-<subreddit>.md` with: subreddit-appropriate title (no link-bait), self-post body, disclosure that you're the maker

For platforms requiring human submission (Show HN, Reddit, sometimes dev.to depending on community rules), call this out explicitly in the plan: **"This must be submitted by a real human account; copy below is ready to paste."**

### 5. Write the master plan file

Save the full dated plan to `.megaphone/launch-plan.md` with this structure:

```markdown
# Launch plan: <project name>

**Launch date:** <YYYY-MM-DD> (<weekday>)
**Channels:** <list>
**Last updated:** <ISO timestamp>

## Pre-launch checklist (Day -30 to -15)

- [ ] task with due-date
- [ ] task with due-date
…

## Asset phase (Day -14 to -7)
…

## Warm-up (Day -6 to -1)
…

## Launch day (Day 0)
…

## Cooldown (Day +1 to +7)
…

## Channel submission packets

- Product Hunt → `.megaphone/launch/producthunt.md`
- Show HN → `.megaphone/launch/show-hn.md`
…
```

### 6. Hand off

Tell the user the plan is in `.megaphone/launch-plan.md` and the per-channel submission copy is in `.megaphone/launch/`. Suggest the single highest-leverage next move based on how far out the launch is:

- T-30 or earlier → "Want me to find the awesome-lists this should be on? (`/megaphone-discover`)"
- T-14 to T-7 → "Want me to draft the build-in-public posts for the warm-up window? (`/megaphone-post`)"
- T-7 or sooner → "Want me to do a launch-readiness check (broken links, missing screenshots, vague README)?"

## Honesty rules

- **Don't fabricate timing certainties.** If a platform's submission window or moderation queue is unknown, say so in the plan rather than inventing a date.
- **Don't auto-submit.** Megaphone produces submission packets and dated tasks; the user submits. Several platforms (Reddit, HN) will ban automated submissions.
- **Don't promise outcomes.** "Aim for a Top 5 PH placement" is fine; "you'll definitely hit #1" is a lie.
- **Disclose bot accounts where required.** If the user plans to post via API on X, the plan must include "ensure X account bio identifies as automated" — this is a platform requirement, not optional.

## Edge cases

- **User has no launch date** — propose three: 30, 45, 60 days out. Recommend whichever gives them time to ship 2–3 build-in-public posts before launch.
- **User has zero existing audience** — extend the warm-up phase to 45 days; emphasize awesome-list submissions and community engagement over social ads.
- **Pre-launch only / waitlist** — skip Product Hunt/HN entirely; lean into BetaList, Peerlist, and a personal site with email capture.
- **B2B / enterprise** — Product Hunt is fine but LinkedIn, Indie Hackers, and direct outreach matter more; don't over-invest in HN.
