"""Mastodon connector.

Auth: per-instance access token (Preferences → Development → New application,
scope: write:statuses).
Posting: POST https://<instance>/api/v1/statuses.

Credential schema: { "instance": "fosstodon.org", "access_token": "xxx" }"""

from __future__ import annotations

import re
from typing import Optional

from connectors._base import PostResult
from _http import HttpError, post_form

# RFC 1123-style hostname: at least two labels, alphanumerics + hyphens,
# 63-char per-label cap, no leading/trailing hyphens, no IPs, no paths.
_HOSTNAME_RE = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    instance = (credentials.get("instance") or "").rstrip("/")
    token = credentials.get("access_token")
    if not instance or not token:
        return PostResult(ok=False, error_type="auth_error", error_message="Missing instance or access_token.")

    overrides = overrides or {}
    visibility = overrides.get("visibility", "public")
    body = body[:500]  # Mastodon default cap; many instances allow more but 500 is safe.

    try:
        resp = post_form(
            f"https://{instance}/api/v1/statuses",
            {"status": body, "visibility": visibility},
            headers={"Authorization": f"Bearer {token}"},
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
    print("Mastodon setup")
    print("--------------")
    print("1. Sign in to your Mastodon instance (e.g. fosstodon.org).")
    print("2. Preferences → Development → New application.")
    print("3. Name it 'Megaphone', enable scope `write:statuses`, save.")
    print("4. Open the application, copy 'Your access token'.")
    print("5. Paste below.\n")
    instance = prompt("Instance hostname (e.g. fosstodon.org): ")
    if instance.startswith("https://"):
        instance = instance[len("https://"):]
    if instance.startswith("http://"):
        instance = instance[len("http://"):]
    instance = instance.rstrip("/")
    if not _HOSTNAME_RE.match(instance):
        # Block IP literals, paths, and other non-hostname inputs that would
        # let an attacker pivot the request to internal services (SSRF).
        raise ValueError(
            "Invalid Mastodon instance hostname. "
            "Expected a public DNS name like 'fosstodon.org'."
        )
    token = prompt("Access token: ", secret=True)
    if not instance or not token:
        raise RuntimeError("Instance and access token are both required.")
    return {"instance": instance, "access_token": token}
