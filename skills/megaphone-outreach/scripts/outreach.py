#!/usr/bin/env python3
"""Megaphone outreach helper.

Two subcommands:
  - venues: score launch venues (awesome-lists, directories, subreddits, newsletters,
            communities) by audience-fit × active / effort
  - amplifiers: score humans (creators, maintainers, podcasters) by
                specificity × audience-overlap × activity

Both produce JSON the skill (Claude) reads, augments with web-search results,
and turns into ranked submission packets and DM drafts.

Stdlib only. The script provides scaffolding + scoring; the actual searching
for venues and amplifiers is delegated to Claude via web search at runtime."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Built-in venue catalog — generic launch directories that exist in 2026.
# Niche subreddits / awesome-lists / newsletters get added by Claude via web
# search at runtime; the JSON output of this script is the seed Claude builds on.
# ---------------------------------------------------------------------------

CATALOG = {
    "directories": [
        {"name": "Product Hunt", "url": "https://www.producthunt.com",
         "audiences": ["consumer", "saas", "indie"], "free": True,
         "wait_days": 0, "submit_difficulty": 3,
         "notes": "Tue/Wed 12:01am PST is the sweet spot. Top 5 needs 300-600 upvotes."},
        {"name": "BetaList", "url": "https://betalist.com",
         "audiences": ["pre-launch", "waitlist"], "free": True,
         "wait_days": 28, "submit_difficulty": 1,
         "notes": "4-week wait for free. Best for pre-launch with email capture."},
        {"name": "Peerlist Launchpad", "url": "https://peerlist.io/launchpad",
         "audiences": ["indie", "designers", "developers"], "free": True,
         "wait_days": 7, "submit_difficulty": 2,
         "notes": "Weekly Launchpad. Forum-style, supportive."},
        {"name": "DevHunt", "url": "https://devhunt.org",
         "audiences": ["developers", "developer-tools"], "free": True,
         "wait_days": 42, "submit_difficulty": 2,
         "notes": "6-week wait free, $49 for next-week placement."},
        {"name": "TinyLaunch", "url": "https://tinylaunch.com",
         "audiences": ["indie", "side-projects"], "free": True,
         "wait_days": 7, "submit_difficulty": 1,
         "notes": "Weekly leaderboard, top 3 get a badge."},
        {"name": "Smol Launch", "url": "https://smollaunch.com",
         "audiences": ["indie"], "free": True, "wait_days": 7, "submit_difficulty": 1},
        {"name": "Open Launch", "url": "https://open-launch.com",
         "audiences": ["indie", "saas"], "free": True, "wait_days": 7, "submit_difficulty": 1},
        {"name": "Indie Hackers", "url": "https://indiehackers.com",
         "audiences": ["indie", "founders"], "free": True, "wait_days": 0, "submit_difficulty": 1,
         "notes": "Self-post format; founder narrative works best."},
        {"name": "Hacker News (Show HN)", "url": "https://news.ycombinator.com",
         "audiences": ["developers", "technical"], "free": True, "wait_days": 0,
         "submit_difficulty": 4,
         "notes": "Human submission only. Tue/Thu 7-9am PT. Format: 'Show HN: <project> – <one-liner>'."},
        {"name": "AlternativeTo", "url": "https://alternativeto.net",
         "audiences": ["consumer", "saas"], "free": True, "wait_days": 14, "submit_difficulty": 2,
         "notes": "Best when your project replaces a known tool — name the alternative."},
        {"name": "There's An AI For That", "url": "https://theresanaiforthat.com",
         "audiences": ["ai-tools"], "free": True, "wait_days": 14, "submit_difficulty": 2},
        {"name": "Uneed", "url": "https://uneed.best",
         "audiences": ["indie", "tools"], "free": True, "wait_days": 7, "submit_difficulty": 1},
        {"name": "Fazier", "url": "https://fazier.com",
         "audiences": ["indie"], "free": True, "wait_days": 7, "submit_difficulty": 1},
    ],
    "newsletters": [
        {"name": "TLDR", "url": "https://tldr.tech/submit",
         "audiences": ["developers", "tech-news"], "free": True,
         "submit_difficulty": 3, "notes": "High bar, broad audience. Pitch before launch."},
        {"name": "Console.dev", "url": "https://console.dev/submit/",
         "audiences": ["developers", "developer-tools"], "free": True, "submit_difficulty": 2},
        {"name": "Pointer", "url": "https://www.pointer.io",
         "audiences": ["engineering-leaders"], "free": True, "submit_difficulty": 3},
        {"name": "Bytes", "url": "https://bytes.dev",
         "audiences": ["javascript", "frontend"], "free": True, "submit_difficulty": 2},
        {"name": "JavaScript Weekly", "url": "https://javascriptweekly.com/contact",
         "audiences": ["javascript"], "free": True, "submit_difficulty": 2},
        {"name": "Python Weekly", "url": "https://www.pythonweekly.com",
         "audiences": ["python"], "free": True, "submit_difficulty": 2},
        {"name": "Hashnode digest", "url": "https://hashnode.com",
         "audiences": ["developers", "blogging"], "free": True, "submit_difficulty": 2},
    ],
    "subreddits_by_audience": {
        "indie": ["SideProject", "indiehackers", "Entrepreneur"],
        "developers": ["programming", "webdev", "coolgithubprojects"],
        "saas": ["SaaS", "startups"],
        "ai-tools": ["singularity", "artificial", "OpenAI"],
        "javascript": ["javascript", "reactjs", "node"],
        "python": ["Python", "learnpython"],
        "designers": ["Design", "web_design"],
        "open-source": ["opensource", "github"],
        "consumer": ["InternetIsBeautiful"],
    },
}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_venue(profile: dict, venue: dict) -> dict:
    """Return {audience_fit, effort, active, score}."""
    aud_primary = (profile.get("audience") or {}).get("primary", "").lower()
    aud_niches = [n.lower() for n in (profile.get("audience") or {}).get("niches", [])]
    venue_audiences = [a.lower() for a in venue.get("audiences", [])]

    overlap = sum(1 for a in venue_audiences if a == aud_primary or a in aud_niches)
    audience_fit = max(1, min(5, overlap + 2))  # at least 1, at most 5
    effort = max(1, min(5, venue.get("submit_difficulty", 2)))
    active = 5  # baseline; the qualitative pass refines this with last-update info
    score = (audience_fit * active) / effort
    return {
        "audience_fit": audience_fit,
        "effort": effort,
        "active": active,
        "score": round(score, 2),
    }


def cmd_venues(args) -> None:
    profile_path = Path(args.profile)
    if not profile_path.exists():
        sys.exit(f"ERROR: profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text())

    aud_primary = (profile.get("audience") or {}).get("primary", "").lower()
    aud_niches = [n.lower() for n in (profile.get("audience") or {}).get("niches", [])]

    venues_out = []

    # Directories + newsletters from the catalog
    for category in ("directories", "newsletters"):
        for v in CATALOG[category]:
            scored = score_venue(profile, v)
            venues_out.append({**v, "type": category[:-1], **scored})

    # Subreddit suggestions per audience
    seen = set()
    for aud in [aud_primary] + aud_niches:
        for sub in CATALOG["subreddits_by_audience"].get(aud, []):
            if sub in seen:
                continue
            seen.add(sub)
            v = {
                "name": f"r/{sub}",
                "url": f"https://reddit.com/r/{sub}",
                "audiences": [aud],
                "free": True,
                "submit_difficulty": 3,
                "notes": "Verify subreddit rules around self-promotion before posting.",
                "type": "subreddit",
            }
            scored = score_venue(profile, v)
            venues_out.append({**v, **scored})

    venues_out.sort(key=lambda x: x["score"], reverse=True)

    out = {
        "ok": True,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "audience_primary": aud_primary,
        "audience_niches": aud_niches,
        "seed_venues": venues_out,
        "next_steps": [
            "Use Claude web search to find awesome-lists matching the project's topics; merge into this list.",
            "Filter out venues with stale activity (last commit / post >90 days).",
            "Cap final list at 15.",
            "Generate per-venue submission packets in .megaphone/outreach/venues/<slug>/packet.md.",
        ],
    }
    _emit(out, args.output)


def cmd_amplifiers(args) -> None:
    """Outputs a search plan + a structured slot list for Claude to fill in.

    Heuristic discovery (Product Hunt makers, Show HN posters, dev.to authors,
    podcast hosts, awesome-list maintainers) is done by Claude via web search.
    This script just provides the scaffolding so the output is consistent."""
    profile_path = Path(args.profile)
    if not profile_path.exists():
        sys.exit(f"ERROR: profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text())

    aud_primary = (profile.get("audience") or {}).get("primary", "")
    niches = (profile.get("audience") or {}).get("niches", [])
    project_name = (profile.get("project") or {}).get("name", "")

    queries = [
        {"source": "product_hunt_makers", "query": f"top {aud_primary} launches Product Hunt last 90 days"},
        {"source": "show_hn", "query": f"Show HN {' OR '.join(niches[:3])} site:news.ycombinator.com"},
        {"source": "devto_authors", "query": f"\"{niches[0] if niches else aud_primary}\" site:dev.to"},
        {"source": "awesome_list_maintainers", "query": f"awesome {niches[0] if niches else aud_primary} site:github.com"},
        {"source": "podcasts", "query": f"{aud_primary} podcast indie maker site:listennotes.com"},
        {"source": "newsletters", "query": f"{aud_primary} newsletter site:tldr.tech OR site:console.dev"},
    ]

    out = {
        "ok": True,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "project": project_name,
        "audience": aud_primary,
        "niches": niches,
        "search_plan": queries,
        "amplifier_slots": [
            {"source": q["source"], "candidates": []} for q in queries
        ],
        "next_steps": [
            "For each search query, run web search and populate the candidates array with: {handle, platform, recent_work_title, recent_work_url, connection_to_project}.",
            "Score each candidate on (specificity × audience_overlap × activity).",
            "Keep top 10 across all sources.",
            "Generate a personalized DM draft per candidate using references/dm-templates.md.",
        ],
    }
    _emit(out, args.output)


def _emit(obj: dict, output: Optional[str]) -> None:
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text)
        print(json.dumps({"ok": True, "output": output}))
    else:
        print(text)


def main() -> None:
    p = argparse.ArgumentParser(description="Megaphone outreach helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("venues", help="Score launch venues for this project")
    v.add_argument("--profile", required=True, help="Path to .megaphone/profile.json")
    v.add_argument("--output", help="Optional path to write the JSON")
    v.set_defaults(func=cmd_venues)

    a = sub.add_parser("amplifiers", help="Build a search plan for amplifiers (Claude fills in)")
    a.add_argument("--profile", required=True)
    a.add_argument("--output")
    a.set_defaults(func=cmd_amplifiers)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
