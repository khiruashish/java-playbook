---
title: Java 8 — Interview Guide
tags: [java, java8, interview]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: intermediate → senior
related: [java8-guide.md]
---

## Java 8 — Interview & Coding Guide

This guide complements `Java8-Guide.md` and focuses on:
- **Interview-style explanations and code snippets.**
- **Hands-on examples** for functional interfaces, streams, Optional, date/time, CompletableFuture, and related APIs.

---

## 1. Functional Interfaces (Built‑in)

### 1.1 `Function<T, R>`

```java
Function<String, Integer> lengthFn = s -> s.length();
int len = lengthFn.apply("java8"); // 5
```

### 1.2 `Predicate<T>`

```java
Predicate<Integer> isEven = n -> n % 2 == 0;
boolean ok = isEven.test(10); // true
```

### 1.3 `Consumer<T>`

```java
Consumer<String> printer = s -> System.out.println(s);
printer.accept("Hello"); // prints "Hello"
```

### 1.4 `Supplier<T>`

```java
Supplier<UUID> uuidSupplier = UUID::randomUUID;
UUID id = uuidSupplier.get();
```

### 1.5 `BiFunction<T, U, R>`

```java
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
int sum = add.apply(2, 3); // 5
```

### 1.6 `UnaryOperator<T>` and `BinaryOperator<T>`

```java
UnaryOperator<String> trim = String::trim;
BinaryOperator<Integer> max = (a, b) -> a > b ? a : b;
```

---

## 2. Custom Functional Interface

```java
@FunctionalInterface
public interface Converter<F, T> {
    T convert(F from);
}

Converter<String, Integer> toInt = Integer::valueOf;
int value = toInt.convert("42"); // 42
```

---

## 3. Default and Static Methods in Interfaces

```java
public interface Logger {
    void log(String msg);

    default void info(String msg) {
        log("INFO: " + msg);
    }

    static Logger stdout() {
        return msg -> System.out.println(msg);
    }
}
```

Interview note:
- Explain why default methods were added (API evolution) and how multiple default methods are resolved.

---

## 4. Lambda Expressions & Method References

### 4.1 Lambdas

```java
List<String> names = Arrays.asList("Ava", "Ben", "Chris");
names.forEach(n -> System.out.println(n));
```

### 4.2 Method references

```java
names.forEach(System.out::println);
```

### 4.3 Constructor references

```java
Supplier<List<String>> listSupplier = ArrayList::new;
List<String> list = listSupplier.get();
```

Key interview points:
- Lambdas implement **functional interfaces**.
- Method reference forms: `Class::staticMethod`, `instance::method`, `Class::instanceMethod`, `Class::new`.

---

## 5. Streams Basics

```java
List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
List<Integer> evens = nums.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
// evens = [2, 4]
```

Concepts:
- **Intermediate operations**: `map`, `filter`, `flatMap`, `distinct`, `sorted`, `limit`, `skip`, `peek`.
- **Terminal operations**: `collect`, `forEach`, `reduce`, `count`, `min`, `max`, `anyMatch`, `allMatch`, `noneMatch`, `findFirst`, `findAny`.

---

## 6. `map` vs `flatMap`

```java
List<List<String>> data = Arrays.asList(
    Arrays.asList("a", "b"),
    Arrays.asList("c")
);

// map: Stream<Stream<String>>
Stream<Stream<String>> mapped = data.stream().map(List::stream);

// flatMap: Stream<String>
List<String> flat = data.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList());
// flat = [a, b, c]
```

Interview explanation:
- `map`: 1‑to‑1 transformation.
- `flatMap`: 1‑to‑N transformation, flattening nested streams.

---

## 7. Collectors Examples

```java
Map<String, Long> countByCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity, Collectors.counting()));

String joined = names.stream().collect(Collectors.joining(", "));
```

Key collectors:
- `toList`, `toSet`, `toMap`.
- `joining`, `groupingBy`, `partitioningBy`.
- `mapping`, `summarizingInt`, `collectingAndThen`.

---

## 8. Optional Basics & Usage

```java
Optional<String> opt = Optional.of("value");
String v1 = opt.orElse("default");
String v2 = opt.orElseGet(() -> "lazyDefault");
String v3 = opt.orElseThrow(() -> new IllegalStateException("missing"));
```

### 8.1 Optional with `map` and `flatMap`

```java
Optional<User> userOpt = Optional.of(user);
String email = userOpt.map(User::getEmail).orElse("n/a");
```

Interview notes:
- Difference between `orElse` and `orElseGet`.
- Why using `Optional.get()` directly is discouraged.

