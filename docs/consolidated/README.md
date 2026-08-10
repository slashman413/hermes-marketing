# Consolidated archive — hermes-* cluster (2026-08-11)

Step 2 of slashman413 portfolio strategy (artifact `60baa945` → `slashman413-repo-strategy.md` §2 Cluster D).
The 7 archived hermes-* repos remain fully readable on GitHub (archived = read-only, NOT deleted).
This folder preserves the genuinely unique, non-clone code/docs in the canonical infra repo
(`hermes-marketing`) so no capability strands in a dead repo.

Archived 2026-08-11 by Cowork task `fb4991aa`: hermes-pro, hermes-make-money, hermes-pay,
hermes-content-recycle, hermes-lead-magnet, hermes-shortsgen, hermes-twse-premium.
Kept: hermes-marketing (this repo), hermes-seo-farm.

## twse-premium/  →  fold into TWSE Quant Suite (NEXT ACTION)

Source: `slashman413/hermes-twse-premium` (archived). Genuine IP, not a clone.
This was the **TWSE Premium paid-signal service**: Ko-fi checkout funnel
(`https://ko-fi.com/s/b99720d13d`) with $19/mo · $49/qtr · $149/yr · $499 lifetime tiers.

- `scripts/premium.py` — TWSE market scan → per-customer email alerts. Scans via
  `slashman413/twse-surge-stocks-dna` engine (the future TWSE Quant Suite core), 2×/day
  weekdays (09:00 / 13:30 Taipei), SMTP delivery, signals.json log.
- `scripts/webhook_bridge.py` — Ko-fi webhook (kofi_subscription/cancellation/refund/
  shop_order) → customer lifecycle in customers.json (injection-safe payload handling).
- `FUNNEL.md` — free-vs-paid line (free = 2004–2026 backtest dashboard + 9-step "大飆股 DNA"
  methodology; paid = daily actionable scans + email alerts). **Use as the monetization spec.**
- `MARKETING.md`, `EMAILS.md`, `AUTOMATION.md`, `SMTP_SETUP.md` — funnel copy, drip email
  scripts, ops automation, SMTP config.
- `trust-post-week-1.md` / `trust-post-week-2.md` — public trust-building signal posts
  (one-week-lag proof of strategy performance). Reuse in the TWSE suite launch.
- Note: `data/customers.json` contained only test/self entries (slashman413@gmail.com,
  success-test@example.com) — no real paying customers at archive time.

**TWSE consolidation task must port premium.py + webhook_bridge.py + FUNNEL.md into the
TWSE Quant Suite monorepo** (Cluster B: twse-surge-stocks-dna engine + tw-etf-dashboard +
twse-backtests + etf-financial-analyzer). Do not rebuild from scratch — the scan/email/
webhook logic is here.

## pay/  — payment webhook module (reference)

Source: `slashman413/hermes-pay` (archived). Real payment-processing code, never deployed
(Render blueprint only, no live service, no workflow). Superseded by the current funnel
(Ko-fi direct links + Gumroad + Mautic), but the webhook logic is the only copy in the org:

- `scripts/webhook.py` — Ko-fi webhook verification + product/tier mapping + customer
  records (HMAC-verified, injection-safe).
- `scripts/payment.py` — checkout-link generator for all products (saas-starter, shortsgen,
  twse, seoengine, dealfinder) → Ko-fi/Gumroad URLs.
- `kofi/` `gumroad/` — product description + welcome-guide copy (ShortsGen Pro, TWSE,
  Dealfinder, SEO Engine). Salvageable sales copy.
- `PAYMENTS.md`, `DEPLOY.md` — setup/deploy docs.

## make-money/  — experiment ledger (reference)

Source: `slashman413/hermes-make-money` (archived). The only non-clone content is the
**experiments research ledger** (5 monetization experiments with rationale + results):

- `experiments/exp-001-shorts-affiliate` — shorts affiliate monetization (script + README)
- `experiments/exp-002-tools-adsense` — AdSense injection into tools pages
- `experiments/exp-003-github-sponsors` — GitHub sponsors exploration
- `experiments/exp-004-twse-premium` — origin of the TWSE Premium experiment (see twse-premium/)
- `experiments/exp-005-saas-template` — SaaS template monetization
- `INCOME.md`, `skills/monetization/exp-001-shorts-affiliate.md` — income-tracking notes

The scaffolding scripts (income.py, auto_skill.py, affiliate_links.py) were generic
"auto-income" templates — not preserved.

## What was NOT extracted (and why)

| Repo | Reason |
|---|---|
| hermes-pro | Only `dashboard.py` (revenue dashboard generator) — the strategy-flagged bot-commit noise. No unique logic. |
| hermes-content-recycle | `recycle.py` only generates per-platform share *text* (no posting APIs); capability overlaps this repo's marketing.py. |
| hermes-lead-magnet | Superseded by the LIVE lead funnel: Cloudflare Worker `lead-capture` (api.slashmantools.us/subscribe → KV → Mautic campaign 10). mock_server.py = demo stub. |
| hermes-shortsgen | SaaS stub engine (0 customers, demo usage only). The actual Shorts upload pipeline lives in `slashman413/pixabay-shorts-bot` (separate repo, workflows already disabled, last run 2026-07-06; channel uploads ~1-2/wk, not 2/day). Nothing live lost. |

## Workflow hygiene

Before archiving, all non-pages workflows on the 7 repos were confirmed disabled
(hermes-pro `Revenue Dashboard` + hermes-make-money `Make Money Pipeline` were the last two
ACTIVE — disabled 2026-08-11; the other 5 repos' workflows were already `disabled_manually`).
Archiving also freezes pushes, so bot commits stop.
