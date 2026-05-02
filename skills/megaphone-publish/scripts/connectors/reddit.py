"""Reddit connector.

Auth: OAuth2 authorization-code flow with installed-/web-app credentials. The
user creates an app at https://www.reddit.com/prefs/apps as type 'web app',
gives client_id + secret. Scopes: identity submit.

Posting: POST https://oauth.reddit.com/api/submit (text post in a chosen
subreddit). Title comes from frontmatter or the first line of the draft.

Credential schema:
{ "client_id": "...", "client_secret": "...", "access_token": "...",
  "refresh_token": "...", "expires_at": ..., "username": "..." }"""

from __future__ import annotations

import base64
import secrets
import time
import urllib.parse
from typing import Optional

from connectors._base import PostResult
from _http import HttpError, post_form
from _oauth_redirect import capture_oauth_code, redirect_uri

AUTH_URL = "https://www.reddit.com/api/v1/authorize"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
SUBMIT_URL = "https://oauth.reddit.com/api/submit"
ME_URL = "https://oauth.reddit.com/api/v1/me"
SCOPE = "identity submit"
USER_AGENT = "megaphone-publish/0.2 (by /u/megaphone)"


def _split_title_body(body: str, frontmatter_title: Optional[str]) -> tuple[str, str]:
    if frontmatter_title:
        return frontmatter_title, body
    # Pull the first non-empty line off as the title; body is the rest.
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.strip():
            return line.strip().lstrip("# ").strip(), "\n".join(lines[i + 1 :]).strip()
    return "Untitled", body


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    creds = dict(credentials)
    overrides = overrides or {}
    if not creds.get("access_token"):
        return PostResult(ok=False, error_type="auth_error", error_message="Not connected.")
    if creds.get("expires_at") and time.time() > creds["expires_at"] - 60:
        new = refresh(creds)
        if not new:
            return PostResult(ok=False, error_type="refresh_token", error_message="Token expired.")
        creds = new

    subreddit = overrides.get("subreddit")
    if not subreddit:
        return PostResult(
            ok=False,
            error_type="bad_body",
            error_message="Reddit posts require .megaphone/overrides/reddit.json with a 'subreddit' field.",
        )

    title, text = _split_title_body(body, overrides.get("title"))

    form = {
        "sr": subreddit,
        "kind": "self",
        "title": title[:300],
        "text": text,
        "api_type": "json",
        "resubmit": "true",
    }
    if overrides.get("flair_id"):
        form["flair_id"] = overrides["flair_id"]
    if overrides.get("nsfw"):
        form["nsfw"] = "true"

    try:
        resp = post_form(
            SUBMIT_URL,
            form,
            headers={
                "Authorization": f"Bearer {creds['access_token']}",
                "User-Agent": USER_AGENT,
            },
        )
    except HttpError as e:
        if e.status == 401:
            return PostResult(ok=False, error_type="refresh_token", error_message=e.body[:300])
        if e.status == 429:
            return PostResult(ok=False, error_type="rate_limit", error_message="Rate limited.", retry_after=60)
        return PostResult(ok=False, error_type="unknown", error_message=e.body[:300])

    data = resp.get("json", {}).get("data", {})
    errors = resp.get("json", {}).get("errors")
    if errors:
        return PostResult(ok=False, error_type="bad_body", error_message=str(errors))
    return PostResult(ok=True, url=data.get("url"), raw=resp)


def refresh(credentials: dict) -> Optional[dict]:
    rt = credentials.get("refresh_token")
    cid = credentials.get("client_id")
    secret = credentials.get("client_secret")
    if not (rt and cid and secret):
        return None
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    try:
        resp = post_form(
            TOKEN_URL,
            {"grant_type": "refresh_token", "refresh_token": rt},
            headers={"Authorization": f"Basic {auth}", "User-Agent": USER_AGENT},
        )
    except HttpError:
        return None
    return _merge_token(credentials, resp)


def _merge_token(creds: dict, token_resp: dict) -> dict:
    out = dict(creds)
    out["access_token"] = token_resp["access_token"]
    if "refresh_token" in token_resp:
        out["refresh_token"] = token_resp["refresh_token"]
    if "expires_in" in token_resp:
        out["expires_at"] = int(time.time()) + int(token_resp["expires_in"])
    return out


def connect(prompt) -> dict:
    print()
    print("Reddit setup")
    print("------------")
    print("1. Open https://www.reddit.com/prefs/apps and click 'are you a developer? create an app'.")
    print("2. Type: 'web app'. Name: anything. About URL: any. ")
    print(f"3. Redirect URI: {redirect_uri()}")
    print("4. Click create. Copy the client ID (under your app name) and the secret.")
    print("5. Paste below.\n")
    client_id = prompt("Reddit client_id: ")
    client_secret = prompt("Reddit client_secret: ", secret=True)
    if not client_id or not client_secret:
        raise RuntimeError("client_id and client_secret are required.")

    state = secrets.token_urlsafe(16)
    auth_qs = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": redirect_uri(),
            "duration": "permanent",
            "scope": SCOPE,
        }
    )
    print()
    print("Opening Reddit authorize page in your browser…")
    try:
        params = capture_oauth_code(f"{AUTH_URL}?{auth_qs}", expected_state=state)
    except RuntimeError as e:
        # OAuth state mismatch — possible CSRF.
        raise RuntimeError(f"Reddit auth aborted: {e}") from e
    if not params or "code" not in params:
        raise RuntimeError("Did not receive an OAuth code from Reddit.")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token_resp = post_form(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": redirect_uri(),
        },
        headers={"Authorization": f"Basic {auth}", "User-Agent": USER_AGENT},
    )
    if "access_token" not in token_resp:
        raise RuntimeError(f"Reddit token exchange failed: {token_resp}")

    return _merge_token(
        {"client_id": client_id, "client_secret": client_secret},
        token_resp,
    )
