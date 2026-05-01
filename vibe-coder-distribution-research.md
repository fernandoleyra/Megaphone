# Distribution Agent for Vibe Coders — Research & Build Plan

**Author:** prepared for Fernando, April 2026
**Working name:** *Megaphone* (placeholder — see naming options at the end)
**Goal:** A framework/app that helps non-technical AI builders ("vibe coders") distribute their projects, gain traction, and earn GitHub stars — via a repo-aware multi-agent system that does the marketing work they don't know how to do.

---

## 1. The problem, sharpened

The vibe-coding wave (Cursor, Claude, v0, Lovable, Bolt, Replit) has turned thousands of non-developers into shippers. They can build; they cannot distribute. Specifically, they tend to lack:

- A dev social presence (no X following, no Bluesky, no HN account with karma)
- Knowledge of *where* to share (Product Hunt vs Show HN vs Peerlist vs Awesome lists)
- The reflex to write build-in-public posts, README heroes, demo GIFs, launch threads
- Patience for the 30-day pre-launch ramp that actually works
- Comfort opening PRs to awesome-lists or DMing maintainers

Everything they need exists as a separate tool or playbook, but stitching it together is the work — and that's exactly what an agent system is good at.

---

## 2. What already exists

### Direct-ish competitors (the small set worth studying)

| Player | What it is | What it misses for our user |
|---|---|---|
| **Vibe Coding Builders** (vibecoding.builders) | Free directory of ~70 vibe-coded projects, profile + project listing | Pure directory. No content gen, no posting, no launch help. |
| **VIBE_ Launchpad** | Launchpad + leaderboard for vibe-coded apps; influencer matching | Single-channel, not repo-aware, no agent automation, doesn't help with GitHub or other platforms |
| **Monolit** | AI auto-publishes founder content to LinkedIn/X | Generic founder tool, doesn't read your repo or plan launches |
| **Postiz / Ocoya / Lately / Highperformr** | Agentic social schedulers across platforms | No repo awareness, no launch orchestration, generic content |
| **LangChain social-media-agent** | OSS agent that turns Slack URLs into posts, human-in-loop | Useful primitive but not a product; requires self-hosting + Slack |
| **Mintlify**, **MyTotems**, **andreasbm/readme**, **Readmecodegen** | Repo → docs site / landing page / README | Each owns one slice; nobody connects asset generation to distribution |

**The wedge:** No single product reads your repo, decides where you should launch, drafts the assets, schedules a multi-week ramp, posts (human-approved), and tracks stars — *for someone who doesn't know what HN is.* That's a defensible position, and it's what we should build.

### Infrastructure we can stand on

