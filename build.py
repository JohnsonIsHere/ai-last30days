#!/usr/bin/env python3
"""Build the ai-last30days site from src/ bodies plus issues.json.

Each file in src/ is an *artifact body*: the HTML exactly as published to a
Claude artifact, which carries its own <title> and <style> but no doctype,
<head> or <body> wrapper, because the artifact platform supplies those at
publish time. GitHub Pages does not, so this script adds them.

Writes:
  index.html                 the newest issue, so the root URL is always readable
  issues/<slug>.html         a permanent copy of every issue
  issues/index.html          the archive listing

Run:  python3 build.py
"""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
ISSUES = ROOT / "issues"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
<style>
  :root {{ color-scheme: light dark; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; }}
  [hidden] {{ display: none !important; }}
</style>
"""

# Injected into the Pages build only. The artifact copy stays free of it,
# because these relative links do not resolve inside an artifact.
NAV_CSS = """
<style>
  .issuenav {
    font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace;
    font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding-block: 14px 0; display: flex; gap: 14px; align-items: baseline;
  }
  .issuenav a { color: var(--ink-faint); text-decoration: none; }
  .issuenav a:hover { color: var(--accent); text-decoration: underline; }
  .issuenav .sep { color: var(--rule); }
</style>
"""

NAV_HTML = '<div class="issuenav"><a href="{archive}">All issues</a><span class="sep">/</span><span>{window}</span></div>'

SHEET_OPEN = '<div class="sheet">'


def build_issue(meta: dict, archive_href: str) -> str:
    body = (SRC / f"{meta['slug']}.html").read_text(encoding="utf-8")

    title_match = re.search(r"<title>(.*?)</title>", body, re.S)
    title = title_match.group(1).strip() if title_match else meta["title"]

    head = HEAD.format(
        title=html.escape(title, quote=True),
        description=html.escape(meta["summary"], quote=True),
    )

    if SHEET_OPEN not in body:
        raise SystemExit(f"{meta['slug']}: no '{SHEET_OPEN}' wrapper found in source")

    nav = NAV_HTML.format(archive=archive_href, window=html.escape(meta["window"]))
    body = body.replace(SHEET_OPEN, f"{SHEET_OPEN}\n  {nav}", 1)

    # Close </head> and open <body> right after the page's own <style> block.
    marker = "</style>\n\n" + SHEET_OPEN
    if marker not in body:
        raise SystemExit(f"{meta['slug']}: could not locate the style/sheet boundary")
    body = body.replace(marker, "</style>\n</head>\n<body>\n\n" + SHEET_OPEN, 1)

    return head + NAV_CSS + body + "\n</body>\n</html>\n"


def build_archive(manifest: dict) -> str:
    rows = []
    for i, meta in enumerate(manifest["issues"]):
        current = ' <span class="current">current</span>' if i == 0 else ""
        rows.append(
            f"""      <a class="row" href="{meta['slug']}.html">
        <span class="when">{html.escape(meta['window'])}</span>
        <span class="main">
          <span class="t">{html.escape(meta['title'])}{current}</span>
          <span class="s">{html.escape(meta['summary'])}</span>
          <span class="topics">{html.escape(meta['topics'])}</span>
        </span>
      </a>"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Monthly AI briefings: {html.escape(manifest['tagline'])}">
