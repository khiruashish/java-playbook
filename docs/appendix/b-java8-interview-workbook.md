---
title: Appendix B — Java 8 Interview Workbook
status: review
---

# Appendix B — Java 8 Interview Workbook

Two parts. **Part 1** is a set of hands-on stream and lambda exercises of the kind asked in coding rounds, each with a hidden solution and — where one exists — the trap an interviewer is actually probing for. **Part 2** is the conceptual question bank from Chapters 06–10.

Every solution compiles on Java 8. Where a later JDK offers a clearly better form, it is shown as a *Modern* note.

## The domain for every exercise

```java title="Domain.java"
record Product(String sku, String name, String vendor, String category,
               long pricePaise, boolean perishable) { }

record OrderLine(String sku, int quantity, long pricePaise) {
    long total() { return quantity * pricePaise; }
}

record Order(String id, String customer, String city,
             List<OrderLine> lines, LocalDate placedOn) {
    long total() { return lines.stream().mapToLong(OrderLine::total).sum(); }
}
```

(Records are Java 16. On Java 8, read them as final classes with the same fields and accessors.)

---

## Part 1 — Coding exercises

### 1. List to map, keyed by SKU

Build a `Map<String, Product>` from a `List<Product>`, keyed by SKU.

??? example "Solution"
    ```java
    Map<String, Product> bySku = products.stream()
        .collect(Collectors.toMap(Product::sku, Function.identity(),
                                  (first, second) -> first));
    ```

!!! warning "The trap"
    The two-argument `toMap(Product::sku, identity())` throws `IllegalStateException` on a duplicate SKU — at runtime, on whatever data triggers it. It also throws `NullPointerException` on a null *value*, even though `HashMap` accepts nulls. Always pass a merge function unless keys are structurally unique. See [Ch 08](../02-language/08-collectors.md).

### 2. Map values to a sorted list

Given `Map<String, Product>`, produce the product names in alphabetical order.

??? example "Solution"
    ```java
    List<String> names = bySku.values().stream()
        .map(Product::name)
        .sorted()
        .collect(Collectors.toList());
    ```
    **Modern:** `.toList()` (Java 16) instead of `collect(Collectors.toList())` — but it returns an **unmodifiable** list.

### 3. Remove duplicate characters, keeping order

`"banana"` → `"ban"`.

??? example "Solution"
    ```java
    String unique = input.chars()
        .distinct()
        .mapToObj(c -> String.valueOf((char) c))
        .collect(Collectors.joining());
    ```
    Output: `ban`

!!! warning "The trap"
    `distinct()` keeps the **first** occurrence on an ordered stream, which is why the order survives. This works for ASCII and most text; characters outside the Basic Multilingual Plane (emoji) are surrogate pairs and need `codePoints()` instead of `chars()`.

### 4. Remove duplicate words, keeping the first occurrence

`"milk rice milk atta rice"` → `"milk rice atta"`.

??? example "Solution"
    ```java
    String result = Arrays.stream(input.trim().split("\\s+"))
        .distinct()
        .collect(Collectors.joining(" "));
    ```
    Output: `milk rice atta`

!!! warning "The trap"
    Without `trim()`, leading whitespace makes `split` produce an **empty first token**.

### 5. Reverse each word in place

`"fresh milk"` → `"hserf klim"`.

??? example "Solution"
    ```java
    String reversed = Arrays.stream(input.split(" "))
        .map(w -> new StringBuilder(w).reverse().toString())
        .collect(Collectors.joining(" "));
    ```
    Output: `hserf klim`

### 6. Every distinct SKU ordered across all orders

??? example "Solution"
    ```java
    Set<String> skus = orders.stream()
        .flatMap(o -> o.lines().stream())
        .map(OrderLine::sku)
        .collect(Collectors.toCollection(TreeSet::new));   // sorted, distinct
    ```
    `flatMap` because each order yields **many** lines. `map` here would give `Stream<List<OrderLine>>`.

### 7. The first perishable product, if any

??? example "Solution"
    ```java
    Optional<Product> first = products.stream()
        .filter(Product::perishable)
        .findFirst();

    String name = first.map(Product::name).orElse("none");
    ```

!!! warning "The trap"
    `findFirst` short-circuits — it stops at the first match. On a **parallel** stream prefer `findAny` if you do not need encounter order; `findFirst` forces ordering and is slower.

### 8. Count orders over ₹1,000

??? example "Solution"
    ```java
    long count = orders.stream()
        .filter(o -> o.total() > 100_000)          // paise
        .count();
    ```

### 9. Sort products by category, then price descending

??? example "Solution"
    ```java
    List<Product> sorted = products.stream()
        .sorted(Comparator.comparing(Product::category)
                          .thenComparing(Product::pricePaise, Comparator.reverseOrder()))
        .collect(Collectors.toList());
    ```

!!! warning "The trap"
    Writing `.thenComparing(Product::pricePaise).reversed()` reverses **both** keys — `reversed()` applies to the whole chain built so far. Pass `Comparator.reverseOrder()` to the one key you want reversed. And never compare with `a - b` — it overflows. See [Ch 23](../03-collections/23-equality-and-ordering.md).

