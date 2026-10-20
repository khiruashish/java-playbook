---
title: Custom ArrayList Implementation
tags: [java, collections, internals, data-structures]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: senior
related: [list-guide.md]
---

## CustomArrayList — Design, Implementation, and Comparison with ArrayList

---

## 1. Purpose & Audience

- **Purpose**: Explain and demonstrate a custom dynamic array implementation `CustomArrayList<E>` in Java, including:
  - **Internal design** (backing array, resizing, indexing).
  - **Operation behavior and complexity**.
  - **Key differences vs `java.util.ArrayList`**.
- **Audience**:
  - Developers learning how `ArrayList` works under the hood.
  - Engineers preparing for interviews that require implementing an `ArrayList`-like structure.
  - Readers needing a concise reference contrasting a minimal custom list and the JDK `ArrayList`.

---

## 2. Overview

- **`CustomArrayList<E>`** is a simple, resizable array-backed list implementation.
- It uses:
  - An internal **`Object[]`** array to store elements.
  - An **`int size`** field to track how many elements are currently in use.
  - A **growth strategy** to expand capacity when new elements are appended or inserted.
- Goals:
  - Emphasize **clarity and learning** over feature completeness.
  - Implement only a **core subset** of `ArrayList` functionality (no fail-fast iterators, no `subList`, etc.).

---

## 3. High-Level Design

### 3.1 Internal data structure

- Fields:
  - `Object[] elementData` — backing array containing elements.
  - `int size` — number of elements in the list.
- Invariants:
  - `0 <= size <= elementData.length`.
  - Valid elements occupy indices `[0, size)`.
  - Indices `[size, elementData.length)` are considered free.

### 3.2 Growth strategy

- When `size == elementData.length` and a new element is added:
  - Allocate a new array with **larger capacity**.
  - Copy all existing elements into the new array.
  - Point `elementData` to the new array.
- A common strategy:
  - **1.5x growth**: `newCapacity = oldCapacity + (oldCapacity >> 1)`.
  - Or **2x growth**: `newCapacity = oldCapacity * 2`.
- This guide uses a clear, simple **1.5x growth** strategy and ensures capacity is at least the requested `minCapacity`.

### 3.3 Indexing and bounds checking

- Valid index ranges:
  - For **access/update** (`get`, `set`, `remove`): `0 <= index < size`.
  - For **insertion** (`add(int index, E element)`): `0 <= index <= size`.
- Invalid indices result in:
  - `IndexOutOfBoundsException` with a descriptive message.

### 3.4 Null handling

- `CustomArrayList` allows **`null` elements**, mirroring `ArrayList`.
- Distinguish “no element” from “`null` element” using `size` and indices, not by `null` checks alone.

---

## 4. CustomArrayList Implementation (Java)

Below is a complete, minimal implementation of `CustomArrayList<E>` focusing on core behavior:

