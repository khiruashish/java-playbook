---
title: ConcurrentHashMap Guide
tags: [java, collections, concurrency, thread-safe]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: senior
related: [hashmap-guide.md]
---

## Java ConcurrentHashMap — Production Design & Usage Guide (Java 8–21)

---

## 1. Purpose & Audience

- **Purpose**: Provide a production-grade design and usage guide for `ConcurrentHashMap`, explaining:
  - **How it works** (high-level internals, guarantees).
  - **Why it’s needed** (vs `HashMap`, `Hashtable`, synchronized wrappers).
  - **How to use it safely** from beginner to advanced/enterprise scenarios.
- **Audience**:
  - Backend and microservice engineers working on concurrent Java systems.
  - Engineers preparing for system design / concurrency interviews.
  - Code reviewers evaluating concurrency-related changes.

---

## 2. Overview

- **`ConcurrentHashMap<K,V>`** is a highly concurrent, thread-safe implementation of `Map`.
- **Key characteristics**:
  - **Thread-safe**: all standard `Map` operations are safe under concurrent access.
  - **Non-blocking reads**: `get`, `containsKey`, etc. do not acquire locks in the common path.
  - **Fine-grained locking / CAS for writes**: writes affect only specific buckets (bins), not the entire map.
  - **Weakly consistent iterators**: iterators never throw `ConcurrentModificationException`, but may see some or none of concurrent updates.
  - **No null keys or values**: all attempts to store `null` result in `NullPointerException`.
- **Typical use cases**:
  - In-memory caches.
  - Metrics and counters.
  - Per-tenant state registries.
  - Thread-safe lookup tables in microservices.

---

## 3. Behavioral Guarantees

- **Thread-safety**:
  - Concurrent `get`, `put`, `remove`, `compute`, `merge`, etc. are safe.
- **Visibility / happens-before**:
  - Once a write operation (e.g., `put`, `compute`, `merge`) returns, its effect becomes visible to other threads according to Java’s memory model (uses `volatile`, CAS, and synchronization internally).
- **Iterators and views**:
  - `keySet()`, `values()`, `entrySet()` and their iterators:
    - Are **weakly consistent**: see a snapshot “around” iteration time.
    - Do **not** throw `ConcurrentModificationException`.
    - Never expose a corrupted internal state.
- **Size and counting**:
  - `size()` and `mappingCount()` are **eventually consistent** under concurrent updates.
  - They can be used for monitoring and heuristics, but not for strict coordination logic.

---

## 4. Internal Design (Java 8+)

### 4.1 High-level architecture

- **Core structure**:
  - Backed by an internal array `Node<K,V>[] table`.
  - Each index in the table is a **bin**, which is either:
    - A short **linked list** of nodes, or
    - A **tree bin** (red-black tree) when collisions are high.
- **Hashing**:
  - Uses a **spread hash** to reduce collisions and distribute keys evenly across bins.

### 4.2 Concurrency model

- **Reads (`get`, `containsKey`, etc.)**:
  - Compute hash, find bin index, traverse bin (list/tree).
  - Typically **lock-free**; only rely on `volatile` reads for visibility.
- **Writes (`put`, `remove`, `compute*`, `merge`)**:
  - Target a single bin:
    - Empty bin: often installed via **CAS**.
    - Non-empty bin: mutate under a **per-bin lock** (synchronized on bin head).
  - This enables high parallelism: different threads can mutate different bins concurrently.
- **Resizing**:
  - When the map grows beyond a threshold, the table is resized.
  - Multiple threads can **help** with resizing by migrating bins to the new table.
  - Uses **forwarding nodes** to coordinate bins that are already moved.

### 4.3 Java 21 `SequencedMap` note

- In Java 21, `ConcurrentHashMap` implements **`SequencedMap`**, adding methods such as:
  - `firstEntry()`, `lastEntry()`, `pollFirstEntry()`, `pollLastEntry()`, `reversed()`.
- **Important**:
  - `ConcurrentHashMap` **does not maintain insertion order**.
  - These operations work on the current iteration order but **must not be used as strict ordering guarantees**.
  - For strict order, prefer `ConcurrentSkipListMap` or synchronized ordered maps.

---

## 5. Construction and Basic Usage

### 5.1 Constructors

```java
ConcurrentHashMap<String, Integer> empty = new ConcurrentHashMap<>();

ConcurrentHashMap<String, Integer> withCapacity =
        new ConcurrentHashMap<>(16); // initial capacity

ConcurrentHashMap<String, Integer> withParams =
        new ConcurrentHashMap<>(16, 0.75f, 4); // capacity, load factor, concurrency level (hint)

ConcurrentHashMap<String, Integer> fromMap =
        new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
```

- **Guidelines**:
  - **Initial capacity**: if you know approximate size \(N\), consider `initialCapacity ≈ N / 0.75` to reduce resizes.
  - **Concurrency level**: in Java 8+, treated largely as a legacy hint; can usually leave default.

