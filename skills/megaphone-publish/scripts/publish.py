#!/usr/bin/env python3
"""Megaphone publish dispatcher.

Reads a draft file, loads the matching connector, applies overrides,
publishes, writes the result to .megaphone/published/<date>.jsonl.

Usage:
  python3 publish.py --platform bluesky --file .megaphone/posts/2026-04-29/bluesky.md
  python3 publish.py --platform devto --file path/to/draft.md --dry-run
  python3 publish.py --platform x --file path/to/draft.md --no-retry"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _common import (  # noqa: E402
    PostResult,
    emit,
    fail,
    info,
    load_credentials,
    load_draft_with_meta,
    load_overrides,
    published_log_path,
    save_credentials,
)


def _load_connector(platform: str):
    try:
        return importlib.import_module(f"connectors.{platform}")
    except ImportError as e:
        fail(f"No connector for '{platform}': {e}")


def _today() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d")


def main() -> None:
    p = argparse.ArgumentParser(description="Publish a megaphone draft to a platform")
    p.add_argument("--platform", required=True, help="bluesky | linkedin | devto | reddit | mastodon | x | hashnode")
    p.add_argument("--file", required=True, help="Path to the draft .md file")
    p.add_argument("--dry-run", action="store_true", help="Build the payload but don't post")
    p.add_argument("--no-retry", action="store_true", help="Disable refresh-token + rate-limit retries")
    args = p.parse_args()

    if not os.path.exists(args.file):
        fail(f"Draft file not found: {args.file}")

    body, meta = load_draft_with_meta(args.file)

    creds = load_credentials(args.platform)
    if not creds:
        fail(
            f"No credentials for {args.platform}. Run: python3 auth.py connect {args.platform}",
        )

    try:
        overrides = load_overrides(args.platform)
    except ValueError as e:
        fail(str(e))

    # Frontmatter beats overrides for fields the post itself wants to declare
    # (title, tags). Overrides win on operational concerns (subreddit, visibility).
    merged_overrides = {**overrides, **{k: v for k, v in meta.items() if k not in overrides}}

    if args.dry_run:
        emit(
            {
                "platform": args.platform,
                "dry_run": True,
                "body_preview": body[:200],
                "body_length": len(body),
                "meta": meta,
                "overrides": overrides,
            }
        )
        return

    module = _load_connector(args.platform)
    result: PostResult = module.publish(body, creds, merged_overrides)

    # Auto-handle refresh-token once.
    if not result.ok and result.error_type == "refresh_token" and not args.no_retry:
        info(f"{args.platform}: token expired, attempting refresh…")
        refreshed = None
        if hasattr(module, "refresh"):
            refreshed = module.refresh(creds)
        if refreshed:
            save_credentials(args.platform, refreshed)
            result = module.publish(body, refreshed, merged_overrides)
        else:
            info(
                f"{args.platform}: refresh failed; reconnect with `python3 auth.py connect {args.platform}`",
            )

    # Auto-handle one rate-limit retry, capped at 90 seconds wait.
    if not result.ok and result.error_type == "rate_limit" and not args.no_retry:
        wait = min(result.retry_after or 60, 90)
        info(f"{args.platform}: rate-limited, waiting {wait}s and retrying…")
        time.sleep(wait)
        result = module.publish(body, load_credentials(args.platform) or creds, merged_overrides)

    log_entry = {
        "platform": args.platform,
        "file": args.file,
        "published_at": _dt.datetime.utcnow().isoformat() + "Z",
        **result.to_dict(),
    }
    log_path = published_log_path(_today())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    emit(log_entry)
    if not result.ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
