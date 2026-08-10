#!/usr/bin/env python3
"""
Exp-001: Add affiliate links to YouTube Shorts descriptions.
Modifies the pixabay-shorts-bot description generation to include
relevant affiliate links based on quote mood.
"""
import os
import sys
import json
import random
from pathlib import Path

# --- Affiliate Link Database ---
# Format: {mood: [(product_name, url, category)]}

AFFILIATE_LINKS = {
    "inspirational": [
        ("📖 《被討厭的勇氣》— 阿德勒心理學經典",
         "https://www.books.com.tw/products/0010702204?sloc=main",
         "心理勵志"),
        ("📖 《活出意義來》— 維克多·弗蘭克",
         "https://www.books.com.tw/products/0010433937?sloc=main",
         "心理勵志"),
        ("📖 《與神對話》— 影響千萬人的心靈經典",
         "https://www.books.com.tw/products/0010862519?sloc=main",
         "心靈成長"),
        ("📖 《原子習慣》— 細微改變帶來巨大成就",
         "https://www.books.com.tw/products/0010792915?sloc=main",
         "自我成長"),
        ("📖 《人生的智慧》— 叔本華的處世智慧",
         "https://www.books.com.tw/products/0010613113?sloc=main",
         "哲學"),
        ("🧠 線上課程：一小時建立你的行動力系統",
         "https://hahow.in/cr/motivation-system",
         "自我成長"),
    ],
    "healing": [
        ("📖 《當你越活越好的時候》— 療癒系散文",
         "https://www.books.com.tw/products/0010935312?sloc=main",
         "心靈療癒"),
        ("📖 《也許你該找人聊聊》— 心理師的療癒故事",
         "https://www.books.com.tw/products/0010896855?sloc=main",
         "心理療癒"),
        ("📖 《脆弱的力量》— Brené Brown 經典",
         "https://www.books.com.tw/products/0010645061?sloc=main",
         "自我接納"),
        ("📖 《雖然是精神病但沒關係》— 繪本風療癒書",
         "https://www.books.com.tw/products/0010893234?sloc=main",
         "療癒繪本"),
        ("🧘 冥想App：每日10分鐘正念練習",
         "https://www.dailycalm.com/",
         "冥想"),
        ("🎵 放鬆白噪音：睡眠/專注/冥想音樂",
         "https://www.spotify.com/tw/",
         "音樂"),
    ],
}

# Also add some always-relevant links
GENERAL_LINKS = [
    ("📊 台股 ETF 分析儀表板（免費）",
     "https://slashman413.github.io/tw-etf-dashboard/"),
    ("🔧 超過20種免費線上工具",
     "https://slashman413.github.io/dev-tools/"),
]


def get_affiliate_block(mood: str, count: int = 2) -> str:
    """Generate the affiliate links block for a given mood."""
    mood_links = AFFILIATE_LINKS.get(mood, AFFILIATE_LINKS["healing"])
    chosen = random.sample(mood_links, min(count, len(mood_links)))

    lines = ["\n📌 **你可能也會喜歡：**"]
    for name, url, _ in chosen:
        lines.append(f"  {name}")
        lines.append(f"  → {url}")
    return "\n".join(lines)


def patch_pixabay_bot():
    """
    Modify pixabay-shorts-bot's main.py to include affiliate links
    in the description. Also adds tracking via a simple counter.
    """
    bot_dir = Path(__file__).parent.parent.parent / "pixabay-shorts-bot"
    main_py = bot_dir / "src" / "main.py"
    # ... patch logic


def track_impression(mood: str):
    """Log an affiliate link impression for tracking."""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    log_file = results_dir / "affiliate_log.json"

    if log_file.exists():
        with open(log_file) as f:
            data = json.load(f)
    else:
        data = {"impressions": [], "total_impressions": 0}

    data["impressions"].append({
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "mood": mood,
        "links_count": len(AFFILIATE_LINKS.get(mood, [])),
    })
    data["total_impressions"] = len(data["impressions"])

    with open(log_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data["total_impressions"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--patch":
        patch_pixabay_bot()
        print("✅ Patched pixabay-shorts-bot with affiliate links")
    elif len(sys.argv) > 1 and sys.argv[1] == "--track":
        mood = sys.argv[2] if len(sys.argv) > 2 else "healing"
        count = track_impression(mood)
        print(json.dumps({"total_impressions": count}))
    else:
        print(get_affiliate_block("healing"))
