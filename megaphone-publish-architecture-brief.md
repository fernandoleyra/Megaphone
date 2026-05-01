# megaphone-publish Architecture Brief
## Research into Upload-Post & Postiz

---

## Section 1: Upload-Post — Architecture & Approach

**Model:** SaaS proxy with hosted API gateway.

**Auth:** User registers at upload-post.com, connects social accounts via OAuth to Upload-Post's dashboard, creates a "Profile" (which aggregates their connected accounts), then generates an API key. The skill calls the Upload-Post API with that key. **User never handles direct OAuth tokens; they're stored server-side on Upload-Post's infrastructure.** This is the core trade-off: simplicity for the skill author (just HTTP + API key) vs. vendor lock-in.

**What the skill does:** Thin wrapper. `SKILL.md` documents ~8 HTTP endpoints. The skill teaches Claude to call curl-like patterns against `https://api.upload-post.com/api/upload`, `upload_photos`, `upload_text`, `upload_document`, and status/scheduling endpoints. No SDK, no concurrency logic, no retry state machine — that's all server-side.

**Per-platform auth flow:** Invisible to the skill. Upload-Post's dashboard handles TikTok OAuth, Instagram OAuth, LinkedIn OAuth, etc. The skill never touches those. This is why it scales to 10 platforms with minimal code.

**Media handling:** FFmpeg support is _opt-in_. The skill can call `/ffmpeg` endpoint to transcode videos before posting, but Upload-Post charges per-minute (free 30min/mo, $12/mo plan = 300min). The skill documents command templates (H.264 encoding, aspect ratio scaling). All re-encoding happens server-side.

**Scheduling:** Native support. Pass `scheduled_date` (ISO-8601) + `timezone` (IANA) in the POST body. Upload-Post returns a `job_id`. No local queue needed — the skill just sets the parameter and forgets.

**Platforms:** TikTok, Instagram, YouTube, LinkedIn, Facebook, X, Threads, Pinterest, Reddit, Bluesky. Media type matrix is clean: videos, photos, carousels, text, documents (LinkedIn only).

**Strengths:**
- Minimal surface area. Skill is ~100 lines of SKILL.md prose + curl examples.
- No local auth state to manage. User's tokens live in Upload-Post's vault.
- Cross-platform reach (10 major platforms).
- FFmpeg on demand (though paid).
- Scheduling baked in.

**Weaknesses:**
- Entirely dependent on Upload-Post service health. If their API is down, publishing is blocked.
- No local-first option. Vibe coders cannot self-host.
- Limited analytics. Upload-Post offers `/analytics/<profile>` but it's basic (followers, impressions, reach).
- Free tier: 10 uploads/month. That's _extremely_ tight for a builder shipping build-in-public content weekly.
- No real-time feedback. Async uploads return a `request_id`; polling for status is your responsibility.
- Platform limitations hidden behind Upload-Post's constraints. If Instagram breaks their API, Upload-Post users wait for a fix.
- Rate limiting: X is rate-capped at 300 posts/3 hours. That's per-user, so if your account hits it, you're blocked.
- Media requirements docs are stale-able. If TikTok changes aspect ratios, the requirement table is out of sync.
- No way to customize per-platform workflows. You post to TikTok and Instagram with the same Caption — no "special message for LinkedIn professionals."

---

## Section 2: Postiz — Architecture & Approach

**Model:** Open-source, self-hosted Next.js (frontend) + NestJS (backend) + Temporal (orchestrator). Full vertical stack. The Claude plugin is an MCP (Model Context Protocol) server wrapping the backend.

**Backend stack:** 
- `apps/backend` (NestJS) handles REST API, database (Prisma ORM), OAuth flows.
- `apps/orchestrator` (Temporal) is a _separate process_ that runs workflows and activities. It's a temporal server + worker that watches for scheduled posts and executes them.
- `libraries/nestjs-libraries/src/integrations/social/` contains 30+ provider implementations (X, LinkedIn, Reddit, Bluesky, Mastodon, Threads, Hashnode, dev.to, Discord, Slack, TikTok, Instagram, Facebook, Pinterest, YouTube, etc.).

**Provider abstraction:** Each platform gets a `.provider.ts` file (e.g., `x.provider.ts`, `bluesky.provider.ts`). All extend `SocialAbstract` base class and implement `SocialProvider` interface.