<title>last30days issues</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600&family=Archivo:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {{
    --paper:#e8eae6; --surface:#f4f5f2; --ink:#171a17; --ink-soft:#4e554e;
    --ink-faint:#7d847c; --rule:#c9ccc4; --rule-soft:#d9dcd4; --accent:#22408c;
    color-scheme: light;
    padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px);
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --paper:#14171a; --surface:#1c2024; --ink:#e6e8e3; --ink-soft:#a8afa7;
      --ink-faint:#777f78; --rule:#343a3e; --rule-soft:#272c30; --accent:#8fabef;
      color-scheme: dark;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper:#14171a; --surface:#1c2024; --ink:#e6e8e3; --ink-soft:#a8afa7;
    --ink-faint:#777f78; --rule:#343a3e; --rule-soft:#272c30; --accent:#8fabef;
    color-scheme: dark;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--paper); color: var(--ink);
    font-family: "Archivo", -apple-system, "Segoe UI", Roboto, sans-serif;
    font-size: 16.5px; line-height: 1.6;
  }}
  .sheet {{ max-width: 820px; margin: 0 auto; padding-inline: 20px; padding-block: 48px 72px; }}
  .wire {{
    font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace;
    font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--ink-faint); display: flex; gap: 12px; align-items: center;
  }}
  .wire b {{ color: var(--accent); font-weight: 500; }}
  .wire .dash {{ flex: 1; height: 1px; background: var(--rule); }}
  h1 {{
    font-family: "Newsreader", Georgia, serif; font-weight: 600;
    font-size: clamp(2.2rem, 8vw, 3.2rem); line-height: 1; letter-spacing: -0.02em;
    margin: 18px 0 0;
  }}
  .tagline {{ color: var(--ink-soft); margin: 12px 0 0; max-width: 46ch; }}
  .list {{ margin-top: 38px; border-top: 2px solid var(--ink); }}
  a.row {{
    display: grid; grid-template-columns: 11rem minmax(0, 1fr); gap: 20px;
    padding: 20px 0; border-bottom: 1px solid var(--rule-soft);
    text-decoration: none; color: var(--ink);
  }}
  @media (max-width: 620px) {{ a.row {{ grid-template-columns: 1fr; gap: 6px; }} }}
  a.row:hover .t {{ color: var(--accent); }}
  .when {{
    font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace;
    font-size: 0.72rem; color: var(--ink-faint); padding-top: 0.35em;
    font-variant-numeric: tabular-nums;
  }}
  .t {{
    font-family: "Newsreader", Georgia, serif; font-size: 1.42rem; font-weight: 600;
    display: block; line-height: 1.15;
  }}
  .current {{
    font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace;
    font-size: 0.56rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--accent); vertical-align: 0.35em; margin-left: 6px;
  }}
  .s {{ display: block; color: var(--ink-soft); font-size: 0.95rem; margin-top: 7px; }}
  .topics {{
    display: block; margin-top: 9px;
    font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace;
    font-size: 0.64rem; letter-spacing: 0.06em; color: var(--ink-faint);
  }}
  footer {{
    margin-top: 40px; padding-top: 18px; border-top: 1px solid var(--rule);
    font-size: 0.86rem; color: var(--ink-soft);
  }}
  footer a {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="sheet">
  <div class="wire"><b>last30days</b><span>archive</span><span class="dash"></span><span>{len(manifest['issues'])} issue{'s' if len(manifest['issues']) != 1 else ''}</span></div>
  <h1>Issues</h1>
  <p class="tagline">{html.escape(manifest['tagline'])}, gathered over a rolling thirty-day window and written up once a month.</p>
  <div class="list">
{chr(10).join(rows)}
  </div>
  <footer>Each issue is a permanent link and never changes after publication. The <a href="../">front page</a> always shows the current one.</footer>
</div>
</body>
</html>
"""


def main() -> None:
    manifest = json.loads((ROOT / "issues.json").read_text(encoding="utf-8"))
    issues = manifest["issues"]
    if not issues:
        raise SystemExit("issues.json lists no issues")

    ISSUES.mkdir(exist_ok=True)

    for meta in issues:
        out = ISSUES / f"{meta['slug']}.html"
        out.write_text(build_issue(meta, archive_href="./"), encoding="utf-8")
        print(f"  issues/{out.name}")

    # Root is the newest issue, so the shared front-page link is always a brief
    # rather than a directory listing.
    latest = issues[0]
    (ROOT / "index.html").write_text(
        build_issue(latest, archive_href="issues/"), encoding="utf-8"
    )
    print(f"  index.html  -> {latest['slug']}")

    (ISSUES / "index.html").write_text(build_archive(manifest), encoding="utf-8")
    print("  issues/index.html")


if __name__ == "__main__":
    main()
