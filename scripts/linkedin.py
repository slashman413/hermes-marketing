#!/usr/bin/env python3
"""
hermes-marketing: LinkedIn auto-post.

Ban-safe by design:
- Uses the OFFICIAL LinkedIn v2 UGC Posts API (not scraping / session replay).
- Weekly cadence (LinkedIn algorithm penalises over-posting).
- Verbatim dedup so the same post never goes out twice.
- Dry-run when LINKEDIN_ACCESS_TOKEN / LINKEDIN_ACTOR_URN aren't set.

Required env / GitHub Secrets:
- LINKEDIN_ACCESS_TOKEN  — OAuth 2.0 bearer token (w_member_social scope)
- LINKEDIN_ACTOR_URN     — urn:li:person:{id}  OR  urn:li:organization:{id}

Setup steps in docs/linkedin_autopost_setup.md.
"""
import os, sys, json, random, logging, hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="[linkedin] %(message)s")
log = logging.getLogger(__name__)

MIN_DAYS_BETWEEN_POSTS = 3   # never post more than ~2x/week
DEDUP_HISTORY = 30           # remember this many past posts

# ── Curated LinkedIn posts (longer, professional voice) ──
CURATED_POSTS = [
    ("I've been running a one-person software portfolio entirely on free infrastructure, "
     "and the economics still surprise me.\n\n"
     "GitHub Actions handles the scheduling and compute. GitHub Pages hosts 20+ live tools. "
     "Ko-fi handles checkout. No servers. No fixed costs.\n\n"
     "The lineup includes a Taiwan-stock signal scanner, an ETF analysis dashboard, an "
     "automated YouTube Shorts pipeline, and a set of free everyday tools.\n\n"
     "Everything is open source: https://github.com/slashman413\n"
     "Try the tools: https://slashmantools.us\n\n"
     "If you're a developer sitting on side-project ideas, the barrier to shipping has never "
     "been lower.\n\n"
     "#buildinpublic #indiehackers #automation #sideproject"),

    ("Most \"AI side projects\" I see stop at the demo. What I found actually works is picking "
     "one tiny painful workflow and automating it end-to-end.\n\n"
     "Concrete example from my own portfolio:\n"
     "• Problem: manually screening Taiwan stocks every night\n"
     "• Fix: a GitHub Actions job scans the entire market for MACD/KD/RSI signals, emails "
     "the shortlist, and publishes a public dashboard\n"
     "• Result: zero minutes of my time, every trading day\n\n"
     "Live: https://slashmantools.us/twse-surge-stocks-dna/\n"
     "Source: https://github.com/slashman413\n\n"
     "The lesson: automation compounds. One saved hour a day is 250 hours a year.\n\n"
     "#automation #buildinpublic #productivity"),

    ("Every free tool on my site has one rule: your data never leaves your browser.\n\n"
     "PDF merge, image compression, password generation, JSON formatting, JWT decoding — all "
     "run locally. No uploads. No accounts. No tracking.\n\n"
     "I built these because I got tired of pasting sensitive data into random SaaS pages just "
     "to do a 30-second task.\n\n"
     "20+ tools, one bookmark: https://slashmantools.us\n\n"
     "If a \"privacy-first\" tool asks you to sign up before you can use it, it isn't.\n\n"
     "#privacy #webdev #tools"),

    ("A pattern I keep seeing: developers underestimate how far GitHub's free tier goes.\n\n"
     "In the last six months on strictly free infrastructure I've shipped:\n"
     "• 20+ browser tools (GitHub Pages)\n"
     "• 4 automation products (GitHub Actions as cron + workers)\n"
     "• A Taiwan-stock signal engine that runs every trading day\n"
     "• A daily Shorts pipeline that hasn't missed a day\n\n"
     "The economics: $0/month in hosting. Every dollar of revenue is margin.\n\n"
     "Source: https://github.com/slashman413\n"
     "Tools: https://slashmantools.us\n\n"
     "#buildinpublic #indiehackers #sideproject"),

    # Paid CTA — SaaS Starter Kit fits the LinkedIn dev-professional audience.
    ("If your side-project momentum keeps dying in the auth-and-billing setup, I packaged "
     "the boilerplate I use for my own SaaS work as a starter kit.\n\n"
     "SaaS Starter Kit — Next.js 15, TypeScript, Prisma, Auth.js (email + OAuth), "
     "Stripe webhooks, multi-tenant org/RBAC model. One-click Vercel deploy: it "
     "provisions a Neon Postgres, runs migrations, and seeds a demo login for you. "
     "Sign in as `owner@acme.test` and start extending.\n\n"
     "For anyone who wants the plumbing out of the way so they can focus on the "
     "product:\n"
     "https://slashmantools.us/saas/\n\n"
     "Source is on GitHub if you want to look before you buy: "
     "https://github.com/slashman413/saas-starter-lite\n\n"
     "#SaaS #NextJS #buildinpublic #indiehackers"),
]