```
SocialProvider extends IAuthenticator + ISocialMediaIntegration:
  - authenticate(code, codeVerifier): generates OAuth tokens + user info
  - refreshToken(token): renews expired OAuth
  - post(id, accessToken, postDetails[]): publishes to platform
  - comment?(id, postId, lastCommentId, accessToken, postDetails[]): posts comments/threads
  - analytics?(id, accessToken, date): retrieves analytics
  - maxLength(additionalSettings?): character limit for platform
  - mention?(token, query, id): autocomplete for @mentions
  - fetchPageInformation?: for fetching page IDs (Facebook, LinkedIn)
```

**OAuth state management:** Providers implement their own auth. Example flow (Reddit):
1. `generateAuthUrl()` returns OAuth URL with state + PKCE code_verifier.
2. User authorizes, gets `code`.
3. `authenticate({ code, codeVerifier })` exchanges code for access + refresh tokens.
4. Tokens stored in Prisma DB (`Integration` table).
5. When posting, `refreshToken()` is called if token expired (happens in workflow via `refreshTokenWithCause` activity).

Error handling is sophisticated: if a provider detects `401` + `"Unsupported Authentication"`, it throws `RefreshToken` exception. The workflow catches that, re-authenticates, and retries the post. This is why each provider has an `handleErrors(body: string, status: number)` method that parses platform-specific error strings.

**Scheduler & queue:** Temporal Workflows + Activities. 
- `postWorkflowV102` is the main workflow. It:
  1. Waits for `post.publishDate` to arrive.
  2. Fetches the post + comments from DB.
  3. Validates account is not disabled/refresh-needed.
  4. Calls `postSocial()` activity for the main post.
  5. If platform supports comments, calls `postComment()` for each child post.
  6. On success, updates DB with post URL and sends notification.
  7. On failure (token expired, rate limit, etc.), handles retry/refresh logic.
- Task queues are provider-specific: `taskQueue: post.integration.providerIdentifier.split('-')[0].toLowerCase()`. So all X posts go to `x` queue, all LinkedIn to `linkedin`, etc. This enables per-provider concurrency control.
- Retries are baked in: `maximumAttempts: 3`, `backoffCoefficient: 1`, `initialInterval: '2 minutes'`.
- Signal-based wake-up: if a user schedules a post for 10am and it's currently 9:45am, the workflow is created but sleeps until 10am via `sleep(dayjs(post.publishDate).diff(dayjs(), 'millisecond'))`.

**Activities** (in `/orchestrator/activities/`):
- `post.activity.ts`: Contains the actual platform posting logic, wrapped in `@ActivityMethod()` decorators. Activities are like functions that Temporal can retry independently.
- Database queries (`getPostsList`, `updatePost`, `changeState`, etc.) are activities because Temporal needs to handle failures/retries.

**The Claude plugin integration:** File: `/libraries/nestjs-libraries/src/chat/start.mcp.ts`.

Postiz exposes an MCP server. The server wraps a Mastra agent (`agent = mastra.getAgent('postiz')`). This agent has tools (the integration methods exposed via decorators like `@Tool()`, `@Plug()`). When Claude calls the plugin, it's making HTTP calls to `/mcp` or `/mcp-oauth` endpoints on the Postiz backend. The backend resolves the request via organization context, then returns tool results.

**Key insight:** The plugin doesn't ship posting logic. It ships an API gateway to the Postiz backend. If you install Postiz, you get the plugin for free. If you want to use the plugin without Postiz, you can't — it's not standalone.

**Strengths:**
- Truly multi-platform (30+ integrations). Easy to add new ones: write a `.provider.ts`, add to `socialIntegrationList` in `integration.manager.ts`, done.
- Self-hostable. Run the entire stack locally (even though it needs a Temporal server, which adds complexity).
- Per-provider concurrency control. X's queue can run max 1 job at a time; others can run more.
- Token refresh is automatic and intelligent. Platform-specific error strings are parsed and translated into retry/refresh actions.
- Composable comments. Support for threading (main post → comment → nested comment chain).
- Workspace/organization multi-tenancy. Built-in from the DB schema.
- Analytics hooks. Providers can implement `analytics()` for retrieving follower counts, impressions, etc.
- Webhooks. Postiz can trigger external systems when a post succeeds/fails.

