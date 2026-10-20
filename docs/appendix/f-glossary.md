---
title: Glossary & JEP Index
status: review
---

# Appendix F — Glossary & JEP Index

## Glossary

Terms as this handbook uses them, with the chapter that treats each in depth.

| Term | Meaning | Chapter |
|---|---|---|
| **ABA problem** | A compare-and-set succeeds because a value changed A → B → A, so the change goes unnoticed | [27](../04-concurrency/27-locks-and-atomics.md) |
| **Algebraic data type** | A sealed interface whose permitted implementations are records — a closed set of cases, each carrying its own data | [12](../02-language/12-java-14-to-17.md) |
| **AOT cache** | Project Leyden's cache of pre-loaded, pre-linked classes and JIT profiles, built from a training run | [36](../05-runtime/36-startup-and-leyden.md) |
| **AQS** | `AbstractQueuedSynchronizer` — one atomic `int` plus a queue of parked threads; the base of most `java.util.concurrent` synchronisers | [27](../04-concurrency/27-locks-and-atomics.md) |
| **Arena** | FFM's lifetime scope for off-heap memory; confined, shared, automatic, or global | [39](../05-runtime/39-ffm-and-vector-api.md) |
| **Backpressure** | A consumer slowing a producer, rather than buffering without limit | [28](../04-concurrency/28-executors.md) |
| **Band (L1–L4)** | This handbook's audience levels: Foundations, Professional, Enterprise, Architect | [Home](../index.md) |
| **Bridge method** | A synthetic method the compiler generates so overriding survives type erasure | [16](../02-language/16-generics.md) |
| **Bulkhead** | Separate capacity per dependency, so one slow downstream cannot exhaust shared resources | [28](../04-concurrency/28-executors.md) |
| **Capture** | The compiler's fresh name for each wildcard occurrence; why a `List<?>` cannot be written back to | [16](../02-language/16-generics.md) |
| **Carrier thread** | A platform thread on which virtual threads are mounted and run | [31](../04-concurrency/31-virtual-threads.md) |
| **CAS** | Compare-and-set — a single hardware instruction that updates memory only if it holds an expected value | [27](../04-concurrency/27-locks-and-atomics.md) |
| **CDS** | Class Data Sharing — an archive of pre-parsed, pre-verified classes memory-mapped at startup | [36](../05-runtime/36-startup-and-leyden.md) |
| **Classpath Exception** | The clause in OpenJDK's GPLv2 licence that lets proprietary code link against the JDK without GPL obligations | [01](../01-platform/01-jdk-landscape.md) |
| **Code cache** | Native memory holding JIT-compiled code; when full, JIT compilation stops silently | [02](../01-platform/02-jvm-runtime-model.md) |
| **Collector** | A mutable reduction — supplier, accumulator, combiner, finisher, characteristics — used by `collect` | [08](../02-language/08-collectors.md) |
| **Compact object headers** | Java 25's 8-byte object header, down from 12 | [35](../05-runtime/35-memory-footprint.md) |
| **Compact source file** | A source file with no class declaration, run directly with `java File.java` | [14](../02-language/14-java-21-to-26.md) |
| **Compressed oops** | 32-bit object references scaled by alignment; available below about 32 GB of heap | [35](../05-runtime/35-memory-footprint.md) |
| **Container support** | The JVM reading cgroup CPU and memory limits rather than the host's; on by default since 10 | [02](../01-platform/02-jvm-runtime-model.md) |
| **Data race** | Two accesses to the same variable from different threads, one a write, with no happens-before ordering | [26](../04-concurrency/26-java-memory-model.md) |
| **Defensive copy** | Copying mutable input in a constructor, or output from an accessor, so callers cannot alter internal state | [22](../03-collections/22-immutability.md) |
| **Deoptimisation** | Discarding JIT-compiled code whose profiling assumptions were violated; shown as `made not entrant` | [02](../01-platform/02-jvm-runtime-model.md) |
| **Dominance** | A pattern case that can never match because an earlier case always matches first — a compile error | [13](../02-language/13-pattern-matching.md) |
| **DRF-SC** | Data-race-free programs behave as if sequentially consistent — the Java Memory Model's central guarantee | [26](../04-concurrency/26-java-memory-model.md) |
| **Effectively final** | A local never reassigned after initialisation; required for lambda capture | [06](../02-language/06-lambdas-functional-interfaces.md) |
| **Encounter order** | The defined first-to-last order of a collection; `HashMap` and `HashSet` have none | [21](../03-collections/21-sequenced-collections.md) |
| **Erasure** | The removal of generic type arguments after compile-time checking | [16](../02-language/16-generics.md) |
| **Escape analysis** | A JIT proof that an object never leaves its method, allowing its allocation to be eliminated | [02](../01-platform/02-jvm-runtime-model.md) |
| **Exhaustiveness** | The compiler's proof that a switch covers every case of an enum or sealed type | [13](../02-language/13-pattern-matching.md) |
| **Fail-fast iterator** | An iterator that throws `ConcurrentModificationException` on structural change — best-effort, not guaranteed | [17](../03-collections/17-choosing-a-collection.md) |
| **Final-field freeze** | The JMM guarantee that final fields are visible as the constructor left them, however the object is published | [26](../04-concurrency/26-java-memory-model.md) |
| **Flow scoping** | A pattern binding is in scope wherever the compiler can prove the match succeeded | [13](../02-language/13-pattern-matching.md) |
| **ForkJoinPool common pool** | The JVM-wide pool shared by parallel streams and default `CompletableFuture` async stages | [28](../04-concurrency/28-executors.md) |
| **Gatherer** | A user-defined intermediate stream operation: initializer, integrator, combiner, finisher | [38](../05-runtime/38-stream-gatherers.md) |
| **Generational hypothesis** | Most objects die young — the observation generational collectors are built on | [34](../05-runtime/34-garbage-collection.md) |
| **Happens-before** | The JMM ordering relation: if A happens-before B, A's effects are visible to B | [26](../04-concurrency/26-java-memory-model.md) |
| **Head-of-line blocking** | One stalled request delaying those behind it; HTTP/2 removes it at the application layer, HTTP/3 at transport | [40](../05-runtime/40-http-client.md) |
| **Heap pollution** | A variable of a parameterised type referring to an object of a different type, typically via generic varargs | [16](../02-language/16-generics.md) |
| **Humongous object** | In G1, an object larger than half a region, allocated straight into old-generation regions | [34](../05-runtime/34-garbage-collection.md) |
| **Idempotency key** | A client-supplied identifier letting a server recognise a retried request | [40](../05-runtime/40-http-client.md) |
| **Incubator** | An early API in a `jdk.incubator.*` module, expected to change | [A](a-jep-matrix.md) |
| **`invokedynamic`** | A bytecode whose call target is decided at runtime by a bootstrap method; behind lambdas, string concatenation, records, pattern switches | [06](../02-language/06-lambdas-functional-interfaces.md) |
| **JFR** | Java Flight Recorder — the JVM's built-in, low-overhead event recorder | [37](../05-runtime/37-profiling-jfr.md) |
| **JMM** | Java Memory Model — the specification of what values a read may return across threads | [26](../04-concurrency/26-java-memory-model.md) |
| **JPMS** | Java Platform Module System, introduced in Java 9 | [11](../02-language/11-java-9-to-11.md) |
| **Live set** | The objects still reachable after a collection; a steadily growing live set is a leak | [34](../05-runtime/34-garbage-collection.md) |
| **Livelock** | Threads that keep running and responding to each other without making progress | [25](../04-concurrency/25-shared-state.md) |
| **Load barrier** | Code on every reference load that lets ZGC relocate objects concurrently | [34](../05-runtime/34-garbage-collection.md) |
| **LTS** | Long-term support — a vendor commitment to backport fixes for years; not a JDK behaviour | [01](../01-platform/01-jdk-landscape.md) |
| **`MatchException`** | Thrown when an exhaustive switch meets a case added after it was compiled | [13](../02-language/13-pattern-matching.md) |
| **Memory barrier** | An instruction preventing the CPU and compiler from reordering memory operations across it | [26](../04-concurrency/26-java-memory-model.md) |
| **Metaspace** | Native memory holding class metadata; unbounded by default | [02](../01-platform/02-jvm-runtime-model.md) |
| **Monitor** | The lock every object carries, acquired by `synchronized` | [25](../04-concurrency/25-shared-state.md) |
| **Multi-release JAR** | A JAR with version-specific classes under `META-INF/versions/N` | [03](../01-platform/03-toolchain.md) |
| **Native image** | GraalVM's ahead-of-time compiled executable — instant start, closed world, lower peak throughput | [36](../05-runtime/36-startup-and-leyden.md) |
| **PECS** | Producer Extends, Consumer Super — the rule for choosing wildcards | [16](../02-language/16-generics.md) |
| **Pinning** | A virtual thread holding its carrier while blocked; `synchronized` pinned until Java 24 | [31](../04-concurrency/31-virtual-threads.md) |
| **Preview feature** | A complete feature that may change or be withdrawn; needs `--enable-preview`; class files bind to one JDK | [04](../01-platform/04-builds-and-preview-features.md), [15](../02-language/15-string-templates-postmortem.md) |
| **QUIC** | The UDP-based transport under HTTP/3, with independent streams | [40](../05-runtime/40-http-client.md) |
| **Record** | A transparent, shallowly immutable carrier whose `equals`, `hashCode`, and `toString` derive from its components | [12](../02-language/12-java-14-to-17.md) |
| **Reentrant** | A lock the owning thread may acquire again without deadlocking itself | [25](../04-concurrency/25-shared-state.md) |
| **`--release`** | The `javac` flag that targets an older Java version **including its API** — never `-source`/`-target` | [01](../01-platform/01-jdk-landscape.md) |
| **Retained size** | Everything that would become collectable if an object were released | [35](../05-runtime/35-memory-footprint.md) |
| **Safe publication** | Making an object's reference and its constructed state visible to other threads together | [26](../04-concurrency/26-java-memory-model.md) |
| **Safepoint bias** | Profilers that sample only at safepoints misattribute time, missing tight loops | [37](../05-runtime/37-profiling-jfr.md) |
| **Scoped value** | An immutable binding visible for the dynamic extent of a block; the replacement for request-context `ThreadLocal` | [33](../04-concurrency/33-scoped-values.md) |
| **Sealed type** | A class or interface whose permitted subtypes are declared and enforced at class load | [12](../02-language/12-java-14-to-17.md) |
| **Sequenced collection** | A collection with a defined encounter order and a uniform API for its ends | [21](../03-collections/21-sequenced-collections.md) |
| **Spliterator** | The iterator underlying every stream, able to split itself for parallel work | [07](../02-language/07-stream-api.md) |
| **Start gate** | A latch that releases all test threads at once so they genuinely overlap | [44](../06-testing/44-testing-concurrency.md) |
| **State verification** | Asserting on results rather than on interactions with collaborators | [42](../06-testing/42-mockito.md) |
| **Structured concurrency** | Subtasks whose lifetime is bounded by a lexical scope; failure cancels siblings | [32](../04-concurrency/32-structured-concurrency.md) |
| **Target typing** | A lambda taking its type from the context it appears in | [06](../02-language/06-lambdas-functional-interfaces.md) |
| **Test double** | A stand-in for a collaborator: dummy, stub, spy, mock, or fake | [42](../06-testing/42-mockito.md) |
| **TLAB** | Thread-local allocation buffer — why allocation is usually a pointer bump | [34](../05-runtime/34-garbage-collection.md) |
| **Treeification** | A `HashMap` bin converting from a list to a red-black tree at eight entries, if the table has at least 64 bins | [19](../03-collections/19-hashmap-internals.md) |
| **Value-based class** | A class whose instances should be compared by `equals`, never by identity — `Optional`, `java.time` | [09](../02-language/09-optional.md) |
| **`VarHandle`** | Typed access to variables with explicit memory-ordering modes; replaces `Unsafe` for atomics | [26](../04-concurrency/26-java-memory-model.md) |
| **View** | A collection backed by another — `subList`, `keySet`, `reversed()`, `unmodifiableList` — that reflects its changes | [21](../03-collections/21-sequenced-collections.md) |
| **Virtual thread** | A JVM-managed thread whose stack lives on the heap and which unmounts when it blocks | [31](../04-concurrency/31-virtual-threads.md) |
| **Volatile** | A field guaranteeing visibility and ordering for single reads and writes — not atomicity | [25](../04-concurrency/25-shared-state.md) |
| **Wait strategy** | Testcontainers' readiness check before handing a container to a test | [43](../06-testing/43-integration-testing.md) |
| **Weakly consistent iterator** | A concurrent-collection iterator that never throws and may or may not reflect concurrent updates | [30](../04-concurrency/30-concurrent-collections.md) |
| **Wither** | A method returning a copy of an immutable object with one component changed | [22](../03-collections/22-immutability.md) |
| **Word tearing** | A non-volatile `long` or `double` write observed half-complete by another thread | [26](../04-concurrency/26-java-memory-model.md) |