### 10. Group products by category

??? example "Solution"
    ```java
    Map<String, List<Product>> byCategory = products.stream()
        .collect(Collectors.groupingBy(Product::category, TreeMap::new, Collectors.toList()));
    ```

!!! warning "The trap"
    Plain `groupingBy(Product::category)` returns a `HashMap`, whose **iteration order is unspecified** — so printing its keys and asserting a particular order is wrong, even if it happens to work on your machine. Supply `TreeMap::new` for sorted keys or `LinkedHashMap::new` for first-seen order. Many published solutions to this exercise get it wrong.

### 11. Split products into perishable and not

??? example "Solution"
    ```java
    Map<Boolean, List<Product>> split = products.stream()
        .collect(Collectors.partitioningBy(Product::perishable));

    List<Product> fresh = split.get(true);        // never null, even if empty
    ```
    `partitioningBy` always returns both keys. `groupingBy` on a boolean omits an empty group.

### 12. Total value of all orders

??? example "Solution"
    ```java
    long total = orders.stream()
        .mapToLong(Order::total)
        .sum();
    ```

!!! warning "The trap"
    `reduce(0L, Long::sum)` on a `Stream<Long>` works but **boxes every value**. `mapToLong(...).sum()` does not. If you do use `reduce`, the identity must satisfy `identity op x == x` — `0` for addition, `1` for multiplication.

### 13. Remove nulls from a list

??? example "Solution"
    ```java
    List<String> cleaned = rawSkus.stream()
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
    ```

### 14. SKU frequency across all orders

How many orders contain each SKU?

??? example "Solution"
    ```java
    Map<String, Long> frequency = orders.stream()
        .flatMap(o -> o.lines().stream().map(OrderLine::sku).distinct())
        .collect(Collectors.groupingBy(Function.identity(), TreeMap::new, Collectors.counting()));
    ```

!!! warning "The trap"
    The inner `distinct()` counts **orders containing** the SKU. Without it you count **lines**, which double-counts an order that lists the same SKU twice. Clarify which the interviewer wants — that question is often the point of the exercise.

### 15. Do all orders have at least one line?

??? example "Solution"
    ```java
    boolean allNonEmpty = orders.stream().allMatch(o -> !o.lines().isEmpty());
    ```

!!! warning "The trap"
    `allMatch` on an **empty** stream returns `true` — vacuous truth. `anyMatch` on an empty stream returns `false`. If "no orders" should not count as success, check emptiness separately.

### 16. The third-highest distinct price

??? example "Solution"
    ```java
    OptionalLong third = products.stream()
        .mapToLong(Product::pricePaise)
        .distinct()                                // essential
        .boxed()
        .sorted(Comparator.reverseOrder())
        .skip(2)
        .mapToLong(Long::longValue)
        .findFirst();
    ```

!!! warning "The trap"
    Without `distinct()`, prices `[900, 900, 500, 300]` give `500` as the "third highest" — actually the second distinct value. Ask whether duplicates count. Also handle fewer than three distinct values: this returns an empty `OptionalLong` rather than throwing.

### 17. Revenue by city

??? example "Solution"
    ```java
    Map<String, Long> revenue = orders.stream()
        .collect(Collectors.groupingBy(Order::city, TreeMap::new,
                                       Collectors.summingLong(Order::total)));
    ```

### 18. The three most expensive products in each category

??? example "Solution"
    ```java
    Map<String, List<Product>> top3 = products.stream()
        .collect(Collectors.groupingBy(Product::category, TreeMap::new,
            Collectors.collectingAndThen(Collectors.toList(), list -> list.stream()
                .sorted(Comparator.comparingLong(Product::pricePaise).reversed())
                .limit(3)
                .collect(Collectors.toList()))));
    ```
    `collectingAndThen` post-processes each group. For very large groups, a bounded min-heap avoids sorting everything — see [Ch 20](../03-collections/20-set-queue-deque.md).

### 19. The first non-repeating character

`"sssubbie"` → `'u'`.

??? example "Solution"
    ```java
    Optional<Character> first = input.chars()
        .mapToObj(c -> (char) c)
        .collect(Collectors.groupingBy(Function.identity(), LinkedHashMap::new, Collectors.counting()))
        .entrySet().stream()
        .filter(e -> e.getValue() == 1)
        .map(Map.Entry::getKey)
        .findFirst();
    ```

!!! warning "The trap"
    `LinkedHashMap::new` is the whole answer. A plain `groupingBy` gives a `HashMap`, loses insertion order, and returns *a* non-repeating character rather than the *first*.

### 20. Find duplicate SKUs in a list

??? example "Solution"
    ```java
    Set<String> seen = new HashSet<>();
    Set<String> duplicates = skus.stream()
        .filter(sku -> !seen.add(sku))           // add returns false if already present
        .collect(Collectors.toSet());
    ```

!!! warning "The trap"
    This relies on a **side effect** in `filter`, which is only correct on a **sequential** stream. The side-effect-free version is `groupingBy(identity(), counting())` then filtering counts greater than one — say so in the interview.