---

## 6. API Overview by Category

> For **full per-method examples with outputs** (e.g., `put`, `get`, `compute`, `merge`, `forEach`, `search`, `reduce`, map/list conversions, Java 21 methods), see **Appendix A** below, where the detailed “Complete Guide” reference is included.

### 6.1 Basic CRUD

- **Insertion and update**:
  - `V put(K key, V value)` – unconditional insert/replace.
  - `V putIfAbsent(K key, V value)` – insert only if key is absent (atomic).
  - `void putAll(Map<? extends K, ? extends V> m)` – copy all mappings.
- **Read**:
  - `V get(Object key)` – value or `null`.
  - `V getOrDefault(Object key, V defaultValue)` – value or default.
  - `boolean containsKey(Object key)` – key existence.
  - `boolean containsValue(Object value)` – may scan entire map; slower.
- **Removal**:
  - `V remove(Object key)` – remove by key.
  - `boolean remove(Object key, Object value)` – conditional remove (atomic).

### 6.2 Atomic update methods

- **Compare-and-update style**:
  - `V replace(K key, V value)`
  - `boolean replace(K key, V oldValue, V newValue)` – CAS-based.
- **Compute family**:
  - `V compute(K key, BiFunction<? super K, ? super V, ? extends V> f)` – always runs function; `null` removes.
  - `V computeIfAbsent(K key, Function<? super K, ? extends V> f)` – runs only when key is absent.
  - `V computeIfPresent(K key, BiFunction<? super K, ? super V, ? extends V> f)` – runs only when key is present.
- **Merge**:
  - `V merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)`
    - Absent → insert `value`.
    - Present → `remappingFunction(old, value)`.
    - Return `null` to remove.

**Design guideline**: For any **“read-modify-write”** operation (e.g., counters, aggregations, conditional updates), prefer expressing the logic via **`compute*`** or **`merge`** instead of manual `get` + `put`.

### 6.3 Views and bulk operations

- **Views**:
  - `Set<K> keySet()`
  - `Collection<V> values()`
  - `Set<Map.Entry<K, V>> entrySet()`
  - `keySet`, `values`, and `entrySet` are **live views** with weakly consistent iterators.
- **Bulk operations (Java 8)**:
  - `forEach(...)` – apply action for each entry (sequential or parallel based on threshold).
  - `search(...)` – return first non-null result from applying a function over entries.
  - `reduce(...)` – aggregate entries using transformer + reducer functions.

### 6.4 Transformations and conversions

- **In-place transform**:
  - `void replaceAll(BiFunction<? super K, ? super V, ? extends V> function)` – change all values in-place.
- **Filtering**:
  - `map.entrySet().removeIf(predicate)` – remove entries matching a condition.
- **Conversions (Map → List)**:
  - Snapshot keys: `new ArrayList<>(map.keySet())`.
  - Snapshot values: `new ArrayList<>(map.values())`.
  - Snapshot entries: `new ArrayList<>(map.entrySet())`.
- **Conversions (List → ConcurrentHashMap)**:
  - Using streams and `Collectors.toConcurrentMap(...)`.

---

## 7. Enterprise-Level Patterns

### 7.1 Read-through cache with `computeIfAbsent`

```java
public class UserProfileCache {

    private final ConcurrentHashMap<Long, UserProfile> cache = new ConcurrentHashMap<>();
    private final UserProfileRepository repository;

    public UserProfileCache(UserProfileRepository repository) {
        this.repository = repository;
    }

    public UserProfile get(long userId) {
        return cache.computeIfAbsent(userId, repository::findById);
    }

    public void invalidate(long userId) {
        cache.remove(userId);
    }

    public void clear() {
        cache.clear();
    }
}
```

### 7.2 Concurrent metrics / counters

```java
public class MetricsRegistry {

    private final ConcurrentHashMap<String, Long> counters = new ConcurrentHashMap<>();

    public void increment(String metricName) {
        counters.merge(metricName, 1L, Long::sum); // atomic increment
    }

    public long getCount(String metricName) {
        return counters.getOrDefault(metricName, 0L);
    }

    public Map<String, Long> snapshot() {
        return new HashMap<>(counters); // stable snapshot for export
    }
}
```

### 7.3 Per-tenant state partitioning

```java
public class TenantStateStore {

    private final ConcurrentHashMap<String, ConcurrentHashMap<String, String>> tenantData =
            new ConcurrentHashMap<>();

    public void put(String tenantId, String key, String value) {
        tenantData
            .computeIfAbsent(tenantId, id -> new ConcurrentHashMap<>())
            .put(key, value);
    }

    public String get(String tenantId, String key) {
        ConcurrentHashMap<String, String> tenantMap = tenantData.get(tenantId);
        return tenantMap != null ? tenantMap.get(key) : null;
    }

    public Map<String, String> snapshotTenant(String tenantId) {
        ConcurrentHashMap<String, String> tenantMap = tenantData.get(tenantId);
        return tenantMap == null ? Map.of() : new HashMap<>(tenantMap);
    }
}
```

