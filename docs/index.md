---
title: Home
---

# Modern Java Enterprise Handbook

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