### 21. Build a CSV row

??? example "Solution"
    ```java
    String row = Stream.of(p.sku(), p.name(), p.vendor(), String.valueOf(p.pricePaise()))
        .collect(Collectors.joining(",", "", "\n"));
    ```
    `joining(delimiter, prefix, suffix)`. Real CSV needs quoting for commas inside values — use a library.

### 22. Parallel stream ordering

??? example "Solution"
    ```java
    List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
    nums.parallelStream().forEach(System.out::print);         // order NOT guaranteed
    nums.parallelStream().forEachOrdered(System.out::print);  // 12345
    ```

!!! warning "The trap"
    `forEachOrdered` restores encounter order at the cost of parallelism in the terminal step. The deeper answer: `parallelStream` uses the shared `ForkJoinPool.commonPool()`, so it is wrong for blocking I/O and rarely a win for small inputs. See [Ch 07](../02-language/07-stream-api.md).

### 23. Cheapest and dearest product in one pass

??? example "Solution"
    ```java
    LongSummaryStatistics stats = products.stream()
        .mapToLong(Product::pricePaise)
        .summaryStatistics();
    long min = stats.getMin(), max = stats.getMax();
    ```
    **Modern:** `Collectors.teeing` (Java 12) combines any two collectors in one pass — useful when you need the `Product` objects, not just the prices.

### 24. Orders placed in the last 30 days

??? example "Solution"
    ```java
    LocalDate cutoff = LocalDate.now(clock).minusDays(30);
    List<Order> recent = orders.stream()
        .filter(o -> !o.placedOn().isBefore(cutoff))
        .collect(Collectors.toList());
    ```

!!! warning "The trap"
    `LocalDate.now()` with no argument uses the system default zone and makes the code untestable. Inject a `Clock`. See [Ch 10](../02-language/10-java-time.md).

---

## Part 2 — Conceptual questions

The remaining sections are the banded questions from [Chapters 06–10](../02-language/06-lambdas-functional-interfaces.md) — lambdas, streams, collectors, `Optional`, and `java.time`.

!!! note "Generated"
    60 questions harvested from 5 chapters by `tools/build-interview-bank.py`. Edit the chapters, not this page.

!!! tip "Use it as a self-test"
    Answer each question aloud before expanding the answer. If your answer is missing the mechanism — *why*, not just *what* — reread the chapter's Internals section.

## Most frequently asked

The 10 questions marked high-frequency across these chapters. Start here.

**What is a functional interface?** ⭐  
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    An interface with exactly one abstract method, which makes it a valid target type for a lambda or method reference. Default and static methods do not count toward that total, which is how `Comparator` carries many helper methods and remains a lambda target. `@FunctionalInterface` makes the compiler enforce the constraint.

**How is a lambda different from an anonymous inner class?** ⭐  
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    An anonymous class produces a separate class file and allocates an instance at every evaluation. A lambda compiles its body to a private method and the call site to `invokedynamic`, so the implementation class is generated at runtime and non-capturing lambdas are cached as singletons. They also differ semantically: `this` inside a lambda refers to the enclosing instance, while inside an anonymous class it refers to the anonymous instance.

**What is the difference between intermediate and terminal operations?** ⭐  
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Intermediate operations like `filter` and `map` return a stream and are lazy — they build up the pipeline without processing anything. A terminal operation like `collect` or `forEach` triggers execution and produces a result or a side effect. A pipeline with no terminal operation does nothing at all.

**In what order do stream operations execute?** ⭐  
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Element by element through the whole pipeline, not stage by stage. Each element is pushed through `filter`, then `map`, then the terminal sink before the next element is read, which is why short-circuiting works and why a `findFirst` can stop after examining three of a million elements. Stateful operations like `sorted` break this by buffering everything before emitting anything.

**What is the difference between `reduce` and `collect`?** ⭐  
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    `reduce` performs an immutable reduction: each step takes the running value and an element and returns a new value, so it suits sums, maxima, and concatenations of value types. `collect` performs a mutable reduction: it creates a container once and mutates it as elements arrive, which is what building a list, set, or map requires. Using `reduce` to build a collection either copies the container per element or shares mutable state unsafely.

**What are the traps in `Collectors.toMap`?** ⭐  
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Three. Duplicate keys throw `IllegalStateException` unless you supply a merge function, and that happens at runtime on data your tests probably do not have. A null value throws `NullPointerException`, even though `HashMap` accepts nulls, because `toMap` uses `merge` internally. And the result is a `HashMap`, so if iteration order matters you must pass a map factory.

**What problem does `Optional` solve?** ⭐  
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    It lets a method signature state that a result may be absent, which a plain reference type cannot. Before it, callers had to learn from documentation or from a production NPE whether a method could return null. It also supplies a vocabulary — `map`, `filter`, `orElse` — for handling absence without nested null checks.

**Why shouldn't `Optional` be used as a field or a parameter?** ⭐  
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    `Optional` is not `Serializable`, so a field breaks serialization, and it adds a wrapper allocation per instance for information a null or a default already conveys. As a parameter it pushes work onto callers, who must write `Optional.empty()` at call sites where an overload would say the same thing better. The JDK follows this itself: `Optional` appears as a return type throughout the API and as a field or parameter nowhere.

