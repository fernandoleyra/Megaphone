"""LinkedIn connector.

Auth: OAuth2 authorization-code flow. User registers an app at
https://www.linkedin.com/developers/, requests `w_member_social` scope, and
provides client_id + client_secret. We complete the redirect at
http://localhost:8765/megaphone/oauth/callback (must be added to the app's
allowed redirect URLs).

Posting: POST https://api.linkedin.com/v2/ugcPosts.

Credential schema:
{
  "client_id": "...",
  "client_secret": "...",
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1735689600,
  "person_urn": "urn:li:person:abc123"
}"""

from __future__ import annotations

import time
import urllib.parse
from typing import Optional

from connectors._base import PostResult
from _http import HttpError, get_json, post_form, post_json
from _oauth_redirect import capture_oauth_code, redirect_uri

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
ME_URL = "https://api.linkedin.com/v2/userinfo"
POST_URL = "https://api.linkedin.com/v2/ugcPosts"
SCOPE = "w_member_social openid profile"


def _api_post(creds: dict, body: str, overrides: dict) -> PostResult:
    person = creds.get("person_urn")
    if not person:
        return PostResult(ok=False, error_type="auth_error", error_message="Missing person_urn.")

    visibility = overrides.get("visibility", "PUBLIC")  # or "CONNECTIONS"

    payload = {
        "author": person,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": body[:3000]},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }
    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    try:
        resp = post_json(POST_URL, payload, headers=headers)
    except HttpError as e:
        if e.status == 401:
            return PostResult(ok=False, error_type="refresh_token", error_message=e.body[:300])
        if e.status == 422 or e.status == 400:
            return PostResult(ok=False, error_type="bad_body", error_message=e.body[:300])
        if e.status == 429:
            return PostResult(ok=False, error_type="rate_limit", error_message="Rate limited.", retry_after=300)
        return PostResult(ok=False, error_type="unknown", error_message=e.body[:300])

    post_id = resp.get("id") or resp.get("_raw")
    url = None
    if isinstance(post_id, str) and post_id.startswith("urn:li:share:"):
        share_id = post_id.split(":")[-1]
        url = f"https://www.linkedin.com/feed/update/urn:li:share:{share_id}/"
    return PostResult(ok=True, url=url, raw=resp)


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    creds = dict(credentials)
    overrides = overrides or {}
    if not creds.get("access_token"):
        return PostResult(ok=False, error_type="auth_error", error_message="Not connected.")
    # Cheap freshness check; LinkedIn tokens last 60 days.
    if creds.get("expires_at") and time.time() > creds["expires_at"] - 60:
        new = refresh(creds)
        if not new:
            return PostResult(ok=False, error_type="refresh_token", error_message="Token expired.")
        creds = new
    return _api_post(creds, body, overrides)


def refresh(credentials: dict) -> Optional[dict]:
    rt = credentials.get("refresh_token")
    if not rt or not credentials.get("client_id") or not credentials.get("client_secret"):
        return None
    try:
        resp = post_form(
            TOKEN_URL,
            {
                "grant_type": "refresh_token",
                "refresh_token": rt,
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
            },
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
    print("LinkedIn setup")
    print("--------------")
    print("1. Open https://www.linkedin.com/developers/apps and click 'Create app'.")
    print("2. Fill in the basics; you do not need a verified company page for personal posting.")
    print("3. Under 'Auth' → 'OAuth 2.0 settings', add redirect URL:")
    print(f"     {redirect_uri()}")
    print("4. Under 'Products' → enable 'Sign In with LinkedIn using OpenID Connect' and")
    print("   'Share on LinkedIn'.")
    print("5. From 'Auth' → copy 'Client ID' and 'Primary Client Secret'. Paste below.\n")
    client_id = prompt("Client ID: ")
    client_secret = prompt("Client Secret: ", secret=True)
    if not client_id or not client_secret:
        raise RuntimeError("client_id and client_secret are required.")

    state = "megaphone"
    auth_qs = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri(),
            "scope": SCOPE,
            "state": state,
        }
    )
    print()
    print("Opening LinkedIn authorize page in your browser…")
    params = capture_oauth_code(f"{AUTH_URL}?{auth_qs}")
    if not params or "code" not in params:
        raise RuntimeError("Did not receive an OAuth code from LinkedIn.")

    token_resp = post_form(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": redirect_uri(),
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if "access_token" not in token_resp:
        raise RuntimeError(f"LinkedIn token exchange failed: {token_resp}")

    me = get_json(
        ME_URL,
        headers={"Authorization": f"Bearer {token_resp['access_token']}"},
    )
    sub = me.get("sub")
    person_urn = f"urn:li:person:{sub}" if sub else None
    if not person_urn:
        raise RuntimeError("Could not derive your LinkedIn person URN from /userinfo.")

    return _merge_token(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "person_urn": person_urn,
        },
        token_resp,
    )
