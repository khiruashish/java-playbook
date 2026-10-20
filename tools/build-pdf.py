#!/usr/bin/env python3
"""Render the built MkDocs site into one print-ready PDF.

Usage:
    mkdocs build
    python3 tools/build-pdf.py [--out handbook.pdf] [--mermaid /path/to/mermaid.min.js]

How it works:
  * serves site/ locally and prints every nav page with headless Chromium (Playwright),
    so Mermaid diagrams render exactly as on the website;
  * Material fetches Mermaid from unpkg — the request is intercepted and served from a
    local mermaid.min.js, so the build works offline;
  * expands collapsible answers and shows every content tab, so nothing is hidden on paper;
  * wraps long code lines instead of letting them run off the page;
  * prepends a cover and a table of contents with real page numbers, adds PDF bookmarks,
    and stamps a footer (chapter title, page number) on every page.

Requires: playwright (with Chromium), pypdf, reportlab.
"""
import argparse, asyncio, functools, html, http.server, io, pathlib, re, socketserver, sys, threading

from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PORT = 8765
_REL = "lib/node_modules/@mermaid-js/mermaid-cli/node_modules/mermaid/dist/mermaid.min.js"
_CANDIDATES = [pathlib.Path.home() / ".npm-global" / _REL, pathlib.Path("/home/claude/.npm-global") / _REL,
               pathlib.Path("/usr/local") / _REL, pathlib.Path("/usr") / _REL, ROOT / "node_modules/mermaid/dist/mermaid.min.js"]
DEFAULT_MERMAID = next((c for c in _CANDIDATES if c.exists()), _CANDIDATES[0])   # or: npm i mermaid@11
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PRINT_CSS = """
@media print {
  .md-typeset pre > code, .md-typeset pre { white-space: pre-wrap !important; word-break: break-word; }
  .md-typeset pre > code { font-size: .62rem !important; }
  .md-typeset table:not([class]) { font-size: .62rem !important; }
  .md-typeset h2 { break-before: auto; break-after: avoid; }
  .md-typeset h3, .md-typeset h4 { break-after: avoid; }
  .md-typeset .mermaid, .admonition, details { break-inside: avoid-page; }
  .md-typeset .highlight .filename { display: block; break-after: avoid; }
  .md-typeset .tabbed-labels { display: none !important; }
  .md-typeset .tabbed-content > .tabbed-block { display: block !important; }
  .print-tab-label { font-weight: 700; font-size: .7rem; color: #3f51b5; margin: .8em 0 .2em; break-after: avoid; }
  .md-typeset .tabbed-block { break-inside: avoid-page; }
  .md-source-file, .md-content__button { display: none !important; }
}
"""

EXPAND_JS = """() => {
  document.querySelectorAll('details').forEach(d => d.open = true);
  // Keep short code blocks and tables whole; let long ones flow across pages instead of leaving a gap.
  document.querySelectorAll('.md-typeset .highlight').forEach(h => {
    const pre = h.querySelector('pre'); if (!pre) return;
    const long = pre.textContent.split('\\n').length > 45;
    h.style.breakInside = long ? 'auto' : 'avoid-page';
    pre.style.breakInside = long ? 'auto' : 'avoid-page';
  });
  document.querySelectorAll('.md-typeset table').forEach(tb => {
    tb.style.breakInside = tb.rows.length > 20 ? 'auto' : 'avoid-page';
  });
  document.querySelectorAll('.tabbed-set').forEach(set => {
    const labels = [...set.querySelectorAll(':scope > .tabbed-labels > label')].map(l => l.textContent.trim());
    [...set.querySelectorAll(':scope > .tabbed-content > .tabbed-block')].forEach((block, i) => {
      if (labels[i] && !block.querySelector(':scope > .print-tab-label')) {
        const p = document.createElement('div'); p.className = 'print-tab-label'; p.textContent = labels[i];
        block.prepend(p);            // inside the panel: travels with its code, never reordered or orphaned
      }
    });
  });
}"""

