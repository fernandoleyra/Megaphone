---
name: megaphone-journey-audit
description: Walk the full user journey for a software project - discovery -> decision -> install -> first run -> activation -> return -> share - and surface friction, dead-ends, and the moment value lands (or fails to). Use this skill whenever the user asks to "audit my user journey", "review my onboarding", "where do users drop off", "is my install flow good", "walk through my project as a new user", "review the first-run experience", "check my activation funnel", "what's the aha moment", or anything where they want a structured friction-finding pass over how someone actually gets from "saw the link" to "got value." Strongly prefer this skill over generic UX feedback - it reads the repo, the landing page, the README, and walks personas through the real flow, then produces a stage-by-stage report with concrete fixes.
---

# megaphone-journey-audit

The user built the thing. Now: can someone actually use it? This skill walks the full journey from "saw the post" to "got value" and points at every place a real human would get stuck. We don't fix the journey — the dev does. We find the friction.

The model is **persona-driven walkthrough on top of static metrics**. The static layer measures things we can count (install steps, required deps, time-to-first-command). The persona layer plays out the journey through three different humans and flags where each gets stuck.

## The seven stages of a user journey

| Stage | What happens | Common failure |
|---|---|---|
| **1. Discovery** | They see a link (Bluesky / HN / awesome-list / search) | Hook doesn't land; they don't click |
| **2. Decision** | They land on the page or README and decide to try it | Hero is vague; trust signals missing |
| **3. Install** | They follow the setup steps | Too many steps, missing deps, sudo prompts |
| **4. First run** | They run the first command | Cryptic output, no example, no fixture data |
| **5. Activation** | They reach the moment value lands ("aha") | Activation moment is buried 3 steps deep |
| **6. Return** | They come back the next day | No reason to return; no "now what" |
| **7. Share** | They tell another person | No share prompt, no shareable artifact |

Most analyses focus on stages 3–4. We cover all seven because the drop-offs are everywhere, and most are 1-line fixes if you find them.

## Workflow

### 1. Identify the targets

The journey audit needs both ends:
- The **discovery surface** — the landing page and/or the GitHub README. Either or both.
- The **repo** — to read install steps, manifest files, scripts, and look for runnable examples.

If the user says "audit my journey" without specifying, default to: the repo at `cwd`, the landing URL from `.megaphone/profile.json` if present, and the repo's README.

Ask only what's not obvious:
- "Is your landing page deployed somewhere I can fetch, or is the README the discovery surface?"
- "What's the activation moment in your head — what does it look like when a user 'gets it'?"  (Optional but very useful; a one-line answer here makes the report 2× more pointed.)

### 2. Run the static analyzer

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-journey-audit/scripts/audit.py" \
  --repo "$(pwd)" \
  --landing https://example.com \
  --output .megaphone/audits/journey-$(date +%Y-%m-%d).json
```

The script measures (full schema in `references/journey-stages.md`):

- **Discovery** — README first 200 chars (preview), landing hero, OG image presence
- **Decision** — README has a "What is this", presence of demo link, license, recent activity (commits in last 30 days)
- **Install** — count of steps in "Install" / "Quick start" / "Getting started", required tools detected (node, python, docker, etc.), required env vars (count of `.env.example` / `process.env` references), presence of `make install` / `npm install` style one-liners
- **First run** — presence of a runnable example in the README (heuristic: a code block immediately following the install section), example command count, has demo URL or hosted-trial option
- **Activation** — presence of "what does success look like" text or screenshot, whether the README explicitly names the aha moment
- **Return** — presence of "what's next" / "going further" / "advanced usage" sections, presence of changelog and last release date
- **Share** — presence of a share button on the landing page, README badge for stars / forks / Discord, "if you liked this" footer

### 3. Persona walkthrough (Claude does this part)

Read `references/personas.md` for the three default personas. For each, narrate the journey end-to-end in second person ("You see a post on Bluesky. The hook says X…"), and at every friction point, write a `[FRICTION]` callout with severity (`low | medium | high | blocker`) and the specific fix.

Default personas (override per project if the audience differs):
1. **The vibe coder** — non-technical, shipped with Lovable, comfortable with Bluesky/X but not GitHub. Mac, no terminal experience. Tries everything on a phone first.
2. **The senior dev** — 30-second skim, scans for red flags, leaves immediately if anything smells off. Asks "what does this replace" within the first paragraph.
3. **The newcomer to the stack** — knows another language. Has Python or Node but not both. Will hit dependency walls.

For each persona, output should look like:

```markdown
## Persona 1: Casey, the vibe coder

**Stage 1 — Discovery.** Casey sees the Bluesky post you scheduled for Tuesday 9am.
The hook reads: "Just shipped a thing that does X. <link>"
[no friction]

**Stage 2 — Decision.** Casey clicks. They land on https://example.com on their iPhone.
The H1 reads: "Welcome to Megaphone".
[FRICTION-medium] The H1 doesn't say what the thing IS or who it's FOR. Casey is gone in 4 seconds. **Fix:** rewrite the H1 to "Distribution toolkit for vibe coders who hate self-promo" (or similar — the rewrite belongs to the dev, but the principle is: name the thing + name the audience + name the wedge).

