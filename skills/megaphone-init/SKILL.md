---
name: megaphone-init
description: Initialize the Megaphone distribution toolkit for a repo. Use this skill whenever the user wants to set up megaphone, start using megaphone, init megaphone for this project, get help marketing or distributing their repo for the first time, or says things like "I just built a thing, help me ship it" or "I want to launch this but I don't know where to start." Trigger especially when the user is a non-technical or vibe-coder type who has a working project but no marketing materials, no social presence, and doesn't know where to share. Even if they don't say "megaphone" explicitly, trigger when their request is clearly about starting a distribution effort from scratch on a repo and there is no `.megaphone/profile.json` yet.
---

# megaphone-init

The user has a project but doesn't know how to distribute it. This skill produces the artifact every other megaphone skill depends on: a project profile that captures what the project is, who it's for, and how the user wants to sound — saved to `.megaphone/profile.json` so it persists across sessions.

The profile is small but high-leverage. Every later skill (`megaphone-assets`, `megaphone-outreach`, `megaphone-post`, `megaphone-publish`, `megaphone-schedule`, `megaphone-audit`, `megaphone-demo`, `megaphone-digest`) reads from it. A bad profile produces generic, AI-sounding output. A good one — especially the voice samples — produces drafts the user actually wants to ship.

## Workflow

### 0. Resolve the target project directory

Megaphone always operates on a single project root. Claude Code sessions almost always start in `$HOME`, so do **not** assume cwd is the project. Resolve the target before doing anything else, and do it without producing visible shell errors.

#### 0a. Probe cwd silently

Run **one** Bash call that is guaranteed to exit 0 — never chain with `&&`, never let `ls` fail on a missing glob. Use a wrapped form like this:

```bash
sh -c '
  cd "$PWD"
  echo "CWD=$PWD"
  echo "BASENAME=$(basename "$PWD")"
  for f in .git package.json pyproject.toml Cargo.toml go.mod README.md .megaphone; do
    [ -e "$f" ] && echo "HAS=$f"
  done
  exit 0
'
```

A directory counts as a "plausible project root" if it has any of: `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `README.md`, or an existing `.megaphone/`.

#### 0b. Branch on what you found

**Case A — cwd IS a plausible project root** (we're already inside a project):

Ask the user a single confirmation:

> "Initialize Megaphone for **`<basename>`** at `<cwd>`? (Y/n)"

- Y or no answer → use cwd, continue to step 1.
- N → fall through to Case B.

**Case B — cwd is NOT a project root** (e.g. `$HOME`, `/tmp`, empty dir):

Don't print a shell-style error. Just tell the user plainly that we need to pick a project, then **lead with memory candidates** — that's the priority path:

1. **Read the user's memory index first.** Open `~/.claude/projects/-Users-leyra/memory/MEMORY.md` and look for entries of type `project` (typically files named `project_*.md` or `*_startup.md`). Each project memory usually contains a path or repo location — pull the project name and any directory hint.
2. **Present them as a numbered list of candidates**, with the path if known. Format:

   > Megaphone needs a project. Here are projects I see in your memory:
   >
   > 1. **Behavioral Brain** — `/Users/leyra/Developer/03_AI_Agents/BehavioralBrain` *(if path known)*
   > 2. **Hearsh waitlist** — *(path unknown)*
   > 3. **Leyra Vibe Coder site** — *(path unknown)*
   > 4. **FrinkLoop** — `/Users/leyra/Developer/03_AI_Agents/FrinkLoop`
   > 5. **Clearly** — *(path unknown)*
   > 6. **Polyoracle** — *(path unknown)*
   >
   > Reply with a number, or paste an absolute path if your project isn't listed.

3. **If the user picks a number but the path is unknown**, ask once: "What's the absolute path for `<name>`?" Optionally offer to search common dev folders: `find ~/Developer ~/code ~/src ~/projects ~/work -maxdepth 3 -type d -iname "<name>" 2>/dev/null`.
4. **If the user pastes a path**, verify it exists with a silent probe (`[ -d "<path>" ] && echo OK || echo MISSING`). If missing, say so and re-ask.

#### 0c. Lock in absolute paths

Once a target path is resolved:

- Use **absolute paths for every Read/Write** for the rest of this skill. Don't rely on cwd.
- For Bash calls, prefix with `cd "<absolute-path>" && ...` so each call is self-contained.
- Never write `.megaphone/` outside the resolved target.

#### 0d. Bash hygiene for later steps

When probing for files that may or may not exist, always:

- Use `[ -e "<path>" ]` guards instead of bare `ls`.
- Wrap multi-step probes in `sh -c '...; exit 0'` so the call always exits 0.
- Never chain unknowns with `&&`.

This is the rule that prevents the "red error block on init" the user has explicitly objected to.

### 1. Detect whether megaphone is already initialized

Check for `.megaphone/profile.json` at the resolved project root.

- If it exists, read it and confirm with the user: "Megaphone is already set up for this repo. Want me to refresh the profile, or jump to a specific skill (assets, launch, post, discover, digest)?"
- If it doesn't, proceed.

### 2. Scan the repo silently

Before asking the user anything, gather what's already obvious. This dramatically reduces how much you need to interview them.

Read in this order, only what exists:
- `README.md` (or README at any case) — pull the title, first paragraph, and any "what is this" / "features" sections
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` — name, description, keywords, license, homepage URL
- Top-level directory layout — `src/`, `app/`, `pages/`, etc. tells you the framework
- `.git/config` or `git remote -v` (run via Bash) — the GitHub URL and default branch
- `git log -50 --oneline` (via Bash) — recent activity, freshness, themes
- `package.json` "homepage" or any obvious "Live demo:" / "Try it:" link in README — the deployed URL
- Any images in `/docs`, `/.github`, `/screenshots` — record their paths

