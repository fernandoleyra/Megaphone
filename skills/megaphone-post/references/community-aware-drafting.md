# Community-platform drafting

The platforms in this file are different from feed-platforms (Bluesky/X/LinkedIn/Threads/Mastodon — those are in `platform-voice.md`). Communities have **rules, culture, and gatekeepers**. A post that works on Bluesky will get downvoted, removed, or roasted on Reddit. This file is the cultural map.

For each platform: **the shape, the things that actually work, the patterns that get nuked, and how to read the room before posting.**

---

## Reddit (per-subreddit)

The single most important rule on Reddit: **read the subreddit's stickied rules + recent posts before drafting.** Subreddits have wildly different cultures, and a generic "indie launch post" works in some, gets you banned in others.

### General Reddit drafting rules

- **Post format:** self-post (text post) with the link inside the body. Link-only posts are deprioritized and read as drive-by promotion.
- **Title:** plain, descriptive, no marketing language. Don't say "INSANE!" or "🚀". Reddit hates clickbait.
- **Body opening:** the first 2 lines are what shows in the feed preview. Earn the click with a specific hook — a number, a confession, a counter-intuitive claim.
- **Maker disclosure:** ALWAYS. Most subs require it; even when not required, lying about authorship gets the post and the account banned.
- **One paragraph on context, then one paragraph on what you built, then a paragraph on what you'd like feedback on.** Reddit responds best to "here's a thing, what do you think" framing.
- **No marketing hype.** "Powerful, fast, easy" is downvote bait. Concrete specifics ("8-second install, no signup") work.
- **Reply to every comment** in the first 4 hours. Reddit's algorithm rewards engagement; ignored posts die.
- **Don't link out to your blog/landing in the body.** Link to your GitHub instead. Links to landing pages with capture forms get flagged as spam.

### Subreddit-by-subreddit guide

#### r/SideProject
- **Audience:** indie makers and side-project shippers. ~800k subscribers. Friendliest sub for indie launches.
- **Best post type:** "I built X for Y" with a screenshot or GIF.
- **Title format:** `I built [project] - [short description of what it does]` or `[Project] - [tagline]`.
- **Tone:** casual, builder-to-builder, transparent about state ("v0.1, rough edges, would love feedback").
- **What gets upvoted:** screenshots/GIFs, stories about the build, tools that solve a real personal pain, OSS releases.
- **What gets downvoted:** waitlists with no product, AI tools without a working demo, anything that smells like pure marketing.
- **Self-promo OK?** Yes — it's the whole point of the sub. Just include the maker disclosure and don't link-spam.

#### r/programming
- **Audience:** professional developers, ~6M subscribers. Tough crowd.
- **Best post type:** technical writing — a deep blog post, a write-up of an interesting bug, a benchmark.
- **What gets upvoted:** OSS releases with substantial technical content, war stories, comparisons with data.
- **What gets nuked:** "Show me your <project>", anything that reads as launch-promo, bootcamp grads asking for help.
- **Self-promo:** technically allowed but heavily moderated. Best to post your own technical writing, not a launch.

#### r/webdev
- **Audience:** web developers, beginners through senior. ~1.5M subs.
- **Best post type:** tutorials, "how I built X with Y stack", project showcases on the weekend showcase thread.
- **Saturday Showcase:** weekly pinned thread for project promotion. Use this. Posting outside it gets removed.
- **Tone:** technical but friendlier than r/programming. "Here's the tech stack" is welcomed.

#### r/reactjs / r/Python / r/javascript / r/golang etc.
- **Audience:** language- or framework-specific. ~hundreds of thousands each.
- **Best post type:** "how I solved X with this language/framework," OSS library releases.
- **Title:** lead with the language/framework so the title tells subscribers it's relevant.
- **Tone:** technical, helpful. Show, don't tell.

#### r/SaaS
- **Audience:** SaaS founders. ~150k subs.
- **Best post type:** "I built/sold/scaled X" with numbers.
- **Tone:** founder-narrative. Transparency about MRR, churn, lessons learned outperforms hype.
- **What gets nuked:** vague "launching soon" posts, growth-hack posts.

#### r/Entrepreneur
- **Audience:** broad founders. ~3M subs but very promotional, lots of noise.
- **Best post type:** stories with concrete lessons; specific numbers; failure post-mortems.
- **What gets nuked:** anything resembling motivational hustle-culture content; vague "I made $X" without details.

#### r/InternetIsBeautiful
- **Audience:** general internet users looking for cool websites. ~16M subs.
- **Best post type:** visually striking, single-purpose websites that don't require signup.
- **Title:** describes what the site does plainly. No marketing.
- **What gets nuked:** anything requiring login before showing value.

