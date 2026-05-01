# Megaphone — competitive analysis & v2 differentiation

**Date:** April 2026
**Question:** What other Claude Code plugins/skills already exist in this space, where do they overlap with megaphone, and what should we add to make ours defensibly unique?

---

## 1. The map of who's already here

I found six plugins/skills in roughly the same neighborhood. None of them is a direct one-to-one competitor — but together they fence in the territory.

| Plugin / Skill | What it does | Distribution focus? | Repo-aware? | Posts? | Launches? |
|---|---|---|---|---|---|
| **solo-founder-toolkit** (ericvtheg) | Idea validation, anti-patterns, landing-page review, build-in-public tweets from git, feature prioritization | partial — heavy on product-side | yes (git commits) | drafts X only (@levelsio style) | no |
| **OpenClaudia** | 62+ marketing skills: SEO audits, blog writing, email sequences, ads, competitor analysis | yes — but generic marketing dept, not launches | no | drafts (blog form) | no |
| **Upload-Post skill** | Actually publishes to TikTok, IG, YT, LinkedIn, FB, X, Threads, Pinterest, Reddit, Bluesky | execution layer only | no | yes — publishes live | no |
| **Postiz Claude plugin** | Schedule, manage, post, analytics across 28+ platforms | execution + scheduling | no | yes — full automation | no |
| **marketingskills / kostja94** | 160+ generic skills: CRO, copywriting, SEO, channels, page types | yes — broad marketing | no | drafts | no |
| **claude-code-marketplace README generator** | Generates README from project structure & dependencies | one slice | yes | no | no |
| **GitHub SEO & Marketing Platform** | Repo SEO, README optimization for AI citation, awesome-list management | yes — overlaps directly | partial | no | no |
| **Megaphone (us)** | Init, assets, launch plan, build-in-public posts, awesome-list discovery, weekly digest | yes — full lifecycle | yes (git + profile + voice) | drafts only | yes — phased plans |

### What this tells us

- **Solo Founder Toolkit is the closest competitor.** It also reads commits, also generates build-in-public content, also reviews landing pages. But it's product-side opinionated (what to build, when to ship) more than distribution-side.
- **Upload-Post / Postiz are not competitors — they're complements.** They publish; we plan and draft. Pairing is obvious.
- **OpenClaudia / marketingskills are huge generic libraries.** They cover surfaces we don't touch (SEO, paid ads, email sequences). They don't cover what we do well (launch orchestration, awesome-list discovery, repo-aware voice matching).
- **Nobody else does end-to-end launch orchestration.** No competitor produces a 30/14/6/0-day plan with per-channel submission packets. This is the strongest moat we already have.
- **Nobody else has a persistent repo-aware profile with voice samples.** Every competitor regenerates context per call. This compounds across uses.

---

## 2. Where we already win — keep doing this

These are real moats. Lead with them in the README and tagline.

1. **Launch orchestration with per-channel packets.** Product Hunt + Show HN + BetaList + Peerlist + DevHunt + Reddit + dev.to with the right copy, sized correctly, on the right day. Solo Founder Toolkit has no equivalent.
2. **Awesome-list and niche-directory discovery with submission instructions.** GitHub SEO Platform touches it but doesn't generate ready-to-paste submission copy.
3. **`.megaphone/profile.json` — a persistent project + voice profile.** Voice samples make our drafts sound like the user, not like an LLM. This is the single biggest quality lever and competitors don't have it.
4. **Lifecycle that chains.** init → assets → launch → post → discover → digest. Most competitors are flat slash-command lists; we're a journey.
5. **Honest about what shouldn't be auto-posted.** Show HN must be human, awesome-list PRs need maintainer permission, X requires bot disclosure. We say so plainly. Most "post-everywhere" competitors don't.
6. **Vibe-coder-specific framing.** Solo Founder Toolkit writes for founders; OpenClaudia writes for marketers. We write for someone who shipped with Lovable and doesn't know what HN is. The tone alone is a wedge.

---

