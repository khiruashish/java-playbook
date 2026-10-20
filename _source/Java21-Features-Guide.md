---
title: Java 21 — New Features
tags: [java, java21, records, sealed-classes]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: intermediate → senior
related: [java21-concurrency-guide.md]
---

## Java 21 Features Guide

A practical overview of **Java 21** (LTS, released September 2023) language and core library features. Each section includes a short concept explanation, code examples, and expected output or behavior.

**Assumptions:** All examples assume a **Java 21** toolchain. Features marked **Preview** require:

```bash
javac --enable-preview --release 21 ...
java --enable-preview ...
```

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. High-level feature table](#2-high-level-feature-table)
- [3. Virtual Threads (JEP 444)](#3-virtual-threads-jep-444)
  - [Concept](#concept)
  - [Example 1: Simple virtual thread](#example-1-simple-virtual-thread)
  - [Example 2: Many virtual threads with ExecutorService](#example-2-many-virtual-threads-with-executorservice)
- [4. Structured Concurrency (JEP 453, Preview)](#4-structured-concurrency-jep-453-preview)
  - [Concept](#concept-1)
  - [Example: ShutdownOnFailure – fetch two resources concurrently](#example-shutdownonfailure--fetch-two-resources-concurrently)
- [5. Scoped Values (JEP 429, Preview)](#5-scoped-values-jep-429-preview)
  - [Concept](#concept-2)
  - [Example: Bind and read a scoped value](#example-bind-and-read-a-scoped-value)
- [6. Sequenced Collections (JEP 431)](#6-sequenced-collections-jep-431)
  - [Concept](#concept-3)
  - [Example: List – getFirst, getLast, addFirst, reversed](#example-list--getfirst-getlast-addfirst-reversed)
  - [Example: LinkedHashMap – reversed view](#example-linkedhashmap--reversed-view)
- [7. Pattern Matching for switch (JEP 441)](#7-pattern-matching-for-switch-jep-441)
  - [Concept](#concept-4)
  - [Example: Format by type with guards and null](#example-format-by-type-with-guards-and-null)
- [8. Record Patterns (JEP 440)](#8-record-patterns-jep-440)
  - [Concept](#concept-5)
  - [Example: Point quadrant with record pattern](#example-point-quadrant-with-record-pattern)
- [9. Unnamed Patterns & Variables (JEP 443, Preview)](#9-unnamed-patterns--variables-jep-443-preview)
  - [Concept](#concept-6)
  - [Example: Ignore components in switch](#example-ignore-components-in-switch)
- [10. String Templates (JEP 430, Preview)](#10-string-templates-jep-430-preview)
  - [Concept](#concept-7)
  - [Example: STR processor](#example-str-processor)
- [11. Foreign Function & Memory API (JEP 442)](#11-foreign-function--memory-api-jep-442)
  - [Concept](#concept-8)
  - [Example: Allocate, write, read in native memory](#example-allocate-write-read-in-native-memory)
- [12. Other improvements (brief)](#12-other-improvements-brief)
- [13. Quick reference table](#13-quick-reference-table)

---

## 1. Introduction

Java 21 is a **Long-Term Support (LTS)** release focused on:

- **Concurrency:** Virtual threads, structured concurrency, and scoped values for scalable, maintainable concurrent code.
- **Language:** Pattern matching for `switch`, record patterns, and (in preview) unnamed patterns/variables and string templates.
- **APIs:** Sequenced collections for consistent access to first/last/reversed elements, and the Foreign Function & Memory (FFM) API for safe native interop.

For general Java 8 streams and collections style, see `Java8-Guide.md` and `List-Guide.md`. For Java 21 concurrency design, see `Java21-Concurrency-Guide.md`.

---

## 2. High-level feature table

| Feature                        | JEP | Category     | Short description                                  | Section |
|--------------------------------|-----|--------------|----------------------------------------------------|---------|
| Virtual Threads                | 444 | Concurrency  | Lightweight threads for high concurrency           | §3      |
| Structured Concurrency         | 453 | Concurrency  | Coordinate subtasks as one unit of work            | §4      |
| Scoped Values                  | 429 | Concurrency  | Immutable, scoped context for threads              | §5      |
| Sequenced Collections          | 431 | Collections  | First/last/reversed on List, Set, Map              | §6      |
| Pattern Matching for switch    | 441 | Language     | Type-safe switch with patterns                     | §7      |
| Record Patterns                | 440 | Language     | Deconstruct records in switch/instanceof           | §8      |
| Unnamed Patterns & Variables   | 443 | Language (P) | Use `_` to ignore values                           | §9      |
| String Templates               | 430 | Language (P) | String interpolation with templates                | §10     |
| Foreign Function & Memory API  | 442 | Interop      | Safe native memory and FFI                         | §11     |

P = Preview in Java 21.

---

## 3. Virtual Threads (JEP 444)

### Concept

**Virtual threads** are lightweight threads managed by the JVM. Many virtual threads run on few platform (OS) threads. They are ideal for I/O-bound or high-concurrency workloads where blocking is acceptable (e.g. waiting on HTTP or DB). You get a simple **thread‑per‑request** style without the cost of millions of platform threads.

### Example 1: Simple virtual thread

```java
Thread.ofVirtual().start(() -> System.out.println("Hello from virtual thread"));
Thread.ofVirtual().name("worker-1").start(() -> System.out.println("Named virtual thread"));
```

**Output:**

```text
Hello from virtual thread
Named virtual thread
```

### Example 2: Many virtual threads with ExecutorService

```java
import java.util.concurrent.*;

public class ManyVirtualThreads {
    public static void main(String[] args) throws Exception {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            var futures = new java.util.ArrayList<Future<String>>();
            for (int i = 0; i < 5; i++) {
                int id = i;
                futures.add(executor.submit(() -> "Task-" + id));
            }
            for (Future<String> f : futures) {
                System.out.println(f.get());
            }
        }
    }
}
```

**Output:**

```text
Task-0
Task-1
Task-2
Task-3
Task-4
```

You can scale to thousands or millions of virtual threads; the JVM schedules them onto a small pool of carrier threads.

---

## 4. Structured Concurrency (JEP 453, Preview)

### Concept

**Structured concurrency** treats a set of concurrent subtasks as **one unit**: if one fails, others are cancelled, and the caller always waits for all subtasks to finish before continuing.

`StructuredTaskScope` provides this behavior and works well with virtual threads.

### Example: ShutdownOnFailure – fetch two resources concurrently

```java
// Requires: javac --enable-preview --release 21 StructuredConcurrencyExample.java
//           java --enable-preview StructuredConcurrencyExample
import java.util.concurrent.StructuredTaskScope;

public class StructuredConcurrencyExample {
    public static void main(String[] args) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var user = scope.fork(StructuredConcurrencyExample::fetchUser);
            var order = scope.fork(StructuredConcurrencyExample::fetchOrder);

            scope.join();
            scope.throwIfFailed();

            System.out.println(user.resultNow() + " / " + order.resultNow());
        }
    }

    static String fetchUser() { return "user-1"; }
    static String fetchOrder() { return "order-42"; }
}
```

**Output:**

```text
user-1 / order-42
```

**Behavior:** If either `fetchUser()` or `fetchOrder()` throws, the other is cancelled and the exception is propagated. The scope ensures no orphaned tasks.

---

## 5. Scoped Values (JEP 429, Preview)

### Concept

**Scoped values** are immutable, inheritable values bound to a lexical scope. They replace or complement `ThreadLocal` and work well with virtual threads:

- A scoped value is visible only within the scope where it was bound and to threads created in that scope.
- When the scope ends, the binding disappears.

### Example: Bind and read a scoped value

```java
// Requires: javac --enable-preview --release 21 ScopedValueExample.java
//           java --enable-preview ScopedValueExample

import jdk.incubator.concurrent.ScopedValue;

public class ScopedValueExample {
    private static final ScopedValue<String> USER = ScopedValue.newInstance();

    public static void main(String[] args) throws InterruptedException {
        ScopedValue.where(USER, "alice").run(() -> {
            System.out.println("Inside scope: " + USER.get());
            Thread v = Thread.ofVirtual().start(() ->
                System.out.println("Child thread: " + USER.get()));
            try {
                v.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        System.out.println("Outside scope: scope ended");
        // USER.get() here would throw NoSuchElementException
    }
}
```

**Output:**

```text
Inside scope: alice
Child thread: alice
Outside scope: scope ended
```

---

## 6. Sequenced Collections (JEP 431)

### Concept

**SequencedCollection**, **SequencedSet**, and **SequencedMap** provide a uniform way to access **first/last** elements and **reversed** views. `List`, `LinkedHashSet`, and `LinkedHashMap` implement these interfaces in Java 21.

### Example: List – getFirst, getLast, addFirst, reversed

```java
import java.util.ArrayList;
import java.util.List;

public class SequencedListExample {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(List.of("b", "c"));
        list.addFirst("a");
        list.addLast("d");

        System.out.println("First: " + list.getFirst());
        System.out.println("Last: " + list.getLast());
        System.out.println("Reversed: " + list.reversed());

        list.removeFirst();
        list.removeLast();
        System.out.println("After remove first/last: " + list);
    }
}
```

**Output:**

```text
First: a
Last: d
Reversed: [d, c, b, a]
After remove first/last: [b, c]
```

### Example: LinkedHashMap – reversed view

```java
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.SequencedMap;

public class SequencedMapExample {
    public static void main(String[] args) {
        LinkedHashMap<String, Integer> map =
            new LinkedHashMap<>(Map.of("a", 1, "b", 2, "c", 3));

        SequencedMap<String, Integer> reversed = map.reversed();
        System.out.println("Reversed map: " + reversed);
    }
}
```

**Output:**

```text
Reversed map: {c=3, b=2, a=1}
```

---

## 7. Pattern Matching for switch (JEP 441)

### Concept

**Pattern matching for switch** allows `switch` to:

- Match on types and deconstruct them.
- Use guards (`when`) for conditions.
- Handle `null` explicitly.

It reduces boilerplate compared to `instanceof` + casts.

### Example: Format by type with guards and null

```java
public class PatternSwitchExample {

    static String format(Object obj) {
        return switch (obj) {
            case null -> "null";
            case Integer i when i > 0 -> "positive int: " + i;
            case Integer i -> "int: " + i;
            case Long l -> "long: " + l;
            case String s -> "string: " + s;
            default -> "other: " + obj;
        };
    }

    public static void main(String[] args) {
        System.out.println(format(1));
        System.out.println(format(-1));
        System.out.println(format("hi"));
        System.out.println(format(null));
    }
}
```

**Output:**

```text
positive int: 1
int: -1
string: hi
null
```

---

## 8. Record Patterns (JEP 440)

### Concept

**Record patterns** let you deconstruct record values directly in `switch` and `instanceof`, binding components by position.

### Example: Point quadrant with record pattern

```java
import java.util.List;

record Point(int x, int y) {}

public class RecordPatternExample {

    static String quadrant(Point p) {
        return switch (p) {
            case Point(0, 0) -> "origin";
            case Point(int x, int y) when x > 0 && y > 0 -> "Q1";
            case Point(int x, int y) when x < 0 && y > 0 -> "Q2";
            case Point(int x, int y) when x < 0 && y < 0 -> "Q3";
            case Point(int x, int y) when x > 0 && y < 0 -> "Q4";
            default -> "axis";
        };
    }

    public static void main(String[] args) {
        for (Point p : List.of(new Point(0, 0), new Point(1, 1), new Point(-1, 2))) {
            System.out.println(p + " -> " + quadrant(p));
        }
    }
}
```

**Output:**

```text
Point[x=0, y=0] -> origin
Point[x=1, y=1] -> Q1
Point[x=-1, y=2] -> Q2
```

---

## 9. Unnamed Patterns & Variables (JEP 443, Preview)

### Concept

Use `_` when:
- You need a pattern/variable syntactically.
- But you do not need to use its value.

This makes intent clear and avoids unused variable warnings.

### Example: Ignore components in switch

```java
// Requires: javac --enable-preview --release 21 UnnamedPatternsExample.java
//           java --enable-preview UnnamedPatternsExample

record Box(String name, int value) {}

public class UnnamedPatternsExample {

    static String describe(Box b) {
        return switch (b) {
            case Box(_, 0) -> "zero value";
            case Box("secret", _) -> "secret box";
            case Box(String n, int v) -> n + ": " + v;
        };
    }

    public static void main(String[] args) {
        System.out.println(describe(new Box("a", 0)));
        System.out.println(describe(new Box("secret", 10)));
        System.out.println(describe(new Box("other", 5)));
    }
}
```

**Output:**

```text
zero value
secret box
other: 5
```

Unnamed local variable example:

```java
int _ = doSideEffectOnly(); // ignore returned value, keep side effect
```

---

## 10. String Templates (JEP 430, Preview)

### Concept

**String templates** provide safe, programmable string interpolation:

- A **template** is a mix of literal text and expressions.
- A **processor** (like `STR`) turns it into a final string.

Requires preview:

```bash
javac --enable-preview --release 21 StringTemplateExample.java
java --enable-preview StringTemplateExample
```

### Example: STR processor

```java
import static java.lang.StringTemplate.STR;

public class StringTemplateExample {
    public static void main(String[] args) {
        String name = "Java";
        int version = 21;
        String msg = STR."Hello, \{name} version \{version}!";
        System.out.println(msg);
    }
}
```

**Output:**

```text
Hello, Java version 21!
```

Expressions inside `\{...}` are evaluated and then replaced by the processor (here, `STR` for basic concatenation).

---

## 11. Foreign Function & Memory API (JEP 442)

### Concept

The **Foreign Function & Memory (FFM) API** provides:

- A safer, high‑level alternative to `sun.misc.Unsafe`.
- A way to allocate/manage off‑heap memory and call native code without full JNI.

Key ideas:
- **Arena**: defines the lifetime of allocations.
- **MemorySegment**: region of memory.
- **ValueLayout**: describes the type and layout of values in memory.

### Example: Allocate, write, read in native memory

```java
import java.lang.foreign.Arena;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;

public class FFMExample {
    public static void main(String[] args) {
        try (Arena arena = Arena.ofConfined()) {
            MemorySegment segment = arena.allocate(ValueLayout.JAVA_INT, 4);
            segment.set(ValueLayout.JAVA_INT, 0, 42);
            int value = segment.get(ValueLayout.JAVA_INT, 0);
            System.out.println("Read back: " + value);
        }
    }
}
```

**Output:**

```text
Read back: 42
```

**Behavior:** The segment is allocated in the arena and automatically freed when the try block exits. No manual free; no use-after-free from Java side when used correctly.

---

## 12. Other improvements (brief)

- **HttpClient:** Continued improvements and stability for HTTP/2 and WebSocket.
- **Deprecations/removals:** Some legacy APIs (e.g. certain constructors or methods) are deprecated or removed; check release notes when upgrading.
- **GC:** ZGC and G1 improvements for low-latency and throughput; ZGC can be the default on some configurations.

For streams, collections, and general Java 8+ style examples, see `Java8-Guide.md` and `Java8-Interview-Guide.md`.

---

## 13. Quick reference table

| Feature                        | JEP | Category     | One-line usage summary                                                   |
|--------------------------------|-----|--------------|---------------------------------------------------------------------------|
| Virtual Threads                | 444 | Concurrency  | `Thread.ofVirtual().start(...)` or `Executors.newVirtualThreadPerTaskExecutor()` |
| Structured Concurrency         | 453 | Concurrency  | `StructuredTaskScope` (e.g. `ShutdownOnFailure`) to run and coordinate subtasks |
| Scoped Values                  | 429 | Concurrency  | `ScopedValue.where(KEY, value).run(() -> ...)` then `KEY.get()`          |
| Sequenced Collections          | 431 | Collections  | `list.getFirst()`, `list.getLast()`, `list.reversed()`                   |
| Pattern Matching switch        | 441 | Language     | `switch (obj) { case Type t -> ...; case null -> ...; default -> ... }`  |
| Record Patterns                | 440 | Language     | `case Point(int x, int y) when x > 0 -> ...`                             |
| Unnamed Patterns/Vars (Preview)| 443 | Language     | Use `_` in patterns or as variable name when value is unused             |
| String Templates (Preview)     | 430 | Language     | `STR."Text \{expr} more text"`                                           |
| FFM API                        | 442 | Interop      | `Arena.ofConfined()`, `arena.allocate(layout)`, `segment.get/set`        |

All examples in this guide target **Java 21**. Preview features require `--enable-preview` at compile and run time.

