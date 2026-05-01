# Megaphone

**The 30-day distribution system for vibe coders.** Pipe your project through Megaphone and a Claude Code session walks you from "I shipped a thing" to a launch with stars on GitHub, posts on the platforms that matter, and a calendar of follow-ups for the next month — all from your terminal, no SaaS in the middle, your OAuth tokens never leave your machine.

You built the thing with Cursor / Lovable / Replit / v0. Megaphone helps the world find it.

## What you get in 30 days

A typical Megaphone run, kicked off the day you're ready to launch:

- **Day -30 → -15** — Project profile, hero copy, banner image prompt, demo GIF. BetaList submitted (it has a 4-week wait). 5–10 awesome-lists picked. 10 amplifier targets identified with personalised DMs drafted. Build-in-public posts cadenced for Bluesky / LinkedIn / dev.to.
- **Day -14 → -7** — Product Hunt tagline & description locked. Show HN title locked. Long-form launch posts written for dev.to / Indie Hackers / Peerlist. Launch-day social sequence scheduled. Pre-launch landing + journey audits scored on a 100-point + 70-point rubric.
- **Day -6 → -1** — Sneak-peek posts go live. Peerlist / DevHunt submissions queued. README polished. First three PH comment replies pre-written.
- **Day 0** — Product Hunt @ 12:01 AM PST. Show HN @ 7 AM PT. Bluesky / LinkedIn / X primary posts go out. TinyLaunch / Open Launch / Smol Launch / Indie Hackers / dev.to all submitted. Amplifier DMs sent.
- **Day +1 → +7** — Launch-day recap drafted. Awesome-list PRs filed where it fits. Stars / posts / traction reported.

The whole thing lives in `.megaphone/` inside your repo, so it's `git diff`-able and survives across Claude Code sessions.

## The nine skills

| Skill | Triggers when you say… | What you get |
|---|---|---|
| `megaphone-init` | "set up megaphone", "init megaphone for this repo" | A `.megaphone/profile.json` capturing what your project is, who it's for, and how you sound |
| `megaphone-assets` | "generate marketing assets", "rewrite my README", "I need a banner" | One-liner, hook, README hero, dev.to intro, landing copy. Crafts banner-image prompts and asks whether to render with **NanoBanana** (Gemini 2.5 Flash Image) or **ChatGPT** (DALL·E). Hands off to `megaphone-demo` for the GIF. |
| `megaphone-demo` | "make a demo gif", "record a demo", "screencast for my README" | Walks the deployed app through a 3–7 step happy path with Playwright, exports a GIF/MP4 to `.megaphone/assets/demo/`. Config-driven so the demo regenerates when the UI changes. |
| `megaphone-post` | "draft a build-in-public post", "draft a Reddit post for r/SideProject", "write a Show HN", "post on Indie Hackers", "draft for dev.to" | **Community-aware drafting.** Feed platforms (Bluesky, X, LinkedIn, Threads, Mastodon, dev.to) AND community platforms (Reddit per-subreddit, Hacker News Show HN, Indie Hackers, Peerlist, Hashnode). Reads the venue's culture before writing. |
| `megaphone-outreach` | "plan my launch", "where should I submit", "find awesome-lists", "who should I reach out to", "draft a DM to <person>", "30-day launch plan" | Four phases: (1) score venues, (2) find amplifiers, (3) draft personalised DMs + submission packets, (4) build the dated 30/14/6/0-day launch plan. |
| `megaphone-publish` | "publish my drafts", "post to bluesky", "ship the launch posts" | Drafts go live on the actual platform — Bluesky, LinkedIn, dev.to, Reddit, Mastodon, X, Hashnode. Fully local OAuth; tokens never leave your machine. |
| `megaphone-schedule` | "schedule this for tuesday 10am", "every friday post from this folder", "set up the launch sequence" | One-offs, recurring cadences (folder-rotation), coordinated launch-day sequences. |
| `megaphone-audit` | "audit my landing page", "audit my user journey", "pre-launch audit", "where do users drop off" | Both audits in one skill. Landing: 100-pt rubric. Journey: 70-pt + three-persona walkthrough naming the activation moment. |
| `megaphone-digest` | "weekly digest", "how's my project doing" | Stars delta, posts published this week, top performers, next best action. |

## Why it's different from the competition

| | Megaphone | Upload-Post | Postiz | Buffer / Hootsuite / Later |
|---|---|---|---|---|
| Where your OAuth tokens live | `~/.megaphone/credentials/` (your machine, 0600) | Their backend | Postiz DB | Their dashboard |
| Subscription | None | $0 / 10 uploads/mo | Free OSS, paid cloud | $6–$120+/mo |
| Repo-aware | Yes | No | No | No |
| Community-platform drafting (Reddit per-sub, Show HN, IH, Peerlist) | First-class | None | Limited | None |
| Launch sequences (cross-platform 30-day timeline) | First-class | × | × | × |
| Cadences pull from a folder | Yes | × | One post repeat | × |
| Amplifier discovery + personalised DMs | Yes | × | × | × |
| Landing + journey audit | Yes | × | × | × |
| Posts to | Bluesky, LinkedIn, dev.to, Reddit, Mastodon, X, Hashnode | 10 platforms incl. TikTok / IG / YouTube | 30+ platforms | 6–28+ platforms |

