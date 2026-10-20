---
title: HashMap — Deep Dive
tags: [java, collections, hashmap, internals]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: intermediate
related: [concurrent-hashmap-guide.md]
---

## Java HashMap — Design, Internals, and Usage Guide (Java 8–21)

---

## 1. Purpose & Audience

- **Purpose**: Provide a production-style guide to `HashMap` that explains:
  - **How `HashMap` works internally** (buckets, hashing, collisions, resizing).
  - **All key APIs** and how to use them from basic to advanced/enterprise scenarios.
  - **Java 8 and Java 21 features**, including stream usage and `SequencedMap` methods.
- **Audience**:
  - Java developers who use `HashMap` regularly and want a deeper understanding.
  - Engineers preparing for interviews requiring knowledge of `HashMap` internals.
  - Team members writing or reviewing production code that relies on maps.

---

## 2. Overview

- **`HashMap<K, V>`** is a hash table-based implementation of the `Map` interface.
- **Key characteristics**:
  - **Average O(1)** time for `get()` and `put()` with a good hash function and low collision rate.
  - **Not thread-safe**: concurrent structural modifications from multiple threads must be externally synchronized (or use `ConcurrentHashMap`).
  - **No duplicate keys**: inserting a duplicate key replaces the previous value.
  - **Allows nulls**: one `null` key and many `null` values.
  - **Ordering**:
    - `HashMap` does **not guarantee iteration order** (even though in practice from Java 8+ it tends to be stable for a given run).
    - For predictable insertion order, use `LinkedHashMap`.
  - **Java 21**: `HashMap` implements `SequencedMap` and exposes new sequence-related methods based on its iteration order.

---

## 3. Behavioral Guarantees & Failure Modes

- **Thread-safety**:
  - `HashMap` is **not** thread-safe.
  - Concurrent modifications without proper locking can lead to:
    - Data races and lost updates.
    - In older Java versions, even infinite loops during resize (fixed since Java 8 but still undefined behavior).
  - For multi-threaded access, prefer:
    - `ConcurrentHashMap` for high concurrency, or
    - `Collections.synchronizedMap(new HashMap<>())` for simple synchronized access.

- **Fail-fast iterators**:
  - Iterators from `keySet()`, `values()`, `entrySet()` are **fail-fast**.
  - If the map is structurally modified after iterator creation (except via iterator’s own `remove()`), the iterator may throw `ConcurrentModificationException`.

- **Null handling**:
  - `HashMap` allows:
    - One `null` key.
    - Multiple `null` values.
  - `get(null)` is valid and returns the value for the `null` key if present.

---

## 4. Internal Design (Java 8+)

### 4.1 Core structures

Internally, a `HashMap` uses:

- An array of buckets: `Node<K,V>[] table`.
- Each bucket holds:
  - A **linked list** of entries when collisions are infrequent.
  - A **red-black tree** (tree bin) when many keys hash to the same bucket (to keep lookups near O(1)).

Each `Node` holds:

- `int hash` — cached hash of the key.
- `K key` — key.
- `V value` — value.
- `Node<K,V> next` — next node in chain (for collision list or tree links).

### 4.2 Hashing and index computation

- For a key `k`:
  - Compute hash: `int h = hash(k)` (which mixes `k.hashCode()` bits for better distribution).
  - Bucket index: typically `index = (n - 1) & h`, where `n` is table length.
  - This ensures indices are in `[0, n-1]` and uses bitmasking for speed when `n` is a power of two.

### 4.3 Collision handling & treeification

- If multiple keys map to the same bucket index:
  - They are stored in a **linked list** initially.
  - When the list length exceeds a threshold (e.g. 8), and table capacity is sufficiently large, it is converted into a **red-black tree**.
  - This conversion keeps worst-case lookup complexity closer to **O(log n)** instead of deteriorating to O(n).

### 4.4 Resizing and load factor

- `HashMap` maintains:
  - A `capacity` (current table length).
  - A `loadFactor` (default 0.75).
  - A `threshold` = `capacity * loadFactor`.
- When `size` exceeds `threshold`:
  - The map resizes: capacity roughly doubles.
  - All entries are rehashed and redistributed into the new table.
- This mechanism maintains a good balance between time (collisions) and space (empty buckets).

### 4.5 Internal structure diagram (simplified)

```mermaid
flowchart TD
  clientCode["ClientCode"]
  hashMap["HashMap<K,V>"]
  table["table: Node[]"]
  bucket0["bucket0"]
  bucket1["bucket1"]
  bucketN["bucketN"]
  listBin["LinkedList bin"]
  treeBin["TreeBin (red-black tree)"]

  clientCode --> hashMap
  hashMap --> table
  table --> bucket0
  table --> bucket1
  table --> bucketN
  bucket0 --> listBin
  bucket1 --> treeBin
```