**Why was `java.time` introduced when `Date` and `Calendar` existed?** ⭐  
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    Because the old API was mutable, not thread-safe, and type-confused: `Date` is an instant despite its name, months are zero-based, and `SimpleDateFormat` corrupts output when shared across threads. `java.time` is immutable and thread-safe throughout, uses one-based months and named enums, and separates the concepts — instant, date, time, zoned date-time — into distinct types so the compiler catches misuse.

**What type should you use to store when an order was placed?** ⭐  
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    `Instant`, or `OffsetDateTime` if the original offset is itself information worth keeping. It is a point on the timeline, independent of any calendar or zone, and it compares and sorts correctly regardless of where it was created. Convert to a `ZonedDateTime` only at the presentation edge, in the viewer's zone.

---

## L1 — Foundations

15 questions.

### Lambdas & Functional Interfaces

**What is a functional interface?** ⭐  
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    An interface with exactly one abstract method, which makes it a valid target type for a lambda or method reference. Default and static methods do not count toward that total, which is how `Comparator` carries many helper methods and remains a lambda target. `@FunctionalInterface` makes the compiler enforce the constraint.

**What is the difference between `Function`, `Predicate`, `Consumer`, and `Supplier`?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    `Function<T,R>` takes one value and returns another. `Predicate<T>` takes one value and returns a boolean, for filtering. `Consumer<T>` takes a value and returns nothing, for side effects. `Supplier<T>` takes nothing and produces a value, typically for lazy or deferred creation. Nearly every other interface in `java.util.function` is a variation of these with more arguments or primitive types.

**What are the kinds of method reference?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    Four: static (`Integer::parseInt`), bound instance (`catalogue::priceFor`, on a specific object), unbound instance (`CartLine::lineTotal`, where the receiver becomes the first parameter), and constructor (`ArrayList::new`). The unbound form is the one people misread, because the receiver appears as an argument rather than before the dot.

### The Stream API

**What is the difference between intermediate and terminal operations?** ⭐  
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Intermediate operations like `filter` and `map` return a stream and are lazy — they build up the pipeline without processing anything. A terminal operation like `collect` or `forEach` triggers execution and produces a result or a side effect. A pipeline with no terminal operation does nothing at all.

**What is the difference between `map` and `flatMap`?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    `map` applies a one-to-one transformation, so ten elements in gives ten out. `flatMap` applies a function that returns a stream per element and merges them into one flat stream, so ten elements can produce any number. Use `flatMap` when each element expands into several — orders to their lines, or unwrapping `Optional`.

**Can you reuse a stream?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    No. A stream supports exactly one terminal operation; a second throws `IllegalStateException`. Streams are pipeline descriptions over a source, not containers, so if you need two results from the same data, either collect once and derive both, or create a fresh stream from the source.

### Collectors & Stream Composition

**What is the difference between `reduce` and `collect`?** ⭐  
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    `reduce` performs an immutable reduction: each step takes the running value and an element and returns a new value, so it suits sums, maxima, and concatenations of value types. `collect` performs a mutable reduction: it creates a container once and mutates it as elements arrive, which is what building a list, set, or map requires. Using `reduce` to build a collection either copies the container per element or shares mutable state unsafely.

**What does `groupingBy` return?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    A `Map` whose keys come from the classifier function and whose values are, by default, a `List` of the elements in each group. The map is a `HashMap`, so key order is unspecified. A second argument — the downstream collector — decides what each group becomes: a count, a sum, a set, or another grouping.

**What is the difference between `groupingBy` and `partitioningBy`?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    `partitioningBy` takes a predicate and always produces exactly two entries, `true` and `false`, even when one side is empty. `groupingBy` with a boolean classifier omits a key entirely when no element matches. For a yes/no split, `partitioningBy` is safer because `get(true)` is never null.

### Optional & Null Strategy

**What problem does `Optional` solve?** ⭐  
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    It lets a method signature state that a result may be absent, which a plain reference type cannot. Before it, callers had to learn from documentation or from a production NPE whether a method could return null. It also supplies a vocabulary — `map`, `filter`, `orElse` — for handling absence without nested null checks.

**What is the difference between `Optional.of` and `Optional.ofNullable`?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    `of` throws `NullPointerException` if given null, so it asserts that the value is present. `ofNullable` converts null to empty, so it adapts code that may legitimately return null. Using `ofNullable` everywhere hides bugs that `of` would surface at the point of creation.

**What is the difference between `orElse` and `orElseGet`?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    `orElse` takes a value, so its argument is evaluated before the call regardless of whether the `Optional` is present. `orElseGet` takes a supplier, invoked only when empty. Use `orElse` for constants and `orElseGet` for anything computed — otherwise you pay the cost on every call, including the happy path.

### java.time

