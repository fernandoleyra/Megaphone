#!/usr/bin/env python3
"""Megaphone auth helper.

Subcommands:
  status [platform]        Print which platforms have credentials saved.
  connect <platform>       Run the platform's interactive auth flow.
  disconnect <platform>    Delete the saved credentials.

Examples (preferred — short wrapper installed by `megaphone-init` §6.0):
  megaphone-auth status
  megaphone-auth status bluesky
  megaphone-auth connect bluesky
  megaphone-auth disconnect linkedin

Examples (long form — works without the wrapper):
  python3 auth.py status
  python3 auth.py connect bluesky

Credentials live at ~/.megaphone/credentials/<platform>.json (chmod 0600)."""

from __future__ import annotations

import argparse
import importlib
import os
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _common import (  # noqa: E402
    delete_credentials,
    emit,
    fail,
    info,
    load_credentials,
    save_credentials,
)

SUPPORTED = ["bluesky", "devto", "linkedin", "reddit", "mastodon", "x", "hashnode"]


def _platform_status(platform: str) -> dict:
    """Per-platform status row. Output is JSON-friendly."""
    import datetime as _dt
    import time as _time

    from _common import cred_path

    p = cred_path(platform)
    creds = load_credentials(platform)
    if creds is None:
        return {
            "platform": platform,
            "connected": False,
            "since": None,
            "expired": False,
        }
    # `since` = mtime of the credential file (when the user last connected).
    try:
        mtime = p.stat().st_mtime
        since = _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc).isoformat()
    except OSError:
        since = None
    # `expired` = creds carry an expires_at in the past (numeric epoch seconds).
    expired = False
    exp = creds.get("expires_at") if isinstance(creds, dict) else None
    if isinstance(exp, (int, float)) and exp > 0 and exp < _time.time():
        expired = True
    return {
        "platform": platform,
        "connected": True,
        "since": since,
        "expired": expired,
    }


def cmd_status(args: argparse.Namespace) -> None:
    if args.platform:
        emit(_platform_status(args.platform))
        return
    emit({"platforms": [_platform_status(p) for p in SUPPORTED]})


def cmd_connect(args: argparse.Namespace) -> None:
    platform = args.platform
    if platform not in SUPPORTED:
        fail(f"Unknown platform '{platform}'. Supported: {', '.join(SUPPORTED)}")
    try:
        module = importlib.import_module(f"connectors.{platform}")
    except ImportError as e:
        fail(f"Could not load connector for {platform}: {e}")

    info(f"Connecting {platform}…")
    from connectors._base import stdin_prompt

    try:
        creds = module.connect(stdin_prompt)
    except Exception as e:
        # Show traceback to stderr so the user can self-diagnose, then exit
        # cleanly without saving partial credentials.
        traceback.print_exc()
        fail(f"Connection cancelled: {e}")
        return

    if not isinstance(creds, dict) or not creds:
        fail(f"{platform}.connect() returned no credentials.")
    save_credentials(platform, creds)
    emit({"platform": platform, "connected": True, "credential_path": str(load_credentials_path(platform))})


def load_credentials_path(platform: str) -> str:
    from _common import cred_path

    return cred_path(platform)


def cmd_disconnect(args: argparse.Namespace) -> None:
    if args.platform not in SUPPORTED:
        fail(f"Unknown platform '{args.platform}'.")
    deleted = delete_credentials(args.platform)
    emit({"platform": args.platform, "deleted": deleted})


def main() -> None:
    p = argparse.ArgumentParser(description="Megaphone auth helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("platform", nargs="?")
    s.set_defaults(func=cmd_status)

    c = sub.add_parser("connect")
    c.add_argument("platform")
    c.set_defaults(func=cmd_connect)

    d = sub.add_parser("disconnect")
    d.add_argument("platform")
    d.set_defaults(func=cmd_disconnect)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