- **Multi-platform posting APIs** (so we don't reinvent OAuth for 12 networks):
  - **Post for Me** — TikTok, IG, FB, X, LinkedIn, YouTube, Threads, Pinterest, Bluesky. From $10/mo.
  - **Upload-Post** — same plus Reddit. From $16/mo.
  - **Zernio (formerly Late)** — 15 platforms incl. Reddit, Bluesky, Discord, Telegram.
  - **Ayrshare** — 13 platforms, free tier (20 posts/mo), Premium $99/mo.
  - None natively support **dev.to** or **Hacker News** — those need our own connectors. dev.to has a clean public API; HN is human-only (we can only draft, never post).
- **GitHub** — full GraphQL/REST API. A GitHub App with read access to repo + release webhook covers everything we need.
- **Launch directories with submit APIs or scrapeable forms:** Product Hunt (full API with maker auth), Peerlist, BetaList, DevHunt, TinyLaunch, Smol Launch, Open Launch, Indie Hackers, Hacker News (manual). DevHunt's "Product Launch List" already auto-submits to 100+ directories in one click — worth either using it or treating it as a feature inspiration.
- **Changelog/release-note generation from git** is a solved problem (git-cliff, conventional-changelog, auto-changelog) — we can layer LLM rephrasing on top.
- **Claude Agent SDK** supports orchestrator-subagent patterns natively, with parallel context-isolated agents — exactly the shape we want.

### The X/Twitter elephant

X removed the free API tier in **February 2026** and moved to pay-per-use (~$0.01 per post written). Bot accounts must self-identify; AI-generated replies need explicit X approval. This means:

- Don't subsidize X posting for users; let each user bring their own X dev key, or drop X entirely from the MVP.
- Lean on **Bluesky, LinkedIn, Reddit, dev.to, Threads, Mastodon** for the core "auto-post" surface — all have free or cheap APIs.
- Treat X as draft-only or pay-per-use in v1.

---

## 3. The mental model

A vibe coder's distribution lifecycle, broken into the surfaces an agent can own:

1. **Understand the project** — read the repo, README, screenshots, commits, package.json, deployed URL.
2. **Generate assets** — better README, hero image, demo GIF prompt, one-liner, 280-char hook, 1500-char dev.to intro, landing page copy, Product Hunt description, Show HN title.
3. **Plan the launch** — pick channels, build a 30/14/6/0-day calendar around a target launch date.
4. **Build in public** — turn each meaningful commit, PR merge, or weekly summary into a post-per-platform.
5. **Distribute** — post on the schedule across connected accounts; submit to directories; draft outreach DMs and PRs to awesome-lists.
6. **Track** — stars, upvotes, traffic, follower growth; weekly digest with next best action.

Six surfaces → six specialized agents under one orchestrator. None of them have to be brilliant; they have to be on time.

---

## 4. Proposed agent architecture

```
                       ┌─────────────────────────┐
                       │      Orchestrator        │
                       │  (Claude Agent SDK)      │
                       └────┬────────────┬───────┘
                            │            │
         ┌──────────────────┼────────────┼──────────────────┐
         │                  │            │                  │
   ┌─────▼──────┐    ┌──────▼─────┐ ┌────▼────────┐   ┌─────▼──────┐
   │ Project    │    │ Asset      │ │ Launch      │   │ Content    │
   │ Scout      │    │ Generator  │ │ Strategist  │   │ Engine     │
   │            │    │            │ │             │   │            │
   │ reads repo │    │ README,    │ │ 30-day plan │   │ daily/wkly │
   │ + commits  │    │ landing,   │ │ per channel │   │ build-in-  │
   │ + screen-  │    │ taglines,  │ │ + drafts    │   │ public     │
   │ shots      │    │ hero img   │ │             │   │ posts      │
   └─────┬──────┘    └──────┬─────┘ └──────┬──────┘   └────┬───────┘
         │                  │              │               │
         └──────────────────┴──────┬───────┴───────────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Review Queue     │  ← human sees every draft
                          │  (web UI)         │     before it ships
                          └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
       ┌──────▼──────┐      ┌──────▼──────┐     ┌───────▼──────┐
       │ Distributor │      │  Outreach   │     │   Tracker    │
       │             │      │             │     │              │
       │ unified     │      │ awesome-    │     │ stars, PH    │
       │ social API, │      │ lists PRs,  │     │ upvotes,     │
       │ PH/Peerlist │      │ Discord/    │     │ traffic,     │
       │ submit      │      │ Slack DMs   │     │ digest       │
       └─────────────┘      └─────────────┘     └──────────────┘
```

**Why split it this way:** each agent has a focused tool set and short context. Project Scout and Asset Generator are repo-heavy. Launch Strategist needs the calendar and channel rules. Content Engine watches git activity. Distributor only handles auth and the posting APIs. Outreach is the only one that has to do open-web reasoning. Tracker is read-only. The orchestrator picks "the next thing the user should be told about" — a lot of the UX win is in *not* dumping all six agents on a non-technical user at once.

### Two automation tiers (recommendation)

| Tier | Default | What's autonomous | What needs approval |
|---|---|---|---|
| **Co-pilot** | yes, for first 30 days | research, drafting, scheduling | every post, every PR, every outreach DM |
| **Autopilot** | opt-in, per-channel, after 14 approved drafts | drafting + posting on the cadence | launches, outreach, anything paid |

**Why a tiered model:** the people with no social presence are also the people most likely to get burned by an over-eager bot. Earn autonomy. Always disclose bot accounts (legally required on X anyway). Give the user a kill switch in the UI header.

---

## 5. What's safe for an agent vs. what isn't

| Task | Autonomy | Why |
|---|---|---|
| Read repo, generate README/landing | full | reversible, low stakes |
| Draft posts/threads | full | nothing posts without approval (tier 1) |
| Schedule already-approved posts | full | user pre-approved the content |
| Open issues/PRs to awesome-lists | **draft only** | maintainers will blacklist spammers; one bad PR poisons the well |
| Reply to comments on launches | **draft only** | tone/community fit is hard; X explicitly requires approval for AI replies |
| Cross-post identical content | full but rate-limited | platforms penalize duplicates — agent should rephrase per platform |
| Buy/run ads | **never auto** | money + reputation |
| DM creators / influencers | **draft only, user sends** | most platforms ban DM automation |
| Track metrics, generate digests | full | read-only |

---

## 6. MVP scope (4 weeks of Claude Code work)

Cut everything that isn't on this list.

**In:**
- GitHub App connection (read repo + releases)
- Project Scout: parse README, package.json/pyproject/cargo, screenshots, deployed URL, recent commits
- Asset Generator: hero one-liner, 280-char hook, 1000-char description, README rewrite, dev.to intro
- Launch Strategist: 30-day plan for **Product Hunt + Show HN + BetaList + Peerlist** only
- Content Engine: weekly summary post drafted from the week's commits/PRs/releases
- Review queue (web UI: cards with edit-and-approve)
- Distributor: post to **Bluesky + LinkedIn + dev.to** through one unified API (start with Post for Me or Ayrshare free tier; build a thin dev.to connector ourselves)
- Awesome-list **discovery** (read-only — surface the 5 most relevant lists with submission instructions; no auto-PRs yet)
- Star/follower tracker, weekly email digest

**Out (Phase 2):**
- X integration (BYO API key or skip)
- Reddit (community gatekeeping is intense, do this carefully)
- Outreach agent that actually opens PRs
- Autopilot tier
- Multi-project / team accounts
- Demo-video generation
- Influencer matching

---

## 7. Tech stack (opinions, not religion)

| Layer | Pick | Why |
|---|---|---|
| Web app | **Next.js 15 + Tailwind + shadcn/ui** | fastest path; review queue is mostly cards |
| Hosting | **Vercel** | one click, free tier fine for MVP |
| DB | **Supabase (Postgres)** | auth, row-level security, storage for images, all in one |
| Background jobs | **Inngest** or **Trigger.dev** | step functions match agent workflows; good retry/observability |
| LLM | **Claude (Agent SDK)** with tool use; Haiku for cheap drafts, Sonnet/Opus for launch-day generation | aligns with what you're building it in |
| Vector store | **pgvector in Supabase** | optional; only needed if we let agents recall past posts/style |
| Social posting | **Post for Me** to start ($10/mo, covers Bluesky/LinkedIn/Threads); fall back to native APIs as needed | beats writing 8 OAuth flows |
| GitHub | **Octokit + GitHub App** | webhooks for releases, PRs, stars |
| Analytics | **PostHog** | free tier, funnels, session replay |
| Auth | **Supabase Auth** | matches DB choice |
| Email digest | **Resend** | clean API, React Email templates |

Total monthly cost to run for one user during MVP: **~$10–25** (Supabase free, Vercel free, Post for Me $10, Anthropic API usage, Resend free).

---

## 8. Step-by-step build plan for Claude Code

Each step is sized for one Claude Code session. Hand them off in order.

**Week 1 — foundations**
1. Scaffold Next.js + Tailwind + shadcn + Supabase + Inngest + Anthropic SDK; Supabase schema for `users`, `projects`, `assets`, `posts`, `schedules`, `metrics`. Auth flow.
2. GitHub App: create the app, install flow, `projects` row created on connect; webhook handler for `release.published` and `push`.
3. Project Scout agent: tool that fetches repo tree, README, manifest files, last 50 commits, deployed URL (parsed from package.json/README), and screenshots from `/docs` or `/.github`. Output: `project_profile` JSON stored on `projects`.

**Week 2 — generation**
4. Asset Generator agent: from `project_profile`, produce one-liner, hook, description, README rewrite, dev.to intro. Store as `assets` rows; render in UI for edit-and-approve.
5. Hero image generator: prompt → image via the user's choice of provider (Anthropic doesn't generate images; use Replicate or DALL·E or skip in v1 and just suggest the prompt).
6. Launch Strategist agent: input launch date + channels; output a `schedule` with rows for every action (`pre-launch tweet`, `submit to BetaList`, `Product Hunt teaser`, etc.) keyed to dates.

