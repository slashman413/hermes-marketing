#!/usr/bin/env python3
"""
One-time Bluesky profile seeder — run via the "Seed Bluesky profile" workflow
(workflow_dispatch). Uses the existing BLUESKY_HANDLE / BLUESKY_APP_PASSWORD
secrets, so no credentials are handled locally.

Does, in order:
  1. Sets display name + bio on the profile record (preserves existing avatar).
  2. Posts a build-in-public intro and PINS it.
  3. Posts 4 value-first seed posts (spaced), so the profile reads as a person
     before the daily promo poster's content shows up.

Idempotent: before doing anything it checks the account's recent posts for the
intro's signature; if already present, it exits without posting again. Safe to
re-trigger.
"""
import os, sys, time, json
from datetime import datetime, timezone

PDS = "https://bsky.social"
PUBLIC = "https://public.api.bsky.app"

DISPLAY_NAME = "slashman · AI 工具人"
BIO = ("Solo dev building in public. 20+ free browser tools, a Taiwan-stock "
       "signal scanner, and automation that runs on GitHub Actions while I "
       "sleep. Everything open source.\n🔗 slashmantools.us")

INTRO = (
    "hi bluesky 👋 i'm a solo dev running a little automation setup on free infra.\n\n"
    "what i've shipped:\n"
    "• 20+ free browser tools (no signup, no tracking) — slashmantools.us\n"
    "• a taiwan-stock quant scanner, backtested 20 years\n"
    "• a youtube channel that generates + uploads itself\n"
    "• all open source: github.com/slashman413\n\n"
    "here to share what actually works building tiny products solo."
)

# INTRO_SIG: a stable substring used to detect prior seeding.
INTRO_SIG = "i'm a solo dev running a little automation setup"

SEEDS = [
    ("the most underrated free tier in tech is GitHub Actions.\n"
     "i use it as a cron + worker fleet: daily stock scans, video generation, "
     "SEO publishing. $0/month.\n"
     "if you have a side-project idea, you probably already have the infra."),

    ("built a thing: paste messy JSON, get it formatted + validated, test a "
     "regex against it — all in the browser, nothing uploaded.\n"
     "free, no signup: slashmantools.us/json-regex-devtools/\n"
     "what tiny tool do you keep re-googling?"),

    ("six months building solo taught me the uncomfortable truth: the code is "
     "never the bottleneck. distribution is.\n"
     "a great tool with no audience makes $0. so i'm doing the scary thing and "
     "posting here. 👋"),

    ("solo devs of bluesky — what's the one workflow you automated that gave "
     "you the most time back?\n"
     "i'll start: nightly taiwan-stock screening. 30 min/day → 0."),
]


def main():
    handle = os.environ.get("BLUESKY_HANDLE")
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD")
    if not (handle and app_pw):
        print("[seed] BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set — abort.")
        sys.exit(1)
    import requests

    # ── auth ──
    s = requests.post(f"{PDS}/xrpc/com.atproto.server.createSession",
                      json={"identifier": handle, "password": app_pw}, timeout=30)
    if s.status_code != 200:
        print(f"[seed] auth failed {s.status_code}: {s.text[:200]}")
        sys.exit(1)
    sess = s.json()
    did, jwt = sess["did"], sess["accessJwt"]
    H = {"Authorization": f"Bearer {jwt}"}
    print(f"[seed] authenticated as {handle} ({did})")

    # ── idempotency: already seeded? ──
    try:
        feed = requests.get(f"{PUBLIC}/xrpc/app.bsky.feed.getAuthorFeed",
                            params={"actor": did, "limit": 50}, timeout=30).json()
        for it in feed.get("feed", []):
            if INTRO_SIG in (it.get("post", {}).get("record", {}).get("text", "")):
                print("[seed] intro already present — profile is seeded. Nothing to do.")
                return
    except Exception as e:
        print(f"[seed] feed check failed (continuing): {e}")

    def create_post(text):
        rec = {"$type": "app.bsky.feed.post", "text": text,
               "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
        # link facets so URLs are clickable
        import re
        facets = []
        for m in re.finditer(r"https?://[^\s]+", text):
            u = m.group(0).rstrip(".,;!?)")
            st = len(text[:m.start()].encode()); facets.append(
                {"index": {"byteStart": st, "byteEnd": st + len(u.encode())},
                 "features": [{"$type": "app.bsky.richtext.facet#link", "uri": u}]})
        if facets: rec["facets"] = facets
        r = requests.post(f"{PDS}/xrpc/com.atproto.repo.createRecord", headers=H,
                          json={"repo": did, "collection": "app.bsky.feed.post", "record": rec},
                          timeout=45).json()
        return r.get("uri"), r.get("cid")

    # ── 1. profile: display name + bio (preserve existing avatar/banner) ──
    try:
        existing = requests.get(f"{PDS}/xrpc/com.atproto.repo.getRecord",
                                params={"repo": did, "collection": "app.bsky.actor.profile", "rkey": "self"},
                                headers=H, timeout=30)
        prof = existing.json().get("value", {}) if existing.status_code == 200 else {}
        prof["$type"] = "app.bsky.actor.profile"
        prof["displayName"] = DISPLAY_NAME
        prof["description"] = BIO
        requests.post(f"{PDS}/xrpc/com.atproto.repo.putRecord", headers=H,
                      json={"repo": did, "collection": "app.bsky.actor.profile",
                            "rkey": "self", "record": prof}, timeout=30)
        print("[seed] profile display name + bio set.")
    except Exception as e:
        print(f"[seed] profile update failed (continuing): {e}")

    # ── 2. intro post + pin ──
    uri, cid = create_post(INTRO)
    print(f"[seed] intro posted: {uri}")
    if uri and cid:
        try:
            existing = requests.get(f"{PDS}/xrpc/com.atproto.repo.getRecord",
                                    params={"repo": did, "collection": "app.bsky.actor.profile", "rkey": "self"},
                                    headers=H, timeout=30)
            prof = existing.json().get("value", {}) if existing.status_code == 200 else {"$type": "app.bsky.actor.profile"}
            prof["pinnedPost"] = {"uri": uri, "cid": cid}
            requests.post(f"{PDS}/xrpc/com.atproto.repo.putRecord", headers=H,
                          json={"repo": did, "collection": "app.bsky.actor.profile",
                                "rkey": "self", "record": prof}, timeout=30)
            print("[seed] intro pinned.")
        except Exception as e:
            print(f"[seed] pin failed (continuing): {e}")

    # ── 3. seed posts (spaced) ──
    for i, t in enumerate(SEEDS):
        time.sleep(5)
        u, _ = create_post(t)
        print(f"[seed] seed {i+1}/{len(SEEDS)} posted: {u}")

    print("[seed] done. Profile seeded.")


if __name__ == "__main__":
    main()
