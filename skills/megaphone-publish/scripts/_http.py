"""Minimal HTTP helpers using stdlib only.

Avoids the requests dependency so megaphone-publish runs anywhere Python 3 is
installed without `pip install` friction."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


class HttpError(Exception):
    def __init__(self, status: int, body: str, headers: dict):
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status
        self.body = body
        self.headers = headers


def _do_request(
    method: str,
    url: str,
    *,
    headers: Optional[dict] = None,
    data: Optional[bytes] = None,
    timeout: int = 30,
) -> tuple[int, str, dict]:
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        raise HttpError(e.code, body, dict(e.headers or {})) from e
    except urllib.error.URLError as e:
        raise HttpError(0, str(e), {}) from e


def post_json(url: str, payload: dict, headers: Optional[dict] = None) -> dict:
    h = {"Content-Type": "application/json", **(headers or {})}
    body = json.dumps(payload).encode("utf-8")
    status, text, _ = _do_request("POST", url, headers=h, data=body)
    if status >= 400:
        raise HttpError(status, text, {})
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}


def post_form(url: str, form: dict, headers: Optional[dict] = None) -> dict:
    h = {"Content-Type": "application/x-www-form-urlencoded", **(headers or {})}
    body = urllib.parse.urlencode(form).encode("utf-8")
    status, text, _ = _do_request("POST", url, headers=h, data=body)
    if status >= 400:
        raise HttpError(status, text, {})
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}


def get_json(url: str, headers: Optional[dict] = None) -> dict:
    status, text, _ = _do_request("GET", url, headers=headers)
    if status >= 400:
        raise HttpError(status, text, {})
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}
