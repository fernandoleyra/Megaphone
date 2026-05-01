---
name: megaphone-post
description: Draft posts from recent git activity across feed platforms (Bluesky, X, LinkedIn, Threads, Mastodon, dev.to) AND community platforms (Reddit per-subreddit, Hacker News Show HN, Indie Hackers, Peerlist, Hashnode). Use when the user says "draft a build-in-public post", "weekly update post", "draft a Reddit post for r/SideProject", "write a Show HN", "post on Indie Hackers", "draft for dev.to", "share my latest commits", "submit to <community>", or wants platform/community-specific copy from recent work. Reads the git log, reconciles with the project profile, applies per-community cultural rules (subreddit norms, HN technical posture, IH founder narrative, Peerlist forum tone) - produces drafts that match the venue, not just the platform.
---

# megaphone-post

Building in public works. Most vibe coders won't do it because they don't know what to say or how to say it on each platform. This skill turns "I shipped some stuff this week" into ready-to-paste posts for Bluesky, LinkedIn, dev.to, X, and Threads — sized correctly per platform and matched to the user's voice.

## Workflow

### 1. Load context

- Read `.megaphone/profile.json`. Required. If missing, run `megaphone-init` first.
- Read recent git activity. Default to the last 7 days. Use Bash:
  - `git log --since="7 days ago" --pretty=format:"%h %s" --no-merges`
  - `git log --since="7 days ago" --stat --no-merges` for context on the size of changes
  - For releases: `git tag --sort=-creatordate | head -3` and `git log <last-tag>..HEAD --oneline`
- Read `references/platform-voice.md` for the per-platform shape, length, and tone.

### 2. Pick the angle

The biggest mistake an automated build-in-public post makes is being a changelog. A good post has *one* angle — pick from these:

- **Ship moment** — "I just shipped X." Best when there's a clearly user-visible feature merged or released.
- **Lesson learned** — "I spent 6 hours on Y, here's what I figured out." Best when commits show a hard problem (lots of churn on one area, debug commits, revert/re-add).
- **Behind the scenes** — "Here's the unglamorous part of building Z." Best when commits are infrastructure / refactors / tests.
- **Numbers update** — "Week N: stars, users, revenue, miles run, whatever." Best when the user has metrics and a regular cadence.
- **Question** — "I'm trying to decide between A and B for X, what would you do?" Best when commits show a clear branch-point or design decision.
- **Demo** — A short clip / GIF of the new feature plus 1–2 sentences. Best when the change is visual.

Pick exactly one angle. Tell the user which one you picked and why — they should be able to redirect you in one line if they wanted a different angle.

If there's nothing meaningful in the last 7 days, say so honestly: "Looks like a quiet week — only 2 commits, both small. Want me to write a behind-the-scenes / lessons post anyway, or wait until you've shipped something?"

### 3. Decide platforms / venues

There are two flavors of post target:

**Feed platforms** (drafts are short-form social, single-author):
- Bluesky · LinkedIn · X · Threads · Mastodon · dev.to (also long-form)

