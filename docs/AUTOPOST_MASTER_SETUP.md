# Master auto-post setup — activate "all posts automatic"

Every promotion channel below is **automated in code**, ban-safe by design, and
runs from GitHub Actions. Only **X is live today**; the rest are dormant until
you add their credentials.

Enable a channel by adding its GitHub Secrets (Settings → Secrets and variables
→ Actions). Skip any channel you don't want — they no-op cleanly without creds.

## Channels at a glance

| Channel | Status | Script | Setup doc | Cadence | Ban-risk |
|---------|--------|--------|-----------|---------|----------|
| X / Twitter        | ✅ **Live** | `scripts/marketing.py`  | (already live) | 3×/day, cap 6/day, dedup | Low |
| LinkedIn           | 🔧 Dormant | `scripts/linkedin.py`   | [linkedin_autopost_setup.md](linkedin_autopost_setup.md)  | ~2×/week, 3-day gate      | Low |
| Reddit             | 🔧 Dormant | `scripts/reddit_post.py`| [reddit_autopost_setup.md](reddit_autopost_setup.md)      | ~1×/month per subreddit   | **Medium** (r/SideProject only by default) |
| Bluesky            | 🔧 Dormant | `scripts/bluesky.py`    | [bluesky_autopost_setup.md](bluesky_autopost_setup.md)    | 2×/day cap, jittered      | Low |
| Facebook Page      | 🔧 Dormant | `slashman413.github.io/social_promo.py` | [meta_autopost_setup.md](../../slashman413.github.io/docs/meta_autopost_setup.md) | 2×/day       | Low (Graph API) |
| Instagram          | 🔧 Dormant | same as above           | same as above                                             | 2×/day                    | Low |
| Threads            | 🔧 Dormant | same as above           | same as above                                             | 2×/day                    | Low |

## Recommended activation order (easiest → riskiest)

Do these one at a time. After each, run the workflow manually (Actions → Daily
Marketing → *Run workflow*) and check the Action log before moving on.

### 1. Bluesky (5 minutes, lowest risk)

1. Bluesky Settings → **App Passwords** → *Add App Password* — name it "hermes"
2. Add secrets: `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`
3. Run the workflow. Check the `[bluesky] posted (...)` line in the log.

### 2. LinkedIn (~15 minutes)

1. https://www.linkedin.com/developers/apps → Create app → request scope
   `w_member_social` (or `w_organization_social` for a company page)
2. Get an OAuth 2.0 access token; note the actor URN from `GET /v2/me`
3. Add secrets: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ACTOR_URN`
4. Run the workflow. Verify on your LinkedIn profile.
5. **Set a calendar reminder for 55 days from now** to rotate the token
   (they expire at 60 days).

### 3. Meta — Facebook + Instagram + Threads (~30 minutes, most setup)

1. https://developers.facebook.com/apps → Create app (Business type)
2. Follow the [full guide](../../slashman413.github.io/docs/meta_autopost_setup.md) for
   `FB_PAGE_*`, `IG_USER_ID`, `IG_GRAPH_TOKEN`, `THREADS_USER_ID`, `THREADS_TOKEN`
3. **Test in dry-run first**: set `META_AUTOPOST=dry` and run the workflow.
   The log will show `[fb:dry]` `[ig:dry]` `[threads:dry]` lines — verify the
   captions/images before going live.
4. Then set `META_AUTOPOST=1` to go live.

### 4. Reddit (last — highest care needed)

1. **Account hygiene check first**: your Reddit account should be ≥30 days
   old with a few genuine (non-promotional) comments in r/SideProject.
2. https://www.reddit.com/prefs/apps → Create app → type **script**
3. Add secrets per the [Reddit setup guide](reddit_autopost_setup.md).
4. Run once, then watch the r/SideProject submission for downvotes/reports. If
   the first post gets flagged, remove the Reddit secrets and revisit in a few
   months. Do **not** add other subreddits to `AUTO_SAFE_SUBS` without reading
   their rules end-to-end.

## Ban-safety guarantees (built into every channel)

- **Official APIs only.** No browser session replay, no scraping.
- **Verbatim dedup.** The same post never goes out twice within the platform's
  dedup window.
- **Daily/weekly caps.** Below every platform's free-tier ceiling.
- **`continue-on-error` on every step.** One channel failing never breaks another.
- **Dry-run when creds missing.** Wiring is testable without going live.

## After activation: monitoring

- Every Daily Marketing failure DMs your Discord webhook (`DISCORD_WEBHOOK`).
- Each platform's state file lives in `hermes-marketing/docs/`
  (`rotation.json`, `linkedin_state.json`, `reddit_state.json`,
  `bluesky_state.json`) — commits to those files after each run are the audit
  trail of what got posted when.

## Rotating credentials

Add a calendar reminder to rotate any short-lived token before it expires:

- **LinkedIn**: 60 days
- **Meta Page/IG/Threads**: 60 days (extendable to long-lived)
- **X**: no expiry, but rotate yearly for hygiene
- **Bluesky app password**: no expiry, but revoke any leaked one immediately
- **Reddit**: script tokens don't expire; rotate if compromised
