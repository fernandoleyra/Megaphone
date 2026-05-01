# DM templates by platform

Tone, length, and structure for personalized outreach. The point of these templates is **structure, not content** — the actual words have to come from real research on the recipient. Every template assumes you've found something specific to reference about their work.

If you can't reference something specific, the DM isn't ready. Skip the recipient or do more research; don't paste a generic template with `<their_recent_post>` left as a placeholder.

## Universal structure (every platform)

1. **Open with proof of context** — name a specific recent thing they made, said, or shipped. NOT "love your work."
2. **One sentence on why they specifically might care** — the connection, in the recipient's framing.
3. **The ask, named clearly** — what would help: RT, mention, blog post, guest spot, beta feedback, intro.
4. **Easy out** — closing that doesn't make them feel guilty if they pass.

What "proof of context" looks like:

- ✅ "Your Bluesky thread last week on observability tools is what got me looking at Honeycomb."
- ✅ "I read your dev.to post on shipping with Cursor and totally relate to the 'demo data is 80% of the work' bit."
- ❌ "I love your content!"
- ❌ "I've been following you for years."
- ❌ "Your work has been a huge inspiration."

The first two are real. The last three are templates someone else has sent them 30 times.

---

## Bluesky / X DM (or @mention if no DM access)

**Length:** 2 short paragraphs, ≤300 chars total ideally.

**Tone:** casual, peer-to-peer, slightly self-deprecating is fine.

**Template:**

```
Your <specific recent post / thread / project> — <one-sentence reaction or what it made you think>.

I shipped <project> this week. <One concrete thing it does that connects to their recent work>. <Link>.

If it lands for you, would love a share. No worries if not — just thought of you.
```

**Real example:**

```
Your thread on why Postgres > Mongo for indie projects had me nodding all the way through, especially the row-level security bit.

I shipped megaphone — a Claude Code plugin that publishes build-in-public posts from your repo without a SaaS layer. Felt like something you'd appreciate given your "no Datadog for indies" stance: <link>

If it lands, a share would be huge. No worries if not.
```

---

## LinkedIn message (or comment-then-DM)

