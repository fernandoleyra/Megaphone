"""Bluesky / atproto connector.

Auth: app password (Settings → App Passwords on bsky.app).
Posting: com.atproto.repo.createRecord with collection app.bsky.feed.post.

Credential schema: { "handle": "user.bsky.social", "app_password": "xxxx" }

Sessions are short-lived; we create a fresh session per publish call, which
sidesteps token-refresh complexity. The cost is one extra HTTP call per post,
which is negligible."""

from __future__ import annotations

import datetime as _dt
from typing import Optional

from connectors._base import PostResult
from _http import HttpError, post_json

PDS = "https://bsky.social"


def _create_session(handle: str, app_password: str) -> dict:
    return post_json(
        f"{PDS}/xrpc/com.atproto.server.createSession",
        {"identifier": handle, "password": app_password},
    )


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    handle = credentials.get("handle")
    app_password = credentials.get("app_password")
    if not handle or not app_password:
        return PostResult(
            ok=False,
            error_type="auth_error",
            error_message="Missing handle or app_password in credentials.",
        )

    body = body[:300]  # Bluesky enforces 300 chars; truncate defensively.

    try:
        session = _create_session(handle, app_password)
    except HttpError as e:
        return PostResult(
            ok=False,
            error_type="auth_error",
            error_message=f"Could not start a Bluesky session: {e.body[:200]}",
        )

    access_jwt = session["accessJwt"]
    did = session["did"]

    record = {
        "$type": "app.bsky.feed.post",
        "text": body,
        "createdAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record,
    }

    try:
        resp = post_json(
            f"{PDS}/xrpc/com.atproto.repo.createRecord",
            payload,
            headers={"Authorization": f"Bearer {access_jwt}"},
        )
    except HttpError as e:
        et = "bad_body" if e.status == 400 else "unknown"
        return PostResult(ok=False, error_type=et, error_message=e.body[:300])

    # uri looks like at://<did>/app.bsky.feed.post/<rkey>
    uri = resp.get("uri", "")
    rkey = uri.split("/")[-1] if uri else ""
    url = f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else None
    return PostResult(ok=True, url=url, raw=resp)


def connect(prompt) -> dict:
    print()
    print("Bluesky setup")
    print("-------------")
    print("1. Open https://bsky.app/settings/app-passwords")
    print("2. Create a new app password (give it any name).")
    print("3. Paste the values below.\n")
    handle = prompt("Bluesky handle (e.g. fernando.bsky.social): ")
    if handle.startswith("@"):
        handle = handle[1:]
    app_password = prompt("App password: ", secret=True)
    # Validate by hitting createSession.
    try:
        _create_session(handle, app_password)
    except HttpError as e:
        raise RuntimeError(f"Bluesky rejected those credentials: {e.body[:200]}") from e
    return {"handle": handle, "app_password": app_password}