**Week 3 — distribution**
7. Review-queue UI: card list of pending posts with platform, scheduled time, edit-in-place, approve/reject.
8. Distributor: integrate Post for Me; on approval, schedule via their API or our own cron through Inngest. Build a thin **dev.to connector** ourselves (single POST to `/api/articles`).
9. Content Engine: webhook handler that, on `release.published` or weekly cron, generates platform-specific posts and drops them into the review queue.

**Week 4 — feedback loop**
10. Tracker: poll GitHub stars + PH/Peerlist results + Bluesky engagement; store time-series in `metrics`. Daily snapshot.
11. Awesome-list discovery: search-API call against GitHub topics + LLM rerank; render a "submit to these 5 lists" page with copy-paste instructions.
12. Weekly email digest: stars delta, top posts, next 7 days of scheduled actions. Resend + React Email.

**Week 5+ buffer** — fixes, onboarding polish, beta with 10 vibe coders from `vibecoding.builders`.

### Things to decide before starting

- **Single project or multi-project per user?** (Recommend: single in v1; multi in v2.)
- **Pricing model?** Free during beta; $19/mo per project sustainable when you're paying for Post for Me + Anthropic.
- **Where's the bot disclosure?** Auto-add "🤖 drafted with Megaphone" footer on first post per platform; let user disable.
- **Brand voice capture** — do we ask the user for 3 examples of their voice on signup, or generate from scratch? (Recommend: ask. 3 paste-ins, ~2 minutes, dramatically better drafts.)