**Weaknesses:**
- Complexity. Temporal adds operational burden. You need to run an orchestrator process, set up a task queue, handle workflow versioning (see `post.workflow.v1.0.2.ts` — there are multiple versions!). This is not local-first.
- OAuth complexity. Every provider must implement its own OAuth flow. If you want to add a 31st platform, you need to handle its auth, token refresh, error codes, rate limits. That's 500+ lines of code per provider.
- Database dependency. Workflows depend on Prisma queries. If DB is slow, the workflow stalls.
- Activation history. Temporal stores all workflow execution history. Over time, this grows and can affect performance.
- The Claude plugin is not a plugin in the traditional sense. It's a thin HTTP gateway. You still need the Postiz backend running.
- Rate limiting is per-provider but static. If X changes its rate limits, you need to update `override maxConcurrentJob = 1`.
- Media handling is provider-specific. No centralized re-encoding. If a provider needs image resize, it implements it itself (see Bluesky reducing images via Sharp).

---

## Section 3: What We Should Steal

**From Upload-Post:**
- **API-first design philosophy.** Keep the skill dumb. HTTP calls, JSON responses, minimal state on the client.
- **Single profile ↔ many accounts.** Users group their connected accounts under a logical name ("my-brand"). This is simpler UX than managing individual account tokens.
- **FFmpeg as a service.** Media re-encoding on demand, not bundled. Charge for minutes used or offer unlimited in paid tier.
- **Unified scheduling.** One `scheduled_date` + `timezone` parameter across all platforms. Don't make users learn per-platform scheduling.
- **Simple error messages.** When posting fails, tell Claude (and the user) why in plain English, not platform error codes.

**From Postiz:**
- **SocialAbstract base class + SocialProvider interface.** The shape is right. Every provider needs auth, posting, error handling, concurrency limits.
- **Per-provider error handling.** `handleErrors(body: string, status: number)` is the pattern. Each platform returns different error strings (X says "duplicate-rules", Reddit says something else). Standardize on a common error type: `{ type: 'refresh-token' | 'bad-body' | 'retry', value: string }`.
- **Task queues for concurrency.** Don't post to all platforms in parallel. Route X posts to the `x` queue (concurrency=1), LinkedIn to `linkedin` (concurrency=2), etc.
- **Workflow + activity separation.** Workflows define the happy path (schedule → wait → post → notify). Activities handle I/O (HTTP calls, DB queries). Retry logic lives in activities.
- **Token refresh signal.** If a provider throws `RefreshToken`, the workflow catches it and calls `refreshTokenWithCause()` before retrying. This handles OAuth token expiry gracefully.
- **Search attributes for debugging.** Temporal workflows support typed search attributes. Store `postId` and `organizationId` so you can query "show me all posts for org X that are stuck".

---

## Section 4: Where We Can Do Better

We're building a **local-first Claude Code skill** (no SaaS), runs on the user's machine, repo-aware, no separate dashboard. Here's what we can improve:

**1. Local-first auth with encrypted vault.**
Neither Upload-Post nor Postiz offer local token storage without infrastructure. We store OAuth tokens locally on the user's machine in an encrypted JSON file (e.g., `~/.megaphone/oauth-vault.json`, decrypted with a master key derived from `MEGAPHONE_SECRET`). This means:
- No SaaS to break.
- No data exfil. Tokens never leave the user's machine.
- Transparent to Claude: the skill reads from the vault, generates a short-lived session token if needed, posts, done.
- Downside: harder to share accounts across machines (users need to copy the vault file or re-auth on each machine).

**2. Repo-aware content adapting.**
Upload-Post and Postiz treat all posts the same. We can do better:
- If the user's repo has a `PLATFORMS.md` file, read it for platform-specific guidance (e.g., "On dev.to, use code blocks and technical depth. On TikTok, use shorter captions and trending sounds.").
- If there's a `.megaphone/overrides/<platform>.json`, apply custom rules (e.g., `{ "x": { "mode": "thread", "hashtags": 5 }, "linkedin": { "mode": "document", "visibility": "PUBLIC" } }`).
- The skill can then adapt the same post to each platform, not just cross-post the same caption.

**3. Async scheduling without infrastructure.**
Upload-Post and Postiz rely on backend schedulers. We use `cron` (on Unix) or `Task Scheduler` (Windows) + a local daemon process (written in Node or Rust) that runs in the background. When a user schedules a post for 10am:
- The skill writes to a local queue file: `~/.megaphone/queue.jsonl` (one JSON per line, append-only).
- A background process (`megaphone-daemon`, could auto-launch via `npx`) polls this file every minute, checks `publishDate`, and publishes.
- No Temporal complexity. No external broker. Just a file and a process.