- **Explanation**:
  - `HashMap` holds an array `table`.
  - Indexing into `table` gives a bucket.
  - Each bucket stores either a linked list or a tree of nodes depending on collision density.

---

## 5. Construction & Basic Usage

### 5.1 Constructors

```java
Map<String, Integer> defaultMap = new HashMap<>();

Map<String, Integer> withCapacity = new HashMap<>(16);        // initial capacity

Map<String, Integer> withLoadFactor = new HashMap<>(16, 0.75f); // capacity, load factor
```

- **Guidelines**:
  - If you know expected size \(N\), pick an initial capacity around `N / loadFactor` to reduce resizes.
  - For typical applications, the default constructor is sufficient.

### 5.2 Basic CRUD

- **Insert / update**: `put`, `putIfAbsent`, `putAll`.
- **Read**: `get`, `getOrDefault`, `containsKey`, `containsValue`.
- **Delete**: `remove(key)`, `remove(key, value)`.
- **Replace**: `replace`, `replaceAll`.

See **Appendix A** for detailed examples of each method.

---

## 6. API Overview by Category

> The sections below summarize common operations. For **method-by-method examples and outputs**, see **Appendix A**, which embeds the full “Java HashMap — Complete Guide (Java 8, Java 21)” reference.

### 6.1 Core operations

- **Insertion**:
  - `V put(K key, V value)`
  - `V putIfAbsent(K key, V value)` (Java 8+)
  - `void putAll(Map<? extends K, ? extends V> m)`
- **Lookup**:
  - `V get(Object key)`
  - `V getOrDefault(Object key, V defaultValue)` (Java 8+)
  - `boolean containsKey(Object key)`
  - `boolean containsValue(Object value)`
- **Deletion**:
  - `V remove(Object key)`
  - `boolean remove(Object key, Object value)` (Java 8+)
- **Size & state**:
  - `int size()`
  - `boolean isEmpty()`
  - `void clear()`

### 6.2 View collections

- `Set<K> keySet()`
- `Collection<V> values()`
- `Set<Map.Entry<K, V>> entrySet()`

Properties:
- Backed by the map; changes are reflected in both directions.
- Iterators are **fail-fast**.

### 6.3 Compute & merge APIs (Java 8+)

- `V compute(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)`
- `V computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)`
- `V computeIfPresent(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)`
- `V merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)`

Usage patterns:
- Use `computeIfAbsent` to lazily create collections or expensive values.
- Use `merge` to accumulate values (e.g. counters, sums) for keys.

### 6.4 Bulk operations & Java 8 forEach

- `void forEach(BiConsumer<? super K, ? super V> action)`
- `void replaceAll(BiFunction<? super K, ? super V, ? extends V> function)`

These provide convenient in-place transformations and iteration.

### 6.5 Java 21 `SequencedMap` methods

`HashMap` implements `SequencedMap` in Java 21, but **does not guarantee insertion order** the way `LinkedHashMap` does. New methods include:

- Sequence views and entries:
  - `SequencedMap<K, V> reversed()`
  - `Map.Entry<K, V> firstEntry()`
  - `Map.Entry<K, V> lastEntry()`
  - `Map.Entry<K, V> pollFirstEntry()`
  - `Map.Entry<K, V> pollLastEntry()`
  - `V putFirst(K key, V value)`
  - `V putLast(K key, V value)`

**Recommendation**:
- For **predictable sequence behavior**, use `LinkedHashMap` as the concrete implementation when you want these methods to reflect insertion order.

---

## 7. Transformations & Conversions (Java 8+)

### 7.1 Value transformations

- **In-place**:

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
map.replaceAll((k, v) -> v * 2);
// {apple=20, banana=40}
```

- **New map via streams**:

```java
Map<String, Integer> doubled = map.entrySet().stream()
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            e -> e.getValue() * 2
        ));
```

### 7.2 Key transformations

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));

Map<String, Integer> upperKeys = map.entrySet().stream()
        .collect(Collectors.toMap(
            e -> e.getKey().toUpperCase(),
            Map.Entry::getValue
        ));
// {APPLE=10, BANANA=20}
```

### 7.3 Filtering

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));

Map<String, Integer> filtered = map.entrySet().stream()
        .filter(e -> e.getValue() >= 10)
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            Map.Entry::getValue
        ));
// {apple=10, banana=20}
```

### 7.4 Map ↔ List conversions

- **Map → List**:
  - Keys: `new ArrayList<>(map.keySet())`
  - Values: `new ArrayList<>(map.values())`
  - Entries: `new ArrayList<>(map.entrySet())`
- **List → Map**:
  - See Appendix A Section 8 for examples:
    - Element as key, index as value.
    - Element as key, transformed value.
    - Handling duplicates via merge.

---

## 8. Enterprise Usage Patterns

Although `HashMap` itself is not concurrent, it is heavily used in enterprise code for **single-threaded** contexts or where access is controlled.

### 8.1 In-memory configuration maps

**Use case**: Load configuration properties from a file or database into a `HashMap` at startup; reads are frequent, writes rare.

```java
public class ConfigService {

