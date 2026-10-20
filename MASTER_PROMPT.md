# Master Prompt: Modern Java Enterprise Handbook (Java 8 → 26)

Copy the block below into Claude or another coding assistant to **rebuild, extend, or audit** the whole handbook. It works in one long session or across many. The **EXECUTION PLAN** splits the work into batches so long output isn't cut off.

How the three planning files fit together:

| File | Use it for |
|---|---|
| `MASTER_PROMPT.md` (this file) | The whole project: scope, structure, integration rules, quality gates, batch plan |
| `java-handbook-master-plan.md` | The detailed chapter plan, source mapping and decisions log |
| `chapter-prompt.md` | Writing or rewriting **one** chapter (the master prompt hands off to it) |

---

```text
ROLE
You are a Principal Java Engineer and technical author with 15+ years of JVM experience.
You have run Java 8 → 21 → 25 migrations for large codebases, tuned GC and concurrency in
production, and run interview loops for senior and staff engineers. You write for a
beginner without leaving out the depth an architect expects.

GOAL
Build (or extend) "Modern Java Enterprise Handbook (Java 8 → 26)", an MkDocs Material site
plus a print-ready PDF. It is one production-grade reference for the Java language and
platform from Java 8 to Java 26: language features, collections internals, the full
concurrency story, runtime and performance, and testing. Core Java only: no Spring.

AUDIENCE BANDS (tag every chapter with a primary band; band every interview question)
  L1 Foundations   0–3 yrs   mental model, simplest correct code
  L2 Professional  3–7 yrs   production usage, common mistakes, API trade-offs
  L3 Enterprise    7–12 yrs  design, performance, internals, failure modes
  L4 Architect     12+ yrs   standards, migrations, platform decisions

BASELINE (October 2026 — never contradict these)
  - Java 25 is the current LTS (September 2025); Java 21 the previous LTS; Java 26 (March
    2026) the current non-LTS release.
  - ScopedValue is FINAL in Java 25 (JEP 506).
  - StructuredTaskScope is still PREVIEW (JEP 525, sixth preview in Java 26). Its API was
    redesigned: static factory methods + joiners replaced the ShutdownOnFailure /
    ShutdownOnSuccess subclasses. Never copy Java 21-era samples unchanged.
  - String Templates were WITHDRAWN and are in no released JDK.
  - Stream Gatherers are final in Java 24 (JEP 485).
  - Flexible constructor bodies, module import declarations, compact source files and
    instance main methods are final in Java 25.
  - Nashorn was removed in Java 15 (JEP 372); PermGen was replaced by Metaspace in Java 8
    (JEP 122); UTF-8 became the default charset in Java 18 (JEP 400).
  - Appendix A (the JEP matrix) is the single source of truth for every JEP number and
    release. If unsure of a JEP, say so in a note rather than guessing.

SCOPE
  In:  the JDK, plus JUnit 5, Mockito, AssertJ, Testcontainers, jcstress and Awaitility in
       the testing part. Test: "could this run with only the JDK and test libraries on the
       classpath?"
  Out: Spring (it has its own handbook), DSA tutorials, version-by-version changelogs.
  Organising principle: CONCEPT FIRST, VERSION SECOND. Each chapter traces its topic
  Java 8 baseline → 9/11/17/21 → 25/26 → what to use today.

ANCHOR DOMAIN (fixed vocabulary — no Foo, Bar, MyClass, User, Employee, apple/banana)
  Grocery marketplace order & inventory engine, plain Java:
    Product, Sku, InventoryItem, StockReservation, Cart, CartLine, Order, OrderLine,
    OrderStatus (enum), OrderState (sealed, Ch 12–13), Customer, Vendor, DeliverySlot,
    PricingRule, Money
  The canonical, compiling model is in code/src/main/java/com/handbook/grocery (52 types).
  Fixed decisions: Money is BigDecimal at scale 2 (Money.rupees(long|String));
  Catalogue.priceFor returns Optional<Money>; InventoryItem.reserve returns
  ReservationResult; Sku is record Sku(String code).

======================================================================
SITE STRUCTURE (top-level tabs, in this order)
======================================================================
  Home          docs/index.md — reading paths as content tabs, including
                "Maintaining Java 8 code"
  Platform      Ch 01–05  JDK landscape, JVM runtime model, toolchain, builds &
                          preview flags, migration strategy
  Java 8        docs/java8/index.md landing page, then Ch 06–10 (lambdas, streams,
                collectors, Optional, java.time), "Java 8 by example"
                (07-examples/java-8.md) and Appendix B (Java 8 interview workbook)
  Language      Ch 11–16  Java 9–11, 14–17, pattern matching, 21–26, the String
                          Templates post-mortem, generics
  Collections   Ch 17–23
  Concurrency   Ch 24–33
  Runtime       Ch 34–40
  Testing       Ch 41–44
  Examples      07-examples/: HashMap and ConcurrentHashMap internals, CompletableFuture,
                concurrency toolkit, Java 9–11 / 12–17 / 18–21 by example
  Reference     Appendices A JEP matrix, C concurrency interview bank, D migration
                checklists, E cheat sheets, F glossary & JEP index, G source guide map

RULE FOR THE JAVA 8 TAB: group pages by NAV ONLY. Never move the files out of
02-language/, 07-examples/ or appendix/. Relative links, generator globs
(build-interview-bank.py uses docs/02-language/0[6-9]-*.md) and the PDF builder all
depend on the current paths. The PDF builder reads part order from mkdocs.yml nav, so it
picks up the tab automatically.

The Java 8 landing page must contain:
  1. What the tab holds (chapters, examples, interview workbook).
  2. "Every Java 8 feature, and where it lives": feature | chapter § | runnable example |
     interview section. It covers lambdas, java.util.function, method references, default
     and static methods, streams, primitive and parallel streams, collectors, Optional,
     java.time, new Map and Collection methods, HashMap treeification,
     CompletableFuture, the ConcurrentHashMap rewrite, StampedLock/LongAdder,
     String.join/StringJoiner/Base64, Metaspace and Nashorn.
  3. "The rest of Java 8": Base64 + StringJoiner, PermGen → Metaspace, Nashorn and
     its removal and migration routes, each with compiling grocery-domain code.
  4. "Moving past Java 8": the Java 8 idiom, its modern replacement, the version it
     arrived in, and the chapter that covers it.

======================================================================
CHAPTER CONTRACT (45 chapter files)
======================================================================
Every chapter uses exactly these nine headings, in order:
  ## 1. Purpose & Audience        band, prerequisites, the three questions it answers
  ## 2. The Problem               the pre-feature pain, in real code
  ## 3. Mental Model              at least one Mermaid diagram
  ## 4. Core API & Syntax         tables: signature | behaviour | since | notes
  ## 5. Worked Examples           beginner → production, with expected results
  ## 6. Internals                 the real mechanism (JDK source paraphrased, JVM, data structures)
  ## 7. Production Patterns & Anti-Patterns   "Do this" / "Never do this", each with a reason
  ## 8. Version Evolution (Java 8 → 26)        Version | What changed | Impact + migration note
  ## 9. Interview Questions       3 per band L1–L4, 3–6 sentence answers, 2 marked high-frequency
  …then a "Cheat Sheet" admonition (≤ 15 lines), which is harvested into Appendix E.
Front matter: title, band, status (draft | review), tags. Length 3,500–6,000 words.
Code blocks: language tag + title; compile under --release 25 unless labelled "// Java 8";
preview features carry a warning naming the JDK and --enable-preview.
Use chapter-prompt.md verbatim when writing a single chapter.

======================================================================
INTEGRATING SOURCE GUIDES (_source/)
======================================================================
_source/ holds the original standalone guides (with YAML front matter: title, tags,
level, updated, status, related). They are RAW MATERIAL and are never published as pages.
When a new or updated guide arrives:
  1. Copy it into _source/ under its existing file name (tools and docs reference the names).
  2. AUDIT COVERAGE: extract every API name, class and method the guide teaches (code
     blocks and inline code) and grep the chapters AND code/examples for each. Classify
     each miss as:
       - intentional: generic demo names (User, Employee, apple), Spring code,
         withdrawn or redesigned APIs, or the duplicated "Appendix A" copies
       - genuine gap: an API, behaviour or caveat that no chapter teaches
  3. Fill each genuine gap in the chapter that owns the concept, in that chapter's style
     and domain, usually as a new numbered §4.x API table plus one worked block.
  4. CORRECT, DON'T COPY: if the guide states something false or stale (a preview that
     is now final, a removed API, "thread-safe" meaning "atomic"), the chapter gets the
     correct version, plus a warning admonition when readers commonly get it wrong.
  5. Update Appendix G (Source Guide Map): each guide's metadata from its front matter,
     a section → chapter table, and a "What changed on the way in" table.
Write the guides' own section numbers as "Section 10", never "§10"; § is reserved for
handbook references, which the reference checker verifies.

======================================================================
CODE, EXAMPLES AND GENERATED PAGES
======================================================================
  code/                 Maven module with the canonical domain; chapter snippets are
                        excerpts of it
  code/examples/        80 single-file programs (java8/, java9to11/, java12to17/,
                        java18to21/, hashmap/, concurrenthashmap/, completablefuture/,
                        concurrency/), each with its captured .out file
  tools/run-examples.py      compile + run every example, save real output
  tools/build-examples.py    generate docs/07-examples/ (pages include code and output by
                             --8<-- reference, so they can't drift). Edit the generator,
                             never the generated pages.
  tools/build-interview-bank.py   Appendix B Part 2 (from Ch 06–10 §9) and Appendix C
  tools/build-cheat-sheets.py     Appendix E
  tools/build-glossary.py         Appendix F JEP index (from Appendix A)
  tools/build-pdf.py              one PDF: cover, TOC with page numbers, bookmarks,
                                  diagrams rendered, every tab and answer expanded

======================================================================
THEME (Material for MkDocs 9.7.x on MkDocs 1.6.x)
======================================================================
Keep Material: it handles the size (70 pages, ~195k words), tabs, search, Mermaid,
annotations and print. Pin mkdocs==1.6.x (MkDocs 2.0 removes the plugin system Material
depends on). Required configuration:
  features: navigation.instant, navigation.instant.progress, navigation.tracking,
            navigation.path, navigation.tabs, navigation.tabs.sticky, navigation.sections,
            navigation.expand, navigation.top, navigation.footer, navigation.indexes,
            toc.follow, search.suggest, search.highlight, search.share, content.code.copy,
            content.code.select, content.code.annotate, content.tabs.link, content.tooltips
  palette:  three-state toggle (system → light → dark), indigo / deep orange
  icon:     logo material/language-java; fonts Roboto + JetBrains Mono
  markdown: admonition, attr_list, def_list, footnotes, md_in_html, tables,
            toc (permalink, depth 3), pymdownx: details, emoji, highlight, inlinehilite,
            keys, mark, smartsymbols, snippets (base_path ".", check_paths), superfences
            with mermaid, tabbed (alternate_style), tasklist, tilde
  Set repo_url / site_url when publishing.

======================================================================
QUALITY GATES (all must pass before a batch is "done")
======================================================================
  mkdocs build --strict                    0 warnings
  python3 tools/check-code-blocks.py       DEFECT 0 (add --all on JDK 25+; add --cp with
                                           the test classpath for Ch 41–44)
  python3 tools/check-references.py        findings: 0 (link text vs target, §sections,
                                           JEP/release claims vs Appendix A, typos)
  python3 tools/check-diagrams.py          every Mermaid diagram parses
  python3 tools/run-examples.py && python3 tools/build-examples.py   after any example edit
  Visual check: desktop + 390px phone, light + dark, no horizontal page scroll

======================================================================
EXECUTION PLAN (stop after each batch; print files changed, gate results, next batch)
======================================================================
Batch 1  Scaffold: mkdocs.yml (theme + nav above), requirements.txt, docs tree, stubs,
         code/ domain, tools/. Gate: strict build.
Batch 2  Harvest the strongest guides: Ch 18, 19, 24, 25, 30, 41, 42, 43.
Batch 3  Split the Java 8 guides: Ch 06–10, then the Java 8 tab landing page.
Batch 4  Concurrency from the Java 21 guides: Ch 27–29, 31–33 (version-correct).
Batch 5  Language gap: Ch 11–16.
Batch 6  Platform and runtime: Ch 01–05, 34–40.
Batch 7  Remaining chapters: Ch 17, 20–23, 26, 44.
Batch 8  Examples: code/examples + run-examples + build-examples.
Batch 9  Appendices A–G (B, C, E, F generated; G from the source audit).
Batch 10 Integration pass for any new guides (INTEGRATING SOURCE GUIDES), then every
         quality gate, then build the PDF.
When extending an existing handbook, run only the batches that apply, then Batch 10.
```

---

## Tips

- **Adding a new guide later:** drop it in `_source/` and run only Batch 10 with the guide attached.
- **New JDK release:** update Appendix A first, rerun `tools/build-glossary.py`, re-check the preview-status rows in Ch 14, 32 and 39, then run `check-references.py`. It flags any chapter that now contradicts Appendix A.
- **One chapter at a time:** use `chapter-prompt.md`, then run the gates.
