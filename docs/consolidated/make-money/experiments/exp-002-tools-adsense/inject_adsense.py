#!/usr/bin/env python3
"""
Exp-002: Inject Google AdSense into all tool site HTML files.
Uses GitHub Actions to auto-deploy.

Usage:
  python inject_adsense.py              # Inject into all tracked repos
  python inject_adsense.py --dry-run    # Preview changes without writing
"""
import os
import re
import sys
import shutil
from pathlib import Path

# AdSense publisher ID - user needs to fill this in after approval
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "ca-pub-XXXXXXXXXXXXXXXX")

# Repos with tool sites that can have ads
TOOL_REPOS = [
    "calculators",
    "pdf-tools",
    "image-compressor",
    "qr-code-generator",
    "color-tools",
    "dev-tools",
    "token-cost-calculator",
    "ai-image-size-calculator",
    "json-regex-devtools",
    "pomodoro-focus-timer",
    "unit-converter",
    "compound-calculator",
    "word-counter",
    "password-generator",
    "llm-calc",
]

# AdSense auto ads script (injected before </head>)
AUTO_ADS_SCRIPT = f'''<!-- Google AdSense -->
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
  crossorigin="anonymous"></script>
'''

# Responsive in-article ad unit
AD_UNIT = '''<!-- ad-unit -->
<ins class="adsbygoogle"
     style="display:block; text-align:center;"
     data-ad-layout="in-article"
     data-ad-format="fluid"
     data-ad-client="CLIENT_ID"
     data-ad-slot="XXXXXXXXXX"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
'''

REPOS_BASE = Path(__file__).parent.parent.parent


def inject_into_html(html_path: Path, dry_run: bool = False) -> bool:
    """Inject AdSense code into an HTML file. Returns True if modified."""
    if not html_path.exists():
        return False

    content = html_path.read_text(encoding="utf-8")

    # Check if already injected
    if "adsbygoogle" in content:
        return False

    # Inject auto ads before </head>
    if "</head>" in content:
        content = content.replace("</head>", f"\n{AUTO_ADS_SCRIPT}</head>")
    else:
        return False

    if not dry_run:
        html_path.write_text(content, encoding="utf-8")
    return True


def process_repo(repo_name: str, dry_run: bool = False) -> list[str]:
    """Process a single tool repo and return list of modified files."""
    repo_dir = REPOS_BASE / repo_name
    if not repo_dir.exists():
        return [f"{repo_name}: directory not found"]

    modified = []
    for html_file in repo_dir.rglob("*.html"):
        if inject_into_html(html_file, dry_run):
            modified.append(str(html_file.relative_to(REPOS_BASE)))

    return modified


def main():
    dry_run = "--dry-run" in sys.argv
    all_modified = []

    for repo in TOOL_REPOS:
        result = process_repo(repo, dry_run)
        all_modified.extend(result)

    if dry_run:
        print(f"[DRY RUN] Would inject AdSense into {len(all_modified)} files:")
    else:
        print(f"Injected AdSense into {len(all_modified)} files:")

    for f in all_modified:
        print(f"  • {f}")


if __name__ == "__main__":
    main()
