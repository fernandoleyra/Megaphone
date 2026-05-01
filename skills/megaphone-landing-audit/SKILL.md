---
name: megaphone-landing-audit
description: Audit a landing page for launch readiness - hero clarity, CTA strength, trust signals, voice match, SEO/OG/social meta, mobile-friendliness, and conversion-killing patterns. Use this skill whenever the user asks to "review my landing page", "audit my landing", "is my landing page good", "check my marketing site", "what's wrong with my landing", "before I launch can you look at the page", "review the conversion flow", or anything where they have a built landing page (URL or local HTML file) and want a structured pre-launch review. The skill assumes the user has already built the page (they're a vibe coder shipping with Lovable / v0 / Cursor / hand-rolled) - it does not generate the page. It produces a scored report with concrete fixes ranked by impact.
---

# megaphone-landing-audit

The user has built a landing page. They ship in days, not months — but the page often has subtle launch-readiness gaps: a hero that doesn't say what the thing is, a CTA buried below the fold, a missing OG image so every share looks broken. This skill runs a structured audit and returns a prioritized fix list.

We **do not generate** landing pages. Vibe coders build their own and they're better at it than we are. Our job is to look at what they built and tell them honestly what's working and what isn't.

## Workflow

### 1. Get the input

Either:
- A live URL (`https://example.com`)
- A path to a local HTML file (e.g., the `index.html` they're previewing locally)
- A path to a directory that contains an `index.html`

If the user just says "audit my landing page" without specifying, look for an obvious candidate:
1. The `homepage` field in `package.json`
2. The deployed URL in `.megaphone/profile.json`
3. A top-level `index.html` or `landing/index.html` or `public/index.html`
4. Else, ask.

### 2. Run the static analyzer

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-landing-audit/scripts/audit.py" \
  --target https://example.com \
  --output .megaphone/audits/landing-$(date +%Y-%m-%d).json
```

The script returns a structured JSON report covering:

- **Meta** — title length, description length, canonical, robots, viewport
- **Open Graph / Twitter Card** — `og:title`, `og:description`, `og:image`, `og:type`, `twitter:card` presence and validity
- **Headings** — h1 count, h1 word count, heading hierarchy
- **CTAs** — first call-to-action found, its text, whether it appears in the first 1500 bytes (a heuristic for above-the-fold)
- **Forms** — count, total fields per form (signup-friction proxy)
- **Images** — total, missing alt, oversized (>500KB)
- **Scripts** — total, blocking
- **Page weight** — gzipped HTML, total external requests if URL is fetched
- **Voice red-flags** — instances of "revolutionary", "next-generation", "10x", "world's first", em-dash hype patterns, "I'm excited to announce"
- **Trust signals** — counts of testimonials (heuristic: blockquote, "users said", etc.), GitHub badge, social proof numbers ("10,000 users")

The script also pulls the **first 8KB of body text** so the skill (Claude) can review the actual content qualitatively in the next step.

### 3. Run the qualitative review

The script's JSON is the input; the skill produces a written audit. The structure of the audit:

**Score: <0–100>** (computed from the static checks; the skill should explain how the score was reached, not just present it as a number)

**Top 3 fixes** — the highest-impact issues, sorted by ROI. For each:
- What's wrong (specific quote from the page if applicable)
- Why it matters (one-sentence reason)
- How to fix (concrete edit or copy suggestion)

**Section-by-section review:**

1. **Hero (above the fold)** — does the H1 + subheadline answer "what is this and who is it for" in under 8 seconds of reading? Quote the actual H1. Compare to the project's tagline in `.megaphone/profile.json` if present.

2. **CTA** — verb-noun construction (good: "Get started free", "Install the plugin"; bad: "Learn more"). Visible above the fold? Different from the secondary action?

3. **Value props** — is each prop concrete (a specific outcome, with a number or named win)? Or generic ("powerful, fast, reliable")?

4. **Trust signals** — testimonials, logos, GitHub stars, user counts. If pre-launch, framing it honestly ("MIT-licensed", "open source", "no signup required") beats faking proof.

5. **Voice** — does the page sound like the user's voice samples in `.megaphone/profile.json`? Flag any AI-default tells (em-dashes as hype punctuation, "I'm thrilled", "let's revolutionize").

6. **Meta / sharing** — title, description, OG image. The OG image is the single most-shared asset — if it's missing, every Bluesky/X/LinkedIn share looks broken. Treat as a launch blocker.

7. **Mobile** — viewport meta present? CTA tappable? Important text not in an image?

8. **Performance hints** — page weight, render-blocking scripts. If the page is >500 KB on first load, call it out.

9. **Honesty check** — does the page promise things the README/repo doesn't deliver? This is rare but lethal.

**Things that are good** — call out 2–3 things the user did well. Audits that are pure negative feedback get ignored.

**Notes for next time** — if the audit found systematic issues (no OG images on any of their pages, generic voice), suggest captures for `.megaphone/profile.json` so future generations from `megaphone-assets` don't repeat the issue.

### 4. Save the audit

Write the markdown report to `.megaphone/audits/landing-<date>.md`. Keep the JSON next to it so the next audit can diff against the last one.

The skill should also write a small `latest.json` symlink-replacement (just a JSON pointer file) so `megaphone-digest` can surface "your last audit was N days ago, score Y."

### 5. Tell the user

Paste the score + top 3 fixes into the chat. Don't dump the full audit — point them at the file. End with one suggested next move:
- If score < 60 → "Want to make the top fix together?"
- If score 60–80 → "Most of these are 5-minute changes. Want me to propose the exact copy?"
- If score > 80 → "You're launch-ready. Want me to set up the launch sequence with `megaphone-schedule`?"

## Scoring rubric

The score isn't a vibe — it's a sum of weighted checks. The script returns the raw weights; the skill explains them.

| Check | Weight | Pass = |
|---|---|---|
| Title present, 30–60 chars | 5 | yes |
| Meta description 50–160 chars | 5 | yes |
| OG title + description + image | 10 | all three |
| Twitter card | 5 | yes |
| Viewport meta | 5 | yes |
| Single H1 with ≤10 words | 8 | yes |
| Heading hierarchy (no h3 before h2 etc.) | 4 | yes |
| Above-fold CTA detected | 10 | yes |
| CTA verb-noun pattern | 6 | yes |
| Trust signals (≥1 of: testimonial, star count, user count, "open source") | 6 | yes |
| ≤2 forms, ≤4 fields each | 6 | yes |
| All images have alt text | 5 | ≥90% have alt |
| No marketing-hype red-flag words | 5 | none found |
| Voice consistent with profile.json (if exists) | 5 | qualitative pass |
| Page weight <500 KB | 5 | yes |
| HTTPS / canonical / robots ok | 5 | all present |
| Performance hint: minified inline JS | 3 | yes |
| Empty state / pre-launch framing if no real proof | 7 | qualitative pass |

Total = 100. The script outputs each check + its actual value + pass/fail; the skill turns it into prose.

## Honesty rules

- **Don't grade on a curve.** A 60/100 launch is a 60/100 launch. Telling the user it's good when it isn't is the worst thing we can do.
- **Don't be cute about easy fixes.** If the OG image is missing, that's "fix this in 10 minutes before launch" not "consider adding visual social previews to optimize sharing engagement."
- **Don't recommend things you can't verify.** We can't measure conversion rate. We can measure whether the page has a CTA. Stay in the lane of what's actually visible in the HTML.
- **Don't generate the page.** The user is the dev. Suggest specific copy or specific tag changes; don't offer to rewrite the page wholesale.

## Edge cases

- **Pre-launch / waitlist page** — adjust the rubric: trust signals are framed differently ("700 on the waitlist" beats "1M users" promise we can't back). Score the empty-state content positively.
- **Single-page app with JS-rendered content** — the static fetch only sees the shell. Note this in the report; if a Playwright run is available the skill can suggest using it, otherwise audit what we can see and flag the limitation.
- **Repo doesn't have `.megaphone/profile.json`** — skip the voice-match check; everything else still works.
- **URL returns 4xx/5xx** — fail clean with a clear message; don't silently audit a 404.
- **User runs the audit twice** — the script writes timestamped files; the skill diffs against the previous audit and surfaces what improved.

## What this skill is NOT

- Not a landing page **generator**. The dev built the page; we audit.
- Not a Lighthouse / PageSpeed clone. We don't run Chrome; we don't measure CLS or LCP. For real Web Vitals, use Chrome DevTools or web.dev/measure.
- Not an A/B-test runner. We score the current state.
- Not a copywriter. We point out what to fix; we suggest specific copy where it's clear; we don't rewrite the whole page.

For the deeper question of "does the user actually convert through this page?", run the companion `megaphone-journey-audit` — that walks the full discovery → install → activation flow.
