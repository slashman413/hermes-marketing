"""Tiny shared helper: post a message to the DISCORD_WEBHOOK if set.

Used by linkedin.py / reddit_post.py / bluesky.py to alert the operator when a
live (not dry-run) post attempt FAILS — most commonly because a token expired.
Without this, per-channel failures would be silent (continue-on-error swallows
them from the workflow's own failure hook)."""
import os, json, urllib.request


def notify(msg: str) -> None:
    url = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not url:
        return
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({"content": msg[:1900]}).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "User-Agent": "Mozilla/5.0 (compatible; hermes-marketing)"},
        )
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        # Never let notification failure break the caller.
        pass
