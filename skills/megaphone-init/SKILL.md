---
name: megaphone-init
description: Initialize the Megaphone distribution toolkit for a repo. Use this skill whenever the user wants to set up megaphone, start using megaphone, init megaphone for this project, get help marketing or distributing their repo for the first time, or says things like "I just built a thing, help me ship it" or "I want to launch this but I don't know where to start." Trigger especially when the user is a non-technical or vibe-coder type who has a working project but no marketing materials, no social presence, and doesn't know where to share. Even if they don't say "megaphone" explicitly, trigger when their request is clearly about starting a distribution effort from scratch on a repo and there is no `.megaphone/profile.json` yet.
---

# megaphone-init

The user has a project but doesn't know how to distribute it. This skill produces the artifact every other megaphone skill depends on: a project profile that captures what the project is, who it's for, and how the user wants to sound — saved to `.megaphone/profile.json` so it persists across sessions.

The profile is small but high-leverage. Every later skill (`megaphone-assets`, `megaphone-launch`, `megaphone-post`, `megaphone-discover`, `megaphone-digest`) reads from it. A bad profile produces generic, AI-sounding output. A good one — especially the voice samples — produces drafts the user actually wants to ship.

## Workflow

### 0. Resolve the target project directory

Megaphone always operates on a single project root. Before anything else, figure out which directory that is. Do **not** assume the current working directory is correct — the skill is often invoked from `$HOME` or an empty chat with no project context.

Steps:

1. **Check the cwd for project signals.** Probe with a single non-fatal command — use `;` not `&&`, and add `2>/dev/null` so a missing path doesn't abort the rest. Example: `ls -la .megaphone 2>/dev/null; ls README.md package.json pyproject.toml Cargo.toml go.mod 2>/dev/null; ls -d .git 2>/dev/null; pwd`. A directory is a plausible project root if it contains any of: `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `README.md`, or an existing `.megaphone/` folder.
2. **If cwd is a project root**, use it and continue to step 1.
3. **If cwd is not a project root** (e.g. `$HOME`, `/tmp`, an empty dir):
   - Tell the user plainly: "You're in `<cwd>`, which doesn't look like a project. Megaphone needs to run inside the project you want to distribute."
   - Offer two paths:
     - **(a)** "Paste the absolute path of the project (e.g. `/Users/you/Developer/my-app`) and I'll initialize it there."
     - **(b)** "Or tell me the project name and I'll look for it under common dev folders (`~/Developer`, `~/code`, `~/src`, `~/projects`, `~/work`)." If they pick this, scan up to 2 levels deep with `find ~/Developer ~/code ~/src ~/projects ~/work -maxdepth 3 -type d -iname "<name>" 2>/dev/null`. If multiple candidates exist, list them and let the user choose.
   - If the assistant has memory or recent conversation context pointing to a likely project (e.g. the user just said "init megaphone for Hearsh"), surface that path as the suggested default — but still confirm before writing.
4. **Once a target path is resolved, use absolute paths for the rest of the skill.** Either `cd "<path>"` once at the start of any Bash invocation, or pass the absolute path to every `Read`/`Write`. Never write `.megaphone/` outside the resolved target.
5. **Bash hygiene reminder for the rest of the skill:** when probing for files that may not exist, chain with `;` not `&&`, and add `2>/dev/null` so the chain reports useful output instead of silently failing on the first missing path.

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
- If they want stars → "Want me to find awesome-lists where this belongs? (`/megaphone-discover`)"
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
