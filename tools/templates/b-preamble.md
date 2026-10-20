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

