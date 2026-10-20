---
title: Examples
status: review
---

# Examples

Short, complete programs you can run — **80 examples**, each shown with the exact output it produced.
The chapters explain *why*; these pages show *what happens*.

!!! tip "Java 8 examples are in the Java 8 tab"
    [Java 8 by Example](java-8.md) is listed under the **[Java 8](../java8/index.md)** tab, next to the
    Java 8 chapters and interview workbook. It is included in the table below for completeness.

| Page | Examples |
|---|---|
| [How HashMap Works Inside](hashmap-internals.md) | 7 |
| [How ConcurrentHashMap Works Inside](concurrenthashmap-internals.md) | 7 |
| [CompletableFuture by Example](completablefuture.md) | 16 |
| [Concurrency Toolkit by Example](concurrency-toolkit.md) | 9 |
| [Java 8 by Example](java-8.md) | 13 |
| [Java 9 to 11 by Example](java-9-11.md) | 11 |
| [Java 12 to 17 by Example](java-12-17.md) | 10 |
| [Java 18 to 21 by Example](java-18-21.md) | 7 |

## How to run an example

Every example is a single file. With JDK 21 or later, no build tool is needed:

```bash
java HashSpreading.java
```

The sources live in `code/examples/` in this repository. A few examples look inside JDK classes and need an
`--add-opens` flag; the exact command is printed under each one.

!!! note "About the captured output"
    Outputs were captured on JDK 21 in a single-core container. Timings and the numbers in the race-condition
    demos vary between runs; where that matters, the page says so.
