#!/usr/bin/env python3
"""Builds index.html (the textbook's contents page) from the chapter folders.

Every folder = a chapter (dashes become spaces: "Ion-trap" -> "Ion trap").
Every .html inside it = a page; its <title> is used as the name.
Prefix folders/files with numbers (01-, 02-) to control order; the number is hidden.
"""
import html, re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SKIP = {".git", "assets"}

def strip_num(s):
    return re.sub(r"^\d+[-_ ]*", "", s)

def page_title(f):
    m = re.search(r"<title>(.*?)</title>", f.read_text(errors="ignore"), re.S | re.I)
    if m and m.group(1).strip():
        return html.unescape(m.group(1).strip())
    t = strip_num(f.stem).replace("-", " ").replace("_", " ")
    return t[:1].upper() + t[1:]

chapters = []
for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith(".")):
    pages = sorted(d.glob("*.html"))
    if pages:
        chapters.append((strip_num(d.name).replace("-", " "), [(page_title(f), quote(f"{d.name}/{f.name}")) for f in pages]))

toc = []
for i, (name, pages) in enumerate(chapters, 1):
    items = "\n".join(f'      <li><a href="{url}">{html.escape(t)}</a></li>' for t, url in pages)
    toc.append(f'  <section>\n    <h2><span class="n">{i}</span>{html.escape(name)}</h2>\n    <ol>\n{items}\n    </ol>\n  </section>')
total = sum(len(p) for _, p in chapters)

(ROOT / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Physics Textbook</title>
<style>
  :root {{ --bg:#faf8f4; --fg:#1d1d1f; --muted:#6b6b70; --card:#ffffff; --line:#e6e2da; --accent:#2f5bd3; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#121214; --fg:#ececef; --muted:#9a9aa2; --card:#1c1c20; --line:#2c2c33; --accent:#8aa8ff; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font:17px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width:680px; margin:0 auto; padding:40px 16px 64px; }}
  h1 {{ font:600 2rem/1.15 Georgia, serif; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin:0 0 32px; font-size:.95rem; }}
  section {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 18px 10px; margin-bottom:16px; }}
  h2 {{ font:600 1.2rem/1.3 Georgia, serif; margin:0 0 8px; display:flex; align-items:center; gap:10px; }}
  .n {{ font:600 .8rem system-ui; color:var(--accent); border:1.5px solid var(--accent); border-radius:50%; width:26px; height:26px; display:inline-grid; place-items:center; flex:none; }}
  ol {{ margin:0; padding:0; list-style:none; }}
  li a {{ display:block; padding:11px 0; border-top:1px solid var(--line); color:var(--fg); text-decoration:none; }}
  li:first-child a {{ border-top:none; }}
  li a::after {{ content:"›"; float:right; color:var(--muted); }}
  li a:active, li a:hover {{ color:var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>Physics Textbook</h1>
  <p class="sub">{len(chapters)} chapters · {total} pages</p>
{chr(10).join(toc)}
</main>
</body>
</html>
""")
print(f"index.html: {len(chapters)} chapters, {total} pages")
