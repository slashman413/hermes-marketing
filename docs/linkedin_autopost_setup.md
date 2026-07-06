# LinkedIn auto-posting setup

`scripts/linkedin.py` posts to LinkedIn via the **official v2 UGC Posts API** —
sanctioned, low ban-risk, and rate-limited to ≤2 posts/week by a built-in
cadence gate. It stays **dormant** until you add the secrets below.

## Turn it on

Set two repository secrets (Settings → Secrets and variables → Actions):

| Secret | What | How to get it |
|--------|------|---------------|
| `LINKEDIN_ACCESS_TOKEN` | OAuth 2.0 bearer token with `w_member_social` (personal) or `w_organization_social` (company page) scope | LinkedIn developer app → OAuth flow → 3-legged token |
| `LINKEDIN_ACTOR_URN`    | Who the post is authored as | `urn:li:person:{your_id}` (get from `GET /v2/me` → `id`) or `urn:li:organization:{page_id}` |

That's it. On the next `Daily Marketing` run, `linkedin.py` will post one of the
curated posts and record it in `docs/linkedin_state.json`.

## Cadence & ban-safety

- **Weekly ceiling**: won't post more often than every 3 days (`MIN_DAYS_BETWEEN_POSTS`).
- **Verbatim dedup**: every post hashed; the same text never goes out twice
  within the last 30 posts.
- **Official API only**: no scraping, no session replay.
- **`continue-on-error: true`** on the workflow step — if LinkedIn ever errors,
  the X pipeline keeps working.

## Token expiry

LinkedIn access tokens expire in **60 days** (default). Rotate before that or
posting will silently return 401 (logged as FAILED in the Action log). Consider
using a refresh-token flow if you want it truly hands-off long-term.

## Test before going live

The script auto-detects missing tokens and prints a `DRY-RUN` preview. To sanity
check locally:

```bash
unset LINKEDIN_ACCESS_TOKEN LINKEDIN_ACTOR_URN
python scripts/linkedin.py     # prints what would be posted
```
