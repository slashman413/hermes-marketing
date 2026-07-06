# Bluesky auto-posting setup

`scripts/bluesky.py` posts to Bluesky via the **official AT Protocol**
(`com.atproto.repo.createRecord`). Sanctioned automation — Bluesky's ToS
explicitly allows programmatic clients — with the same ban-safety discipline as
the X poster: 2/day cap, verbatim dedup, jittered spacing.

## Turn it on

Set two repository secrets (Settings → Secrets and variables → Actions):

| Secret | What | How to get it |
|--------|------|---------------|
| `BLUESKY_HANDLE`       | Your full handle, e.g. `slashman413.bsky.social` | Your Bluesky profile URL |
| `BLUESKY_APP_PASSWORD` | An **app password**, not your account password | Bluesky → Settings → **App Passwords** → *Add App Password* |

**Always use an app password.** App passwords can be revoked individually and
have scoped permissions; they're the sanctioned way to give a script write
access. Never put your main account password in the secret.

## What gets posted

- 5 curated posts (see `CURATED_POSTS` in `scripts/bluesky.py`), 4 shared with
  the X pool and 1 Bluesky-native (small, honest, no hashtags — matches the
  culture).
- Links are attached as **rich-text facets** so they render as blue clickable
  links, not raw text.

## Ban-safety knobs

- `MAX_POSTS_PER_DAY = 2` (workflow fires 3×/day; the daily cap trims to 2)
- `POST_SPACING_SEC = (25, 90)` jittered pause between posts in the same run
- `DEDUP_HISTORY = 40` verbatim-dedup window
- `CHAR_LIMIT = 300` matches Bluesky's grapheme-cluster limit

## Test before going live

```bash
unset BLUESKY_HANDLE BLUESKY_APP_PASSWORD
python scripts/bluesky.py   # DRY-RUN, prints what would be posted
```
