# Per-platform auth setup

How to connect each platform that megaphone-publish supports. Times listed are how long this takes a first-time user.

Credentials are stored locally at `~/.megaphone/credentials/<platform>.json` (chmod 0600). Nothing leaves your machine. To delete: `python3 auth.py disconnect <platform>`.

The interactive flow is run by `auth.py connect <platform>`; this file is reference material — read it when the user asks why they need to register an OAuth app or what scope to choose.

---

## Bluesky · ~30 seconds

**Auth model:** "App passwords" — a Bluesky-specific token, not OAuth. Generated in your account settings.

**Steps:**
1. Open https://bsky.app/settings/app-passwords
2. Click "Add App Password", give it a name like "megaphone".
3. Copy the password (shown only once).
4. Run `auth.py connect bluesky` and paste your handle (e.g. `fernando.bsky.social`) and the app password.

**Stored:** `{handle, app_password}`. Validated by creating a session against `bsky.social`.

---

## dev.to · ~30 seconds

**Auth model:** Static API key. No OAuth, no rotation.

**Steps:**
1. Open https://dev.to/settings/extensions
2. Scroll to "DEV Community API Keys", click "Generate API Key", give it a name.
3. Copy the key.
4. Run `auth.py connect devto` and paste the key.

**Stored:** `{api_key}`. Used as the `api-key` header.

---

## Mastodon · ~1 minute

**Auth model:** Per-instance access token. Each Mastodon instance hosts its own OAuth, but Mastodon also lets you create a personal "application" that gives you a long-lived access token directly — much simpler than the full OAuth dance for our case.

**Steps:**
1. Sign in to your Mastodon instance (e.g. `fosstodon.org`, `hachyderm.io`, `mastodon.social`).
2. Preferences → Development → "New application".
3. Name: "Megaphone". Scopes: enable `write:statuses` (others optional).
4. Save. Open the application, copy the value labelled "Your access token".
5. Run `auth.py connect mastodon` and paste the instance hostname + the token.

**Stored:** `{instance, access_token}`. Posts go to `https://<instance>/api/v1/statuses`.

---

## Hashnode · ~1 minute

**Auth model:** Personal Access Token. GraphQL-only API.

**Steps:**
1. Open https://hashnode.com/settings/developer
2. Click "Generate New Token", give it a name.
3. Copy the token.
4. Run `auth.py connect hashnode` and paste the token. The script then queries Hashnode for the publications on your account and asks which one to use as the default; that publication's ID is stored alongside the token.

**Stored:** `{token, publication_id}`. Used as the `Authorization` header against `gql.hashnode.com`.

---

## LinkedIn · ~5 minutes

**Auth model:** OAuth2 authorization-code flow. LinkedIn requires that posts come from a registered "app", so the user creates one once.

**Why register an app:** LinkedIn restricts third-party posting to apps that have requested specific products. We need the **Share on LinkedIn** product (free, no review) + **Sign In with LinkedIn using OpenID Connect** (free) — the latter so we can read the user's `sub` claim and turn it into the `urn:li:person:...` URN that posts require.

**Steps:**
1. Open https://www.linkedin.com/developers/apps and click "Create app".
2. Fill the basics. The "company" field can be anything personal — LinkedIn auto-creates a placeholder if you don't have one.
3. Verify the app (LinkedIn sends a confirmation email).
4. Open the app → Auth tab → "OAuth 2.0 settings" → add redirect URL: `http://localhost:8765/megaphone/oauth/callback`.
5. Open the Products tab → request both **Sign In with LinkedIn using OpenID Connect** and **Share on LinkedIn**. These are auto-approved (no manual review).
6. Back to Auth tab → copy "Client ID" and "Primary Client Secret".
7. Run `auth.py connect linkedin`. Paste the IDs; a browser window will open to authorize the app on your account; on success, the redirect closes the loop and the script saves tokens.

**Stored:** `{client_id, client_secret, access_token, refresh_token, expires_at, person_urn}`. Tokens are valid for 60 days; megaphone refreshes automatically.