**Community platforms** (drafts must obey the venue's culture, not just the platform):
- Reddit (per-subreddit — `r/SideProject`, `r/programming`, `r/SaaS`, etc.)
- Hacker News Show HN (technical, no marketing language, human submission only)
- Indie Hackers (founder narrative, transparent numbers)
- Peerlist Launchpad (forum-style, weekly batch)
- Hashnode (long-form developer blogging)

If the user said "draft a Reddit post" or "write a Show HN", treat it as a community draft and read `references/community-drafting.md` before writing — it has per-venue cultural rules that look very different from feed-platform tone.

If the user said "draft for Bluesky / LinkedIn / X / Threads / Mastodon / dev.to", treat it as a feed draft and read `references/platform-voice.md` for sizing and tone.

If unspecified, ask once with multi-select. Default suggestion: whatever `.megaphone/profile.json` lists as connected, plus Bluesky + LinkedIn for cold-start users.

Reminder for X: posting via API costs ~$0.01/post since Feb 2026 and bot accounts must self-disclose. If the user wants to post via API rather than copy/paste, the bio must say automated. Note this in the post output if relevant.

### 4. Write platform-specific drafts

For each platform, generate a draft that fits **its** shape, not a one-size-fits-all post run through a length filter.

Per-platform shape (full detail in `references/platform-voice.md`):

- **Bluesky** — 300 chars max, conversational, friendly developer culture. One concrete detail. Link last. No hashtags.
- **X** — 280 chars or thread. If thread, hook in tweet 1, the body across 3–5 tweets, link in last. Threads get more engagement than singles for build-in-public content.
- **LinkedIn** — 1200–2000 chars, paragraph form, slightly more polished. Lead with a specific moment or lesson, not "I'm excited to announce…" Open hooks that work: "I just spent 6 hours debugging…", "Here's a thing I didn't expect about…", "Week N of building <project>:". End with a question that invites comments.
- **dev.to** — 800+ words. Full post with title, intro, the lesson/story, code snippet if relevant, conclusion, tags. Use the project name and stack as tags. Set canonical URL if cross-posting.
- **Threads** — 500 chars, casual, more visual. Like Bluesky but lower bar for polish.
- **Mastodon** — 500 chars, friendly, can include hashtags (Mastodon culture supports them more than Bluesky).

For each platform, the post must:
1. Open with a hook in the **first line** (this is what shows in the preview / feed)
2. Include one concrete detail not anyone could fake (a number, a specific bug, a file name, a screenshot caption)
3. Match the voice samples from the profile
4. End with the appropriate next step (link, "DM if curious", question to readers)

### 5. Save the drafts

Write each draft to `.megaphone/posts/YYYY-MM-DD/<platform>.md` (use today's date). Prepend a comment header explaining the angle and length budget so the user understands what they're looking at:

```markdown
<!-- Bluesky · ≤300 chars · angle: ship moment -->

Just shipped a thing that's been on my list for 6 weeks: <feature>.

It does <specific concrete thing> in <specific time>. Try it: <link>
```

If any draft would exceed the platform limit, don't truncate — rewrite it to fit. Then double-check the character count and include it in the comment header.

### 6. Show the user

Give them a one-paragraph summary of what you wrote: which platforms, which angle, where the files are. Don't paste all the drafts back into chat — they can open the files. Offer one concrete follow-up: "Want me to draft a follow-up for next week, or schedule these via your posting tool?"

## Quality bar

A draft fails if any of these are true. Reject and rewrite:

- It says "I'm excited to announce" or "I'm thrilled to share"
- It uses 3+ exclamation points
- It's a generic changelog ("Today I added X, fixed Y, refactored Z") with no angle
- It claims an outcome the commits don't support
- It uses emoji in voices that don't have emoji
- It's the same text reshaped to different lengths instead of platform-native shapes
- It lies — saying "100 users" when the user doesn't have 100 users; "open-source" when the repo isn't public; etc.

## Edge cases

- **No commits this week** — say so. Offer to write a "behind the scenes / what I'm thinking about" post instead, drawing from the `notes` field in the profile.
- **Sensitive commits** — if a commit message reveals auth tokens, customer data, or anything that shouldn't be public, do NOT include it in the post. Tell the user you skipped it.
- **Very large refactor / multi-feature week** — pick the *one* most user-visible change as the angle; mention the rest as "also: X, Y" in a single line. Don't list everything.
- **First-ever post** — the post should briefly explain what the project is for new readers ("I'm building <project>, a <one-liner> for <audience>"). After the first one, assume readers know.
- **User wants to schedule rather than post** — Megaphone doesn't post. Hand the drafts to the user with a note that posting tools like Post for Me, Buffer, or Typefully take Markdown directly.
