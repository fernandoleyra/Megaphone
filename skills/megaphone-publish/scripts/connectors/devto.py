"""dev.to connector.

Auth: API key (Settings → Account → API Keys).
Posting: POST https://dev.to/api/articles with { article: { title, body_markdown, tags, published } }.

Credential schema: { "api_key": "xxx" }

The draft frontmatter can carry: title, tags, series, canonical_url, published.
If `title` is missing, we extract the first H1 from the body."""

from __future__ import annotations

import re
from typing import Optional

from connectors._base import PostResult
from _common import load_draft_with_meta
from _http import HttpError, post_json

API = "https://dev.to/api/articles"


def _extract_title(body: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return m.group(1) if m else "Untitled"


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    api_key = credentials.get("api_key")
    if not api_key:
        return PostResult(ok=False, error_type="auth_error", error_message="Missing api_key.")

    overrides = overrides or {}

    # The body passed in is already cleaned by the dispatcher, but dev.to wants
    # frontmatter for title/tags. The dispatcher stripped frontmatter into a
    # separate dict via load_draft_with_meta; the publish path receives the
    # raw body here. To support frontmatter we re-parse if a __meta sentinel
    # was attached:
    meta = overrides.copy()

    title = meta.get("title") or _extract_title(body)
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    article = {
        "title": title[:128],
        "body_markdown": body,
        "published": meta.get("published", True),
        "tags": tags[:4],
    }
    if "series" in meta:
        article["series"] = meta["series"]
    if "canonical_url" in meta:
        article["canonical_url"] = meta["canonical_url"]

    try:
        resp = post_json(
            API,
            {"article": article},
            headers={"api-key": api_key, "Accept": "application/vnd.forem.api-v1+json"},
        )
    except HttpError as e:
        if e.status in (401, 403):
            return PostResult(ok=False, error_type="auth_error", error_message=e.body[:300])
        if e.status == 422:
            return PostResult(ok=False, error_type="bad_body", error_message=e.body[:300])
        if e.status == 429:
            return PostResult(ok=False, error_type="rate_limit", error_message="Rate limited.", retry_after=60)
        return PostResult(ok=False, error_type="unknown", error_message=e.body[:300])

    return PostResult(ok=True, url=resp.get("url"), raw=resp)


def connect(prompt) -> dict:
    print()
    print("dev.to setup")
    print("------------")
    print("1. Go to https://dev.to/settings/extensions")
    print("2. Scroll to 'DEV Community API Keys' and create a new key.")
    print("3. Paste it below.\n")
    api_key = prompt("dev.to API key: ", secret=True)
    if not api_key:
        raise RuntimeError("API key is required.")
    return {"api_key": api_key}
