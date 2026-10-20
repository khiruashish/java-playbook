# Reusable Chapter Prompt

Paste this at the start of every chapter-generation session, filling in the four `{{...}}` placeholders. Nothing else should vary between sessions — consistency comes from this prompt, not from editing afterwards.

---

## The prompt

```
You are writing one chapter of the "Modern Java Enterprise Handbook (Java 8 → 26)",
an MkDocs Material handbook. Read the constraints fully before writing.

CHAPTER
  Number:          {{NN}}
  Title:           {{TITLE}}
  Part / path:     {{docs/0X-part/NN-slug.md}}
  Primary band:    {{L1 Foundations | L2 Professional | L3 Enterprise | L4 Architect}}
  Source material: {{paste the relevant existing guide, or "none — write from scratch"}}

DOMAIN
  All examples use the grocery-marketplace order & inventory engine, plain Java,
  no framework. Fixed vocabulary — use these type names and no others:
    Product, Sku, InventoryItem, StockReservation,
    Cart, CartLine, Order, OrderLine, OrderStatus (enum), OrderState (sealed),
    Customer, Vendor, DeliverySlot, PricingRule, Money
  Never write Foo, Bar, MyClass, Example1, or Test123.
  The canonical signatures are in code/ — Money.rupees(long|String),
  Catalogue.priceFor -> Optional<Money>, InventoryItem.reserve -> ReservationResult.

BASELINE (September 2026 — do not contradict these)
  - Java 25 is the current LTS (September 2025). Java 21 is the previous LTS.
  - Java 26 (March 2026) is the current non-LTS release.
  - ScopedValue is FINAL as of Java 25 (JEP 506) — not preview.
  - StructuredTaskScope is still PREVIEW (JEP 525, 6th preview in Java 26) and its
    API changed from the Java 21 shape: the ShutdownOnFailure / ShutdownOnSuccess
    subclasses were replaced by static factory methods with joiners. Do not copy
    Java 21-era samples without rewriting them.
  - String Templates were WITHDRAWN and ship in no released JDK.
  - Stream Gatherers are final as of Java 24 (JEP 485).
  - Flexible constructor bodies, module import declarations, and compact source
    files with instance main methods are final as of Java 25.
  - Spring references target Spring Boot 4 / Spring Framework 7.
  If you are not certain of a JEP number or its preview/final status, say so
  explicitly in a note rather than guessing.

REQUIRED STRUCTURE — all nine parts, in this order, using these exact headings:
  ## 1. Purpose & Audience
  ## 2. The Problem
  ## 3. Mental Model
  ## 4. Core API & Syntax
  ## 5. Worked Examples
  ## 6. Internals
  ## 7. Production Patterns & Anti-Patterns
  ## 8. Version Evolution (Java 8 → 26)
  ## 9. Interview Questions

CONTENT RULES
  - Part 1 states the band, the prerequisites, and the three questions this
    chapter answers.
  - Part 2 shows the pre-feature pain with real code before showing the fix.
  - Part 3 contains at least one Mermaid diagram (flowchart, sequenceDiagram,
    stateDiagram-v2, or classDiagram).
  - Part 4 is tables, not prose: signature | behaviour | since | notes.
  - Part 5 runs beginner → production, each example with expected output.
  - Part 6 explains the actual mechanism — bytecode, JVM behaviour, data
    structures, scheduler, whatever applies. No hand-waving.
  - Part 7 is split into "Do this" and "Never do this", each item with a reason.
  - Part 8 is a table: Version | What changed | Impact, plus a migration note.
  - Part 9 has 3 questions per band (L1–L4), each with a model answer of 3–6
    sentences. Mark the two questions most likely to be asked.
  - Close with a "Cheat Sheet" admonition block summarising the chapter in
    under 15 lines. This gets harvested into Appendix E.

FORMATTING
  - MkDocs Material flavour: admonitions (!!! note / warning / tip / danger),
    content tabs (=== "Java 8" / === "Java 25"), code annotations.
  - Every code block gets a language tag and a title:
      ```java title="StockReservation.java"
  - Preview-feature code carries a warning admonition naming the JDK version
    and the --enable-preview requirement.
  - Front matter at the top of the file:
      ---
      title: {{TITLE}}
      band: {{L1|L2|L3|L4}}
      status: draft
      tags: [{{tag}}, {{tag}}]
      ---
  - Cross-links use relative paths: [Virtual Threads](../04-concurrency/31-virtual-threads.md)
  - Length: 3,500–6,000 words. If the material exceeds that, stop and tell me
    the chapter should be split rather than truncating Part 6 or 9.

OUTPUT
  A single markdown file, complete, ready to drop at the path above.
  No commentary before or after the file content.
```

---

## Continuation prompt

When a chapter runs long and output is cut off:

```
Continue the chapter exactly where you stopped. Do not repeat any content
already produced, do not re-emit the front matter, and do not summarise.
Resume mid-sentence if that is where you stopped.
```

---

## Post-generation checklist

Run this against every chapter before marking `status: review`.

- [ ] All nine headings present, in order
- [ ] Front matter complete, `status` accurate
- [ ] At least one Mermaid diagram in Part 3
- [ ] Every code block compiles under `--release 25` (or is labelled with its baseline)
- [ ] Preview features carry the warning admonition
- [ ] Domain vocabulary only — no `Foo`/`Bar`/`MyClass`
- [ ] No stale preview claims (check against the BASELINE block)
- [ ] 12 interview questions, 3 per band, 2 marked as high-frequency
- [ ] Cheat sheet block present
- [ ] Cross-links resolve (`mkdocs build --strict`)
- [ ] Word count between 3,500 and 6,000
