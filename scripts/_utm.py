"""Shared UTM tagger — adds channel attribution to slashmantools.us links so
Google Analytics (G-MY95FHB8JG on every tool page) can attribute traffic per
channel. Applied at send time so curated post strings stay clean.

ONLY tags slashmantools.us links:
- Ko-fi shop links don't reliably pass UTM through to conversion tracking, and
  we don't want to risk altering a working checkout URL.
- github.com / youtube.com have their own analytics; UTM is noise there.

Idempotent: a link that already has a query string ('?') is left untouched.
"""
import re

# Match a slashmantools.us URL up to the first whitespace; capture trailing
# sentence punctuation separately so we don't fold it into the URL.
_LINK = re.compile(r"(https://slashmantools\.us(?:/[^\s]*?)?)([.,;!?)）。，、]*)(?=\s|$)")


def tag(text: str, source: str, campaign: str = "hermes") -> str:
    """Append utm params to every bare slashmantools.us link in `text`.
    `source` is the channel, e.g. 'x', 'bluesky', 'linkedin', 'reddit',
    'facebook', 'instagram', 'threads'."""
    def _add(m):
        url, trail = m.group(1), m.group(2)
        if "?" in url or "utm_" in url:
            return m.group(0)
        return f"{url}?utm_source={source}&utm_medium=social&utm_campaign={campaign}{trail}"
    return _LINK.sub(_add, text)