    private final Map<String, String> configs = new HashMap<>();

    public void load(Map<String, String> loaded) {
        configs.clear();
        configs.putAll(loaded);
    }

    public String get(String key) {
        return configs.get(key);
    }

    public String getOrDefault(String key, String defaultValue) {
        return configs.getOrDefault(key, defaultValue);
    }
}
```

- Safe in single-threaded or properly synchronized initialization flows.

### 8.2 Lookup tables and registries

**Use case**: Map a string identifier to a strategy implementation or handler.

```java
public interface PaymentProcessor {
    void process(PaymentRequest request);
}

public class PaymentProcessorRegistry {

    private final Map<String, PaymentProcessor> processors = new HashMap<>();

    public void register(String type, PaymentProcessor processor) {
        processors.put(type, processor);
    }

    public PaymentProcessor getProcessor(String type) {
        return processors.get(type);
    }
}
```

### 8.3 Aggregation and analytics (single-threaded or batched)

**Use case**: Count events, group data, or compute statistics within a single-threaded batch job.

```java
public class EventCounter {

    private final Map<String, Long> counts = new HashMap<>();

    public void increment(String key) {
        counts.merge(key, 1L, Long::sum);
    }

    public long getCount(String key) {
        return counts.getOrDefault(key, 0L);
    }
}
```

---

## 9. HashMap vs ConcurrentHashMap vs LinkedHashMap

| Aspect                     | `HashMap`                              | `ConcurrentHashMap`                        | `LinkedHashMap`                                      |
|----------------------------|----------------------------------------|-------------------------------------------|------------------------------------------------------|
| Thread-safety              | Not thread-safe                        | Thread-safe, highly concurrent            | Not thread-safe                                      |
| Null keys / values         | 1 null key, many null values           | No null keys/values                       | Same as `HashMap`                                    |
| Iteration order            | Not guaranteed                         | Not guaranteed                            | Predictable insertion or access order                |
| Iterators                  | Fail-fast                              | Weakly consistent                         | Fail-fast                                            |
| Typical use                | Single-threaded maps, basic data store | Shared concurrent maps                    | Maps where order matters (e.g., LRU, predictable UI)|

**Guidance**:
- Use **`HashMap`** in single-threaded or externally synchronized contexts.
- Use **`ConcurrentHashMap`** when many threads read/write concurrently.
- Use **`LinkedHashMap`** when you need insertion or access-order iteration (caches, ordered views).

---

## 10. Quick Reference Cheat Sheet

- **Insert / update**:
  - `map.put(k, v)`
  - `map.putIfAbsent(k, v)`
  - `map.compute(k, (k, v) -> ...)`
  - `map.computeIfAbsent(k, k2 -> ...)`
  - `map.merge(k, v, (oldV, newV) -> ...)`
- **Read**:
  - `map.get(k)`
  - `map.getOrDefault(k, defaultValue)`
  - `map.containsKey(k)`
  - `map.containsValue(v)`
- **Delete**:
  - `map.remove(k)`
  - `map.remove(k, v)`
  - `map.clear()`
- **Views & iteration**:
  - `map.keySet()`, `map.values()`, `map.entrySet()`
  - All iterators are fail-fast.
- **Transform / filter (Java 8+)**:
  - `map.replaceAll((k, v) -> ...)`
  - `map.entrySet().stream().filter(...).collect(...)`
- **Conversions**:
  - Map → List: `new ArrayList<>(map.keySet())`, `new ArrayList<>(map.values())`
  - List → Map: `list.stream().collect(Collectors.toMap(...))`

---

## Appendix A: Java HashMap — Complete Guide (Java 8, Java 21)

The following reference content provides **all HashMap methods with examples and outputs**, transformation patterns, conversions, and Java 8 / Java 21 examples.

---

## Java HashMap — Complete Guide (Java 8, Java 21)

Introduction to `HashMap`, all its methods with examples and output, transformations, Map → List conversions, insertion, deletion, replace operations, and Java 8 / Java 21 examples.

---

## Table of Contents

- [1. HashMap introduction](#1-hashmap-introduction)
- [2. All HashMap methods with examples and output](#2-all-hashmap-methods-with-examples-and-output)
  - [2.1 put, putIfAbsent, putAll](#2-1-put-putifabsent-putall)
  - [2.2 get, getOrDefault](#2-2-get-getordefault)
  - [2.3 remove](#2-3-remove)
  - [2.4 replace, replaceAll](#2-4-replace-replaceall)
  - [2.5 containsKey, containsValue](#2-5-containskey-containsvalue)
  - [2.6 size, isEmpty, clear](#2-6-size-isempty-clear)
  - [2.7 keySet, values, entrySet](#2-7-keyset-values-entryset)
  - [2.8 compute, computeIfAbsent, computeIfPresent](#2-8-compute-computeifabsent-computeifpresent)
  - [2.9 merge](#2-9-merge)
  - [2.10 forEach (Java 8)](#2-10-foreach-java-8)
  - [2.11 Java 21: SequencedMap methods](#2-11-java-21-sequencedmap-methods)
- [3. Transformations](#3-transformations)
  - [3.1 Transform values (e.g., multiply all values by 2)](#3-1-transform-values-e-g-multiply-all-values-by-2)
  - [3.2 Transform keys](#3-2-transform-keys)
  - [3.3 Filter entries](#3-3-filter-entries)
- [4. Insertion operations](#4-insertion-operations)
  - [4.1 Basic insertion](#4-1-basic-insertion)
  - [4.2 Insert only if absent](#4-2-insert-only-if-absent)
  - [4.3 Insert with computeIfAbsent](#4-3-insert-with-computeifabsent)
  - [4.4 Insert all from another map](#4-4-insert-all-from-another-map)
- [5. Deletion operations](#5-deletion-operations)
  - [5.1 Remove by key](#5-1-remove-by-key)
  - [5.2 Remove by key-value pair](#5-2-remove-by-key-value-pair)
  - [5.3 Remove entries matching condition](#5-3-remove-entries-matching-condition)
  - [5.4 Clear all](#5-4-clear-all)
- [6. Replace operations](#6-replace-operations)
  - [6.1 Replace value for key](#6-1-replace-value-for-key)
  - [6.2 Replace if value matches](#6-2-replace-if-value-matches)
  - [6.3 Replace all values](#6-3-replace-all-values)
- [7. Map to List conversions](#7-map-to-list-conversions)
  - [7.1 Keys to List](#7-1-keys-to-list)
  - [7.2 Values to List](#7-2-values-to-list)
  - [7.3 Entries to List](#7-3-entries-to-list)
  - [7.4 Stream: keys to List](#7-4-stream-keys-to-list)
  - [7.5 Stream: values to List](#7-5-stream-values-to-list)
  - [7.6 Stream: entries to List of custom objects](#7-6-stream-entries-to-list-of-custom-objects)
  - [7.7 Map to List of keys sorted by values](#7-7-map-to-list-of-keys-sorted-by-values)
- [8. List to Map conversions](#8-list-to-map-conversions)
  - [8.1 List to Map (element as key, index as value)](#8-1-list-to-map-element-as-key-index-as-value)
  - [8.2 List to Map (element as key, transformed value)](#8-2-list-to-map-element-as-key-transformed-value)
  - [8.3 List to Map with duplicate keys (merge)](#8-3-list-to-map-with-duplicate-keys-merge)
- [9. Java 8 Stream operations with Map](#9-java-8-stream-operations-with-map)
  - [9.1 Filter entries](#9-1-filter-entries)
  - [9.2 Map entries to different type](#9-2-map-entries-to-different-type)
  - [9.3 Sort by key](#9-3-sort-by-key)
  - [9.4 Sort by value](#9-4-sort-by-value)
  - [9.5 Group by value](#9-5-group-by-value)
- [10. Coding interview questions](#10-coding-interview-questions)
  - [10.1 Count frequency of characters in string](#10-1-count-frequency-of-characters-in-string)
  - [10.2 Find first non-repeated character](#10-2-find-first-non-repeated-character)
  - [10.3 Two Sum (indices)](#10-3-two-sum-indices)
  - [10.4 Group anagrams](#10-4-group-anagrams)
  - [10.5 Merge two maps (sum values for same keys)](#10-5-merge-two-maps-sum-values-for-same-keys)
  - [10.6 Find duplicate elements](#10-6-find-duplicate-elements)
  - [10.7 Sort map by value (descending)](#10-7-sort-map-by-value-descending)
  - [10.8 Invert map (swap keys and values)](#10-8-invert-map-swap-keys-and-values)
  - [10.9 Find key with maximum value](#10-9-find-key-with-maximum-value)
  - [10.10 Check if two maps are equal (ignoring order)](#10-10-check-if-two-maps-are-equal-ignoring-order)
- [11. Quick reference table](#11-quick-reference-table)

---

## 1. HashMap introduction

- **`HashMap<K, V>`** is a hash table-based implementation of the `Map` interface. It stores key-value pairs, allows one null key and multiple null values, and does not guarantee order (Java 7 and earlier) or insertion order (Java 8+).
- **Key characteristics:**
  - **O(1)** average time for `get()` and `put()` operations (assuming good hash distribution).
  - **Not thread-safe** — use `ConcurrentHashMap` or `Collections.synchronizedMap()` for multi-threaded access.
  - **No duplicate keys** — adding a duplicate key replaces the old value.
  - **Allows null** — one null key, multiple null values.

```java
Map<String, Integer> map = new HashMap<>();
Map<String, Integer> withCapacity = new HashMap<>(16);  // initial capacity
Map<String, Integer> withLoadFactor = new HashMap<>(16, 0.75f);  // capacity, load factor
```

---

## 2. All HashMap methods with examples and output

### 2.1 put, putIfAbsent, putAll

| Method | Description |
|--------|-------------|
| `V put(K key, V value)` | Associates key with value; returns previous value (or null) |
| `V putIfAbsent(K key, V value)` | Puts only if key is absent; returns existing value or null |
| `void putAll(Map<? extends K, ? extends V> m)` | Copies all mappings from m |

```java
Map<String, Integer> map = new HashMap<>();
Integer old1 = map.put("apple", 10);        // old1 = null, map = {apple=10}
Integer old2 = map.put("apple", 20);        // old2 = 10, map = {apple=20}
Integer old3 = map.putIfAbsent("banana", 30); // old3 = null, map = {apple=20, banana=30}
Integer old4 = map.putIfAbsent("apple", 25);  // old4 = 20 (unchanged), map = {apple=20, banana=30}
map.putAll(Map.of("mango", 40, "berry", 50)); // map = {apple=20, banana=30, mango=40, berry=50}
```

**Output:** `old1 = null`, `old2 = 10`, `old3 = null`, `old4 = 20`; final map: `{apple=20, banana=30, mango=40, berry=50}`

---

### 2.2 get, getOrDefault

| Method | Description |
|--------|-------------|
| `V get(Object key)` | Value for key, or null if absent |
| `V getOrDefault(Object key, V defaultValue)` | Value for key, or defaultValue if absent |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
Integer val1 = map.get("apple");              // 10
Integer val2 = map.get("mango");              // null
Integer val3 = map.getOrDefault("mango", 0);   // 0
Integer val4 = map.getOrDefault("apple", 0);   // 10
```

