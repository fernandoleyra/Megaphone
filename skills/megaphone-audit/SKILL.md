---
name: megaphone-audit
description: Audit a project before launch - score the landing page (hero, CTA, OG, trust signals, voice, performance), walk the full user journey through three personas (discovery -> decision -> install -> first run -> activation -> return -> share), or run both. Use this skill whenever the user asks to "audit my project", "review my landing page", "is my landing good", "audit my user journey", "where do users drop off", "review my onboarding", "walk through my project as a new user", "before I launch can you check this", "pre-launch audit", or anything where they want a structured pre-launch review of either the landing surface, the activation flow, or the whole journey. The skill picks which subcommand to run based on what the user asks for; if the request is ambiguous or "audit everything", run both. We do not generate landing pages or fix journeys - we score and surface friction; the dev fixes.
---

# megaphone-audit

Two complementary pre-launch audits in one skill:

- **Landing audit** — scores the deployed page (HTML/CSS surface) on a 100-pt rubric.
- **Journey audit** — walks the full discovery → activation flow with three personas and surfaces friction stage by stage.

Most launches benefit from running both. The landing audit catches "the page is broken / vague / un-shareable." The journey audit catches "the page is fine but the install flow is brutal." Different failure modes, different rubrics.

## Preamble: project resolution & bash hygiene

This skill operates inside a single project root and reads `.megaphone/profile.json` from there. Before doing anything:

1. **Resolve the target project.** If the cwd already looks like a project (`.git/`, `package.json`, etc.) and contains `.megaphone/profile.json`, use it. Otherwise, follow the resolution flow from `megaphone-init` §0b — confirm `<basename>` for cwd, or pick from memory candidates / paste a path. Never assume `$HOME` is the project.
2. **Exit-zero probes.** When checking for files that may not exist, wrap probes in `sh -c '...; exit 0'` and use `[ -e "<path>" ]` guards. Never let a missing file produce a visible red error block on first run.
3. **Absolute paths after resolution.** Once the target is known, use absolute paths for every Read/Write and prefix Bash with `cd "<path>" && ...`.

## When to run which

| User says… | Run |
|---|---|
| "review my landing page", "is my landing good", "audit the page" | landing |
| "audit my journey", "review onboarding", "where do users drop off", "walk through as a new user" | journey |
| "audit my project", "pre-launch audit", "before launch can you check this", "review everything" | both |

If unclear, ask once: "Are we looking at the landing page in isolation, the full new-user journey, or both?"

## Workflow

### 1. Landing audit

Run when the user wants to score the marketing page in isolation.

**Inputs:**
- A live URL, or a local HTML file path, or a directory containing `index.html`
- If unspecified, look for: `homepage` in `package.json` → `deployed_url` in `.megaphone/profile.json` → top-level `index.html` / `landing/index.html` / `public/index.html` → ask.

**Run:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-audit/scripts/audit_landing.py" \
  --target https://example.com \
  --output .megaphone/audits/landing-$(date +%Y-%m-%d).json
```

**Output:** structured JSON the skill turns into a markdown report. The 100-point rubric covers:

- Title + meta description length, complete OG card (title + description + image), Twitter card, viewport
- Single H1 (≤10 words), heading hierarchy, above-fold CTA, verb-noun CTA pattern
- Trust signals (testimonials, badges, star counts, "open source" labels)
- Form friction (≤2 forms, ≤4 fields each)
- Image alt-text coverage (≥90%)
- Marketing-hype red flags (no "revolutionary", "next-gen", "world's first", "I'm excited to announce", em-dash hype patterns)
- Voice match against `.megaphone/profile.json` voice samples (qualitative — defer to skill review)
- Page weight (<500 KB), HTTPS + canonical + robots, no render-blocking external scripts
- Pre-launch / waitlist framing if applicable (qualitative)

Read `references/landing-checklist.md` for the full per-check guidance and "what good looks like" examples.

**Report structure** (write to `.megaphone/audits/landing-<date>.md`):

```markdown
# Landing audit — <project> — <date>

**Score:** XX/100  (static checks: YY, deferred to qualitative: ZZ)

## Top 3 fixes
1. <highest-impact issue> — <why it matters> — <concrete fix>
2. ...
3. ...

## Section-by-section

### Hero (above the fold)
<H1 quote, comparison to profile tagline, 8-second clarity check>

### CTA
<verb-noun analysis, above-fold check, primary vs secondary>

### Value props
<concreteness — number/name/win — vs generic "powerful, fast, reliable">

### Trust signals
<what's there, what's faked, pre-launch framing if relevant>

### Voice
<diff against profile.json voice samples; flag AI-default tells>

### Meta / sharing
<title, description, OG image — the OG image is launch-blocking if missing>

### Mobile
<viewport meta, tappable CTA, no-text-in-images>

### Performance hints
<page weight, blocking scripts, layout shift>

