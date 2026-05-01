# Landing-page audit checklist

Reference for what each rubric check actually means and how to interpret the results. Read this when surfacing findings to the user.

## Hero (above the fold)

The reader decides in 8 seconds whether to keep reading. The H1 + subheadline have to do four jobs:

1. Name what the thing is (a noun: "Distribution toolkit", "Build-in-public scheduler")
2. Name who it's for (an audience: "for vibe coders", "for indie founders")
3. Name the wedge — one specific outcome
4. Be free of marketing fluff (no "revolutionary", no "next-generation")

Bad examples:
- "Welcome to Megaphone" — what does it do?
- "Reimagining the future of distribution" — what does that even mean?
- "The most powerful platform you've never heard of" — empty

Good examples:
- "Distribution toolkit for vibe coders who hate self-promo" — concrete and named
- "Schedule launches across Bluesky, LinkedIn and dev.to without leaving your repo" — names the platforms and the constraint

## CTA

The CTA is verb + noun. Action + concrete object.

Good: "Get started free", "Install the plugin", "Try the demo", "See the docs".
Bad: "Learn more", "Click here", "Submit", "Continue".

The first CTA should be visible above the fold. Mobile users in particular will not scroll past the hero on a slow connection.

## OG / Twitter card

This is the single highest-leverage 5-minute fix on most landing pages. Without an OG image, every share on Bluesky/X/LinkedIn shows a broken-looking tile. The image should be at least 1200×630, clearly readable on a phone-sized preview, branded.

Required tags:
- `<meta property="og:title" content="..." />`
- `<meta property="og:description" content="..." />`
- `<meta property="og:image" content="https://.../full-url.png" />`
- `<meta name="twitter:card" content="summary_large_image" />`

The OG image should be the **full URL**, not relative — many crawlers don't resolve relative paths.

## Trust signals

If the project is launched and has real users, surface that proof:
- "1,200 GitHub stars" + linked badge
- "Used by [3 real company logos]"
- "What people are saying" section with 2–3 attributed quotes
- "5,000 builders shipped with this last quarter"

If pre-launch and there's no proof to surface, **don't fake it**. Lean on alternative signals that are honest:
- "Open source — read the code"
- "MIT licensed"
- "No signup, runs on your machine"
- "Built by [real human], shipping in public, here's the thread"

## Forms

Friction is fields × required-ness. A signup form with one field (email) converts ~3× a form with five. Even captchas, terms-acceptance checkboxes, and dropdowns reduce conversion measurably.

Audit the highest-friction form. Each field that can be inferred or asked for later should be removed.

## Voice

Compare against the voice samples in `.megaphone/profile.json`. Specific tells of AI-default voice (which the user did NOT write) include:

- Em-dashes used as punchline punctuation in places the user's samples don't use them
- Exclamation points on every sentence
- "I'm excited to announce" / "I'm thrilled" openers
- Triplets of generic adjectives ("powerful, fast, reliable")
- "In today's world" / "In the modern era" / "Now more than ever"
- Hyphenated buzzwords ("next-generation", "cutting-edge")

If the page reads like a TechCrunch press release and the user's voice samples read like a Slack message, the page is going to feel inauthentic to whoever the user already knows.

## Performance hints

We don't run Lighthouse — but we can still flag the obvious:
- Page weight > 500 KB on the first byte → suspicious for a marketing page
- More than 5 render-blocking external scripts → kill loading speed on mobile
- Image elements without explicit width/height → cause layout shift
- Forms without `autocomplete=` attributes → Safari/iOS friction

For real Web Vitals (CLS, LCP, INP) point the user at https://pagespeed.web.dev or Chrome DevTools.

## Mobile

- Viewport meta with `width=device-width, initial-scale=1` — required, no exceptions
- CTA tappable (≥44×44 CSS pixels)
- No important text rendered inside images
- Text sizes ≥14px

We can verify viewport meta from HTML alone. The other items the human has to confirm visually.

## Pre-launch / waitlist mode

A waitlist page has a different rubric:
- Trust signals are framed as social proof of demand, not usage ("join 700 on the waitlist", "127 stars in 24 hours")
- The CTA is "Get notified" or "Reserve your spot", not "Try it free"
- The hero doesn't need to deliver value — just promise it credibly

Score these positively when the framing is honest. Penalize them when the framing pretends usage that doesn't exist.

## Things we deliberately don't check

- **Conversion rate.** We can't measure it from HTML alone. Use PostHog, Plausible, or your own analytics.
- **A/B tests.** Out of scope for an audit.
- **Lighthouse / Web Vitals.** Use a real browser tool.
- **Color contrast / accessibility scores.** Static analysis can catch some of this; for a full a11y audit use axe DevTools or Lighthouse's a11y panel.
- **Copy comparison to competitors.** Out of scope. We compare to the user's own voice samples.

## Reading the score

| Score | Meaning |
|---|---|
| 90–100 | Launch-ready. Ship it. |
| 75–89 | Few small fixes, mostly polish. |
| 60–74 | Real gaps that will hurt at launch. Fix the top 3 before you press go. |
| 40–59 | Fundamentals are missing. The page is a 30-minute fix away from being good but isn't there yet. |
| <40 | Don't launch on this. Either rebuild the hero block or push the launch date. |
