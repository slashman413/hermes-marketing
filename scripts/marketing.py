#!/usr/bin/env python3
"""
hermes-marketing: Automated cross-platform marketing engine.
Posts to X/Twitter and generates SEO pages for all hermes products.
"""
import os, sys, json, random, logging, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

# ── Anti-ban safeguards ──
# X free tier caps writes (~17/day, 500/mo). Stay well under and never repeat
# a tweet verbatim (X rejects duplicates and spam-flags repetitive promo).
MAX_TWEETS_PER_DAY = 6
DEDUP_HISTORY = 40          # remember this many recent tweet hashes
POST_SPACING_SEC = (25, 90) # jittered pause between posts in one run

BASE_DIR = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Products with Ko-fi purchase links ──
PRODUCTS = {
    "shortsgen": {
        "name": "ShortsGen Pro",
        "tagline": "AI自動生成YouTube Shorts — 名言+音樂+自動上傳",
        "url": "https://ko-fi.com/s/896aa3c229",
        "price": "$29/mo",
        "ko-fi": True,
        "hashtags": ["YouTubeShorts", "AIContent", "ContentCreation"],
    },
    "twse": {
        "name": "TWSE Premium",
        "tagline": "台股即時掃描訊號 — 每日Email通知買賣點",
        "url": "https://ko-fi.com/s/b99720d13d",
        "price": "$49/mo",
        "ko-fi": True,
        "hashtags": ["台股", "投資", "StockTW"],
    },
    "dealfinder": {
        "name": "Deal Finder Pro",
        "tagline": "每日Amazon特價自動通知 — 省錢就該自動化",
        "url": "https://ko-fi.com/s/5730f8f947",
        "price": "$9",  # matches the live Ko-fi listing — do not advertise a higher price
        "ko-fi": True,
        "hashtags": ["AmazonDeals", "省錢", "DealFinder"],
    },
    "seo": {
        "name": "SEO Content Engine",
        "tagline": "自動生成SEO文章 — GitHub Pages免費託管",
        "url": "https://ko-fi.com/s/a03f0a8e3b",
        "price": "$19/mo",
        "ko-fi": True,
        "hashtags": ["SEO", "ContentMarketing", "GitHubPages"],
    },
    "saas_starter": {
        "name": "SaaS Starter",
        "tagline": "Ship a multi-tenant B2B SaaS this weekend — Next.js 15 + Prisma + Auth.js, RBAC, billing, API keys",
        "url": "https://slashmaster6.gumroad.com/l/kuvajr?utm_source=twitter&utm_medium=social&utm_campaign=hermes-marketing",
        "price": "$99",
        "ko-fi": False,
        "hashtags": ["nextjs", "SaaS", "buildinpublic"],
    },
    "tools": {
        "name": "免費工具集",
        "tagline": "計算機+PDF+QR碼+圖片壓縮 20+免費線上工具",
        "url": "https://slashmantools.us/",
        "price": "免費",
        "ko-fi": False,
        "hashtags": ["FreeTools", "Productivity", "OnlineTools"],
    },
    "youtube": {
        "name": "Gentle Soul",
        "tagline": "每日心靈語錄Shorts — 療癒系AI影片頻道",
        "url": "https://www.youtube.com/@GentleSoul666",
        "price": "免費訂閱",
        "ko-fi": False,
        "hashtags": ["Shorts", "Quotes", "心靈雞湯"],
    },
}