### Honesty check
<does the page promise what the README delivers?>

## What's good
<2–3 things the user did well — never skip this>

## Suggested next move
<one concrete action>
```

### 2. Journey audit

Run when the user wants the full new-user friction map.

**Inputs:**
- The repo path (defaults to `cwd`)
- An optional landing URL / file (the skill will fetch a lightweight summary; for the deep landing pass run the landing audit too)

**Run:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-audit/scripts/audit_journey.py" \
  --repo "$(pwd)" \
  --landing https://example.com \
  --output .megaphone/audits/journey-$(date +%Y-%m-%d).json
```

**Output:** stage-by-stage scoring across the seven journey stages (each 0–10, total 0–70):

| Stage | What we measure |
|---|---|
| 1. Discovery | README first 200 chars, landing reachable, OG image presence, recent activity |
| 2. Decision | "What is" / "About" section, license, demo link, recent commits |
| 3. Install | Section presence, command count, required tools, env-var count |
| 4. First run | Usage / Quick start section, runnable code blocks |
| 5. Activation | Screenshot, demo URL, explicit naming of the aha moment |
| 6. Return | Changelog file, "what's next" / "advanced" sections |
| 7. Share | Star/fork/Discord badges, share prompt, OG image |

Read `references/journey-stages.md` for the per-stage friction patterns and healthy/worrying/broken thresholds.

**The qualitative half is the personas.** For each of three personas (read `references/journey-personas.md`), narrate the journey end-to-end in second person ("You see a Bluesky post. You click. The H1 reads…") and at every friction point write a `[FRICTION-{low|medium|high|blocker}]` callout with the specific fix.

The default personas:

1. **Casey, the vibe coder** — non-technical, shipped with Lovable, reading on phone, no terminal experience
2. **Dani, the senior dev** — 30-second skim, scans for red flags, leaves on the slightest smell
3. **Sam, the newcomer to the stack** — Windows + JS native, has Python but not the muscle memory

Adapt or replace personas if `.megaphone/profile.json` lists a more specific audience.

**The most-valuable single output: name the activation moment.** What's the moment value lands? How many steps from "click install" to that moment? Compare to the healthy baseline (≤5 for indie tools, ≤10 for frameworks). If the path is too long, the top fix in the report is "compress the path to activation."

**Report structure** (write to `.megaphone/audits/journey-<date>.md`):

```markdown
# Journey audit — <project> — <date>

**Score:** XX/70 (discovery YY/10, decision YY/10, install YY/10, first-run YY/10, activation YY/10, return YY/10, share YY/10)

## Activation moment
<one paragraph naming the moment value lands>
<step count from install to activation, healthy/worrying/broken>

## Friction (ranked by impact)

### Blockers (fix before launch)
- ...

### High-impact (fix this week)
- ...

### Polish (when you have time)
- ...

## Persona walkthroughs

### Persona 1: Casey
<second-person narration with [FRICTION-…] callouts>
Did Casey activate? Did they return? Did they share?

### Persona 2: Dani
...

### Persona 3: Sam
...

## What's good
<2–3 things, especially in the personas' voices>

## Suggested next move
<one concrete action>
```

### 3. Both (the recommended pre-launch sweep)

Run both back-to-back. Produce a combined summary at the top:

```markdown
# Pre-launch audit — <project> — <date>

**Landing:** XX/100. Top fix: <one line>.
**Journey:** XX/70. Activation moment: <one line>. Top fix: <one line>.

**Go/no-go recommendation:** <go | go after fixing top blockers | not yet>
```

Then link to the two detailed reports.

## Telling the user

After running, paste a short summary into chat (the score for each, the top 1–2 fixes), then point at the saved markdown files. Don't dump full audits in chat — they're long.

End with one suggested next move:
- Score < 50 → "Want to walk through the top blocker fix together?"
- Score 50–80 → "Most of these are README + landing edits. Want me to draft them?"
- Score > 80 → "You're launch-ready. Want me to set up the launch sequence with `megaphone-schedule`?"

## Honesty rules

- **Don't grade on a curve.** A 60/100 is a 60/100.
- **Don't substitute your own ideal user.** If `.megaphone/profile.json` says it's for sysadmins, don't audit as if it's for vibe coders.
- **Don't claim things we can't verify.** We don't measure conversion rate, we don't run Lighthouse, we don't run real usability tests.
- **Don't generate fixes the dev should write.** Suggest specific README/landing edits; don't rewrite their site.

## What this skill is NOT

- Not a Lighthouse / PageSpeed clone (no Web Vitals).
- Not a real usability research tool (we don't run sessions with users).
- Not a copywriter (we point at gaps; the dev writes).
- Not a code-quality / security audit (use `engineering:code-review`).

For the per-skill detail, read the reference files: `references/landing-checklist.md` for the landing rubric, `references/journey-personas.md` and `references/journey-stages.md` for the journey audit.
