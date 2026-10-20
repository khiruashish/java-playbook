---
title: Concurrency Toolkit by Example
status: review
---

# Concurrency Toolkit by Example

The everyday building blocks of concurrent Java, one small runnable example each: threads, locks, atomics,
visibility, executors, and the coordination tools in `java.util.concurrent`.

!!! tip "Every example here is real"
    Each program below compiles and runs as shown, and the output is exactly what it printed on JDK 21.
    Copy one into a file and run it with the command shown underneath — no build tool needed.

---

## 1. Threads: start, join, and start() vs run()

`start()` runs the task on a new thread; `run()` is only a method call on the current one. `join()` waits for a thread to finish. See [Ch 24](../04-concurrency/24-threading-fundamentals.md).

```java title="C01_ThreadBasics.java"
--8<-- "code/examples/concurrency/C01_ThreadBasics.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C01_ThreadBasics.out"
```

<small>Run it: `java C01_ThreadBasics.java`</small>

---

## 2. A race condition, and synchronized

`count++` is read–add–write, so two threads can overwrite each other's update. `synchronized` makes the whole step exclusive. See [Ch 25](../04-concurrency/25-shared-state.md).

!!! note "Why there is a `Thread.yield()`"
    The output was captured on a single-core machine, where threads rarely interleave on their own.
    The `yield()` makes the switch happen exactly inside the unsafe window — which is what a real
    multi-core server does without help. Exact numbers vary from run to run; the conclusion does not.


```java title="C02_RaceAndSynchronized.java"
--8<-- "code/examples/concurrency/C02_RaceAndSynchronized.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C02_RaceAndSynchronized.out"
```

<small>Run it: `java C02_RaceAndSynchronized.java`</small>

---

## 3. Atomics: counters without locks

`AtomicInteger` for exact values such as IDs, `LongAdder` for busy metrics, and compare-and-set for state transitions. See [Ch 27](../04-concurrency/27-locks-and-atomics.md).

```java title="C03_AtomicsAndLongAdder.java"
--8<-- "code/examples/concurrency/C03_AtomicsAndLongAdder.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C03_AtomicsAndLongAdder.out"
```

<small>Run it: `java C03_AtomicsAndLongAdder.java`</small>

---

## 4. volatile: making a write visible

Without `volatile`, the worker thread may never see the flag change. `volatile` guarantees visibility — but not atomicity. See [Ch 26](../04-concurrency/26-java-memory-model.md).

```java title="C04_VolatileFlag.java"
--8<-- "code/examples/concurrency/C04_VolatileFlag.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C04_VolatileFlag.out"
```

<small>Run it: `java C04_VolatileFlag.java`</small>

---

## 5. ExecutorService and Futures

`invokeAll` runs a batch and waits; `invokeAny` returns the first success. A task's exception is kept inside its `Future` until you call `get()`. See [Ch 28](../04-concurrency/28-executors.md).

```java title="C05_ExecutorAndFutures.java"
--8<-- "code/examples/concurrency/C05_ExecutorAndFutures.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C05_ExecutorAndFutures.out"
```

<small>Run it: `java C05_ExecutorAndFutures.java`</small>

---

## 6. CountDownLatch: wait for N events

Start taking orders only after every vendor connection is ready.

```java title="C06_CountDownLatch.java"
--8<-- "code/examples/concurrency/C06_CountDownLatch.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C06_CountDownLatch.out"
```

<small>Run it: `java C06_CountDownLatch.java`</small>

---

## 7. Semaphore: cap concurrent access

Twenty tasks, but never more than three calls to a fragile API at once — the right way to limit a resource when using virtual threads.

```java title="C07_SemaphoreLimit.java"
--8<-- "code/examples/concurrency/C07_SemaphoreLimit.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C07_SemaphoreLimit.out"
```

<small>Run it: `java C07_SemaphoreLimit.java`</small>

---

## 8. ReentrantLock: give up instead of hanging

`tryLock` with a timeout lets a thread fail fast. `synchronized` can only wait forever. Always `unlock()` in `finally`.

```java title="C08_ReentrantLockTryLock.java"
--8<-- "code/examples/concurrency/C08_ReentrantLockTryLock.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C08_ReentrantLockTryLock.out"
```

<small>Run it: `java C08_ReentrantLockTryLock.java`</small>

---

## 9. BlockingQueue: producer and consumer

The queue hands orders from a producer to a consumer; a full queue makes the producer wait. A "poison pill" value tells the consumer to stop.

```java title="C09_ProducerConsumer.java"
--8<-- "code/examples/concurrency/C09_ProducerConsumer.java"
```

```text title="Output"
--8<-- "code/examples/concurrency/C09_ProducerConsumer.out"
```

<small>Run it: `java C09_ProducerConsumer.java`</small>