**Why was `java.time` introduced when `Date` and `Calendar` existed?** ⭐  
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    Because the old API was mutable, not thread-safe, and type-confused: `Date` is an instant despite its name, months are zero-based, and `SimpleDateFormat` corrupts output when shared across threads. `java.time` is immutable and thread-safe throughout, uses one-based months and named enums, and separates the concepts — instant, date, time, zoned date-time — into distinct types so the compiler catches misuse.

**What is the difference between `LocalDateTime` and `ZonedDateTime`?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    `LocalDateTime` is a date and time with no zone, so it does not identify a point on the timeline — 14:30 on 20 September is a different instant in Kolkata than in London. `ZonedDateTime` adds a `ZoneId` with its DST rules, which makes it unambiguous. Use `LocalDateTime` only for recurring wall-clock concepts, never for recording when something happened.

**What is the difference between `Duration` and `Period`?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    `Duration` measures time in seconds and nanoseconds, so `ofDays(1)` is exactly 86,400 seconds. `Period` measures calendar amounts in years, months, and days, so one day means the same wall-clock time on the next date. Across a DST boundary they give different answers, and choosing the wrong one produces a bug that appears twice a year.

---

## L2 — Professional

15 questions.

### Lambdas & Functional Interfaces

**How is a lambda different from an anonymous inner class?** ⭐  
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    An anonymous class produces a separate class file and allocates an instance at every evaluation. A lambda compiles its body to a private method and the call site to `invokedynamic`, so the implementation class is generated at runtime and non-capturing lambdas are cached as singletons. They also differ semantically: `this` inside a lambda refers to the enclosing instance, while inside an anonymous class it refers to the anonymous instance.

**Why must captured local variables be effectively final?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    Because a lambda captures the *value* of a local, not the variable — locals live on the stack and the lambda may outlive the frame. Allowing reassignment would leave the lambda holding a stale copy with no way to reconcile. Fields are exempt because they are captured through `this` by reference.

**Why were default methods added to interfaces?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    To allow interface evolution without breaking implementations. Adding `stream()`, `forEach`, and `removeIf` to `Collection` in Java 8 would have broken every existing implementer, unless the new methods shipped with bodies. Multiple inheritance of behaviour is the side effect, resolved by three rules: a class beats an interface, a more specific interface beats a less specific one, and otherwise the implementer must override explicitly.

### The Stream API

**In what order do stream operations execute?** ⭐  
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Element by element through the whole pipeline, not stage by stage. Each element is pushed through `filter`, then `map`, then the terminal sink before the next element is read, which is why short-circuiting works and why a `findFirst` can stop after examining three of a million elements. Stateful operations like `sorted` break this by buffering everything before emitting anything.

**Why is `peek` unreliable?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Because the pipeline may elide operations it can prove unnecessary. Since Java 9, `count()` can answer from the source's known size without traversing at all, so a `peek` before it never runs. It is documented for debugging specifically because its execution is not guaranteed, which makes it wrong for any side effect that matters.

**Why use `mapToInt` instead of `map` for numbers?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Because `map` on a `Stream<T>` produces a `Stream<Integer>`, boxing every element, while `mapToInt` produces an `IntStream` that works on primitives. It also unlocks `sum`, `average`, and `summaryStatistics`, which only exist on primitive streams. On large datasets the boxing difference is measurable in allocation and GC pressure.

### Collectors & Stream Composition

**What are the traps in `Collectors.toMap`?** ⭐  
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Three. Duplicate keys throw `IllegalStateException` unless you supply a merge function, and that happens at runtime on data your tests probably do not have. A null value throws `NullPointerException`, even though `HashMap` accepts nulls, because `toMap` uses `merge` internally. And the result is a `HashMap`, so if iteration order matters you must pass a map factory.

**What is a downstream collector?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    The second argument to `groupingBy` or `partitioningBy`, deciding what each group is reduced to. It can be any collector — `counting()`, `toSet()`, `mapping(...)`, or another `groupingBy`, which is how arbitrary nesting works with no special support in the API. This composability is what makes `collect` more than a list builder.

**`filtering` downstream versus `filter` upstream — what is the difference?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Filtering before `groupingBy` removes elements before classification, so a group whose elements are all filtered out disappears from the result entirely. `filtering` as a downstream classifies first and filters within each group, so the key survives with an empty collection. Which you want depends on whether the report should show the empty group, and the two spellings look nearly identical.

### Optional & Null Strategy

**Why shouldn't `Optional` be used as a field or a parameter?** ⭐  
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    `Optional` is not `Serializable`, so a field breaks serialization, and it adds a wrapper allocation per instance for information a null or a default already conveys. As a parameter it pushes work onto callers, who must write `Optional.empty()` at call sites where an overload would say the same thing better. The JDK follows this itself: `Optional` appears as a return type throughout the API and as a field or parameter nowhere.

**When do you use `flatMap` instead of `map` on an `Optional`?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    When the function you are applying already returns an `Optional`. `map` would wrap that result again, producing `Optional<Optional<T>>`; `flatMap` merges the two levels. It is the same rule as streams — if the mapper returns the wrapper type, flat-map it.

