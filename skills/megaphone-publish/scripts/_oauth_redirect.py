"""Tiny localhost OAuth2 redirect catcher.

Used by LinkedIn, Reddit, and X auth flows. Spins up an HTTP server on
localhost:8765, waits for the OAuth provider to redirect there with the
authorization code, returns the code, shuts down. The user never sees a
broken page — we serve a clean "you can close this tab" response."""

from __future__ import annotations

import http.server
import socketserver
import threading
import urllib.parse
import webbrowser
from typing import Optional

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 8765
REDIRECT_PATH = "/megaphone/oauth/callback"


def _make_handler(received: dict):
    """Build a request handler bound to a specific `received` dict so two
    concurrent capture calls can't corrupt each other."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - http.server API
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != REDIRECT_PATH:
                self.send_response(404)
                self.end_headers()
                return
            params = dict(urllib.parse.parse_qsl(parsed.query))
            received.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            body = """<!doctype html><html><head><title>Megaphone</title></head>
<body style="font-family:system-ui;max-width:480px;margin:80px auto;padding:0 24px;color:#222;">
<h2 style="margin:0 0 12px;">Connected.</h2>
<p style="color:#555;line-height:1.5;">You can close this tab and return to your terminal.</p>
</body></html>"""
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, *args, **kwargs):  # silence access logs
            pass

    return _Handler


def capture_oauth_code(
    authorize_url: str,
    timeout: int = 180,
    expected_state: Optional[str] = None,
) -> Optional[dict]:
    """Open the authorize_url in the user's browser, wait for the redirect,
    return the query params dict (typically {'code': ..., 'state': ...}).

    If `expected_state` is provided and the callback's `state` does not match,
    raise RuntimeError to prevent CSRF / cross-flow contamination.

    Returns None on timeout."""
    received: dict = {}
    handler_cls = _make_handler(received)
    server = socketserver.TCPServer((REDIRECT_HOST, REDIRECT_PORT), handler_cls)
    server.timeout = 1
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        webbrowser.open(authorize_url)
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            if received:
                params = dict(received)
                if expected_state is not None and params.get("state") != expected_state:
                    raise RuntimeError(
                        "OAuth state mismatch — possible CSRF; aborting connect."
                    )
                return params
            time.sleep(0.25)
        return None
    finally:
        server.shutdown()
        server.server_close()


def redirect_uri() -> str:
    return f"http://{REDIRECT_HOST}:{REDIRECT_PORT}{REDIRECT_PATH}"
