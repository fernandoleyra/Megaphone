# Personas for the journey walkthrough

Three default personas covering most indie / vibe-coder audiences. Adapt or replace per project — `.megaphone/profile.json` may name a more specific audience that beats these.

When walking the journey for each persona, narrate in second person ("You see…"), keep the tone observational not prescriptive, and at every friction point write a `[FRICTION-<severity>]` callout.

Severity scale:
- `low` — adds a small amount of cognitive load; user proceeds
- `medium` — visibly slows the user; some users abandon
- `high` — most users abandon at this point
- `blocker` — journey ends here

---

## Casey — the vibe coder

**Background:** Built their last project with Lovable / v0 / Cursor without writing a line of code. Comfortable shipping HTML/CSS, can edit a Next.js component if it's mostly there. Doesn't have a terminal-based mental model. Saw your project mentioned on Bluesky. Reading on phone.

**What they look for:**
- Can I see what this is in 5 seconds, on mobile?
- Is there a "try it" link that doesn't require an install?
- If I have to install, can I copy-paste two commands and be done?
- Does it look maintained?

**What they ignore:**
- Architecture diagrams
- Performance benchmarks
- Anything in a small font or below the third scroll

**Where they typically drop off:**
- README opens with "## Architecture"
- Install requires `git clone` + `cd` + `python3 -m venv` + `source venv/bin/activate` + `pip install` + `cp .env.example .env` + filling 7 env vars
- Demo only runs on macOS with X11
- "First run" section says "see the docs"

**What activates them:**
- Demo URL they can click
- Hosted free trial
- Single-command install with sensible defaults
- A screenshot that shows the value

**What they share:**
- A shareable artifact (a generated image, a tweet preview, a result)
- A pretty landing page they can paste into Bluesky

---

## Dani — the senior dev

**Background:** 12 years building software, currently a tech lead at a Series B startup. Browses HN at 7am, opens 4–5 GitHub repos, stars one, closes the rest. Has strong opinions about prose, tooling, and unnecessary abstractions.

**What they look for:**
- What problem does this solve? (literally the first sentence)
- What does it replace? (in their existing toolkit)
- What does the code look like? (often clicks `src/` before reading the README)
- Is the maintainer credible? (last commit date, issue response times)

**What they ignore:**
- Marketing language ("revolutionary", "10x", "next-gen")
- Vague benefits ("makes your life easier")
- Roadmap promises
- Any reference to "AI-powered" without specifics

**Where they typically drop off:**
- First paragraph doesn't say what the project DOES (technically)
- README has fewer than 50 lines, no example
- Last commit is >6 months old
- Maintainer has 0 response on open issues
- It's "yet another X" without naming the X clearly

**What activates them:**
- A code example in the README that compiles/runs as-is
- A clear "vs" comparison table against the obvious alternative
- A concrete benchmark (with numbers, not "fast")
- Installable in one command without yak-shaving

**What they share:**
- A code snippet of what surprised them (positively)
- A retweet of the maintainer if the project shows good taste

---

## Sam — the newcomer to the stack

**Background:** Knows JavaScript well; has only run Python scripts that someone else wrote. On a Windows laptop. Found your project by searching "[the problem this solves]" on Google. Determined to make it work but lacks the muscle memory.

**What they look for:**
- Does this run on Windows? (or do they have to use WSL?)
- Are the install steps explicit about which interpreter to use?
- Will the example in the README actually run for them?
- Is there a community to ask questions in?

**What they ignore:**
- Unix-only assumptions (they'll Google around them, but it'll cost them)

**Where they typically drop off:**
- README assumes `python3` (Windows ships `python` not `python3`)
- Install requires `make` (not native on Windows)
- Required env vars include things only documented in the source code
- Error messages on first run are unhelpful (e.g. `KeyError: 'OPENAI_API_KEY'` with no hint about what's needed)

**What activates them:**
- Cross-platform install (`pip install x` works regardless of OS)
- Helpful error messages ("OPENAI_API_KEY environment variable required — see README §Setup")
- A Discord / community link
- A "common errors" section in the README

**What they share:**
- Almost never. They'll come back and use the tool quietly. To get them to share, the project has to actively prompt + give them an easy share artifact.

---

## How to choose / replace personas

If `.megaphone/profile.json` lists a specific audience (e.g., `audience.primary: "designers"`, `audience.niches: ["figma users"]`), replace one of the defaults with a persona shaped to that audience. The structure is the same: background, what they look for, what they ignore, where they drop off, what activates them, what they share.

If the project is B2B / enterprise:
- Replace Casey with **Priya, the platform engineer at a 200-person company** — needs an SSO story, on-prem option, license terms.
- Keep Dani.
- Replace Sam with **Jordan, the developer doing a buy-vs-build evaluation** — needs comparison data, total cost of ownership.

If the project is consumer:
- Replace Dani with **Morgan, the discerning power user** — has opinions, will tweet a screenshot if it's good.

Be honest about the audience. A persona walkthrough that uses the wrong personas is worse than no walkthrough.
