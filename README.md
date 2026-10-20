# Modern Java Enterprise Handbook (Java 8 → 26)

MkDocs Material handbook covering the Java language and platform from Java 8 to Java 26.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve                       # http://127.0.0.1:8000
```

## Files

| File | Purpose |
|---|---|
| `MASTER_PROMPT.md` | One prompt to rebuild, extend or audit the whole handbook, including how to integrate new guides. |
| `java-handbook-master-plan.md` | Scope, chapter plan, source mapping, roadmap. Read first. |
| `chapter-prompt.md` | Reusable prompt for generating each chapter. |
| `mkdocs.yml` | Site config + full 45-chapter nav. |
| `scaffold-handbook.sh` | Creates the docs tree and stub files. |
| `_source/` | The original guides (now with front matter). Raw material, never published; see Appendix G for where each section lives. |
| `DEPLOYMENT.md` | Step-by-step: from the zip to a live GitHub Pages site, with troubleshooting. |
| `.github/workflows/deploy.yml` | Builds with `--strict` and publishes to GitHub Pages on every push to `main`. |
| `code/` | Compilable example project; snippets are included, not pasted. |
| `tools/` | Generators for Appendices B, C, E, and F — see master plan §8. |

## Site layout

| Tab | Contents |
|---|---|
| Platform | Ch 01–05 |
| **Java 8** | A Java 8 overview page, Ch 06–10, *Java 8 by Example*, and Appendix B (Java 8 interview workbook) |
| Language | Ch 11–16 |
| Collections · Concurrency · Runtime · Testing | Ch 17–23 · 24–33 · 34–40 · 41–44 |
| Examples | HashMap and ConcurrentHashMap internals, CompletableFuture, concurrency toolkit, Java 9–21 by example |
| Reference | Appendices A, C, D, E, F and G (Source Guide Map) |

The Java 8 tab groups pages through `mkdocs.yml` nav only. The files stay in `02-language/`, `07-examples/` and `appendix/`, so links and generators are unaffected.

## Build

```bash
mkdocs build --strict                 # fails on broken links
python3 tools/check-code-blocks.py    # compiles every Java block: expect DEFECT 0
python3 tools/check-references.py     # link text, § sections, JEP claims: expect findings: 0
mkdocs gh-deploy --force              # manual publish to GitHub Pages (or push and let Actions do it)
```

For PDF: uncomment the `print-site` plugin in `mkdocs.yml` and the matching
line in `requirements.txt`, then `mkdocs build` and open `site/print_page.html`.

## Examples

80 short, complete programs — HashMap and ConcurrentHashMap internals, CompletableFuture, the
concurrency toolkit, and every major feature from Java 8 to 21 — each shown with its real output.
Sources are in `code/examples/`; the pages include them, so a page can never show code that doesn't run.

```bash
python3 tools/run-examples.py          # compile + run every example, save real output to .out files
python3 tools/build-examples.py        # regenerate docs/07-examples/ from them
java code/examples/hashmap/HashSpreading.java    # or run any single example directly (JDK 21+)
```

## PDF

The whole handbook as one print-ready PDF — cover, contents with page numbers,
bookmarks, rendered diagrams, expanded answers, every content tab shown:

```bash
pip install playwright pypdf reportlab && playwright install chromium
npm install -g @mermaid-js/mermaid-cli     # provides a local mermaid.min.js (works offline)
mkdocs build
python3 tools/build-pdf.py --out modern-java-enterprise-handbook.pdf
```

## Checks

```bash
mkdocs build --strict                  # links, nav, front matter
python3 tools/check-diagrams.py        # every Mermaid diagram parses (strict mode does not check this)
python3 tools/check-code-blocks.py     # every Java block compiles, or has a recorded reason
python3 tools/check-references.py      # links, § refs and JEP/release claims agree with their targets
```

