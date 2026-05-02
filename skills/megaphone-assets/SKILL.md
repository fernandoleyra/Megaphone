---
name: megaphone-assets
description: Generate marketing assets for a software project - taglines, hooks, README hero, dev.to intros, landing-page copy, social bio one-liners, banner-image prompts (NanoBanana / ChatGPT), and hand-off to `megaphone-demo` for the GIF. Use when the user asks to "generate marketing assets", "rewrite my README", "give me a tagline", "make a launch post", "I need copy for the landing page", "what should I put in my GitHub bio", "make me a banner", "I need a hero image", or similar. Trigger when they're prepping a launch and need words + images. Reads the project profile, matches the user's voice, asks NanoBanana (clean illustrations) vs ChatGPT (photorealism) for the banner, and sizes copy per platform.
---

# megaphone-assets

The user has a project (and ideally a `.megaphone/profile.json`). This skill writes the short-form copy they'll paste into READMEs, social bios, dev.to intros, Product Hunt descriptions, and landing pages.

The trick: each platform has a different shape, and bad copy is almost always the wrong *shape* for the surface — a 280-char hook tries to live as a 1500-word essay, or a one-liner reads like a press release. This skill produces the right shape per surface, in the user's voice.

## Preamble: project resolution & bash hygiene

This skill operates inside a single project root and reads `.megaphone/profile.json` from there. Before doing anything:

1. **Resolve the target project.** If the cwd already looks like a project (`.git/`, `package.json`, etc.) and contains `.megaphone/profile.json`, use it. Otherwise, follow the resolution flow from `megaphone-init` §0b — confirm `<basename>` for cwd, or pick from memory candidates / paste a path. Never assume `$HOME` is the project.
2. **Exit-zero probes.** When checking for files that may not exist, wrap probes in `sh -c '...; exit 0'` and use `[ -e "<path>" ]` guards. Never let a missing file produce a visible red error block on first run.
3. **Absolute paths after resolution.** Once the target is known, use absolute paths for every Read/Write and prefix Bash with `cd "<path>" && ...`.

## Workflow

### 1. Load context

- Read `.megaphone/profile.json`. If missing, run the `megaphone-init` workflow first (or tell the user to). Don't try to write good copy without a profile.
- Read the latest README so suggestions don't contradict what's already there.

### 2. Confirm scope

Ask which assets the user wants in **one** AskUserQuestion (multi-select). Default selection if they say "all" or skip:

- Tagline (≤80 chars, the elevator-pitch line)
- Social hook (≤240 chars, leaves room for a link)
- README hero block (title + tagline + 1-paragraph description + 3 bullet features + screenshot/GIF placeholder)
- dev.to intro (~150 words, sets up a longer post)
- Landing page hero (headline + subheadline + primary CTA + 3 value props)
- Product Hunt tagline + description (PH allows 60-char tagline + 260-char description)
- GitHub bio one-liner (≤160 chars)
- Bluesky / X / LinkedIn launch post (per-platform; see `references/platform-voice.md`)

### 2.5. Offer visual assets (the README's biggest single upgrade)

Before writing copy, ask whether the user wants visual assets. A README hero image (banner) and a short demo GIF are the two highest-leverage additions a vibe coder can make — they roughly double star-rate. Most projects skip them because the tools feel like a separate workflow.

Use one AskUserQuestion call (multi-select), framed as "want help producing the visuals":

- **Banner / hero image** (static; ~1280×640) — explains what the project IS in one frame
- **Demo GIF / MP4** (animated; ~5–8s) — shows what the project DOES
- Skip — I'll handle visuals myself