**Output:** `val1 = 10`, `val2 = null`, `val3 = 0`, `val4 = 10`

---

### 2.3 remove

| Method | Description |
|--------|-------------|
| `V remove(Object key)` | Removes mapping for key; returns value (or null) |
| `boolean remove(Object key, Object value)` | Removes only if key maps to value; returns true if removed |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 30));
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
| `V replace(K key, V value)` | Replaces value for key if present; returns old value (or null) |
| `boolean replace(K key, V oldValue, V newValue)` | Replaces only if key maps to oldValue; returns true if replaced |
| `void replaceAll(BiFunction<? super K, ? super V, ? extends V> function)` | Replaces each value with function(key, value) |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
Integer old1 = map.replace("apple", 15);              // old1 = 10, map = {apple=15, banana=20}
boolean replaced = map.replace("banana", 20, 25);     // replaced = true, map = {apple=15, banana=25}
boolean notReplaced = map.replace("banana", 30, 35);  // notReplaced = false
map.replaceAll((k, v) -> v * 2);                      // map = {apple=30, banana=50}
```

**Output:** `old1 = 10`, `replaced = true`, `notReplaced = false`; after replaceAll: `{apple=30, banana=50}`

---

### 2.5 containsKey, containsValue

| Method | Description |
|--------|-------------|
| `boolean containsKey(Object key)` | true if map contains key |
| `boolean containsValue(Object value)` | true if map contains value |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
boolean hasKey = map.containsKey("apple");      // true
boolean hasValue = map.containsValue(20);        // true
boolean noKey = map.containsKey("mango");       // false
boolean noValue = map.containsValue(100);       // false
```

