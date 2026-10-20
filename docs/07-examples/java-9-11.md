---
title: Java 9 to 11 by Example
status: review
---

# Java 9 to 11 by Example

Java 9 brought collection factories and stream additions; Java 10 added `var`; Java 11 — the first LTS after
Java 8 — added string and file helpers and the standard HTTP client.

!!! tip "Every example here is real"
    Each program below compiles and runs as shown, and the output is exactly what it printed on JDK 21.
    Copy one into a file and run it with the command shown underneath — no build tool needed.

---

## 1. Java 9 · List.of, Set.of, Map.of

Compact, **immutable** collections that reject `null` and duplicate set elements. See [Ch 11](../02-language/11-java-9-to-11.md).

```java title="J09_CollectionFactories.java"
--8<-- "code/examples/java9to11/J09_CollectionFactories.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J09_CollectionFactories.out"
```

<small>Run it: `java J09_CollectionFactories.java`</small>

---

## 2. Java 9 · takeWhile, dropWhile, iterate, ofNullable

`takeWhile` stops at the first element that fails; `filter` checks them all.

```java title="J09_StreamAdditions.java"
--8<-- "code/examples/java9to11/J09_StreamAdditions.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J09_StreamAdditions.out"
```

<small>Run it: `java J09_StreamAdditions.java`</small>

---

## 3. Java 9 · Optional.or, ifPresentOrElse, stream

Chain fallbacks with `or`, and flatten a list of Optionals with `Optional::stream`.

```java title="J09_OptionalAdditions.java"
--8<-- "code/examples/java9to11/J09_OptionalAdditions.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J09_OptionalAdditions.out"
```

<small>Run it: `java J09_OptionalAdditions.java`</small>

---

## 4. Java 9 · private interface methods

Default methods can share a helper without exposing it.

```java title="J09_PrivateInterfaceMethods.java"
--8<-- "code/examples/java9to11/J09_PrivateInterfaceMethods.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J09_PrivateInterfaceMethods.out"
```

<small>Run it: `java J09_PrivateInterfaceMethods.java`</small>

---

## 5. Java 9 · try-with-resources on existing variables

Effectively final resources can be listed directly; they close in reverse order.

```java title="J09_TryWithResources.java"
--8<-- "code/examples/java9to11/J09_TryWithResources.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J09_TryWithResources.out"
```

<small>Run it: `java J09_TryWithResources.java`</small>

---

## 6. Java 10 · var

Type inference for local variables. Beware the bare diamond: `var list = new ArrayList<>()` is an `ArrayList<Object>`.

```java title="J10_Var.java"
--8<-- "code/examples/java9to11/J10_Var.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J10_Var.out"
```

<small>Run it: `java J10_Var.java`</small>

---

## 7. Java 10 · List.copyOf and unmodifiable collectors

A copy is a snapshot; `unmodifiableList` is a view that still reflects changes. See [Ch 22](../03-collections/22-immutability.md).

```java title="J10_CopyOf.java"
--8<-- "code/examples/java9to11/J10_CopyOf.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J10_CopyOf.out"
```

<small>Run it: `java J10_CopyOf.java`</small>

---

## 8. Java 11 · isBlank, strip, lines, repeat

`strip()` understands Unicode whitespace; `trim()` only ASCII.

```java title="J11_StringMethods.java"
--8<-- "code/examples/java9to11/J11_StringMethods.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J11_StringMethods.out"
```

<small>Run it: `java J11_StringMethods.java`</small>

---

## 9. Java 11 · Files.readString and writeString

Read or write a whole file in one call, as UTF-8.

```java title="J11_Files.java"
--8<-- "code/examples/java9to11/J11_Files.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J11_Files.out"
```

<small>Run it: `java J11_Files.java`</small>

---

## 10. Java 11 · Predicate.not and var in lambdas

`Predicate.not(String::isBlank)` keeps method references readable.

```java title="J11_PredicateNotAndVarLambdas.java"
--8<-- "code/examples/java9to11/J11_PredicateNotAndVarLambdas.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J11_PredicateNotAndVarLambdas.out"
```

<small>Run it: `java J11_PredicateNotAndVarLambdas.java`</small>

---

## 11. Java 11 · the HTTP client

Synchronous and asynchronous calls. A tiny local server stands in for a real API, so this runs offline. Create one client and reuse it; set both timeouts. See [Ch 40](../05-runtime/40-http-client.md).

```java title="J11_HttpClient.java"
--8<-- "code/examples/java9to11/J11_HttpClient.java"
```

```text title="Output"
--8<-- "code/examples/java9to11/J11_HttpClient.out"
```

<small>Run it: `java J11_HttpClient.java`</small>
