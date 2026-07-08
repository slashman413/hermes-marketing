# Marketing automation — operator status

_Single source of truth for the auto-post system's state. Skim this first._

## TL;DR — your next actions

1. **Answer the `GENTLE10` question** (see "Open decisions"). Blocks nothing else, but it's a live false-promo risk.
2. **Activate channels** — `./scripts/setup_secrets.sh bluesky` (5 min, lowest risk), verify with the **Preflight** workflow, then work down the list in `AUTOPOST_MASTER_SETUP.md`.
3. Everything else is done and running.

## Channel status

| Channel | State | Cadence | Notes |
|---|---|---|---|
| Bluesky | ✅ **LIVE & POSTING** | 2×/day cap | **first real posts confirmed 2026-07-08 08:00 UTC** (2/2: YouTube-channel + SaaS Starter, clickable links). First actual social posts of the whole project. |
| X / Twitter | ⚠️ **DRY-RUN ONLY — `X_API_*` secrets were NEVER set** | 3×/day, cap 6 | Discovered 2026-07-08 via preflight (SKIP) + tweet_count=0 since the dry-run fix. All prior "posts" were dry-runs; nothing has ever reached X. Create an app at developer.x.com (free tier, Read+Write), add the 4 secrets. |
| LinkedIn | 🔧 dormant | ~2×/wk | needs `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ACTOR_URN` |
| Reddit (r/SideProject only) | 🔧 dormant | ~1×/mo per sub | needs `REDDIT_*` (5 secrets); account ≥30d old first |
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

## Resolved

- ~~`GENTLE10` coupon~~ — **RESOLVED 2026-07-07**: removed the false/contradictory "$9.99 / GENTLE10" promo from all 4 spots; now honest flat $29, no code (commits d185e3e, b5c2686).
- ~~Ko-fi links~~ — **VERIFIED LIVE 2026-07-07**: all 4 (ShortsGen/TWSE/Deal Finder/SEO) resolve with working "Buy now" buttons on the ytstories0413 shop. (Direct fetches 403 on Cloudflare; confirmed via reader proxy.)

## Open decisions (need you)

1. **Activate channels** — `./scripts/setup_secrets.sh bluesky` (5 min, lowest risk) → run Preflight → done. Then work down `AUTOPOST_MASTER_SETUP.md`.
2. **X account handle** — confirm via a "Daily Marketing" Actions run log (whichever account owns the `X_API_*` secrets). Can't be read from code.
3. ~~`ai-tech-news-vid-2ppl` deploy~~ — **LAUNCHED 2026-07-08** 🎉. User created the Gumroad product (`l/njserv`, $34). Buy buttons wired (+ landing price corrected $39→$34 to match checkout). The product repo turned out to be **private** (Pages can't publish on free plan), so the landing is served from the hub repo at `slashman413.github.io/ai-tech-news-vid-2ppl/` → live at slashmantools.us/ai-tech-news-vid-2ppl/ (verified 200, checkout 200). Added to Meta rotation (26 sites) + X curated pool. **Landing source of truth stays in the private repo's `docs/`; copy to the hub on change.**

## Token expiry reminders

LinkedIn ~60d · Meta Page/IG/Threads ~60d · Bluesky app password (revoke if leaked) · X (rotate yearly). Failure alerts fire to Discord on expiry.
