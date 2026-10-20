# Modern Java Enterprise Handbook (Java 8 → 26) — Master Plan

> Planning document. Read this before generating any chapter.
> Target: MkDocs Material site + PDF export. 42 chapters, 6 appendices, 4 levels.
> Baseline: September 2026. Java 25 = current LTS. Java 26 = current non-LTS.

---

## 1. Scope & Positioning

### 1.1 What this handbook is

A single, production-grade reference covering **the Java language and platform from Java 8 through Java 26** — every significant language feature, the collections framework internals, the full concurrency story, runtime/performance behaviour, and the testing discipline that goes with it.

### 1.2 What it is NOT

- **Not a Spring handbook.** Spring Boot 4 has its own handbook. This one stops at the JDK boundary — **core Java only**. Every example compiles against the JDK plus, in the testing part, JUnit, Mockito, and Testcontainers. No framework annotations, no application context, no starters.

  The test to apply to any chapter: *could this code run with nothing on the classpath but the JDK and the test libraries?* If not, it belongs in the Spring handbook. A framework may be **named** as an example of the ecosystem — "Spring's `SpringExtension` uses `ParameterResolver`" — but never taught.

### 1.2.1 Deferred to the Spring Boot handbook

Material cut from this handbook's scope, to be written there:

| Topic | Was drafted in |
|---|---|
| `@SpringBootTest` and test slices (`@WebMvcTest`, `@DataJpaTest`, `@JsonTest`) | Ch 43, removed |
| Application-context caching and `@DirtiesContext` | Ch 43, removed |
| Bean overrides: `@MockitoBean`, `@MockitoSpyBean`, `@TestBean` | Ch 43, removed |
| `@ServiceConnection` and `@DynamicPropertySource` | Ch 43, removed |
| `MockMvc`, `TestRestTemplate`, `WebTestClient` | Ch 43, removed |
| `@Transactional` test rollback semantics | Ch 43, removed |
| `spring.threads.virtual.enabled` | Ch 31, do not add |
| Spring Data repositories, JPA entity mapping | never in scope |

A draft of the Spring-flavoured Chapter 43 is retained as raw material for that handbook.
- **Not a DSA handbook.** `CustomArrayList` appears to explain `ArrayList` internals, not to teach algorithms.
- **Not version-by-version.** Organising by JDK release produces a changelog, not a handbook. Organise by **concept**, and show the evolution *inside* each concept chapter.

### 1.3 Core organising principle

> **Concept first, version second.**

Every chapter follows an evolution arc: *Java 8 baseline → what changed at 9/11/17/21 → current state at 25/26 → what to use today*. A reader on Java 8 in a legacy codebase and a reader starting greenfield on Java 25 both find themselves in the same chapter.

### 1.4 Anchor domain

Reuse the **grocery marketplace** domain, but a different subsystem from the Spring Boot 4 handbook: the **order & inventory engine**, written in plain Java with no framework.

Why it fits:
- Order/inventory maps naturally onto collections (catalogue lookups, cart lists, price maps).
- Concurrent stock reservation is a real, non-toy concurrency problem — it exercises atomics, locks, `ConcurrentHashMap`, virtual threads, and structured concurrency without contrivance.
- Order state transitions are the natural home for sealed types + record patterns + pattern matching for `switch`.
- Cross-handbook consistency: same domain language as the Spring Boot 4 and Angular 22 handbooks.

Fixed domain vocabulary (use these names in every chapter):

```
Product, Sku, InventoryItem, StockReservation,
Cart, CartLine, Order, OrderLine, OrderStatus (enum), OrderState (sealed, Ch 12–13),
Customer, Vendor, DeliverySlot, PricingRule, Money
```

### 1.5 Level bands

| Band | Label | Audience |
|---|---|---|
| L1 | Foundations | 0–3 yrs — needs the mental model |
| L2 | Professional | 3–7 yrs — writes production code daily |
| L3 | Enterprise | 7–12 yrs — owns design and performance |
| L4 | Architect | 12+ yrs — sets standards, runs migrations |

Every chapter is tagged with a primary band. Every chapter's Interview section is banded L1–L4.

---

## 2. Existing Assets & Coverage Map

Twelve source guides, ~265 KB, already written. They become **raw material**, not chapters — each is harvested, expanded to the 9-part format, re-grounded in the anchor domain, and version-updated to 25/26.

