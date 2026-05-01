---
name: megaphone-discover
description: Find the right awesome-lists, directories, subreddits, Discord/Slack communities, and niche launch platforms where a project belongs - with submission instructions for each. Use this skill whenever the user asks to "find awesome-lists for my project", "where should I submit", "find communities for my repo", "directories to list my project", "find subreddits where this would fit", "what awesome-list does this go on", or anything where they're looking for the right venues to share their work outside the big launch platforms. Trigger especially when the user has just shipped or is preparing to launch and wants to know where the long-tail discovery happens.
---

# megaphone-discover

Big launches (Product Hunt, Show HN) bring a spike. Awesome-lists, niche directories, and topic-relevant communities bring the *compounding* — slow, steady traffic from the people most likely to actually star and use the project. This skill finds those venues for the user's specific project and produces a ranked, ready-to-act list.

## Workflow

### 1. Load context

- Read `.megaphone/profile.json`. Required.
- Note the project's tech stack, audience, niches, and goals — these drive the search.

### 2. Generate candidate venues

Use web search and reasoning to find candidates across these venue types:

**Awesome-lists** (highest leverage for OSS / dev tools)
- Search: `"awesome <topic>" site:github.com` for each topic in the profile (stack items, audience, problem domain).
- For each candidate awesome-list, check: how recently was it updated? (active = last 90 days). What are its submission criteria? (look at CONTRIBUTING.md and recent PRs).
- Skip any awesome-list that's archived, hasn't merged a PR in 6+ months, or has explicit rules that exclude this project type.

**Niche directories / launch platforms**
- DevHunt (developer tools), TinyLaunch, Smol Launch, Open Launch, Peerlist Launchpad, Indie Hackers, BetaList, Uneed, Fazier, There's An AI For That (AI tools), AlternativeTo (anything with an alternative), G2 / Capterra (B2B SaaS, slower).
- For each, note: free vs paid submission, current wait time, audience fit.

**Subreddits**
- Search for subreddits whose recent posts are about the same topic. Skip any sub with an explicit "no self-promotion" rule unless it has a Saturday Showcase / Self-Promo thread.
- For each candidate, note: subscriber count, weekly post volume, and whether the project would actually be useful to that audience (vs spammy).

**Discord / Slack communities**
- Most are invite-only or hard to find programmatically. Use heuristics: the project's main framework usually has an official Discord linked from its docs. The audience's problem domain often has a Slack (e.g., MLOps Community, Indie Hackers Slack).
- Don't pretend to know about a community you can't verify exists.

**Newsletters**
- TLDR, Console.dev, Pointer, SaaS Weekly, Indie Hackers newsletter, Bytes, JavaScript Weekly, Python Weekly. Each has a tip-line for project mentions.
- Note submission link and editorial tone for each.

**Hacker News (manual only)**
- HN Show submissions are human-only. Include HN as a "if you're ready to spend launch day on it" note rather than a checkbox; cross-reference `megaphone-launch` if a launch plan exists.

### 3. Rank by fit and effort

For each candidate, score (1–5) on three axes:

- **Audience fit** — would the people in this venue actually use the project?
- **Effort** — how much work is the submission? (Simple PR = low effort, full landing-page submission with screenshots = high)
- **Active** — is the venue alive? (Posts within the last week / merged PRs within the last month = yes)

Sort by `(audience fit × active) / effort`. The top of the list is "do today, takes 10 minutes." The bottom is "if you have time."

Cap the output at **15 venues**. Long lists don't get acted on.

### 4. Generate submission packets

For each top-tier venue, produce a ready-to-paste submission packet. Save under `.megaphone/discover/<venue-slug>/`. Each packet has:

```markdown
# <Venue name>

**Type:** awesome-list | directory | subreddit | newsletter | community
**URL:** <where to submit>
**Wait time / cadence:** <e.g., "PRs typically merged in 1-3 days", "weekly digest sent Mondays">
**Effort:** <low | medium | high>
**Audience fit:** <1–5> · <one-line reason>

## How to submit

<Specific instructions: open a PR adding this line, post in this thread, email this address, etc.>

## Submission copy

<For awesome-lists: the exact line to add to the README, formatted to match the list's existing style.>

<For directories: the tagline, description, screenshots needed.>

<For subreddits: the post title, the body text, with explicit maker disclosure if the sub requires it.>

<For newsletters: the email pitch — 3 sentences max.>

## Notes

<Anything specific: "this maintainer prefers PRs without screenshots", "this sub bans new accounts under 30 days", "this newsletter wants a screenshot in the email".>
```

### 5. Write a master discovery file

Save the ranked list to `.megaphone/discover/index.md`:

```markdown
# Discovery results: <project name>

Generated: <ISO timestamp>

## Top 5 — do today

1. <venue> · <fit/effort> · <link to packet>
2. …

## Awesome-lists (PRs)

- <venue> · <link> · <packet>

## Directories

- <venue> · <link> · <packet>

## Subreddits

- <subreddit> · <subscribers> · <link> · <packet>

## Newsletters

- <name> · <pitch link> · <packet>

## Communities (require human entry)

- <name> · <invite or how to find> · <how to introduce yourself>
```

### 6. Hand off

Tell the user the list is in `.megaphone/discover/index.md` and the per-venue submission packets are next to it. Recommend they tackle the top 3 today — most of the leverage is in the first three tries.

## Quality and ethics rules

- **Verify before listing.** Don't include an awesome-list, subreddit, or community you couldn't actually find via search. Listing fictional venues is the fastest way to lose user trust.
- **Respect "no self-promo" rules.** If a sub or community bans self-promotion, list them anyway with a note explaining the rule and how to engage authentically (typically: contribute to others' threads first, post in dedicated showcase threads only).
- **Always disclose maker status** in the submission copy where required. Reddit and Indie Hackers typically require this. Lying about authorship gets the project banned.
- **Don't submit anywhere yourself.** The skill produces packets; the human submits. Many awesome-list maintainers explicitly reject AI-generated PRs; opening one without permission burns the relationship for the user.
- **Skip dead venues.** If an awesome-list's last commit is from 2022, it's not a discovery channel anymore. Move on.

## Edge cases

- **No obvious awesome-list for this project's niche** — say so. Suggest the user *create* one as a side play; awesome-lists are themselves SEO and stargazer magnets.
- **Project is too generic** — surface this. "I couldn't find venues that are a strong fit because the README doesn't make clear who this is for. Want to sharpen the positioning first? (`/megaphone-assets`)"
- **Project is in a saturated niche** (e.g., yet another to-do app) — be honest. Suggest 2–3 angles where the project might still find an audience (a specific niche, a specific stack, a specific use-case).
- **User asks for "anywhere I can post"** — push back gently. Spraying submissions hurts more than it helps. Recommend the top 5 and stop.
