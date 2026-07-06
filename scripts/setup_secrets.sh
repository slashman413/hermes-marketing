#!/usr/bin/env bash
# setup_secrets.sh — interactive one-shot: set GitHub Actions secrets for one
# auto-post channel at a time via the gh CLI. Turns the "click 6 things in
# the GitHub UI" workflow into a 2-minute paste job.
#
# Usage:
#     ./scripts/setup_secrets.sh bluesky      # 2 secrets
#     ./scripts/setup_secrets.sh linkedin     # 2 secrets
#     ./scripts/setup_secrets.sh reddit       # 5 secrets
#     ./scripts/setup_secrets.sh meta         # 6 secrets + META_AUTOPOST toggle
#     ./scripts/setup_secrets.sh check        # `gh secret list` for this repo
#
# Requirements:
#   - `gh` CLI installed + authenticated (`gh auth status`)
#   - Run from a checkout of the target repo (hermes-marketing or slashman413.github.io)
#
# Every prompt lets you paste the secret value. Empty input = skip that secret.
# The script never echoes secret values back to the terminal.

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh CLI not installed. https://cli.github.com/" >&2; exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "❌ gh not authenticated. Run: gh auth login" >&2; exit 1
fi

# Ensure we're in a git repo with a github.com remote.
if ! git remote get-url origin 2>/dev/null | grep -q github.com; then
  echo "❌ Run this from a git checkout with a github.com origin remote." >&2; exit 1
fi

REPO=$(git remote get-url origin | sed -E 's#(git@github.com:|https://[^/]+/)##; s#\.git$##')
echo "Target repo: $REPO"
echo

set_secret() {
  local name="$1" desc="$2"
  printf "  %-24s (%s)\n  paste value (or empty to skip): " "$name" "$desc"
  IFS= read -r -s value; echo
  if [ -z "$value" ]; then echo "    ↷ skipped"; return; fi
  printf '%s' "$value" | gh secret set "$name" --repo "$REPO"
  echo "    ✅ set"
}

case "${1:-}" in
  bluesky)
    echo "▶ Bluesky (5-min setup, lowest risk)"
    echo "  Get an app password: Bluesky Settings → App Passwords → Add App Password"
    echo
    set_secret BLUESKY_HANDLE       "e.g. slashman413.bsky.social"
    set_secret BLUESKY_APP_PASSWORD "app password (NOT your account password)"
    ;;
  linkedin)
    echo "▶ LinkedIn (~15 min)"
    echo "  Get a token: developer.linkedin.com → app → OAuth → w_member_social"
    echo "  Actor URN: GET /v2/me → 'urn:li:person:{id}'"
    echo
    set_secret LINKEDIN_ACCESS_TOKEN "OAuth 2.0 bearer token (60d expiry)"
    set_secret LINKEDIN_ACTOR_URN    "urn:li:person:{id} or urn:li:organization:{id}"
    ;;
  reddit)
    echo "▶ Reddit (script app; account should be ≥30 days old)"
    echo "  Create app: reddit.com/prefs/apps → 'create app' → type=script"
    echo
    set_secret REDDIT_CLIENT_ID     "14-char id shown under the app name"
    set_secret REDDIT_CLIENT_SECRET "the 'secret' field"
    set_secret REDDIT_USERNAME      "reddit username"
    set_secret REDDIT_PASSWORD      "reddit password"
    set_secret REDDIT_USER_AGENT    "e.g. 'slashman413-hermes/1.0 by u/slashman413'"
    ;;
  meta)
    echo "▶ Meta (Facebook Page + Instagram + Threads)"
    echo "  Get tokens: developers.facebook.com → app (Business type)"
    echo "  Recommend testing with META_AUTOPOST=dry BEFORE setting to 1."
    echo
    set_secret FB_PAGE_ID       "your Facebook Page id"
    set_secret FB_PAGE_TOKEN    "long-lived Page token (pages_manage_posts)"
    set_secret IG_USER_ID       "IG business user id (from /page-id?fields=instagram_business_account)"
    set_secret IG_GRAPH_TOKEN   "token with instagram_content_publish scope"
    set_secret THREADS_USER_ID  "Threads user id"
    set_secret THREADS_TOKEN    "long-lived Threads token (threads_content_publish)"
    echo
    echo "  Enable flag — set to 'dry' first to smoke-test the pipeline, then '1' to go live:"
    set_secret META_AUTOPOST    "'1' = live post · 'dry' = simulate · empty = off (default)"
    ;;
  check)
    gh secret list --repo "$REPO"
    ;;
  ""|-h|--help)
    echo "usage: $0 {bluesky|linkedin|reddit|meta|check}" >&2
    echo "see docs/AUTOPOST_MASTER_SETUP.md for the full guide"
    exit 1
    ;;
  *)
    echo "unknown channel: $1" >&2; exit 1
    ;;
esac

echo
echo "Done. Trigger the next scheduled run manually to test:"
echo "  gh workflow run 'Daily Marketing' --repo $REPO"
echo "or via the Actions tab → Run workflow."
