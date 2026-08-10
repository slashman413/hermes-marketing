#!/usr/bin/env python3
"""
AdSense Injector — 批量注入 Google AdSense 到所有工具站 repo
"""
import os, sys, subprocess, shutil
from pathlib import Path

WORK_DIR = Path("/d/Hermes-Agent")

TOOL_REPOS = [
    "calculators", "pdf-tools", "image-compressor", "qr-code-generator",
    "color-tools", "dev-tools", "token-cost-calculator", "ai-image-size-calculator",
    "json-regex-devtools", "pomodoro-focus-timer", "unit-converter",
    "compound-calculator", "word-counter", "password-generator", "llm-calc",
    "ai-prompt-library", "ai-image-size-calculator",
]

ADSENSE_SCRIPT = '''<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
'''

AD_PLACEHOLDER = '''<div class="adsense-placeholder" style="text-align:center;padding:20px;margin:20px 0;background:#1e293b;border-radius:12px;border:2px dashed #334155;color:#475569;font-size:0.9rem;">📢 AdSense 廣告將在此顯示（核准後自動啟用）</div>'''


def process_repo(repo_name: str) -> bool:
    """Process a single tool repo. Returns True if modified."""
    repo_dir = WORK_DIR / repo_name
    
    # Clone if not exists
    if not repo_dir.exists():
        r = subprocess.run(
            ["git", "clone", f"git@github.com:slashman413/{repo_name}.git", str(repo_dir)],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            print(f"  ❌ Clone failed: {r.stderr[:100]}")
            return False
    
    # Find index.html
    html_files = list(repo_dir.rglob("index.html"))
    if not html_files:
        print(f"  ⚠️  No index.html found in {repo_name}")
        return False
    
    modified = False
    for html_path in html_files:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        
        # Skip if already done
        if "adsbygoogle" in content:
            print(f"  ⏭️  Already has AdSense: {html_path.relative_to(WORK_DIR)}")
            continue
        
        # Inject script before </head>
        if "</head>" in content:
            content = content.replace("</head>", f"\n{ADSENSE_SCRIPT}</head>")
        else:
            continue
        
        # Inject placeholder before </body>
        if "</body>" in content:
            content = content.replace("</body>", f"\n{AD_PLACEHOLDER}\n</body>")
        
        html_path.write_text(content, encoding="utf-8")
        print(f"  ✅ Injected: {html_path.relative_to(WORK_DIR)}")
        modified = True
    
    if modified:
        r = subprocess.run(
            ["git", "add", "-A"], cwd=str(repo_dir), capture_output=True, text=True, timeout=10
        )
        r = subprocess.run(
            ["git", "commit", "-m", "Add Google AdSense placeholder + auto ads\n\nauthor: hermes-agent-deepseek-v4-flash"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            print(f"  📝 Committed: {repo_name}")
            r = subprocess.run(
                ["git", "push"], cwd=str(repo_dir), capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0:
                print(f"  🚀 Pushed: {repo_name}")
            else:
                print(f"  ⚠️  Push failed: {r.stderr[:100]}")
        else:
            if "nothing to commit" in r.stderr or "nothing to commit" in r.stdout:
                print(f"  ⏭️  Nothing to commit for {repo_name}")
    
    return True


def main():
    print("🚀 Starting AdSense injection...")
    success = 0
    for repo in TOOL_REPOS:
        print(f"\n📦 {repo}:")
        try:
            if process_repo(repo):
                success += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n✅ Done: {success}/{len(TOOL_REPOS)} repos processed")


if __name__ == "__main__":
    main()
