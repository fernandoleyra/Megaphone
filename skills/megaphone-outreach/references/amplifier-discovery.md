# Amplifier discovery

How to find the 5–10 humans who'd plausibly share an indie project. The point isn't volume; it's fit. Five personalized DMs land more than 50 sprayed templates.

## Where to look — by source

### 1. Recent Product Hunt launches in the same category

Visit https://www.producthunt.com/categories/<category> and pull top launches from the last 90 days. The makers of those products are:

- Already in this niche
- Already comfortable launching things publicly
- Often willing to RT or comment on similar launches if asked respectfully

For each maker, capture: their X / Bluesky handle, the product they launched, the date, and one specific thing about that product that connects to yours.

### 2. Recent Show HN posts on the topic

Search https://hn.algolia.com for `Show HN: <topic keyword>` filtered to last year. The submitter (`@username` on HN) often has a personal site / X account / GitHub linked from their HN profile.

Show HN submitters tend to be:
- Technical, opinionated
- More likely to engage if your project shows good engineering taste
- Active on HN (so a comment from them on your Show HN day matters)

### 3. dev.to authors who covered similar problems

Search https://dev.to/search?q=<topic>&filter_by=articles. Authors with multiple articles in the topic tend to be:
- Influencers in the niche on dev.to specifically (where the article-feed traffic happens)
- Open to writing follow-up posts mentioning related tools, especially OSS

For each author, capture: dev.to handle, their best-performing article on the topic (link), and one specific takeaway from that article.

### 4. Maintainers of upstream tools you build on

If your project uses Tool X, the maintainer of Tool X often appreciates a heads-up that something interesting is being built on their work. They may mention it in their newsletter, README "ecosystem" section, or social.

For each upstream maintainer, capture: GitHub handle, the specific way your project depends on / extends their tool, what category your project fits into within their ecosystem.

This source has the highest hit rate of all five — maintainers are flattered when their tool is the foundation of something cool, and they're often the ones with the most credibility with your exact target audience.

### 5. Authors of relevant awesome-lists

Awesome-list maintainers are gatekeepers and amplifiers in one. If your project would fit their list, they're a double-win: they can both add it AND mention it on their socials.

For each, capture: GitHub handle, list name, the most-recent additions to the list (so you understand what they consider on-topic).

### 6. Podcast hosts in the niche

Search https://www.listennotes.com/?q=<topic> or https://podchaser.com. Podcast hosts looking for episode topics in your niche are excellent targets — but with a much higher bar (you need to be a guest-worthy story, not just a tool).

For each, capture: host name, podcast name, the most recent episode that touches your niche, and the angle from your project that would be a fit for their show.

### 7. Newsletter editors

TLDR, Console.dev, Pointer, JavaScript Weekly, Python Weekly, Hashnode digest, Bytes — all editorialize their picks. They have public submission forms but personalized email to the editor (where findable) outperforms the form.

For each, capture: editor name, newsletter name, recent picks that match your category. Submit via the public form first (it's the "respectful" channel), DM only if you have a real connection point.

---

## Scoring amplifiers

Once you have candidates, score each on three axes (1–5 each):

- **Specificity of connection** — how concrete is the link between their work and yours? "They wrote about indie launches" is generic; "they wrote a 2,000-word post about Postiz, which is what megaphone-publish replaces" is specific.
- **Audience overlap** — would their followers actually use your project? A 100k-follower lifestyle creator who once mentioned indie hacking has lower overlap than a 5k-follower indie maker who tweets daily about their projects.
- **Activity** — have they posted in the last 30 days? Some "amplifiers" are inactive accounts.

`score = specificity × audience_overlap × activity` (out of 125).

Top 10 by score = your outreach list. The rest are noise.

---

## What NOT to do

- **Don't pick by follower count.** A 1,000-follower indie maker with high overlap is a better target than a 100,000-follower generalist.
- **Don't pitch competitors.** They'll either ignore or roast you. Save your reach for people who'd actually amplify.
- **Don't pitch ghosts.** If their last post is 6+ months old, skip — the DM lands in an inactive inbox.
- **Don't pitch journalists who don't cover your beat.** A TechCrunch reporter covering enterprise AI isn't going to write about your indie tool. Pitch the right beat.
- **Don't add the same person three times** through different channels (X DM + email + LinkedIn). Pick one channel and use it.

---

## What "specific recent work" means

This is the make-or-break detail. The DM template assumes you can name something concrete the recipient did recently. Concrete means:

- ✅ "Your thread last Tuesday on observability tools" (date + topic + format)
- ✅ "Your dev.to post 'Why I switched from Mongo to Postgres'" (exact title)
- ✅ "Your launch of <product> on Product Hunt" (named product + venue)
- ❌ "Your interest in indie hacking" (vague)
- ❌ "Your great content" (lazy)
- ❌ "Your work in tech" (means nothing)

If you can't name something concrete after 5 minutes of looking, the recipient isn't a great fit for personalized outreach. Move to the next candidate.

---

## Volume over a 30-day launch window

A reasonable distribution of outreach over the launch window:

- **T-30 to T-15:** identify 10 amplifiers, 15 venues
- **T-14 to T-7:** send 3–5 personalized DMs (high-fit amplifiers; ask for "mentions if it lands"); submit to 2 awesome-lists
- **T-6 to T-1:** send remaining DMs (medium-fit amplifiers); finalize submission packets
- **T 0 (launch day):** quick follow-ups to amplifiers ("today's the day; if you want to share, here's the link")
- **T+1 to T+7:** thank-yous to anyone who shared; recap post; submit to remaining venues

Total volume: ~10 DMs sent, ~15 submissions. Expected yes-rate: 20–40% for DMs from a real reply, ~80% for submissions to fitting venues.

If your reply rate is below 20%, the issue is almost always the DMs themselves: too generic, no concrete reference, or wrong audience match. Iterate on the messages, not the volume.