**Stage 3 — Install.** Casey scrolls past the hero, sees `pip install megaphone`. They're on a Mac that has Python 2 by default; they don't know what `pip3` is.
[FRICTION-high] The README assumes Python 3 + pip is set up. **Fix:** add a one-line "If you don't have Python 3 yet" link to https://python.org or to a brew command.
…
```

End each persona's walk with a one-line summary: did they activate? Did they return? Did they share?

### 4. Synthesize the friction report

After the three personas, write a unified ranked friction list:

**Blockers (fix before launch)** — friction that stops the journey entirely for at least one persona. The user cannot launch with these.

**High-impact (fix this week)** — friction that doesn't block but actively loses people.

**Polish (fix when you have time)** — small wins, multiple per stage usually.

For each friction item, include:
- Stage(s) where it occurs
- Persona(s) it affects
- Severity
- The specific fix

### 5. Surface the activation moment

The single most-valuable insight from a journey audit is naming the activation moment — the moment a user has gotten value and would say "okay I get it now."

For software projects, common activation moments:
- Library / SDK: their first successful API call returns useful data
- App: they save / produce / see the first artifact
- Tool: their first non-trivial command succeeds with visible output
- OSS framework: the demo from the README runs locally
- API service: `curl` returns the right thing

Write one paragraph naming the activation moment for this project. Then:
- Estimate the number of steps from "click install" to activation
- Compare that count to a healthy baseline (≤5 for indie tools, ≤10 for frameworks)
- If they exceed the baseline, the top fix in the report should be "compress the path to activation."

### 6. Save the audit

Write the markdown report to `.megaphone/audits/journey-<date>.md`. Keep the JSON next to it.

### 7. Tell the user

Paste the activation-moment summary + the blocker list (if any) into chat. Don't dump the full persona walkthroughs — point them at the file.

End with one suggested next move:
- If there are blockers → "Want to walk through the top blocker fix together?"
- If only high-impact → "Most of these are README rewrites. Want me to draft them?"
- If only polish → "You're in good shape. Want to set up the launch sequence with `megaphone-schedule`?"

## What "good" looks like by stage

A useful rule of thumb when writing the report: a healthy indie-tool journey looks like this.

| Stage | Healthy | Worrying | Broken |
|---|---|---|---|
| Discovery hook | First sentence names the thing + audience | Generic "powerful tool" hook | "Welcome to X" or no hook |
| Decision (hero/README) | Reader knows what + who + why in 8s | Reader has to read 3 paragraphs | Reader still confused after 1 minute |
| Install | ≤3 commands, copy-paste runs | 5–10 commands, some manual | 10+ commands, decisions, env vars |
| First run | Runnable example in README | "See the docs" with a link | No example; user has to invent input |
| Activation | Within 5 minutes of first run | Within 30 minutes | Not clear it ever happens |
| Return | "What's next" + recent changelog | Stale-looking repo | No reason to return |
| Share | Star button + share blurb + GIF | Star button only | None of the above |

## Honesty rules

- **Don't grade the project on its potential.** Grade the page and repo as they are right now. A future-roadmap line in the README is not a feature today.
- **Don't substitute your own "ideal user" for the dev's.** If the dev says it's for technical engineers, audit it as if a technical engineer were the persona — don't apply Casey-the-vibe-coder to a tool meant for sysadmins.
- **Don't recommend rewriting half the codebase.** Stay in the friction-finding lane. Suggest README/landing/onboarding edits, not architectural rewrites.
- **Activation isn't always magical.** Some tools' value is "saves an hour a week" — the activation is the user realizing the savings, which may take 3 sessions, not 3 minutes. Name that honestly.

## Edge cases

- **No deployed landing** — audit only the README. Note in the report that the landing-page check is deferred; suggest the user run `megaphone-landing-audit` once they have a page.
- **Repo has no README** — that IS the report. Tell the user clearly that the discovery surface is missing.
- **The repo's primary language has no install** (e.g., a static-content repo) — adapt: install becomes "clone and open"; first run becomes "the first artifact they see."
- **The user pushes back on a persona finding** — listen. They know their audience better than us. Update the report based on their input; the personas are starting points, not gospel.

## What this skill is NOT

- **Not a UX research tool.** We don't run real user tests. Replace this with real usability testing once you have users.
- **Not an analytics replacement.** PostHog / Plausible / Amplitude tell you where actual users drop off. We tell you where they're likely to drop off based on what's in your repo + landing today.
- **Not a copywriter.** We point at friction; we suggest specific fixes where they're obvious; we don't rewrite the README wholesale.

## Why this is better than what's out there

Most "user journey audit" tools are either:
- A SaaS funnel-analytics product (Mixpanel, Amplitude) that requires real users — useless pre-launch
- A generic UX-review checklist that doesn't read your code
- A consultant who spends an hour and bills four

Megaphone-journey-audit reads your actual repo + landing, simulates three real personas, and produces a stage-by-stage friction report — for free, in minutes, before you have users. It complements `megaphone-landing-audit` (which scores the landing page in isolation) and pairs with `megaphone-validate` (the launch-readiness check) for a complete pre-launch sanity pass.
