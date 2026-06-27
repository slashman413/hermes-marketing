#!/usr/bin/env python3
"""
hermes-marketing: Automated cross-platform marketing engine.
Promotes all hermes products across channels.
"""
import os, sys, json, random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

# All products with their marketing copy
PRODUCTS = {
    "shortsgen": {
        "name": "ShortsGen Pro",
        "tagline": "AI自動生成YouTube Shorts — 名言語錄 + 背景音樂 + 自動上傳",
        "url": "https://github.com/slashman413/hermes-shortsgen",
        "price": "$29/mo",
        "audience": ["創作者", "YTber", "行銷人"],
        "benefits": ["每日自動產出", "無需剪輯", "自動上傳YouTube"],
    },
    "twse": {
        "name": "TWSE Premium",
        "tagline": "台股即時掃描訊號 — Email/Telegram每日通知",
        "url": "https://github.com/slashman413/hermes-twse-premium",
        "price": "$49/mo",
        "audience": ["投資人", "交易員", "台股散戶"],
        "benefits": ["每日盤中掃描", "技術指標訊號", "Email通知"],
    },
    "dealfinder": {
        "name": "Deal Finder",
        "tagline": "每日Amazon特價 — 聯盟行銷自動比價",
        "url": "https://github.com/slashman413/hermes-deal-finder",
        "price": "免費",
        "audience": ["省錢族", "購物者", "3C愛好者"],
        "benefits": ["每日更新", "多分類", "直接購買"],
    },
    "seo": {
        "name": "SEO Content Engine",
        "tagline": "自動生成SEO優化文章 — GitHub Pages + AdSense",
        "url": "https://github.com/slashman413/hermes-seo-farm",
        "price": "免費/$19 Pro",
        "audience": ["部落客", "站長", "SEO新手"],
        "benefits": ["自動生成", "SEO優化", "免費託管"],
    },
    "tools": {
        "name": "免費線上工具集",
        "tagline": "計算機、PDF、壓縮、QR碼等20+免費工具",
        "url": "https://slashman413.github.io/dev-tools/",
        "price": "完全免費",
        "audience": ["一般使用者", "工程師", "設計師"],
        "benefits": ["免安裝", "瀏覽器執行", "完全免費"],
    },
    "youtube": {
        "name": "Gentle Soul YouTube",
        "tagline": "每日心靈語錄 Shorts — 療癒人心",
        "url": "https://www.youtube.com/@GentleSoul666",
        "price": "免費訂閱",
        "audience": ["心靈成長", "自我提升", "療癒"],
        "benefits": ["每日更新", "名言語錄", "背景音樂"],
    },
    "github": {
        "name": "Free GitHub Tools",
        "tagline": "開放原始碼工具 — 人人都能免費使用",
        "url": "https://github.com/slashman413",
        "price": "免費開源",
        "audience": ["開發者", "工程師"],
        "benefits": ["開放原始碼", "免費使用", "可自行部署"],
    },
}


# Cross-promotion templates
CROSS_PROMOS = {
    "youtube_to_tools": "🎬 喜歡今天的 Shorts嗎？這裡有更多免費工具 👉 {url}",
    "tools_to_youtube": "🔧 用完工具了嗎？來看今天的療癒 Shorts 👉 {url}",
    "github_to_all": "💻 所有工具都是開源的！來看看原始碼 👉 {url}",
    "product_launch": "🚀 全新推出 {name}！{tagline} 👉 {url}",
    "social_proof": "🌟 {name} 已經幫助多位使用者！{tagline} 👉 {url} #{tag}",
}

# Posting schedule per channel
SCHEDULE = {
    "twitter": {
        "posts_per_day": 3,
        "best_times": ["08:00", "12:00", "18:00"],  # UTC
        "format": "{text}\n\n{url}\n\n#{tags}",
    },
    "github_discussions": {
        "posts_per_week": 2,
        "best_days": ["Monday", "Thursday"],
    },
    "reddit": {
        "posts_per_week": 1,
        "subreddits": ["r/taiwan", "r/stock", "r/selfhosted", "r/github"],
    },
}


def generate_tweet() -> str:
    """Generate a promotional tweet."""
    product_key = random.choice(list(PRODUCTS.keys()))
    product = PRODUCTS[product_key]
    
    templates = [
        f"🚀 {product['name']} — {product['tagline']}\n\n{product['url']}",
        f"💡 你知道嗎？{product['name']} 可以幫你{product['benefits'][0]}\n\n{product['url']}",
        f"🔥 {product['name']} 來了！{product['tagline']}\n\n{product['url']}",
        f"🎯 推薦給{product['audience'][0]}：{product['name']}\n{product['tagline']}\n\n{product['url']}",
    ]
    
    return random.choice(templates)


