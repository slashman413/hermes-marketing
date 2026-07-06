#!/usr/bin/env python3
"""
preview_all.py — dry-run every auto-poster and show exactly what would go out.

Runs locally with no credentials required. Shows for each channel:
  - Which curated post would be picked
  - Whether the channel would actually post now (cadence gate open?)
  - Any warnings (missing tokens, etc.)

Use before enabling any live posting, or any time you want to see the
current shape of the promo pipeline.

    python scripts/preview_all.py
"""
import importlib.util, sys, os
from pathlib import Path

HERE = Path(__file__).parent

# Force dry-run for every channel (remove any live creds from env).
for k in [
    "X_API_KEY","X_API_SECRET","X_ACCESS_TOKEN","X_ACCESS_TOKEN_SECRET",
    "LINKEDIN_ACCESS_TOKEN","LINKEDIN_ACTOR_URN",
    "REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USERNAME","REDDIT_PASSWORD",
    "BLUESKY_HANDLE","BLUESKY_APP_PASSWORD",
]:
    os.environ.pop(k, None)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hr(title: str):
    print()
    print("═" * 70)
    print(f" {title}")
    print("═" * 70)


def preview_x():
    hr("X / Twitter (marketing.py)")
    m = _load("mk", HERE / "marketing.py")
    log = m.load_rotation_log()
    remaining = m.MAX_TWEETS_PER_DAY - log.get("tweet_count", 0)
    print(f"cap:         {m.MAX_TWEETS_PER_DAY}/day  used_today: {log.get('tweet_count', 0)}  remaining: {max(0, remaining)}")
    if remaining <= 0:
        print("gate:        CLOSED (daily cap reached)")
        return
    for i in range(min(2, remaining)):
        text = m.pick_fresh_text(log)
        if text is None:
            print("(no non-duplicate post available)")
            break
        m.record_posted(log, text)  # in-memory only; not persisted
        print(f"\n--- would tweet #{i+1} ---")
        print(text)


def preview_linkedin():
    hr("LinkedIn (linkedin.py)")
    li = _load("li", HERE / "linkedin.py")
    state = li._load_state()
    if li._too_soon(state):
        print(f"gate:        CLOSED (last post <{li.MIN_DAYS_BETWEEN_POSTS}d ago at {state.get('last_post_at')})")
        return
    text = li._pick_fresh(state)
    if text is None:
        print("(no fresh post available)")
        return
    print("gate:        OPEN")
    print("\n--- would post ---")
    print(text)


def preview_reddit():
    hr("Reddit (reddit_post.py)")
    rp = _load("rp", HERE / "reddit_post.py")
    state = rp._load_state()
    cand = rp._pick_candidate(state)
    if cand is None:
        print("gate:        CLOSED (all safe subs on cooldown or dedup exhausted)")
        return
    print(f"gate:        OPEN → r/{cand['subreddit']}")
    print(f"\n--- would submit ---")
    print(f"title: {cand['title']}")
    print(f"\n{cand['body']}")


def preview_bluesky():
    hr("Bluesky (bluesky.py)")
    bs = _load("bs", HERE / "bluesky.py")
    state = bs._load_state()
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = state.get("post_count", 0) if state.get("last_date") == today else 0
    remaining = bs.MAX_POSTS_PER_DAY - used
    print(f"cap:         {bs.MAX_POSTS_PER_DAY}/day  used_today: {used}  remaining: {max(0, remaining)}")
    if remaining <= 0:
        print("gate:        CLOSED (daily cap reached)")
        return
    for i in range(min(remaining, 2)):
        text = bs._pick_fresh(state)
        if text is None:
            print("(no fresh post available)")
            break
        state.setdefault("posted_hashes", []).append(bs._hash(text))
        print(f"\n--- would post #{i+1} ({len(text)}/{bs.CHAR_LIMIT} chars) ---")
        print(text)


def main():
    print("Preview: what every channel would post right now (all dry-run).")
    print("No credentials used. No files modified.")
    preview_x()
    preview_linkedin()
    preview_reddit()
    preview_bluesky()
    print()
    print("═" * 70)
    print("Meta (FB/IG/Threads) preview: run the social-promo workflow with")
    print("META_AUTOPOST=dry in slashman413.github.io — that's the equivalent")
    print("dry-run for the Meta path (needs image rendering, not previewable here).")


if __name__ == "__main__":
    main()
