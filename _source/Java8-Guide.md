---
title: Java 8 — Enterprise Reference
tags: [java, java8, streams, lambdas, optional]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: beginner → architect
related: [java8-interview-guide.md]
---

## Java 8 — Complete Enterprise Reference Guide

---

## 0. How to Use This Guide

- **Audience**: Developers from beginner to senior/architect level.
- **Scope**: All major Java 8 language and library additions, with:
  - **Definition**
  - **Why** it was introduced / problems it solves
  - **Syntax**
  - **Code examples**
  - **Internal workings (where relevant)**
  - **Performance considerations**
  - **Best practices & common mistakes**
  - **Enterprise use cases**
- **Companion**: For focused interview problems and coding questions, see `Java8-Interview-Guide.md`.

---

## 1. Introduction to Java 8

### 1.1 Why Java 8 was a major release

- First **huge language update** since Java 5 generics.
- Brought **functional programming constructs**:
  - Lambdas
  - Method references
  - Streams
  - Functional interfaces
- Introduced robust **Date/Time API** (`java.time`) and **Optional**.
- Added **default methods** to interfaces, enabling more flexible evolution of APIs.

### 1.2 Problems in Java 7 era

- Verbose, boilerplate-heavy code (anonymous inner classes, for-loops).
- No standard way to:
  - Express declarative data processing pipelines.
  - Represent “maybe” values (`null` + NPE plague).
  - Work safely with dates, times, and time zones (Joda-Time widely used instead).
- APIs such as `Collections` / `Map` lacked fluent, functional-style operations.

### 1.3 Functional programming introduction

- **Functional programming** treats computation as the evaluation of functions:
  - **Pure functions**: no side effects, same output for same input.
  - **Higher-order functions**: functions that take or return other functions.
  - **Immutability**: data is not mutated, new values are created.
- Java 8 does **not** make Java a pure FP language, but:
  - Adds support for **lambda expressions** and **method references**.
  - Enables functional-style APIs (Streams, `Optional`, `CompletableFuture`).

### 1.4 Backward compatibility & architecture

- Java 8 features are **additive**:
  - Old code continues to work unmodified.
  - New interfaces/APIs extended via **default methods**.
- Under the hood:
  - Lambdas compiled as `invokedynamic` call sites, not as anonymous inner classes.
  - JIT can aggressively optimize lambda/stream pipelines.

Enterprise takeaway:
- Java 8 gives you **more expressive code** and **better performance** for data processing-heavy backends without breaking old code.

---

## 2. Functional Programming in Java (Concepts)

### 2.1 Core concepts

**Pure functions**
- Definition: No side effects; output depends only on inputs.
- Benefits: Easy to test, reason about, and parallelize.

**Higher‑order functions**
- Definition: Functions that take/return functions.
- In Java 8: using `Function`, `Predicate`, etc., and methods like `map`, `filter`.

**Immutability**
- Prefer not to mutate objects in place, especially shared state.
- Use `final` and immutable collections where reasonable.

**Side effects**
- Any observable change outside a function (I/O, global variables, modifying arguments).
- In enterprise code: log, DB write, HTTP calls.

### 2.2 Examples in Java

```java
// Pure function: no shared state, no side effects
int addTax(int amount, int taxRatePercent) {
    return amount + (amount * taxRatePercent / 100);
}

// Higher-order function: takes a Function
List<Integer> transform(List<Integer> ints, Function<Integer, Integer> f) {
    return ints.stream().map(f).collect(Collectors.toList());
}

// Usage
List<Integer> prices = List.of(100, 200);
List<Integer> withTax = transform(prices, p -> addTax(p, 10));
```

Enterprise best practice:
- Keep **core business rules** as pure functions where possible, and **wrap side effects** (DB, messaging) at the boundaries.

---

## 3. Lambda Expressions

### 3.1 Definition

- A **lambda expression** is a concise way to represent an anonymous function (an instance of a functional interface).

### 3.2 Why introduced / problem solved

- Replaces verbose anonymous inner classes used for callbacks:

```java
// Before Java 8
Collections.sort(list, new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareToIgnoreCase(b);
    }
});
```

With Java 8:

```java
Collections.sort(list, (a, b) -> a.compareToIgnoreCase(b));
```

### 3.3 Syntax & target typing

```java
// (parameters) -> expression
(x, y) -> x + y

// (parameters) -> { statements; return ...; }
(String name) -> {
    System.out.println("Hello " + name);
    return name.length();
}
```

