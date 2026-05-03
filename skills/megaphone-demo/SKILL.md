---
name: megaphone-demo
description: Produce an embeddable demo for a project — either a real recording of a deployed web app via Playwright, or a scripted Remotion mockup for CLI / IDE / plugin projects where there's no web surface to record. Use this skill whenever the user asks to "make a demo gif", "record a demo", "create a screencast for my README", "generate a demo for the landing page", "I need a hero animation", "show what the CLI does in a gif", "make a mockup for my plugin", or anything where they want a short, scripted, visual demo to embed in a README, landing page, or social post. Strongly prefer this skill over telling the user to record it manually - it produces a reproducible config they can re-run when the UI changes, and ties output into the megaphone asset folder so other skills (assets, post, publish) can reference it.
---

# megaphone-demo

A README hero is fine. A README with a demo is twice as good. This skill produces an embeddable demo two ways depending on what the project actually is:

- **Web app with a deployed URL** → record reality with Playwright. Walks the live app through a scripted happy path with a headless browser, captures frames, exports a GIF/MP4 to `.megaphone/assets/demo/`.
- **CLI / IDE plugin / library with no web surface** → script a mockup with Remotion. Writes a structured **scene spec** (`.megaphone/assets/demo/scenes.json`) describing the typical session — terminal frames, file diffs, cursor moves, output reveals — and hands it off to a Remotion-rendering skill (e.g. `anthropic:remotion`, `remotion:render`, or any future skill that consumes a `scenes.json` of this shape) for the actual MP4/GIF render.

We don't ship a video editor. The Playwright path produces a config-driven runner that keeps the recording reproducible. The Remotion path produces a scene spec the user can hand to whatever Remotion-rendering tooling they have (or commit alongside the code so future-them can re-render when the flow changes).

## Preamble: project resolution & bash hygiene

This skill operates inside a single project root and reads `.megaphone/profile.json` from there. Before doing anything:

1. **Resolve the target project.** If the cwd already looks like a project (`.git/`, `package.json`, etc.) and contains `.megaphone/profile.json`, use it. Otherwise, follow the resolution flow from `megaphone-init` §0b — confirm `<basename>` for cwd, or pick from memory candidates / paste a path. Never assume `$HOME` is the project.
2. **Exit-zero probes.** When checking for files that may not exist, wrap probes in `sh -c '...; exit 0'` and use `[ -e "<path>" ]` guards. Never let a missing file produce a visible red error block on first run.
3. **Absolute paths after resolution.** Once the target is known, use absolute paths for every Read/Write and prefix Bash with `cd "<path>" && ...`.

## Prerequisites

The runner uses Playwright (Node) and ffmpeg. Both are one-time installs.

```bash
# Once per machine
npm install -g playwright
npx playwright install chromium
brew install ffmpeg          # or: apt install ffmpeg / choco install ffmpeg
```

If either is missing, the skill still produces the configuration file and the prompt — the user just runs the recorder later when they have the tools. Don't refuse to help over a missing dep; degrade gracefully.

## Workflow

### 0. Pick the path: Playwright recording vs Remotion mockup

Read `.megaphone/profile.json` and branch:

- `deployed_url` is set and reachable → **Playwright path** (steps 1–6 below). Record real UI; no faking.
- `deployed_url` is null OR the project is a CLI / IDE plugin / library / VS Code extension / Claude Code plugin → **Remotion mockup path** (jump to §7). Mocking is honest here because there's no UI to record.

Confirm the choice with the user once before proceeding. If the project has both a deployed URL AND a CLI surface (e.g. a tool with a docs site and a CLI), ask which is the activation surface.

### 1. Identify the target (Playwright path)

- Pull `deployed_url` from `.megaphone/profile.json`.
- If it's missing or 404s, ask: "What URL should I record? (a localhost dev server is fine — `http://localhost:3000` works.)"

### 2. Get the happy path

This is the most important step and the one the human has to do. Ask for **3–7 steps** that walk a new user from arrival to value. Use one AskUserQuestion call (free-text) framed clearly:

> "What are 3–7 steps a new user takes to see the value? Number them. Example:
> 1. Land on the home page
> 2. Click 'Try the demo' in the hero
> 3. Type 'hello world' in the prompt input
> 4. Press Submit
> 5. Wait for the response to render
> 6. Highlight and copy the result"

