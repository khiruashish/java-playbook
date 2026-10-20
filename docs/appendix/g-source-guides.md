---
title: Appendix G — Source Guide Map
status: review
---

# Appendix G — Source Guide Map

This handbook grew out of ten standalone guides. Their content now lives inside the chapters, expanded to the 9-part format, rewritten for the grocery order and inventory domain, and corrected for Java 25 and 26. This page shows where each part of each guide went, so if you remember something from a guide you can find its current home.

The original guides are kept unpublished in `_source/` in the repository, as raw material.

## The ten guides

| Guide | Level | Last updated | Now lives in |
|---|---|---|---|
| Java 8 — Enterprise Reference | Beginner → Architect | 2026-06-14 | [Ch 06](../02-language/06-lambdas-functional-interfaces.md)–[Ch 10](../02-language/10-java-time.md), the [Java 8](../java8/index.md) tab |
| Java 8 — Interview Guide | Intermediate → Senior | 2026-06-14 | Interview section (Section 9) of Ch 06–10, [Appendix B](b-java8-interview-workbook.md) |
| Java 21 — New Features | Intermediate → Senior | 2026-06-14 | [Ch 12](../02-language/12-java-14-to-17.md), [Ch 13](../02-language/13-pattern-matching.md), [Ch 14](../02-language/14-java-21-to-26.md), [Ch 15](../02-language/15-string-templates-postmortem.md), [Ch 21](../03-collections/21-sequenced-collections.md), [Ch 39](../05-runtime/39-ffm-and-vector-api.md) |
| Java 21 — Concurrency & Virtual Threads | Senior → Architect | 2026-06-14 | [Ch 31](../04-concurrency/31-virtual-threads.md), [Ch 32](../04-concurrency/32-structured-concurrency.md), [Ch 33](../04-concurrency/33-scoped-values.md), [Appendix C](c-concurrency-interview-bank.md) |
| Java Threading — Basics | Beginner → Intermediate | 2026-06-14 | [Ch 24](../04-concurrency/24-threading-fundamentals.md), [Ch 25](../04-concurrency/25-shared-state.md), [Ch 28](../04-concurrency/28-executors.md) |
| Java Threading — Enterprise | Senior → Architect | 2026-06-14 | [Ch 27](../04-concurrency/27-locks-and-atomics.md), [Ch 28](../04-concurrency/28-executors.md), [Ch 29](../04-concurrency/29-completable-future.md), [Ch 33](../04-concurrency/33-scoped-values.md), [Appendix C](c-concurrency-interview-bank.md) |
| Java List Guide | Beginner → Intermediate | 2026-06-14 | [Ch 17](../03-collections/17-choosing-a-collection.md), [Ch 18](../03-collections/18-list-internals.md), [Ch 21](../03-collections/21-sequenced-collections.md) |
| Custom ArrayList Implementation | Senior | 2026-06-14 | [Ch 18 §6.6](../03-collections/18-list-internals.md), [Ch 18 §6.7](../03-collections/18-list-internals.md) |
| HashMap — Deep Dive | Intermediate | 2026-06-14 | [Ch 19](../03-collections/19-hashmap-internals.md), [Ch 21](../03-collections/21-sequenced-collections.md), [HashMap internals by example](../07-examples/hashmap-internals.md) |
| ConcurrentHashMap Guide | Senior | 2026-06-14 | [Ch 30](../04-concurrency/30-concurrent-collections.md), [ConcurrentHashMap internals by example](../07-examples/concurrenthashmap-internals.md) |

## Section by section

### Java 8 — Enterprise Reference