# ── Curated ready-to-post tweets (content pack 2026-07-04) ──
# Preferred over auto-assembled templates; each is used at most once per
# DEDUP window so the timeline never shows a duplicate.
CURATED_POSTS = [
    "I shipped 20+ free browser tools this year — calculators, PDF merge, "
    "QR codes, image compression, color palettes, dev utilities.\n"
    "No signup. No ads-wall. Just open and use.\n"
    "👉 https://slashmantools.us\n#buildinpublic #FreeTools #IndieHacker",

    "還在盯盤怕錯過台股買賣點？\n"
    "TWSE Premium 每天自動掃描全上市股票的 MACD/KD/RSI/ADX，訊號直接寄到你 Email。\n"
    "延遲版免費看：https://slashmantools.us/twse-surge-stocks-dna/\n"
    "即時版 $49/月 👉 https://ko-fi.com/s/b99720d13d\n#台股 #投資 #量化",

    "My GitHub Actions bot makes 2 YouTube Shorts a day while I sleep — "
    "quote + music + auto-upload, zero editing.\n"
    "See it live: https://www.youtube.com/@GentleSoul666\n"
    "Run it yourself ($29/mo): https://ko-fi.com/s/896aa3c229\n"
    "#YouTubeShorts #AIContent #automation",

    "Guessing which Taiwan ETF to buy?\n"
    "Free dashboard: fundamentals + technicals for 0050 / 0056 / 00878, "
    "refreshed daily from a whole-market scan.\n"
    "👉 https://slashmantools.us/tw-etf-dashboard/dashboard.html\n"
    "#ETF #台股 #Investing #00878",

    "I run a one-person automation setup on free infra:\n"
    "• GitHub Actions = my cron + workers\n"
    "• GitHub Pages = 20+ tool sites\n"
    "• Ko-fi = checkout\n"
    "All open source 👇\nhttps://github.com/slashman413\n"
    "#buildinpublic #indiehackers",

    "想這週末就上線一個 SaaS？\n"
    "SaaS Starter Kit：Next.js 15 + Prisma + Auth.js + Stripe，一鍵 Vercel 部署。多租戶／RBAC／訂閱都內建。\n"
    "👉 https://slashmaster6.gumroad.com/l/kuvajr\n"
    "#SaaS #buildinpublic #NextJS",

    "Amazon 特價每天都有，但你抓得到嗎？\n"
    "Deal Finder Pro：每天自動掃描熱門類別，命中你的關鍵字就 Email 通知，只要 $9。\n"
    "👉 https://ko-fi.com/s/5730f8f947\n"
    "#AmazonDeals #省錢 #自動化",

    "想經營 SEO 部落格，但寫不動每天更新？\n"
    "SEO Content Engine 自動幫你產出 SEO 文章＋免費 GitHub Pages 託管，$19/月。\n"
    "👉 https://ko-fi.com/s/a03f0a8e3b\n"
    "#SEO #ContentMarketing #GitHubPages",
    "I kept losing the first week of every SaaS to the same plumbing — auth, orgs, "
    "roles, billing, API keys.\nSo I built it once, done right, and shipped it.\n"
    "Free Lite (auth+multi-tenancy+RBAC): https://github.com/slashman413/saas-starter-lite\n"
    "Full — $99: https://slashmaster6.gumroad.com/l/kuvajr?utm_source=twitter&utm_medium=social&utm_campaign=hermes-marketing\n"
    "#nextjs #SaaS #buildinpublic",

    "The part most SaaS boilerplates fake: real multi-tenancy.\n"
    "In SaaS Starter every query is scoped by organizationId — one org can never "
    "read another's data.\nRead the code free (Lite): "
    "https://github.com/slashman413/saas-starter-lite\n#nextjs #Prisma #SaaS",

    "SaaS Starter — a Next.js 15 boilerplate where billing isn't a lie:\n"
    "the Stripe webhook is signature-verified, API keys are SHA-256-hashed, "
    "audit logs are per-org.\n$99, lifetime updates 👉 "
    "https://slashmaster6.gumroad.com/l/kuvajr?utm_source=twitter&utm_medium=social&utm_campaign=hermes-marketing\n"
    "#buildinpublic #indiehackers",
]

# ── Tweet templates (rotated for variety) ──
# NB: the {hashtags} placeholder receives an already-hash-prefixed string
# ("#tag1 #tag2 #tag3"), so templates do NOT prefix another '#' before it.
TWEET_TEMPLATES = [
    "{emoji} {name} — {tagline}\n\n👉 {url}\n\n{hashtags}",
    "{emoji} 推薦給大家！{name}\n{tagline}\n\n{url}\n{hashtags}",
    "{emoji} 試試這個：{name}\n\"{tagline}\"\n\n👇 了解更多\n{url}\n{hashtags}",
    "{emoji} 你還在{problem}嗎？\n{name} 可以幫你{solution}！\n\n{url}\n{hashtags}",
]

PROBLEMS = {
    "saas_starter": ["rebuilding auth/orgs/RBAC on every project", "losing a week to SaaS plumbing"],
    "shortsgen": ["手動剪輯影片很花時間", "每天為內容發想煩惱"],
    "twse": ["錯過台股買賣點", "沒時間盯盤"],
    "dealfinder": ["錯過Amazon好康", "每天手動比價很累"],
    "seo": ["寫文章SEO優化好難", "內容產出速度太慢"],
    "tools": ["找不到好用的免費工具"],
    "youtube": ["需要正能量"],
}

SOLUTIONS = {
    "saas_starter": ["start from a production-ready multi-tenant foundation", "ship the product, not the plumbing"],
    "shortsgen": ["自動化產出，每天2支Shorts", "AI幫你選名言+配樂"],
    "twse": ["自動掃描所有上市股票", "Email即時通知訊號"],
    "dealfinder": ["自動比價+通知", "再也不錯過特價"],
    "seo": ["自動生成SEO文章", "免費GitHub Pages託管"],
    "tools": ["20+工具免安裝直接使用"],
    "youtube": ["每天一支療癒Shorts訂閱支持"],
}

