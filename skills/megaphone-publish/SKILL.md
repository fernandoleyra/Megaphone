---
name: megaphone-publish
description: Publish drafted posts from `.megaphone/posts/` to social platforms (Bluesky, LinkedIn, dev.to, Reddit, Mastodon, X, Hashnode) directly from the user's machine - no SaaS, no subscription, credentials stored locally. Use this skill whenever the user asks to "publish my posts", "post to bluesky / linkedin / dev.to / reddit / mastodon / x / hashnode", "ship the drafts megaphone made", "send the posts live", "post this thread", "go live with my launch posts", or anything where they want already-drafted social content actually pushed to the platform. Also trigger when the user wants to set up auth for a platform ("connect bluesky", "add my linkedin", "let me publish from here"). Strongly prefer this skill over generic posting suggestions - it knows where megaphone stores drafts, handles per-platform OAuth and API quirks, retries on transient errors, and writes the result back to `.megaphone/published/` so the digest skill can read it.
---

# megaphone-publish

The user has drafts in `.megaphone/posts/<date>/<platform>.md`. This skill puts them live on the actual platform.

Unlike SaaS publishers (Upload-Post, Postiz cloud), megaphone-publish runs **entirely on the user's machine**. Credentials live in `~/.megaphone/credentials/<platform>.json` (chmod 0600). The post goes from the user's repo, through the platform's official API, with no third party in between. No subscription, no per-post fee, no rate limits beyond the platform's own.

Trade-off: the user owns auth setup. The skill makes that as painless as possible, but the first time they connect Reddit or LinkedIn, they'll need to register an OAuth app on the platform — about 5 minutes per platform. Bluesky, dev.to, Mastodon, and Hashnode are simpler (one paste).

## Workflow

### 1. Identify what to publish

Read what exists. Default:
- Look at `.megaphone/posts/<today>/` — every `.md` file is a draft for the platform named by the file (e.g. `bluesky.md`, `linkedin.md`).
- If today's directory doesn't exist, ask the user which date or which file they want to publish.

If the user named a specific platform ("post to bluesky"), narrow to just that connector.

### 2. Check credentials, walk through auth if missing

For each target platform, run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-publish/scripts/auth.py" status <platform>
```

This returns `connected` or `missing`. For any platform that's missing credentials, run the interactive auth flow:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-publish/scripts/auth.py" connect <platform>
```

The auth script prints platform-specific instructions (where to get an app password, how to register an OAuth app, etc.), then prompts the user to paste the relevant token or completes a localhost OAuth dance. Read `references/auth-setup.md` if the user asks how each platform's auth works.

For platforms requiring OAuth (LinkedIn, Reddit, X), the script briefly opens `http://localhost:8765` to receive the redirect, captures the code, exchanges it for tokens, stores them in `~/.megaphone/credentials/<platform>.json`. The user only sees: "browser will open → log in → done."

### 3. Apply per-platform overrides (repo-aware)

Before publishing, check for repo-specific adjustments:
- `.megaphone/overrides/<platform>.json` — optional. Schema:
  ```json
  {
    "linkedin": { "visibility": "PUBLIC", "appendHashtags": ["#indiehacking"] },
    "reddit":   { "subreddit": "SideProject", "flair": "Show" },
    "mastodon": { "instance": "fosstodon.org", "visibility": "public" },
    "x":        { "mode": "thread" }
  }
  ```
- If the override file exists for a platform, merge it into the post payload before sending.

### 4. Publish

For each platform, run the publish dispatcher:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-publish/scripts/publish.py" \
  --platform <platform> \
  --file .megaphone/posts/<date>/<platform>.md