**Output:** `hasKey = true`, `hasValue = true`, `noKey = false`, `noValue = false`

---

### 2.6 size, isEmpty, clear

| Method | Description |
|--------|-------------|
| `int size()` | Number of key-value mappings |
| `boolean isEmpty()` | true if size is 0 |
| `void clear()` | Removes all mappings |

```java
Map<String, Integer> map = new HashMap<>(Map.of("a", 1, "b", 2));
int size = map.size();          // 2
boolean empty = map.isEmpty();  // false
map.clear();                    // map = {}
boolean emptyAfter = map.isEmpty(); // true
```

**Output:** `size = 2`, `empty = false`, after clear `emptyAfter = true`

---

### 2.7 keySet, values, entrySet

| Method | Description |
|--------|-------------|
| `Set<K> keySet()` | Set view of keys (changes reflect in map) |
| `Collection<V> values()` | Collection view of values (changes reflect in map) |
| `Set<Map.Entry<K, V>> entrySet()` | Set view of entries (changes reflect in map) |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
Set<String> keys = map.keySet();                    // [apple, banana] (order may vary)
Collection<Integer> values = map.values();          // [10, 20]
Set<Map.Entry<String, Integer>> entries = map.entrySet();
// [apple=10, banana=20]
keys.remove("apple");                               // map = {banana=20}
```

**Output:** `keys` and `values` collections; removing from `keySet` removes from map.

---

### 2.8 compute, computeIfAbsent, computeIfPresent

| Method | Description |
|--------|-------------|
| `V compute(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` | Computes new value from key and current value (or null); removes if function returns null |
| `V computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)` | Computes value only if key is absent |
| `V computeIfPresent(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` | Computes value only if key is present |

```java
Map<String, Integer> map = new HashMap<>();
map.put("apple", 10);

// compute: always runs function
Integer computed = map.compute("apple", (k, v) -> v + 5);  // computed = 15, map = {apple=15}
Integer computed2 = map.compute("banana", (k, v) -> 20);   // computed2 = 20, map = {apple=15, banana=20}
map.compute("apple", (k, v) -> null);                      // removes apple, map = {banana=20}

// computeIfAbsent: only if absent
map.put("apple", 10);
Integer absent = map.computeIfAbsent("mango", k -> 30);    // absent = 30, map = {apple=10, banana=20, mango=30}
Integer absent2 = map.computeIfAbsent("apple", k -> 50);   // absent2 = 10 (unchanged)

// computeIfPresent: only if present
Integer present = map.computeIfPresent("apple", (k, v) -> v * 2); // present = 20, map = {apple=20, ...}
Integer present2 = map.computeIfPresent("berry", (k, v) -> 100);  // present2 = null (no-op)
```

**Output:** Values as commented; map changes accordingly.

---

### 2.9 merge

| Method | Description |
|--------|-------------|
| `V merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)` | If key absent, puts value; if present, applies remappingFunction(oldValue, newValue) |

```java
Map<String, Integer> map = new HashMap<>();
map.put("apple", 10);

