---
title: "JEP Matrix (Java 8 → 26)"
status: review
---

# Appendix A — JEP Matrix (Java 8 → 26)

Every significant JDK Enhancement Proposal referenced in this handbook, by release, with its status and the chapter that covers it.

!!! info "Verification"
    JEP numbers and statuses for **Java 22–26** were checked in September 2026 against the OpenJDK page *JEPs in JDK 25 integrated since JDK 21* and the official JDK 25 and JDK 26 general-availability announcements. Earlier numbers follow the OpenJDK JEP index. Preview and incubator statuses change between releases — for anything newer than this page, check [openjdk.org/jeps](https://openjdk.org/jeps/0).

## How to read this

| Status | Meaning | Production use |
|---|---|---|
| **Final** | Permanent part of the platform | Yes |
| **Preview** | Complete, but may change or be withdrawn; needs `--enable-preview` | No — see [Ch 15](../02-language/15-string-templates-postmortem.md) |
| **Incubator** | Early API in a `jdk.incubator.*` module; expected to change | No |
| **Experimental** | A VM feature behind an unlock flag | Evaluation only |
| **Removal** | Takes something out of the platform | Plan for it |

**LTS releases** are 8, 11, 17, 21, and 25. LTS is a vendor support commitment, not a JDK property ([Ch 01](../01-platform/01-jdk-landscape.md)).

---

## Release by release

### Java 8 — 2014 · LTS

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 126 | Lambda expressions and virtual extension methods | Final | [06](../02-language/06-lambdas-functional-interfaces.md) |
| 107 | Bulk data operations for collections (Streams) | Final | [07](../02-language/07-stream-api.md) |
| 150 | Date and time API (`java.time`) | Final | [10](../02-language/10-java-time.md) |
| 122 | Remove the permanent generation (Metaspace) | Final | [02](../01-platform/02-jvm-runtime-model.md) |
| 155 | Concurrency updates (`LongAdder`, `StampedLock`, CHM rewrite) | Final | [27](../04-concurrency/27-locks-and-atomics.md), [30](../04-concurrency/30-concurrent-collections.md) |

### Java 9 — 2017

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 261 | Module system (JPMS) | Final | [11](../02-language/11-java-9-to-11.md) |
| 269 | Convenience factory methods for collections (`List.of`) | Final | [17](../03-collections/17-choosing-a-collection.md) |
| 193 | Variable handles (`VarHandle`) | Final | [26](../04-concurrency/26-java-memory-model.md) |
| 248 | G1 becomes the default collector | Final | [34](../05-runtime/34-garbage-collection.md) |
| 254 | Compact strings | Final | [35](../05-runtime/35-memory-footprint.md) |
| 280 | Indify string concatenation | Final | [03](../01-platform/03-toolchain.md) |
| 222 | `jshell` | Final | [03](../01-platform/03-toolchain.md) |
| 282 | `jlink` | Final | [03](../01-platform/03-toolchain.md) |
| 238 | Multi-release JAR files | Final | [03](../01-platform/03-toolchain.md) |
| 252 | CLDR locale data by default | Final | [05](../01-platform/05-migration-strategy.md) |
| 266 | More concurrency updates (Flow API, `CompletableFuture` timeouts) | Final | [29](../04-concurrency/29-completable-future.md) |

### Java 10 — 2018

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 286 | Local-variable type inference (`var`) | Final | [11](../02-language/11-java-9-to-11.md) |
| 310 | Application Class-Data Sharing | Final | [36](../05-runtime/36-startup-and-leyden.md) |

### Java 11 — 2018 · LTS

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 321 | HTTP Client (standard) | Final | [40](../05-runtime/40-http-client.md) |
| 323 | `var` in lambda parameters | Final | [11](../02-language/11-java-9-to-11.md) |
| 330 | Launch single-file source-code programs | Final | [03](../01-platform/03-toolchain.md) |
| 328 | Flight Recorder (open-sourced) | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 320 | Remove the Java EE and CORBA modules | Removal | [05](../01-platform/05-migration-strategy.md) |
| 333 | ZGC | Experimental | [34](../05-runtime/34-garbage-collection.md) |

### Java 12–13

| JEP | Feature | Status | Release | Chapter |
|---|---|---|---|---|
| 341 | Default CDS archives | Final | 12 | [36](../05-runtime/36-startup-and-leyden.md) |
| 350 | Dynamic CDS archives | Final | 13 | [36](../05-runtime/36-startup-and-leyden.md) |

### Java 14

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 361 | Switch expressions | Final | [12](../02-language/12-java-14-to-17.md) |
| 358 | Helpful `NullPointerException`s | Final | [09](../02-language/09-optional.md) |
| 349 | JFR event streaming | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 363 | Remove the CMS collector | Removal | [34](../05-runtime/34-garbage-collection.md) |

### Java 15

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 378 | Text blocks | Final | [12](../02-language/12-java-14-to-17.md) |
| 377 | ZGC — production-ready | Final | [34](../05-runtime/34-garbage-collection.md) |
| 379 | Shenandoah — production-ready | Final | [34](../05-runtime/34-garbage-collection.md) |
| 372 | Remove the Nashorn JavaScript engine | Removal | [05](../01-platform/05-migration-strategy.md) |
| 374 | Disable and deprecate biased locking | Deprecation | [25](../04-concurrency/25-shared-state.md) |

### Java 16

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 395 | Records | Final | [12](../02-language/12-java-14-to-17.md) |
| 394 | Pattern matching for `instanceof` | Final | [13](../02-language/13-pattern-matching.md) |
| 396 | Strongly encapsulate JDK internals by default | Final | [11](../02-language/11-java-9-to-11.md) |
| 338 | Vector API | Incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |

### Java 17 — 2021 · LTS

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 409 | Sealed classes | Final | [12](../02-language/12-java-14-to-17.md) |
| 403 | Strongly encapsulate JDK internals (remove `--illegal-access`) | Final | [05](../01-platform/05-migration-strategy.md) |
| 411 | Deprecate the Security Manager for removal | Deprecation | [05](../01-platform/05-migration-strategy.md) |

### Java 18–20

| JEP | Feature | Status | Release | Chapter |
|---|---|---|---|---|
| 400 | UTF-8 by default | Final | 18 | [04](../01-platform/04-builds-and-preview-features.md) |
| 421 | Deprecate finalization for removal | Deprecation | 18 | [05](../01-platform/05-migration-strategy.md) |
| 425 | Virtual threads | Preview | 19 | [31](../04-concurrency/31-virtual-threads.md) |
| 428 | Structured concurrency | Incubator | 19 | [32](../04-concurrency/32-structured-concurrency.md) |
| 429 | Scoped values | Incubator | 20 | [33](../04-concurrency/33-scoped-values.md) |

### Java 21 — 2023 · LTS

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 444 | **Virtual threads** | **Final** | [31](../04-concurrency/31-virtual-threads.md) |
| 441 | **Pattern matching for `switch`** | **Final** | [13](../02-language/13-pattern-matching.md) |
| 440 | **Record patterns** | **Final** | [13](../02-language/13-pattern-matching.md) |
| 431 | **Sequenced collections** | **Final** | [21](../03-collections/21-sequenced-collections.md) |
| 439 | Generational ZGC | Final (opt-in) | [34](../05-runtime/34-garbage-collection.md) |
| 453 | Structured concurrency | Preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 446 | Scoped values | Preview | [33](../04-concurrency/33-scoped-values.md) |
| 430 | String templates | Preview — **later withdrawn** | [15](../02-language/15-string-templates-postmortem.md) |
| 442 | Foreign Function & Memory API | Third preview | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 443 | Unnamed patterns and variables | Preview | [14](../02-language/14-java-21-to-26.md) |
| 445 | Unnamed classes and instance main methods | Preview | [14](../02-language/14-java-21-to-26.md) |

### Java 22 — 2024 · *verified*

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 454 | **Foreign Function & Memory API** | **Final** | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 456 | **Unnamed variables and patterns** | **Final** | [14](../02-language/14-java-21-to-26.md) |
| 458 | **Launch multi-file source-code programs** | **Final** | [03](../01-platform/03-toolchain.md) |
| 423 | Region pinning for G1 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 461 | Stream gatherers | Preview | [38](../05-runtime/38-stream-gatherers.md) |
| 459 | String templates | Second preview — **later withdrawn** | [15](../02-language/15-string-templates-postmortem.md) |
| 447 | Statements before `super(...)` | Preview | [14](../02-language/14-java-21-to-26.md) |

### Java 23 — 2024 · *verified*

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 467 | **Markdown documentation comments** | **Final** | [14](../02-language/14-java-21-to-26.md) |
| 474 | **ZGC: generational mode by default** | **Final** | [34](../05-runtime/34-garbage-collection.md) |
| 471 | Deprecate `sun.misc.Unsafe` memory-access methods for removal | Deprecation | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 473 | Stream gatherers | Second preview | [38](../05-runtime/38-stream-gatherers.md) |
| 455 | Primitive types in patterns | Preview | [13](../02-language/13-pattern-matching.md) |
| — | String templates | **Withdrawn — not in 23** | [15](../02-language/15-string-templates-postmortem.md) |

### Java 24 — 2025 · *verified*

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 491 | **Synchronize virtual threads without pinning** | **Final** | [31](../04-concurrency/31-virtual-threads.md), [25](../04-concurrency/25-shared-state.md) |
| 485 | **Stream gatherers** | **Final** | [38](../05-runtime/38-stream-gatherers.md) |
| 483 | **Ahead-of-time class loading and linking** | **Final** | [36](../05-runtime/36-startup-and-leyden.md) |
| 484 | **Class-File API** | **Final** | — |
| 475 | Late barrier expansion for G1 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 490 | ZGC: remove the non-generational mode | Removal | [34](../05-runtime/34-garbage-collection.md) |
| 486 | Permanently disable the Security Manager | Removal | [05](../01-platform/05-migration-strategy.md) |
| 479 | Remove the Windows 32-bit x86 port | Removal | [05](../01-platform/05-migration-strategy.md) |
| 472 | Prepare to restrict the use of JNI | Final (warnings) | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 498 | Warn upon use of memory-access methods in `sun.misc.Unsafe` | Final (warnings) | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 493 | Linking run-time images without JMODs | Final | [03](../01-platform/03-toolchain.md) |
| 496, 497 | Quantum-resistant ML-KEM and ML-DSA | Final | — |

### Java 25 — 2025 · LTS · *verified*

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 506 | **Scoped values** | **Final** | [33](../04-concurrency/33-scoped-values.md) |
| 513 | **Flexible constructor bodies** | **Final** | [14](../02-language/14-java-21-to-26.md) |
| 511 | **Module import declarations** | **Final** | [14](../02-language/14-java-21-to-26.md) |
| 512 | **Compact source files and instance main methods** | **Final** | [14](../02-language/14-java-21-to-26.md) |
| 519 | **Compact object headers** | **Final** | [35](../05-runtime/35-memory-footprint.md) |
| 521 | **Generational Shenandoah** | **Final** | [34](../05-runtime/34-garbage-collection.md) |
| 510 | Key derivation function API | Final | — |
| 514 | Ahead-of-time command-line ergonomics | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 515 | Ahead-of-time method profiling | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 518 | JFR cooperative sampling | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 520 | JFR method timing and tracing | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 509 | JFR CPU-time profiling | **Experimental** | [37](../05-runtime/37-profiling-jfr.md) |
| 505 | Structured concurrency | Fifth preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 507 | Primitive types in patterns | Third preview | [13](../02-language/13-pattern-matching.md) |
| 502 | Stable values | Preview | — |
| 470 | PEM encodings of cryptographic objects | Preview | — |
| 508 | Vector API | Tenth incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 503 | Remove the 32-bit x86 port | Removal | [05](../01-platform/05-migration-strategy.md) |

### Java 26 — March 2026 · *verified*

| JEP | Feature | Status | Chapter |
|---|---|---|---|
| 517 | **HTTP/3 for the HTTP Client API** | **Final** | [40](../05-runtime/40-http-client.md) |
| 516 | **Ahead-of-time object caching with any GC** | **Final** | [36](../05-runtime/36-startup-and-leyden.md) |
| 522 | **G1: improve throughput by reducing synchronisation** | **Final** | [34](../05-runtime/34-garbage-collection.md) |
| 500 | Prepare to make final mean final | Final (warnings) | [26](../04-concurrency/26-java-memory-model.md), [22](../03-collections/22-immutability.md) |
| 504 | Remove the Applet API | Removal | [05](../01-platform/05-migration-strategy.md) |
| 525 | Structured concurrency — adds `Joiner.onTimeout()` | Sixth preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 530 | Primitive types in patterns | Fourth preview | [13](../02-language/13-pattern-matching.md) |
| 526 | Lazy constants (formerly stable values) | Second preview | — |
| 524 | PEM encodings of cryptographic objects | Second preview | — |
| 529 | Vector API | Eleventh incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |

---

## Feature lineages

How long each feature took from first appearance to final — and which never got there.

| Feature | Path | Final in | Previews / incubations |
|---|---|---|---|
| Switch expressions | 325 → 354 → **361** | 14 | 2 |
| Text blocks | 355 → 368 → **378** | 15 | 2 |
| Records | 359 → 384 → **395** | 16 | 2 |
| `instanceof` patterns | 305 → 375 → **394** | 16 | 2 |
| Sealed classes | 360 → 397 → **409** | 17 | 2 |
| Pattern matching for `switch` | 406 → 420 → 427 → 433 → **441** | 21 | 4 |
| Record patterns | 405 → 432 → **440** | 21 | 2 |
| Virtual threads | 425 → 436 → **444** | 21 | 2 |
| Foreign Function & Memory | 412 → 419 → 424 → 434 → 442 → **454** | 22 | 5 |
| Unnamed variables and patterns | 443 → **456** | 22 | 1 |
| Stream gatherers | 461 → 473 → **485** | 24 | 2 |
| Scoped values | 429 → 446 → 464 → 481 → 487 → **506** | 25 | 5 |
| Flexible constructor bodies | 447 → 482 → 492 → **513** | 25 | 3 |
| Module import declarations | 476 → 494 → **511** | 25 | 2 |
| Compact source files | 445 → 463 → 477 → 495 → **512** | 25 | 4 |
| Compact object headers | 450 (experimental) → **519** | 25 | 1 |
| Generational Shenandoah | 404 (experimental) → **521** | 25 | 1 |
| **Structured concurrency** | 428 → 437 → 453 → 462 → 480 → 499 → 505 → 525 | **Not yet** | 8 and counting |
| **Primitive types in patterns** | 455 → 488 → 507 → 530 | **Not yet** | 4 and counting |
| **Vector API** | 338 → … → 508 → 529 | **Not yet** | 11 incubations since Java 16 |
| **String templates** | 430 → 459 → *withdrawn* | **Never** | 2, then removed |

Two patterns stand out. Most language features take **two previews**; the ones that took four or five changed shape substantially along the way. And structured concurrency, the Vector API, and String Templates show the full range of outcomes for a preview feature: still evolving, waiting on another project, or withdrawn — which is why [Chapter 15](../02-language/15-string-templates-postmortem.md) and [Chapter 04](../01-platform/04-builds-and-preview-features.md) recommend keeping preview features out of anything you cannot rewrite.

---

## Still not final as of Java 26

| Feature | Current JEP | Status | Blocked on |
|---|---|---|---|
| Structured concurrency | 525 | Sixth preview | API refinement |
| Primitive types in patterns | 530 | Fourth preview | Language design |
| Lazy constants | 526 | Second preview | API refinement |
| PEM encodings | 524 | Second preview | API refinement |
| Vector API | 529 | Eleventh incubator | **Project Valhalla** |

---

## Removals to plan for

| Removed | Release | JEP | Replacement |
|---|---|---|---|
| Java EE and CORBA modules | 11 | 320 | Jakarta EE dependencies |
| CMS collector | 14 | 363 | G1, ZGC, Shenandoah |
| Nashorn | 15 | 372 | GraalJS or another engine |
| `--illegal-access` | 17 | 403 | `--add-opens`, or upgrade the library |
| Security Manager (disabled) | 24 | 486 | Process and container isolation |
| Non-generational ZGC | 24 | 490 | Generational ZGC |
| 32-bit x86 ports | 24–25 | 479, 503 | 64-bit |
| Applet API | 26 | 504 | — |
| `sun.misc.Unsafe` memory access | Future | 471, 498 | FFM and `VarHandle` |
| Finalization | Future | 421 | `Cleaner`, try-with-resources |