**Posting:** `POST https://api.linkedin.com/v2/ugcPosts` with `shareMediaCategory: NONE` for text posts. We default visibility to PUBLIC; override with `.megaphone/overrides/linkedin.json`.

---

## Reddit · ~5 minutes

**Auth model:** OAuth2 authorization-code flow with refresh tokens (`duration: permanent`).

**Steps:**
1. Open https://www.reddit.com/prefs/apps
2. Click "are you a developer? create an app".
3. Type: **web app**. Name: anything. About URL: any (Reddit accepts blanks but warns). Redirect URI: `http://localhost:8765/megaphone/oauth/callback`. Click "create app".
4. The card now shows your **client ID** (small text below the app name) and **secret** (next to "secret"). Copy both.
5. Run `auth.py connect reddit`. Paste the IDs; browser will authorize; tokens get saved.

**Stored:** `{client_id, client_secret, access_token, refresh_token, expires_at}`. Reddit access tokens expire in 1 hour; refresh tokens are permanent.

**Subreddit selection:** Reddit posts require a target subreddit. Megaphone won't guess. Add `.megaphone/overrides/reddit.json` with at least:
```json
{ "subreddit": "SideProject" }
```
Optional fields: `flair_id`, `nsfw`, `title` (otherwise the first non-blank line of the draft becomes the title).

**User-Agent:** Reddit aggressively blocks generic UAs. Megaphone identifies as `megaphone-publish/0.2 (by /u/megaphone)`. If you need to override (recommended once you have karma), edit the `USER_AGENT` constant at the top of `connectors/reddit.py`.

---

## X (Twitter) · ~5 minutes + paid API

**Heads up:** As of February 2026, posting via the X API costs ~$0.01 per post created under their pay-per-use pricing. Bot-like accounts must self-disclose in the bio. The billing relationship is between you and X; megaphone never touches your money.

**Auth model:** OAuth2 with PKCE, user-context. Refresh tokens are supported when the app requests `offline.access`.

**Steps:**
1. Open https://developer.x.com → create a project + app.
2. Configure "User authentication settings":
   - Type: Web App, Native App
   - Callback URI: `http://localhost:8765/megaphone/oauth/callback`
   - Website URL: any
3. Choose "Confidential client" (recommended) and generate a client secret. Public-client (no secret) also works.
4. Copy Client ID and Client Secret.
5. Run `auth.py connect x`. Paste IDs; browser will open the X authorize page. After consent, tokens are saved.
6. The script asks for your X handle (without @) so result URLs look right.

**Stored:** `{client_id, client_secret, access_token, refresh_token, expires_at, username}`. Access tokens last 2 hours; megaphone refreshes automatically.

**Threading:** by default, X posts a single tweet (truncated to 280 chars). To post a thread, set in `.megaphone/overrides/x.json`:
```json
{ "mode": "thread" }
```
Threads can be controlled in the draft by separating tweets with a line of `---` (preferred) — otherwise megaphone splits the body on sentence boundaries to fit 280 chars per tweet.

**Bot disclosure:** if your account is automated, X policy requires disclosing this in your profile bio. Megaphone does not edit your bio for you; do it manually before publishing.

---

## What megaphone-publish refuses to support

- **Hacker News.** Submissions must come from a real human account with karma; the API doesn't accept programmatic submits. Use `megaphone-launch` to draft the Show HN title and copy, then submit by hand.
- **Awesome-list PRs.** Maintainers explicitly reject AI-generated submissions in many lists. `megaphone-discover` produces ready-to-paste packets; you submit them.
- **Instagram / TikTok / Threads (Meta) / YouTube.** Their OAuth and content rules add a lot of complexity (business account requirements, video transcoding, vertical aspect ratios) that's out of scope for v1. Use Postiz or Upload-Post if you need them today; megaphone may add them later.
- **Cross-posting identical text.** `megaphone-post` writes a different draft per platform. The publish dispatcher only ever sends `<platform>.md` to the matching platform — it will not duplicate.