### 7.4 Thread-safe accumulators with nested mutable values

```java
public class Accumulator {

    private final ConcurrentHashMap<String, AtomicInteger> accumulators =
            new ConcurrentHashMap<>();

    public void increment(String key) {
        accumulators
            .computeIfAbsent(key, k -> new AtomicInteger(0))
            .incrementAndGet();
    }

    public int get(String key) {
        AtomicInteger value = accumulators.get(key);
        return value != null ? value.get() : 0;
    }
}
```

---

## 8. Performance, Tuning, and Anti-Patterns

### 8.1 When to use ConcurrentHashMap

- Multiple threads frequently read/write a shared map.
- You need:
  - High throughput and low contention.
  - Atomic compound operations (`compute`, `merge`, `putIfAbsent`).

### 8.2 When not to use

- Single-threaded or effectively single-threaded code → prefer `HashMap`.
- Strict ordering required → `ConcurrentSkipListMap` or synchronized `LinkedHashMap`.
- Complex caching (TTL, LRU/LFU, refresh) → use a cache library (Caffeine, Redis, etc.).

### 8.3 Common anti-patterns

- Manual check-then-act:

```java
// NOT SAFE under concurrency
if (!map.containsKey(key)) {
    map.put(key, computeValue(key));
}
```

- **Prefer**: `map.computeIfAbsent(key, k -> computeValue(k));`

- Mutating non-thread-safe values stored in the map without synchronization.
- Using `size()` for strict decisions under concurrent updates.
- Doing heavy I/O or long-running work inside `compute` / `merge` functions.

---

## 9. HashMap vs ConcurrentHashMap (At a Glance)

| Aspect              | HashMap                                       | ConcurrentHashMap                                        |
|---------------------|-----------------------------------------------|----------------------------------------------------------|
| Thread-safety       | Not thread-safe                               | Thread-safe, highly concurrent                           |
| Null keys/values    | 1 null key, many null values                  | No null keys/values (throws `NullPointerException`)      |
| Reads               | Fast, unsafe under concurrency                | Fast, typically lock-free                                |
| Writes              | Fast, unsafe under concurrency                | Slightly slower due to per-bin locking/CAS               |
| Iterators           | Fail-fast (`ConcurrentModificationException`) | Weakly consistent, never fail-fast                       |
| Size accuracy       | Exact (single-threaded)                       | Approximate under concurrent modifications               |
| Typical use case    | Single-threaded / externally synchronized     | Shared data in concurrent applications                   |

---

## 10. Quick Reference Cheat Sheet

- **Insert / update**:
  - `map.put(k, v)` – unconditional.
  - `map.putIfAbsent(k, v)` – insert-if-absent.
  - `map.compute(k, (k, v) -> ...)` – atomic read-modify-write.
  - `map.merge(k, v, (old, nv) -> ...)` – atomic combine/aggregate.
- **Read**:
  - `map.get(k)`, `map.getOrDefault(k, default)`
  - `map.containsKey(k)`
- **Delete**:
  - `map.remove(k)`
  - `map.remove(k, v)`
- **Transform / filter**:
  - `map.replaceAll((k, v) -> ...)`
  - `map.entrySet().removeIf(e -> condition)`
- **Conversions**:
  - Map → List: `new ArrayList<>(map.keySet())`, `new ArrayList<>(map.values())`
  - List → Map: `list.stream().collect(Collectors.toConcurrentMap(...))`

---

## Appendix A: Detailed API Examples (Reference)

### Java ConcurrentHashMap — Complete Guide (Java 8, Java 21)

Introduction to `ConcurrentHashMap`, thread-safety, all methods with examples and output, transformations, Map → List conversions, concurrent operations, and Java 8 / Java 21 examples.

---

## Table of Contents