// merge: if absent, use value; if present, merge
Integer merged1 = map.merge("apple", 5, Integer::sum);     // merged1 = 15, map = {apple=15}
Integer merged2 = map.merge("banana", 20, Integer::sum);    // merged2 = 20 (no merge, key absent)
map.merge("apple", 10, (old, newVal) -> null);             // removes apple (function returns null)
```

**Output:** `merged1 = 15`, `merged2 = 20`; after null merge, apple is removed.

---

### 2.10 forEach (Java 8)

| Method | Description |
|--------|-------------|
| `void forEach(BiConsumer<? super K, ? super V> action)` | Performs action for each entry |

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
map.forEach((k, v) -> System.out.println(k + " -> " + v));
// apple -> 10
// banana -> 20
```

---

### 2.11 Java 21: SequencedMap methods

`HashMap` implements **`SequencedMap`** in Java 21. New methods:

| Method | Description |
|--------|-------------|
| `SequencedMap<K, V> reversed()` | Reversed view |
| `Map.Entry<K, V> firstEntry()` | First entry (insertion order) |
| `Map.Entry<K, V> lastEntry()` | Last entry |
| `Map.Entry<K, V> pollFirstEntry()` | Remove and return first |
| `Map.Entry<K, V> pollLastEntry()` | Remove and return last |
| `V putFirst(K key, V value)` | Put at beginning |
| `V putLast(K key, V value)` | Put at end |

**Note:** `HashMap` does not maintain insertion order by default. Use **`LinkedHashMap`** for ordered behavior with these methods.

```java
LinkedHashMap<String, Integer> map = new LinkedHashMap<>(Map.of("a", 1, "b", 2, "c", 3));
SequencedMap<String, Integer> reversed = map.reversed();  // view: {c=3, b=2, a=1}
Map.Entry<String, Integer> first = map.firstEntry();      // a=1
Map.Entry<String, Integer> last = map.lastEntry();        // c=3
```

---

## 3. Transformations

### 3.1 Transform values (e.g., multiply all values by 2)

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));

// replaceAll (in-place)
map.replaceAll((k, v) -> v * 2);
// map = {apple=20, banana=40}

// Stream: new map (original unchanged)
Map<String, Integer> doubled = map.entrySet().stream()
        .collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue() * 2));
```

**Output:** `{apple=20, banana=40}`

---

### 3.2 Transform keys

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));

// Stream: new map with uppercase keys
Map<String, Integer> upperKeys = map.entrySet().stream()
        .collect(Collectors.toMap(e -> e.getKey().toUpperCase(), Map.Entry::getValue));
// {APPLE=10, BANANA=20}
```

---

### 3.3 Filter entries

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));