**Length:** longer than X, shorter than email. ≤180 words body. **Include a meaningful subject line** ("subject" is just the first sentence in LinkedIn's UI).

**Tone:** more polished than X. Lead with the connection point, not the project.

**Template:**

```
<First sentence — names a specific shared interest or specific recent post of theirs>

<Two sentences on what you built and why it connects to their work>

<Specific ask>. <Easy out>.
```

**Real example:**

```
I saw your LinkedIn post last week about indie founders not knowing where to launch — Product Hunt vs Hacker News vs niche directories, and the "spray and pray" pattern. Resonated.

I built megaphone, a Claude Code plugin that bundles launch orchestration + per-channel submission packets so the user gets a 30-day plan instead of 30 tabs. Thought of your post as I was finishing the launch-channel reference.

If you have 5 minutes to take a look, I'd love your thoughts — and if it fits something you're writing about, even better. Either way, thanks for shipping good content this year.
```

---

## Email

**Length:** ≤150 words. Subject line that says what it is in plain English (not "Quick question" — that's spam-shaped).

**Tone:** professional but human. Email recipients are checking quickly; surface the ask in the first 30 words.

**Subject:** `<verb noun>: <what>` — e.g., "Building open-source launch tooling — wondering if you'd take a look"

**Template:**

```
<Salutation by first name>

<First sentence — proof of context: a specific recent thing they did + your reaction>

<Two sentences: what you built + the connection to their work>

<Specific ask> <If applicable, what's in it for them>

<Easy out>

<Sign-off with link to project / your handle>
```

**Real example:**

```
Subject: Open-source launch tooling — would love your eyes on it

Hi Sarah,

Your TLDR newsletter pick last Thursday on Postiz convinced me to look at the open-source social-publishing space — and led me down a rabbit hole.

I built megaphone, a local-first Claude Code plugin that handles the build-in-public + launch flow without a SaaS layer. It's complementary to Postiz, not competitive — Postiz publishes; megaphone reads your repo and drafts what to publish, and now also schedules and audits.

I'd love your honest read on whether this is a fit for TLDR's developer subscribers. Happy to send a 90-second walkthrough video if it's easier than reading the README.

No pressure if not — and thanks for the consistent picks. They've shaped a lot of my reading this year.

— Fernando · github.com/fernando/megaphone
```

---

## GitHub issue / DM

**Use case:** the recipient is the maintainer of a tool you build on, an awesome-list, or an upstream library.

**Length:** technical. Lead with the relevance to their project.

**Where:** open an issue on their repo if it's labeled `discussion` / `community` / `feedback`. DM only if they've explicitly invited it (rare).

**Template (issue body):**

```markdown
Hi <maintainer> — not a bug, just a heads-up: I built <project> on top of <their tool> and it touches <specific thing in their tool> in <specific way>.

<One paragraph on what your project does and why their users might care>

If you'd like, I can:
- Open a PR adding <project> to your README's "ecosystem" / "built with" section
- Submit to <their awesome-list> if there is one
- Just close this — heads-up was the main thing

<Link to the project + your handle>

Thanks for shipping <their tool>. <Specific thing about it>.
```

This is a soft entry, not a pitch. Maintainers get pitched constantly; the heads-up framing makes you stand out as someone who shipped first and is being respectful second.

---

## Podcast pitch (cold email)

**Length:** ≤120 words. The host is reading on phone, fast.

**Subject:** `Pitch: <topic the show covers>, <one specific angle>`

**Template:**

```
Hi <host>,

Listened to <specific recent episode> — <one-sentence specific reaction>.

I'd be a fit for an episode on <specific angle that matches their show's tone>:
- <Specific thing 1>
- <Specific thing 2>
- <Specific thing 3>

I'm <one-line credibility marker — not a pitch, just relevance>.

Happy to send a 90-second sample of what I'd cover, or pass entirely if it's not right for the show.

— <handle> · <one-line bio>
```

Three concrete bullets in the middle is what separates a pitch that gets a yes from one that gets ignored. Hosts need to be able to imagine the conversation in 30 seconds.

---

## Awesome-list maintainer DM (rare; usually just open the PR)

Only use this if the awesome-list has explicit submission rules requiring contact, or if the project is a borderline fit and you want to ask first.

**Template:**

```
Hi <maintainer>,

I see <awesome-list> doesn't currently include <category> tools. I built <project> which fits <specific subcategory>.

I'd open a PR adding <one-line entry — exact format the list uses>. Before I do, two questions:
1. Does this fit the list's scope?
2. Anything specific you want in the entry that other entries don't have?

Project link: <url>

Thanks for maintaining the list — <specific thing about it>.
```

99% of the time, just open the PR. This template is for the 1% where the fit is uncertain.

---

## Anti-patterns to avoid

These are what gets DMs blocked or marked as spam. Read this list before sending anything.

- **"Hope this finds you well"** — instant spam-flag.
- **"I have a quick question"** — and then 200 words. People learn to skip these.
- **"I'd love to chat"** — chat about what? Specifically.
- **"Schedule a 15-minute call"** — never as the first ask. People don't take calls with strangers about indie projects.
- **Linking before introducing** — link at the end, after the reader knows whether to click.
- **Multiple asks in one DM** — pick the highest-impact ask. Let them say yes to that.
- **Leading with the project name** — "Hi! I built X, and it does Y, and I think you'd love it." The reader doesn't care yet; you have to earn the project mention.
- **Templated openers obvious to read** — "I noticed you're a leader in <field>" reads as automation. People can tell.
- **Asking for endorsement before they've used the product** — that's not how endorsements work. Ask for a try, not a yes.
- **Bumping** — if no reply after 7 days, move on. A "just checking in" follow-up rarely converts and often annoys.

---

## When NOT to DM

- The recipient has explicitly said "please don't DM me" in their bio.
- The recipient hasn't posted in 6 months — they're inactive on that platform.
- The recipient is a major figure (10k+ followers in a niche) and you have no actual connection point — they get 50 DMs a day, your odds are near zero. Better to engage publicly with their content for a few weeks first.
- The recipient is a competitor — they're not going to amplify you, and the DM looks weird.
- You're under 24 hours from launch — too late for DMs. Pre-launch warm-up is the right window.

If you're not sure whether to DM someone, the answer is usually no. Better to engage publicly with their content for a while and let them notice you, then DM later.
