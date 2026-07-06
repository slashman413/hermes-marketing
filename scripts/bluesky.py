#!/usr/bin/env python3
"""
hermes-marketing: Bluesky (AT Protocol) auto-post.

Ban-safe: uses the OFFICIAL AT Protocol (com.atproto.repo.createRecord). No
scraping, no session replay. Two-post-per-day cap with jittered spacing and
verbatim dedup, matching the X poster's discipline.

Required env / GitHub Secrets:
- BLUESKY_HANDLE      — your full handle, e.g. slashman413.bsky.social
- BLUESKY_APP_PASSWORD — an APP password (Settings → App Passwords), NOT your
                        main account password

Setup steps in docs/bluesky_autopost_setup.md.
"""
import os, sys, json, random, logging, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="[bluesky] %(message)s")
log = logging.getLogger(__name__)

MAX_POSTS_PER_DAY = 2
DEDUP_HISTORY = 40
POST_SPACING_SEC = (25, 90)
CHAR_LIMIT = 300   # Bluesky grapheme-cluster limit

# Same curated pool as the X poster, plus one Bluesky-native post.
# (Bluesky users respond well to open-source/indie authenticity.)
CURATED_POSTS = [
    "I shipped 20+ free browser tools this year — calculators, PDF merge, "
    "QR codes, image compression, color palettes, dev utilities.\n"
    "No signup. No ads-wall. Just open and use.\n"
    "👉 https://slashmantools.us",

    "My GitHub Actions bot makes 2 YouTube Shorts a day while I sleep — "
    "quote + music + auto-upload, zero editing.\n"
    "See it live: https://www.youtube.com/@GentleSoul666",

    "Guessing which Taiwan ETF to buy?\n"
    "Free dashboard: fundamentals + technicals for 0050 / 0056 / 00878, "
    "refreshed daily.\n"
    "👉 https://slashmantools.us/tw-etf-dashboard/dashboard.html",

    "I run a one-person automation setup on free infra:\n"
    "• GitHub Actions = my cron + workers\n"
    "• GitHub Pages = 20+ tool sites\n"
    "• Ko-fi = checkout\n"
    "All open source 👇\nhttps://github.com/slashman413",

    # Bluesky-native tone (small, honest, no hashtags)
    "hey bsky — i'm the person quietly running ~25 repos of automations on "
    "github's free tier. taiwan-stock scanner, etf dashboard, daily shorts bot, "
    "20+ browser tools. all open source.\n"
    "https://github.com/slashman413",

    # Paid CTA, dev-native tone
    "want to ship a SaaS this weekend?\n"
    "SaaS Starter Kit — Next.js 15 + Prisma + Auth.js + Stripe, one-click "
    "Vercel deploy. multi-tenant, RBAC, subs, all built in.\n"
    "https://slashmaster6.gumroad.com/l/kuvajr",

    # Paid CTA, honest tone
    "if you trade Taiwan stocks — the scanner is $49/mo (email alerts + "
    "real-time signals). free delayed version if you just want to see how "
    "it works.\n"
    "delayed: slashmantools.us/twse-surge-stocks-dna/\n"
    "paid: ko-fi.com/s/b99720d13d",
]

PDS = "https://bsky.social"


def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def _load_state() -> dict:
    p = BASE_DIR / "docs" / "bluesky_state.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_date": "", "post_count": 0, "posted_hashes": []}


def _save_state(state: dict):
    p = BASE_DIR / "docs" / "bluesky_state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _pick_fresh(state: dict) -> str | None:
    posted = state.setdefault("posted_hashes", [])
    fresh = [t for t in CURATED_POSTS if _hash(t) not in posted and len(t) <= CHAR_LIMIT]
    return random.choice(fresh) if fresh else None


def _extract_link_facet(text: str):
    """Return a facet linking the first http(s):// URL, so Bluesky renders it clickable."""
    import re
    m = re.search(r"https?://\S+", text)
    if not m:
        return None
    b = text.encode("utf-8")
    start = len(text[: m.start()].encode("utf-8"))
    end   = len(text[: m.end()].encode("utf-8"))
    return [{
        "index": {"byteStart": start, "byteEnd": end},
        "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}],
    }]


def post_to_bluesky(text: str) -> bool:
    handle = os.environ.get("BLUESKY_HANDLE")
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD")
    if not (handle and app_pw):
        log.info("DRY-RUN (no BLUESKY_HANDLE / BLUESKY_APP_PASSWORD):\n" + text[:200])
        return True
    try:
        import requests
    except ImportError:
        log.warning("requests not installed; skipping.")
        return False
    try:
        s = requests.post(f"{PDS}/xrpc/com.atproto.server.createSession",
                          json={"identifier": handle, "password": app_pw}, timeout=30)
        if s.status_code != 200:
            log.warning(f"createSession failed {s.status_code}: {s.text[:200]}")
            from _discord import notify
            hint = " (Bluesky app password may have been revoked)" if s.status_code == 401 else ""
            notify(f"🔴 Bluesky auth FAILED (HTTP {s.status_code}){hint}\n```{s.text[:300]}```")
            return False
        sess = s.json()
        record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        facets = _extract_link_facet(text)
        if facets:
            record["facets"] = facets
        r = requests.post(
            f"{PDS}/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {sess['accessJwt']}"},
            json={"repo": sess["did"], "collection": "app.bsky.feed.post", "record": record},
            timeout=45,
        )
        ok = r.status_code == 200 and "uri" in r.json()
        log.info(f"{'posted' if ok else 'FAILED'} ({r.status_code}) {r.json().get('uri','')}")
        if not ok:
            from _discord import notify
            notify(f"🔴 Bluesky createRecord FAILED (HTTP {r.status_code})\n```{r.text[:300]}```")
        return ok
    except Exception as e:
        log.warning(f"error: {e}")
        return False


def _live() -> bool:
    return bool(os.environ.get("BLUESKY_HANDLE") and os.environ.get("BLUESKY_APP_PASSWORD"))


def main():
    state = _load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("last_date") != today:
        state["last_date"] = today
        state["post_count"] = 0

    want = min(2, max(0, MAX_POSTS_PER_DAY - state.get("post_count", 0)))
    if want == 0:
        log.info(f"daily cap reached ({MAX_POSTS_PER_DAY}); skipping.")
        if _live():
            _save_state(state)
        return

    live = _live()
    for i in range(want):
        text = _pick_fresh(state)
        if text is None:
            log.info("no fresh post available; skipping.")
            break
        if post_to_bluesky(text) and live:
            # Only persist state after a REAL live post; dry-runs must not
            # burn the daily cap (else first live day is already at ceiling).
            state["post_count"] = state.get("post_count", 0) + 1
            posted = state.setdefault("posted_hashes", [])
            posted.append(_hash(text))
            del posted[:-DEDUP_HISTORY]
        if i < want - 1:
            time.sleep(random.randint(*POST_SPACING_SEC))

    if live:
        _save_state(state)


if __name__ == "__main__":
    main()