- **Target typing**: compiler infers the functional interface type from the context.
- **Type inference**: often omit parameter types:

```java
Comparator<String> cmp = (a, b) -> a.compareToIgnoreCase(b);
```

### 3.4 Examples

**Runnable**

```java
Runnable r = () -> System.out.println("Running");
new Thread(r).start();
```

**Comparator & collections sorting**

```java
List<String> names = new ArrayList<>(List.of("Bob", "alice", "Charlie"));
names.sort(String::compareToIgnoreCase); // method reference
```

### 3.5 Enterprise examples

**Stream processing**

```java
List<Order> highValue = orders.stream()
    .filter(o -> o.total() > 10_000)
    .sorted(Comparator.comparing(Order::total).reversed())
    .collect(Collectors.toList());
```

**Async tasks**

```java
ExecutorService pool = Executors.newFixedThreadPool(8);
Future<Result> f = pool.submit(() -> expensiveCalculation(input));
```

**Event handling**

```java
button.setOnClickListener(event -> auditService.logClick(event));
```

### 3.6 Performance & best practices

- Lambdas are **not** anonymous inner classes; they are cheap and JIT‑friendly.
- Avoid capturing large objects or unnecessary state in lambdas; prefer stateless or small captures.
- Prefer method references (`Class::method`) for clarity where possible.

Common mistakes:
- Overusing lambdas when simple method calls suffice.
- Writing deeply nested lambdas instead of small named methods.

---

## 4. Functional Interfaces

### 4.1 Definition

- A **functional interface** has exactly **one abstract method**.
- Examples: `Runnable`, `Callable`, `Comparator`, and Java 8’s `java.util.function` package.
- Annotated with `@FunctionalInterface` (optional but recommended).

### 4.2 Why introduced / problem solved

- Provides a standard set of **function types** (e.g. `Function<T,R>`, `Predicate<T>`) to pass behavior as arguments while keeping type safety.

### 4.3 Core built‑in functional interfaces

| Interface | Method | Purpose |
|----------|--------|---------|
| `Function<T,R>` | `R apply(T t)` | Map a value of type T to R |
| `Predicate<T>` | `boolean test(T t)` | Boolean test on a value |
| `Consumer<T>` | `void accept(T t)` | Perform an action with T (no return) |
| `Supplier<T>` | `T get()` | Provide a T, no input |
| `UnaryOperator<T>` | `T apply(T t)` | Function from T to T |
| `BinaryOperator<T>` | `T apply(T t1, T t2)` | Combine two Ts into one T |
| `BiFunction<T,U,R>` | `R apply(T t, U u)` | Function of two inputs |
| `BiConsumer<T,U>` | `void accept(T t, U u)` | Consumer of two inputs |

Examples (from your reference):

```java
Function<String, Integer> lengthFn = s -> s.length();
Predicate<Integer> isEven = n -> n % 2 == 0;
Consumer<String> printer = System.out::println;
Supplier<UUID> uuidSupplier = UUID::randomUUID;
UnaryOperator<String> trim = String::trim;
BinaryOperator<Integer> max = Integer::max;
```

### 4.4 Default & static methods in interfaces

Java 8 allows:

- **default methods**:

```java
public interface Logger {
    void log(String msg);

    default void info(String msg) {
        log("INFO: " + msg);
    }

    static Logger noop() {
        return msg -> { };
    }
}
```

Why:
- To evolve interfaces (add new behavior) without breaking existing implementations.

Common pitfalls:
- Multiple inheritance conflict:
  - If a class implements two interfaces with the same default method, you must override and resolve.

Enterprise use:
- Provide shared behaviors in SDKs and domain interfaces (e.g. auditing, basic validation).

---

## 5. Stream API — Deep Guide

### 5.1 Definition & motivation

- **Stream**: A sequence of elements supporting sequential and parallel aggregate operations.
- Solves:
  - Boilerplate loops.
  - External iteration with manual mutable state.
  - Complex mapping/filtering logic scattered across loops.

### 5.2 Stream architecture

Pipeline:
- **Source**: collection, array, I/O channel, generator.
- **Intermediate operations**: `map`, `filter`, `sorted`, `flatMap`, etc. (lazy, return a new stream).
- **Terminal operation**: `collect`, `reduce`, `forEach`, `count`, etc. (triggers execution).

Text diagram:

```
Collection -> stream() -> filter(...) -> map(...) -> sorted(...) -> collect(...)
   (source)           (intermediate ops)             (terminal op)
```

### 5.3 Stream creation

```java
// From collections
Stream<String> s1 = list.stream();
Stream<String> s2 = list.parallelStream();

// From values
Stream<Integer> s3 = Stream.of(1, 2, 3);

// generate (infinite stream)
Stream<Double> randoms = Stream.generate(Math::random);

// iterate (infinite)
Stream<Integer> evens = Stream.iterate(0, n -> n + 2);
```

### 5.4 Intermediate operations

| Operation | Description |
|----------|-------------|
| `map` | Transform each element |
| `filter` | Keep elements matching predicate |
| `flatMap` | Flatten nested streams |
| `distinct` | Remove duplicates (uses `equals`) |
| `sorted` | Sort elements (natural or custom comparator) |
| `peek` | Inspect elements (for debugging) |
| `limit` | Take first N elements |
| `skip` | Skip first N elements |

Examples:

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "Bob");

List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());

List<String> uniqueSorted = names.stream()
    .distinct()
    .sorted()
    .collect(Collectors.toList());
```

### 5.5 Terminal operations

| Operation | Purpose |
|----------|---------|
| `collect` | Convert to collection or other result |
| `forEach` | Perform action for each element (side effects) |
| `reduce` | Fold elements into a single value |
| `count` | Number of elements |
| `min` / `max` | Smallest / largest according to comparator |
| `anyMatch` / `allMatch` / `noneMatch` | Match predicates |
| `findFirst` / `findAny` | Get element wrapped in `Optional` |

Examples:

```java
long count = names.stream().filter(n -> n.startsWith("A")).count();

Optional<String> firstLong = names.stream()
    .filter(n -> n.length() > 3)
    .findFirst();

int totalLength = names.stream()
    .mapToInt(String::length)
    .sum();
```

### 5.6 Collectors

Common collectors:

- `toList()`, `toSet()`, `toMap(keyMapper, valueMapper[, mergeFn])`
- `joining(delimiter[, prefix, suffix])`
- `groupingBy(classifier[, downstream])`
- `partitioningBy(predicate[, downstream])`
- `mapping`, `collectingAndThen`, `summarizingInt`, etc.

Example enterprise aggregations:

```java
// Orders per customer
Map<String, Long> ordersPerCustomer = orders.stream()
    .collect(Collectors.groupingBy(Order::customerId, Collectors.counting()));

// Total revenue per day
Map<LocalDate, BigDecimal> revenuePerDay = orders.stream()
    .collect(Collectors.groupingBy(
        Order::orderDate,
        Collectors.mapping(
            Order::totalAmount,
            Collectors.reducing(BigDecimal.ZERO, BigDecimal::add)
        )
    ));
```

### 5.7 Parallel streams

- `parallelStream()` or `stream().parallel()` uses **ForkJoinPool.commonPool()**.
- Benefits:
  - Can speed up **CPU-bound**, associative operations on large data sets.
- Risks:
  - Overhead > benefit for small collections.
  - Shared mutable state becomes dangerous (must avoid side effects).
  - Can starve other tasks using the common pool.

Best practices:
- Use for **CPU-bound**, stateless, order‑insensitive operations on large datasets.
- Avoid I/O inside parallel streams.
- For web apps, prefer explicit executors / virtual threads over parallel streams for request-level concurrency.

Common mistakes:
- Assuming order is preserved by `forEach` on parallel stream (`forEachOrdered` if you need order).
- Updating shared structures (`ArrayList`, `HashMap`) inside `forEach` on parallel streams.

---

## 6. Optional API

### 6.1 Definition & motivation

- **`Optional<T>`** represents a value that may be present or absent.
- Introduced to:
  - Make nullability explicit.
  - Reduce `NullPointerException` and imperative null checks.

### 6.2 Core methods

```java
Optional<String> opt = Optional.of("value");       // throws NPE if null
Optional<String> maybe = Optional.ofNullable(possiblyNull);
Optional<String> empty = Optional.empty();

opt.isPresent();           // boolean
opt.ifPresent(v -> ...);   // run if present

String v1 = opt.orElse("fallback");
String v2 = opt.orElseGet(() -> expensiveFallback());
String v3 = opt.orElseThrow(() -> new IllegalStateException("Missing"));