| Source guide | Size | Feeds chapter(s) | Action |
|---|---|---|---|
| `Java8-Guide.md` | 25 KB | Ch 06, 07, 08, 09, 10 | **Split** — currently five chapters in one file |
| `Java8-Interview-Guide.md` | 13 KB | Ch 06–10 interview sections, App. B | **Distribute** into per-chapter Q&A |
| `Java21-Features-Guide.md` | 18 KB | Ch 12, 13, 14, 22, 30, 37 | **Split + update** — several items moved past preview since |
| `Java21-Concurrency-Guide.md` | 15 KB | Ch 30, 31 | **Split + update** — API changed across previews |
| `Threading-Basic-Guide.md` | 12 KB | Ch 24, 25 | Expand |
| `Threading-Enterprise-Guide.md` | 16 KB | Ch 26, 27, 28, 32 | **Split** |
| `List-Guide.md` | 43 KB | Ch 17, 18, 21 | Split; strip duplicate appendix |
| `HashMap-Guide.md` | 40 KB | Ch 19, 21 | Split; strip duplicate appendix |
| `ConcurrentHashMap-Guide.md` | 39 KB | Ch 29 | Expand; strip duplicate appendix |
| `CustomArrayList-Guide.md` | 14 KB | Ch 18 | Merge as second half of ArrayList chapter |
| `Unit-Testing-Guide.md` | 13 KB | Ch 38, 39 | Split |
| `Integration-Testing-Guide.md` | 17 KB | Ch 40 | Expand |

### 2.1 Known defects in the source material to fix during harvest

1. **Duplicated appendices.** `List-Guide`, `HashMap-Guide`, and `ConcurrentHashMap-Guide` each carry a near-complete second copy of themselves as "Appendix A". Roughly 40% of those three files is redundant. Keep the structured body; convert the appendix's method-by-method examples into a single API reference table per chapter.
2. **Stale preview status.** The Java 21 guides describe `StructuredTaskScope`, `ScopedValue`, and String Templates as previews. As of Java 25: `ScopedValue` is **final** (JEP 506); `StructuredTaskScope` is still **preview** but its API changed substantially (factory methods and joiners replaced the `ShutdownOnFailure` / `ShutdownOnSuccess` subclasses); **String Templates was withdrawn entirely** and is in no released JDK. Every code sample in those guides needs re-verification against JDK 25.
3. **Spring Boot 3 references.** Update to Spring Boot 4 / Framework 7 in the callouts.
4. **No Java 9–17 coverage.** Modules, `var`, text blocks, switch expressions, records, and sealed types are entirely missing — the biggest gap.
5. **No JVM/GC/profiling coverage.** Nothing on memory model, GC, JFR, or startup. This is where L3/L4 readers actually live.

---

## 3. Chapter Plan

### Part 0 — Getting Started

| # | Chapter | Band | Source |
|---|---|---|---|
| 00 | How to use this handbook | — | new |

### Part 1 — The Platform (Ch 01–05)

| # | Chapter | Band | Source |
|---|---|---|---|
| 01 | The JDK landscape: 8 → 26, LTS cadence, distributions | L1 | new |
| 02 | JVM runtime model: class loading, memory areas, JIT | L2 | new |
| 03 | The toolchain: javac, jshell, jlink, jpackage, single-file launch | L2 | new |
| 04 | Build & toolchains: Maven/Gradle, release flag, preview features | L2 | new |
| 05 | Migration strategy: 8 → 11 → 17 → 21 → 25 | L4 | new |

### Part 2 — Language Evolution (Ch 06–16)

| # | Chapter | Band | Source |
|---|---|---|---|
| 06 | Lambdas, functional interfaces, method references | L1 | Java8-Guide §2–4, Java8-Interview §1–4 |
| 07 | The Stream API: architecture and pipelines | L2 | Java8-Guide §5, Java8-Interview §5–6 |
| 08 | Collectors and advanced stream composition | L2 | Java8-Guide §5.6, Java8-Interview §7, §14 |
| 09 | Optional and a null strategy | L2 | Java8-Guide §6, Java8-Interview §8 |
| 10 | `java.time`: dates, durations, zones | L1 | Java8-Guide §7, Java8-Interview §10 |
| 11 | Java 9–11: modules, `var`, collection factories, HttpClient | L3 | new |
| 12 | Java 14–17: records, sealed types, text blocks, switch expressions | L2 | new |
| 13 | Pattern matching: `instanceof` → `switch` → record patterns | L2 | Java21-Features §7–9 |
| 14 | Java 21–26 language: unnamed vars, flexible constructors, module imports, compact source files, Markdown javadoc | L3 | Java21-Features §9 |
| 15 | The features that didn't land: String Templates and what to learn from it | L4 | Java21-Features §10 |
| 16 | Generics in depth: variance, erasure, bounded types, API design | L3 | new |

