# Platform voice reference

Per-platform shape, tone, and constraints for build-in-public posts. Read this before drafting; do not rely on memory for character limits.

Last updated: April 2026.

---

## Bluesky

- **Char limit:** 300
- **Tone:** developer-friendly, conversational, slightly self-deprecating. Less polished than LinkedIn, more substantive than X.
- **Hashtags:** by convention, no hashtags. Bluesky culture has not adopted them the way other platforms have.
- **Best shape:** hook in the first line (it's what shows in the preview), one concrete detail, link at the end.
- **What works:** specific bug stories, technical decisions, "I just shipped X" with a screenshot.
- **What doesn't:** marketing-speak, all caps, more than one exclamation point.

**Example:**
```
Just spent 4 hours figuring out why my GitHub OAuth flow was returning a token but no user — turns out scope was missing on the redirect URL.

Documented it so the next person doesn't have to: <link>
```

---

## X (Twitter)

- **Char limit:** 280 per tweet. Threads are encouraged for build-in-public content.
- **Tone:** punchier than Bluesky. Hooks matter more because the feed is denser.
- **Threads:** open with a sentence that promises a payoff. Body in 3–5 tweets. Link in the LAST tweet (links in the first tweet hurt distribution).
- **Hashtags:** use 0–2, only if extremely relevant. More than that hurts engagement.
- **Visual:** screenshot, GIF, or short video lifts engagement substantially. Always include if available.
- **Reminder for Megaphone:** API posting costs ~$0.01 per post since Feb 2026, bot accounts must disclose, AI replies require approval. Default to draft-only.

**Example (thread):**
```
Tweet 1: I rebuilt my auth flow this week and stars went from flat to +12/day. Here's what changed 🧵

Tweet 2: Old flow had 3 redirects and a popup. Median time-to-first-success was 47 seconds.

Tweet 3: New flow is 1 click + a magic link. Median is 8 seconds.

Tweet 4: The wins came from cutting things, not adding. Removed: account creation, password setup, the welcome modal.

Tweet 5: Code is OSS if you want to grab the pattern: <link>
```

---

## LinkedIn

- **Char limit:** 3000. Algorithmic sweet spot is 1200–2000.
- **Tone:** more polished, founder-narrative shape. Story-led, not announcement-led.
- **Format:** short paragraphs (1–3 sentences each), generous whitespace.
- **Hooks that work:** "I just spent 6 hours debugging X…", "Here's what I didn't expect about Y…", "Week N of building <project>:". Avoid "I'm excited to announce" — it gets ignored.
- **End with a question** — posts asking questions get 2–3× the comments.
- **Hashtags:** 3–5 at the bottom. LinkedIn rewards hashtag use for discoverability.

**Example:**
```
I shipped the boring half of <project> this week.

No new features. Just: better error messages, a fixed memory leak, and a setup flow that doesn't require reading the README.

Honestly the most useful work I've done all month. New features make the changelog. Polish is what makes people actually use the thing.

Anyone else fighting the urge to build something new when you should be sanding the rough edges?

#indiehacking #buildinpublic #softwaredevelopment
```

---

## dev.to

- **Length:** 800+ words. Algorithmic sweet spot 1500–2500.
- **Title:** promise a payoff — a number, a takeaway, a confession. "How I…", "What I learned…", "X mistakes I made…"
- **Format:** intro that hooks, body broken into H2/H3 sections, code snippets with syntax highlighting, conclusion that wraps the lesson.
- **Tags:** 4 tags max. Use stack tags (`#javascript`, `#react`, `#python`) and category tags (`#opensource`, `#beginners`, `#showdev`).
- **Cover image:** strongly recommended. A clean screenshot or simple illustration outperforms text-only posts substantially.
- **Canonical URL:** if cross-posting, set canonical to the original blog post.

**Title examples that work:**
- "I built a launch checklist generator and learned why my first post flopped"
- "5 things I changed in my README that doubled my GitHub stars"
- "How I fixed our build pipeline (and why I should have done it 6 months earlier)"

---

## Threads (Meta)

- **Char limit:** 500.
- **Tone:** casual, visual-first. Lower bar than LinkedIn or dev.to.
- **Visual:** screenshots / short clips perform better than text-only.
- **Hashtags:** few but accepted.
- **Best for:** consumer-facing products. Less developer audience than Bluesky or X.

---

## Mastodon

- **Char limit:** 500 default (varies by instance up to 1000).
- **Tone:** friendly, technical-positive, supportive. Hashtags are part of the culture.
- **Hashtags:** 2–4 relevant ones. They drive Mastodon's federated discovery.
- **Best instances for tech:** fosstodon.org (FOSS), hachyderm.io (tech), mastodon.social (general).
- **Note:** posts can include CW (content warnings) for politics, NSFW, etc. — usually irrelevant for build-in-public but mention it if a post warrants it.

---

## Universal voice rules

These apply across every platform. Apply them in addition to the per-platform shape above.

1. **Match the user's voice samples** from `.megaphone/profile.json`. If the user is casual, be casual. If they curse, you can curse where the platform allows.
2. **One concrete detail per post.** A number, a file name, a specific bug, a screenshot caption. "Generates the README in 8 seconds" beats "fast and easy."
3. **Active verbs.** "I shipped X" beats "X has been shipped."
4. **One exclamation point max** per post, and only when something genuinely shipped. Not on every sentence.
5. **No emoji** unless the user's voice samples use emoji.
6. **No "I'm excited to announce"** anywhere, ever. It signals "this is press release filler."
7. **No outcome lies.** Don't claim 100 users when there aren't 100 users; don't say "trending on HN" unless it actually trended.
8. **The opening line is the whole game** on every short-form platform — it's what shows in the preview. If you can't hook with the first sentence, rewrite it.
