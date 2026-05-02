---
name: megaphone-outreach
description: Plan launches and execute communication outreach - find venues (awesome-lists, directories, subreddits, newsletters, communities), find amplifiers (creators, maintainers, podcasters), draft per-venue submission packets and personalized DMs that reference the recipient's actual work, and produce a 30/14/6/0-day launch plan. Use when the user says "plan my launch", "where should I submit", "find awesome-lists", "find communities for my project", "who should I reach out to", "draft a DM to <person>", "make a launch checklist", "30-day launch plan", "I'm launching on Product Hunt", "find newsletters that would cover this", "help me prepare outreach". Reads the project profile, scores venues by fit/effort/active, drafts personalized DMs, produces ready-to-paste copy per channel.
---

# megaphone-outreach

Most indie projects don't fail because they're bad. They fail because nobody hears about them. This skill closes that gap. It does four things, all from the same project profile:

1. **Find venues** — awesome-lists, directories, subreddits, newsletters, communities where the project belongs
2. **Find amplifiers** — humans (creators, maintainers, podcasters, journalists) who'd plausibly share it
3. **Draft the asks** — submission packets per venue, personalized DMs per amplifier
4. **Plan the timing** — 30/14/6/0-day launch plan that orchestrates all of the above

This skill consolidates the older launch and discover skills, and adds the amplifier outreach layer that didn't exist before.

## Preamble: project resolution & bash hygiene

This skill operates inside a single project root and reads `.megaphone/profile.json` from there. Before doing anything:

1. **Resolve the target project.** If the cwd already looks like a project (`.git/`, `package.json`, etc.) and contains `.megaphone/profile.json`, use it. Otherwise, follow the resolution flow from `megaphone-init` §0b — confirm `<basename>` for cwd, or pick from memory candidates / paste a path. Never assume `$HOME` is the project.
2. **Exit-zero probes.** When checking for files that may not exist, wrap probes in `sh -c '...; exit 0'` and use `[ -e "<path>" ]` guards. Never let a missing file produce a visible red error block on first run.
3. **Absolute paths after resolution.** Once the target is known, use absolute paths for every Read/Write and prefix Bash with `cd "<path>" && ...`.

## Workflow — pick a phase or run them in order

The skill has four phases. The user usually wants one phase at a time; ask which:

- **Discover venues** — "where should I submit"
- **Find amplifiers** — "who should I reach out to"
- **Draft outreach** — "write the DMs", "draft the submissions"
- **Plan launch** — "make a 30-day launch plan"

If the user says "plan my launch" or "do everything," run all four in order. They build on each other — the venues + amplifiers feed into the launch plan tasks.

### Phase 1 — Discover venues

Read `.megaphone/profile.json` to know the project's stack, audience, niches, and goals.

Run the venue scorer:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-outreach/scripts/outreach.py" venues \
  --profile .megaphone/profile.json \
  --output .megaphone/outreach/venues.json
```

The scorer produces a candidate list across five venue types:

- **Awesome-lists** — search GitHub `awesome <topic>` for each topic in the profile, filter by recently-updated (last 90 days)
- **Niche directories / launch platforms** — DevHunt, TinyLaunch, Smol Launch, Open Launch, Peerlist Launchpad, Indie Hackers, BetaList, Uneed, Fazier, AlternativeTo, There's An AI For That
- **Subreddits** — match subreddit topics to project niches; respect "no self-promo" rules
- **Newsletters** — TLDR, Console.dev, Pointer, JavaScript Weekly, Python Weekly, Bytes, etc.
- **Communities** — Discord/Slack workspaces in the project's domain

Then the skill ranks each candidate (1–5 each):
- **Audience fit** — would the people in this venue actually use the project?
- **Effort** — how much work is the submission?
- **Active** — is the venue alive (recent activity)?

Sorts by `(audience_fit × active) / effort`. The top of the list is "do today, takes 10 minutes." The bottom is "if you have time."

Cap at **15 venues** total. Long lists don't get acted on.

For each top-tier venue, write a submission packet under `.megaphone/outreach/venues/<slug>/packet.md`:

```markdown
# <Venue name>

**Type:** awesome-list | directory | subreddit | newsletter | community
**URL:** <where to submit>
**Wait time:** <e.g., "PRs typically merged in 1-3 days">
**Effort:** low | medium | high
**Audience fit:** 1–5 · <one-line reason>

## How to submit
<exact steps: open this PR, post in this thread, email this address>

## Submission copy
<ready-to-paste — for awesome-lists, the exact line to add; for directories, tagline+description+screenshots; for subreddits, post title + body with maker disclosure; for newsletters, 3-sentence pitch>

## Notes
<anything specific: "this maintainer prefers PRs without screenshots", "this sub bans new accounts under 30 days">
```

Read `references/awesome-list-submission.md` for the canonical PR shape and the maintainer-tolerance rules.

### Phase 2 — Find amplifiers

The 15-venue list is half the story. The other half is **humans** — creators, OSS maintainers, podcast hosts, technical writers — who could amplify the launch with a single share.

Run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-outreach/scripts/outreach.py" amplifiers \
  --profile .megaphone/profile.json \
  --output .megaphone/outreach/amplifiers.json
```