### Reddit anti-patterns (universal)

- New account (<30 days) posting promotional content → flagged automatically
- Posting the same project across 5 subreddits in 1 hour → removed and rate-limited
- Replying with stock phrases ("Thanks!", "Great point!") → looks bot-like
- Editing the post 30 times → triggers spam filters
- Linking shorteners (bit.ly etc.) → most subs auto-remove

### Reddit pre-flight checklist

Before posting in a sub, read:
1. The sidebar rules
2. The 3 most recent successful posts (>50 upvotes) — match their shape
3. The 3 most recent removed posts (where visible) — note what got them removed

If a sub has a Saturday Showcase thread, use it instead of a top-level post. Always.

---

## Hacker News (Show HN)

HN is the loneliest, highest-stakes launch. Get on the front page and you'll get 10,000 visitors and 200 stars in a day; whiff and you'll get 3 upvotes and a single sentence in the comments.

### Submission format

- **Title:** `Show HN: <project> – <one-liner>` exactly. The em-dash matters; HN's regex catches it.
- **One-liner:** ≤8 words, names what the thing technically does. NOT marketing.
  - ✅ `Show HN: Megaphone – distribution toolkit for indie devs`
  - ✅ `Show HN: Tinybase – a tiny client-side database`
  - ❌ `Show HN: The future of indie launches is here`
- **URL:** point to a working demo or to the GitHub repo. Not to a landing page with a waitlist (HN deprioritizes these).

### The first comment (the maker comment)

You're allowed — and expected — to post a comment as the maker, immediately after submitting. This is where you tell the technical story. Format:

```
Hi HN — I built <project> over the last <N weeks/months>.

The story: I wanted to <specific personal need>, looked at <existing tools>, and was frustrated by <specific limitation>. So I built <project>, which <specific technical approach>.

Specifically: <2-3 technical implementation choices>. <Performance/scale numbers if they're real>. <The trade-offs you made>.

Open-source under <license>. Looking for <specific feedback type — design choices, edge cases, technical critique>.

Happy to answer questions in this thread.
```

The "story → tech → trade-offs → ask" structure is what HN responds to. Don't pitch; explain what you built and how.

### What works on HN

- **OSS projects** with a clean, single-file README and a working install
- **Technical depth** — a benchmark with numbers, a non-obvious implementation choice, a known-hard problem solved differently
- **Honest trade-offs** — "I picked Postgres over Mongo because…" is HN catnip
- **Specific scope** — "tiny X" or "minimal Y" works; "comprehensive platform for everything" doesn't
- **Links to source code** in the first comment

### What kills posts on HN

- **Marketing language** — "revolutionary", "next-gen", "the future of", "AI-powered", "10x faster" (without proof)
- **Vague claims** without numbers
- **Closed-source SaaS** with a free tier ad
- **Clickbait titles** — Show HN community will roast and downvote
- **"For non-technical users" framing** — HN is technical users; this framing reads as "this isn't for you"
- **Submitter karma <100** combined with promotional content — auto-flagged

### Timing

- **Tuesday or Thursday, 7–9 AM PT** is the front-page-friendly window.
- **Avoid weekends and Mondays** — Mondays have noise from inbox-clearing, weekends have low engagement.
- **Don't repost** if you flop. HN tracks reposts; they hurt more than help.

### How megaphone helps with Show HN

- Generate the title in the right format
- Generate the maker-comment in the "story → tech → trade-offs → ask" structure
- Surface the technical-depth points to lead with, drawing from the project's commits and architecture
- Remind the user: HN posting is human-only. We don't automate this.

---

## Indie Hackers

Founder-narrative platform. The community values transparency about numbers, process, and failures.

### Best post types

- **"I built X in N weeks/months"** — story-shape, with screenshots, milestones, lessons.
- **"How I got my first <N> users / dollars"** — concrete numbers and channels.
- **"Lessons from launching X"** — post-mortem after PH/HN day.
- **"I'm thinking of building Y, what do you think"** — pre-commit feedback solicitation.

### Format

- **Title:** descriptive, not clickbait. "I built [project] to solve [problem]" or "From idea to launch: [project]" both work.
- **Length:** 400–800 words. Longer than a tweet; shorter than a dev.to post.
- **Structure:** story → what you built → numbers (if any) → what you'd ask the community.
- **Screenshots:** include 1–2. The platform supports inline images well.

### Tone