### Part 3 — Collections & Data (Ch 17–23)

| # | Chapter | Band | Source |
|---|---|---|---|
| 17 | The collections framework: choosing the right structure | L1 | List-Guide §2 |
| 18 | `List` internals: ArrayList, LinkedList, and building your own | L2 | List-Guide §3–9 + CustomArrayList-Guide |
| 19 | `HashMap` internals: hashing, treeification, resizing | L2 | HashMap-Guide |
| 20 | `Set`, `Queue`, `Deque`, and `PriorityQueue` | L2 | new |
| 21 | Sequenced Collections (Java 21) | L2 | List-Guide §5.6, HashMap-Guide §6.5 |
| 22 | Immutability: factory methods, views, defensive copying, records as data | L3 | new |
| 23 | `equals`, `hashCode`, `Comparable`, `Comparator` — the contracts | L2 | new |

### Part 4 — Concurrency (Ch 24–33)

| # | Chapter | Band | Source |
|---|---|---|---|
| 24 | Threading fundamentals: lifecycle, interruption, daemon threads | L1 | Threading-Basic §2–4 |
| 25 | Shared state: race conditions, `synchronized`, `volatile`, deadlock | L2 | Threading-Basic §5–6 |
| 26 | The Java Memory Model: happens-before, safe publication, final fields | L4 | new |
| 27 | Locks, atomics, and the `java.util.concurrent` toolbox | L3 | Threading-Enterprise §3 |
| 28 | Executors and thread pool design | L3 | Threading-Enterprise §3.1, Threading-Basic §7 |
| 29 | `CompletableFuture`: composition, timeouts, error handling | L3 | Threading-Enterprise §3.3, Java8-Interview §11 |
| 30 | `ConcurrentHashMap` and the concurrent collections | L3 | ConcurrentHashMap-Guide |
| 31 | Virtual threads: model, scheduling, pinning, pitfalls | L3 | Java21-Concurrency §3–5, Java21-Features §3 |
| 32 | Structured concurrency: Java 21 preview → Java 26 (JEP 525) | L4 | Java21-Concurrency §6, §8 |
| 33 | Context propagation: `ThreadLocal` → `ScopedValue` (final in 25) | L3 | Threading-Enterprise §6, Java21-Features §5 |

### Part 5 — Runtime & Performance (Ch 34–40)

| # | Chapter | Band | Source |
|---|---|---|---|
| 34 | Garbage collection: G1, generational ZGC, generational Shenandoah | L4 | new |
| 35 | Memory footprint: object layout, compact object headers (JEP 519) | L4 | new |
| 36 | Startup and warmup: CDS, AOT cache, Project Leyden (JEP 483 in 24; 514/515 in 25; 516 in 26) | L4 | new |
| 37 | Profiling with JFR: CPU-time profiling, method timing, flight recording | L3 | new |
| 38 | Stream Gatherers (Java 24) and extending the Stream API | L3 | new |
| 39 | Escaping the JVM: FFM API (final: JEP 454), Vector API, replacing `Unsafe`/JNI | L4 | Java21-Features §11 |
| 40 | The HTTP Client: HTTP/1.1 → HTTP/2 → HTTP/3 (JEP 517) | L3 | new |

### Part 6 — Testing & Quality (Ch 41–44)

| # | Chapter | Band | Source |
|---|---|---|---|
| 41 | JUnit 5: lifecycle, assertions, parameterized tests | L1 | Unit-Testing-Guide §2–6 |
| 42 | Test doubles with Mockito: mocks, statics, argument captors | L2 | Unit-Testing-Guide §7–9 |
| 43 | Integration testing with Testcontainers (JDBC + `java.net.http`, no framework) | L3 | Integration-Testing-Guide |
| 44 | Testing concurrent code: jcstress, Awaitility, virtual-thread traps | L4 | new |

### Appendices

