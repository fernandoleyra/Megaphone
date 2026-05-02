# Canonical platform IDs

The single source of truth for platform identifiers across `megaphone-post`, `megaphone-publish`, and `megaphone-schedule`. When a skill, file path, command-line flag, or queue row needs to name a platform, use the `id` column.

| id | Display name | Aliases | Voice doc |
|---|---|---|---|
| `bluesky` | Bluesky | `bsky` | `bluesky.md` |
| `x` | X | `twitter` | `x.md` |
| `linkedin` | LinkedIn | — | `linkedin.md` |
| `devto` | dev.to | `dev-to` | `devto.md` |
| `mastodon` | Mastodon | — | `mastodon.md` |
| `threads` | Threads | — | `threads.md` |
| `hashnode` | Hashnode | — | `hashnode.md` |
| `reddit` | Reddit | — | `reddit.md` |

## Rules

- **File names** under `.megaphone/posts/<date>/`, `.megaphone/launch/`, and `.megaphone/published/` use the `id` exactly: `bluesky.md`, not `bsky.md` or `bluesky-launch.md`.
- **Connector files** at `skills/megaphone-publish/scripts/connectors/<id>.py` match the `id`.
- **Voice docs** at `skills/megaphone-post/references/platform-voice.md` and `skills/megaphone-assets/references/platform-voice.md` reference the `Voice doc` column for per-platform tone.
- **CLI flags** (e.g. `auth.py connect <id>`, `publish.py --platform <id>`, `schedule.py once --platform <id>`) accept the `id` only.
- **Aliases** are recognized for convenience in user-facing prompts but normalized to `id` before any file write or CLI call.

## Adding a new platform

1. Add a row to this table.
2. Add `skills/megaphone-publish/scripts/connectors/<id>.py` exporting a `Connector` matching the `_base.Connector` protocol.
3. Add a voice doc entry in `skills/megaphone-post/references/platform-voice.md`.
4. Add per-platform best-time data in `skills/megaphone-schedule/references/best-time-data.md` if scheduling is supported.
5. Mention the platform in the `megaphone-publish` plugin description and SKILL.md frontmatter.

## What is *not* on this list

Platforms megaphone deliberately does not support in v1 (Hacker News, Awesome-list PRs, Instagram, TikTok, YouTube, Meta Threads — different from Bluesky's Threads if any). See `auth-setup.md` § "What megaphone-publish refuses to support" for rationale.