---

## JEP index

Every JEP in [Appendix A](a-jep-matrix.md), by number. Generated from Appendix A by `tools/build-glossary.py` — edit A, not this table.

| JEP | Feature | Release | Status | Chapter |
|---|---|---|---|---|
| 107 | Bulk data operations for collections (Streams) | 8 | Final | [07](../02-language/07-stream-api.md) |
| 122 | Remove the permanent generation (Metaspace) | 8 | Final | [02](../01-platform/02-jvm-runtime-model.md) |
| 126 | Lambda expressions and virtual extension methods | 8 | Final | [06](../02-language/06-lambdas-functional-interfaces.md) |
| 150 | Date and time API (`java.time`) | 8 | Final | [10](../02-language/10-java-time.md) |
| 155 | Concurrency updates (`LongAdder`, `StampedLock`, CHM rewrite) | 8 | Final | [27](../04-concurrency/27-locks-and-atomics.md), [30](../04-concurrency/30-concurrent-collections.md) |
| 193 | Variable handles (`VarHandle`) | 9 | Final | [26](../04-concurrency/26-java-memory-model.md) |
| 222 | `jshell` | 9 | Final | [03](../01-platform/03-toolchain.md) |
| 238 | Multi-release JAR files | 9 | Final | [03](../01-platform/03-toolchain.md) |
| 248 | G1 becomes the default collector | 9 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 252 | CLDR locale data by default | 9 | Final | [05](../01-platform/05-migration-strategy.md) |
| 254 | Compact strings | 9 | Final | [35](../05-runtime/35-memory-footprint.md) |
| 261 | Module system (JPMS) | 9 | Final | [11](../02-language/11-java-9-to-11.md) |
| 266 | More concurrency updates (Flow API, `CompletableFuture` timeouts) | 9 | Final | [29](../04-concurrency/29-completable-future.md) |
| 269 | Convenience factory methods for collections (`List.of`) | 9 | Final | [17](../03-collections/17-choosing-a-collection.md) |
| 280 | Indify string concatenation | 9 | Final | [03](../01-platform/03-toolchain.md) |
| 282 | `jlink` | 9 | Final | [03](../01-platform/03-toolchain.md) |
| 286 | Local-variable type inference (`var`) | 10 | Final | [11](../02-language/11-java-9-to-11.md) |
| 310 | Application Class-Data Sharing | 10 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 320 | Remove the Java EE and CORBA modules | 11 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 321 | HTTP Client (standard) | 11 | Final | [40](../05-runtime/40-http-client.md) |
| 323 | `var` in lambda parameters | 11 | Final | [11](../02-language/11-java-9-to-11.md) |
| 328 | Flight Recorder (open-sourced) | 11 | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 330 | Launch single-file source-code programs | 11 | Final | [03](../01-platform/03-toolchain.md) |
| 333 | ZGC | 11 | Experimental | [34](../05-runtime/34-garbage-collection.md) |
| 338 | Vector API | 16 | Incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 341 | Default CDS archives | 12 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 349 | JFR event streaming | 14 | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 350 | Dynamic CDS archives | 13 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 358 | Helpful `NullPointerException`s | 14 | Final | [09](../02-language/09-optional.md) |
| 361 | Switch expressions | 14 | Final | [12](../02-language/12-java-14-to-17.md) |
| 363 | Remove the CMS collector | 14 | Removal | [34](../05-runtime/34-garbage-collection.md) |
| 372 | Remove the Nashorn JavaScript engine | 15 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 374 | Disable and deprecate biased locking | 15 | Deprecation | [25](../04-concurrency/25-shared-state.md) |
| 377 | ZGC — production-ready | 15 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 378 | Text blocks | 15 | Final | [12](../02-language/12-java-14-to-17.md) |
| 379 | Shenandoah — production-ready | 15 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 394 | Pattern matching for `instanceof` | 16 | Final | [13](../02-language/13-pattern-matching.md) |
| 395 | Records | 16 | Final | [12](../02-language/12-java-14-to-17.md) |
| 396 | Strongly encapsulate JDK internals by default | 16 | Final | [11](../02-language/11-java-9-to-11.md) |
| 400 | UTF-8 by default | 18 | Final | [04](../01-platform/04-builds-and-preview-features.md) |
| 403 | Strongly encapsulate JDK internals (remove `--illegal-access`) | 17 | Final | [05](../01-platform/05-migration-strategy.md) |
| 409 | Sealed classes | 17 | Final | [12](../02-language/12-java-14-to-17.md) |
| 411 | Deprecate the Security Manager for removal | 17 | Deprecation | [05](../01-platform/05-migration-strategy.md) |
| 421 | Deprecate finalization for removal | 18 | Deprecation | [05](../01-platform/05-migration-strategy.md) |
| 423 | Region pinning for G1 | 22 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 425 | Virtual threads | 19 | Preview | [31](../04-concurrency/31-virtual-threads.md) |
| 428 | Structured concurrency | 19 | Incubator | [32](../04-concurrency/32-structured-concurrency.md) |
| 429 | Scoped values | 20 | Incubator | [33](../04-concurrency/33-scoped-values.md) |
| 430 | String templates | 21 | Preview — later withdrawn | [15](../02-language/15-string-templates-postmortem.md) |
| 431 | Sequenced collections | 21 | Final | [21](../03-collections/21-sequenced-collections.md) |
| 439 | Generational ZGC | 21 | Final (opt-in) | [34](../05-runtime/34-garbage-collection.md) |
| 440 | Record patterns | 21 | Final | [13](../02-language/13-pattern-matching.md) |
| 441 | Pattern matching for `switch` | 21 | Final | [13](../02-language/13-pattern-matching.md) |
| 442 | Foreign Function & Memory API | 21 | Third preview | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 443 | Unnamed patterns and variables | 21 | Preview | [14](../02-language/14-java-21-to-26.md) |
| 444 | Virtual threads | 21 | Final | [31](../04-concurrency/31-virtual-threads.md) |
| 445 | Unnamed classes and instance main methods | 21 | Preview | [14](../02-language/14-java-21-to-26.md) |
| 446 | Scoped values | 21 | Preview | [33](../04-concurrency/33-scoped-values.md) |
| 447 | Statements before `super(...)` | 22 | Preview | [14](../02-language/14-java-21-to-26.md) |
| 453 | Structured concurrency | 21 | Preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 454 | Foreign Function & Memory API | 22 | Final | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 455 | Primitive types in patterns | 23 | Preview | [13](../02-language/13-pattern-matching.md) |
| 456 | Unnamed variables and patterns | 22 | Final | [14](../02-language/14-java-21-to-26.md) |
| 458 | Launch multi-file source-code programs | 22 | Final | [03](../01-platform/03-toolchain.md) |
| 459 | String templates | 22 | Second preview — later withdrawn | [15](../02-language/15-string-templates-postmortem.md) |
| 461 | Stream gatherers | 22 | Preview | [38](../05-runtime/38-stream-gatherers.md) |
| 467 | Markdown documentation comments | 23 | Final | [14](../02-language/14-java-21-to-26.md) |
| 470 | PEM encodings of cryptographic objects | 25 | Preview | — |
| 471 | Deprecate `sun.misc.Unsafe` memory-access methods for removal | 23 | Deprecation | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 472 | Prepare to restrict the use of JNI | 24 | Final (warnings) | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 473 | Stream gatherers | 23 | Second preview | [38](../05-runtime/38-stream-gatherers.md) |
| 474 | ZGC: generational mode by default | 23 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 475 | Late barrier expansion for G1 | 24 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 479 | Remove the Windows 32-bit x86 port | 24 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 483 | Ahead-of-time class loading and linking | 24 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 484 | Class-File API | 24 | Final | — |
| 485 | Stream gatherers | 24 | Final | [38](../05-runtime/38-stream-gatherers.md) |
| 486 | Permanently disable the Security Manager | 24 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 490 | ZGC: remove the non-generational mode | 24 | Removal | [34](../05-runtime/34-garbage-collection.md) |
| 491 | Synchronize virtual threads without pinning | 24 | Final | [31](../04-concurrency/31-virtual-threads.md), [25](../04-concurrency/25-shared-state.md) |
| 493 | Linking run-time images without JMODs | 24 | Final | [03](../01-platform/03-toolchain.md) |
| 496 | Quantum-resistant ML-KEM and ML-DSA | 24 | Final | — |
| 497 | Quantum-resistant ML-KEM and ML-DSA | 24 | Final | — |
| 498 | Warn upon use of memory-access methods in `sun.misc.Unsafe` | 24 | Final (warnings) | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 500 | Prepare to make final mean final | 26 | Final (warnings) | [26](../04-concurrency/26-java-memory-model.md), [22](../03-collections/22-immutability.md) |
| 502 | Stable values | 25 | Preview | — |
| 503 | Remove the 32-bit x86 port | 25 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 504 | Remove the Applet API | 26 | Removal | [05](../01-platform/05-migration-strategy.md) |
| 505 | Structured concurrency | 25 | Fifth preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 506 | Scoped values | 25 | Final | [33](../04-concurrency/33-scoped-values.md) |
| 507 | Primitive types in patterns | 25 | Third preview | [13](../02-language/13-pattern-matching.md) |
| 508 | Vector API | 25 | Tenth incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 509 | JFR CPU-time profiling | 25 | Experimental | [37](../05-runtime/37-profiling-jfr.md) |
| 510 | Key derivation function API | 25 | Final | — |
| 511 | Module import declarations | 25 | Final | [14](../02-language/14-java-21-to-26.md) |
| 512 | Compact source files and instance main methods | 25 | Final | [14](../02-language/14-java-21-to-26.md) |
| 513 | Flexible constructor bodies | 25 | Final | [14](../02-language/14-java-21-to-26.md) |
| 514 | Ahead-of-time command-line ergonomics | 25 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 515 | Ahead-of-time method profiling | 25 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 516 | Ahead-of-time object caching with any GC | 26 | Final | [36](../05-runtime/36-startup-and-leyden.md) |
| 517 | HTTP/3 for the HTTP Client API | 26 | Final | [40](../05-runtime/40-http-client.md) |
| 518 | JFR cooperative sampling | 25 | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 519 | Compact object headers | 25 | Final | [35](../05-runtime/35-memory-footprint.md) |
| 520 | JFR method timing and tracing | 25 | Final | [37](../05-runtime/37-profiling-jfr.md) |
| 521 | Generational Shenandoah | 25 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 522 | G1: improve throughput by reducing synchronisation | 26 | Final | [34](../05-runtime/34-garbage-collection.md) |
| 524 | PEM encodings of cryptographic objects | 26 | Second preview | — |
| 525 | Structured concurrency — adds `Joiner.onTimeout()` | 26 | Sixth preview | [32](../04-concurrency/32-structured-concurrency.md) |
| 526 | Lazy constants (formerly stable values) | 26 | Second preview | — |
| 529 | Vector API | 26 | Eleventh incubator | [39](../05-runtime/39-ffm-and-vector-api.md) |
| 530 | Primitive types in patterns | 26 | Fourth preview | [13](../02-language/13-pattern-matching.md) |