def generate_cross_promotions() -> list[dict]:
    """Generate cross-promotion tasks between products."""
    promos = []
    product_list = list(PRODUCTS.keys())
    
    for _ in range(5):
        src = random.choice(product_list)
        dst = random.choice([p for p in product_list if p != src])
        dst_url = PRODUCTS[dst]["url"]
        
        template_key = random.choice(list(CROSS_PROMOS.keys()))
        template = CROSS_PROMOS[template_key]
        text = template.format(
            name=PRODUCTS[dst]["name"],
            tagline=PRODUCTS[dst]["tagline"],
            url=dst_url,
            tag=random.choice(["opensource", "productivity", "investing", "github"]),
        )
        
        promos.append({
            "from": src,
            "to": dst,
            "text": text,
            "url": dst_url,
            "scheduled": datetime.now().isoformat(),
        })
    
    return promos


def generate_seo_backlinks_html() -> str:
    """Generate an HTML page with cross-links between all products."""
    links_html = ""
    for key, product in PRODUCTS.items():
        links_html += f"""
        <div class="link-card">
            <h3>{product['name']}</h3>
            <p>{product['tagline']}</p>
            <p class="price">💰 {product['price']}</p>
            <a href="{product['url']}" target="_blank">🔗 前往 →</a>
        </div>"""
    
    cross_promos = generate_cross_promotions()
    promo_html = "".join(f'<li>{p["text"]}</li>' for p in cross_promos)
    
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>hermes 生態系 — 所有免費工具與服務</title>
<meta name="description" content="免費線上工具、YouTube Shorts生成器、台股訊號、SEO內容引擎 — 全部開放原始碼">
<style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:-apple-system,sans-serif; background:#0a0a1a; color:#e2e8f0; max-width:900px; margin:auto; padding:20px; }}
    h1 {{ text-align:center; padding:30px 0; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:15px; }}
    .link-card {{ background:#1e293b; border-radius:16px; padding:20px; }}
    .link-card h3 {{ margin-bottom:5px; }}
    .link-card p {{ color:#94a3b8; font-size:0.9rem; }}
    .link-card .price {{ color:#f59e0b; margin:8px 0; }}
    .link-card a {{ color:#3b82f6; text-decoration:none; font-weight:bold; }}
    .promos {{ background:#1e293b; border-radius:16px; padding:20px; margin:20px 0; }}
    .promos li {{ padding:8px 0; border-bottom:1px solid #0f172a; color:#94a3b8; }}
    footer {{ text-align:center; padding:30px; color:#475569; }}
</style>
</head>
<body>
    <h1>🌐 hermes 生態系</h1>
    <p style="text-align:center;color:#64748b;">所有工具與服務一覽 — 免費使用，開放原始碼</p>
    <div class="grid">{links_html}</div>
    <div class="promos">
        <h2>🔄 交叉推廣文案</h2>
        <ul>{promo_html}</ul>
    </div>
    <footer>hermes-marketing · 每日自動更新行銷內容</footer>
</body>
</html>"""


def generate_readme_badges() -> str:
    """Generate badge markdown for all repos."""
    badges = []
    for key, product in PRODUCTS.items():
        badges.append(f"[![{product['name']}](https://img.shields.io/badge/{key}-{product['price'].replace(' ','%20')}-blue)]({product['url']})")
    return "\n".join(badges)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if cmd in ("tweet", "all"):
        tweet = generate_tweet()
        print(f"🐦 Tweet: {tweet[:200]}")
    
    if cmd in ("promo", "all"):
        promos = generate_cross_promotions()
        for p in promos[:3]:
            print(f"🔄 {p['from']} → {p['to']}: {p['text'][:100]}...")
    
    if cmd in ("seo", "all"):
        html = generate_seo_backlinks_html()
        docs_dir = BASE_DIR / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"✅ SEO backlinks page generated")
    
    if cmd in ("badges", "all"):
        print(f"🏷️ Badges:\n{generate_readme_badges()}")
    
    if cmd in ("report", "all"):
        print(f"\n📊 行銷日報 ({datetime.now().strftime('%Y-%m-%d')})")
        print(f"  產品數: {len(PRODUCTS)}")
        print(f"  行銷管道: {len(SCHEDULE)}")
        print(f"  交叉推廣組合: {len(PRODUCTS)**2 - len(PRODUCTS)}")


if __name__ == "__main__":
    main()
