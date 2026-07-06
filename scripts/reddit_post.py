#!/usr/bin/env python3
"""
hermes-marketing: Reddit auto-post.

Reddit is the RISKIEST platform to automate — subreddits enforce local rules
(most notably r/taiwan's 10% self-promo cap) and shadow-ban is quick. This
script is deliberately conservative:

- Only posts to subreddits in AUTO_SAFE_SUBS. Any other subreddit is refused,
  even if hand-added to the pool. Change this list only after reading the sub's
  rules yourself.
- Monthly cadence per subreddit (MIN_DAYS_BETWEEN_POSTS_PER_SUB = 28).
- Verbatim dedup on (subreddit, title, body).
- Uses the OFFICIAL Reddit API via praw with a script-app user-agent.
- Self-post only (text body). Link-only posts get spam-flagged faster.
- Dry-run when REDDIT_* creds missing.

Required env / GitHub Secrets:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USERNAME
- REDDIT_PASSWORD           (or use REDDIT_REFRESH_TOKEN, see docs)
- REDDIT_USER_AGENT         (e.g. "slashman413-hermes/1.0 by u/slashman413")

Setup steps in docs/reddit_autopost_setup.md.
"""
import os, sys, json, random, logging, hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="[reddit] %(message)s")
log = logging.getLogger(__name__)

# ── Ban-safety knobs ──
AUTO_SAFE_SUBS = {"SideProject"}   # only these subs will ever be auto-posted to
MIN_DAYS_BETWEEN_POSTS_PER_SUB = 28
DEDUP_HISTORY = 30

# ── Curated Reddit posts (title + body, r/SideProject-safe only) ──
CURATED_POSTS = [
    {
        "subreddit": "SideProject",
        "title": "Built a 20+ tool micro-SaaS portfolio solo on 100% free infra (GH Actions + Pages + Ko-fi)",
        "body": (
            "Solo dev here. Everything runs on free tiers:\n\n"
            "- GitHub Actions as cron/workers (Shorts gen, stock scans, deal alerts, SEO pages)\n"
            "- GitHub Pages hosts 20+ tool sites\n"
            "- Ko-fi for the paid tiers\n\n"
            "Free tools: https://slashmantools.us  \n"
            "Source: https://github.com/slashman413\n\n"
            "Happy to answer anything about the stack or what actually converts."
        ),
    },
    {
        "subreddit": "SideProject",
        "title": "6 months in: what actually worked automating a one-dev software portfolio",
        "body": (
            "Quick brain-dump on what moved the needle for me running side-projects solo:\n\n"
            "- **GitHub Actions is a cron/worker platform in disguise.** I use it for daily "
            "Shorts generation, stock signal scans, deal-finder emails, SEO page publishing.\n"
            "- **GitHub Pages > any static host.** Free, HTTPS, CDN, and it just works with "
            "custom domains. 20+ tool sites live on it.\n"
            "- **Ko-fi for checkout.** Setup was minutes, not days. Fees are reasonable for "
            "the volume.\n"
            "- **Content is the bottleneck, not code.** I ended up automating the marketing "
            "posts too (official APIs only, staying inside ToS).\n\n"
            "Everything's open: https://github.com/slashman413  \n"
            "Live tools: https://slashmantools.us\n\n"
            "AMA on the stack or the economics."
        ),
    },
]


def _hash(sub: str, title: str, body: str) -> str:
    return hashlib.sha256(f"{sub}|{title}|{body}".encode("utf-8")).hexdigest()[:16]


def _load_state() -> dict:
    p = BASE_DIR / "docs" / "reddit_state.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_post_per_sub": {}, "posted_hashes": []}


def _save_state(state: dict):
    p = BASE_DIR / "docs" / "reddit_state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _sub_too_soon(state: dict, sub: str) -> bool:
    last = state.get("last_post_per_sub", {}).get(sub, "")
    if not last:
        return False
    try:
        dt = datetime.fromisoformat(last)
    except Exception:
        return False
    return (datetime.now(timezone.utc) - dt).days < MIN_DAYS_BETWEEN_POSTS_PER_SUB


def _pick_candidate(state: dict):
    posted = state.get("posted_hashes", [])
    # Filter to safe subs, cadence-clear, and not-recently-posted.
    fresh = [
        p for p in CURATED_POSTS
        if p["subreddit"] in AUTO_SAFE_SUBS
        and not _sub_too_soon(state, p["subreddit"])
        and _hash(p["subreddit"], p["title"], p["body"]) not in posted
    ]
    return random.choice(fresh) if fresh else None


def post_to_reddit(cand: dict) -> bool:
    """Submit a self-post via praw. Dry-run if creds missing."""
    creds = {
        "client_id":     os.environ.get("REDDIT_CLIENT_ID"),
        "client_secret": os.environ.get("REDDIT_CLIENT_SECRET"),
        "username":      os.environ.get("REDDIT_USERNAME"),
        "password":      os.environ.get("REDDIT_PASSWORD"),
        "user_agent":    os.environ.get("REDDIT_USER_AGENT", "hermes-marketing/1.0"),
    }
    if not all(v for k, v in creds.items() if k != "user_agent"):
        log.info(f"DRY-RUN (creds missing) → would post to r/{cand['subreddit']}:")
        log.info(f"  title: {cand['title']}")
        log.info(f"  body:  {cand['body'][:120]}…")
        return True
    if cand["subreddit"] not in AUTO_SAFE_SUBS:
        log.warning(f"refusing to auto-post to r/{cand['subreddit']} (not in AUTO_SAFE_SUBS)")
        return False
    try:
        import praw
    except ImportError:
        log.warning("praw not installed; skipping.")
        return False
    try:
        r = praw.Reddit(**creds)
        submission = r.subreddit(cand["subreddit"]).submit(
            title=cand["title"], selftext=cand["body"], send_replies=True,
        )
        log.info(f"posted to r/{cand['subreddit']}: {submission.shortlink}")
        return True
    except Exception as e:
        log.warning(f"FAILED to post to r/{cand['subreddit']}: {e}")
        return False


def main():
    state = _load_state()
    cand = _pick_candidate(state)
    if cand is None:
        log.info("no eligible post (cadence gate or dedup exhausted).")
        return
    if post_to_reddit(cand):
        state.setdefault("last_post_per_sub", {})[cand["subreddit"]] = \
            datetime.now(timezone.utc).isoformat()
        posted = state.setdefault("posted_hashes", [])
        posted.append(_hash(cand["subreddit"], cand["title"], cand["body"]))
        del posted[:-DEDUP_HISTORY]
        _save_state(state)


if __name__ == "__main__":
    main()