**4. Per-platform build-in-public posts (not just cross-posts).**
When a user publishes to multiple platforms, we give them a chance to customize:
- Detect if the post is from `megaphone-post` (the build-in-public skill). If so, prompt: "Customize for each platform before posting? (y/n)"
- If yes, run a sub-workflow for each platform: show Claude the platform's rules, ask for tweaks, apply them, post.
- This requires hooking into `megaphone-post`'s draft output and routing it through per-platform adapters.

**5. Media processing pipeline (local).**
Instead of delegating to FFmpeg-as-a-service (Upload-Post) or having each provider implement it (Postiz), we include a local media processor:
- Use `ffmpeg-static` (bundled) for common transformations: resize, crop, compress, transcode.
- The skill inspects the media, checks platform requirements, auto-fixes (e.g., "TikTok needs 9:16, image is 4:3 → auto-crop + pad").
- This is fast (local) and free (no per-minute billing).
- For advanced use (e.g., "add animated captions"), fall back to manual ffmpeg command injection.

**6. Analytics caching and aggregation.**
Upload-Post's analytics endpoint is basic. Postiz supports provider-specific analytics but depends on querying each provider individually. We cache and aggregate:
- After posting, schedule a follow-up activity (24h, 7d, 30d) to fetch analytics from each platform.
- Store in local SQLite: `postId | platform | metric | value | timestamp`.
- Skill can query "Show me engagement on last 10 posts" without hitting platform APIs repeatedly.
- Bonus: enables cross-platform comparison ("dev.to gets 100 views per post, X gets 500 impressions").

**7. Graceful platform abstraction with fallbacks.**
Both Upload-Post and Postiz have a hard limit: if a platform API breaks, the post fails. We add resilience:
- Define fallback chains. If TikTok auth fails, ask: "Post to Instagram instead? (y/n)"
- If a media format is rejected by platform A, automatically try a converted version before failing.
- Log all attempts to `.megaphone/logs/`, so users can debug.

---

## Section 5: The Platforms List (Priority Order)

**Tier 1: Essential (launch support)**
- **X (Twitter).** Auth: OAuth2 (straightforward). Free API tier: 300 posts/3hr (rate-limited but workable). Content: text + images + video (≤140s). Why first: biggest audience for build-in-public, most forgiving API.
- **LinkedIn.** Auth: OAuth2 (requires app registration). Free API tier: generous (no hard limit per se, but account-level caps exist). Content: text, images, documents, videos. Why: professional audience, strong engagement, platform for long-form writing.
- **Bluesky.** Auth: App passwords (non-standard but simple: generate in settings, use like API key). Free API tier: unlimited. Content: text, images, videos. Why: small but engaged community, open protocol, alternative to X.

**Tier 2: High-value (first month after launch)**
- **dev.to.** Auth: API token (no OAuth, just a static key in dashboard). Free API tier: unlimited. Content: articles (Markdown), metadata (tags, series). Why: developer audience, SEO benefits, cross-posts from blogs. **Specific advantage:** dev.to's article API is elegant; Postiz has a provider for this.
- **Reddit.** Auth: OAuth2 (PKCE). Free API tier: 1 request/sec (strict but manageable). Content: text posts, image posts, video posts (to subreddits). Why: community-driven, niche subreddits for indie builders. **Friction:** each post needs a subreddit ID; no universal "post to all subreddits."
- **Mastodon.** Auth: OAuth2 (instance-specific; each Mastodon server has its own OAuth endpoint). Free API tier: unlimited. Content: text, images, videos. Why: decentralized, privacy-first, growing indie community. **Friction:** users need to pick a server; no single endpoint.

**Tier 3: Nice-to-have (post-launch expansion)**
- **Hashnode.** Auth: API token. Free API tier: unlimited. Content: articles (Markdown), publication metadata. Why: developer-focused blogging platform, good for long-form content. **Note:** API is newer; less mature than dev.to.
- **Threads.** Auth: OAuth2 (requires Meta Business account). Free API tier: same as Instagram/Facebook (generous). Content: text, images, video, carousels. Why: official Twitter competitor, owned by Meta. **Friction:** Meta's OAuth is complex; requires business account setup.
- **Mastodon (custom servers).** If tier 2 launches, allow instance selection (e.g., "Post to fosstodon.org, techhub.social, etc.").

