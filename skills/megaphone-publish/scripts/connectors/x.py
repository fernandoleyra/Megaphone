"""X (Twitter) connector.

Auth: OAuth2 user-context with PKCE. User registers an app at
https://developer.x.com, sets the redirect URL to our localhost catcher.
Scopes: tweet.read tweet.write users.read offline.access.

NOTE: as of February 2026, posting via the X API is paid (~$0.01 per post
created) under X's pay-per-use pricing. Bot-like accounts must self-disclose
in their bio. Megaphone-publish surfaces this cost up-front; the user is
billed by X, not by us.

Posting: POST https://api.twitter.com/2/tweets

Credential schema:
{ "client_id": "...", "client_secret": "...", "access_token": "...",
  "refresh_token": "...", "expires_at": ..., "code_verifier_seen": true,
  "username": "..." }"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
import urllib.parse
from typing import Optional

from connectors._base import PostResult
from _http import HttpError, post_form, post_json
from _oauth_redirect import capture_oauth_code, redirect_uri

AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
TWEET_URL = "https://api.twitter.com/2/tweets"
SCOPE = "tweet.read tweet.write users.read offline.access"


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(os.urandom(40)).decode().rstrip("=")
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    )
    return verifier, challenge


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

    # Thread support: if overrides.mode == 'thread', split body on lines starting with '---' or numbered tweets
    mode = overrides.get("mode", "single")
    parts = _split_thread(body) if mode == "thread" else [body[:280]]

    last_id = None
    first_url = None
    for i, part in enumerate(parts):
        payload = {"text": part[:280]}
        if last_id:
            payload["reply"] = {"in_reply_to_tweet_id": last_id}
        try:
            resp = post_json(
                TWEET_URL,
                payload,
                headers={
                    "Authorization": f"Bearer {creds['access_token']}",
                    "Content-Type": "application/json",
                },
            )
        except HttpError as e:
            if e.status == 401:
                return PostResult(ok=False, error_type="refresh_token", error_message=e.body[:300])
            if e.status == 429:
                return PostResult(ok=False, error_type="rate_limit", error_message="Rate limited.", retry_after=900)
            if e.status in (400, 403):
                return PostResult(ok=False, error_type="bad_body", error_message=e.body[:300])
            return PostResult(ok=False, error_type="unknown", error_message=e.body[:300])

        data = resp.get("data", {})
        tid = data.get("id")
        if not tid:
            return PostResult(ok=False, error_type="unknown", error_message=str(resp)[:300])
        if first_url is None:
            handle = creds.get("username", "i")
            first_url = f"https://twitter.com/{handle}/status/{tid}"
        last_id = tid

    return PostResult(ok=True, url=first_url)


def _split_thread(body: str) -> list[str]:
    parts: list[str] = []
    chunk: list[str] = []
    for line in body.splitlines():
        if line.strip() == "---":
            if chunk:
                parts.append("\n".join(chunk).strip())
                chunk = []
            continue
        chunk.append(line)
    if chunk:
        parts.append("\n".join(chunk).strip())
    if len(parts) == 1 and len(parts[0]) > 280:
        # Auto-chunk by sentence if no '---' was present.
        text = parts[0]
        out, current = [], ""
        for sentence in text.replace("\n", " ").split(". "):
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 2 > 270:
                out.append(current.strip())
                current = sentence + ". "
            else:
                current += sentence + ". "
        if current.strip():
            out.append(current.strip())
        return out
    return parts


def refresh(credentials: dict) -> Optional[dict]:
    rt = credentials.get("refresh_token")
    cid = credentials.get("client_id")
    secret = credentials.get("client_secret")
    if not (rt and cid):
        return None
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if secret:
        auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"
    try:
        resp = post_form(
            TOKEN_URL,
            {
                "grant_type": "refresh_token",
                "refresh_token": rt,
                "client_id": cid,
            },
            headers=headers,
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
    print("X (Twitter) setup")
    print("-----------------")
    print("Heads up: posting via the X API costs ~$0.01 per post created since")
    print("Feb 2026, and bot-like accounts must self-disclose in the bio. The")
    print("billing relationship is between you and X; megaphone does not bill")
    print("you for posts.\n")
    print("1. Open https://developer.x.com and create a project + app.")
    print("2. Under 'User authentication settings', enable OAuth 2.0:")
    print("     - Type: Web App, Native App")
    print(f"     - Callback URI: {redirect_uri()}")
    print("     - Website URL: any (e.g. https://example.com)")
    print("3. Generate a Client ID and a Client Secret (use 'Confidential client').")
    print("4. Paste below.\n")
    client_id = prompt("X client_id: ")
    client_secret = prompt("X client_secret (or blank for public client): ", secret=True)
    if not client_id:
        raise RuntimeError("client_id is required.")

    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(8)
    auth_qs = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri(),
            "scope": SCOPE,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    print()
    print("Opening X authorize page in your browser…")
    params = capture_oauth_code(f"{AUTH_URL}?{auth_qs}")
    if not params or "code" not in params:
        raise RuntimeError("Did not receive an OAuth code from X.")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if client_secret:
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"
    token_resp = post_form(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": redirect_uri(),
            "client_id": client_id,
            "code_verifier": verifier,
        },
        headers=headers,
    )
    if "access_token" not in token_resp:
        raise RuntimeError(f"X token exchange failed: {token_resp}")

    handle = prompt("Your X handle without @ (used to format result URLs): ")

    return _merge_token(
        {
            "client_id": client_id,
            "client_secret": client_secret or "",
            "username": handle,
        },
        token_resp,
    )