```java
public class CustomArrayList<E> {

    private static final int DEFAULT_CAPACITY = 10;

    private Object[] elementData;
    private int size;

    public CustomArrayList() {
        this.elementData = new Object[DEFAULT_CAPACITY];
        this.size = 0;
    }

    public CustomArrayList(int initialCapacity) {
        if (initialCapacity < 0) {
            throw new IllegalArgumentException("Illegal capacity: " + initialCapacity);
        }
        this.elementData = new Object[initialCapacity];
        this.size = 0;
    }

    public int size() {
        return size;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public E get(int index) {
        rangeCheck(index);
        @SuppressWarnings("unchecked")
        E element = (E) elementData[index];
        return element;
    }

    public E set(int index, E element) {
        rangeCheck(index);
        @SuppressWarnings("unchecked")
        E oldValue = (E) elementData[index];
        elementData[index] = element;
        return oldValue;
    }

    public void add(E element) {
        ensureCapacity(size + 1);
        elementData[size++] = element;
    }

    public void add(int index, E element) {
        rangeCheckForAdd(index);
        ensureCapacity(size + 1);
        System.arraycopy(elementData, index, elementData, index + 1, size - index);
        elementData[index] = element;
        size++;
    }

    public E remove(int index) {
        rangeCheck(index);
        @SuppressWarnings("unchecked")
        E oldValue = (E) elementData[index];

        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(elementData, index + 1, elementData, index, numMoved);
        }
        elementData[--size] = null; // clear to let GC work
        return oldValue;
    }

    public boolean remove(Object o) {
        if (o == null) {
            for (int i = 0; i < size; i++) {
                if (elementData[i] == null) {
                    fastRemove(i);
                    return true;
                }
            }
        } else {
            for (int i = 0; i < size; i++) {
                if (o.equals(elementData[i])) {
                    fastRemove(i);
                    return true;
                }
            }
        }
        return false;
    }

    public void clear() {
        for (int i = 0; i < size; i++) {
            elementData[i] = null;
        }
        size = 0;
    }

    public boolean contains(Object o) {
        return indexOf(o) >= 0;
    }

    public int indexOf(Object o) {
        if (o == null) {
            for (int i = 0; i < size; i++) {
                if (elementData[i] == null) {
                    return i;
                }
            }
        } else {
            for (int i = 0; i < size; i++) {
                if (o.equals(elementData[i])) {
                    return i;
                }
            }
        }
        return -1;
    }

    public Object[] toArray() {
        Object[] result = new Object[size];
        System.arraycopy(elementData, 0, result, 0, size);
        return result;
    }

    private void ensureCapacity(int minCapacity) {
        if (elementData.length < minCapacity) {
            grow(minCapacity);
        }
    }

    private void grow(int minCapacity) {
        int oldCapacity = elementData.length;
        int newCapacity = oldCapacity + (oldCapacity >> 1); // 1.5x growth
        if (newCapacity < minCapacity) {
            newCapacity = minCapacity;
        }
        if (newCapacity == 0) {
            newCapacity = DEFAULT_CAPACITY;
        }

        Object[] newArray = new Object[newCapacity];
        System.arraycopy(elementData, 0, newArray, 0, size);
        elementData = newArray;
    }

    private void rangeCheck(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }

    private void rangeCheckForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }

    private void fastRemove(int index) {
        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(elementData, index + 1, elementData, index, numMoved);
        }
        elementData[--size] = null;
    }
}
```

**Notes**:

- This implementation is **not synchronized**; treat it as you would `ArrayList` in terms of thread safety.
- `@SuppressWarnings("unchecked")` is used where `Object` is cast back to `E`.

---

## 5. Operation Complexity & Behavior

### 5.1 Time complexity

- `get(int index)` → **O(1)**.
- `set(int index, E element)` → **O(1)**.
- `add(E element)` (append) → **Amortized O(1)**.
- `add(int index, E element)` (insert) → **O(n)** (shifts elements after index).
- `remove(int index)` → **O(n)** (shifts trailing elements).
- `contains(Object o)`, `indexOf(Object o)` → **O(n)**.

### 5.2 Space behavior

- Backing array capacity can be **greater than `size`**.
- The implementation **does not shrink** automatically when elements are removed.

### 5.3 Error behavior

- Invalid indices for `get`, `set`, or `remove` throw `IndexOutOfBoundsException`.
- Invalid indices for `add(index, element)` (index < 0 or > size) also throw `IndexOutOfBoundsException`.

---

## 6. Differences vs `java.util.ArrayList`

### 6.1 Feature comparison

| Aspect / Feature                 | `CustomArrayList<E>`                      | `java.util.ArrayList<E>`                           |
|----------------------------------|-------------------------------------------|----------------------------------------------------|
| Backing structure                | `Object[]` + `int size`                   | `Object[]` + `int size`                            |
| Growth strategy                  | Simple 1.5x, no shrink                    | Tuned growth, may shrink via `trimToSize()`        |
| Random access                    | O(1)                                      | O(1)                                               |
| Append `add(E)`                  | Amortized O(1)                            | Amortized O(1)                                     |
| Insert/remove by index           | O(n)                                      | O(n)                                               |
| Null elements                    | Allowed                                   | Allowed                                            |
| Thread-safety                    | Not thread-safe                           | Not thread-safe                                    |
| Implements `List<E>`             | No                                        | Yes                                                |
| Fail-fast iterator (`modCount`)  | No                                        | Yes                                                |
| `subList`, `ensureCapacity`, etc.| Not implemented                           | Implemented                                         |
| `RandomAccess` marker            | No                                        | Yes                                                |
| Serialization                    | No                                        | Yes                                                |