**Why is calling `get()` discouraged?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    Because it throws `NoSuchElementException` on empty, making it exactly as unsafe as the null dereference `Optional` was meant to prevent, while its name suggests it is the normal way to read the value. Java 10 added `orElseThrow()` as an identically-behaving method with an honest name. Where absence really is a bug, use `orElseThrow()`; otherwise use `map`, `orElseGet`, or `ifPresent`.

### java.time

**What type should you use to store when an order was placed?** ⭐  
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    `Instant`, or `OffsetDateTime` if the original offset is itself information worth keeping. It is a point on the timeline, independent of any calendar or zone, and it compares and sorts correctly regardless of where it was created. Convert to a `ZonedDateTime` only at the presentation edge, in the viewer's zone.

**Why is `SimpleDateFormat` dangerous and what replaces it?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    It holds mutable parsing state in instance fields, so a shared instance used concurrently produces wrong results or exceptions — silently, and usually only under load. The replacement, `DateTimeFormatter`, is immutable and thread-safe, so a `static final` field is correct. Legacy code with a static `SimpleDateFormat` is a real bug even when it appears to work.

**How do you make code that reads the current time testable?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    Inject a `Clock` and use the `now(clock)` overloads that every `java.time` type provides. Tests pass `Clock.fixed` to freeze time or `Clock.offset` to shift it, so date-dependent logic becomes deterministic with no static mocking. It also improves the production code, by making time an explicit dependency rather than ambient state.

---

## L3 — Enterprise

15 questions.

### Lambdas & Functional Interfaces

**What does `invokedynamic` do for lambdas, and why does it matter?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    It defers the decision of how to create the lambda instance to the runtime: on first execution the JVM calls `LambdaMetafactory`, which spins an implementation class and returns a linked call site used for all subsequent calls. This avoids a class file per lambda, allows non-capturing lambdas to be cached as singletons, and — importantly — means the strategy is not fixed by the class file. Lambda performance improved across JDK releases with no recompilation.

**How do you handle checked exceptions in a lambda?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    None of the standard functional interfaces declare them, so the options are to catch and wrap inside the lambda, to define your own throwing interface plus an adapter that wraps, or to keep the code as an ordinary loop where the checked exception propagates normally. The loop is often the right answer — a `try`/`catch` inside every lambda reads worse than the loop it replaced, and wrapping in `RuntimeException` loses the compiler's help without gaining much.

**When does a lambda allocate, and when does it not?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    A lambda that captures nothing from its enclosing scope is stateless, so the metafactory can return the same instance on every evaluation — no allocation after the first. A lambda that captures a local or the enclosing `this` needs those values stored, so a new instance is created per evaluation. In a hot loop this is the difference between zero allocation and one object per iteration, which is worth knowing though rarely worth contorting code for.

### The Stream API

**When does `parallel()` actually help?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    When the dataset is large, the per-element work is CPU-bound and substantial, the source splits cheaply — an array or `ArrayList` rather than a linked structure — and the operation is stateless and associative. Outside that combination the split-and-merge overhead usually exceeds the gain. The default should be sequential, with `parallel()` added after measurement rather than on the assumption that more data means more parallelism.

**What is the risk of parallel streams in a web application?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    They run on the shared `ForkJoinPool.commonPool()`, sized for CPU work and shared by the entire JVM. Concurrent requests contend for the same small pool, and any blocking operation inside a parallel stream consumes a pool thread while doing nothing, starving every other parallel stream in the process. There is no per-pipeline pool parameter, so the fix is to use an executor or virtual threads for that work instead.

**What does a `Spliterator` do, and why does the source matter?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    It drives traversal with `tryAdvance` and enables parallelism with `trySplit`, and it reports characteristics — `SIZED`, `ORDERED`, `DISTINCT`, `SORTED` — that the pipeline uses to skip work. The source determines how well it splits: an `ArrayList` halves in constant time, a `LinkedList` must be walked, and a generator barely splits at all. That is why the same parallel pipeline can be fast on one collection and slower than sequential on another.

### Collectors & Stream Composition

**What are the five components of a `Collector`?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    `supplier` creates an empty container, `accumulator` folds one element into it, `combiner` merges two containers, `finisher` converts the container into the final result, and `characteristics` supplies hints such as `IDENTITY_FINISH`, `UNORDERED`, and `CONCURRENT`. The combiner is only invoked for parallel streams, and the finisher is skipped entirely when `IDENTITY_FINISH` is set.

**Why do custom collectors break only under `parallel()`?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Because the combiner is never called on a sequential stream — there is one container from start to finish. A combiner that returns the wrong container, drops elements, or is not associative therefore passes every sequential test and fails non-deterministically the moment someone parallelises the pipeline. Writing the combiner and reasoning about associativity is the part that cannot be skipped.

**When does `groupingByConcurrent` actually help?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Only on a parallel, unordered stream where the concurrent map's write cost is lower than the cost of building and merging per-thread maps — typically large streams with many small groups. It declares `CONCURRENT`, which lets every thread accumulate into one shared `ConcurrentMap` and skips the merge tree entirely. On a sequential stream it is strictly worse, since you pay concurrent-write overhead for no parallelism.

### Optional & Null Strategy