**Tier 4: Optional (community requests, later)**
- **Instagram.** Auth: OAuth2 (Meta Business Account). Free: business account required. Content: images, Reels (video), carousels, Stories. Why: visual platform, huge reach. **Friction:** Meta's approval process, Instagram Studio required for scheduling, Reels have strict requirements (9:16, 15s–90s). **Implementation note:** Postiz has two providers: `instagram.provider.ts` and `instagram.standalone.provider.ts` (for personal accounts), suggesting this platform is tricky.
- **TikTok.** Auth: OAuth2 (China/international servers; requires business account for scheduling). Free: limited, essentially requires TikTok Creator Marketplace. Content: short video (15s–10min), photos (with music). Why: enormous reach for creators. **Friction:** TikTok's API is heavily gated; no personal account posting via API. Hard pass for indie builders without business status.
- **Pinterest.** Auth: OAuth2 (straightforward). Free API: limited (1000 req/month in free tier, generous paid). Content: Pins (image + link), video Pins, carousels. Why: visual content discovery, good for tutorials/guides. **Friction:** Pins need a destination link; not suitable for text-only posts.
- **YouTube.** Auth: OAuth2. Free API: generous. Content: videos (upload), Shorts (video clips). Why: biggest video platform. **Friction:** video upload is heavy (requires resumable media upload protocol); Shorts have strict requirements (9:16, ≤60s). Consider as tier 3.5 or later.

**Tier N: Niche/Specialized (skip for v1)**
- **Discord.** Requires bot token (different auth model). Good for community announcements, not public distribution. Skip for v1.
- **Slack.** Same as Discord; skip.
- **Google Business Profile.** Requires business account; niche. Skip for v1.
- **Facebook Pages.** Meta ecosystem; same OAuth as Instagram. Could include with Threads/Instagram cluster if we tackle Meta. Currently skip.

---

## Summary Table

| Platform | Auth Difficulty | Free Tier | Post Types | v1? | Notes |
|---|---|---|---|---|---|
| X | Easy | 300/3hr | text, images, video | YES | Essential, high reach |
| LinkedIn | Medium | Generous | text, images, docs, video | YES | Professional, long-form |
| Bluesky | Easy | Unlimited | text, images, video | YES | Growing, open protocol |
| dev.to | Easy (token) | Unlimited | articles (MD) | YES | Developer audience, API clean |
| Reddit | Medium | 1 req/sec | text, images, video | YES | Niche communities, PKCE auth |
| Mastodon | Medium | Unlimited | text, images, video | YES | Decentralized, privacy-first |
| Hashnode | Easy (token) | Unlimited | articles (MD) | Pending | Developer audience, newer |
| Threads | Medium | Generous | text, images, video, carousel | Later | Meta ecosystem, approval needed |
| YouTube | Hard | Generous | video, Shorts | Later | Video-heavy, resumable upload |
| Instagram | Hard | Business account | images, Reels, carousels | Later | Meta ecosystem, Studio required |
| Pinterest | Medium | Limited | Pins, video | Later | Visual content only |
| TikTok | Hard | Business only | video, photos | Later | API heavily gated |

---

**Recommendation for megaphone-publish v1:** Launch with **X, LinkedIn, Bluesky, dev.to, Reddit, Mastodon.** This covers:
- Microblogging (X, Bluesky).
- Professional networking (LinkedIn).
- Developer blogging (dev.to).
- Communities (Reddit, Mastodon).
- No Meta involvement (complex OAuth, business account requirements).
- No video upload complexity (YouTube, Instagram, TikTok).

Add **Hashnode, Threads, YouTube** in v1.1 if feedback demands it. Save **Instagram, TikTok, Facebook** for later when we have capacity for their OAuth/approval complexity.

---

## Closing Reflection

**Upload-Post** is a masterclass in simplicity: delegate everything to a SaaS proxy, charge for value-add (FFmpeg), ship a skill that's almost pure prose. **The cost:** vendor lock-in, free tier too tight, analytics too basic.

**Postiz** is a masterclass in extensibility: modular providers, per-provider concurrency, workflow-based orchestration, self-hostable. **The cost:** operational complexity (Temporal, multi-process), OAuth handling fragmentation.

**megaphone-publish** should split the difference:
- **Local-first + encrypted vault** (vs. Upload-Post's cloud dependency).
- **Modular per-platform adapters** (like Postiz's providers, but simpler: each adapter is a ~150-line function, not a 500-line class).
- **Simple scheduling** (local queue file + cron-like daemon, not Temporal).
- **Repo-aware customization** (neither competitor does this).
- **Graceful degradation** (fallback chains, media re-encoding on the fly).

The result: a skill that indie builders can trust (runs on their machine), extend (add platforms easily), and iterate on (no waiting for SaaS pushes).