EMOJIS = {
    "saas_starter": "🛠🚀🧱", "shortsgen": "🎬🚀⚡", "twse": "📊💰📈",
    "dealfinder": "🛒🔥💎", "seo": "📝🚀🔍", "tools": "🔧🛠️⚙️", "youtube": "💭✨🌿",
}


def load_rotation_log() -> dict:
    """Load product promotion history from log file."""
    log_path = BASE_DIR / "docs" / "rotation.json"
    if log_path.exists():
        try:
            return json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_promoted": {}, "tweet_count": 0, "last_date": ""}


def save_rotation_log(data: dict):
    """Save promotion history."""
    path = BASE_DIR / "docs" / "rotation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _tweet_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def pick_fresh_text(log_data: dict) -> str | None:
    """Return a curated tweet not posted within the dedup window, else a
    freshly-built template tweet. Returns None only if everything is a dup."""
    posted = log_data.setdefault("posted_hashes", [])
    fresh = [t for t in CURATED_POSTS if _tweet_hash(t) not in posted]
    if fresh:
        return random.choice(fresh)
    # Curated pool exhausted for now — fall back to a template, retry for a
    # non-duplicate a few times before giving up.
    for _ in range(8):
        candidate = build_tweet(random.choice(list(PRODUCTS.keys())))
        if _tweet_hash(candidate) not in posted:
            return candidate
    return None


def record_posted(log_data: dict, text: str):
    posted = log_data.setdefault("posted_hashes", [])
    posted.append(_tweet_hash(text))
    del posted[:-DEDUP_HISTORY]  # keep only the most recent N


def build_tweet(product_key: str) -> str:
    """Build a single tweet for a product."""
    p = PRODUCTS[product_key]
    tmpl = random.choice(TWEET_TEMPLATES)
    emoji = random.choice(EMOJIS.get(product_key, "🚀").split())
    problems = PROBLEMS.get(product_key, [""])
    solutions = SOLUTIONS.get(product_key, [""])

    # Turn ["tag1","tag2"] into "#tag1 #tag2" — must be done here, not in the
    # template, or the join yields "#tag1 tag2" (bug 2026-07 fix).
    hashtags = " ".join("#" + h.lstrip("#") for h in p["hashtags"])

    text = tmpl.format(
        emoji=emoji,
        name=p["name"],
        tagline=p["tagline"],
        url=p["url"],
        hashtags=hashtags,
        problem=random.choice(problems),
        solution=random.choice(solutions),
    )

    # Ensure within 280 chars
    if len(text) > 280:
        text = text[:277] + "..."
    return text


def post_to_x(text: str) -> bool:
    """Post tweet to X/Twitter if credentials available, else dry-run.
    Returns True only when a real post was attempted (regardless of API outcome).
    Dry-run returns False so callers don't burn the daily cap on empty-creds runs."""
    api_key = os.environ.get("X_API_KEY", "")
    api_secret = os.environ.get("X_API_SECRET", "")
    access_token = os.environ.get("X_ACCESS_TOKEN", "")
    access_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

    # Attribution: tag slashmantools.us links so GA can credit X for the traffic.
    # (URLs are t.co-wrapped to 23 chars on X, so this never affects tweet length.)
    try:
        from _utm import tag as _utm_tag
        text = _utm_tag(text, "x")
    except Exception:
        pass  # never let attribution tagging block a post

    has_creds = all([api_key, api_secret, access_token, access_secret])

    if not has_creds:
        log.info(f"🐦 [DRY-RUN] Would tweet:\n{text}\n")
        return False

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key, consumer_secret=api_secret,
            access_token=access_token, access_token_secret=access_secret,
        )
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        log.info(f"✅ Tweeted! https://x.com/user/status/{tweet_id}")
    except Exception as e:
        log.warning(f"❌ Tweet failed: {e}")
        log.info(f"   Text was: {text[:100]}...")
    # API failure still counts as "attempted": record the hash so we don't
    # immediately retry the exact same text; the tweet_count reflects attempts.
    return True