| Guide section | Now in |
|---|---|
| Section 1 Introduction, Section 2 Functional programming concepts | [Ch 06](../02-language/06-lambdas-functional-interfaces.md) |
| Section 3 Lambda expressions, Section 4 Functional interfaces, Section 8 Method references, Section 9 Default methods | [Ch 06](../02-language/06-lambdas-functional-interfaces.md) |
| Section 5 Stream API (creation, operations, architecture), Section 12 Parallel streams | [Ch 07](../02-language/07-stream-api.md) |
| Section 5.6 Collectors | [Ch 08](../02-language/08-collectors.md) |
| Section 6 Optional | [Ch 09](../02-language/09-optional.md) |
| Section 7 Date and Time API | [Ch 10](../02-language/10-java-time.md) |
| Section 10 Nashorn, Section 14 Base64, Section 15.1 PermGen and Metaspace | [Java 8 overview](../java8/index.md#the-rest-of-java-8) |
| Section 11 CompletableFuture, Section 17.3 Parallel microservice calls | [Ch 29](../04-concurrency/29-completable-future.md) |
| Section 13 Collections improvements (`forEach`, `removeIf`, `replaceAll`, Map methods) | [Ch 18](../03-collections/18-list-internals.md), [Ch 19 §4.3](../03-collections/19-hashmap-internals.md) |
| Section 16 Enterprise best practices, Section 17 Project sketches | Production Patterns (Section 7) of Ch 06–10 |
| Section 18 Interview overview, Section 19 Cheat sheet | Interview (Section 9) of Ch 06–10, [Appendix E](e-cheat-sheets.md) |

### Java 8 — Interview Guide

| Guide section | Now in |
|---|---|
| Lambdas, functional interfaces, method references | [Ch 06 §9](../02-language/06-lambdas-functional-interfaces.md) |
| Streams, intermediate vs terminal, laziness | [Ch 07 §9](../02-language/07-stream-api.md) |
| Collectors and grouping | [Ch 08 §9](../02-language/08-collectors.md) |
| Optional | [Ch 09 §9](../02-language/09-optional.md) |
| Date and time | [Ch 10 §9](../02-language/10-java-time.md) |
| CompletableFuture | [Ch 29 §9](../04-concurrency/29-completable-future.md) |
| Nashorn, Base64 | [Java 8 overview](../java8/index.md#the-rest-of-java-8) |
| Coding exercises and scenario questions | [Appendix B](b-java8-interview-workbook.md), Part 1 |

### Collections guides

| Guide | Section | Now in |
|---|---|---|
| List | Choosing a list, interface overview | [Ch 17](../03-collections/17-choosing-a-collection.md) |
| List | `ArrayList` vs `LinkedList`, complexity, internals, fail-fast iteration | [Ch 18](../03-collections/18-list-internals.md) |
| List | `indexOf`, `lastIndexOf`, `ListIterator` | [Ch 18 §4.4](../03-collections/18-list-internals.md) |
| List | Immutable lists (`List.of`, `copyOf`, `unmodifiableList`) | [Ch 18 §4.1](../03-collections/18-list-internals.md), [Ch 22](../03-collections/22-immutability.md) |
| List | Sequenced collections | [Ch 21](../03-collections/21-sequenced-collections.md) |
| List | Streams on lists, grouping and partitioning | [Ch 07](../02-language/07-stream-api.md), [Ch 08](../02-language/08-collectors.md) |
| Custom ArrayList | Growth, `add`, `remove`, `fastRemove`, iterator | [Ch 18 §6.2](../03-collections/18-list-internals.md), [Ch 18 §6.6](../03-collections/18-list-internals.md) |
| HashMap | Hashing, buckets, treeification, resize | [Ch 19 §6.1](../03-collections/19-hashmap-internals.md), [HashMap internals by example](../07-examples/hashmap-internals.md) |
| HashMap | `put`/`get`/`compute`/`merge` API | [Ch 19 §4.2](../03-collections/19-hashmap-internals.md), [Ch 19 §4.3](../03-collections/19-hashmap-internals.md) |
| HashMap | Views, `putAll`, sorting entries by key or value, top-N, max by value | [Ch 19 §4.5](../03-collections/19-hashmap-internals.md) |
| HashMap | `equals`/`hashCode` contract, mutable keys | [Ch 19 §5.4](../03-collections/19-hashmap-internals.md), [Ch 23](../03-collections/23-equality-and-ordering.md) |
| ConcurrentHashMap | Atomic operations, `computeIfAbsent`, check-then-act | [Ch 30 §4.1](../04-concurrency/30-concurrent-collections.md), [Ch 30 §5.2](../04-concurrency/30-concurrent-collections.md) |
| ConcurrentHashMap | `putAll` and `clear` atomicity | [Ch 30 §4.4](../04-concurrency/30-concurrent-collections.md) |
| ConcurrentHashMap | Internals, sizing, bulk parallel operations | [Ch 30](../04-concurrency/30-concurrent-collections.md), [ConcurrentHashMap internals by example](../07-examples/concurrenthashmap-internals.md) |

### Concurrency and Java 21 guides

| Guide | Section | Now in |
|---|---|---|
| Threading Basics | Thread lifecycle, `join`, interruption, daemon threads | [Ch 24](../04-concurrency/24-threading-fundamentals.md) |
| Threading Basics | Race conditions, `synchronized`, `volatile`, deadlock, `wait`/`notify` | [Ch 25](../04-concurrency/25-shared-state.md) |
| Threading Basics | Executor basics | [Ch 28](../04-concurrency/28-executors.md) |
| Threading Enterprise | Locks, atomics, the `java.util.concurrent` toolbox | [Ch 27](../04-concurrency/27-locks-and-atomics.md) |
| Threading Enterprise | Thread pool design, `CompletableFuture` | [Ch 28](../04-concurrency/28-executors.md), [Ch 29](../04-concurrency/29-completable-future.md) |
| Threading Enterprise | `ThreadLocal` and context propagation | [Ch 33](../04-concurrency/33-scoped-values.md) |
| Java 21 Concurrency | Virtual threads, scheduling, pinning | [Ch 31](../04-concurrency/31-virtual-threads.md) |
| Java 21 Concurrency | Structured concurrency | [Ch 32](../04-concurrency/32-structured-concurrency.md) |
| Java 21 Features | Records, sealed types | [Ch 12](../02-language/12-java-14-to-17.md) |
| Java 21 Features | Pattern matching, record patterns | [Ch 13](../02-language/13-pattern-matching.md) |
| Java 21 Features | Unnamed variables and patterns | [Ch 14](../02-language/14-java-21-to-26.md) |
| Java 21 Features | Sequenced collections | [Ch 21](../03-collections/21-sequenced-collections.md) |
| Java 21 Features | Scoped values | [Ch 33](../04-concurrency/33-scoped-values.md) |
| Java 21 Features | String Templates | [Ch 15](../02-language/15-string-templates-postmortem.md) |
| Java 21 Features | Foreign Function & Memory API | [Ch 39](../05-runtime/39-ffm-and-vector-api.md) |

## What changed on the way in

The chapters intentionally differ from the guides in a few ways:

| In the guide | In the handbook | Why |
|---|---|---|
| String Templates shown as a Java 21 preview | [Ch 15](../02-language/15-string-templates-postmortem.md) explains why it was withdrawn | It was removed before final and is in no released JDK |
| `StructuredTaskScope.ShutdownOnFailure` / `ShutdownOnSuccess` | Joiner-based API, still preview in Java 26 | The API was redesigned across previews ([Ch 32](../04-concurrency/32-structured-concurrency.md)) |
| `ScopedValue` as a preview | Final since Java 25 | JEP 506 ([Ch 33](../04-concurrency/33-scoped-values.md)) |
| `@RestController`, `JdbcTemplate` and other Spring examples | Plain-JDK code only | This handbook stops at the JDK boundary; Spring is covered in its own handbook |
| `User`, `Employee`, `apple`/`banana` demo data | The grocery order and inventory domain (`Sku`, `CartLine`, `Order`) | One consistent domain across all chapters |
| Each collections guide repeated as its own "Appendix A" | One API table per chapter | The duplicates were about 40% of those files |
| ConcurrentHashMap `putAll` described as thread-safe | Thread-safe but **not atomic** | Readers can see a partially applied `putAll` ([Ch 30 §4.4](../04-concurrency/30-concurrent-collections.md)) |
