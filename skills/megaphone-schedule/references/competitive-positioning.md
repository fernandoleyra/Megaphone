# Megaphone-schedule vs the field

## How we compare

|  | Megaphone | Buffer | Hootsuite | Later | Typefully | Publer | Postiz |
|---|---|---|---|---|---|---|---|
| One-off scheduling | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Recurring cadence (rotate from a folder) | ✓ | weak | weak | weekly slots | × | × | ✓ (single post) |
| Launch sequences (cross-platform timeline) | **first-class** | × | manual | × | × | × | × |
| Bulk import (CSV / JSON) | JSON sequences | × | 350-post bulk | × | × | unlimited CSV | × |
| Best-time intelligence | research + own history | "Smart Schedule" generic | calendar hint | account-specific (IG) | × | "peak engagement" | × |
| Per-platform draft (not cross-post same caption) | ✓ | × | × | × | × | × | limited |
| Repo-aware (knows your project, voice, releases) | ✓ | × | × | × | × | × | × |
| Local-first (no SaaS dashboard) | ✓ | × | × | × | × | × | self-host |
| Failure handling visible to user | structured types + log | undocumented | suspended | undocumented | × | × | retry |
| Pricing | free, BYO platform fees | $6–$120/mo | $49+/mo | $25+/mo | $50–$200/mo | flexible | free OSS / paid cloud |

## Where each competitor wins

**Buffer** — simplicity. The "queue + slots" model genuinely reduces decision fatigue. For users who don't care about timing, it's perfect.

**Hootsuite** — team approval workflows and bulk uploads. If you have 5 marketers reviewing every post, it earns its price.

**Later** — visual planner for Instagram. If your launch is image-first and IG-first, Later's calendar is best-in-class.

**Typefully** — drafting experience for X threads. The async-collaboration UX (drafts, comments, share-with-team) is better than anyone's.

**Publer** — bulk CSV. Upload 500 posts, edit in a grid, schedule the lot. Indie-friendly pricing.

**Postiz** — self-hostable, 30+ platform providers, recurring repost cadence. The closest in spirit to megaphone.

## Where we win

1. **Sequences are first-class.** "Launch day: Bluesky 8am, LinkedIn 9am, dev.to 10am, Mastodon 11am, Hashnode 12pm" is one JSON file that becomes one queue write. No competitor models a launch as a unit.

2. **Cadences pull from a folder.** Postiz repeats one post on a cadence; Buffer needs you to manually re-queue. We point at `posts/evergreen/bluesky/`, the runner picks the oldest unposted file, fires it, advances. Matches how indie devs actually maintain build-in-public content.

3. **Repo-aware.** Schedules live in your repo (`.megaphone/schedule/`), can be `git diff`'d, can be committed alongside your code. No SaaS dashboard to lose access to. If your laptop dies, your launch plan is in your repo.

4. **No subscription, no per-post fee.** You pay platforms what platforms charge (Bluesky free, X $0.01/post, etc.). Megaphone takes nothing in the middle. Compare to Buffer's $6–$120/mo or Hootsuite's $49+/mo.

5. **Best-time data is honest.** Industry baseline as the starting point, automatically switching to the user's own engagement data once they have ≥5 posts per platform. Always labeled with the source ("based on industry research" vs "based on your own posts").

6. **Failure handling is structured.** Same error-type taxonomy as `megaphone-publish` (`refresh_token` / `bad_body` / `rate_limit` / `network` / `unknown`), retries are bounded and visible (`.megaphone/schedule/log.jsonl`), every attempt is logged. If a post fails, the user knows why and what to do.

7. **Catch-up is sane.** If the laptop was offline for 3 days and 12 cadence fires were missed, we generate ONE catch-up post per cadence — not 12. The "apologize and spam" pattern that other tools default to is worse than just resuming.

8. **No AI gimmicks.** We don't claim to "AI-generate captions" or "AI-pick hashtags." `megaphone-post` and `megaphone-assets` already do that, in the user's voice, and they're separate skills the user can audit. We don't double-charge for the same trick.

## Where we deliberately don't compete

- **Visual content planner / Instagram grid.** Later wins this; we don't try.
- **Approval workflow for 10-person teams.** Hootsuite wins this. Megaphone is single-person-by-default; v2 may add reviewer fields but not a workflow engine.
- **Image / video editing inside the tool.** Out of scope. Use whatever you'd already use (Figma, Canva, ffmpeg).
- **TikTok / Instagram / YouTube.** Postiz and Upload-Post handle these; their OAuth and content rules are a different problem class.

## When users should NOT pick megaphone

Be honest. If the user is:
- Running an agency with many clients → use Hootsuite.
- Instagram-first → use Later.
- Drafting X threads with 3 collaborators → use Typefully.
- Bulk-loading a year of evergreen content from a CSV → use Publer.
- Already running Postiz happily → don't switch.

Megaphone is for the indie / vibe-coder shipping a software project who wants their build-in-public, launch-day, and ongoing distribution to all live alongside their code. That's the wedge.