The trade-off: Megaphone doesn't try to do TikTok, Instagram, YouTube. Their auth and content rules add a lot of friction. Postiz and Upload-Post are still better for those. **Megaphone is built for launching software projects and earning GitHub stars** — which is what indie devs and vibe coders are actually doing.

## How it's designed

- **Local-first.** Per-project state lives in `.megaphone/` inside your project. User-wide credentials live in `~/.megaphone/credentials/` (mode 0600, written atomically). Both survive across Claude Code sessions.
- **Human-in-the-loop by default.** Every post is drafted to a file you can edit before `megaphone-publish` puts it live. Outreach DMs are never auto-sent.
- **Repo-aware.** Skills read your repo: README, manifest files, recent commits, deployed URL, voice samples. The more you commit, the better the posts.
- **Stdlib-only Python.** No `pip install` step for the core. Demo GIFs require Playwright + ffmpeg (one-time install).
- **Honest about platform rules.** Hacker News submissions, awesome-list PRs, X auto-replies, Reddit promotional rules — the plugin says what's automatable and what isn't, plainly.

## Security

- OAuth flows use a cryptographically random `state` parameter that is verified on the redirect — blocks the classic OAuth code-injection CSRF.
- The local OAuth redirect catcher binds to loopback only and rejects any callback whose state doesn't match.
- Credential JSON files are written atomically with mode 0600 from creation (no readable window).
- All `--platform` arguments are allowlisted before any module import or subprocess call.
- The publish dispatcher always uses `sys.executable` (no PATH lookup) when invoking the publish script from the scheduler.

## Install

```bash
# In Claude Code
/plugin install <path-to-megaphone>
```

Or drop the plugin folder into your `.claude/plugins/` directory.

## Typical first session

```
You: I just built a thing with Lovable. Help me ship it.
Claude: [megaphone-init triggers] → scans repo, asks 3 short questions, writes .megaphone/profile.json

You: ok, generate the assets
Claude: [megaphone-assets triggers] → asks "banner via NanoBanana or ChatGPT?",
        crafts the image prompt, suggests demo GIF via megaphone-demo,
        writes hook + README hero + dev.to intro

You: where should I submit and who should I DM?
Claude: [megaphone-outreach triggers] → scores 15 venues, finds 10 amplifiers,
        drafts per-venue submission packets and per-amplifier personalised DMs

You: draft a Show HN and a Reddit r/SideProject post about what I shipped
Claude: [megaphone-post triggers] → reads community-drafting.md for HN posture
        and r/SideProject culture, generates two appropriate drafts

You: ok, publish the Bluesky one and schedule LinkedIn for Tuesday 10am
Claude: [megaphone-publish + megaphone-schedule trigger]

You: pre-launch audit
Claude: [megaphone-audit triggers] → runs landing audit + journey audit,
        names activation moment, ranks blockers
```

## Setting up publish auth

First-time auth is needed once per platform. Times below are first-time setup.

| Platform | Auth | Time |
|---|---|---|
| Bluesky | App password | ~30 sec |
| dev.to | API key | ~30 sec |
| Mastodon | Per-instance access token | ~1 min |
| Hashnode | Personal access token | ~1 min |
| LinkedIn | Register an OAuth app, then connect | ~5 min |
| Reddit | Register an OAuth app, then connect | ~5 min |
| X | Register an OAuth app + paid API | ~5 min |

See `skills/megaphone-publish/references/auth-setup.md` for step-by-step.

## What's NOT in the plugin

- Hacker News submission (HN is human-only by policy)
- Awesome-list PR auto-submission (maintainers reject these)
- Auto-DMs to amplifiers (against most platforms' ToS)
- TikTok / Instagram / Threads / YouTube (Meta OAuth and content rules; out of scope)
- Image / video generation (skill writes the prompt; you generate via NanoBanana or ChatGPT)

## Roadmap

- v0.7: Engagement annotation in `.megaphone/published/` (so `suggest-time` switches to the user's own data automatically; `digest` shows top-performing posts)
- v0.7: AI-assistant citation optimization pass (helps your README and dev.to posts get cited by ChatGPT/Claude/Perplexity)
- v0.8: Comment-reply drafting (the user's own posts on Reddit / dev.to / IH after they go live)
- v0.8: Newsletter pitch templates with editor-specific personalisation

## License

MIT
