#!/usr/bin/env python3
"""
preflight.py — verify that every configured auto-post channel's credentials
actually authenticate, WITHOUT posting anything.

Called after adding secrets via setup_secrets.sh (or the GitHub UI) to catch
typos / wrong scopes / expired tokens immediately instead of waiting for the
next scheduled run. For each channel, calls a lightweight "who am I" endpoint
using the credentials from environment.

Exit code:
  0 — all channels with tokens set authenticated successfully
  1 — at least one channel with tokens set failed to authenticate

Channels without any tokens set are reported as SKIPPED (not a failure).

Usage:
    python scripts/preflight.py

Or via a workflow_dispatch job — see .github/workflows/preflight.yml.
"""
import os, sys, json, urllib.request

RESULTS = []


def _get(url: str, headers: dict | None = None, timeout: int = 15) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(4096).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read(4096).decode("utf-8", "ignore")
        except Exception: pass
        return e.code, body
    except Exception as e:
        return 0, str(e)


def _post(url: str, data: dict, headers: dict | None = None, timeout: int = 15) -> tuple[int, str]:
    body = json.dumps(data).encode("utf-8")
    hdr = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=body, headers=hdr, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(4096).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        b = ""
        try: b = e.read(4096).decode("utf-8", "ignore")
        except Exception: pass
        return e.code, b
    except Exception as e:
        return 0, str(e)


def _report(name: str, status: str, detail: str = "") -> None:
    marker = {"OK": "✅", "FAIL": "❌", "SKIP": "⏭ "}.get(status, "?")
    line = f"{marker} {name:<12} {status}"
    if detail:
        line += f" — {detail}"
    print(line)
    RESULTS.append((name, status))


def check_x():
    token = os.environ.get("X_ACCESS_TOKEN")
    api_key = os.environ.get("X_API_KEY")
    if not (token and api_key and os.environ.get("X_API_SECRET") and os.environ.get("X_ACCESS_TOKEN_SECRET")):
        _report("X/Twitter", "SKIP", "no X_* creds set"); return
    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key, consumer_secret=os.environ["X_API_SECRET"],
            access_token=token, access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
        )
        me = client.get_me()
        _report("X/Twitter", "OK", f"authenticated as @{me.data.username}")
    except Exception as e:
        _report("X/Twitter", "FAIL", str(e)[:150])


def check_linkedin():
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        _report("LinkedIn", "SKIP", "no LINKEDIN_ACCESS_TOKEN"); return
    status, body = _get("https://api.linkedin.com/v2/me",
                        headers={"Authorization": f"Bearer {token}"})
    if status == 200:
        _report("LinkedIn", "OK", "GET /v2/me = 200")
    elif status == 401:
        _report("LinkedIn", "FAIL", "401 — token expired or invalid")
    elif status == 403:
        _report("LinkedIn", "FAIL", "403 — missing w_member_social scope?")
    else:
        _report("LinkedIn", "FAIL", f"HTTP {status}: {body[:100]}")


def check_reddit():
    if not all(os.environ.get(k) for k in ("REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USERNAME","REDDIT_PASSWORD")):
        _report("Reddit", "SKIP", "no REDDIT_* creds"); return
    try:
        import praw
        r = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
            user_agent=os.environ.get("REDDIT_USER_AGENT", "hermes-marketing/1.0"),
        )
        me = r.user.me()
        _report("Reddit", "OK", f"authenticated as u/{me}")
    except Exception as e:
        _report("Reddit", "FAIL", str(e)[:150])


def check_bluesky():
    handle = os.environ.get("BLUESKY_HANDLE")
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD")
    if not (handle and app_pw):
        _report("Bluesky", "SKIP", "no BLUESKY_* creds"); return
    status, body = _post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        {"identifier": handle, "password": app_pw},
    )
    if status == 200:
        try:
            did = json.loads(body).get("did", "")
            _report("Bluesky", "OK", f"session created ({did[:24]}...)")
        except Exception:
            _report("Bluesky", "OK", "session created")
    else:
        _report("Bluesky", "FAIL", f"HTTP {status}: {body[:100]}")


def check_facebook():
    token = os.environ.get("FB_PAGE_TOKEN"); page = os.environ.get("FB_PAGE_ID")
    if not (token and page):
        _report("Facebook", "SKIP", "no FB_PAGE_* creds"); return
    status, body = _get(f"https://graph.facebook.com/v21.0/{page}?fields=name&access_token={token}")
    if status == 200:
        try:
            _report("Facebook", "OK", f"Page: {json.loads(body).get('name','?')}")
        except Exception:
            _report("Facebook", "OK", "page reachable")
    else:
        _report("Facebook", "FAIL", f"HTTP {status}: {body[:120]}")


def check_instagram():
    token = os.environ.get("IG_GRAPH_TOKEN"); ig = os.environ.get("IG_USER_ID")
    if not (token and ig):
        _report("Instagram", "SKIP", "no IG_* creds"); return
    status, body = _get(f"https://graph.facebook.com/v21.0/{ig}?fields=username&access_token={token}")
    if status == 200:
        try:
            _report("Instagram", "OK", f"user: @{json.loads(body).get('username','?')}")
        except Exception:
            _report("Instagram", "OK", "IG user reachable")
    else:
        _report("Instagram", "FAIL", f"HTTP {status}: {body[:120]}")


def check_threads():
    token = os.environ.get("THREADS_TOKEN"); tid = os.environ.get("THREADS_USER_ID")
    if not (token and tid):
        _report("Threads", "SKIP", "no THREADS_* creds"); return
    status, body = _get(f"https://graph.threads.net/v1.0/{tid}?fields=username&access_token={token}")
    if status == 200:
        try:
            _report("Threads", "OK", f"user: @{json.loads(body).get('username','?')}")
        except Exception:
            _report("Threads", "OK", "Threads user reachable")
    else:
        _report("Threads", "FAIL", f"HTTP {status}: {body[:120]}")


def main():
    print("Preflight — verify auto-post channel credentials (no posts made)\n")
    check_x()
    check_linkedin()
    check_reddit()
    check_bluesky()
    check_facebook()
    check_instagram()
    check_threads()

    fails = [n for n, s in RESULTS if s == "FAIL"]
    oks   = [n for n, s in RESULTS if s == "OK"]
    print(f"\n{len(oks)} authenticated, {len(fails)} failed, {len(RESULTS)-len(oks)-len(fails)} skipped.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