// Keep only entries where value >= 10
Map<String, Integer> filtered = map.entrySet().stream()
        .filter(e -> e.getValue() >= 10)
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
// {apple=10, banana=20}
```

---

## 4. Insertion operations

### 4.1 Basic insertion

```java
Map<String, Integer> map = new HashMap<>();
map.put("apple", 10);           // {apple=10}
map.put("banana", 20);          // {apple=10, banana=20}
map.put("apple", 15);           // {apple=15, banana=20} (replaced)
```

---

### 4.2 Insert only if absent

```java
Map<String, Integer> map = new HashMap<>();
map.putIfAbsent("apple", 10);   // {apple=10}
map.putIfAbsent("apple", 20);   // {apple=10} (unchanged)
```

---

### 4.3 Insert with computeIfAbsent

```java
Map<String, List<String>> map = new HashMap<>();
map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("apple");
map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("banana");
// {fruits=[apple, banana]}
```

---

### 4.4 Insert all from another map

```java
Map<String, Integer> map1 = new HashMap<>(Map.of("apple", 10));
Map<String, Integer> map2 = Map.of("banana", 20, "mango", 30);
map1.putAll(map2);
// map1 = {apple=10, banana=20, mango=30}
```

---

## 5. Deletion operations

### 5.1 Remove by key

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
map.remove("apple");            // {banana=20}
```

---

### 5.2 Remove by key-value pair

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
map.remove("apple", 10);        // true, {banana=20}
map.remove("banana", 30);       // false (value mismatch)
```

---

### 5.3 Remove entries matching condition

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));
map.entrySet().removeIf(e -> e.getValue() < 10);
// {apple=10, banana=20}
```

---

### 5.4 Clear all

```java
map.clear();                    // {}
```

---

## 6. Replace operations

### 6.1 Replace value for key

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10));
map.replace("apple", 20);       // {apple=20}
map.replace("banana", 30);      // no-op (key absent)
```

---

### 6.2 Replace if value matches

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10));
map.replace("apple", 10, 20);   // true, {apple=20}
map.replace("apple", 10, 30);    // false (value mismatch)
```

---

### 6.3 Replace all values

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
map.replaceAll((k, v) -> v * 2);
// {apple=20, banana=40}
```

---

## 7. Map to List conversions

### 7.1 Keys to List

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
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

### 7.5 Stream: values to List

```java
List<Integer> values = map.values().stream().collect(Collectors.toList());
List<Integer> sortedValues = map.values().stream()
        .sorted()
        .collect(Collectors.toList());
```

---

### 7.6 Stream: entries to List of custom objects

```java
List<String> keyValuePairs = map.entrySet().stream()
        .map(e -> e.getKey() + "=" + e.getValue())
        .collect(Collectors.toList());
// [apple=10, banana=20]
```

---

### 7.7 Map to List of keys sorted by values

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 30, "banana", 10, "mango", 20));
List<String> keysByValue = map.entrySet().stream()
        .sorted(Map.Entry.comparingByValue())
        .map(Map.Entry::getKey)
        .collect(Collectors.toList());
// [banana, mango, apple]
```

---

## 8. List to Map conversions

### 8.1 List to Map (element as key, index as value)

```java
List<String> list = List.of("apple", "banana", "mango");
Map<String, Integer> map = IntStream.range(0, list.size())
        .boxed()
        .collect(Collectors.toMap(list::get, i -> i));
// {apple=0, banana=1, mango=2}
```

---

### 8.2 List to Map (element as key, transformed value)

```java
List<String> list = List.of("apple", "banana", "mango");
Map<String, Integer> map = list.stream()
        .collect(Collectors.toMap(Function.identity(), String::length));
// {apple=5, banana=6, mango=5}
```

---

### 8.3 List to Map with duplicate keys (merge)

```java
List<String> list = List.of("apple", "banana", "apple", "mango");
Map<String, Long> count = list.stream()
        .collect(Collectors.toMap(Function.identity(), v -> 1L, Long::sum));
// {apple=2, banana=1, mango=1}
```

---

## 9. Java 8 Stream operations with Map

### 9.1 Filter entries

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 5));
Map<String, Integer> filtered = map.entrySet().stream()
        .filter(e -> e.getValue() >= 10)
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
```

---

### 9.2 Map entries to different type

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
Map<String, String> stringValues = map.entrySet().stream()
        .collect(Collectors.toMap(Map.Entry::getKey, e -> String.valueOf(e.getValue())));
```

---

### 9.3 Sort by key

```java
Map<String, Integer> sortedByKey = map.entrySet().stream()
        .sorted(Map.Entry.comparingByKey())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
                (e1, e2) -> e1, LinkedHashMap::new));
```

---

### 9.4 Sort by value

```java
Map<String, Integer> sortedByValue = map.entrySet().stream()
        .sorted(Map.Entry.comparingByValue())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
                (e1, e2) -> e1, LinkedHashMap::new));
```

---

### 9.5 Group by value

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20, "mango", 10));
Map<Integer, List<String>> grouped = map.entrySet().stream()
        .collect(Collectors.groupingBy(Map.Entry::getValue,
                Collectors.mapping(Map.Entry::getKey, Collectors.toList())));
