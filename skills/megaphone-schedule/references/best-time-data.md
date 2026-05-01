# Best-time-to-post — what's actually true in 2026

Based on industry research (Sprout Social, Later, Hootsuite, Buffer's Smart Scheduling 2025) plus indie-dev community signal as of April 2026. **Use as a baseline. Override with the user's own engagement data once you have ≥5 published posts per platform.**

## Universal pattern

Across LinkedIn, X, Bluesky, dev.to, and Threads, the strongest weekly engagement window for "knowledge work" content is **Tuesday–Thursday, 9–11 AM in the audience's local time**.

Avoid:
- **Mondays** (low focus, inbox-clearing)
- **Fridays after 1 PM** (context-switching to weekend)
- **Saturdays / Sundays** for technical content (developer audiences are off-screen)

## Per-platform

### Bluesky
- **Tue–Thu 9–10 AM local** is the sweet spot for tech-leaning content.
- The platform skews heavily developer; activity tracks office hours more closely than X does.
- Threads (multi-post Bluesky chains) outperform single posts for technical takeaways.
- Hashtags do not exist as a discovery mechanism (Bluesky cultural choice). Don't force them.

### LinkedIn
- **Wed 10 AM** is the single highest-engagement slot.
- **Tue / Thu 10–11 AM** are close behind.
- Long-form (1200–2000 chars) and document/carousel posts dwell longest.
- Posts ending in a question get 2–3× the comments; comments are the engagement signal LinkedIn rewards most.
- Avoid "I'm excited to announce" — the algorithm de-amplifies these openers in 2026.

### dev.to
- **Tue / Thu 8 AM ET** publishes catch the morning newsletter and trending feed cycle.
- Articles posted before 7 AM ET tend to fall off the feed before peak readership.
- **#showdev**, **#opensource**, **#beginners** tags drive significant tag-feed traffic. Use them when they fit honestly.
- Cover image lifts CTR materially — even a clean screenshot beats text-only.

### Reddit
- Per-subreddit. Generic "best times" don't apply.
- **Most subreddits' peaks**: Tue–Thu 7–9 AM ET (commute window) and 7–9 PM ET (evening browse).
- For r/SideProject specifically, weekend self-post performance is strong — different from weekday-only platforms.
- Always check the sub's mod-pinned thread for posting rules and any "self-promo Saturday" gates.

### Mastodon
- Tue / Thu **9–10 AM** in the user's instance timezone.
- Posts with 2–4 hashtags get the most discovery via Mastodon's federated tag feeds (unlike Bluesky).
- Cross-posting from X/Bluesky verbatim is detectable and tends to get muted; rephrase per-platform.

### X (Twitter)
- Tue–Thu 8–9 AM ET and 5–7 PM ET.
- Threads dramatically outperform single tweets for build-in-public content.
- Posts with one image or short video have ~3× the engagement of text-only.
- API posting requires bot-self-disclosure in bio (X policy as of Feb 2026); the actual best time matters less if your account doesn't follow this rule.

### Hashnode
- Tue / Thu 10 AM ET — similar shape to dev.to.
- Tag selection matters more than time-of-day; #ai, #webdev, #python are the highest-traffic tags.
- Cross-posting from your own blog (with canonical URL set) is encouraged by Hashnode itself.

## Timezone discipline

The "best window" is in the **audience's** timezone, not the author's. For a US-leaning audience, ET is the right anchor. For a primarily European audience, shift two windows:
- 8 AM CET → catch UK + EU morning
- 6 PM CET → US East morning + EU evening

For a global indie-dev audience (the megaphone default), **ET 9 AM** + **ET 6 PM** form a "double-tap" pattern that hits both halves of the planet without spamming.

## When to override the baseline

Once `.megaphone/published/<date>.jsonl` has ≥5 posts per platform with an `engagement.score` field (added by `megaphone-digest` when it pulls platform analytics), `_best_time.suggest()` switches to the user's own data. This cuts over automatically — no flag to flip.

If the user's data shows a window 2+ standard deviations from the baseline (e.g., they have a niche European/Asia audience and their best time is 6 AM ET), trust the data. The point of this whole system is to eventually outgrow generic advice.

## What to ignore

These show up in marketing copy but have no 2026 evidence:
- Specific emoji counts increasing engagement
- "5 hashtags is the magic number" (varies wildly per platform; ignore)
- Tuesday is "always" best (Wednesday is now the LinkedIn winner)
- Posting at exact :07 / :13 minutes for "algorithm trickery"
- Repost-the-same-thread-after-24-hours (X de-amplifies these in 2026)
