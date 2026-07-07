# Marketing automation — operator status

_Single source of truth for the auto-post system's state. Skim this first._

## TL;DR — your next actions

1. **Answer the `GENTLE10` question** (see "Open decisions"). Blocks nothing else, but it's a live false-promo risk.
2. **Activate channels** — `./scripts/setup_secrets.sh bluesky` (5 min, lowest risk), verify with the **Preflight** workflow, then work down the list in `AUTOPOST_MASTER_SETUP.md`.
3. Everything else is done and running.

## Channel status

| Channel | State | Cadence | Notes |
|---|---|---|---|
| X / Twitter | ✅ **LIVE** | 3×/day, cap 6 | official API, dedup, jitter, curated pool |
| LinkedIn | 🔧 dormant | ~2×/wk | needs `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ACTOR_URN` |
| Reddit (r/SideProject only) | 🔧 dormant | ~1×/mo per sub | needs `REDDIT_*` (5 secrets); account ≥30d old first |
| Bluesky | 🔧 dormant | 2×/day cap | needs `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` |
| Facebook / Instagram / Threads | 🔧 dormant | 2×/day | needs Meta app secrets + `META_AUTOPOST=1` (test `=dry` first). In `slashman413.github.io/social_promo.py`. |

All dormant channels: official APIs only, verbatim dedup, cadence caps, dry-run
when creds absent, Discord failure alerts, and per-channel UTM attribution.

## What's built (this repo unless noted)

- **Posters:** `scripts/marketing.py` (X), `linkedin.py`, `reddit_post.py`, `bluesky.py`; Meta in `slashman413.github.io/social_promo.py`.
- **Attribution:** `scripts/_utm.py` tags `slashmantools.us` links per channel → GA `G-MY95FHB8JG` shows the breakdown. Ko-fi/GitHub/YouTube links left alone.
- **Tooling:** `scripts/preview_all.py` (dry-run preview), `scripts/preflight.py` (verify tokens without posting), `scripts/setup_secrets.sh` (bulk-set via gh CLI).
- **CI:** `.github/workflows/tests.yml` runs `tests/test_autopost.py` (30 zero-dependency regression tests) on push; `preview.yml` + `preflight.yml` are one-click health checks.
- **Docs:** `AUTOPOST_MASTER_SETUP.md` (ordered activation guide), per-channel `*_autopost_setup.md`, `content_pack_2026-07-04.md`.

## Prices (canonical: `hermes-pay/scripts/payment.py`)

ShortsGen $29 · TWSE Premium $49 · Deal Finder **$9** · SEO Content Engine $19/mo · SaaS Starter $99 (Gumroad).
All Ko-fi links verified live 2026-07-07 (direct fetch 403s are Cloudflare bot-block, not dead links).

## Open decisions (need you)

1. **`GENTLE10` coupon** — advertised in `hermes-pay/docs/index.html` (lines 70, 103) and `pixabay-shorts-bot/src/main.py` (309-310, auto-posted to every YouTube description). The copy is also self-contradictory: one place says "10% off", another "首月 $9.99" (~66% off), and the Ko-fi checkout shows a flat $29 with no coupon field. **If the code exists on Ko-fi → reconcile the copy to one consistent offer. If not → remove the $9.99/GENTLE10 claims.** Not auto-touched (could be a real active promo).
2. **Ko-fi links** — eyeball once in a browser (can't be automated-checked past Cloudflare).
3. **X account handle** — confirm via a "Daily Marketing" Actions run log (whichever account owns the `X_API_*` secrets).
4. **`ai-tech-news-vid-2ppl` is undeployed** — a $39 product ("YouTube channel in a box") with a finished landing page that 404s on both slashmantools.us and github.io. It can't be promoted or sold until deployed (enable GitHub Pages / set the CNAME path). Left out of rotations deliberately — promoting a dead URL is worse than silence.

## Token expiry reminders

LinkedIn ~60d · Meta Page/IG/Threads ~60d · Bluesky app password (revoke if leaked) · X (rotate yearly). Failure alerts fire to Discord on expiry.
