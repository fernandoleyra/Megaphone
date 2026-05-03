# Changelog

All notable changes to Megaphone are tracked here. The project follows
[semantic versioning](https://semver.org/) — minor version bumps add features,
patch versions fix bugs, breaking changes wait for the next major.

## [0.7.8] — 2026-05-03

### Fixed
- `megaphone-audit` `audit_journey.py` had three false-negative bugs that under-scored repos by ~20 points:
  - `first_run_signals` only matched section titles `Usage / Quick start / Quickstart / Getting started / Example / Examples`. Now also matches `First run / First-run / Get started / Typical first session / First session`.
  - `share_signals` regex only counted Markdown-syntax badges `![](shields.io...)`. READMEs that center badges in `<p>` tags use `<img src=...>` form, which wasn't counted. Now matches both syntaxes and a wider list of badge providers (img.shields.io, github.com, codecov, codacy, codeclimate, circleci, travis-ci).
  - `return_signals.what_next_section` only matched `What's next / Going further / Next steps`. Now also matches `Roadmap / What's coming` — the more common heading in OSS READMEs.
- Net effect on Megaphone's own self-audit: 24/70 → 45/70 with no further README work; the bugs were artificially deflating the baseline.

## [0.7.7] — 2026-05-03

### Added
- `## First run` section in README with a 3-command session showing the activation moment in plain language. Promotes what was buried as "Typical first session."
- `## Roadmap` section in README — concrete 0.8 / 0.9 / 1.0 targets so reviewers see momentum, not just history.
- `CHANGELOG.md` (this file) — curated version history.
- `megaphone-demo`: documented dual-path workflow — Playwright for deployed web apps, Remotion mockup for CLI/plugin projects via a structured scene spec handed off to a Remotion-rendering skill.
- `megaphone-schedule`: launch-cadence question (1-day blitz / 7-day sprint / 30-day plan / custom) when setting up a sequence, replacing the hardcoded 30/14/6/0 assumption.

### Changed
- `megaphone-demo` SKILL.md branches at the top on `deployed_url` presence — no URL routes to the Remotion mockup path; URL stays on the Playwright path.

## [0.7.6] — 2026-05-03

### Changed
- `megaphone-schedule` now recommends **launchd LaunchAgent** as the primary macOS path, demoting cron to a Linux-first / macOS-fallback option. Cron on macOS silently no-ops when the user's terminal lacks Full Disk Access — `crontab -` returns 0 and `crontab -l` is empty. launchd avoids the FDA dance entirely and is Apple's native scheduler.
- SKILL.md instructs Claude to generate a small install script in `.megaphone/schedule/` rather than asking the user to paste a multi-line crontab line. Long cron lines wrap on paste in many terminals and produce "bad minute" errors.

## [0.7.5] — 2026-05-03

### Fixed
- `add-sequence` was ignoring the `timezone` field of the spec (line 208 used `_now().tzinfo` instead of the requested zone). Launch sequences shifted by the offset between the user's system clock and the launch timezone — typically several hours, enough to break a Day-0 schedule. Now applies `zoneinfo.ZoneInfo(tzname)` and errors cleanly on unknown zones.
- `megaphone-schedule` SKILL.md no longer recommends `anthropic-skills:schedule` (cloud) for the runner. Remote agents can't access `~/.megaphone/credentials/` — every fire would silently fail with `auth_error`, defeating the local-first design. Added an explicit "do not propose cloud schedulers" guard.

## [0.7.1] — 2026-05-02

### Fixed
- Marketplace install: switched single-plugin marketplace source to bare `{source: "url", url: "..."}` form. The earlier `{source, url, path}` triplet caused `/plugin marketplace add` to never populate the cache, so users saw no commands or skills.

## [0.7.0] — 2026-05-02

### Added
- `megaphone-auth` wrapper — short command (`megaphone-auth status`, `megaphone-auth connect <platform>`, `megaphone-auth disconnect <platform>`) auto-installed to `~/.local/bin` by `/megaphone:init`. Replaces the 130-character full path that fragile terminals split on paste.
- 6 slash commands: `init`, `post`, `publish`, `schedule`, `audit`, `digest`. Auto-discovered skills cover the rest.
- `/megaphone:init` connects distribution channels during init with a clear reconnect path. Profile schema extended with `platforms.connected[]` and an audience enum.
- Canonical `platform-ids.md` reference — single source of truth for `bluesky`, `x`, `linkedin`, `devto`, `mastodon`, `threads`, `hashnode`, `reddit` IDs across `megaphone-post`, `megaphone-publish`, and `megaphone-schedule`.
- Mastodon connector validates instance hostname (RFC 1123-style) before any HTTP request — blocks IP literals and paths to prevent SSRF pivots to internal services.
- OAuth `state` parameter validated on the publish-side callback handler (CSRF mitigation).
- Full `.megaphone/` directory tree created during init so downstream skills don't have to guard missing paths.

### Fixed
- `megaphone-post` and `megaphone-digest` now guard for git presence (worktree-less repos no longer crash).
- `megaphone-demo` ffmpeg invocation uses glob input pattern (handles non-zero-padded frame numbers).
- All skills include the project-resolution preamble — never assume `$HOME` is the project; resolve target via `.git/`, `package.json`, or memory candidates.
- Standardized launch artifacts under `.megaphone/launch/` (plus `bash hygiene` exit-zero probe rules so first-run errors don't show red blocks).

[0.7.8]: https://github.com/fernandoleyra/Megaphone/compare/v0.7.7...v0.7.8
[0.7.7]: https://github.com/fernandoleyra/Megaphone/compare/v0.7.6...v0.7.7
[0.7.6]: https://github.com/fernandoleyra/Megaphone/compare/v0.7.5...v0.7.6
[0.7.5]: https://github.com/fernandoleyra/Megaphone/compare/abaceca...v0.7.5
[0.7.1]: https://github.com/fernandoleyra/Megaphone/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/fernandoleyra/Megaphone/releases/tag/v0.7.0
