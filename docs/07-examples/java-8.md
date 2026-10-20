---
title: Java 8 by Example
status: review
---

# Java 8 by Example

Java 8 (2014) changed how Java is written: lambdas, streams, `Optional`, the `java.time` API and default methods.
Every example is a complete program. Where a line uses a later feature for brevity — such as `Stream.toList()`
(Java 16) or records (Java 16) — the Java 8 equivalent is noted in a comment.

!!! tip "Every example here is real"
    Each program below compiles and runs as shown, and the output is exactly what it printed on JDK 21.
    Copy one into a file and run it with the command shown underneath — no build tool needed.

---

## 1. Lambdas and functional interfaces

A lambda is a short way to pass behaviour. `Predicate`, `Function`, `Consumer` and `Supplier` cover most needs, and they compose with `and`, `negate` and `andThen`. See [Ch 06](../02-language/06-lambdas-functional-interfaces.md).

```java title="J8_01_Lambdas.java"
--8<-- "code/examples/java8/J8_01_Lambdas.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_01_Lambdas.out"
```

<small>Run it: `java J8_01_Lambdas.java`</small>

---

## 2. Method references

Four forms — static, unbound, bound and constructor — each a shorthand for a lambda.

```java title="J8_02_MethodReferences.java"
--8<-- "code/examples/java8/J8_02_MethodReferences.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_02_MethodReferences.out"
```

<small>Run it: `java J8_02_MethodReferences.java`</small>

---

## 3. Default and static interface methods

Interfaces can now carry behaviour: default methods that implementers inherit, and static factory methods.

```java title="J8_03_DefaultAndStaticMethods.java"
--8<-- "code/examples/java8/J8_03_DefaultAndStaticMethods.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_03_DefaultAndStaticMethods.out"
```

<small>Run it: `java J8_03_DefaultAndStaticMethods.java`</small>

---

## 4. Streams: filter, map, collect

Build a pipeline, then run it with a terminal operation. The laziness demo shows that elements flow one at a time and processing stops as soon as `findFirst` is satisfied. See [Ch 07](../02-language/07-stream-api.md).

```java title="J8_04_StreamBasics.java"
--8<-- "code/examples/java8/J8_04_StreamBasics.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_04_StreamBasics.out"
```

<small>Run it: `java J8_04_StreamBasics.java`</small>

---

## 5. Collectors: group, partition, join, map

The collectors that do most real work. `TreeMap::new` keeps the output order stable. See [Ch 08](../02-language/08-collectors.md).

```java title="J8_05_Collectors.java"
--8<-- "code/examples/java8/J8_05_Collectors.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_05_Collectors.out"
```

<small>Run it: `java J8_05_Collectors.java`</small>

---

## 6. flatMap, reduce and primitive streams

`flatMap` flattens nested lists; `mapToInt` avoids boxing; `reduce` folds values together.

```java title="J8_06_FlatMapAndReduce.java"
--8<-- "code/examples/java8/J8_06_FlatMapAndReduce.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_06_FlatMapAndReduce.out"
```

<small>Run it: `java J8_06_FlatMapAndReduce.java`</small>

---

## 7. Optional

A return type that says "there may be no result". Note that `orElse` evaluates its argument even when a value is present — `orElseGet` does not. See [Ch 09](../02-language/09-optional.md).

```java title="J8_07_Optional.java"
--8<-- "code/examples/java8/J8_07_Optional.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_07_Optional.out"
```

<small>Run it: `java J8_07_Optional.java`</small>

---

## 8. java.time

Immutable types for dates, times, durations and time zones. See [Ch 10](../02-language/10-java-time.md).

```java title="J8_08_DateTime.java"
--8<-- "code/examples/java8/J8_08_DateTime.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_08_DateTime.out"
```

<small>Run it: `java J8_08_DateTime.java`</small>

---

## 9. The new Map methods

`getOrDefault`, `putIfAbsent`, `merge`, `compute*` and `replaceAll` replace most get-check-put code.

```java title="J8_09_MapApi.java"
--8<-- "code/examples/java8/J8_09_MapApi.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_09_MapApi.out"
```

<small>Run it: `java J8_09_MapApi.java`</small>

---

## 10. removeIf, replaceAll and Comparator chains

Bulk operations on collections, and comparators built by composition instead of hand-written `compare` methods.

```java title="J8_10_CollectionApi.java"
--8<-- "code/examples/java8/J8_10_CollectionApi.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_10_CollectionApi.out"
```

<small>Run it: `java J8_10_CollectionApi.java`</small>

---

## 11. String.join, StringJoiner and Base64

Small additions that removed a lot of utility code.

```java title="J8_11_StringsAndBase64.java"
--8<-- "code/examples/java8/J8_11_StringsAndBase64.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_11_StringsAndBase64.out"
```

<small>Run it: `java J8_11_StringsAndBase64.java`</small>

---

## 12. Parallel streams

Same result for CPU-bound work — but only worthwhile for large data, and never for blocking I/O.

```java title="J8_12_ParallelStreams.java"
--8<-- "code/examples/java8/J8_12_ParallelStreams.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_12_ParallelStreams.out"
```

<small>Run it: `java J8_12_ParallelStreams.java`</small>

---

## 13. Where streams come from

Collections, arrays, ranges, and generated or iterated sequences.

```java title="J8_13_StreamSources.java"
--8<-- "code/examples/java8/J8_13_StreamSources.java"
```

```text title="Output"
--8<-- "code/examples/java8/J8_13_StreamSources.out"
```

<small>Run it: `java J8_13_StreamSources.java`</small>