The amplifier finder is heuristic — read `references/amplifier-discovery.md` for the full search strategy. Summary:

- Recent Product Hunt launches in the same category → makers who might cross-share
- Recent Show HN posts on the topic → folks who care about this niche
- dev.to authors who covered similar problems → potential blog amplifiers
- Authors of the relevant awesome-lists → maintainers who'd add the project AND mention it
- Maintainers of upstream tools the project builds on → if the project is a useful add to their ecosystem
- Podcast hosts in the niche (`<topic> podcast` site:listennotes.com or similar)

For each amplifier candidate, surface:
- Who they are (name, handle, primary platform)
- Why they might share (specific recent work that connects to this project)
- What to ask for (RT, blog mention, podcast guest spot, beta feedback)
- Best contact channel (DM, email, GitHub issue)

Cap at **10 amplifiers** for v1. The point isn't to spray; it's to send 5–10 personalized messages that get 2–3 yeses.

### Phase 3 — Draft the outreach

Two parallel drafting tasks:

**3a. Per-venue submission packets** (already covered in Phase 1's output). The skill should walk through each top-3 venue and verify the packet copy matches the user's voice (read the `voice.samples` from `.megaphone/profile.json`).

**3b. Per-amplifier DMs**. For each amplifier from Phase 2, draft a personalized message saved to `.megaphone/outreach/dms/<handle>.md`.

Read `references/dm-templates.md` for the templates. The structure is always:

1. **Open with proof of context** — reference the amplifier's specific recent post / project / talk by name. NOT "I love your work" (vague, performative). YES "Your Bluesky thread on observability tools is what made me start using Honeycomb."
2. **One sentence on why they specifically might care** — the connection between their work and yours
3. **The ask, named clearly** — RT? Mention? 5-min review? Beta access? Be specific.
4. **Easy out** — "no problem if not, just thought of you" closes the loop without making them feel bad

Per-platform tone matches `references/dm-templates.md`:
- Bluesky / X DM — short, casual, two paragraphs max
- LinkedIn — slightly more formal, name the connection point first
- Email — subject line that says what it is, ≤150 words body
- GitHub issue / DM — lead with the technical relevance, not the promotion

**Honesty rules baked in:**

- **Don't draft templated DMs.** If we can't reference the recipient's specific work, the DM isn't ready — surface that to the user as "we couldn't find specific recent work for <amplifier>; either skip or research more."
- **Never auto-send.** Megaphone produces drafts; the user sends them. Auto-DMing is against most platforms' ToS and reputation-toxic.
- **Don't lie about urgency or scarcity.** No "limited beta spots" if there aren't any.
- **Disclose what you are.** "I built X" is fine. Pretending to be a fan first and only revealing the project at the end is the kind of behavior that makes people block "indie outreach."

### Phase 4 — Plan the launch

This is the orchestration layer that ties venues + amplifiers + posts (`megaphone-post`) into a dated 30/14/6/0-day timeline.

Read `references/launch-channels.md` for current per-platform rules and timing windows.

Ask once for what's not in the profile:

- **Launch date** — exact date, "next month", or "in ~6 weeks"; default to 30 days out
- **Channels** — multi-select. Recommend a starter set based on audience:
  - Developer tools → Product Hunt + Show HN + DevHunt + Peerlist + dev.to
  - End-user app → Product Hunt + BetaList + Reddit (relevant sub) + Indie Hackers
  - SaaS / business tool → Product Hunt + BetaList + Peerlist + LinkedIn + Indie Hackers
  - Open-source library → Show HN + dev.to + relevant awesome-list submissions + Reddit
- **Existing audience** — drives whether the plan starts with a warm-up or assumes cold start
- **Time budget** — caps how many channels we plan for (two channels done well > seven half-launched)

Build the dated checklist using the **30/14/6/0** cadence:

**Day -30 to -15 (foundation phase)**
- README hero in place; add screenshot/GIF if missing
- Reserve handles on every channel
- Submit to BetaList (typical 4-week wait for feature)
- Begin a build-in-public cadence on whichever social platforms the user has presence on (`/megaphone-post` drafts these)
- Identify 5–10 awesome-lists / subreddits / Discord communities (Phase 1 output above)
- Reach out to 3–5 amplifiers from Phase 2 — draft the DMs

**Day -14 to -7 (asset phase)**
- Finalize hero image / GIF (`/megaphone-assets`, `/megaphone-demo`)
- Lock the Product Hunt tagline + description (≤60 + ≤260 chars)
- Lock the Show HN title (`Show HN: <project> – <one-liner>`)
- Write the dev.to / Indie Hackers / Peerlist long-form launch posts (`/megaphone-post`)
- Schedule launch-day social posts via `/megaphone-schedule`
- If launching on Product Hunt: confirm Tuesday or Wednesday at 12:01 AM PST

**Day -6 to -1 (warm-up phase)**
- Tease the launch on social with a sneak peek 4 days out
- Submit to Peerlist Launchpad and DevHunt for the launch week
- README polish — typos, broken links, dependency versions
- Pre-write the first 3 comment replies the user is likely to need on PH

**Launch day (Day 0)**
- 12:01 AM PST: Product Hunt post goes live
- 7 AM PST: Show HN submission with the agreed title (human submission only — HN bans bots)
- 8 AM PST: primary social posts go out via `/megaphone-publish` (or scheduled via `/megaphone-schedule`)
- Submit to: TinyLaunch, Open Launch, Smol Launch, Indie Hackers, dev.to
- Reply to every comment within an hour for the first 8 hours
- DM the 3–5 amplifiers — "today's the day; if it's a fit, would love a share"
- Mid-day social update with current traction
- End-of-day thank-you post + screenshot

**Day +1 to +7 (cooldown phase)**
- Write a "what happened on launch day" recap for dev.to / LinkedIn / X
- Follow up with anyone who left thoughtful PH comments — DM thanks
- Submit to any awesome-lists where the project clearly belongs (use Phase 1)
- Run `/megaphone-digest` to capture before/after metrics

Save the master plan to `.megaphone/outreach/launch-plan.md` and per-channel submission packets to `.megaphone/outreach/launch/<channel>.md`.

For platforms requiring human submission (Show HN, Reddit, sometimes dev.to), call this out explicitly in the plan: **"This must be submitted by a real human account; copy below is ready to paste."**

## Saving and organizing

Per-repo:
```
.megaphone/outreach/
├── venues.json              ← Phase 1 raw
├── amplifiers.json          ← Phase 2 raw
├── launch-plan.md           ← Phase 4 master plan
├── venues/
│   └── <slug>/packet.md     ← Per-venue submission copy
├── dms/
│   └── <handle>.md          ← Per-amplifier DMs
└── launch/
    ├── producthunt.md
    ├── show-hn.md
    ├── betalist.md
    ├── peerlist.md
    └── ...
```

Everything lives in the repo so it's `git diff`-able and survives across sessions.

## Telling the user

After running a phase, paste a short summary into chat (e.g., "Top 5 venues, top 5 amplifiers, launch plan ready") and point at the saved files. Don't dump everything in chat.

End with one suggested next move:
- After Phase 1 → "Want me to find amplifiers next? (Phase 2)"
- After Phase 2 → "Want me to draft the DMs? (Phase 3)"
- After Phase 3 → "Want me to weave these into a dated launch plan? (Phase 4)"
- After Phase 4 → "Plan is in `.megaphone/outreach/launch-plan.md`. Want me to schedule the social posts via `/megaphone-schedule`?"

## Honesty and ethics rules

- **Never auto-submit.** Megaphone produces packets; the user submits. Auto-PRs to awesome-lists are the fastest way to get the project blacklisted.
- **Never auto-DM.** Same reason. Most platforms ban this. Reputation matters more than reach.
- **Always disclose maker status** in submission copy where required. Reddit and Indie Hackers explicitly require it. Lying about authorship gets the project banned.
- **Don't list venues we couldn't verify.** If a search didn't find an awesome-list, don't fabricate one.
- **Don't fake amplifier connections.** "Your post on X said Y" should be a real quote from a real post. We surface what we can find via search; if we can't find specific recent work for someone, we don't include them.
- **Skip dead venues.** If an awesome-list's last commit is from 2022, it's not a discovery channel anymore.
- **Don't recommend communities the user shouldn't be in.** No "spammy growth-hacking Discord" submissions. The project's reputation lives downstream of every submission.

## Edge cases

- **No `.megaphone/profile.json`** — say so. Run `/megaphone-init` first; the profile drives everything here.
- **Project is too generic** — surface this. "Your README says 'tool for everyone'; I couldn't find venues with strong fit. Want to sharpen the positioning first via `/megaphone-assets`?"
- **No obvious awesome-list for this project's niche** — suggest the user *create* one as a side play; awesome-lists are themselves SEO and stargazer magnets.
- **Saturated niche** (yet another to-do app) — be honest. Suggest 2–3 angles where the project might still find an audience.
- **User asks for "anywhere I can post"** — push back gently. Spraying submissions hurts more than helps. Recommend the top 5.
- **Pre-launch / waitlist only** — skip Product Hunt and Show HN entirely; lean into BetaList, Peerlist, and a personal site with email capture.

## What this skill is NOT

- Not an auto-poster. Use `/megaphone-publish` for posting, `/megaphone-schedule` for scheduling.
- Not a CRM. We don't track DMs sent / replied / converted; that's overhead the user doesn't need at this stage.
- Not a public-relations agency. We won't pitch your project to Wired. We surface real venues + real amplifiers; the user does the actual outreach.

## How this fits with the rest of megaphone

- `megaphone-init` produces the profile that drives venue + amplifier matching
- `megaphone-assets` produces the copy + banner + GIF that the submission packets reference
- `megaphone-post` produces the platform-specific posts the launch plan schedules — read its `references/community-aware-drafting.md` for the per-platform writing guidance
- `megaphone-publish` and `megaphone-schedule` execute the timeline
- `megaphone-audit` runs the pre-launch sanity check before Day 0
- `megaphone-digest` reports on what happened after launch