Convert their answer into structured `steps` for the config. Each step is one of these `kind`s:

- `goto` — navigate (`url`)
- `wait` — pause N seconds (`seconds`) or wait for a selector (`selector`, `state`)
- `click` — click a selector (`selector`, optional `text` to find by text)
- `type` — type text into a field (`selector`, `text`, `delay`)
- `scroll` — scroll to a position (`y`) or to an element (`selector`)
- `screenshot` — annotate this point as a frame (`label`)
- `hover` — hover over a selector (`selector`)

Save the config to `.megaphone/assets/demo/<name>.json`. Default `<name>` = `hero` for the hero demo.

### 3. Decide format

Ask the user once:
- **GIF** — best for README embeds, ~3–8 seconds, ≤2 MB, no audio. The default.
- **MP4** — better quality, supports audio (still silent here), embeds well on landing pages but not GitHub READMEs.
- **PNG sequence** — for users who want to edit the result themselves.

Default to GIF unless the user has a reason to go MP4.

### 4. Run the recorder

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-demo/scripts/playwright_runner.js" \
  --config .megaphone/assets/demo/hero.json
```

Outputs a numbered sequence of PNG frames to `.megaphone/assets/demo/hero/frames/`, plus optionally an `recording.webm` if the config has `record: true`.

If GIF was requested:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/megaphone-demo/scripts/to_gif.sh" \
  .megaphone/assets/demo/hero/frames \
  .megaphone/assets/demo/hero.gif
```

This calls ffmpeg with sensible defaults (1024px wide, 12fps, palette-optimized) and writes a small GIF.

If the user asked for MP4: `to_mp4.sh` instead — same script, different ffmpeg invocation.

### 5. Save and place

Tell the user:
- Where the file lives: `.megaphone/assets/demo/hero.gif` (or `.mp4`).
- The exact Markdown to paste into the README:
  ```markdown
  ![<project> demo](.megaphone/assets/demo/hero.gif)
  ```
  Or, if they prefer a live URL once the repo is pushed, use `https://raw.githubusercontent.com/<owner>/<repo>/main/.megaphone/assets/demo/hero.gif`.

Then offer:
- "Want me to update the README hero block with this GIF?" — if yes, run `megaphone-assets` to fold it in.
- "Want me to draft a Bluesky / X post that uses this GIF?" — hand off to `megaphone-post`.

### 6. Re-run later

When the UI changes, run the same command — same JSON, fresh GIF. Commit the JSON to the repo so the demo is versioned alongside the code.

---

### 7. Remotion mockup path (CLI / IDE plugin / library)