**What does it mean that `Optional` is a value-based class?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    It means identity is unspecified: two `Optional` instances wrapping equal values may or may not be the same object, so `==` comparison, synchronisation, and identity-sensitive uses are all unsupported. It also signals the class is a candidate for Project Valhalla's value types, which would remove the allocation entirely. The practical rules are to compare with `equals`, never lock on one, and never rely on `Optional.empty()` returning a cached instance.

**What is a complete null strategy, beyond `Optional`?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    `Optional` covers return types where absence is expected. Parameters use `Objects.requireNonNull` to fail fast at the boundary with a named argument. Collection-returning methods return empty collections rather than null or `Optional`. Fields use null with a nullability annotation, or a default value, or the Null Object pattern where absence has behaviour. Nullability annotations plus static analysis then enforce what the compiler cannot.

**Does `Optional` have a performance cost worth caring about?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    Every `Optional` is an allocation, so a hot lookup path returning one per call allocates per call. Escape analysis frequently eliminates it — the wrapper usually does not escape the calling method, so the JIT can scalarise it — but not always, and not predictably. In a measured hot path, returning a documented nullable value is a legitimate trade; everywhere else the clarity is worth more than the allocation.

### java.time

**What happens when you construct a `ZonedDateTime` for a time that does not exist?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    During a spring-forward gap, `ZonedDateTime.of` moves the result forward by the length of the gap rather than throwing — 01:30 becomes 02:30. In a fall-back overlap, where a wall-clock time occurs twice, it selects the earlier offset, and `withLaterOffsetAtOverlap()` chooses the second occurrence. Silent resolution is usually what you want, but it means a scheduling bug produces a wrong time instead of an error, so check `getRules().getValidOffsets(...)` if a gap should be rejected in your domain.

**Why store a `ZoneId` rather than an offset for a future event?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    Because the offset for a given zone changes — with DST, and occasionally by legislation. An event stored as `+01:00` next October keeps that offset even if the rules change, so it drifts relative to local time. Storing `Europe/London` plus the local time lets the current rules resolve the offset at the point it matters. For past events the reverse holds: recording the actual offset is more faithful than depending on the current tz database.

**What precision issues arise when persisting an `Instant`?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    `Instant` holds nanoseconds, but Postgres `timestamptz` and MySQL `DATETIME(6)` store microseconds, and `java.util.Date` only milliseconds. A value round-tripped through the database comes back truncated, so equality assertions fail and comparisons drift. Truncate explicitly with `truncatedTo(ChronoUnit.MICROS)` before persisting, so the loss is deliberate and the in-memory value matches what was stored.

---

## L4 — Architect

15 questions.

### Lambdas & Functional Interfaces

**When is a functional interface the right API design, and when is it not?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    It fits when the abstraction genuinely is one operation and callers will supply varied behaviour — a pricing rule, a retry policy, a key extractor. It stops fitting when the abstraction has multiple related operations, needs named implementations for logging and configuration, or benefits from identity for registration and deregistration. Lambdas have unspecified identity and unhelpful `toString`, so a plugin registry keyed on handler instances should take named objects, not lambdas.

**A team's codebase has `Function<String, Function<Integer, Function<Order, Money>>>` in its API. What is wrong and what do you propose?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    Currying nested functions is idiomatic in languages with the syntax to support it; in Java it produces types nobody can read, no parameter names, no documentation targets, and stack traces full of `lambda$`. Replace it with a named interface whose single method has named parameters, or with a small record carrying the inputs. The functional core is fine — the problem is expressing it through anonymous generic composition rather than through a type with a name.

**How would you evaluate whether converting loops to lambdas and streams improved a codebase?**   
<small>[Lambdas & Functional Interfaces](../02-language/06-lambdas-functional-interfaces.md)</small>

??? success "Answer"
    By the same criteria as any refactoring: does the intent read more directly, do failures localise better, and is the performance acceptable. Lambdas win where the loop was ceremony around one expression, and lose where the body is long, throws checked exceptions, mutates several variables, or needs `break` semantics that do not express well. Stack traces and debuggability are a real cost — measure by asking whether a developer unfamiliar with the code can follow a production stack trace back to a line.

### The Stream API

**A team has rewritten all loops as streams and performance regressed. How do you approach it?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Profile before theorising, but the usual causes are predictable: boxing where primitive streams belonged, `parallel()` added on small or blocking workloads, `sorted()` or `distinct()` forcing full buffering in pipelines that were previously short-circuiting, and `Collectors.toMap` or `groupingBy` doing expensive merging under parallelism. The deeper issue is treating the rewrite as an end in itself — a stream that replaces ceremony is an improvement, one that replaces a tight numeric loop usually is not.

**How would you decide whether a data-processing pipeline belongs in streams, in a loop, or in the database?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    By where the data lives and how much of it moves. Aggregation over a large table belongs in SQL — pulling a million rows into the JVM to `groupingBy` them is the wrong boundary regardless of how the Java reads. Streams fit in-memory transformation of data you already hold, especially where the pipeline reads as a description of the transformation. A loop stays right where the body does several things, throws checked exceptions, or needs early exit with complex state.