---

## 9. Parallel Streams

```java
long count = nums.parallelStream().filter(n -> n > 2).count();
```

Key talking points:
- Uses **ForkJoinPool.commonPool**.
- Best for CPU-bound, associative operations on large datasets.
- Not good for blocking I/O or small lists.

---

## 10. Date and Time API

```java
LocalDate today = LocalDate.now();
LocalDate nextWeek = today.plusWeeks(1);

Instant start = Instant.now();
// ... work ...
Instant end = Instant.now();
Duration d = Duration.between(start, end);
```

Discussion:
- Why `java.time` is superior to `java.util.Date` / `Calendar` (immutability, clarity, time zones).

---

## 11. CompletableFuture

```java
CompletableFuture<String> future =
    CompletableFuture.supplyAsync(() -> "data")
        .thenApply(String::toUpperCase);

String result = future.join(); // "DATA"
```

Key methods:
- `supplyAsync`, `runAsync`.
- `thenApply`, `thenAccept`, `thenCompose`, `thenCombine`.
- `allOf`, `anyOf`, `exceptionally`, `handle`.

Enterprise example:

```java
CompletableFuture<User> userF = CompletableFuture.supplyAsync(() -> loadUser(id));
CompletableFuture<List<Order>> ordersF = CompletableFuture.supplyAsync(() -> loadOrders(id));

UserProfile profile = userF.thenCombine(ordersF, UserProfile::new).join();
```

---

## 12. Nashorn (JavaScript Engine) – Legacy

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
engine.eval("print('hello')");
```

Discuss:
- Deprecated in newer Java versions; know it historically for Java 8.

---

## 13. Base64 Encoding

```java
String encoded = Base64.getEncoder().encodeToString("hello".getBytes(StandardCharsets.UTF_8));
byte[] decoded = Base64.getDecoder().decode(encoded);
```

Use cases:
- Basic auth headers, token encoding, binary → text (JSON) encoding.

---

## 14. Stream API & Interview Examples (with Output)

Below are consolidated examples (adapted from your reference) that frequently appear in interviews.

### 14.1 Convert List to Map (id → name)

```java
List<User> users = Arrays.asList(
    new User(1, "Ava"),
    new User(2, "Ben")
);
Map<Integer, String> idToName = users.stream()
    .collect(Collectors.toMap(User::getId, User::getName));
System.out.println(idToName);
// Output: {1=Ava, 2=Ben}
```

### 14.2 Convert Map to List (values)

```java
Map<Integer, String> map = new HashMap<>();
map.put(1, "A");
map.put(2, "B");
List<String> values = new ArrayList<>(map.values());
System.out.println(values);
// Output: [A, B]
```

### 14.3 Remove duplicate characters from a string

```java
String input = "banana";
String unique = input.chars()
    .distinct()
    .mapToObj(c -> String.valueOf((char) c))
    .collect(Collectors.joining());
System.out.println(unique);
// Output: ban
```

### 14.4 Remove duplicate words

```java
String s = "java java spring boot spring";
String result = Arrays.stream(s.split("\\s+"))
    .distinct()
    .collect(Collectors.joining(" "));
System.out.println(result);
// Output: java spring boot
```

### 14.5 Reverse a string

```java
String s = "hello";
String reversed = new StringBuilder(s).reverse().toString();
System.out.println(reversed);
// Output: olleh
```

### 14.6 Reverse each word in a sentence

```java
String s = "java spring";
String reversedWords = Arrays.stream(s.split("\\s+"))
    .map(w -> new StringBuilder(w).reverse().toString())
    .collect(Collectors.joining(" "));