MERMAID_DONE_JS = """() => document.querySelectorAll('pre.mermaid').length === 0 &&
  [...document.querySelectorAll('div.mermaid')].every(e => e.getBoundingClientRect().height > 0)"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(directory):
    handler = functools.partial(_Quiet, directory=str(directory))
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def nav_pages():
    """(part, path) in nav order, read from mkdocs.yml without evaluating its python tags."""
    text = (ROOT / "mkdocs.yml").read_text().split("\nnav:", 1)[1]
    pages, part = [], None
    for line in text.splitlines():
        m = re.match(r"^  - (\w[^:]*):\s*$", line)
        if m: part = m.group(1).strip(); continue
        for path in re.findall(r"([\w./-]+\.md)", line):
            pages.append((part or "Home", path))
    return pages


def url_for(path):
    if path == "index.md": return "/"
    if path.endswith("/index.md"): return "/" + path[: -len("index.md")]
    return "/" + path[:-3] + "/"


async def render_pages(pages, mermaid_path, workdir):
    out = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(color_scheme="light")

        async def route(r):
            u = r.request.url
            if "mermaid" in u and u.endswith(".js"):
                await r.fulfill(path=str(mermaid_path), content_type="application/javascript")
            elif u.startswith(f"http://127.0.0.1:{PORT}"):
                await r.continue_()
            else:
                await r.abort()                      # fonts/CDNs: offline, fall back to system fonts
        await ctx.route("**/*", route)

        page = await ctx.new_page()
        for n, (part, path) in enumerate(pages):
            await page.goto(f"http://127.0.0.1:{PORT}{url_for(path)}", wait_until="load")
            try:
                await page.wait_for_function(MERMAID_DONE_JS, timeout=20000)
            except Exception:
                print(f"  ! diagrams not fully rendered on {path}", file=sys.stderr)
            await page.add_style_tag(content=PRINT_CSS)
            await page.evaluate(EXPAND_JS)
            title = (await page.evaluate("() => document.querySelector('.md-content h1')?.textContent || document.title")).strip()
            title = re.sub(r"\s*¶\s*$", "", title)
            pdf = workdir / f"{n:03d}.pdf"
            await page.pdf(path=str(pdf), format="A4", print_background=True,
                           margin={"top": "16mm", "bottom": "20mm", "left": "14mm", "right": "14mm"})
            out.append((part, path, title, pdf))
            print(f"  {n+1:>2}/{len(pages)}  {len(PdfReader(pdf).pages):>3} pp  {title}")
        await browser.close()
    return out


async def render_html(html_text, target):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pg = await browser.new_page()
        await pg.set_content(html_text, wait_until="load")
        await pg.pdf(path=str(target), format="A4", print_background=True,
                     margin={"top": "20mm", "bottom": "20mm", "left": "18mm", "right": "18mm"})
        await browser.close()


def cover_html():
    return """<html><body style="font-family:'DejaVu Sans',sans-serif;margin:0">
    <div style="height:250mm;display:flex;flex-direction:column;justify-content:center;padding:0 10mm">
      <div style="font-size:13pt;color:#3f51b5;letter-spacing:2px">JAVA 8 → 26</div>
      <h1 style="font-size:34pt;margin:6mm 0 4mm;line-height:1.15">Modern Java<br>Enterprise Handbook</h1>
      <div style="font-size:13pt;color:#555;max-width:140mm;line-height:1.5">
        The language, collections, concurrency, runtime and testing — organised by concept,
        traced from Java 8 to the current state on Java 25 LTS.</div>
      <div style="margin-top:22mm;font-size:10.5pt;color:#777;line-height:1.7">
        44 chapters · 6 appendices<br>Baseline: Java 25 LTS · Java 26 · September 2026</div>
    </div></body></html>"""


def toc_html(entries):
    rows, current = [], None
    for part, title, page in entries:
        if part != current:
            rows.append(f'<tr><td colspan="2" style="padding-top:5mm;font-weight:700;color:#3f51b5;'
                        f'font-size:11pt">{html.escape(part)}</td></tr>')
            current = part
        rows.append(f'<tr><td style="padding:1.2mm 0 1.2mm 4mm">{html.escape(title)}</td>'
                    f'<td style="text-align:right;color:#555">{page}</td></tr>')
    return ("<html><body style=\"font-family:'DejaVu Sans',sans-serif;font-size:10pt\">"
            "<h1 style='font-size:20pt'>Contents</h1><table style='width:100%;border-collapse:collapse'>"
            + "".join(rows) + "</table></body></html>")


def stamp_footers(writer, labels, first_numbered):
    """Draw every footer on ONE multi-page canvas so the font is embedded once, then overlay."""
    pdfmetrics.registerFont(TTFont("DejaVu", FONT))
    buf = io.BytesIO(); c = None
    for i, page in enumerate(writer.pages):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        if c is None: c = canvas.Canvas(buf, pagesize=(w, h))
        c.setPageSize((w, h))
        if i >= first_numbered:
            c.setFont("DejaVu", 7.5); c.setFillGray(0.45)
            c.drawString(40, 22, labels[i][:90])
            c.drawRightString(w - 40, 22, str(i + 1))
        c.showPage()
    c.save(); buf.seek(0)
    overlay = PdfReader(buf)
    for i, page in enumerate(writer.pages):
        if i >= first_numbered:
            page.merge_page(overlay.pages[i])
            page.compress_content_streams(level=9)     # merging rewrites content uncompressed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "modern-java-enterprise-handbook.pdf"))
    ap.add_argument("--mermaid", default=str(DEFAULT_MERMAID))
    args = ap.parse_args()
    if not (SITE / "index.html").exists(): sys.exit("site/ not built — run `mkdocs build` first")
    if not pathlib.Path(args.mermaid).exists(): sys.exit(f"mermaid.min.js not found at {args.mermaid}")

    work = pathlib.Path("/tmp/handbook-pdf"); work.mkdir(exist_ok=True)
    for f in work.glob("*.pdf"): f.unlink()
    srv = serve(SITE)
    pages = nav_pages()
    print(f"rendering {len(pages)} pages")
    rendered = asyncio.run(render_pages(pages, args.mermaid, work))
    srv.shutdown()

    counts = [len(PdfReader(pdf).pages) for *_, pdf in rendered]
    cover = work / "cover.pdf"; toc = work / "toc.pdf"
    asyncio.run(render_html(cover_html(), cover))

    def entries(front):                              # front = pages before the first chapter page
        start, out = front + 1, []
        for (part, _, title, _), n in zip(rendered, counts):
            out.append((part, title, start)); start += n
        return out
    asyncio.run(render_html(toc_html(entries(2)), toc))            # guess: 1 cover + 1 TOC page
    front = 1 + len(PdfReader(toc).pages)
    asyncio.run(render_html(toc_html(entries(front)), toc))        # final numbers

    writer, labels = PdfWriter(), []
    for pdf, label in [(cover, ""), (toc, "Contents")]:
        for pg in PdfReader(pdf).pages: writer.add_page(pg); labels.append(label)
    starts = {}
    for (part, path, title, pdf) in rendered:
        starts[path] = len(writer.pages)
        for pg in PdfReader(pdf).pages: writer.add_page(pg); labels.append(title)

    parents = {}
    writer.add_outline_item("Contents", 1)
    for (part, path, title, _) in rendered:
        if part == "Home":
            writer.add_outline_item(title, starts[path]); continue
        if part not in parents:
            parents[part] = writer.add_outline_item(part, starts[path])
        if not path.endswith("/index.md"):
            writer.add_outline_item(title, starts[path], parent=parents[part])

    stamp_footers(writer, labels, first_numbered=1)
    writer.add_metadata({"/Title": "Modern Java Enterprise Handbook (Java 8 → 26)",
                         "/Author": "Ashish", "/Subject": "Java 8 to 26 — core Java reference"})
    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    with open(args.out, "wb") as f: writer.write(f)
    print(f"wrote {args.out}: {len(writer.pages)} pages")


if __name__ == "__main__":
    main()
