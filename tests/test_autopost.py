#!/usr/bin/env python3
"""
Regression tests for the auto-post scripts. Zero dependencies — runs with bare
`python3 tests/test_autopost.py` (no pytest needed). Exit 0 = all pass.

Each test pins down a bug fixed during the 2026-07 hardening pass, so a future
edit that reintroduces one fails loudly. Tests never touch real state files
(each module's BASE_DIR is redirected to a temp dir) and never hit the network
(dry-run paths only — no credentials are set).
"""
import importlib.util, sys, tempfile, os, re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
_PASS = 0
_FAIL = 0


def load(mod_name: str, base_tmp: Path):
    """Load scripts/<mod_name>.py fresh, with BASE_DIR pointed at a temp dir so
    state-file writes never hit the repo."""
    path = SCRIPTS / f"{mod_name}.py"
    spec = importlib.util.spec_from_file_location(f"_t_{mod_name}", path)
    m = importlib.util.module_from_spec(spec)
    # ensure sibling imports (e.g. `from _discord import notify`) resolve
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(m)
    if hasattr(m, "BASE_DIR"):
        m.BASE_DIR = base_tmp
    return m


def check(name: str, cond: bool, detail: str = ""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ✅ {name}")
    else:
        _FAIL += 1
        print(f"  ❌ {name}{('  — ' + detail) if detail else ''}")


def clear_creds():
    for k in list(os.environ):
        if any(k.startswith(p) for p in
               ("X_API", "X_ACCESS", "LINKEDIN_", "REDDIT_", "BLUESKY_",
                "FB_", "IG_", "THREADS_", "META_AUTOPOST", "DISCORD_")):
            os.environ.pop(k, None)


# ── marketing.py (X) ─────────────────────────────────────────────────────────
def test_marketing(tmp):
    print("marketing.py (X):")
    clear_creds()
    m = load("marketing", tmp)

    # Bug 1: hashtags rendered "#tag1 tag2 tag3" (only first tagged).
    ok_tags = True
    for _ in range(60):
        for key in m.PRODUCTS:
            t = m.build_tweet(key)
            tail = t.split("\n")[-1]
            if tail.strip().startswith("#"):
                # every whitespace-separated token on the hashtag line must start with #
                if any(tok and not tok.startswith("#") for tok in tail.split()):
                    ok_tags = False
    check("hashtags all prefixed with # (no '#a b c' bug)", ok_tags)

    # Bug 2: the empty "✅ {benefit1}" template was removed.
    check("no benefits template with empty placeholders",
          all("{benefit" not in tpl for tpl in m.TWEET_TEMPLATES))

    # Bug 3+5: dedup + daily cap hold across a full day of runs.
    log = {"last_promoted": {}, "tweet_count": 0, "last_date": ""}
    seen, dupes = set(), 0
    for _ in range(6):
        for _ in range(2):
            if log["tweet_count"] >= m.MAX_TWEETS_PER_DAY:
                break
            txt = m.pick_fresh_text(log)
            if txt is None:
                break
            h = m._tweet_hash(txt)
            if h in seen:
                dupes += 1
            seen.add(h)
            m.record_posted(log, txt)
            log["tweet_count"] += 1
    check("no verbatim duplicate tweets in a day", dupes == 0, f"{dupes} dupes")
    check(f"daily cap respected (<= {m.MAX_TWEETS_PER_DAY})",
          log["tweet_count"] <= m.MAX_TWEETS_PER_DAY)
    check("posted_hashes bounded to DEDUP_HISTORY",
          len(log["posted_hashes"]) <= m.DEDUP_HISTORY)

    # Bug 6: post_to_x returns False in dry-run so callers don't burn the cap.
    check("post_to_x dry-run returns False", m.post_to_x("hello") is False)

    # Bug 8 (content): Deal Finder price matches canonical $9.
    check("Deal Finder price is $9", m.PRODUCTS["dealfinder"]["price"] == "$9",
          m.PRODUCTS["dealfinder"]["price"])

    # Curated posts fit X's 280 limit and are unique. X counts every URL as
    # 23 chars (t.co wrapping), so measure EFFECTIVE length, not literal —
    # a post with long UTM URLs can be literally >280 yet valid.
    _url = re.compile(r"https?://\S+")
    def x_len(t):
        return len(_url.sub("x" * 23, t))
    over = [(i, x_len(t)) for i, t in enumerate(m.CURATED_POSTS) if x_len(t) > 280]
    check("curated posts <= 280 effective (t.co) chars", not over, str(over))
    hashes = [m._tweet_hash(t) for t in m.CURATED_POSTS]
    check("curated posts hashes unique", len(set(hashes)) == len(hashes))


# ── linkedin.py / reddit_post.py / bluesky.py dry-run purity ─────────────────
def test_dryrun_no_state(tmp):
    print("dry-run state purity (LinkedIn / Reddit / Bluesky):")
    clear_creds()

    li = load("linkedin", tmp / "li"); (tmp / "li").mkdir(exist_ok=True)
    li.BASE_DIR = tmp / "li"
    li.main()
    check("LinkedIn dry-run writes no state file",
          not (tmp / "li" / "docs" / "linkedin_state.json").exists())
    check("LinkedIn _live() False without tokens", li._live() is False)

    rp = load("reddit_post", tmp / "rp"); (tmp / "rp").mkdir(exist_ok=True)
    rp.BASE_DIR = tmp / "rp"
    rp.main()
    check("Reddit dry-run writes no state file",
          not (tmp / "rp" / "docs" / "reddit_state.json").exists())
    check("Reddit _live() False without creds", rp._live() is False)
    check("all curated Reddit posts target AUTO_SAFE_SUBS only",
          {p["subreddit"] for p in rp.CURATED_POSTS}.issubset(rp.AUTO_SAFE_SUBS))
    check("r/taiwan NOT in AUTO_SAFE_SUBS", "taiwan" not in rp.AUTO_SAFE_SUBS)

    bs = load("bluesky", tmp / "bs"); (tmp / "bs").mkdir(exist_ok=True)
    bs.BASE_DIR = tmp / "bs"
    bs.main()
    check("Bluesky dry-run writes no state file",
          not (tmp / "bs" / "docs" / "bluesky_state.json").exists())
    check("Bluesky _live() False without tokens", bs._live() is False)
    check("Bluesky posts <= 300 chars", all(len(t) <= 300 for t in bs.CURATED_POSTS))
    # facet byte-offset correctness
    for t in bs.CURATED_POSTS:
        f = bs._extract_link_facet(t)
        if f:
            idx = f[0]["index"]
            got = t.encode("utf-8")[idx["byteStart"]:idx["byteEnd"]].decode("utf-8")
            check(f"bluesky facet offsets exact ({got[:30]}...)",
                  got == f[0]["features"][0]["uri"])
            break


# ── preflight.py ─────────────────────────────────────────────────────────────
def test_preflight(tmp):
    print("preflight.py:")
    clear_creds()
    pf = load("preflight", tmp)
    # With no creds, every channel should SKIP and nothing should FAIL.
    pf.RESULTS.clear()
    for fn in (pf.check_x, pf.check_linkedin, pf.check_reddit, pf.check_bluesky,
               pf.check_facebook, pf.check_instagram, pf.check_threads):
        try:
            fn()
        except SystemExit:
            pass
    fails = [n for n, s in pf.RESULTS if s == "FAIL"]
    skips = [n for n, s in pf.RESULTS if s == "SKIP"]
    check("preflight: all channels SKIP with no creds", len(skips) == 7, str(pf.RESULTS))
    check("preflight: zero FAIL with no creds", len(fails) == 0, str(fails))


def main():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_marketing(tmp)
        test_dryrun_no_state(tmp)
        test_preflight(tmp)
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