If you can't run Bash (rare in Claude Code, but possible), do as much as you can with file reads alone. Don't get stuck.

### 3. Ask only what you couldn't infer

Use AskUserQuestion sparingly. Aim for **three questions max**, only the ones the repo scan didn't answer. Common gaps:

- **Audience** — "Who is this for? Other developers, end users, a niche community, all of the above?" — only ask if the README doesn't make this obvious.
- **Goals** — "What's the win? GitHub stars, paying customers, a job, just feedback?" — this changes which channels to target later.
- **Voice samples** — "Paste 1–3 things you've written that sound like you (a tweet, a slack message, an old blog post). I'll match that voice when drafting posts. If you don't have any, just say 'no samples' and I'll default to a clean, friendly indie-maker tone."

If the user explicitly skips voice samples, default to: "warm, plainspoken, slightly understated, no marketing speak, no exclamation points unless something genuinely shipped, no em-dashes used as hype punctuation."

### 4. Write `.megaphone/profile.json`

Create the directory if it doesn't exist. Schema:

```json
{
  "version": 1,
  "created_at": "<ISO 8601 timestamp>",
  "project": {
    "name": "string",
    "tagline": "one line, ≤80 chars",
    "what_it_does": "1–2 sentence description",
    "stack": ["tech", "stack", "items"],
    "repo_url": "https://github.com/...",
    "deployed_url": "https://... or null",
    "license": "MIT/etc."
  },
  "audience": {
    "primary": "developers | end-users | designers | founders | other (specify)",
    "niches": ["specific communities"]
  },
  "goals": {
    "primary": "stars | users | revenue | feedback | job | other",
    "target_launch_date": "YYYY-MM-DD or null"
  },
  "voice": {
    "samples": ["paste 1", "paste 2"],
    "guidance": "the inferred or default voice rules"
  },
  "screenshots": ["path/to/image.png"],
  "notes": "anything else captured during init"
}
```

Also create empty subdirectories the other skills will use: `.megaphone/assets/`, `.megaphone/posts/`, `.megaphone/metrics/`.

Add `.megaphone/metrics/` to `.gitignore` if a `.gitignore` exists — metrics are local-only noise.

### 5. Suggest the next step, briefly

Don't dump the full menu of skills on the user. Pick the single highest-value next move based on what they said:

- If they want to ship soon → "Want me to draft launch assets next? (`/megaphone-assets`)"
- If they want stars → "Want me to find awesome-lists where this belongs? (`/megaphone-outreach`)"
- If they're early and unsure → "Want a quick set of marketing assets so the README and socials don't look empty? (`/megaphone-assets`)"

Keep the suggestion to one line. End the turn.

## Edge cases

- **Empty repo / no README** — Tell the user honestly: "There's not much in the repo yet for me to work with. Want to give me a 2-sentence pitch and I'll generate a starter README to anchor the profile?" Then proceed with their pitch as the source of truth.
- **Monorepo / multiple projects** — Ask which package the profile is for. Megaphone v1 is single-project per profile.
- **Private repo, no remote** — Profile still works; just leave `repo_url` empty and note it for later.
- **User refuses to answer** — Fall back to defaults from the repo scan and proceed. A profile that's 70% correct is better than a stuck conversation.

## Why these choices matter

- **Voice samples are the single biggest quality lever.** Three pasted messages turn generic LLM-speak into "this sounds like me." Treat them as gold.
- **Persisting to `.megaphone/profile.json`** means later skills don't reinterview the user every time. They're not building distribution from scratch each session.
- **Three questions, max** respects the user's attention. Onboarding fatigue is the most common reason people abandon tools like this.