def generate_html(promoted: list[str]) -> str:
    """Generate marketing landing page."""
    cards = ""
    for key, p in PRODUCTS.items():
        glow = "style='border:2px solid #f59e0b'" if key in promoted else ""
        price_tag = f"<span class='price'>{p['price']}</span>" if p.get('ko-fi') else "<span class='price free'>Free</span>"
        cards += f"""
        <div class='card' {glow}>
            <h3>{p['name']}</h3>
            <p>{p['tagline']}</p>
            {price_tag}
            <a href='{p['url']}'>了解更多 →</a>
        </div>"""

    canonical = "https://slashman413.github.io/hermes-marketing/"
    og_image = "https://slashmantools.us/og.png"  # reuse the hub's shared OG image
    return f"""<!DOCTYPE html>
<html lang='zh-TW'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>hermes 生態系 — 工具與服務</title>
<meta name='description' content='免費線上工具、YouTube自動化、台股訊號 — 全部開放原始碼'>
<link rel='canonical' href='{canonical}'>
<!-- Open Graph (Facebook / LinkedIn / Discord / Slack) -->
<meta property='og:type' content='website'>
<meta property='og:site_name' content='slashman413'>
<meta property='og:title' content='hermes 生態系 — 工具與服務'>
<meta property='og:description' content='免費線上工具、YouTube 自動化、台股訊號 — 全部開放原始碼'>
<meta property='og:url' content='{canonical}'>
<meta property='og:image' content='{og_image}'>
<meta property='og:locale' content='zh_TW'>
<!-- Twitter Card -->
<meta name='twitter:card' content='summary_large_image'>
<meta name='twitter:title' content='hermes 生態系 — 工具與服務'>
<meta name='twitter:description' content='免費線上工具、YouTube 自動化、台股訊號 — 全部開放原始碼'>
<meta name='twitter:image' content='{og_image}'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:#0a0a1a;color:#e2e8f0;max-width:1000px;margin:auto;padding:20px}}
h1{{text-align:center;padding:30px 0;font-size:2rem}}
.subtitle{{text-align:center;color:#64748b;margin-bottom:30px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
.card{{background:#1e293b;border-radius:16px;padding:24px;transition:transform .2s}}
.card:hover{{transform:translateY(-4px)}}
.card h3{{margin-bottom:8px;font-size:1.1rem}}
.card p{{color:#94a3b8;font-size:.9rem;margin-bottom:12px}}
.price{{display:inline-block;background:#f59e0b;color:#0a0a1a;padding:2px 10px;border-radius:20px;font-size:.8rem;font-weight:bold;margin-bottom:12px}}
.price.free{{background:#22c55e;color:#0a0a1a}}
.card a{{display:inline-block;margin-top:8px;color:#3b82f6;text-decoration:none;font-weight:bold}}
.card a:hover{{text-decoration:underline}}
.promoted-badge{{display:inline-block;background:#f59e0b;color:#0a0a1a;padding:2px 8px;border-radius:4px;font-size:.7rem;margin-left:8px}}
footer{{text-align:center;padding:40px 0;color:#475569}}
.tweet-log{{background:#1e293b;border-radius:12px;padding:16px;margin:20px 0;font-size:.85rem;color:#94a3b8}}
.copy-btn{{background:#3b82f6;color:#fff;border:none;padding:6px 12px;border-radius:8px;cursor:pointer;font-size:.8rem}}
</style>
</head>
<body>
<h1>🌐 hermes 生態系</h1>
<p class='subtitle'>所有工具與服務 — 免費使用・開放原始碼</p>
<div class='grid'>{cards}</div>
<footer>
hermes-marketing · 每日自動行銷推廣<br>
<small>更新時間: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</small>
</footer>
</body>
</html>"""


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    log_data = load_rotation_log()

    if cmd in ("tweet", "all"):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if log_data.get("last_date") != today:
            log_data["last_date"] = today
            log_data["tweet_count"] = 0

        remaining = MAX_TWEETS_PER_DAY - log_data.get("tweet_count", 0)
        want = min(2, max(0, remaining))
        if want == 0:
            log.info(f"⏸ Daily cap reached ({MAX_TWEETS_PER_DAY}); skipping tweets.")
        for i in range(want):
            tweet = pick_fresh_text(log_data)
            if tweet is None:
                log.info("⏸ No non-duplicate tweet available; skipping.")
                break
            # Only bump counters when a real post was attempted (creds present).
            # Otherwise a dry-run (missing X_* secrets) would silently exhaust
            # the daily cap and blocked live posts after tokens were restored.
            posted = post_to_x(tweet)
            if posted:
                record_posted(log_data, tweet)
                log_data["tweet_count"] = log_data.get("tweet_count", 0) + 1
            # Jittered anti-spam spacing only matters between REAL posts; skip it
            # in dry-run (no creds) so manual/CI dry-runs don't idle 25-90s.
            if posted and i < want - 1:
                time.sleep(random.randint(*POST_SPACING_SEC))

    if cmd in ("seo", "all"):
        # Highlight the least-recently-promoted products (no side effects — the
        # HTML page must not consume the daily tweet budget).
        products = sorted(
            PRODUCTS.keys(),
            key=lambda k: log_data.get("last_promoted", {}).get(k, ""),
        )[:2]
        now_iso = datetime.now(timezone.utc).isoformat()
        for k in products:
            log_data.setdefault("last_promoted", {})[k] = now_iso
        html = generate_html(products)
        docs_dir = BASE_DIR / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "index.html").write_text(html, encoding="utf-8")
        log.info("✅ Marketing page generated")

    save_rotation_log(log_data)

    log.info(f"📊 Total tweets so far today: {log_data.get('tweet_count', 0)}")


if __name__ == "__main__":
    main()