## 3. Where competitors beat us — close these gaps

### Gap A — We draft but don't publish
**Solo Founder Toolkit** also drafts only, but **Upload-Post** publishes live to 10 platforms with a free tier (10 uploads/month) and **Postiz** schedules across 28+. For a non-technical user, "draft → copy → paste → 6 tabs" is a friction wall.

**Fix:** add `megaphone-publish` — a skill that hands `.megaphone/posts/<date>/*.md` off to whichever publisher the user has installed (Upload-Post, Postiz, or a generic Post-for-Me / Ayrshare config). We don't reinvent OAuth; we delegate.

### Gap B — We don't generate the landing page
Solo Founder Toolkit reviews landing pages; nobody generates one from a repo. Yet a launch without a landing page hurts.

**Fix:** add `megaphone-landing` — produces a single-file HTML+Tailwind landing page (or an Astro / Next.js scaffold for users who want more) with hero, three feature blocks, screenshots, CTA, and footer. Drops it in `landing/` ready to deploy to Vercel/Netlify in one click.

### Gap C — We don't generate the demo GIF
Every successful launch has a hero animation. Generating one is hard. No competitor does it.

**Fix:** add `megaphone-demo` — uses Playwright to open the deployed URL, click through a 4–6 step "happy path" the user describes, records the run, exports a GIF or short MP4. This is a real wedge — even a rough version beats nothing.

### Gap D — We don't validate launch readiness
A bad launch hurts the user's credibility. Solo Founder Toolkit reviews landing pages; we don't audit anything before suggesting they ship.

**Fix:** add `megaphone-validate` — pre-launch checklist: README length & hero, demo URL works, license file, screenshots present, contributing guide, no obvious typos, recent commit activity, working install command. Outputs a launch-readiness score (0–100) with the top three fixes. Either upgrade the launch skill or split it out.

### Gap E — We don't optimize for AI-assistant citations
This is a 2026-specific distribution surface that nobody has clearly named yet. ChatGPT/Claude/Perplexity now cite repos and dev.to posts as sources. Optimizing your README to be AI-citable (clear definitional sentences, FAQ structure, "what is X" sections, schema markup) is becoming a real channel. The GitHub SEO Platform mentions it.

**Fix:** add `megaphone-citecraft` — or fold into `megaphone-assets` as an "AI-discoverability pass." Specific actions: add a "What is <project>?" H2 with a one-paragraph definitional answer, restructure features as FAQ-style Q&A, ensure the GitHub topics/keywords are filled, add schema.org markup to the landing page. Easy to under-deliver here, but a 12-month moat if we get there first with a clear playbook.

### Gap F — We don't help with influencer / amplifier outreach
We mention drafting outreach DMs in the launch plan but don't actually find the people. OpenClaudia and Upload-Post don't either.

**Fix:** add `megaphone-outreach` — given the project's niche, search for recent PH launches in the same category, HN posts on the topic, dev.to authors who covered similar problems. Surface 5–10 humans who'd plausibly amplify. Draft a personalized DM per person referencing their specific past work. Human-in-loop only — no auto-DM.

### Gap G — We don't run on a schedule
The user has to remember to run `megaphone-post` and `megaphone-digest`. Competitors with cron-style scheduling (Postiz, Upload-Post) win on consistency.

**Fix:** lean on the existing `schedule` skill: add a small section to `megaphone-init` that asks "Want a Friday weekly post draft and a Monday digest?" and creates two scheduled tasks. Doesn't need new code, just docs.

### Gap H — We don't have an umbrella entrypoint
Six slash commands work for the technical user; for the non-technical user, "what skill do I run" is itself a barrier. Most plugins have this problem.

**Fix:** add `/megaphone` — a thin orchestrator skill that reads `.megaphone/` state and recommends the next sub-skill. "You don't have a profile yet → run `/megaphone-init`." "You have a profile but no assets → run `/megaphone-assets`." "Your launch is in 7 days → run `/megaphone-validate`."

---

