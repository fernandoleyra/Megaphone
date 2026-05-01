# Journey stages — what we measure and what to look for

Reference for the stage-level scoring in `audit.py` and the qualitative review the skill produces on top.

Each stage has:
- **What we count** (static metrics from the script)
- **What to look at** (what the skill notices in the persona walkthrough)
- **Common friction patterns**
- **Healthy / worrying / broken thresholds**

---

## Stage 1 — Discovery

**What we count**
- README exists? First 200 chars preview.
- Landing page reachable? Title + H1 + OG image presence.
- Recent commits in the last 30 days.

**What to look at**
- Is the discovery hook (Bluesky post, HN title, awesome-list line) doing its job? If it brought the user to a page that doesn't match the hook's promise, it's the hook's fault, not the page's.
- Does the OG image render correctly when the page is shared? (We can verify the meta tag exists; the actual rendering needs a manual paste check.)

**Common friction**
- "Welcome to ProjectName" hero (says nothing)
- OG image missing → broken-looking shares
- Landing page is a one-pager that doesn't match the README

**Thresholds**
- Healthy: README exists + landing has H1 + OG image set
- Worrying: only README exists, or landing missing OG
- Broken: nothing exists, or 404 on the linked landing

---

## Stage 2 — Decision

**What we count**
- License present
- "What is" / "About" / "Overview" / "Why" section in README
- Demo link
- Recent activity (commits in last 30 days)

**What to look at**
- After 8 seconds, does the reader know what + who + why?
- Trust signals — is the project visibly maintained? Last commit date matters.
- For OSS specifically: license is non-negotiable. Without one, downstream users can't legally use the code.

**Common friction**
- README opens with installation steps before saying what the thing is
- No license file → enterprise / cautious users stop here
- Last commit was 14 months ago → looks abandoned

**Thresholds**
- Healthy: clear "what is" within the first 200 chars + license + recent activity
- Worrying: missing one of those three
- Broken: missing two or more

---

## Stage 3 — Install

**What we count**
- Install / Quick start / Getting started section present
- Number of shell commands counted in that section
- Required tools detected from manifest files (node, python, rust, etc.)
- Required env vars (counted from .env.example or grepped from src)

**What to look at**
- Can the install be copy-pasted as a single block?
- Are there hidden prerequisites (Postgres running, node 20+, ffmpeg installed)?
- Are env vars documented inline, or only in source code?
- What happens on Windows? On Linux without sudo?
- Is there a Docker option for users who'd rather not pollute their machine?

**Common friction**
- 8+ install commands
- Implicit dep on a system tool (`make`, `ffmpeg`, `pg_dump`) without a "you need…" note
- `cp .env.example .env` followed by 7 mandatory variables you have to obtain elsewhere
- Step says "configure your favorite database" with no help on which to use

**Thresholds**
- Healthy: ≤3 commands, install works on macOS / Linux / WSL
- Worrying: 4–6 commands, or 1 platform-specific gotcha
- Broken: 8+ commands, or platform-specific without a workaround

---

## Stage 4 — First run

**What we count**
- "Usage" / "Quick start" / "Example" section presence
- Code block count in that section
- Preview of the first code block

**What to look at**
- Is there a runnable example using fixture data, or does the user have to invent input?
- Does the example show output, or just a command?
- Does the example use real-looking data that matches the project's actual purpose?

**Common friction**
- "Run `node index.js` and follow the prompts" with no idea what to type
- Example uses a config file the user hasn't seen yet
- Output of the example isn't shown — user has to guess if it worked
- Example assumes a database that wasn't created in the install step

**Thresholds**
- Healthy: code block + showing input + showing expected output
- Worrying: code block input only, no output shown
- Broken: no code block at all, or "see the docs"

---

## Stage 5 — Activation

The aha moment. The single moment where the user thinks "oh, I get it, this is useful." Naming this moment is the most-valuable single output of a journey audit.

**What we count**
- Screenshot in README (any image)
- Demo URL
- Explicit naming of the activation moment ("what success looks like", etc.)

**What to look at**
- Does the README explicitly name the moment value lands?
- Is it 1 step, 5 steps, or 30 steps from "ran the install" to "saw the value"?
- Could activation be moved earlier? (e.g., a hosted demo before the install)

**Common friction**
- Activation requires the user to bring their own data (auth, content, etc.)
- Activation is "configure 12 things" before "see the result"
- Activation isn't named anywhere — the user has to guess what's good about this

**Thresholds**
- Healthy: ≤5 steps to first value + a hosted demo + screenshot
- Worrying: 5–10 steps, no demo, single screenshot
- Broken: >10 steps or activation isn't articulated anywhere

---

## Stage 6 — Return

**What we count**
- Changelog / CHANGES / HISTORY file presence
- "What's next" / "Going further" / "Advanced usage" section
- Recent commits (already from stage 1/2)

**What to look at**
- Is there a reason to come back next week / next month?
- Does the project ship visibly (changelog, releases, social posts)?
- Is there a follow-up artifact (newsletter, Discord, blog) the user can subscribe to?

**Common friction**
- No changelog → users can't tell if anything's improved
- "Once you've installed it, you're done" → no path forward
- No advanced section → users plateau

**Thresholds**
- Healthy: changelog + "next steps" + recent ship velocity
- Worrying: missing one
- Broken: missing all

---

## Stage 7 — Share

**What we count**
- Star / fork / Discord / chat badges in README
- Explicit share prompt ("if you liked this, please star")
- OG image (already from stage 1)

**What to look at**
- Is there a shareable artifact the user produces (a screenshot, a generated image, a result link)?
- Is the OG image worth sharing? (A pretty image gets shared; a default GitHub repo card doesn't.)
- Is there a "tell a friend" moment in the UX?

**Common friction**
- No share artifact: tools that produce no output are hard to share
- Share asks too early ("STAR THIS REPO" at the top of the README without proof)
- Share asks too late (footer-buried where nobody looks)

**Thresholds**
- Healthy: shareable artifact + appropriate share prompt + good OG
- Worrying: missing one
- Broken: project is fundamentally not share-able (e.g., a CLI tool with no visual output, no badge, no community)

---

## How to read the totals

The script returns a stage-by-stage score (each 0–10) and a total out of 70. Map:

- **60–70:** Mature journey. Most users will activate. Time to grow.
- **45–59:** Real gaps. The walkthrough will surface 3–5 actionable fixes.
- **30–44:** Foundations missing. Walkthrough will read like a list of "this entire stage isn't there yet."
- **<30:** Don't launch yet. Either the README needs a major pass or the activation moment hasn't been designed.

The score is a starting point. The persona walkthroughs are where the actual insight lives — read them in the audit file.
