---
title: Java 8
status: review
---

# Java 8

Java 8 (March 2014) is the release that changed how Java is written. Lambdas, streams, `Optional`, `java.time` and default methods arrived together, and most enterprise codebases still carry a large Java 8 core. Everything Java 8 in this handbook is collected in this tab:

| Read | What you get |
|---|---|
| [Ch 06](../02-language/06-lambdas-functional-interfaces.md) → [Ch 10](../02-language/10-java-time.md) | The five Java 8 chapters, in the handbook's 9-part format |
| [Java 8 by Example](../07-examples/java-8.md) | 13 complete programs, each with the output it really printed |
| [Appendix B](../appendix/b-java8-interview-workbook.md) | 24 coding exercises with their traps, plus every Java 8 interview question banded L1–L4 |

Each chapter follows the same arc as the rest of the book: the Java 8 baseline first, then what changed in Java 9, 11, 17, 21 and 25, then what to use today. Code labelled `// Java 8` compiles on Java 8. Everything else targets the current release, with the Java 8 form noted where it differs.

---

## Every Java 8 feature, and where it lives

| Feature | Chapter | Run it | Interview |
|---|---|---|---|
| Lambda expressions, target typing, effectively-final capture | [Ch 06 §4.1](../02-language/06-lambdas-functional-interfaces.md), [Ch 06 §5.5](../02-language/06-lambdas-functional-interfaces.md) | [Example 1](../07-examples/java-8.md#1-lambdas-and-functional-interfaces) | [Appendix B](../appendix/b-java8-interview-workbook.md) |
| `java.util.function`: `Predicate`, `Function`, `Supplier`, `Consumer` and their primitive forms | [Ch 06 §4.2](../02-language/06-lambdas-functional-interfaces.md) | [Example 1](../07-examples/java-8.md#1-lambdas-and-functional-interfaces) | [Ch 06 §9](../02-language/06-lambdas-functional-interfaces.md) |
| Method references (all four kinds) | [Ch 06 §4.5](../02-language/06-lambdas-functional-interfaces.md) | [Example 2](../07-examples/java-8.md#2-method-references) | [Ch 06 §9](../02-language/06-lambdas-functional-interfaces.md) |
| `@FunctionalInterface`, default and static interface methods | [Ch 06](../02-language/06-lambdas-functional-interfaces.md) | [Example 3](../07-examples/java-8.md#3-default-and-static-interface-methods) | [Ch 06 §9](../02-language/06-lambdas-functional-interfaces.md) |
| Stream API: creation, intermediate and terminal operations, laziness | [Ch 07 §4.1](../02-language/07-stream-api.md) | [Example 4](../07-examples/java-8.md#4-streams-filter-map-collect), [Example 13](../07-examples/java-8.md#13-where-streams-come-from) | [Ch 07 §9](../02-language/07-stream-api.md) |
| `flatMap`, `reduce`, `IntStream` / `LongStream` / `DoubleStream` | [Ch 07 §4.4](../02-language/07-stream-api.md), [Ch 07 §5.1](../02-language/07-stream-api.md), [Ch 07 §5.5](../02-language/07-stream-api.md) | [Example 6](../07-examples/java-8.md#6-flatmap-reduce-and-primitive-streams) | [Ch 07 §9](../02-language/07-stream-api.md) |
| Parallel streams and the common ForkJoinPool | [Ch 07](../02-language/07-stream-api.md) | [Example 12](../07-examples/java-8.md#12-parallel-streams) | [Ch 07 §9](../02-language/07-stream-api.md) |
| `Collectors`: `groupingBy`, `partitioningBy`, `toMap`, `joining`, downstream collectors | [Ch 08](../02-language/08-collectors.md) | [Example 5](../07-examples/java-8.md#5-collectors-group-partition-join-map) | [Ch 08 §9](../02-language/08-collectors.md) |
| `Optional` and a null strategy | [Ch 09](../02-language/09-optional.md) | [Example 7](../07-examples/java-8.md#7-optional) | [Ch 09 §9](../02-language/09-optional.md) |
| `java.time`: `LocalDate`, `Instant`, `ZonedDateTime`, `Duration`, `Period`, formatting | [Ch 10](../02-language/10-java-time.md) | [Example 8](../07-examples/java-8.md#8-javatime) | [Ch 10 §9](../02-language/10-java-time.md) |
| New `Map` methods: `getOrDefault`, `putIfAbsent`, `computeIfAbsent`, `merge`, `forEach`, `replaceAll` | [Ch 19 §4.3](../03-collections/19-hashmap-internals.md), [Ch 19 §4.5](../03-collections/19-hashmap-internals.md) | [Example 9](../07-examples/java-8.md#9-the-new-map-methods) | [Ch 19 §9](../03-collections/19-hashmap-internals.md) |
| Collection defaults: `removeIf`, `replaceAll`, `List.sort`, `Comparator.comparing().thenComparing()` | [Ch 18](../03-collections/18-list-internals.md), [Ch 06 §5.3](../02-language/06-lambdas-functional-interfaces.md) | [Example 10](../07-examples/java-8.md#10-removeif-replaceall-and-comparator-chains) | [Ch 18 §9](../03-collections/18-list-internals.md) |
| `HashMap` treeification of long bins | [Ch 19 §6.3](../03-collections/19-hashmap-internals.md) | [HashMap internals](../07-examples/hashmap-internals.md) | [Ch 19 §9](../03-collections/19-hashmap-internals.md) |
| `CompletableFuture` | [Ch 29](../04-concurrency/29-completable-future.md) | [CompletableFuture by Example](../07-examples/completablefuture.md) | [Appendix C](../appendix/c-concurrency-interview-bank.md) |
| `ConcurrentHashMap` rewrite and bulk parallel operations | [Ch 30 §4.3](../04-concurrency/30-concurrent-collections.md) | [ConcurrentHashMap internals](../07-examples/concurrenthashmap-internals.md) | [Appendix C](../appendix/c-concurrency-interview-bank.md) |
| `StampedLock`, `LongAdder` | [Ch 27](../04-concurrency/27-locks-and-atomics.md) | [Concurrency toolkit](../07-examples/concurrency-toolkit.md) | [Appendix C](../appendix/c-concurrency-interview-bank.md) |
| `String.join`, `StringJoiner`, `Base64` | [Below](#base64-and-stringjoiner) | [Example 11](../07-examples/java-8.md#11-stringjoin-stringjoiner-and-base64) | — |
| PermGen removed, Metaspace added | [Below](#permgen-and-metaspace), [Ch 02](../01-platform/02-jvm-runtime-model.md) | — | — |
| Nashorn JavaScript engine (removed in Java 15) | [Below](#nashorn) | — | — |

---

## The rest of Java 8

Three smaller Java 8 changes don't need a chapter of their own, but they still come up in maintenance work and interviews.

### Base64 and StringJoiner

Before Java 8, Base64 meant Apache Commons Codec or the internal `sun.misc.BASE64Encoder`, which was never a public API. `java.util.Base64` provides three flavours, each with an encoder and a decoder:

| Factory | Alphabet | Use for |
|---|---|---|
| `Base64.getEncoder()` / `getDecoder()` | Standard (`+`, `/`) | General binary-to-text |
| `Base64.getUrlEncoder()` / `getUrlDecoder()` | URL-safe (`-`, `_`) | Tokens in URLs and file names |
| `Base64.getMimeEncoder()` / `getMimeDecoder()` | Standard, wrapped at 76 characters | Email attachments |

```java title="Encoding a delivery-slot token"
String slotToken = "SLOT-2026-10-21-0900|BLR-560001";

String encoded = Base64.getUrlEncoder().withoutPadding()
        .encodeToString(slotToken.getBytes(StandardCharsets.UTF_8));

String decoded = new String(Base64.getUrlDecoder().decode(encoded), StandardCharsets.UTF_8);
// decoded.equals(slotToken) → true
```

Always pass a `Charset`. `getBytes()` with no argument uses the platform default, which was machine-dependent until Java 18 (JEP 400) made UTF-8 the default.

`String.join` and `StringJoiner` replaced the classic "append, then strip the trailing comma" loop:

```java title="Joining SKU codes for a pick slip"
List<String> codes = List.of("MILK-1L", "BREAD-400G", "EGGS-12");

String simple = String.join(", ", codes);                 // MILK-1L, BREAD-400G, EGGS-12

StringJoiner slip = new StringJoiner(" | ", "[", "]");
slip.setEmptyValue("[no items]");
codes.forEach(slip::add);
String formatted = slip.toString();                       // [MILK-1L | BREAD-400G | EGGS-12]
```

In a stream, `Collectors.joining(", ", "[", "]")` does the same thing and uses a `StringJoiner` internally.

### PermGen and Metaspace

Up to Java 7, class metadata lived in the **Permanent Generation**, a fixed-size region of the Java heap. Applications that loaded many classes, or redeployed repeatedly in an application server, ran into `OutOfMemoryError: PermGen space`, and tuning `-XX:MaxPermSize` was guesswork.

Java 8 (JEP 122) moved class metadata into **Metaspace**, which is allocated from native memory and grows on demand:

| | Java 7 and earlier | Java 8 and later |
|---|---|---|
| Region | PermGen, inside the heap | Metaspace, native memory |
| Size | Fixed: `-XX:MaxPermSize` | **Unbounded by default**: cap with `-XX:MaxMetaspaceSize` |
| Failure | `OutOfMemoryError: PermGen space` | `OutOfMemoryError: Metaspace` |
| Interned strings, static fields | In PermGen | Moved to the heap (strings moved in Java 7) |

"Unbounded" is not "free". A class-loader leak now shows up as slowly growing native memory, and in a container that can end in an OOM kill instead of a clean Java exception. Set `-XX:MaxMetaspaceSize` in containers. The full memory map is in [Ch 02](../01-platform/02-jvm-runtime-model.md).

### Nashorn

Java 8 replaced the old Rhino engine with **Nashorn**, a faster JavaScript engine reached through the `javax.script` API:

```java title="Java 8 to 14 only: evaluating a pricing rule in JavaScript"
// Java 8
javax.script.ScriptEngine engine =
        new javax.script.ScriptEngineManager().getEngineByName("nashorn");
// engine.eval("0.9 * 499") → 449.1 on Java 8–14.
// On Java 15+, getEngineByName("nashorn") returns null, so the same call throws a NullPointerException.
```

Nashorn was deprecated in Java 11 (JEP 335) and **removed in Java 15** (JEP 372). If legacy code still uses it, there are three migration routes:

1. **Standalone Nashorn**: the `org.openjdk.nashorn:nashorn-core` library, which keeps the same `javax.script` API on Java 15 and later.
2. **GraalJS** (GraalVM polyglot), the actively developed engine, for new work.
3. **No script engine at all**: replace the script with plain Java rules. This is usually the best option for business rules like pricing, which belong in typed, testable code.

See [Ch 05](../01-platform/05-migration-strategy.md) for where this fits in a migration.

---

## Moving past Java 8

Java 8 code is still everywhere, but new code shouldn't stop there. The most common upgrades, with their chapters:

| Java 8 idiom | Modern replacement | Since | Chapter |
|---|---|---|---|
| `collect(Collectors.toList())` | `stream.toList()` | 16 | [Ch 07](../02-language/07-stream-api.md) |
| `Arrays.asList(...)` / `Collections.unmodifiableList` | `List.of(...)`, `List.copyOf(...)` | 9, 10 | [Ch 22](../03-collections/22-immutability.md) |
| `optional.isPresent() ? optional.get() : …` | `orElseThrow()`, `ifPresentOrElse`, `or` | 9, 10 | [Ch 09](../02-language/09-optional.md) |
| Value classes with `equals`/`hashCode` by hand | `record` | 16 | [Ch 12](../02-language/12-java-14-to-17.md) |
| `instanceof` followed by a cast | Pattern matching, `switch` patterns | 16, 21 | [Ch 13](../02-language/13-pattern-matching.md) |
| `list.get(list.size() - 1)` | `list.getLast()` | 21 | [Ch 21](../03-collections/21-sequenced-collections.md) |
| A thread pool sized for blocking I/O | Virtual threads | 21 | [Ch 31](../04-concurrency/31-virtual-threads.md) |
| A custom collector for windowing or folding | Stream gatherers | 24 | [Ch 38](../05-runtime/38-stream-gatherers.md) |

The full upgrade path is in [Ch 05](../01-platform/05-migration-strategy.md) and [Appendix D](../appendix/d-migration-checklists.md).
