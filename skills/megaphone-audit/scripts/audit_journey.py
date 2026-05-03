#!/usr/bin/env python3
"""Megaphone user-journey audit (static layer).

Inspects the repo + (optional) landing URL/file and emits a structured JSON
report covering the seven journey stages. The skill (Claude) reads the JSON
and walks personas through it for the qualitative half.

Stdlib only."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Repo introspection
# ---------------------------------------------------------------------------

def find_readme(repo: Path) -> Optional[Path]:
    for cand in ("README.md", "README.MD", "Readme.md", "readme.md", "README"):
        p = repo / cand
        if p.exists():
            return p
    return None


def read_section(text: str, *titles: str) -> Optional[str]:
    """Extract the body of a markdown section by H1/H2/H3 title (any of)."""
    pat = r"^(#{1,3})\s*(?:" + "|".join(re.escape(t) for t in titles) + r")\b.*$"
    m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    start = m.end()
    # End at the next heading of equal-or-higher level.
    level = len(m.group(1))
    next_heading = re.search(rf"^{'#' * level}\s+", text[start:], re.MULTILINE)
    if next_heading:
        return text[start:start + next_heading.start()].strip()
    return text[start:].strip()


def install_steps_count(readme: str) -> dict:
    """Count steps in install / quick-start / getting-started.

    Heuristic: lines that start with `$`, `>`, `npm `, `pip `, `pnpm `,
    `yarn `, `cargo `, `go `, or are inside a fenced code block of a
    likely-shell language."""
    out = {"steps": 0, "code_blocks": 0, "section_found": False, "preview": None}
    body = read_section(readme, "Install", "Installation", "Quick start", "Quickstart", "Getting started", "Setup")
    if not body:
        return out
    out["section_found"] = True
    out["preview"] = body[:500]
    # Pull fenced code blocks
    for fence in re.findall(r"```(?:bash|sh|shell|console|zsh|cmd|powershell)?\s*\n(.*?)```", body, re.DOTALL):
        out["code_blocks"] += 1
        for line in fence.strip().splitlines():
            ln = line.strip()
            if not ln or ln.startswith("#"):
                continue
            if ln.startswith("$") or ln.startswith(">"):
                out["steps"] += 1
            elif re.match(r"^(npm|pnpm|yarn|pip|pip3|pipx|cargo|go|brew|apt|sudo|curl|wget|git|docker|make|bun|deno) ", ln):
                out["steps"] += 1
    return out


def required_tools(repo: Path, readme: str) -> list[str]:
    tools = set()
    if (repo / "package.json").exists():
        tools.add("node")
    if any((repo / f).exists() for f in ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile")):
        tools.add("python")
    if (repo / "Cargo.toml").exists():
        tools.add("rust")
    if (repo / "go.mod").exists():
        tools.add("go")
    if (repo / "Dockerfile").exists() or (repo / "docker-compose.yml").exists():
        tools.add("docker")
    if (repo / "Gemfile").exists():
        tools.add("ruby")
    if re.search(r"\bnode(\.js)?\b", readme, re.IGNORECASE):
        tools.add("node")
    if re.search(r"\bpython\b", readme, re.IGNORECASE):
        tools.add("python")
    return sorted(tools)


def env_vars_required(repo: Path) -> dict:
    env_count = 0
    sources = []
    examples = repo / ".env.example"
    if examples.exists():
        for line in examples.read_text(errors="replace").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                env_count += 1
        sources.append(".env.example")
    # Cheap grep across common src dirs
    for sub in ("src", "app", "lib"):
        d = repo / sub
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix in (".js", ".ts", ".tsx", ".jsx", ".py"):
                    try:
                        text = f.read_text(errors="replace")
                    except (OSError, UnicodeDecodeError):
                        continue
                    matches = re.findall(r"process\.env\.([A-Z_][A-Z0-9_]*)|os\.environ\[['\"]([A-Z_][A-Z0-9_]*)['\"]\]|os\.getenv\(['\"]([A-Z_][A-Z0-9_]*)['\"]", text)
                    for m in matches:
                        for v in m:
                            if v:
                                sources.append(v)
            break
    sources_unique = sorted(set(sources))
    if not env_count and sources_unique:
        env_count = len(sources_unique)
    return {"count": env_count, "sample": sources_unique[:10]}


def first_run_signals(readme: str) -> dict:
    """Look for a runnable example following the install section."""
    body = read_section(
        readme,
        "First run", "First-run",
        "Usage", "Quick start", "Quickstart",
        "Getting started", "Get started",
        "Example", "Examples",
        "Typical first session", "First session",
    )
    out = {"section_found": body is not None, "code_block_count": 0, "first_block_preview": None}
    if not body:
        return out
    blocks = re.findall(r"```[a-z]*\s*\n(.*?)```", body, re.DOTALL)
    out["code_block_count"] = len(blocks)
    if blocks:
        out["first_block_preview"] = blocks[0].strip()[:400]
    return out


def activation_signals(readme: str) -> dict:
    out = {"has_screenshot": False, "names_aha": False, "has_demo_url": False}
    if re.search(r"!\[[^\]]*\]\([^)]+\)", readme):
        out["has_screenshot"] = True
    if re.search(r"\bdemo\b.*?https?://", readme, re.IGNORECASE):
        out["has_demo_url"] = True
    if re.search(r"(what (it|this) does|the aha|first useful|first value|success looks like)", readme, re.IGNORECASE):
        out["names_aha"] = True
    return out


def return_signals(repo: Path, readme: str) -> dict:
    out = {"changelog": False, "what_next_section": False, "advanced_section": False, "last_release": None}
    for cand in ("CHANGELOG.md", "CHANGES.md", "HISTORY.md"):
        if (repo / cand).exists():
            out["changelog"] = True
            break
    if read_section(readme, "What's next", "Going further", "Next steps", "Roadmap", "What's coming"):
        out["what_next_section"] = True
    if read_section(readme, "Advanced", "Advanced usage"):
        out["advanced_section"] = True
    return out


def share_signals(readme: str) -> dict:
    out = {"badges": 0, "share_prompt": False}
    # Markdown badge syntax: ![alt](url)
    md_badges = re.findall(
        r"!\[[^\]]*\]\(https?://(?:img\.shields\.io|github\.com|api\.codacy\.com|api\.codeclimate\.com|codecov\.io|app\.codacy\.com|circleci\.com|travis-ci\.com|travis-ci\.org)[^)]*\)",
        readme,
    )
    # HTML badge syntax: <img src="https://img.shields.io/..."> — common when README centers badges in a <p>
    html_badges = re.findall(
        r'<img[^>]+src=["\']https?://(?:img\.shields\.io|github\.com|api\.codacy\.com|api\.codeclimate\.com|codecov\.io|app\.codacy\.com|circleci\.com|travis-ci\.com|travis-ci\.org)[^"\']*["\'][^>]*>',
        readme,
        re.IGNORECASE,
    )
    out["badges"] = len(md_badges) + len(html_badges)
    if re.search(r"(if you (like|enjoyed)|star (the|this) repo|share if|please star|consider starring)", readme, re.IGNORECASE):
        out["share_prompt"] = True
    return out


def recent_activity(repo: Path) -> dict:
    """Use `git log` if available; else fall back to mtime of common files."""
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "log", "--since=30.days", "--pretty=format:%h"],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode == 0:
            commits = [l for l in proc.stdout.splitlines() if l.strip()]
            return {"commits_last_30d": len(commits), "source": "git"}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {"commits_last_30d": None, "source": "unavailable"}


# ---------------------------------------------------------------------------
# Landing fetch (lightweight; full audit lives in megaphone-audit landing mode)
# ---------------------------------------------------------------------------

def fetch_landing(target: str) -> dict:
    if not target:
        return {"available": False}
    try:
        if target.startswith("http"):
            req = urllib.request.Request(target, headers={"User-Agent": "megaphone-audit-journey/0.4"})
            with urllib.request.urlopen(req, timeout=15) as r:
                body = r.read().decode("utf-8", errors="replace")
        else:
            p = Path(target)
            if p.is_dir():
                p = p / "index.html"
            body = p.read_text(errors="replace")
    except Exception as e:  # noqa: BLE001
        return {"available": False, "error": str(e)}
    title = (re.search(r"<title>(.*?)</title>", body, re.IGNORECASE | re.DOTALL) or [""])
    title = title.group(1).strip() if hasattr(title, "group") else ""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.IGNORECASE | re.DOTALL)
    h1_text = re.sub(r"<[^>]+>", " ", h1.group(1)).strip() if h1 else None
    og_image = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', body, re.IGNORECASE)
    return {
        "available": True,
        "title": title,
        "h1": h1_text,
        "og_image_present": bool(og_image),
        "byte_size": len(body),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="Path to the project repo")
    p.add_argument("--landing", default=None, help="URL or path to local landing HTML (optional)")
    p.add_argument("--output", help="Optional path to write the JSON report")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(json.dumps({"ok": False, "error": f"repo not found: {repo}"}))
        sys.exit(2)

    readme_path = find_readme(repo)
    readme = readme_path.read_text(errors="replace") if readme_path else ""

    discovery = {
        "readme_found": readme_path is not None,
        "readme_first_200": readme[:200] if readme else None,
        "landing": fetch_landing(args.landing) if args.landing else {"available": False},
    }
    decision = {
        "license_present": (repo / "LICENSE").exists() or (repo / "LICENSE.md").exists(),
        "what_is_section": bool(read_section(readme, "What is", "About", "Overview", "Why", "What it does")),
        "demo_link": bool(re.search(r"\bdemo\b.*?https?://", readme, re.IGNORECASE)),
        "recent_activity": recent_activity(repo),
    }
    install = install_steps_count(readme)
    install["required_tools"] = required_tools(repo, readme)
    install["env_vars"] = env_vars_required(repo)
    first_run = first_run_signals(readme)
    activation = activation_signals(readme)
    ret = return_signals(repo, readme)
    share = share_signals(readme)

    # Stage-level scoring (0–10 each, summed to 70 total)
    def stage_score():
        s = {}

        # Discovery
        d = 0
        if discovery["readme_found"]:
            d += 4
        if discovery["landing"].get("available"):
            d += 3
        if discovery["landing"].get("og_image_present"):
            d += 3
        s["discovery"] = d

        # Decision
        d = 0
        if decision["what_is_section"]:
            d += 4
        if decision["license_present"]:
            d += 2
        if decision["demo_link"]:
            d += 2
        ra = decision["recent_activity"].get("commits_last_30d")
        if ra is not None and ra > 0:
            d += 2
        s["decision"] = d

        # Install
        d = 0
        if install["section_found"]:
            d += 4
        steps = install.get("steps", 0)
        if steps == 0:
            d += 0
        elif steps <= 3:
            d += 4
        elif steps <= 6:
            d += 2
        if install["env_vars"]["count"] <= 1:
            d += 2
        s["install"] = d

        # First run
        d = 0
        if first_run["section_found"]:
            d += 5
        if first_run["code_block_count"] >= 1:
            d += 5
        s["first_run"] = d

        # Activation
        d = 0
        if activation["has_screenshot"]:
            d += 4
        if activation["has_demo_url"]:
            d += 3
        if activation["names_aha"]:
            d += 3
        s["activation"] = d

        # Return
        d = 0
        if ret["changelog"]:
            d += 4
        if ret["what_next_section"]:
            d += 3
        if ret["advanced_section"]:
            d += 3
        s["return"] = d

        # Share
        d = 0
        if share["badges"] >= 1:
            d += 4
        if share["share_prompt"]:
            d += 3
        if discovery["landing"].get("og_image_present"):
            d += 3
        s["share"] = d

        return s

    stage_scores = stage_score()
    total = sum(stage_scores.values())
    report = {
        "ok": True,
        "audited_at": _dt.datetime.utcnow().isoformat() + "Z",
        "repo": str(repo),
        "landing_target": args.landing,
        "stages": {
            "discovery": discovery,
            "decision": decision,
            "install": install,
            "first_run": first_run,
            "activation": activation,
            "return": ret,
            "share": share,
        },
        "stage_scores": stage_scores,
        "score_total": total,
        "score_max": 70,
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out)
        print(json.dumps({"ok": True, "score_total": total, "score_max": 70, "report": args.output}))
    else:
        print(out)


if __name__ == "__main__":
    main()
