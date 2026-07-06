# Reddit auto-posting setup

`scripts/reddit_post.py` posts to Reddit via the **official API (praw)**. Reddit
is the highest-risk platform to automate — subreddits enforce local rules and
shadow-ban is quick — so this script is deliberately conservative:

- **Only `r/SideProject`** is on the auto-safe allowlist. Any other subreddit is
  refused, even if you hand-add it to the pool. `r/taiwan` is explicitly NOT
  auto-posted to (its 10%-self-promo rule would get you shadow-banned).
- **Monthly per-subreddit ceiling** (`MIN_DAYS_BETWEEN_POSTS_PER_SUB = 28`).
- **Verbatim dedup** on (subreddit, title, body).
- **Self-post only** (text body). Link-only posts get spam-flagged faster.

## Turn it on

Reddit app: https://www.reddit.com/prefs/apps → **create app** → type = "script".

Set five repository secrets:

| Secret | What |
|--------|------|
| `REDDIT_CLIENT_ID`     | The 14-char id under the app name |
| `REDDIT_CLIENT_SECRET` | The "secret" field |
| `REDDIT_USERNAME`      | Your reddit username |
| `REDDIT_PASSWORD`      | Your reddit password (or use a refresh token flow — see below) |
| `REDDIT_USER_AGENT`    | e.g. `slashman413-hermes/1.0 by u/slashman413` |

That's it. On the next `Daily Marketing` run, `reddit_post.py` will submit one
post to `r/SideProject` (if the 28-day gate is clear) and record it in
`docs/reddit_state.json`. Subsequent runs during the same 28-day window will
log `no eligible post` and skip.

## Account hygiene before switching this on

Reddit will filter/shadow-ban new or low-karma accounts posting external URLs.
Before enabling:

- Account should be **at least 30 days old** with some non-promotional comment
  karma (a few genuine comments in the target sub).
- Skim the r/SideProject rules again; they change occasionally.
- Read your first auto-post's comments — Reddit gives feedback fast, and if the
  post gets reported or downvoted, back off for a few months.

## Adding more subreddits (careful)

To add another subreddit to the auto pool:

1. Read that sub's rules end-to-end (especially about self-promotion cadence).
2. Add its name to `AUTO_SAFE_SUBS` in `scripts/reddit_post.py`.
3. Add a post entry to `CURATED_POSTS` targeting that subreddit.
4. Consider raising `MIN_DAYS_BETWEEN_POSTS_PER_SUB` further if the sub is strict.

Do **not** add `r/taiwan` — post there manually only, and only when you have
been contributing non-promotional comments to the sub.

## Test before going live

```bash
unset REDDIT_CLIENT_ID REDDIT_CLIENT_SECRET REDDIT_USERNAME REDDIT_PASSWORD
python scripts/reddit_post.py     # prints what would be posted
```