System.out.println(reversedWords);
// Output: avaj gnirps
```

### 14.7 flatMap example

```java
List<List<Integer>> list = Arrays.asList(
    Arrays.asList(1, 2),
    Arrays.asList(3, 4)
);
List<Integer> flat = list.stream().flatMap(List::stream).collect(Collectors.toList());
System.out.println(flat);
// Output: [1, 2, 3, 4]
```

### 14.8 map() example

```java
List<String> names = Arrays.asList("ava", "ben");
List<String> upper = names.stream().map(String::toUpperCase).collect(Collectors.toList());
System.out.println(upper);
// Output: [AVA, BEN]
```

### 14.9 Find first element

```java
List<Integer> nums = Arrays.asList(10, 20, 30);
int first = nums.stream().findFirst().orElse(-1);
System.out.println(first);
// Output: 10
```

### 14.10 Filter and count

```java
List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
long count = nums.stream().filter(n -> n > 2).count();
System.out.println(count);
// Output: 3
```

### 14.11 Sort ascending/descending

```java
List<Integer> nums = Arrays.asList(4, 1, 3);
List<Integer> asc = nums.stream().sorted().collect(Collectors.toList());
List<Integer> desc = nums.stream().sorted(Comparator.reverseOrder()).collect(Collectors.toList());
System.out.println(asc);  // [1, 3, 4]
System.out.println(desc); // [4, 3, 1]
```

### 14.12 Group by

```java
List<User> users = Arrays.asList(
    new User(1, "A", "NY"),
    new User(2, "B", "SF"),
    new User(3, "C", "NY")
);
Map<String, List<User>> byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));
System.out.println(byCity.keySet());
// Output: [NY, SF]
```

### 14.13 Partition by predicate

```java
List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
Map<Boolean, List<Integer>> parts = nums.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
System.out.println(parts.get(true));
// Output: [2, 4]
```

### 14.14 Sum using reduce

```java
int sum = nums.stream().reduce(0, Integer::sum);
System.out.println(sum);
// Output: 15
```

### 14.15 Remove nulls

```java
List<String> list = Arrays.asList("A", null, "B");
List<String> cleaned = list.stream().filter(Objects::nonNull).collect(Collectors.toList());
System.out.println(cleaned);
// Output: [A, B]
```

### 14.16 Frequency map

```java
List<String> items = Arrays.asList("a", "b", "a");
Map<String, Long> freq = items.stream()
    .collect(Collectors.groupingBy(s -> s, Collectors.counting()));
System.out.println(freq);
// Output: {a=2, b=1}
```

### 14.17 Check all match

```java
boolean allEven = Arrays.asList(2, 4, 6).stream().allMatch(n -> n % 2 == 0);
System.out.println(allEven);
// Output: true
```

### 14.18 Nth highest number (3rd)

```java
List<Integer> nums = Arrays.asList(9, 1, 5, 3, 7);
int third = nums.stream()
    .sorted(Comparator.reverseOrder())
    .skip(2)
    .findFirst()
    .orElse(-1);
System.out.println(third);
// Output: 5
```

### 14.19 Parallel stream order

```java
List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
nums.parallelStream().forEach(System.out::print);
System.out.println();
nums.parallelStream().forEachOrdered(System.out::print);
System.out.println();
// First line: order not guaranteed; second line: 12345
```

---

## 15. Higher‑Level Interview Questions (Conceptual)

### 15.1 Beginner

- What is a lambda expression? How is it different from an anonymous class?
- What is a functional interface? Give examples.
- What is the difference between `map` and `flatMap` in streams?
- What problem does `Optional` solve?

### 15.2 Intermediate

- Explain how `groupingBy` and `partitioningBy` work, with examples.
- How do you handle checked exceptions inside a stream pipeline?
- What are `orElse`, `orElseGet`, and `orElseThrow`? When would you use each?
- When would you choose `parallelStream()` over `stream()`?

### 15.3 Advanced

- Describe how Java 8 streams are implemented internally (spliterators, laziness).
- Discuss the pitfalls of using parallel streams in a web application.
- Explain the difference between `thenApply`, `thenCompose`, and `thenCombine` in `CompletableFuture`.
- How does `java.time` improve on `java.util.Date` and `Calendar` in terms of design and thread safety?

### 15.4 Architect‑level

- Design a microservice that aggregates data from multiple downstream services using **CompletableFuture** or streams. Discuss timeouts and error handling.
- Compare approaches: reactive streams vs Java 8 streams vs CompletableFuture vs (modern) virtual threads for I/O-bound workloads.
- How would you migrate a legacy codebase to Java 8 (or Java 21) while keeping risk low?

---

## 16. Quick Interview Cheat Sheet

| Topic | Key points |
|-------|-----------|
| Functional interfaces | Exactly one abstract method, used as lambda targets. |
| Lambdas vs anonymous classes | Lambdas are lighter, use `invokedynamic`; better for functional style. |
| Streams | Lazy; intermediate ops return streams; terminal ops execute. No reuse of a stream. |
| Optional | Use to model optional return values, not as fields; avoid `get()` without check. |
| Parallel streams | Use for CPU-bound operations; beware side effects and common pool contention. |
| `java.time` | Immutable, thread-safe; clear separation of date, time, zone. |
| CompletableFuture | Asynchronous pipelines, better than `Future`; supports composition and error handling. |
| Default methods | Enable API evolution, but can create diamond problems; override to resolve. |

Use this file as your **Java 8 interview workbook**; use `Java8-Guide.md` as your **architecture and design reference**. 