### 6.2 Design intent

- **CustomArrayList**:
  - Designed for **clarity, education, and demonstration**.
  - Helps show how dynamic arrays behave internally.
- **ArrayList (JDK)**:
  - Optimized, feature-complete, widely tested.
  - Should be the default choice for production code.

---

## 7. Usage Examples

### 7.1 Basic usage

```java
public class CustomArrayListDemo {
    public static void main(String[] args) {
        CustomArrayList<String> list = new CustomArrayList<>();

        list.add("apple");
        list.add("banana");
        list.add("cherry");

        System.out.println("Size: " + list.size());      // Size: 3
        System.out.println("First: " + list.get(0));     // First: apple

        list.set(1, "blueberry");
        System.out.println("Index 1: " + list.get(1));   // Index 1: blueberry

        list.add(1, "banana");
        // List now: [apple, banana, blueberry, cherry]

        list.remove(2);
        // List now: [apple, banana, cherry]

        for (int i = 0; i < list.size(); i++) {
            System.out.println("Element " + i + ": " + list.get(i));
        }
    }
}
```

### 7.2 Comparing with `ArrayList`

```java
import java.util.ArrayList;

public class ListComparison {
    public static void main(String[] args) {
        CustomArrayList<Integer> custom = new CustomArrayList<>();
        ArrayList<Integer> jdk = new ArrayList<>();

        for (int i = 0; i < 5; i++) {
            custom.add(i);
            jdk.add(i);
        }

        System.out.println("CustomArrayList size: " + custom.size()); // 5
        System.out.println("ArrayList size: " + jdk.size());          // 5

        System.out.println("Custom index 2: " + custom.get(2)); // 2
        System.out.println("ArrayList index 2: " + jdk.get(2)); // 2
    }
}
```

### 7.3 Demonstrating resizing

```java
public class ResizingDemo {
    public static void main(String[] args) {
        CustomArrayList<Integer> list = new CustomArrayList<>(2);

        for (int i = 0; i < 10; i++) {
            list.add(i);
            System.out.println("Added " + i + ", size=" + list.size());
        }
    }
}
```

In this example:
- Start with a small initial capacity.
- Observe how the list grows as elements are appended.

---

## 8. When to Use CustomArrayList vs ArrayList

- **Use `CustomArrayList` when**:
  - You are **learning or teaching** data structure internals.
  - You need a **simple, self-contained example** for interviews or documentation.
  - You want to experiment with different growth strategies or constraints.

- **Use `ArrayList` when**:
  - You are writing **production-grade Java code**.
  - You rely on standard `List<E>` APIs and ecosystem integration.
  - You want robust behavior, optimizations, and long-term maintenance support.

---

## 9. Quick Reference Cheat Sheet

- **Fields**:
  - `Object[] elementData` — storage array.
  - `int size` — number of stored elements.
- **Core methods**:
  - `int size()`, `boolean isEmpty()`
  - `E get(int index)`, `E set(int index, E element)`
  - `void add(E element)`, `void add(int index, E element)`
  - `E remove(int index)`, `boolean remove(Object o)`
  - `void clear()`, `boolean contains(Object o)`, `int indexOf(Object o)`
  - `Object[] toArray()`
- **Complexity**:
  - Random access: **O(1)**.
  - Append add: amortized **O(1)**.
  - Insert/remove at index: **O(n)**.
  - Search/contains/indexOf: **O(n)**.

This document plus the `CustomArrayList<E>` implementation above form a complete, clean Markdown/Confluence-style reference for understanding and explaining custom dynamic arrays in Java and how they relate to `java.util.ArrayList`.