---

## 9. Risks & how to dodge them

| Risk | Mitigation |
|---|---|
| Platforms ban auto-posters | Use sanctioned APIs only; respect rate limits; add bot disclosure; never auto-DM |
| Generic AI-sounding posts | Voice-capture step at signup; run drafts through a "does this sound like a person" critic agent before showing |
| Low-quality launches that hurt the user's credibility | Human-in-loop default; a "launch readiness" check that flags missing screenshots, vague README, no demo |
| User connects everything, never approves anything | Onboarding ships *one* post on day 1 (cheap win); weekly nag email |
| X API cost surprises | BYO X key or skip X; never silently bill the user for posts |
| Awesome-list maintainers blacklist us | Stay in "draft + show user how to submit" mode for v1; only graduate to auto-PR after explicit list-by-list permission |
| Spammy reputation drag | Optional but smart: don't let the same user account post identical text across networks; per-platform rephrase |

---

## 10. Naming options (pick one before week 2)

- **Megaphone** — clear, friendly
- **Liftoff** — launch-coded, available .dev domain check
- **Hype** — short, vibe-coder native
- **Shipmate** — couples with build-in-public culture
- **Boost** — overloaded but searchable
- **Halo** — distribution = the halo around your repo

---

## 11. Sources

- [Indie Hacker SaaS Stack 2026 — TLDL](https://www.tldl.io/resources/indie-hacker-saas-stack-2026)
- [Open Source Marketing Playbook for Indie Hackers — Indie Radar](https://indieradar.app/blog/open-source-marketing-playbook-indie-hackers)
- [Indie Dev Toolkit — David Dias (GitHub)](https://github.com/thedaviddias/indie-dev-toolkit)
- [LangChain social-media-agent (GitHub)](https://github.com/langchain-ai/social-media-agent)
- [Postiz — agentic social scheduling](https://postiz.com/)
- [Ocoya — AI social management](https://www.ocoya.com/)
- [Lately — AI social agent (Kately)](https://www.lately.ai/)
- [Highperformr — AI agents for solo creators](https://www.highperformr.ai/tools/ai-agents)
- [andreasbm/readme — auto README generator](https://github.com/andreasbm/readme)
- [Readmecodegen — AI README generator](https://www.readmecodegen.com/builder)
- [Mintlify auto-docs from repos](https://www.mintlify.com/blog/auto-generate-docs-from-repos)
- [MyTotems — landing page for GitHub projects](https://www.mytotems.page/)
- [Vibe Coding Builders directory](https://www.vibecoding.builders)
- [TechCrunch — Lovable launches mobile vibe-coding (Apr 2026)](https://techcrunch.com/2026/04/28/lovable-launches-its-vibe-coding-app-on-ios-and-android/)
- [Why I Built a Marketplace for Vibe-Coded Apps — dev.to (VIBE_)](https://dev.to/imran_hassan_df9c98d874de/why-i-built-a-marketplace-for-vibe-coded-apps-3gho)
- [Product Hunt Launch Checklist 2026 — Teract](https://www.teract.ai/resources/product-hunt-launch-checklist-2026)
- [How to Launch on Product Hunt 2026 — LaunchList](https://getlaunchlist.com/blog/how-to-launch-on-product-hunt-2026)
- [Product Hunt vs Hacker News — Poindeo](https://poindeo.com/blog/product-hunt-vs-hacker-news)
- [Peerlist Launchpad](https://peerlist.io/launchpad/2026/week/18)
- [DevHunt — Product Launch List (100+ directories)](https://devhunt.org/tool/product-launch-list)
- [Smol Launch — 13 Best Product Hunt Alternatives 2026](https://smollaunch.com/product-hunt-alternatives)
- [10 Proven Ways to Boost Your GitHub Stars in 2026 — Scrapegraph](https://scrapegraphai.com/blog/gh-stars)
- [The Ultimate Playbook for Getting More GitHub Stars — HackerNoon](https://hackernoon.com/the-ultimate-playbook-for-getting-more-github-stars)
- [GitHub Star Growth: 9 Levers That Compound — dev.to](https://dev.to/iris1031/github-star-growth-9-levers-that-compound-in-2026-15d)
- [Building an Awesome List That Gets Stars — dev.to](https://dev.to/glue_admin_3465093919ac6b/building-an-awesome-list-that-actually-gets-stars-step-by-step-g6f)
- [sindresorhus/awesome — canonical list of awesome lists](https://github.com/sindresorhus/awesome)
- [Post for Me — unified social posting API](https://www.postforme.dev/)
- [Upload-Post — multi-platform posting](https://www.upload-post.com/how-to/post-to-multiple-social-media-at-once/)
- [Zernio (formerly Late) — 15-platform social API](https://getlate.dev/)
- [Ayrshare — social media API](https://www.ayrshare.com/)
- [X API Pricing 2026 — Xpoz](https://www.xpoz.ai/blog/guides/understanding-twitter-api-pricing-tiers-and-alternatives/)
- [X API pay-per-use launch — We Are Founders](https://www.wearefounders.uk/the-x-api-price-hike-a-blow-to-indie-hackers/)
- [Multi-agent sessions — Claude API docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)
- [Building multi-agent systems — when and how — Claude blog](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them)
- [Build an AI Marketing Company with Paperclip and Claude Code — MindStudio](https://www.mindstudio.ai/blog/build-multi-agent-company-paperclip-claude-code)
- [git-cliff — customizable changelog generator](https://git-cliff.org/)
- [conventional-changelog (GitHub)](https://github.com/conventional-changelog/conventional-changelog)
