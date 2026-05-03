<p align="center">
  <img src="assets/banner.png" alt="Megaphone — launch-orchestration plugin for Claude Code" />
</p>

<h1 align="center">Megaphone</h1>

<p align="center">
  <b>The launch-orchestration plugin for indie & vibe coders.</b><br/>
  Plans your launch, drafts every channel, publishes to your accounts — fully local, no SaaS in the middle.
</p>

<p align="center">
  <a href="https://github.com/fernandoleyra/megaphone/stargazers"><img src="https://img.shields.io/github/stars/fernandoleyra/megaphone?style=flat-square" alt="Stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Claude%20Code-Plugin-8B5CF6?style=flat-square" alt="Claude Code Plugin">
  <img src="https://img.shields.io/badge/version-0.7.0-orange?style=flat-square" alt="Version">
</p>

---

You built the thing. **Megaphone helps the world find it.**

It scans your repo, drafts community-aware posts (Reddit per-subreddit, Show HN, Indie Hackers, Peerlist, Hashnode + the usual feed platforms), runs outreach to venues and amplifiers, publishes the drafts to live platforms, schedules launch sequences, audits your landing page, and tracks traction — all from inside Claude Code.

Your OAuth tokens stay on your machine. No backend. No subscription.

## Install

In Claude Code, run:

```
/plugin marketplace add fernandoleyra/megaphone
/plugin install megaphone
```

Then enable it: run `/plugin`, find **megaphone** in the list, and toggle it on. Apply with `/reload-plugins` (or restart Claude Code). You'll get **9 skills** (auto-triggered from natural language) and **6 slash commands** (for explicit invocation).

If skills or commands don't show up, run `/plugin` again and confirm megaphone is enabled, then `/reload-plugins`.

## Slash commands

| Command | What it does |
|---|---|
| `/megaphone:init` | Scan repo, write `.megaphone/profile.json` |
| `/megaphone:post` | Draft a community-aware post for a venue |
| `/megaphone:publish` | Publish a draft to a live platform |
| `/megaphone:schedule` | Schedule a post, cadence, or launch sequence |
| `/megaphone:audit` | Landing page + user journey audit |
| `/megaphone:digest` | Weekly traction digest |

The other three skills (`megaphone-assets`, `megaphone-demo`, `megaphone-outreach`) are conversational by nature — invoke them by describing what you want.

## What you get — 9 skills

These auto-trigger when Claude detects a matching intent in your message. The phrases below are examples — exact wording isn't required.

| Skill | Example phrases | What it does |
|---|---|---|
| `megaphone-init` | "set up megaphone", "init megaphone for this repo" | Scans your repo and writes `.megaphone/profile.json` capturing what your project is, who it's for, and how you sound. |
| `megaphone-assets` | "generate marketing assets", "rewrite my README", "I need a banner" | One-liner, hook, README hero, dev.to intro, landing copy. Crafts banner-image prompts (NanoBanana / DALL·E). |
| `megaphone-demo` | "make a demo gif", "record a demo" | Walks your deployed app through a 3–7 step happy path with Playwright, exports a GIF/MP4. |
| `megaphone-post` | "draft a Show HN", "draft a Reddit r/SideProject post", "post on Indie Hackers" | **Community-aware drafting.** Reads each venue's culture before writing — Reddit per-sub, HN, IH, Peerlist, Hashnode + Bluesky, X, LinkedIn, Threads, Mastodon, dev.to. |
| `megaphone-outreach` | "plan my launch", "find awesome-lists", "draft a DM to <person>" | Four phases: score venues → find amplifiers → draft personalized DMs + submission packets → build the 30/14/6/0-day launch plan. |
| `megaphone-publish` | "publish my drafts", "post to bluesky", "ship the launch posts" | Drafts go live on the actual platform — Bluesky, LinkedIn, dev.to, Reddit, Mastodon, X, Hashnode. Local OAuth, tokens never leave your machine. |
| `megaphone-schedule` | "schedule this for tuesday 10am", "set up the launch sequence" | One-offs, recurring cadences from a folder, coordinated launch-day sequences. |
| `megaphone-audit` | "audit my landing page", "audit my user journey", "pre-launch audit" | Landing page (100-pt rubric) + journey audit (70-pt + three-persona walkthrough). Names the activation moment and ranks blockers. |
| `megaphone-digest` | "weekly digest", "how's my project doing" | Stars delta, posts published, top performers, next best action. |