- [1. ConcurrentHashMap introduction](#1-concurrenthashmap-introduction)
- [2. All ConcurrentHashMap methods with examples and output](#2-all-concurrenthashmap-methods-with-examples-and-output)
  - [2.1 put, putIfAbsent, putAll](#2-1-put-putifabsent-putall)
  - [2.2 get, getOrDefault](#2-2-get-getordefault)
  - [2.3 remove](#2-3-remove)
  - [2.4 replace, replaceAll](#2-4-replace-replaceall)
  - [2.5 containsKey, containsValue](#2-5-containskey-containsvalue)
  - [2.6 size, isEmpty, mappingCount (Java 8)](#2-6-size-isempty-mappingcount-java-8)
  - [2.7 keySet, values, entrySet](#2-7-keyset-values-entryset)
  - [2.8 compute, computeIfAbsent, computeIfPresent](#2-8-compute-computeifabsent-computeifpresent)
  - [2.9 merge](#2-9-merge)
  - [2.10 forEach (Java 8)](#2-10-foreach-java-8)
  - [2.11 search, reduce (Java 8)](#2-11-search-reduce-java-8)
  - [2.12 Java 21: SequencedMap methods](#2-12-java-21-sequencedmap-methods)
- [3. Thread-safety and concurrent operations](#3-thread-safety-and-concurrent-operations)
  - [3.1 Concurrent reads and writes](#3-1-concurrent-reads-and-writes)
  - [3.2 Atomic operations](#3-2-atomic-operations)
  - [3.3 Concurrent updates with compute](#3-3-concurrent-updates-with-compute)
- [4. Transformations](#4-transformations)
  - [4.1 Transform values (thread-safe)](#4-1-transform-values-thread-safe)
  - [4.2 Filter entries (thread-safe)](#4-2-filter-entries-thread-safe)
- [5. Insertion operations (thread-safe)](#5-insertion-operations-thread-safe)
  - [5.1 Basic insertion](#5-1-basic-insertion)
  - [5.2 Insert only if absent (atomic)](#5-2-insert-only-if-absent-atomic)
  - [5.3 Insert with computeIfAbsent (atomic)](#5-3-insert-with-computeifabsent-atomic)
- [6. Deletion operations (thread-safe)](#6-deletion-operations-thread-safe)
  - [6.1 Remove by key](#6-1-remove-by-key)
  - [6.2 Remove by key-value pair (atomic)](#6-2-remove-by-key-value-pair-atomic)
  - [6.3 Remove entries matching condition](#6-3-remove-entries-matching-condition)
- [7. Map to List conversions](#7-map-to-list-conversions)
  - [7.1 Keys to List](#7-1-keys-to-list)
  - [7.2 Values to List](#7-2-values-to-list)
  - [7.3 Entries to List](#7-3-entries-to-list)
  - [7.4 Stream: keys to List](#7-4-stream-keys-to-list)
- [8. List to ConcurrentHashMap conversions](#8-list-to-concurrenthashmap-conversions)
  - [8.1 List to ConcurrentHashMap](#8-1-list-to-concurrenthashmap)
  - [8.2 List to ConcurrentHashMap with duplicate keys (merge)](#8-2-list-to-concurrenthashmap-with-duplicate-keys-merge)
- [9. Java 8 Stream operations with ConcurrentHashMap](#9-java-8-stream-operations-with-concurrenthashmap)
  - [9.1 Parallel stream operations](#9-1-parallel-stream-operations)
  - [9.2 Sort by value (thread-safe)](#9-2-sort-by-value-thread-safe)
- [10. Coding interview questions](#10-coding-interview-questions)
  - [10.1 Thread-safe counter](#10-1-thread-safe-counter)
  - [10.2 Concurrent frequency counter](#10-2-concurrent-frequency-counter)
  - [10.3 Thread-safe cache with computeIfAbsent](#10-3-thread-safe-cache-with-computeifabsent)
  - [10.4 Concurrent map merge (sum values)](#10-4-concurrent-map-merge-sum-values)
  - [10.5 Thread-safe accumulator](#10-5-thread-safe-accumulator)
- [11. Differences: HashMap vs ConcurrentHashMap](#11-differences-hashmap-vs-concurrenthashmap)
- [12. Quick reference table](#12-quick-reference-table)


---




## 1. ConcurrentHashMap introduction

- **`ConcurrentHashMap<K, V>`** is a thread-safe, hash table-based implementation of the `Map` interface. It allows concurrent read and write operations without external synchronization.
- **Key characteristics:**
  - **Thread-safe** — multiple threads can read and write concurrently without blocking (for most operations).
  - **No locking for reads** — read operations (get, containsKey, etc.) do not block.
  - **Segment-based locking (Java 7)** / **CAS + synchronized (Java 8+)** — write operations lock only the bucket/segment, not the entire map.
  - **No null keys or values** — throws `NullPointerException` if null is inserted.
  - **Weakly consistent iterators** — iterators reflect the state at some point during iteration; may or may not show updates.

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
ConcurrentHashMap<String, Integer> withCapacity = new ConcurrentHashMap<>(16);
ConcurrentHashMap<String, Integer> withLoadFactor = new ConcurrentHashMap<>(16, 0.75f, 4);  // capacity, load factor, concurrency level
```

**Note:** In Java 8+, `concurrencyLevel` parameter is ignored (kept for compatibility). The implementation uses dynamic resizing.

---

## 2. All ConcurrentHashMap methods with examples and output

### 2.1 put, putIfAbsent, putAll

| Method | Description |
|--------|-------------|
| `V put(K key, V value)` | Associates key with value; returns previous value (or null). **Thread-safe.** |
| `V putIfAbsent(K key, V value)` | Puts only if key is absent; returns existing value or null. **Thread-safe.** |
| `void putAll(Map<? extends K, ? extends V> m)` | Copies all mappings from m. **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
Integer old1 = map.put("apple", 10);        // old1 = null, map = {apple=10}
Integer old2 = map.put("apple", 20);        // old2 = 10, map = {apple=20}
Integer old3 = map.putIfAbsent("banana", 30); // old3 = null, map = {apple=20, banana=30}
Integer old4 = map.putIfAbsent("apple", 25);  // old4 = 20 (unchanged), map = {apple=20, banana=30}
map.putAll(Map.of("mango", 40, "berry", 50)); // map = {apple=20, banana=30, mango=40, berry=50}
```

**Output:** `old1 = null`, `old2 = 10`, `old3 = null`, `old4 = 20`; final map: `{apple=20, banana=30, mango=40, berry=50}`

**Thread-safety:** All operations are thread-safe. Multiple threads can call `put` concurrently.

---

### 2.2 get, getOrDefault

| Method | Description |
|--------|-------------|
| `V get(Object key)` | Value for key, or null if absent. **Non-blocking read.** |
| `V getOrDefault(Object key, V defaultValue)` | Value for key, or defaultValue if absent. **Non-blocking read.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
Integer val1 = map.get("apple");              // 10
Integer val2 = map.get("mango");              // null
Integer val3 = map.getOrDefault("mango", 0);   // 0
Integer val4 = map.getOrDefault("apple", 0);   // 10
```

**Output:** `val1 = 10`, `val2 = null`, `val3 = 0`, `val4 = 10`

**Thread-safety:** Read operations do not block; multiple threads can read concurrently.

---

### 2.3 remove

| Method | Description |
|--------|-------------|
| `V remove(Object key)` | Removes mapping for key; returns value (or null). **Thread-safe.** |
| `boolean remove(Object key, Object value)` | Removes only if key maps to value; returns true if removed. **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20, "mango", 30));
Integer removed1 = map.remove("banana");              // removed1 = 20, map = {apple=10, mango=30}
boolean removed2 = map.remove("apple", 10);          // removed2 = true, map = {mango=30}
boolean removed3 = map.remove("mango", 50);          // removed3 = false (value mismatch)
Integer removed4 = map.remove("berry");               // removed4 = null
```

**Output:** `removed1 = 20`, `removed2 = true`, `removed3 = false`, `removed4 = null`; final map: `{mango=30}`

---

### 2.4 replace, replaceAll

| Method | Description |
|--------|-------------|
| `V replace(K key, V value)` | Replaces value for key if present; returns old value (or null). **Thread-safe.** |
| `boolean replace(K key, V oldValue, V newValue)` | Replaces only if key maps to oldValue; returns true if replaced. **Thread-safe (compare-and-swap).** |
| `void replaceAll(BiFunction<? super K, ? super V, ? extends V> function)` | Replaces each value with function(key, value). **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
Integer old1 = map.replace("apple", 15);              // old1 = 10, map = {apple=15, banana=20}
boolean replaced = map.replace("banana", 20, 25);     // replaced = true, map = {apple=15, banana=25}
boolean notReplaced = map.replace("banana", 30, 35);  // notReplaced = false
map.replaceAll((k, v) -> v * 2);                      // map = {apple=30, banana=50}
```

**Output:** `old1 = 10`, `replaced = true`, `notReplaced = false`; after replaceAll: `{apple=30, banana=50}`

**Thread-safety:** `replace(key, oldValue, newValue)` uses **compare-and-swap (CAS)**, making it atomic.

---

### 2.5 containsKey, containsValue

| Method | Description |
|--------|-------------|
| `boolean containsKey(Object key)` | true if map contains key. **Non-blocking.** |
| `boolean containsValue(Object value)` | true if map contains value. **May scan entire map; slower.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
boolean hasKey = map.containsKey("apple");      // true
boolean hasValue = map.containsValue(20);        // true
boolean noKey = map.containsKey("mango");       // false
boolean noValue = map.containsValue(100);       // false
```

**Output:** `hasKey = true`, `hasValue = true`, `noKey = false`, `noValue = false`

---

### 2.6 size, isEmpty, mappingCount (Java 8)

| Method | Description |
|--------|-------------|
| `int size()` | Number of mappings. **May be inaccurate during concurrent updates.** |
| `long mappingCount()` | Number of mappings as long. **More accurate for large maps.** |
| `boolean isEmpty()` | true if size is 0 |
| `void clear()` | Removes all mappings. **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("a", 1, "b", 2));
int size = map.size();              // 2
long count = map.mappingCount();     // 2L (Java 8+)
boolean empty = map.isEmpty();       // false
map.clear();                        // map = {}
boolean emptyAfter = map.isEmpty(); // true
```

**Output:** `size = 2`, `count = 2L`, `empty = false`, after clear `emptyAfter = true`

**Note:** `size()` may be inaccurate during concurrent modifications. Use `mappingCount()` for better accuracy.

---

### 2.7 keySet, values, entrySet

| Method | Description |
|--------|-------------|
| `Set<K> keySet()` | Set view of keys. **Weakly consistent iterator.** |
| `Collection<V> values()` | Collection view of values. **Weakly consistent iterator.** |
| `Set<Map.Entry<K, V>> entrySet()` | Set view of entries. **Weakly consistent iterator.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
Set<String> keys = map.keySet();                    // [apple, banana] (order may vary)
Collection<Integer> values = map.values();          // [10, 20]
Set<Map.Entry<String, Integer>> entries = map.entrySet();
// [apple=10, banana=20]
keys.remove("apple");                               // map = {banana=20}
```

**Output:** `keys` and `values` collections; removing from `keySet` removes from map.

**Thread-safety:** Iterators are **weakly consistent** — they reflect the state at some point during iteration and may or may not show concurrent updates.

---

### 2.8 compute, computeIfAbsent, computeIfPresent

| Method | Description |
|--------|-------------|
| `V compute(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` | Computes new value; **thread-safe.** Removes if function returns null. |
| `V computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)` | Computes value only if key is absent. **Thread-safe.** |
| `V computeIfPresent(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` | Computes value only if key is present. **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("apple", 10);

// compute: always runs function (thread-safe)
Integer computed = map.compute("apple", (k, v) -> v + 5);  // computed = 15, map = {apple=15}
Integer computed2 = map.compute("banana", (k, v) -> 20);   // computed2 = 20, map = {apple=15, banana=20}
map.compute("apple", (k, v) -> null);                      // removes apple, map = {banana=20}

// computeIfAbsent: only if absent (thread-safe)
map.put("apple", 10);
Integer absent = map.computeIfAbsent("mango", k -> 30);    // absent = 30, map = {apple=10, banana=20, mango=30}
Integer absent2 = map.computeIfAbsent("apple", k -> 50);   // absent2 = 10 (unchanged)

// computeIfPresent: only if present (thread-safe)
Integer present = map.computeIfPresent("apple", (k, v) -> v * 2); // present = 20, map = {apple=20, ...}
Integer present2 = map.computeIfPresent("berry", (k, v) -> 100);  // present2 = null (no-op)
```

**Output:** Values as commented; map changes accordingly.

**Thread-safety:** All compute methods are **atomic** — the remapping function is executed atomically for the key.

---

### 2.9 merge

| Method | Description |
|--------|-------------|
| `V merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)` | If key absent, puts value; if present, applies remappingFunction(oldValue, newValue). **Thread-safe.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("apple", 10);

// merge: if absent, use value; if present, merge (thread-safe)
Integer merged1 = map.merge("apple", 5, Integer::sum);     // merged1 = 15, map = {apple=15}
Integer merged2 = map.merge("banana", 20, Integer::sum);    // merged2 = 20 (no merge, key absent)
map.merge("apple", 10, (old, newVal) -> null);             // removes apple (function returns null)
```

**Output:** `merged1 = 15`, `merged2 = 20`; after null merge, apple is removed.

**Thread-safety:** `merge` is **atomic** — useful for concurrent counters or aggregations.

---

### 2.10 forEach (Java 8)

| Method | Description |
|--------|-------------|
| `void forEach(long parallelismThreshold, BiFunction<? super K, ? super V, ? extends U> transformer, BiConsumer<? super U, ? super K> action)` | Parallel forEach with transformer. |
| `void forEach(BiConsumer<? super K, ? super V> action)` | Performs action for each entry. **Thread-safe iteration.** |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
map.forEach((k, v) -> System.out.println(k + " -> " + v));
// apple -> 10
// banana -> 20
```

---

### 2.11 search, reduce (Java 8)

| Method | Description |
|--------|-------------|
| `U search(long parallelismThreshold, BiFunction<? super K, ? super V, ? extends U> searchFunction)` | Searches for a non-null result; returns first found. |
| `U reduce(long parallelismThreshold, BiFunction<? super K, ? super V, ? extends U> transformer, BiFunction<? super U, ? super U, ? extends U> reducer)` | Reduces entries using transformer and reducer. |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));
String found = map.search(1, (k, v) -> v > 15 ? k : null);  // "banana" or "apple"
Integer sum = map.reduce(1, (k, v) -> v, Integer::sum);      // 35
```

**Output:** `found` is a key with value > 15; `sum = 35`.

---

### 2.12 Java 21: SequencedMap methods

`ConcurrentHashMap` implements **`SequencedMap`** in Java 21. New methods:

| Method | Description |
|--------|-------------|
| `SequencedMap<K, V> reversed()` | Reversed view (insertion order not guaranteed) |
| `Map.Entry<K, V> firstEntry()` | First entry (may vary) |
| `Map.Entry<K, V> lastEntry()` | Last entry (may vary) |
| `Map.Entry<K, V> pollFirstEntry()` | Remove and return first |
| `Map.Entry<K, V> pollLastEntry()` | Remove and return last |

**Note:** `ConcurrentHashMap` does not maintain insertion order. These methods may return arbitrary entries.

---

## 3. Thread-safety and concurrent operations

### 3.1 Concurrent reads and writes

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Thread 1: writes
new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        map.put("key" + i, i);
    }
}).start();

// Thread 2: reads (non-blocking)
new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        Integer val = map.get("key" + i);  // may return null if write hasn't happened yet
    }
}).start();
```

**Key point:** Reads do not block writes, and writes do not block reads (except for the same bucket).

---

### 3.2 Atomic operations

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Atomic increment
map.compute("counter", (k, v) -> v == null ? 1 : v + 1);

// Atomic merge (useful for counters)
map.merge("count", 1, Integer::sum);  // thread-safe increment

// Atomic replace-if-equals
map.replace("key", 10, 20);  // only replaces if current value is 10
```

---

### 3.3 Concurrent updates with compute

```java
ConcurrentHashMap<String, List<String>> map = new ConcurrentHashMap<>();

// Thread-safe: computeIfAbsent + add
map.computeIfAbsent("fruits", k -> new CopyOnWriteArrayList<>()).add("apple");
map.computeIfAbsent("fruits", k -> new CopyOnWriteArrayList<>()).add("banana");
// {fruits=[apple, banana]}
```

**Note:** Use thread-safe collections (e.g., `CopyOnWriteArrayList`) as values if multiple threads modify them.

---

## 4. Transformations

### 4.1 Transform values (thread-safe)

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));

// replaceAll (in-place, thread-safe)
map.replaceAll((k, v) -> v * 2);
// map = {apple=20, banana=40}

// Stream: new map (original unchanged)
ConcurrentHashMap<String, Integer> doubled = map.entrySet().stream()
        .collect(Collectors.toConcurrentMap(Map.Entry::getKey, e -> e.getValue() * 2));
```

**Output:** `{apple=20, banana=40}`

---

### 4.2 Filter entries (thread-safe)

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));

// Keep only entries where value >= 10
ConcurrentHashMap<String, Integer> filtered = map.entrySet().stream()
        .filter(e -> e.getValue() >= 10)
        .collect(Collectors.toConcurrentMap(Map.Entry::getKey, Map.Entry::getValue));
// {apple=10, banana=20}
```

---

## 5. Insertion operations (thread-safe)

### 5.1 Basic insertion

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("apple", 10);           // {apple=10} (thread-safe)
map.put("banana", 20);          // {apple=10, banana=20}
map.put("apple", 15);           // {apple=15, banana=20} (replaced)
```

---

### 5.2 Insert only if absent (atomic)

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.putIfAbsent("apple", 10);   // {apple=10}
map.putIfAbsent("apple", 20);   // {apple=10} (unchanged, atomic)
```

---

### 5.3 Insert with computeIfAbsent (atomic)

```java
ConcurrentHashMap<String, List<String>> map = new ConcurrentHashMap<>();
map.computeIfAbsent("fruits", k -> new CopyOnWriteArrayList<>()).add("apple");
map.computeIfAbsent("fruits", k -> new CopyOnWriteArrayList<>()).add("banana");
// {fruits=[apple, banana]}
```

---

## 6. Deletion operations (thread-safe)

### 6.1 Remove by key

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
map.remove("apple");            // {banana=20} (thread-safe)
```

---

### 6.2 Remove by key-value pair (atomic)

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
map.remove("apple", 10);        // true, {banana=20} (atomic compare-and-swap)
map.remove("banana", 30);       // false (value mismatch)
```

---

### 6.3 Remove entries matching condition

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));
map.entrySet().removeIf(e -> e.getValue() < 10);
// {apple=10, banana=20}
```

---

## 7. Map to List conversions

### 7.1 Keys to List

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20));
List<String> keys = new ArrayList<>(map.keySet());
// [apple, banana] (order may vary)
```

---

### 7.2 Values to List

```java
List<Integer> values = new ArrayList<>(map.values());
// [10, 20]
```

---

### 7.3 Entries to List

```java
List<Map.Entry<String, Integer>> entries = new ArrayList<>(map.entrySet());
// [apple=10, banana=20]
```

---

### 7.4 Stream: keys to List

```java
List<String> keys = map.keySet().stream().collect(Collectors.toList());
List<String> sortedKeys = map.keySet().stream()
        .sorted()
        .collect(Collectors.toList());
```

---

## 8. List to ConcurrentHashMap conversions

### 8.1 List to ConcurrentHashMap

```java
List<String> list = List.of("apple", "banana", "mango");
ConcurrentHashMap<String, Integer> map = list.stream()
        .collect(Collectors.toConcurrentMap(Function.identity(), String::length));
// {apple=5, banana=6, mango=5}
```

---

### 8.2 List to ConcurrentHashMap with duplicate keys (merge)

```java
List<String> list = List.of("apple", "banana", "apple", "mango");
ConcurrentHashMap<String, Long> count = list.stream()
        .collect(Collectors.toConcurrentMap(Function.identity(), v -> 1L, Long::sum));
// {apple=2, banana=1, mango=1}
```

---

## 9. Java 8 Stream operations with ConcurrentHashMap

### 9.1 Parallel stream operations

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));

// Parallel stream (thread-safe)
Map<String, Integer> filtered = map.entrySet().parallelStream()
        .filter(e -> e.getValue() >= 10)
        .collect(Collectors.toConcurrentMap(Map.Entry::getKey, Map.Entry::getValue));
```

---

### 9.2 Sort by value (thread-safe)

```java
ConcurrentHashMap<String, Integer> sortedByValue = map.entrySet().stream()
        .sorted(Map.Entry.comparingByValue())
        .collect(Collectors.toConcurrentMap(Map.Entry::getKey, Map.Entry::getValue,
                (e1, e2) -> e1, ConcurrentHashMap::new));
```

---

## 10. Coding interview questions

### 10.1 Thread-safe counter

```java
ConcurrentHashMap<String, Integer> counters = new ConcurrentHashMap<>();

// Increment counter (thread-safe)
coutners.merge("count", 1, Integer::sum);

// Or using compute
coutners.compute("count", (k, v) -> v == null ? 1 : v + 1);
```

---

### 10.2 Concurrent frequency counter

```java
List<String> words = List.of("apple", "banana", "apple", "mango");
ConcurrentHashMap<String, Long> freq = words.parallelStream()
        .collect(Collectors.toConcurrentMap(Function.identity(), v -> 1L, Long::sum));
// {apple=2, banana=1, mango=1}
```

---

### 10.3 Thread-safe cache with computeIfAbsent

```java
ConcurrentHashMap<String, String> cache = new ConcurrentHashMap<>();

String getValue(String key) {
    return cache.computeIfAbsent(key, k -> expensiveOperation(k));
}
```

---

### 10.4 Concurrent map merge (sum values)

```java
ConcurrentHashMap<String, Integer> map1 = new ConcurrentHashMap<>(Map.of("a", 1, "b", 2));
ConcurrentHashMap<String, Integer> map2 = new ConcurrentHashMap<>(Map.of("b", 3, "c", 4));

map2.forEach((k, v) -> map1.merge(k, v, Integer::sum));
// map1 = {a=1, b=5, c=4}
```

---

### 10.5 Thread-safe accumulator

```java
ConcurrentHashMap<String, AtomicInteger> accumulators = new ConcurrentHashMap<>();

void increment(String key) {
    accumulators.computeIfAbsent(key, k -> new AtomicInteger(0)).incrementAndGet();
}
```

---

## 11. Differences: HashMap vs ConcurrentHashMap

| Feature | HashMap | ConcurrentHashMap |
|---------|---------|-------------------|
| **Thread-safety** | No | Yes |
| **Null keys/values** | One null key, multiple null values | No nulls (throws NPE) |
| **Read performance** | Fast | Fast (non-blocking) |
| **Write performance** | Fast | Slightly slower (locking) |
| **Iterator** | Fail-fast (throws `ConcurrentModificationException`) | Weakly consistent |
| **Size** | Accurate | May be inaccurate during concurrent updates |
| **Use case** | Single-threaded or synchronized externally | Multi-threaded without external synchronization |

---

## 12. Quick reference table

| Operation | Method / Code |
|-----------|---------------|
| Insert (thread-safe) | `map.put(key, value)` |
| Insert if absent (atomic) | `map.putIfAbsent(key, value)` |
| Get (non-blocking) | `map.get(key)` or `map.getOrDefault(key, defaultValue)` |
| Remove (thread-safe) | `map.remove(key)` or `map.remove(key, value)` |
| Replace (atomic) | `map.replace(key, value)` or `map.replace(key, oldValue, newValue)` |
| Replace all (thread-safe) | `map.replaceAll((k, v) -> newValue)` |
| Compute (atomic) | `map.compute(key, (k, v) -> newValue)` |
| Compute if absent (atomic) | `map.computeIfAbsent(key, k -> value)` |
| Merge (atomic) | `map.merge(key, value, (old, new) -> merged)` |
| Thread-safe counter | `map.merge("key", 1, Integer::sum)` |
| List → ConcurrentHashMap | `list.stream().collect(Collectors.toConcurrentMap(...))` |

---

All examples use **Java 8** streams and collectors; Java 21 **SequencedMap** methods are noted where applicable. **ConcurrentHashMap** is designed for high-concurrency scenarios where multiple threads access the map simultaneously.