| # | Appendix | Source |
|---|---|---|
| A | JEP matrix: every significant feature, Java 8 → 26 | new |
| B | Java 8 interview workbook | Java8-Interview-Guide §14–16 |
| C | Concurrency interview bank (L1 → L4) | Java21-Concurrency §11, Threading-Enterprise §8.3 |
| D | Migration checklists: 8→11, 11→17, 17→21, 21→25 | new |
| E | Cheat sheet index (one card per chapter) | harvested |
| F | Glossary and JEP number index | new |

**Totals:** 45 chapter files + 6 appendices. Roughly 18 harvest-and-expand, 27 written from scratch.

---

## 4. Chapter Format (the 9-part contract)

Every chapter file follows this structure without exception:

1. **Purpose & Audience** — what this chapter answers, band, prerequisites
2. **The Problem** — what was painful before this feature/concept existed
3. **Mental Model** — the diagram-first explanation (Mermaid)
4. **Core API & Syntax** — the reference surface, in tables
5. **Worked Examples** — progressive, grounded in the order/inventory domain
6. **Internals** — how it actually works underneath
7. **Production Patterns & Anti-Patterns** — what to do, what breaks
8. **Version Evolution** — Java 8 → 26 timeline for this topic, with a migration note
9. **Interview Questions** — banded L1/L2/L3/L4, with model answers

### 4.1 Non-negotiable conventions

- **Every code block compiles.** Target `--release 25` unless demonstrating an older baseline, in which case label the block `// Java 8`.
- **Preview features are labelled** with an admonition stating the JDK version and that `--enable-preview` is required.
- **Every chapter has at least one Mermaid diagram** in Part 3.
- **Every chapter ends with a cheat-sheet block** that gets harvested into Appendix E.
- **Domain names are fixed** — see §1.4. No `Foo`, `Bar`, `MyClass`.
- **Cross-links use relative paths** so PDF export resolves them.
- **Target length:** 3,500–6,000 words per chapter. Under 3,000 means the chapter is thin; over 7,000 means it should split.

---

## 5. Production Roadmap

| Phase | Chapters | Why this order |
|---|---|---|
| **0. Scaffold** | — | Repo, `mkdocs.yml`, stubs, CI. Half a day. |
| **1. Harvest** | 18, 19, 30, 24, 25, 41, 42, 43 | Convert the strongest existing guides first. Fast wins, proves the format. |
| **2. Split** | 06, 07, 08, 09, 10, 31, 32, 33 | Break the multi-topic guides apart and version-correct them. |
| **3. Fill the language gap** | 11, 12, 13, 14, 15, 16 | The Java 9–17 hole is the most visible omission. |
| **4. Fill the platform gap** | 01–05, 34–40 | The L3/L4 differentiator; nothing exists yet. |
| **5. Complete** | 17, 20, 21, 22, 23, 26, 27, 28, 29, 44 | Remaining chapters. |
| **6. Appendices** | A–F | Mechanical once chapters exist; A and E are harvests. |
| **7. Polish** | — | Cross-links, PDF export, code compile check, consistency pass. |

At one chapter per session, this is roughly 45 sessions. At three, roughly 15.

---

## 6. Repository Layout

```
java-handbook/
├── mkdocs.yml
├── requirements.txt
├── README.md
├── java-handbook-master-plan.md      ← this file
├── chapter-prompt.md                 ← reusable generation prompt
├── scaffold-handbook.sh
├── _source/                          ← original 12 guides, read-only, never published
├── code/                             ← compilable example project
│   ├── pom.xml
│   └── src/main/java/com/handbook/grocery/...
└── docs/
    ├── index.md
    ├── 01-platform/
    ├── 02-language/
    ├── 03-collections/
    ├── 04-concurrency/
    ├── 05-runtime/
    ├── 06-testing/
    ├── appendix/
    └── assets/
```

### 6.1 The `code/` directory

Every non-trivial sample lives in a real Maven module compiled by CI, and is pulled into the docs with the snippet syntax rather than pasted:

```markdown
```java title="StockReservation.java"
--8<-- "code/src/main/java/com/handbook/grocery/inventory/StockReservation.java"
```
```

This is the single highest-value decision in the whole plan. Pasted code rots silently across 45 chapters; included code breaks the build the moment it stops compiling.

---

## 7. Decisions — resolved

All four open decisions were settled during writing (September 2026).