Optional<Integer> len = opt.map(String::length);
Optional<Integer> parsed = opt.flatMap(this::parseIntSafely);
Optional<String> filtered = opt.filter(s -> !s.isBlank());
```

### 6.3 Enterprise usage

**Repository layer**:

```java
interface UserRepository {
    Optional<User> findById(String id);
}
```

**Service layer**:

```java
User getUserOrThrow(String id) {
    return userRepository.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

**API handling**:
- Use `Optional` at boundaries between layers or to model optional parameters, but **avoid** using `Optional` fields in JPA entities or for everything indiscriminately.

Common mistakes:
- Calling `get()` without checking presence (`NoSuchElementException`).
- Using `Optional` in performance-critical hot paths (minimal but some overhead).

---

## 7. New Date and Time API (`java.time`)

### 7.1 Problems with `java.util.Date` and `Calendar`

- Mutable and not thread-safe.
- Confusing APIs (months 0‑based, time zones ambiguous).
- Mixed responsibilities (formatting, parsing, arithmetic).

### 7.2 New types

| Type | Description |
|------|-------------|
| `LocalDate` | Date without time zone (`2024-01-01`) |
| `LocalTime` | Time without date or time zone (`10:15:30`) |
| `LocalDateTime` | Date and time, no time zone |
| `ZonedDateTime` | Date/time with time zone |
| `Instant` | Point in time on UTC time-line |
| `Duration` | Time-based amount (seconds, nanos) |
| `Period` | Date-based amount (days, months, years) |

Examples:

```java
LocalDate today = LocalDate.now();
LocalDate nextWeek = today.plusWeeks(1);

LocalDateTime now = LocalDateTime.now();
ZonedDateTime utcNow = now.atZone(ZoneId.of("UTC"));

Instant start = Instant.now();
// ... operation ...
Instant end = Instant.now();
Duration d = Duration.between(start, end);
```

### 7.3 Formatting & parsing

```java
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String formatted = LocalDateTime.now().format(fmt);
LocalDateTime parsed = LocalDateTime.parse("2024-01-01 10:15:00", fmt);
```

Enterprise examples:
- Normalize all timestamps to `Instant` or `ZonedDateTime` in UTC at persistence boundaries.
- Use `ZoneId` per tenant or region in financial calculations.

Best practices:
- Treat `java.time` types as **immutable** value objects.
- Avoid mixing legacy `Date`/`Calendar` with new API; convert at edges using `Date.from(instant)` and `date.toInstant()`.

---

## 8. Method References

### 8.1 Types

| Kind | Syntax | Example |
|------|--------|---------|
| Static | `Type::staticMethod` | `Math::max` |
| Instance of particular object | `instance::method` | `printer::println` |
| Instance (arbitrary) | `Type::instanceMethod` | `String::toLowerCase` |
| Constructor | `Type::new` | `ArrayList::new` |

Examples:

```java
List<String> names = List.of("Ava", "Ben");
names.forEach(System.out::println);

Supplier<List<String>> listSupplier = ArrayList::new;
List<String> list = listSupplier.get();
``>

Best practices:
- Use method references when they **improve readability**; avoid when they hide important logic.

---

## 9. Default Methods in Interfaces

### 9.1 Why introduced

- To evolve interfaces (e.g., `List`, `Map`) without breaking all implementing classes.
- Enables adding new behavior as default implementations.

Example:

```java
public interface Vehicle {
    void start();

    default void stop() {
        System.out.println("Vehicle stopped");
    }
}
```

Multiple inheritance resolution:

```java
interface A { default void foo() { System.out.println("A"); } }
interface B { default void foo() { System.out.println("B"); } }

class C implements A, B {
    @Override
    public void foo() {
        A.super.foo(); // or B.super.foo(), or custom logic
    }
}
```

Best practices:
- Use default methods for **helper behavior**, not to hide complex logic.
- Avoid deep default method hierarchies; complexity can explode.

---

## 10. Nashorn JavaScript Engine (Deprecated in newer Java)

### 10.1 Definition & usage

- **Nashorn** is a JavaScript engine added in Java 8 (deprecated in Java 11, removed later).
- Allows executing JS from Java.

Example:

```java
import javax.script.*;

ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
engine.eval("print('Hello from JS')");
```

Enterprise use (historical):
- Light scripting, dynamic configuration, simple rules engines.

Modern note:
- Prefer **GraalVM polyglot** or external engines; Nashorn is legacy.

---

## 11. CompletableFuture

### 11.1 Definition & motivation

- `CompletableFuture` extends `Future` with:
  - Non‑blocking callbacks (`thenApply`, `thenAccept`).
  - Composition (`thenCompose`, `thenCombine`).
  - Better exception handling (`exceptionally`, `handle`).

### 11.2 Key methods & patterns

```java
// supplyAsync: return a value
CompletableFuture<String> f1 =
    CompletableFuture.supplyAsync(() -> callRemoteService());

// runAsync: void
CompletableFuture<Void> f2 =
    CompletableFuture.runAsync(() -> audit("start"));

// thenApply: transform result
CompletableFuture<Integer> length =
    f1.thenApply(String::length);

// thenCompose: flatten nested async
CompletableFuture<UserDetails> details =
    getUserAsync(id).thenCompose(this::getDetailsAsync);

// thenCombine: combine two independent futures
CompletableFuture<Result> combined =
    priceAsync.thenCombine(stockAsync, Result::new);

// exceptionally: fallback on error
CompletableFuture<String> safe =
    f1.exceptionally(ex -> "fallback");

// handle: inspect result or exception
CompletableFuture<String> handled =
    f1.handle((val, ex) -> ex == null ? val : "error");
```

Enterprise examples:
- Parallel API calls to multiple downstream services, aggregating results into a single response.
- Asynchronous background processing (email notifications, analytics).

Best practices:
- Avoid mixing blocking (`get()`) and non‑blocking (callbacks) styles; prefer `join()` in top-level orchestrators.
- Use a custom `Executor` for heavy tasks; don’t overload the common pool in server apps.

---

## 12. Parallel Streams

### 12.1 Internal workings

- Use **ForkJoinPool.commonPool** by default.
- Tasks split recursively into sub-tasks (“**work stealing**”).
- Suitable for:
  - CPU-bound, parallelizable, **associative** operations.

### 12.2 When to use

- Large datasets (e.g., millions of items).
- CPU‑intensive calculations where each element processing is non-trivial.

### 12.3 When **not** to use

- I/O-bound operations that block (database, HTTP).
- Small collections (parallel overhead dominates).
- Code that mutates shared state or depends heavily on encounter order.

Performance considerations:
- Test empirically; parallel may be slower if misused.
- Be aware that **threads from the common pool** might interfere with other parallel operations (e.g., `CompletableFuture` using default executors).

---

## 13. Java 8 Collections Improvements

### 13.1 `forEach`, `removeIf`, `replaceAll`, `sort`

```java
list.forEach(System.out::println);

list.removeIf(s -> s.isBlank());

list.replaceAll(String::toUpperCase);

list.sort(Comparator.naturalOrder());
```

### 13.2 Map improvements

```java
map.putIfAbsent(key, value);
map.computeIfAbsent(key, k -> new ArrayList<>());
map.computeIfPresent(key, (k, v) -> v + 1);
map.merge(key, 1L, Long::sum);
```

Enterprise usage:
- Counters, caches, and accumulators with `merge`.
- Lazy initialization with `computeIfAbsent` for per-tenant or per-user state.

---

## 14. Base64 Encoding

### 14.1 API

```java
Base64.Encoder encoder = Base64.getEncoder();
Base64.Decoder decoder = Base64.getDecoder();

String encoded = encoder.encodeToString("hello".getBytes(StandardCharsets.UTF_8));
byte[] decoded = decoder.decode(encoded);
```

Enterprise usage:
- Basic authentication headers.
- Encoding binary blobs (keys, tokens) for JSON or text protocols.

---

## 15. Java 8 Performance Improvements (High‑Level)

### 15.1 PermGen removal & Metaspace

- Java 8 replaced **PermGen** (fixed-size area for class metadata) with **Metaspace** (native memory, grows as needed).
- Reduces `OutOfMemoryError: PermGen space` issues, simplifies tuning.

### 15.2 Lambda & stream optimization

- Lambdas compiled as `invokedynamic` call sites.
- JIT can inline and optimize stream pipelines.

Best practices:
- Avoid unnecessary intermediate collections; favor fluent pipelines.
- Use primitive streams (`IntStream`, `LongStream`) for numeric processing to minimize boxing.

---

## 16. Enterprise Best Practices with Java 8

### 16.1 Streams in service layers

- Keep pipelines **readable**:
  - One operation per line.
  - Extract complex lambdas into named methods.

Bad:

```java
return orders.stream().filter(o -> o.getCustomer() != null && o.getCustomer().isActive()
    && o.getAmount() > 1000 && o.getItems().size() > 3).map(...).collect(...);
```

Better:

```java
return orders.stream()
    .filter(this::isHighValueActiveCustomerOrder)
    .map(this::toDto)
    .collect(Collectors.toList());
```

### 16.2 Avoiding performance bottlenecks

- Don’t overuse `parallelStream` in web apps.
- Avoid creating unnecessary intermediate lists in hot paths.
- For I/O, consider **CompletableFuture** or (in modern Java) **virtual threads** instead of parallel streams.

### 16.3 Exception handling in streams

- Wrap checked exceptions in custom runtime exceptions or adapt to `Try`-style utilities.
- Don’t swallow exceptions inside lambdas—log or propagate meaningfully.

### 16.4 Clean code practices

- Use `Optional` at edges, not everywhere.
- Prefer immutable DTOs (e.g., constructors, builders).
- Use functional interfaces for small behaviors, avoid passing large stateful lambdas.

---

## 17. Real Enterprise Project Examples (Sketches)

### 17.1 Order processing system

```java
class OrderService {

    List<OrderSummary> findHighValueOrdersForCustomer(String customerId) {
        return orderRepository.findByCustomer(customerId).stream()
            .filter(o -> o.total().compareTo(BigDecimal.valueOf(10_000)) > 0)
            .sorted(Comparator.comparing(Order::orderDate).reversed())
            .map(this::toSummary)
            .collect(Collectors.toList());
    }
}
```

### 17.2 Employee data processing

```java
Map<String, Double> avgSalaryPerDept(List<Employee> employees) {
    return employees.stream()
        .collect(Collectors.groupingBy(Employee::department,
            Collectors.averagingDouble(Employee::salary)));
}
```

### 17.3 Parallel microservice calls (with CompletableFuture)

```java
OrderDetails getOrderDetails(String orderId) {
    CompletableFuture<Order> orderF = CompletableFuture.supplyAsync(() -> loadOrder(orderId));
    CompletableFuture<Customer> customerF = orderF.thenCompose(o ->
        CompletableFuture.supplyAsync(() -> loadCustomer(o.customerId())));
    CompletableFuture<List<Shipment>> shipmentsF =
        CompletableFuture.supplyAsync(() -> loadShipments(orderId));

    CompletableFuture.allOf(orderF, customerF, shipmentsF).join();

    return new OrderDetails(orderF.join(), customerF.join(), shipmentsF.join());
}
```

---

## 18. Java 8 Interview Questions (Overview)

This guide focuses on **concepts and design**. For a curated list of:
- Beginner → architect‑level questions.
- Coding problems using streams, Optionals, lambdas, CompletableFuture, date/time.

See: **`Java8-Interview-Guide.md`**.

---

## 19. Java 8 Cheat Sheet (High‑Level)

### 19.1 Streams

- Create: `list.stream()`, `Stream.of(...)`, `IntStream.range(...)`.
- Transform: `map`, `filter`, `flatMap`, `sorted`, `distinct`, `limit`, `skip`.
- Terminal: `collect`, `forEach`, `reduce`, `count`, `findFirst`, `findAny`, `min`, `max`.
- Collectors: `toList`, `toSet`, `toMap`, `joining`, `groupingBy`, `partitioningBy`.

### 19.2 Optional

- Create: `Optional.of`, `ofNullable`, `empty`.
- Use: `map`, `flatMap`, `filter`, `orElse`, `orElseGet`, `orElseThrow`, `ifPresent`.

### 19.3 Functional interfaces

- Core: `Function`, `Predicate`, `Consumer`, `Supplier`, `UnaryOperator`, `BinaryOperator`, `BiFunction`, `BiConsumer`.

### 19.4 CompletableFuture

- Create: `supplyAsync`, `runAsync`.
- Transform: `thenApply`, `thenCompose`, `thenAccept`.
- Combine: `thenCombine`, `allOf`, `anyOf`.
- Handle errors: `exceptionally`, `handle`.

### 19.5 Date/Time

- `LocalDate.now()`, `LocalDateTime.now()`, `ZonedDateTime.now(ZoneId.of("UTC"))`.
- `Duration.between(start, end)`, `Period.between(d1, d2)`.
- `DateTimeFormatter.ofPattern("yyyy-MM-dd")`.

For more detailed examples and Q&A‑style problems, refer to **`Java8-Interview-Guide.md`**. 

