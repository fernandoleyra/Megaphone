#!/usr/bin/env python3
"""Megaphone landing-page static audit.

Pulls a target (URL or local HTML file), parses the markup, and emits a
JSON report scored against the rubric in SKILL.md. The skill (Claude) then
adds qualitative review on top.

Stdlib only. Uses html.parser to avoid an external dependency."""

from __future__ import annotations

import argparse
import datetime as _dt
import html.parser
import json
import os
import re
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# HTML extraction
# ---------------------------------------------------------------------------

@dataclass
class Findings:
    title: Optional[str] = None
    description: Optional[str] = None
    canonical: Optional[str] = None
    robots: Optional[str] = None
    viewport: Optional[str] = None
    og: dict = field(default_factory=dict)
    twitter: dict = field(default_factory=dict)
    h1s: list = field(default_factory=list)
    h2_count: int = 0
    h3_count: int = 0
    heading_order_violations: int = 0
    first_cta: Optional[dict] = None
    ctas_above_fold: int = 0
    ctas_total: int = 0
    forms: list = field(default_factory=list)
    images: dict = field(default_factory=lambda: {"total": 0, "missing_alt": 0})
    scripts: dict = field(default_factory=lambda: {"total": 0, "blocking": 0, "inline": 0})
    page_bytes: int = 0
    body_excerpt: str = ""
    is_https: Optional[bool] = None
    fetch_error: Optional[str] = None


_HYPE_PATTERNS = [
    r"\brevolutionar(y|ize)\b",
    r"\bnext[- ]gen(eration)?\b",
    r"\b10x\b",
    r"\bworld'?s first\b",
    r"\bcutting[- ]edge\b",
    r"\bseamless\b",
    r"\bgame[- ]changer\b",
    r"\bI'?m (excited|thrilled) to announce\b",
    r"— the future of\b",
    r"\bunlock the power\b",
    r"\bempower(ing)? (your|our|the)\b",
]

_TRUST_PATTERNS = [
    (r"\d{1,3}(,\d{3})+ users?\b", "user_count"),
    (r"\d{1,3}(,\d{3})*\+ users?\b", "user_count"),
    (r"trusted by\b", "trust_phrase"),
    (r"github\.com/.*?stargazers?\b", "github_stars_link"),
    (r"<img[^>]+shields\.io[^>]+>", "shields_badge"),
    (r"open[- ]source\b", "open_source_label"),
    (r"MIT licen[sc]e\b", "license_label"),
    (r"<blockquote", "testimonial_blockquote"),
    (r"\d+ stars?\b", "star_count_phrase"),
]


class Extractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.f = Findings()
        self._stack: list[str] = []
        self._in_title = False
        self._title_buf: list[str] = []
        self._capture_text: list[str] = []
        self._heading_order: list[str] = []
        self._cta_candidates: list[tuple[int, str, str, dict]] = []  # (offset, tag, text, attrs)
        self._current_form_fields = 0
        self._in_form = False

    # --- structural events ---

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        offset = self.getpos()[0] * 200  # rough pseudo-byte position by line
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            self._handle_meta(a)
        elif tag == "link" and a.get("rel") in ("canonical", "['canonical']"):
            self.f.canonical = a.get("href")
        elif tag == "html":
            pass
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading_order.append(tag)
            self._capture_text = []
            self._stack.append(tag)
        elif tag == "form":
            self._in_form = True
            self._current_form_fields = 0
        elif tag in ("input", "textarea", "select") and self._in_form:
            t = (a.get("type") or "").lower()
            if t not in ("hidden", "submit", "button", "reset"):
                self._current_form_fields += 1
        elif tag in ("a", "button"):
            self._capture_text = []
            self._stack.append((tag, a, offset))
        elif tag == "img":
            self.f.images["total"] += 1
            if not (a.get("alt") and a["alt"].strip()):
                self.f.images["missing_alt"] += 1
        elif tag == "script":
            self.f.scripts["total"] += 1
            if a.get("src"):
                if not (a.get("async") is not None or a.get("defer") is not None):
                    self.f.scripts["blocking"] += 1
            else:
                self.f.scripts["inline"] += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.f.title = "".join(self._title_buf).strip() or None
        elif tag in ("h1", "h2", "h3"):
            text = "".join(self._capture_text).strip()
            if tag == "h1":
                self.f.h1s.append(text)
            elif tag == "h2":
                self.f.h2_count += 1
            elif tag == "h3":
                self.f.h3_count += 1
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
        elif tag == "form":
            self.f.forms.append({"fields": self._current_form_fields})
            self._in_form = False
            self._current_form_fields = 0
        elif tag in ("a", "button"):
            if self._stack and isinstance(self._stack[-1], tuple) and self._stack[-1][0] == tag:
                _, attrs, offset = self._stack.pop()
                text = "".join(self._capture_text).strip()
                if not text:
                    return
                cls = (attrs.get("class") or "").lower()
                role = (attrs.get("role") or "").lower()
                href = attrs.get("href") or ""
                is_cta = (
                    tag == "button"
                    or "btn" in cls
                    or "cta" in cls
                    or "button" in cls
                    or role == "button"
                    or any(href.startswith(p) for p in ("/signup", "/sign-up", "/start", "/get-started", "/install"))
                )
                if is_cta:
                    self._cta_candidates.append((offset, tag, text, attrs))

    def handle_data(self, data):
        if self._in_title:
            self._title_buf.append(data)
        if self._capture_text is not None:
            self._capture_text.append(data)

    # --- helpers ---

    def _handle_meta(self, a: dict):
        name = (a.get("name") or "").lower()
        prop = (a.get("property") or "").lower()
        content = a.get("content") or ""
        if name == "description":
            self.f.description = content
        elif name == "viewport":
            self.f.viewport = content
        elif name == "robots":
            self.f.robots = content
        elif prop.startswith("og:"):
            self.f.og[prop[3:]] = content
        elif name.startswith("twitter:"):
            self.f.twitter[name[8:]] = content


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_target(target: str) -> tuple[str, dict]:
    """Return (html, meta) where meta has page_bytes, is_https, fetch_error."""
    if target.startswith("http://") or target.startswith("https://"):
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "megaphone-audit/0.6"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read()
            return body.decode("utf-8", errors="replace"), {
                "page_bytes": len(body),
                "is_https": target.startswith("https://"),
                "fetch_error": None,
            }
        except urllib.error.HTTPError as e:
            return "", {"page_bytes": 0, "is_https": target.startswith("https://"), "fetch_error": f"HTTP {e.code}"}
        except urllib.error.URLError as e:
            return "", {"page_bytes": 0, "is_https": target.startswith("https://"), "fetch_error": str(e)}
    # Local file
    p = Path(target)
    if p.is_dir():
        p = p / "index.html"
    if not p.exists():
        return "", {"page_bytes": 0, "is_https": None, "fetch_error": f"file not found: {p}"}
    body = p.read_bytes()
    return body.decode("utf-8", errors="replace"), {
        "page_bytes": len(body),
        "is_https": None,
        "fetch_error": None,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

CHECKS = [
    ("title_present_length",     "Title 30–60 chars",                    5),
    ("description_present",      "Meta description 50–160 chars",         5),
    ("og_complete",              "OG title + description + image",       10),
    ("twitter_card",             "Twitter card present",                  5),
    ("viewport",                 "Viewport meta present",                 5),
    ("h1_single_concise",        "Single H1 with ≤10 words",              8),
    ("heading_hierarchy",        "Heading hierarchy clean",               4),
    ("cta_above_fold",           "Above-the-fold CTA detected",          10),
    ("cta_verb_noun",            "CTA reads action-verb + noun",          6),
    ("trust_signals",            "At least one trust signal",             6),
    ("low_form_friction",        "≤2 forms, ≤4 fields each",              6),
    ("alt_coverage",             "≥90% images have alt text",             5),
    ("no_hype_words",            "No marketing-hype red-flag words",      5),
    ("voice_consistency",        "Voice match — profile.json check",      5),  # qualitative; default partial
    ("page_weight",              "Page weight <500 KB",                   5),
    ("https_canonical_robots",   "HTTPS + canonical + robots ok",         5),
    ("scripts_low_blocking",     "No render-blocking external scripts",   3),
    ("empty_state_framing",      "Honest pre-launch framing if applicable", 7),
]


def score(findings: Findings, html_text: str, meta: dict) -> dict:
    results = {}

    def title_check():
        t = findings.title or ""
        return 30 <= len(t) <= 60

    def desc_check():
        d = findings.description or ""
        return 50 <= len(d) <= 160

    def og_check():
        return all(k in findings.og and findings.og[k].strip() for k in ("title", "description", "image"))

    def twitter_check():
        return bool(findings.twitter.get("card"))

    def viewport_check():
        v = (findings.viewport or "").lower()
        return "width=device-width" in v

    def h1_check():
        if len(findings.h1s) != 1:
            return False
        words = len(findings.h1s[0].split())
        return 1 <= words <= 10

    def hierarchy_check():
        return findings.heading_order_violations == 0  # filled below before scoring

    def cta_above_fold_check():
        return findings.ctas_above_fold > 0

    def cta_verb_noun_check():
        if not findings.first_cta:
            return False
        text = findings.first_cta["text"].lower()
        verbs = (
            "get", "start", "try", "install", "download", "join", "sign", "create",
            "build", "ship", "launch", "request", "claim", "subscribe", "see", "view", "explore",
        )
        words = re.findall(r"[a-z]+", text)
        return bool(words) and words[0] in verbs and len(words) <= 4

    def trust_check():
        for pattern, _label in _TRUST_PATTERNS:
            if re.search(pattern, html_text, re.IGNORECASE):
                return True
        return False

    def form_friction_check():
        if not findings.forms:
            return True
        if len(findings.forms) > 2:
            return False
        return all(f["fields"] <= 4 for f in findings.forms)

    def alt_check():
        n = findings.images["total"]
        if n == 0:
            return True
        return (n - findings.images["missing_alt"]) / n >= 0.9

    def no_hype_check():
        for p in _HYPE_PATTERNS:
            if re.search(p, html_text, re.IGNORECASE):
                return False
        return True

    def voice_check():
        return None  # qualitative — leave to the skill

    def weight_check():
        return meta.get("page_bytes", 0) < 500 * 1024

    def https_check():
        is_https = meta.get("is_https")
        if is_https is False:
            return False
        return bool(findings.canonical)

    def scripts_check():
        return findings.scripts.get("blocking", 0) == 0

    def empty_state_check():
        return None  # qualitative

    handlers = {
        "title_present_length": title_check,
        "description_present": desc_check,
        "og_complete": og_check,
        "twitter_card": twitter_check,
        "viewport": viewport_check,
        "h1_single_concise": h1_check,
        "heading_hierarchy": hierarchy_check,
        "cta_above_fold": cta_above_fold_check,
        "cta_verb_noun": cta_verb_noun_check,
        "trust_signals": trust_check,
        "low_form_friction": form_friction_check,
        "alt_coverage": alt_check,
        "no_hype_words": no_hype_check,
        "voice_consistency": voice_check,
        "page_weight": weight_check,
        "https_canonical_robots": https_check,
        "scripts_low_blocking": scripts_check,
        "empty_state_framing": empty_state_check,
    }

    earned = 0
    deferred = 0
    for key, label, weight in CHECKS:
        passed = handlers[key]()
        if passed is None:
            results[key] = {"label": label, "weight": weight, "passed": None, "value": None, "deferred_to_skill": True}
            deferred += weight
        else:
            results[key] = {"label": label, "weight": weight, "passed": bool(passed)}
            if passed:
                earned += weight
    total_assigned = sum(w for _, _, w in CHECKS) - deferred
    static_score = round((earned / total_assigned) * (100 - deferred)) if total_assigned else 0
    return {"score_static": static_score, "deferred_points": deferred, "checks": results, "earned": earned}


def find_heading_violations(html_text: str) -> int:
    """Count cases where a deeper heading appears before its proper parent."""
    headings = re.findall(r"<h([1-6])\b", html_text, re.IGNORECASE)
    violations = 0
    seen_levels: set[int] = set()
    for h in headings:
        lvl = int(h)
        if lvl > 1 and (lvl - 1) not in seen_levels:
            violations += 1
        seen_levels.add(lvl)
    return violations


def find_hype_hits(html_text: str) -> list[dict]:
    out = []
    for p in _HYPE_PATTERNS:
        for m in re.finditer(p, html_text, re.IGNORECASE):
            out.append({"pattern": p, "match": m.group(0), "context": _context(html_text, m.start(), 60)})
    return out[:20]


def find_trust_hits(html_text: str) -> list[dict]:
    out = []
    for p, label in _TRUST_PATTERNS:
        m = re.search(p, html_text, re.IGNORECASE)
        if m:
            out.append({"label": label, "match": m.group(0), "context": _context(html_text, m.start(), 60)})
    return out


def _context(text: str, start: int, span: int) -> str:
    a = max(0, start - span)
    b = min(len(text), start + span)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def body_excerpt(html_text: str) -> str:
    body = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.IGNORECASE | re.DOTALL)
    raw = body.group(1) if body else html_text
    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:8000]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, help="URL or path to HTML file/dir")
    p.add_argument("--output", help="Optional path to write the JSON report")
    p.add_argument("--profile", help="Path to .megaphone/profile.json for voice context")
    args = p.parse_args()

    html_text, meta = load_target(args.target)
    if meta.get("fetch_error"):
        print(json.dumps({"ok": False, "error": meta["fetch_error"]}, indent=2))
        sys.exit(2)

    extractor = Extractor()
    extractor.feed(html_text)
    f = extractor.f
    f.page_bytes = meta["page_bytes"]
    f.is_https = meta.get("is_https")
    f.fetch_error = meta.get("fetch_error")

    # First-CTA heuristic: pick whichever CTA candidate has the lowest offset.
    ctas = sorted(extractor._cta_candidates, key=lambda x: x[0])
    if ctas:
        offset, tag, text, attrs = ctas[0]
        f.first_cta = {"text": text, "tag": tag, "offset_hint": offset}
        # Above-the-fold proxy: line-position-based offset under ~1500 (rough)
        for offset, _, _, _ in ctas:
            if offset < 1500:
                f.ctas_above_fold += 1
        f.ctas_total = len(ctas)

    f.heading_order_violations = find_heading_violations(html_text)
    f.body_excerpt = body_excerpt(html_text)

    rubric = score(f, html_text, meta)
    profile = None
    if args.profile and Path(args.profile).exists():
        try:
            profile = json.loads(Path(args.profile).read_text())
        except json.JSONDecodeError:
            profile = None

    report = {
        "ok": True,
        "target": args.target,
        "audited_at": _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "page": {
            "title": f.title,
            "description": f.description,
            "canonical": f.canonical,
            "robots": f.robots,
            "viewport": f.viewport,
            "og": f.og,
            "twitter": f.twitter,
            "page_bytes": f.page_bytes,
            "is_https": f.is_https,
        },
        "headings": {"h1s": f.h1s, "h2_count": f.h2_count, "h3_count": f.h3_count, "violations": f.heading_order_violations},
        "ctas": {"first": f.first_cta, "above_fold": f.ctas_above_fold, "total": f.ctas_total},
        "forms": f.forms,
        "images": f.images,
        "scripts": f.scripts,
        "hype_hits": find_hype_hits(html_text),
        "trust_hits": find_trust_hits(html_text),
        "body_excerpt": f.body_excerpt,
        "profile_audience": (profile or {}).get("audience"),
        "profile_voice_samples": (profile or {}).get("voice", {}).get("samples"),
        "rubric": rubric,
    }

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out)
        print(json.dumps({"ok": True, "score_static": rubric["score_static"], "report": args.output}))
    else:
        print(out)


if __name__ == "__main__":
    main()
