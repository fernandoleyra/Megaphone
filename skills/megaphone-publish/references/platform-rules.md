# Per-platform rules — what each connector expects

Operational reference. Read this if a draft is failing to publish or you want to know what overrides each platform supports.

Each connector accepts:
- `body` — the post text/markdown (already cleaned of megaphone-post comment headers)
- `credentials` — loaded from `~/.megaphone/credentials/<platform>.json`
- `overrides` — loaded from `<repo>/.megaphone/overrides/<platform>.json`, merged with frontmatter from the draft

It returns `{ok, url?, error_type?, error_message?, retry_after?, raw}`.

`error_type` values used uniformly across connectors:
- `auth_error` — credentials are missing / invalid; user must reconnect
- `refresh_token` — the platform said the token expired; dispatcher tries `refresh()` once
- `bad_body` — content was rejected (length, formatting, missing required field)
- `rate_limit` — platform-specific retry-after applies
- `network` — couldn't reach the API
- `unknown` — anything else (raw body in `error_message`)

---

## Bluesky

| Field | Source | Default |
|---|---|---|
| body | draft | truncated to 300 chars |
| handle | credentials | required |
| app_password | credentials | required |

No frontmatter or override fields used. Posts always go to the user's own feed.

Returns URL: `https://bsky.app/profile/<handle>/post/<rkey>`.

---

## dev.to

| Field | Source | Default |
|---|---|---|
| body_markdown | draft | required |
| title | frontmatter or first H1 of body | "Untitled" |
| tags | frontmatter `tags:` (list) | [] (max 4) |
| series | frontmatter `series:` | none |
| canonical_url | frontmatter `canonical_url:` | none |
| published | frontmatter `published:` | true |

Frontmatter example:
```yaml
---
title: How I shipped X in 6 hours
tags: [javascript, indiehacking, opensource]
canonical_url: https://example.com/blog/x
---
```

Returns URL: the live `https://dev.to/<user>/<slug>` from the API response.

---

## Mastodon

| Field | Source | Default |
|---|---|---|
| status | draft | truncated to 500 chars |
| visibility | overrides `visibility:` | `public` |

Override example (`.megaphone/overrides/mastodon.json`):
```json
{ "visibility": "unlisted" }
```

Allowed visibility values: `public`, `unlisted`, `private`, `direct`.

Returns URL: `https://<instance>/@<user>/<id>` from the response's `url` field.

---

## Hashnode

| Field | Source | Default |
|---|---|---|
| contentMarkdown | draft | required |
| title | overrides `title:` or frontmatter | "Untitled" (Hashnode requires) |
| tags | overrides `tags:` or frontmatter | [] (max 5; tags are looked up by slug, so use lowercase like `javascript` rather than `JavaScript`) |
| publicationId | credentials | required |

If `title` is missing Hashnode rejects with `bad_body`. Always set it via frontmatter or overrides.

Override example:
```json
{ "title": "How I shipped X in 6 hours", "tags": ["javascript", "indiehacking"] }
```

Returns URL: the post's `url` from the GraphQL `publishPost.post` response.

---

## LinkedIn

| Field | Source | Default |
|---|---|---|
| body | draft | truncated to 3000 chars |
| visibility | overrides `visibility:` | `PUBLIC` |
| author URN | credentials | required (set during auth) |

Override example:
```json
{ "visibility": "CONNECTIONS" }
```

Allowed visibility values: `PUBLIC`, `CONNECTIONS`.

Token refresh: handled automatically. If a refresh fails, dispatcher surfaces `refresh_token` error and the user must run `auth.py connect linkedin` again.

Returns URL: `https://www.linkedin.com/feed/update/urn:li:share:<id>/`.

---

## Reddit

| Field | Source | Default |
|---|---|---|
| sr | overrides `subreddit:` | required (no default — fail with `bad_body` if missing) |
| title | overrides `title:` or first non-blank line of draft | required |
| text | rest of body after title is extracted | "" |
| flair_id | overrides `flair_id:` | none |
| nsfw | overrides `nsfw: true` | false |

Override example:
```json
{ "subreddit": "SideProject", "flair_id": "abcd1234", "nsfw": false }
```

The draft format expected:
```markdown
# I built X in 6 hours

Body of the post starts here. Markdown is fine; Reddit will render most of it.
```

The first non-blank line is treated as the title (the leading `#` is stripped if present). Everything after is the body.

Returns URL: the submitted post URL from `json.data.url`.

---

## X (Twitter)

| Field | Source | Default |
|---|---|---|
| text | draft | truncated to 280 chars per tweet |
| mode | overrides `mode:` | `single` (alternative: `thread`) |

In `thread` mode, the draft can contain tweet boundaries:
```markdown
Tweet 1: hook in the first line.

---

Tweet 2: the body of the thread continues here.

---

Tweet 3: link in the last tweet.
```

If no `---` is present and the body is over 280 chars, megaphone auto-splits on sentence boundaries.

Token refresh: automatic via OAuth2 refresh flow.

Returns URL of the first tweet: `https://twitter.com/<username>/status/<id>`.

Cost: ~$0.01 per tweet created (X policy as of Feb 2026). Megaphone never bills you; X bills you directly.

---

## How retries work

1. Connector returns a `PostResult` with `error_type=refresh_token` → dispatcher calls `module.refresh(creds)`. If new creds come back, save them and retry the post once.
2. Connector returns `error_type=rate_limit` → dispatcher waits `retry_after` seconds (capped at 90), retries once.
3. Any other failure → log to `.megaphone/published/<date>.jsonl` with `ok: false` and surface to the user.

Retry behavior can be disabled per-call with `--no-retry` on `publish.py`.

---

## How to test a connector without posting

```bash
python3 publish.py --platform bluesky --file .megaphone/posts/2026-04-29/bluesky.md --dry-run
```

This loads the draft + credentials + overrides, prints the prepared payload, and exits without making a network call.