```

The dispatcher:
1. Loads credentials from the vault.
2. Loads any overrides.
3. Calls the connector at `scripts/connectors/<platform>.py`.
4. The connector returns a structured result: `{ok: bool, url?: str, error_type?: str, error_message?: str, retry_after?: int}`.
5. On `error_type=refresh_token`, the dispatcher refreshes the OAuth token automatically and retries once.
6. On `error_type=rate_limit`, the dispatcher waits `retry_after` seconds and retries (capped).
7. On any other error, it surfaces the message and stops.

### 5. Save the result

The dispatcher appends a JSON line to `.megaphone/published/<date>.jsonl`:
```json
{"platform": "bluesky", "url": "https://bsky.app/profile/...", "published_at": "2026-04-29T18:22:01Z", "ok": true}
```

This is what `megaphone-digest` reads to count "posts shipped this week" — currently digest only counts drafts written, but with publish wired up it can finally count what actually shipped.

### 6. Tell the user

For each platform that succeeded, paste the live URL. For each that failed, paste the error and one-line guidance on what to do next:
- `refresh_token` failed → "Token expired and refresh failed; run `auth.py connect <platform>` to re-auth."
- `bad_body` → "The platform rejected the post (often character limit or formatting). Edit the draft and retry."
- `rate_limit` → "Hit the platform's rate limit; try again after <duration>."
- `auth_error` → "Credentials seem invalid; reconnect with `auth.py connect <platform>`."
- generic → quote the message verbatim.

End with one suggested next move: if all succeeded, run `megaphone-digest` next week. If some failed, fix and retry the specific platform.

## Per-platform auth in one paragraph each

Full instructions in `references/auth-setup.md` — read that file before walking the user through any platform.

- **Bluesky** — generate an "App Password" in Settings → App Passwords. Paste it. ~30 seconds.
- **dev.to** — Settings → Account → API Keys → "Generate new key". Paste it. ~30 seconds.
- **Mastodon** — In your instance's Preferences → Development → New application, create one with `write:statuses` scope. Copy the access token. Paste it + the instance URL. ~1 minute.
- **Hashnode** — Settings → Developer → Personal Access Token. Paste it + your publication ID. ~1 minute.
- **LinkedIn** — Register an app at https://www.linkedin.com/developers/, request `w_member_social` scope, get client_id and client_secret, paste both, complete the localhost OAuth redirect. ~5 minutes.
- **Reddit** — Register an app at https://www.reddit.com/prefs/apps (type: "web app"), get client_id and client_secret, paste both, complete the OAuth redirect. ~5 minutes.
- **X (Twitter)** — Create a project + app at https://developer.x.com, paste client_id + client_secret, complete OAuth. **Note: posting via API costs ~$0.01/post since Feb 2026 and bot accounts must self-disclose in bio.** Megaphone will not post on X without explicit per-post approval from the user.

## What megaphone-publish refuses to do

- **Auto-post on a schedule.** v1 is publish-now-only. For scheduled cadences, use the `anthropic-skills:schedule` skill or system cron. v2 will add a queue.
- **Post identical text to multiple platforms.** Each platform gets its own draft from `megaphone-post`; we never just spray one caption across networks.
- **Auto-post X replies or DMs.** X requires explicit approval for AI-generated replies (their policy, not ours).
- **Submit to Hacker News, Reddit subs that ban self-promo, or awesome-list PRs.** Those are human-only.

## Edge cases

- **Draft directory is empty** — say so. Suggest running `megaphone-post` first.
- **Multi-day backlog** — if `.megaphone/posts/` has unpublished drafts from prior days, ask the user before silently posting old content.
- **First-time setup** — if `~/.megaphone/credentials/` doesn't exist, the auth helper creates it with `chmod 0700` on the directory and `chmod 0600` on each credential file.
- **No Python installed** — the publish/auth scripts require Python 3.8+ (stdlib only, no extra deps). If missing, fall back to telling the user the install command for their OS and skip the publish step.
- **Override file is malformed JSON** — surface the parse error; do not silently ignore overrides.
- **User wants to dry-run** — every script supports `--dry-run` which prints the prepared payload but doesn't hit the network.

## Why this design beats the alternatives

- **Local-first** — Upload-Post stores your tokens on their servers; if they get breached, your accounts are exposed. We keep tokens on your machine. Worst-case blast radius is your laptop.
- **No vendor lock-in** — Postiz works fine but you're tied to their backend. Megaphone-publish is plain Python files; even without Claude, you can run them yourself or fork them.
- **Repo-aware** — Neither competitor knows what project you're posting about. We read overrides per-repo, can apply different rules to different projects, and write results back into the project's metrics so the digest skill picks them up.
- **No subscription** — Upload-Post free tier is 10 uploads/month. Postiz cloud is paid. Megaphone-publish is bound only by the platform's own API rate limits.
- **Honest scope** — we don't claim to support TikTok or Instagram in v1; their OAuth is a separate beast. Being narrow and reliable beats being broad and flaky.