If the user picks **banner**, do not generate the image yourself (Claude can't generate images). Instead:

1. **Craft a tight image prompt** in plain English using the `project_profile`. Aim for ≤60 words, name the subject + style + mood + palette + composition. Example for a CLI tool:

   > "Editorial-illustration banner for a developer-tools project called Megaphone. Subject: a vintage brass loudspeaker on a dark navy background, with thin sans-serif type 'Megaphone' in the upper-left and a soft warm light grading from amber to orange in the bottom-right. Flat colors, clean shapes, no clutter, no text other than the title. 1280×640, web-safe contrast."

2. **Ask which tool to use.** Use a single AskUserQuestion call with two clear options:
   - **NanoBanana** (a.k.a. Gemini 2.5 Flash Image) — fast, cheap, very strong on consistent style and clean illustrations. Available at https://aistudio.google.com or via Replicate. Best when the user wants iteration speed.
   - **ChatGPT** (DALL·E 3 / GPT image gen) — higher photorealism, slower iteration, more familiar UX. Available at https://chat.openai.com.

   Default recommendation: **NanoBanana for clean illustrative banners; ChatGPT for photorealistic hero shots or when the user is already inside ChatGPT.**

3. **Save the prompt** to `.megaphone/assets/banner-prompt.md` so the user can re-use or refine it. Format:

   ```markdown
   # Banner image prompt

   **Tool suggestion:** NanoBanana (https://aistudio.google.com)
   **Dimensions:** 1280×640 (16:8 aspect, README-friendly)
   **Output target:** docs/banner.png

   ## Prompt

   <the prompt text>

   ## How to use

   1. Open the tool above.
   2. Paste the prompt.
   3. Generate. If the first result is off, iterate by adding constraints
      ("make the loudspeaker more vintage", "darken the navy").
   4. Download the best result as `docs/banner.png` (or wherever you keep
      images in the repo).
   5. Run `/megaphone-assets` again to fold the new banner into the README hero.
   ```

4. **Suggest the README placement** — when the user comes back with the image, the README hero block should reference it as `![<project> banner](docs/banner.png)` immediately under the H1.

If the user picks **demo GIF**, hand off to `/megaphone-demo`. That skill knows how to record a Playwright-driven happy path and produce a GIF or MP4 in `.megaphone/assets/demo/`. Don't try to record one from inside this skill.

If the user picks both, run the banner-prompt step first (it's instant; they can generate while we keep working), then queue `/megaphone-demo` for after the rest of the assets are written.

### 3. Write the assets

For each requested asset, follow these constraints:

**Tagline (≤80 chars).** Concrete, not aspirational. Names the *who* and the *outcome*. No "the future of X" or "AI-powered Y" unless the user's voice samples are unironically that style.

> ✅ "Distribution toolkit for vibe coders who hate self-promo."
> ❌ "Reimagining how indie creators reach their audience."

**Social hook (≤240 chars).** Leads with the most surprising or specific thing about the project. Ends with what the reader can do next (link, install, try). One concrete detail beats five generic ones.

**README hero block.** Use this skeleton:

```markdown
# <Project name>

<Tagline.>

<1 paragraph: who it's for + what problem it solves + how it does it. ≤4 sentences.>

![<project> banner](docs/banner.png)

<!-- If a demo GIF exists at .megaphone/assets/demo/hero.gif, embed it
     immediately after the banner — animated visual is the second-biggest
     star-rate driver after the banner itself. -->
![<project> demo](.megaphone/assets/demo/hero.gif)

## Why <project>

- <Specific feature framed as user benefit>
- <Specific feature framed as user benefit>
- <Specific feature framed as user benefit>

## Quick start

<3-line install/run snippet>
```

The image paths are placeholders unless real files exist:
- If `docs/banner.png` (or `.megaphone/assets/banner.png`) is present, use it.
- If `.megaphone/assets/demo/hero.gif` is present (produced by `megaphone-demo`), include the GIF line.
- If neither exists, do NOT add the image lines. Instead, tell the user: "The README looks tight; the single biggest remaining upgrade is a banner image and a demo GIF. Want me to set those up?" and offer to run the visual-assets step (section 2.5) again.

**dev.to intro (~150 words).** Title that promises a payoff (a number, a takeaway, a confession), opens with a 1-sentence story or stat, transitions to the project. Don't bury the project link past the third paragraph.

**Landing page hero.**
- Headline: ≤8 words, outcome-focused
- Subheadline: ≤25 words, names the audience and the wedge
- Primary CTA: 2–3 words, action verb + noun ("Get started free", "Install the plugin")
- Three value props: each is one sentence, leads with a verb, names a concrete win

**Product Hunt tagline + description.**
- Tagline: ≤60 chars, includes the audience and the outcome
- Description: ≤260 chars, expands the tagline and ends with a specific call ("free during beta", "no signup required")

**GitHub bio one-liner.** ≤160 chars. Names the project, the audience, and one differentiator. End with the link.

**Per-platform launch posts.** Read `references/platform-voice.md` for the tone and constraints per platform. Generate one draft per platform the user picked. Each post should:
- Open with a hook in the first line (it's what shows in the preview)
- Include one concrete detail not in the README
- End with the link
- Match the voice samples from the profile

### 4. Save the output

Write each asset to `.megaphone/assets/<asset-name>.md`. Use these filenames:

- `tagline.md`
- `social-hook.md`
- `readme-hero.md`
- `devto-intro.md`
- `landing-hero.md`
- `producthunt.md`
- `github-bio.md`
- `posts/launch-bluesky.md`, `posts/launch-linkedin.md`, etc.

For each, prepend a short comment at the top explaining the surface and constraints, so when the user opens the file later they understand what it's for:

```markdown
<!-- Tagline: ≤80 chars, used as repo description, social bio, README subtitle. -->

Distribution toolkit for vibe coders who hate self-promo.
```

### 5. Show the user a quick summary

After writing, list the files created and call out the one or two assets you'd start with. Don't paste all of the copy back — they can read the files. Offer one concrete next move (`megaphone-launch` if no launch plan exists yet, otherwise `megaphone-post`).

## Quality bar — read before generating

A draft fails if any of these are true. Reject your own draft and rewrite if you spot one:

- It uses the words "revolutionize", "leverage", "seamless", "robust", "cutting-edge", "next-generation", or "empower" outside an intentional ironic context
- It opens with "In today's world…" or "Are you tired of…"
- The tagline could apply to any project (no specifics about the audience or the wedge)
- It promises something the README doesn't actually deliver
- It uses em-dashes as hype punctuation when the user's voice samples don't
- The CTA is generic ("Learn more")

## Voice rules (apply across every asset)

- Match the voice samples in `profile.json`. If they're casual, be casual. If they curse, you can curse where the platform allows.
- One concrete number, name, or fact per piece, minimum. "Generates the README in 8 seconds" beats "fast and easy."
- Active verbs over passive ones. "Megaphone reads your repo and writes the launch posts" beats "Posts are written based on repo analysis."
- No more than one exclamation point per asset, and only when something genuinely shipped.
- No emoji unless the voice samples include emoji.

## Edge cases

- **No voice samples** — fall back to: warm, plainspoken, slightly understated. Better to be a little flat than to be cringe.
- **README is already excellent** — say so. Suggest small concrete tweaks (reorder, add a hero image, sharpen the tagline) instead of rewriting wholesale.
- **User asks for one specific asset** — just write that one. Don't proactively generate the whole set.
- **Project is pre-launch / has no users yet** — frame everything in terms of who it's *for* and what it *does*, never social proof you don't have. Don't fabricate testimonials.