// {10=[apple, mango], 20=[banana]}
```

---

## 10. Coding interview questions

### 10.1 Count frequency of characters in string

```java
String s = "hello";
Map<Character, Long> freq = s.chars()
        .mapToObj(c -> (char) c)
        .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
// {h=1, e=1, l=2, o=1}
```

---

### 10.2 Find first non-repeated character

```java
String s = "hello";
Optional<Character> first = s.chars()
        .mapToObj(c -> (char) c)
        .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))
        .entrySet().stream()
        .filter(e -> e.getValue() == 1)
        .map(Map.Entry::getKey)
        .findFirst();
// Optional['h']
```

---

### 10.3 Two Sum (indices)

```java
int[] nums = {2, 7, 11, 15};
int target = 9;
Map<Integer, Integer> map = new HashMap<>();
for (int i = 0; i < nums.length; i++) {
    int complement = target - nums[i];
    if (map.containsKey(complement)) {
        // return new int[]{map.get(complement), i};
    }
    map.put(nums[i], i);
}
```

---

### 10.4 Group anagrams

```java
List<String> words = List.of("eat", "tea", "tan", "ate", "nat", "bat");
Map<String, List<String>> anagrams = words.stream()
        .collect(Collectors.groupingBy(word -> {
            char[] chars = word.toCharArray();
            Arrays.sort(chars);
            return new String(chars);
        }));
// {aet=[eat, tea, ate], ant=[tan, nat], abt=[bat]}
```

---

### 10.5 Merge two maps (sum values for same keys)

```java
Map<String, Integer> map1 = Map.of("a", 1, "b", 2);
Map<String, Integer> map2 = Map.of("b", 3, "c", 4);
Map<String, Integer> merged = Stream.concat(map1.entrySet().stream(), map2.entrySet().stream())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, Integer::sum));
// {a=1, b=5, c=4}
```

---

### 10.6 Find duplicate elements

```java
List<String> list = List.of("a", "b", "a", "c", "b");
Set<String> duplicates = list.stream()
        .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))
        .entrySet().stream()
        .filter(e -> e.getValue() > 1)
        .map(Map.Entry::getKey)
        .collect(Collectors.toSet());
// {a, b}
```

---

### 10.7 Sort map by value (descending)

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 30, "banana", 10, "mango", 20));
Map<String, Integer> sorted = map.entrySet().stream()
        .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
                (e1, e2) -> e1, LinkedHashMap::new));
// {apple=30, mango=20, banana=10}
```

---

### 10.8 Invert map (swap keys and values)

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 10, "banana", 20));
Map<Integer, String> inverted = map.entrySet().stream()
        .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));
// {10=apple, 20=banana}
```

---

### 10.9 Find key with maximum value

```java
Map<String, Integer> map = new HashMap<>(Map.of("apple", 30, "banana", 10, "mango", 20));
Optional<String> maxKey = map.entrySet().stream()
        .max(Map.Entry.comparingByValue())
        .map(Map.Entry::getKey);
// Optional["apple"]
```

---

### 10.10 Check if two maps are equal (ignoring order)

```java
Map<String, Integer> map1 = new HashMap<>(Map.of("a", 1, "b", 2));
Map<String, Integer> map2 = new HashMap<>(Map.of("b", 2, "a", 1));
boolean equal = map1.equals(map2);  // true
```

---

## 11. Quick reference table

| Operation | Method / Code |
|-----------|---------------|
| Insert | `map.put(key, value)` |
| Insert if absent | `map.putIfAbsent(key, value)` |
| Get | `map.get(key)` or `map.getOrDefault(key, defaultValue)` |
| Remove | `map.remove(key)` or `map.remove(key, value)` |
| Replace | `map.replace(key, value)` or `map.replace(key, oldValue, newValue)` |
| Replace all | `map.replaceAll((k, v) -> newValue)` |
| Contains | `map.containsKey(key)`, `map.containsValue(value)` |
| Transform values | `map.replaceAll((k, v) -> transform(v))` or stream |
| Filter entries | `map.entrySet().stream().filter(...).collect(...)` |
| Sort by key | `entrySet().stream().sorted(Map.Entry.comparingByKey())` |
| Sort by value | `entrySet().stream().sorted(Map.Entry.comparingByValue())` |
| Map → List (keys) | `new ArrayList<>(map.keySet())` |
| Map → List (values) | `new ArrayList<>(map.values())` |
| Map → List (entries) | `new ArrayList<>(map.entrySet())` |
| List → Map | `list.stream().collect(Collectors.toMap(...))` |
| Group by value | `entrySet().stream().collect(Collectors.groupingBy(...))` |

---

All examples use **Java 8** streams and collectors; Java 21 **SequencedMap** methods are noted where applicable.

