# Awesome-list submission packet

How to submit to a GitHub awesome-list without getting ignored or rejected. Awesome-lists are one of the highest-leverage compounding traffic sources for an indie project — but maintainers are picky and the wrong submission burns the relationship.

## Pre-flight checklist

Before opening a PR, confirm:

1. **The list is alive.** Last commit within the last 90 days. If it's older, the list is effectively dead — submitting won't get merged.
2. **Your project fits the list's scope.** Read the list's CONTRIBUTING.md or the existing entries — is your project actually similar in shape, or is it a stretch?
3. **You read the contribution guide.** Some lists require: test the link works, alphabetical ordering, exactly N words in the description, no marketing language, English-only. Following these saves a "please fix and resubmit" round.
4. **Your project is good enough.** ≥10 stars on its own (not from your friends), a working README, a license file. If the project itself isn't ready, the awesome-list submission is premature.

## The submission line

99% of awesome-lists use this exact pattern:

```markdown
- [Project name](URL) - One-line description. Tags or context if appropriate.
```

Examples that work:

```markdown
- [Megaphone](https://github.com/x/megaphone) - Local-first launch toolkit for indie projects. Drafts posts, schedules launches, audits landing pages.

- [Postiz](https://github.com/gitroomhq/postiz-app) - Open-source social media scheduler with 30+ providers and AI agents. Self-hostable.
```

Notes:
- **Period at the end** of the description — most lists require it.
- **Sentence case** unless the list uses title case throughout.
- **Don't oversell.** "Powerful, fast, easy-to-use scheduler" gets rejected; "Open-source social media scheduler" gets merged.
- **Match the list's existing style.** If every other entry uses a verb opener ("Schedules…", "Generates…"), use a verb. If every other entry uses noun phrases, use a noun phrase.

## How to open the PR

```bash
git clone https://github.com/<owner>/<awesome-list>
cd <awesome-list>
git checkout -b add-<project-name>
# Edit README.md to add your line in the right section, in alphabetical order
git add README.md
git commit -m "Add <project name>"
git push origin add-<project-name>
# Open PR via GitHub web UI
```

PR title format that works: `Add <project name>` — short and specific.

PR description that works:

```markdown
Hi! Adding <project name> to <section>.

<One-paragraph: what it does, who it's for, why it fits this list>

- License: MIT
- Stars: <real number>
- Last release: <date>
- Tested the link works ✓
- Alphabetical order ✓
- Followed the description format in CONTRIBUTING.md ✓
```

That last checklist signals you read the contribution guide. Maintainers merge these PRs faster.

## What to NEVER do

- **Don't open a PR for a project that isn't yours** without permission from the project's maintainer.
- **Don't submit duplicate PRs** to the same list (one PR for v1, another for v2). Edit the existing PR if you need to.
- **Don't argue if a maintainer rejects.** Their list, their rules. Move on; submit to a different list.
- **Don't include your own project in PRs adding other projects.** That's the fastest way to get a PR closed.
- **Don't promote outside the merge.** "And while you're here, please RT my launch" turns the PR into spam.
- **Don't spam-submit to lists that don't fit.** Maintainers talk to each other; one bad submission can blacklist you across multiple lists.

## What a "soft no" looks like

Sometimes maintainers don't reject the PR — they just don't merge. Reasons:
- Your project is borderline-fit (technically meets the criteria, but isn't really what the list curates)
- Your project is too new (some lists wait for ≥100 stars before merging)
- The maintainer is overloaded (legitimate; bump after 14 days, once)

If 30 days pass with no merge and no comment, close the PR yourself with a short polite note ("happy to resubmit when <project> is more mature; thanks for the awesome list"). This preserves the relationship.

## When to NOT submit

- **The list is dead** (no commits in 6+ months).
- **The list explicitly bans your project's category** ("no AI tools" lists won't take an AI tool, however much you reframe it).
- **Your project doesn't fit but you want to "try anyway"** — don't. The maintainer will close it and remember you.
- **You haven't read the existing entries.** If you don't know what the list curates, your submission is going to feel off, no matter how well-written.

## After the merge

- Tweet / Bluesky / LinkedIn post: "Just got added to <awesome-list>! [link]" — the maintainer often reciprocates with a like or quote.
- DM a thank-you to the maintainer. Don't ask for anything else; just thank them.
- Update your repo's README to mention "Featured in <awesome-list>." This raises trust signal for visitors.

## How megaphone helps

The skill produces, per top-tier awesome-list, a packet at `.megaphone/outreach/venues/<list-slug>/packet.md` with:

- The exact line to add (matching the list's format)
- The PR title and description
- The fork-clone-edit-PR command sequence
- Notes on the list's specific quirks (alphabetical, license requirement, etc.)

You then run the commands and open the PR. Megaphone never opens PRs on your behalf.
