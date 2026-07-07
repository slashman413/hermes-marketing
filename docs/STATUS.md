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

## Resolved

- ~~`GENTLE10` coupon~~ — **RESOLVED 2026-07-07**: removed the false/contradictory "$9.99 / GENTLE10" promo from all 4 spots; now honest flat $29, no code (commits d185e3e, b5c2686).
- ~~Ko-fi links~~ — **VERIFIED LIVE 2026-07-07**: all 4 (ShortsGen/TWSE/Deal Finder/SEO) resolve with working "Buy now" buttons on the ytstories0413 shop. (Direct fetches 403 on Cloudflare; confirmed via reader proxy.)

## Open decisions (need you)

1. **Activate channels** — `./scripts/setup_secrets.sh bluesky` (5 min, lowest risk) → run Preflight → done. Then work down `AUTOPOST_MASTER_SETUP.md`.
2. **X account handle** — confirm via a "Daily Marketing" Actions run log (whichever account owns the `X_API_*` secrets). Can't be read from code.
3. **`ai-tech-news-vid-2ppl` — deploy is blocked on TWO things (investigated 2026-07-07):**
   - **No checkout.** The landing's Buy buttons point to `slashmaster6.gumroad.com` (store homepage), not a product page — there's no dedicated $39 Gumroad product (kuvajr is SaaS Starter). Deploying now = a live sales page you can't buy from. → Create the Gumroad product, send me the URL, I wire the Buy button.
   - **Pages not enabled.** Siblings serve via "Deploy from branch" (a repo Settings toggle needing API access I don't have). → Toggle Settings → Pages → source = `main /docs`, OR I add a GitHub Actions deploy workflow — but only after the checkout is fixed (won't publish a broken funnel).

## Token expiry reminders

LinkedIn ~60d · Meta Page/IG/Threads ~60d · Bluesky app password (revoke if leaked) · X (rotate yearly). Failure alerts fire to Discord on expiry.