- **Transparent.** Real MRR / users / churn beats vague "growing fast." Even if numbers are small ("12 users, $0 MRR, here's the journey") — the community respects honesty over puffery.
- **Founder-to-founder.** Not "as a thought leader" voice. Like writing to a peer.
- **Ask-driven.** End with a specific question that invites engagement: "Has anyone built distribution tooling for indie devs? Curious what worked for you."

### What gets upvoted

- Posts with real numbers
- Failure post-mortems with takeaways
- Build-in-public threads with weekly updates
- Tools that solve a problem indie hackers have themselves

### What gets ignored or downvoted

- "Join my waitlist" with no demo
- Generic "I'm launching soon" without specifics
- Cross-posted X-thread copy
- Coach/consultant pitches

### Engagement after posting

- Reply to every comment in the first 24 hours
- Upvote thoughtful replies
- Don't link to your blog/landing aggressively in replies; link once in the post and that's it

---

## Peerlist Launchpad

Forum-style platform for indie makers, designers, builders. Peerlist Launchpad is weekly — submissions go into the next week's batch.

### Submission

- **Project description:** ≤500 chars, focuses on what the thing does + who it's for.
- **Problem / solution split:** Peerlist's submission form has these as separate fields. Use the split — don't try to merge them into one paragraph.
- **Demo URL:** required.
- **GitHub link:** optional but lifts trust signal.
- **Screenshots / cover image:** required. The cover image shows up in the feed.

### Tone

- **Maker-to-maker.** Less polished than LinkedIn, more polished than Reddit.
- **Transparent about state.** "First week of public beta, looking for feedback" works.
- **Question-shaped engagement** — Peerlist users comment thoughtfully. End with a question.

### Side benefit

- DR-75 backlink from your Peerlist project page
- Profile doubles as a portfolio with linked GitHub, Dribbble, and Product Hunt
- Forum-style comment threads — you can have actual conversations there

---

## Hashnode

Developer-focused blogging platform. Cross-posts well from a personal blog with `canonical_url` set.

### Post format

- **Length:** 800–2500 words is the sweet spot.
- **Title:** promises a payoff. "How I built X with Y stack" / "5 lessons from shipping Z" / "A better approach to X".
- **Tags:** 5 max. Use the language/framework as primary tags; #ai, #webdev, #python pull serious tag-feed traffic.
- **Cover image:** essential. Hashnode features posts with strong cover images on their digest.
- **Code blocks:** GitHub-flavored markdown; use language hints for syntax highlighting.

### What works

- Tutorials with code that compiles
- Comparisons with data ("X vs Y: I rebuilt the same thing twice")
- Migration stories ("Why we moved from X to Y")
- Behind-the-scenes posts on architecture choices

### What doesn't

- Pure marketing content
- Posts under 500 words (looks low-effort)
- Posts without code (Hashnode is developer-blog-first)
- Posts duplicated verbatim from another platform without canonical URL set

### Cross-posting

If you blog on a personal site, set `canonical_url` to the original. Hashnode honors this — Google won't penalize you for duplicate content. This lets you publish to Hashnode AND keep SEO juice on your own site.

---

## Universal community-post rules

These apply across Reddit, IH, Peerlist, Hashnode:

1. **Read 3 recent successful posts in the venue before drafting.** Match the shape, not just the topic.
2. **One concrete detail in the first 50 words** — a number, a name, a specific thing. The reader should be able to tell what kind of post this is by line 2.
3. **Disclose maker status.** "I built this" not "I'm sharing this."
4. **End with a question.** Comments drive distribution on every community platform.
5. **Reply to every comment for at least 4 hours.** The community remembers and rewards engagement.
6. **Don't cross-post identical text.** Each platform's culture is different; rewrite per-venue.
7. **Don't oversell.** Communities have very calibrated bullshit detectors. Underplay slightly.

---

## How megaphone-post uses this file

When the user asks for a community post (Reddit / IH / HN / Peerlist / Hashnode):

1. Identify the platform AND the specific community (e.g., "Reddit r/SideProject", not just "Reddit").
2. Read the matching section of this file.
3. Read 3 recent successful posts in the actual venue (web search).
4. Generate a draft that matches the venue's shape, voice, and norms.
5. Save to `.megaphone/posts/<date>/<platform-slug>.md` (e.g., `reddit-r-sideproject.md`, `hn-show-hn.md`, `indiehackers.md`).

Drafts include a comment-header noting which platform-specific rules were applied:

```markdown
<!-- r/SideProject · self-post · maker disclosed · ≤200 char title · ends with question -->

Title: I built megaphone — distribution toolkit for indie devs (looking for feedback)

Hey r/SideProject!

I built megaphone over the last few weeks because…
```

The comment-header is for the user's reference; remove it before submitting.
