#!/usr/bin/env python3
"""Megaphone auth helper.

Subcommands:
  status [platform]        Print which platforms have credentials saved.
  connect <platform>       Run the platform's interactive auth flow.
  disconnect <platform>    Delete the saved credentials.

Examples:
  python3 auth.py status
  python3 auth.py status bluesky
  python3 auth.py connect bluesky
  python3 auth.py disconnect linkedin

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
    cred_path,
    delete_credentials,
    emit,
    fail,
    info,
    load_credentials,
    save_credentials,
)

SUPPORTED = ("bluesky", "devto", "linkedin", "reddit", "mastodon", "x", "hashnode")


def cmd_status(args: argparse.Namespace) -> None:
    if args.platform:
        creds = load_credentials(args.platform)
        emit({"platform": args.platform, "connected": creds is not None})
        return
    out = []
    for p in SUPPORTED:
        out.append({"platform": p, "connected": load_credentials(p) is not None})
    emit({"platforms": out})


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
    emit({"platform": platform, "connected": True, "credential_path": str(cred_path(platform))})


def cmd_disconnect(args: argparse.Namespace) -> None:
    if args.platform not in SUPPORTED:
        fail(f"Unknown platform '{args.platform}'.")
    deleted = delete_credentials(args.platform)
    emit({"platform": args.platform, "deleted": deleted})


def main() -> None:
    p = argparse.ArgumentParser(description="Megaphone auth helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("platform", nargs="?", choices=SUPPORTED)
    s.set_defaults(func=cmd_status)

    c = sub.add_parser("connect")
    c.add_argument("platform", choices=SUPPORTED)
    c.set_defaults(func=cmd_connect)

    d = sub.add_parser("disconnect")
    d.add_argument("platform", choices=SUPPORTED)
    d.set_defaults(func=cmd_disconnect)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