**What do Stream Gatherers change about this picture?**   
<small>[The Stream API](../02-language/07-stream-api.md)</small>

??? success "Answer"
    Until Java 24 the set of intermediate operations was closed — you could write a custom `Collector` for the terminal step, but windowing, running folds, and stateful scans had no expression and got rewritten as loops. Gatherers (JEP 485) make intermediate operations extensible, so sliding windows, fixed batches, and scan-style operations become first-class pipeline stages. It closes the main gap where a stream previously had to be abandoned halfway.

### Collectors & Stream Composition

**When should you write a custom collector rather than compose existing ones?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    Rarely, and only when the composition genuinely cannot express the operation — a bounded top-N that must not buffer the whole stream, or an accumulation into a domain-specific structure with its own merge semantics. `mapping`, `filtering`, `flatMapping`, `collectingAndThen`, `reducing`, and `teeing` cover nearly everything else. The cost of a custom collector is the combiner: you now own a correctness obligation that only manifests under parallelism.

**A report pipeline does four passes over the same list to compute four aggregates. How would you restructure it?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    If the aggregates are a count, sum, min, max, and average of one numeric field, `summarizingInt` gives all five in one pass. For two aggregates needing different collectors, `teeing` merges them at the end of a single traversal. Beyond two, a small custom collector or a record accumulator with a three-argument `collect(supplier, accumulator, combiner)` is cleaner than nesting `teeing` calls — at which point it is worth asking whether the aggregation belongs in the database instead.

**How do Stream Gatherers relate to collectors?**   
<small>[Collectors & Stream Composition](../02-language/08-collectors.md)</small>

??? success "Answer"
    They are the mirror image. A `Collector` is an extensible *terminal* operation; until Java 24 the set of *intermediate* operations was closed, so windowing, running folds, and stateful scans had no expression in a pipeline and got rewritten as loops. Gatherers make intermediate operations extensible with a similar four-function shape — initializer, integrator, combiner, finisher. Together they close the extensibility gap at both ends of a stream.

### Optional & Null Strategy

**How would you introduce `Optional` into a large legacy codebase?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    At API boundaries first, working inward: change lookup and finder methods that currently return null, since those are where callers most often get it wrong, and the compiler forces every caller to confront the change. Do not sweep internal code — an `Optional` on a private method that is always present adds noise. Resist converting fields and parameters entirely. Pair the change with nullability annotations and a static-analysis gate, because `Optional` only documents the cases it covers.

**When is a sealed result type better than `Optional`?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    When absence has a reason that callers must distinguish. `Optional<InventoryItem>` cannot tell "no such SKU" from "SKU exists but is discontinued" from "catalogue unreachable", and callers that need to react differently end up throwing exceptions for control flow. A sealed interface with `Found`, `Discontinued`, and `Unavailable` variants, consumed with pattern matching for `switch`, makes every case explicit and exhaustively checked by the compiler. `Optional` is the right tool when the only question is present or absent.

**A team has `Optional` in fields, parameters, and collections throughout. How do you unwind it?**   
<small>[Optional & Null Strategy](../02-language/09-optional.md)</small>

??? success "Answer"
    Start by establishing why: usually someone read "don't use null" as "use `Optional` everywhere", so the fix is a shared convention before a code change. Then prioritise by risk — `Optional` fields on serializable types may already be failing in production, and `Optional` inside collections doubles the emptiness cases callers must handle. Parameters come next, replaced by overloads, since each change ripples to call sites and is best done per class with the compiler enforcing completeness. Leave return types alone: those are the ones that were right.

### java.time

**How would you design date-time handling across a distributed system?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    Standardise on `Instant` for everything that records when something happened, serialised as ISO-8601 with an explicit offset, and never depend on any JVM's default zone. Keep `ZoneId` alongside the local time for future scheduled events, since only the zone survives rule changes. Convert to human time at the presentation edge and nowhere else, so services compare and sort on unambiguous values. Then make tz database currency an operational concern — a stale JDK schedules against stale rules.

**A system stores `LocalDateTime` for order timestamps and is now being deployed in a second region. What is the problem and how do you fix it?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    The stored values are ambiguous: they were written in whatever the original server's default zone was, which is an assumption recorded nowhere. Ordering, filtering, and reporting across regions will silently mix wall-clock times from different offsets. The fix is a migration to `Instant` or `OffsetDateTime`, but it needs a documented assumption about the zone the existing data was written in — and if the original deployment ever changed zones or observed DST, some rows are genuinely unrecoverable and the assumption has to be stated rather than discovered.

**When is `OffsetDateTime` the right choice over `Instant` or `ZonedDateTime`?**   
<small>[java.time](../02-language/10-java-time.md)</small>

??? success "Answer"
    When you need a point on the timeline *and* the offset that applied where it was recorded, but not the full zone rules. It is the natural type for API payloads and database columns, since it is unambiguous, sorts correctly, and preserves the local context of the event without depending on the tz database. `Instant` is better internally where the offset carries no meaning, and `ZonedDateTime` is required only when future arithmetic must respect DST rules.