## 4. Ranked recommendations

If we ship one v2: **`megaphone-publish`** — kills the biggest friction (drafts → live posts) and pairs us with Upload-Post / Postiz instead of competing with them.

If we ship three v2s, in order:

1. **`megaphone-publish`** — close the publish gap by delegating, not building OAuth.
2. **`megaphone-landing`** — deployable landing page is a clear wedge nobody owns.
3. **`megaphone-validate`** — pre-launch audit; the missing piece between assets and launch day. Cheap to build, immediate value.

If we want to go further:

4. **`megaphone-demo`** — Playwright-driven GIF; nobody else does this; high-effort but hero-feature potential.
5. **`megaphone`** umbrella entrypoint — UX glue that makes the 8-skill plugin feel like one product.
6. **`megaphone-outreach`** — niche amplifier finder + personalized DM drafts.
7. **`megaphone-citecraft`** — AI-search-citation optimization pass; speculative but on-trend.

Skip / deprioritize:

- Building a full publishing layer ourselves (Upload-Post and Postiz already won this).
- Generic marketing-department coverage (SEO audits, paid ads, email sequences). OpenClaudia owns this. Stay narrow.
- Idea validation / feature prioritization (Solo Founder Toolkit owns this; it's not our circle).

---

## 5. Sharper positioning

After this comparison, the one-sentence pitch should change from:

> "Distribution toolkit for vibe coders — scan a repo, generate launch assets, plan the ramp, draft posts, find awesome-lists, track traction."

to something more pointed:

> **"The launch-orchestration plugin for vibe coders. Plans the 30-day ramp, drafts every channel's submission packet, and tracks traction — paired with whichever publisher you already use."**

That move:
- Names the moat (launch orchestration) instead of listing six features
- Concedes the publish layer to Upload-Post/Postiz on purpose
- Keeps "vibe coders" as the user, which competitors don't claim

---

## 6. What to put in the README to compete

Three things competitors don't say clearly that we should:

1. **A comparison table** — explicit "Megaphone vs Upload-Post vs Solo Founder Toolkit" — readers love these and they save us a thousand words.
2. **The voice-sample step** — front and center, with a side-by-side of "AI-default" vs "voice-matched" output. This is the single thing that makes a draft worth shipping.
3. **The "what we don't automate" promise** — list HN, awesome-list PRs, X auto-replies, DMs. Frame it as a feature: respect for the platforms and the user's reputation.

---

## Sources

- [solo-founder-toolkit (ericvtheg)](https://github.com/ericvtheg/solo-founder-toolkit)
- [Show HN — Solo Founder Toolkit](https://news.ycombinator.com/item?id=46349612)
- [OpenClaudia skills (62+ marketing skills)](https://github.com/OpenClaudia/openclaudia-skills)
- [Composio — Best Marketing Skills for Claude Code 2026](https://composio.dev/content/best-marketing-skills)
- [Upload-Post skill — 10+ social platforms](https://www.upload-post.com/skills/claude-code)
- [Upload-Post on GitHub](https://github.com/Upload-Post/upload-post-skill)
- [Postiz Claude plugin — 28+ platforms](https://claude.com/plugins/postiz)
- [marketingskills (coreyhaines31)](https://github.com/coreyhaines31/marketingskills)
- [marketing-skills (kostja94, 160+ skills)](https://github.com/kostja94/marketing-skills)
- [claude-skills (alirezarezvani, 232+ skills)](https://github.com/alirezarezvani/claude-skills)
- [README generator — claude-code-marketplace](https://github.com/GLINCKER/claude-code-marketplace/blob/main/skills/documentation/readme-generator/SKILL.md)
- [GitHub Marketing Claude Code Skill](https://mcpmarket.com/tools/skills/github-growth-marketing)
- [awesome-claude-skills curated list (travisvn)](https://github.com/travisvn/awesome-claude-skills)
- [awesome-claude-code-and-skills (GetBindu)](https://github.com/GetBindu/awesome-claude-code-and-skills)