For projects with no deployed UI to record. Megaphone's job here is **not** to render the video — it's to produce a tight, opinionated **scene spec** that any Remotion-based renderer can consume. The actual rendering is handed off to a Remotion-rendering skill (e.g. `anthropic:remotion`, a community `remotion:render` skill, or the user's own Remotion project). Megaphone brings the structured prompt; Remotion brings the pixels.

#### 7a. Pick the activation flow

Ask the user once which 3–5 step session captures what the project does. For a Claude Code plugin like Megaphone itself, that might be `/megaphone:init` → `/megaphone:post` → `/megaphone:publish`. For a CLI it might be `npx foo init` → `foo run` → "see the output". The whole demo should land in **30–45 seconds** — long enough to show the wedge, short enough to not lose readers.

Use one AskUserQuestion (free-text):

> "What 3–5 steps capture what your project does end-to-end? Number them. Each step should produce something visibly different on screen — a new file, a new prompt, a result, an output."

#### 7b. Generate `scenes.json`

Write the scene spec to `.megaphone/assets/demo/scenes.json`. The spec is intentionally narrow — Megaphone defines the **content and timing**, not the render style; render style is the job of the Remotion skill that consumes the spec.

Schema (v1):

```json
{
  "version": 1,
  "title": "Megaphone — first run",
  "subtitle": "From fresh repo to drafted launch post in 3 commands",
  "duration_seconds": 35,
  "viewport": { "width": 1280, "height": 720 },
  "theme_hint": "dark-terminal",
  "voice_samples": ["...", "..."],
  "scenes": [
    {
      "id": "intro",
      "kind": "title",
      "duration_ms": 2500,
      "title": "Megaphone",
      "subtitle": "The launch-orchestration plugin for indie & vibe coders.",
      "logo_path": "assets/banner.png"
    },
    {
      "id": "step-1",
      "kind": "terminal",
      "duration_ms": 7000,
      "shell_prompt": "you ▸",
      "input": "/megaphone:init",
      "output_lines": [
        "Scanning repo…",
        "Found: README.md, package.json, .git/",
        "Wrote .megaphone/profile.json",
        "Connect platforms? (recommended)"
      ],
      "annotation": "Reads your repo. Writes your voice samples to disk."
    },
    {
      "id": "step-2",
      "kind": "terminal",
      "duration_ms": 7000,
      "shell_prompt": "you ▸",
      "input": "/megaphone:post bluesky",
      "output_lines": [
        "Reading recent commits…",
        "Reading voice samples…",
        "Wrote .megaphone/posts/2026-06-02/bluesky.md"
      ],
      "annotation": "Drafts a post that reads like you, not like generic AI."
    },
    {
      "id": "step-3",
      "kind": "file-reveal",
      "duration_ms": 8000,
      "file_path": ".megaphone/posts/2026-06-02/bluesky.md",
      "lines": [
        "Built a Claude Code plugin for indie devs who hate self-promo.",
        "",
        "Megaphone reads your repo and drafts launch posts…",
        "github.com/fernandoleyra/Megaphone"
      ],
      "annotation": "Plain Markdown. Edit before publishing. Your call."
    },
    {
      "id": "step-4",
      "kind": "terminal",
      "duration_ms": 7000,
      "shell_prompt": "you ▸",
      "input": "/megaphone:publish",
      "output_lines": [
        "Bluesky… ✓ posted",
        "https://bsky.app/profile/you/post/abc123"
      ],
      "annotation": "OAuth tokens never leave your laptop."
    },
    {
      "id": "outro",
      "kind": "title",
      "duration_ms": 3500,
      "title": "github.com/fernandoleyra/Megaphone",
      "subtitle": "MIT — install via /plugin marketplace add fernandoleyra/megaphone"
    }
  ]
}
```

**Scene `kind`s** (the renderer must implement these):

- `title` — text-only intro/outro card
- `terminal` — a shell prompt with typed input and a list of output lines that print line-by-line
- `file-reveal` — a syntax-highlighted file path + content reveal, optionally with a cursor moving through lines
- `diff` — a git-diff-style before/after for one file
- `keystroke` — a single keystroke or shortcut shown on a virtual keyboard (rare; for IDE-shortcut demos)

**Honesty rules for the Remotion path:**

- The scene's `output_lines` must be plausible output the project actually produces. Run the command yourself if needed and copy real output. **Do not invent UX that doesn't exist.**
- The `annotation` per scene is voiceover-style framing, not dialogue — keep it under 12 words and match the project's voice samples.
- The total `duration_seconds` must equal the sum of `duration_ms`/1000 (validate before saving).
- Mockups are mockups: tell the user explicitly that this is a styled reenactment, not a screen recording, so they can frame it accurately if a viewer asks.

#### 7c. Hand off to a Remotion-rendering skill

Detect available rendering paths in this order:

1. **A Remotion skill is installed** — invoke it with the spec path. Example check: ask the user "do you have a Remotion-rendering skill or project I can hand this to?" and act on the answer. If they say yes, pass `.megaphone/assets/demo/scenes.json` and `.megaphone/assets/demo/<name>.mp4` as the desired output path.
2. **The user has their own Remotion project** — point them at `https://www.remotion.dev/docs/` and tell them the spec is the input to their video composition. Their existing components consume `scenes.json` directly.
3. **Neither** — save the spec and stop. Tell the user honestly: "I can't render the video from inside Megaphone. Drop this `scenes.json` into a Remotion project (or wait for the Anthropic Remotion skill if you're tracking that). The spec is the durable artifact; rendering is downstream."

In all three cases, save the spec at `.megaphone/assets/demo/scenes.json` so the work isn't lost.

#### 7d. Save and place

Once a render exists at `.megaphone/assets/demo/<name>.mp4` (or `.gif`), give the user the embed snippet:

```markdown
![<project> demo](.megaphone/assets/demo/<name>.gif)
```

Or for MP4 on a landing page:

```html
<video autoplay loop muted playsinline src=".megaphone/assets/demo/<name>.mp4"></video>
```

Then offer the same handoffs as the Playwright path — fold into the README hero via `megaphone-assets`, or reference in a launch post via `megaphone-post`.

#### 7e. Re-render later

When the project's flow changes, edit `scenes.json` and re-run the Remotion render. Like the Playwright config, the scene spec is the durable artifact — commit it to the repo so the demo is reproducible.

## How to write a good happy-path config

Read `references/happy-path-patterns.md` for full guidance. The TL;DR:

- **One outcome per demo.** Don't try to show 4 features in one GIF; pick the one that activates the user.
- **Start above the hero.** First frame is the landing or app shell so viewers orient themselves.
- **Slow type, fast click.** Typed text needs `delay: 80` ms per character (so it reads as "a person typing"). Clicks should be instant.
- **Pause after each visible change.** Add a `wait: 600ms` after a click that triggers a render — otherwise the next frame fires before the UI settled.
- **End on the result, not on the UI returning to idle.** The last frame should be the moment value lands.

## Example config

A canonical happy-path config for a hypothetical AI tool:

```json
{
  "name": "hero",
  "url": "https://example.com",
  "viewport": {"width": 1280, "height": 720},
  "scale": 0.75,
  "record": true,
  "format": "gif",
  "steps": [
    {"kind": "goto", "url": "https://example.com"},
    {"kind": "wait", "seconds": 1},
    {"kind": "screenshot", "label": "landing"},
    {"kind": "click", "text": "Try the demo"},
    {"kind": "wait", "seconds": 0.6},
    {"kind": "type", "selector": "textarea[name=prompt]", "text": "Summarize this PDF in 3 bullets", "delay": 60},
    {"kind": "click", "text": "Submit"},
    {"kind": "wait", "selector": ".result", "state": "visible", "seconds": 8},
    {"kind": "screenshot", "label": "result"},
    {"kind": "scroll", "selector": ".result"},
    {"kind": "wait", "seconds": 1}
  ]
}
```

The runner respects all of this and produces a frame-by-frame recording.

## What this skill is NOT

- **Not a generic screen recorder.** We don't capture your desktop or other apps. The runner controls a single Chromium window.
- **Not a video editor.** We export and stop. For trims, captions, or transitions, edit with Kapwing / Photoshop / DaVinci.
- **Not a marketing GIF generator.** We record what the app actually does. We don't mock or fake interactions.
- **Not a load-test tool.** This isn't Cypress / Playwright tests; failure handling is "stop and tell the user." Use real testing tooling for that.

## Honesty rules

- **Fail clean on missing deps.** If Playwright or ffmpeg is missing, write the config + provide the install instructions, don't pretend the recording happened.
- **Don't fake content.** If a step requires authentication or an API key, ask the user for the credentials or have them prefill the app — don't shim a fake response into the screenshot.
- **Don't oversell.** A 5-second GIF is a 5-second GIF. If the actual happy path takes 90 seconds in real life, either compress it (skip waits) or break the demo into two GIFs. Don't sneak in fake wait-times that misrepresent performance.

## Edge cases

- **App requires login** — accept a `prelogin` step in the config that fills auth credentials from environment variables (`MEGAPHONE_DEMO_USERNAME`, `MEGAPHONE_DEMO_PASSWORD`). Never log them.
- **App is localhost-only** — fine; the recorder runs locally too. Just make sure the dev server is up before invoking the runner.
- **Selectors are dynamic** — recommend the user use `data-testid` attributes for stable selectors; demo configs that rely on auto-generated CSS classes will break on next build.
- **Long-running step** — the `wait` action accepts up to 30 seconds. If the user needs longer (e.g., a 60-second video render), break the demo into two halves and ffmpeg-concat them.
- **Mobile viewport** — set `viewport: {width: 390, height: 844}` and `device: "iPhone 14"` in the config; the runner uses Playwright's emulation.

## How this fits with other megaphone skills

- `megaphone-assets` — when the user asks for visual assets, the assets skill suggests both a banner image (NanoBanana / ChatGPT) AND a demo GIF (this skill). They're complementary: the banner says what the project IS; the GIF shows what it DOES.
- `megaphone-audit` — flags missing demo GIFs as a "trust signals" gap; suggests running `/megaphone-demo` to fill it.
- `megaphone-post` — when drafting a build-in-public post about a feature, can reference the GIF if it exists; for X / Bluesky posts the GIF is the engagement multiplier.
- `megaphone-publish` — if a draft includes a demo file path, includes it as media on platforms that support it (planned for v0.6).