## Why it's different

| | Megaphone | Upload-Post | Postiz | Buffer / Hootsuite |
|---|---|---|---|---|
| Where your tokens live | **Your machine** | Their backend | Their DB | Their dashboard |
| Subscription | **None** | $0 / 10 uploads/mo | Freemium | $6–$120+/mo |
| Repo-aware drafting | ✅ | ❌ | ❌ | ❌ |
| Community-platform drafting (Reddit per-sub, HN, IH) | **First-class** | ❌ | Limited | ❌ |
| Cross-platform launch sequences | ✅ | ❌ | ❌ | ❌ |
| Amplifier discovery + personalized DMs | ✅ | ❌ | ❌ | ❌ |
| Landing + journey audits | ✅ | ❌ | ❌ | ❌ |

The trade-off: we don't do TikTok / Instagram / YouTube. **Megaphone is built for launching software** — which is what indie devs actually need.

## Design principles

- **Human-in-the-loop by default.** Every post is drafted to a file you can edit before publishing. Outreach DMs are never auto-sent.
- **Repo-aware.** Skills read your README, manifests, recent commits, deployed URL, voice samples. The more you commit, the better the posts.
- **Persistent.** Per-project state in `.megaphone/`, user-wide credentials in `~/.megaphone/credentials/` (chmod 0600). Survives across sessions. Credentials are managed via the short `megaphone-auth` command (auto-installed to `~/.local/bin` by `/megaphone:init`) — `megaphone-auth status`, `megaphone-auth connect <platform>`, `megaphone-auth disconnect <platform>`.
- **Stdlib-only Python.** No `pip install` for the core. Demo GIFs need Playwright + ffmpeg (one-time).
- **Honest about platform rules.** HN, awesome-lists, Reddit promo rules, X auto-replies — Megaphone says plainly what's automatable and what isn't.

## Typical first session

```
You: I just built a thing. Help me ship it.
Claude: [megaphone-init] → scans repo, writes .megaphone/profile.json

You: generate the assets
Claude: [megaphone-assets] → banner prompt + hook + README hero + dev.to intro

You: where should I submit and who should I DM?
Claude: [megaphone-outreach] → 15 venues scored, 10 amplifiers, personalized packets

You: draft a Show HN and an r/SideProject post
Claude: [megaphone-post] → reads HN posture and r/SideProject culture, drafts both

You: publish the Bluesky one, schedule LinkedIn for Tuesday 10am
Claude: [megaphone-publish + megaphone-schedule]

You: pre-launch audit
Claude: [megaphone-audit] → landing rubric + journey walkthrough + activation moment
```

## Requirements

- **Claude Code** (latest)
- **Python 3.10+** (stdlib only — no pip install for the core)
- **Optional:** Playwright + ffmpeg (only if you use `megaphone-demo` for GIFs)

## ⭐ Star this repo

If Megaphone helps you launch something, **please star the repo**. Stars are the single biggest signal that keeps this project alive and free for everyone. It costs you one click — and it helps another indie dev find it.

[**→ Star Megaphone on GitHub**](https://github.com/fernandoleyra/megaphone)

## Acknowledgments

Megaphone stands on the shoulders of:

- [**Anthropic Claude Code**](https://github.com/anthropics/claude-code) — the platform that made plugins like this possible.
- [**Anthropic official skills**](https://github.com/anthropics/skills) — reference patterns for the skills format.
- [**obra/superpowers**](https://github.com/obra/superpowers) — for showing what a great Claude Code plugin looks like end-to-end.

If you build something on top of Megaphone, ping me — I'd love to see it.

## License

[MIT](LICENSE) © 2026 Fernando Leyra. Free to use, fork, modify, and redistribute.