1. **Java 26 depth — inline, no dedicated part.** Java 26 items appear inside the concept chapters: HTTP/3 in Ch 40, structured concurrency's sixth preview in Ch 32, G1 throughput (JEP 522) in Ch 34, AOT object caching (JEP 516) in Ch 36, final-field warnings (JEP 500) in Ch 26.
2. **JEP verification — done.** Every JEP cited was checked against OpenJDK sources for Java 22–26. All 54 numbers were correct; eight statements about release or status were corrected (JEP 509 experimental; 516 in 26 not 25; 472's scope; 479 vs 503; plus four gaps filled). Appendix A is the verified reference.
3. **Exercises — centralised, not per chapter.** Appendix B carries 24 coding exercises with explicit traps; Appendices B and C turn every chapter's interview questions into collapsible self-tests.
4. **Splitting the volume — not needed.** The finished handbook is about 195,000 words and 1.5 MB of Markdown, which MkDocs search and navigation handle comfortably.

## 8. Maintenance

Three pages are generated. Edit the sources, then rerun:

| Page | Generated from | Command |
|---|---|---|
| Appendix B, Part 2 | Chapters 06–10, section 9 | `tools/build-interview-bank.py docs/appendix/b-java8-interview-workbook.md "Appendix B — Java 8 Interview Workbook" "docs/02-language/0[6-9]-*.md" "docs/02-language/10-*.md" --preamble tools/templates/b-preamble.md` |
| Appendix C | Chapters 24–33, section 9 | `tools/build-interview-bank.py docs/appendix/c-concurrency-interview-bank.md "Appendix C — Concurrency Interview Bank" "docs/04-concurrency/*[0-9]-*.md"` |
| Appendix E | Every chapter's cheat sheet | `tools/build-cheat-sheets.py` |
| Appendix F, JEP index | Appendix A tables | `tools/build-glossary.py` |

The canonical domain lives in `code/` (52 types; see `code/README.md`). Chapters show excerpts of it.

Code verification: `tools/check-code-blocks.py` extracts all 483 Java blocks, compiles them with the local JDK, and classifies the results. Run it after editing any code sample. On a JDK 25+ machine, add `--all` to include the 61 blocks that use features final after Java 21. Reviewed exceptions are fingerprinted in `tools/code-check-baseline.json`; a run should report `DEFECT 0`.

Diagram verification: `tools/check-diagrams.py` parses all 138 Mermaid diagrams with Mermaid itself — `mkdocs build --strict` does not, and two broken diagrams had passed it.

Reference verification: `tools/check-references.py` checks that every link's text matches its target (chapter number, title, §section) and that every JEP release claim in prose and version tables agrees with Appendix A — 824 links and 125 claims at last run.

Examples (Part 7): `code/examples/` holds 80 single-file programs; `tools/run-examples.py` runs them and captures real output, and `tools/build-examples.py` generates `docs/07-examples/` — two internals walkthroughs (HashMap, ConcurrentHashMap), CompletableFuture, the concurrency toolkit, and Java 8 / 9–11 / 12–17 / 18–21 feature pages. Pages include code and output by reference, so they cannot drift. Rerun both after editing an example.

PDF: `tools/build-pdf.py` renders the built site through headless Chromium into one book (about 935 pages, ~15 MB). Rebuild it after any content change.

Source-guide integration (October 2026): the ten guides were re-supplied with YAML front matter and copied over `_source/` (same file names). A coverage audit of every API the guides teach against the chapters and `code/examples` found five genuine gaps, now filled: `indexOf`/`lastIndexOf`/`ListIterator` (Ch 18 §4.4), `remove(Object)`/`fastRemove` internals (Ch 18 §6.2), `putAll`, map views and sorting entries by key or value (Ch 19 §4.2, §4.5), and `ConcurrentHashMap.putAll`/`clear` being thread-safe but not atomic (Ch 30 §4.4, which corrects the guide). Nashorn, Base64 and PermGen → Metaspace are covered on the new Java 8 landing page (`docs/java8/index.md`). Appendix G maps every guide section to its chapter. Java 8 content (Ch 06–10, Java 8 examples, Appendix B) now has its own nav tab; the files did not move.

On each new JDK release: update Appendix A from the OpenJDK release page, rerun `build-glossary.py`, and check the preview-status rows in Ch 14, 32, and 39.
