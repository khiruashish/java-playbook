#!/usr/bin/env python3
"""Parse every ```mermaid block in docs/ with Mermaid's own parser (headless Chromium).
mkdocs --strict does not validate diagram syntax; a broken diagram renders as an error box.

Usage: python3 tools/check-diagrams.py [--mermaid /path/to/mermaid.min.js]"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import importlib.util
spec = importlib.util.spec_from_file_location("bp", ROOT / "tools/build-pdf.py"); bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

def diagrams():
    for f in sorted((ROOT / "docs").rglob("*.md")):
        lines = f.read_text().splitlines()
        i = 0
        while i < len(lines):
            m = re.match(r"^(\s*)```mermaid\s*$", lines[i])
            if m:
                ind = m.group(1); j = i + 1; body = []
                while j < len(lines) and lines[j].strip() != "```":
                    body.append(lines[j][len(ind):]); j += 1
                yield str(f.relative_to(ROOT)), i + 1, "\n".join(body)
                i = j
            i += 1

async def main():
    mermaid = sys.argv[sys.argv.index("--mermaid") + 1] if "--mermaid" in sys.argv else str(bp.DEFAULT_MERMAID)
    ds = list(diagrams())
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.set_content("<html><body></body></html>")
        await pg.add_script_tag(path=mermaid)
        await pg.evaluate("() => mermaid.initialize({startOnLoad:false})")
        bad = []
        for f, line, src in ds:
            err = await pg.evaluate("""async (src) => { try { await mermaid.parse(src); return null; }
                                         catch (e) { return String(e.message || e).split('\\n').slice(0,3).join(' | '); } }""", src)
            if err: bad.append((f, line, err))
        await b.close()
    print(f"diagrams: {len(ds)} · invalid: {len(bad)}")
    for f, line, err in bad: print(f"  {f}:{line}  {err[:160]}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
