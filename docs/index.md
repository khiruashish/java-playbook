---
title: Home
---

<div class="pb-hero" markdown>
<div markdown>

<span class="pb-kicker">Java 8 → Java 26 · organised by concept</span>

<h1>Modern Java Enterprise Handbook</h1>

<p class="pb-lead">A complete reference to the Java language and platform. Every chapter traces its topic from the Java 8 baseline to Java 25 LTS and beyond.</p>

[Start with the platform](01-platform/index.md){ .md-button .md-button--primary }
[Language](02-language/index.md){ .md-button }
[Concurrency](04-concurrency/index.md){ .md-button }

</div>
<div class="pb-stack" aria-hidden="true">
<div class="pb-stack-plane">
<div class="pb-layer l-cpu">JVM runtime<small>JIT · GC · threads</small></div>
<div class="pb-layer l-car">JDK libraries<small>collections · streams · java.time</small></div>
<div class="pb-layer l-fjp">Java language<small>records · sealed types · patterns</small></div>
<div class="pb-layer l-vt">Your code<small>Java 8 → 26</small></div>
</div>
<div class="pb-stack-legend">What runs underneath every<br>line of Java you write</div>
</div>
</div>

<div class="pb-stats">
<div class="pb-stat"><b>69</b><span>pages</span></div>
<div class="pb-stat"><b>9</b><span>sections</span></div>
<div class="pb-stat"><b>140</b><span>diagrams</span></div>
<div class="pb-stat"><b>132</b><span>Java source files</span></div>
</div>

## Explore the handbook

<div class="pb-cards" markdown>

<div class="pb-card" markdown>
<span class="pb-icon">:material-layers:</span>

[Platform](01-platform/index.md){ .pb-title }

The JDK Landscape (8 → 26), JVM Runtime Model, The Toolchain, Builds, Release Flags & Preview Features…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-numeric-8-circle:</span>

[Java 8](java8/index.md){ .pb-title }

Lambdas & Functional Interfaces, The Stream API, Collectors & Stream Composition, Optional & Null Strategy…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-code-braces:</span>

[Language](02-language/index.md){ .pb-title }

Java 9–11: Modules, var, HttpClient, Java 14–17: Records, Sealed Types, Text Blocks, Pattern Matching, Java 21–26 Language Features…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-format-list-bulleted:</span>

[Collections](03-collections/index.md){ .pb-title }

Choosing the Right Collection, List Internals & CustomArrayList, HashMap Internals, Set, Queue & Deque…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-lightning-bolt:</span>

[Concurrency](04-concurrency/index.md){ .pb-title }

Threading Fundamentals, Shared State & Synchronization, The Java Memory Model, Locks, Atomics & java.util.concurrent…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-engine:</span>

[Runtime](05-runtime/index.md){ .pb-title }

Garbage Collection, Memory Footprint & Object Layout, Startup, Warmup & Project Leyden, Profiling with JFR…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-test-tube:</span>

[Testing](06-testing/index.md){ .pb-title }

JUnit 5, Mockito & Test Doubles, Integration Testing & Testcontainers, Testing Concurrent Code…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-flask:</span>

[Examples](07-examples/index.md){ .pb-title }

HashMap — how it works inside, ConcurrentHashMap — how it works inside, CompletableFuture by example, Concurrency toolkit by example…
</div>

<div class="pb-card" markdown>
<span class="pb-icon">:material-bookshelf:</span>

[Reference](appendix/index.md){ .pb-title }

A · JEP Matrix (Java 8 → 26), C · Concurrency Interview Bank, D · Migration Checklists, E · Cheat Sheet Index…
</div>

</div>

A complete reference to the Java language and platform, **Java 8 through Java 26**,
organised by concept rather than by release. Every chapter traces its topic from
the Java 8 baseline to the current state on Java 25 LTS.

## How to read this

=== "Learn by running code"
    Start with **[Examples](07-examples/index.md)** — 80 short programs, each shown
    with the real output it printed. Begin with
    [HashMap — how it works inside](07-examples/hashmap-internals.md) or
    [CompletableFuture by example](07-examples/completablefuture.md), then follow the
    links into the chapters for the *why*.

=== "Maintaining Java 8 code"
    Open the **[Java 8](java8/index.md)** tab. It collects the five Java 8 chapters
    (lambdas, streams, collectors, `Optional`, `java.time`), the 13 runnable Java 8
    examples and the Java 8 interview workbook, plus a map of every Java 8 feature to
    the chapter that covers it.

=== "New to modern Java"
    Start with [The JDK Landscape](01-platform/01-jdk-landscape.md), then work
    through the **Java 8** and **Language** tabs in order, running the matching
    [Java 8–21 examples](07-examples/index.md) as you go. Skip **Runtime** until
    you have shipped something.

=== "Upgrading a legacy codebase"
    Start with [Migration Strategy](01-platform/05-migration-strategy.md) and
    [Appendix D](appendix/d-migration-checklists.md), then read the Part 8
    "Version Evolution" section of each chapter that touches your code.

=== "Preparing for interviews"
    Run the [HashMap](07-examples/hashmap-internals.md) and
    [ConcurrentHashMap](07-examples/concurrenthashmap-internals.md) walkthroughs —
    interviewers ask about both constantly — then read Part 9 of every chapter, then
    [Appendix B](appendix/b-java8-interview-workbook.md) and
    [Appendix C](appendix/c-concurrency-interview-bank.md).

=== "Tuning production"
    Go straight to **Concurrency** and **Runtime**.

## Baseline

| Item | Status |
|---|---|
| Java 25 | Current LTS (September 2025) |
| Java 21 | Previous LTS (September 2023) |
| Java 26 | Current non-LTS (March 2026) |
| Spring references | Spring Boot 4 / Framework 7 |

## Conventions

- Code targets `--release 25` unless a block is explicitly labelled with an older baseline.
- Preview features carry a warning admonition naming the JDK version.
- All examples use one running domain: a grocery-marketplace **order & inventory engine**.