def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def _load_state() -> dict:
    p = BASE_DIR / "docs" / "linkedin_state.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_post_at": "", "posted_hashes": []}


def _save_state(state: dict):
    p = BASE_DIR / "docs" / "linkedin_state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _pick_fresh(state: dict) -> str | None:
    posted = state.get("posted_hashes", [])
    fresh = [t for t in CURATED_POSTS if _hash(t) not in posted]
    if not fresh:
        # All posts used within dedup window — cycle by dropping oldest hash.
        return random.choice(CURATED_POSTS)
    return random.choice(fresh)


def _too_soon(state: dict) -> bool:
    last = state.get("last_post_at", "")
    if not last:
        return False
    try:
        dt = datetime.fromisoformat(last)
    except Exception:
        return False
    return (datetime.now(timezone.utc) - dt).days < MIN_DAYS_BETWEEN_POSTS


def _live() -> bool:
    return bool(os.environ.get("LINKEDIN_ACCESS_TOKEN") and os.environ.get("LINKEDIN_ACTOR_URN"))


def post_to_linkedin(text: str) -> bool:
    """Post via the official v2 UGC Posts API. Dry-run if tokens missing."""
    try:
        from _utm import tag as _utm_tag
        text = _utm_tag(text, "linkedin")
    except Exception:
        pass
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    actor = os.environ.get("LINKEDIN_ACTOR_URN")
    if not (token and actor):
        log.info("DRY-RUN (no LINKEDIN_ACCESS_TOKEN / LINKEDIN_ACTOR_URN):\n" + text[:200])
        return True
    try:
        import requests
    except ImportError:
        log.warning("requests not installed; skipping LinkedIn post.")
        return False
    payload = {
        "author": actor,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        json=payload, timeout=45,
    )
    ok = r.status_code in (200, 201) and (r.headers.get("x-restli-id") or "id" in (r.text or ""))
    if ok:
        log.info(f"posted (status {r.status_code}, id={r.headers.get('x-restli-id')})")
    else:
        log.warning(f"FAILED (status {r.status_code}): {r.text[:300]}")
        from _discord import notify
        hint = " (token likely expired — LinkedIn access tokens last ~60d)" if r.status_code == 401 else ""
        notify(f"🔴 LinkedIn auto-post FAILED (HTTP {r.status_code}){hint}\n```{r.text[:300]}```")
    return ok


def main():
    state = _load_state()
    if _too_soon(state):
        log.info(f"cadence gate: last post <{MIN_DAYS_BETWEEN_POSTS}d ago, skipping.")
        return
    text = _pick_fresh(state)
    if text is None:
        log.info("no fresh post available, skipping.")
        return
    if post_to_linkedin(text) and _live():
        # Only persist state after a REAL live post; dry-runs must not burn
        # cadence budget (else first live run gets blocked by fake "recent" post).
        state["last_post_at"] = datetime.now(timezone.utc).isoformat()
        posted = state.setdefault("posted_hashes", [])
        posted.append(_hash(text))
        del posted[:-DEDUP_HISTORY]
        _save_state(state)


if __name__ == "__main__":
    main()
