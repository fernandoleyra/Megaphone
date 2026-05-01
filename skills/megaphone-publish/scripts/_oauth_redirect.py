"""Tiny localhost OAuth2 redirect catcher.

Used by LinkedIn, Reddit, and X auth flows. Spins up an HTTP server on
localhost:8765, waits for the OAuth provider to redirect there with the
authorization code, returns the code, shuts down. The user never sees a
broken page — we serve a clean "you can close this tab" response.

Security notes:
  * The server binds to the loopback interface only; it never listens on a
    routable address.
  * The caller MUST pass a cryptographically random `state` parameter; the
    handler refuses any redirect whose state doesn't match. This blocks the
    classic OAuth code-injection CSRF where an attacker tricks the user's
    browser into completing the flow with an attacker-controlled code.
  * Only the configured callback path is honored; everything else returns 404.
"""

from __future__ import annotations

import http.server
import secrets
import socketserver
import threading
import time
import urllib.parse
import webbrowser
from typing import Optional

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 8765
REDIRECT_PATH = "/megaphone/oauth/callback"


def new_state() -> str:
    """Return a fresh CSRF state token. Pass to capture_oauth_code and into the
    authorize URL's `state` query parameter."""
    return secrets.token_urlsafe(32)


def _make_handler(expected_state: str, received: dict):
    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - http.server API
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != REDIRECT_PATH:
                self.send_response(404)
                self.end_headers()
                return
            params = dict(urllib.parse.parse_qsl(parsed.query))
            # CSRF check: refuse anything whose state does not match what the
            # caller generated for this single auth flow.
            if not secrets.compare_digest(params.get("state", ""), expected_state):
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"State mismatch. Refusing this redirect.\n")
                return
            received.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<!doctype html><html><head><title>Megaphone</title></head>"
                b"<body style=\"font-family:system-ui;max-width:480px;margin:80px auto;"
                b"padding:0 24px;color:#222;\">"
                b"<h2 style=\"margin:0 0 12px;\">Connected.</h2>"
                b"<p style=\"color:#555;line-height:1.5;\">You can close this tab "
                b"and return to your terminal.</p></body></html>"
            )

        def log_message(self, *args, **kwargs):  # silence access logs
            pass

    return _Handler


def capture_oauth_code(authorize_url: str, expected_state: str, timeout: int = 180) -> Optional[dict]:
    """Open authorize_url in the browser, wait for the redirect, return params.

    Returns the redirect's query-param dict (typically {'code', 'state', ...}),
    or None on timeout. The handler will reject any redirect whose `state`
    parameter does not match `expected_state`.
    """
    received: dict = {}
    handler_cls = _make_handler(expected_state, received)

    class _ReusableServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = _ReusableServer((REDIRECT_HOST, REDIRECT_PORT), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        webbrowser.open(authorize_url)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if received:
                return dict(received)
            time.sleep(0.25)
        return None
    finally:
        server.shutdown()
        server.server_close()


def redirect_uri() -> str:
    return f"http://{REDIRECT_HOST}:{REDIRECT_PORT}{REDIRECT_PATH}"
