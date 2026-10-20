---
title: CompletableFuture by Example
status: review
---

# CompletableFuture by Example

A `CompletableFuture<T>` is a value that will arrive later. Instead of blocking to wait for it, you describe
**what to do when it arrives** — transform it, combine it with another, or recover if it fails.

## Which method do I need?

| You want to… | Use | Example |
|---|---|---|
| Start work in the background | `supplyAsync` / `runAsync` | [1](#1-start-work-in-the-background) |
| Transform the result | `thenApply` | [2](#2-transform-the-result) |
| Use the result, return nothing | `thenAccept` / `thenRun` | [3](#3-consume-the-result) |
| Chain a call that returns a future | `thenCompose` | [4](#4-chain-dependent-calls) |
| Combine two independent results | `thenCombine` | [5](#5-run-two-calls-in-parallel) |
| Wait for many | `allOf` | [6](#6-wait-for-many-calls) |
| Take the fastest | `anyOf` | [7](#7-take-the-fastest-answer) |
| Recover from failure | `exceptionally` | [8](#8-recover-with-a-fallback) |
| Handle success and failure together | `handle` | [9](#9-handle-success-and-failure-in-one-place) |
| Log without changing the result | `whenComplete` | [10](#10-observe-without-changing-the-result) |
| Give up after a time limit | `orTimeout` / `completeOnTimeout` | [11](#11-timeouts) |
| Control which threads run the work | pass an `Executor` | [12](#12-choose-the-executor) |

Start at example 1 — each builds on the previous one.

!!! tip "Every example here is real"
    Each program below compiles and runs as shown, and the output is exactly what it printed on JDK 21.
    Copy one into a file and run it with the command shown underneath — no build tool needed.

---

## 1. Start work in the background

`supplyAsync` runs the task on another thread and returns immediately. `join()` waits for the result.

```java title="CF01_SupplyAsync.java"
--8<-- "code/examples/completablefuture/CF01_SupplyAsync.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF01_SupplyAsync.out"
```

<small>Run it: `java CF01_SupplyAsync.java`</small>

---

## 2. Transform the result

`thenApply` is to a future what `map` is to a stream: each step receives the previous result.

```java title="CF02_ThenApply.java"
--8<-- "code/examples/completablefuture/CF02_ThenApply.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF02_ThenApply.out"
```

<small>Run it: `java CF02_ThenApply.java`</small>

---

## 3. Consume the result

`thenAccept` uses the value and returns nothing; `thenRun` runs afterwards without seeing it.

```java title="CF03_ThenAcceptThenRun.java"
--8<-- "code/examples/completablefuture/CF03_ThenAcceptThenRun.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF03_ThenAcceptThenRun.out"
```

<small>Run it: `java CF03_ThenAcceptThenRun.java`</small>

---

## 4. Chain dependent calls

When the next step is itself asynchronous, `thenApply` nests a future inside a future. `thenCompose` flattens it — the same idea as `flatMap`.

```java title="CF04_ThenCompose.java"
--8<-- "code/examples/completablefuture/CF04_ThenCompose.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF04_ThenCompose.out"
```

<small>Run it: `java CF04_ThenCompose.java`</small>

---

## 5. Run two calls in parallel

Two independent 400 ms calls, merged with `thenCombine`, finish in about 400 ms — not 800.

```java title="CF05_ThenCombine.java"
--8<-- "code/examples/completablefuture/CF05_ThenCombine.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF05_ThenCombine.out"
```

<small>Run it: `java CF05_ThenCombine.java`</small>

---

## 6. Wait for many calls

`allOf` completes when every future has. It returns `CompletableFuture<Void>`, so read each result from its original future — `join()` no longer blocks at that point.

```java title="CF06_AllOf.java"
--8<-- "code/examples/completablefuture/CF06_AllOf.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF06_AllOf.out"
```

<small>Run it: `java CF06_AllOf.java`</small>

---

## 7. Take the fastest answer

`anyOf` completes with the first result. It returns `Object`, and it does not cancel the slower calls.

```java title="CF07_AnyOf.java"
--8<-- "code/examples/completablefuture/CF07_AnyOf.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF07_AnyOf.out"
```

<small>Run it: `java CF07_AnyOf.java`</small>

---

## 8. Recover with a fallback

`exceptionally` runs only on failure and supplies a replacement value. Notice the exception arrives **wrapped** in a `CompletionException`.

```java title="CF08_Exceptionally.java"
--8<-- "code/examples/completablefuture/CF08_Exceptionally.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF08_Exceptionally.out"
```

<small>Run it: `java CF08_Exceptionally.java`</small>

---

## 9. Handle success and failure in one place

`handle` always runs and receives both the value and the exception (one of them is `null`).

```java title="CF09_Handle.java"
--8<-- "code/examples/completablefuture/CF09_Handle.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF09_Handle.out"
```

<small>Run it: `java CF09_Handle.java`</small>

---

## 10. Observe without changing the result

`whenComplete` is for side effects like metrics. It cannot recover — the failure still reaches `join()`.

```java title="CF10_WhenComplete.java"
--8<-- "code/examples/completablefuture/CF10_WhenComplete.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF10_WhenComplete.out"
```

<small>Run it: `java CF10_WhenComplete.java`</small>

---

## 11. Timeouts

Java 9 added `orTimeout` (fail) and `completeOnTimeout` (use a default). Neither stops the underlying task.

```java title="CF11_Timeouts.java"
--8<-- "code/examples/completablefuture/CF11_Timeouts.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF11_Timeouts.out"
```

<small>Run it: `java CF11_Timeouts.java`</small>

---

## 12. Choose the executor

Without an executor, async stages use the shared `ForkJoinPool.commonPool()`. For blocking work pass your own — on Java 21, a virtual-thread executor.

!!! note "Why the output says `Thread-N`"
    The output was captured on a one-core machine. When the common pool's parallelism is below 2, `CompletableFuture` starts **a new thread per task** instead of using the pool. On a multi-core machine the first line reads `ForkJoinPool.commonPool-worker-N`.


```java title="CF12_Executors.java"
--8<-- "code/examples/completablefuture/CF12_Executors.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF12_Executors.out"
```

<small>Run it: `java CF12_Executors.java`</small>

---

## 13. Wrap a callback API

Create an incomplete future and complete it from the callback. This is how you adapt older SDKs that report results through listeners.

```java title="CF13_ManualComplete.java"
--8<-- "code/examples/completablefuture/CF13_ManualComplete.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF13_ManualComplete.out"
```

<small>Run it: `java CF13_ManualComplete.java`</small>

---

## 14. Which thread runs a stage?

A non-async stage runs on the thread that completes the future — or on **your** thread if it is already complete. The `...Async` variants always hand off to an executor. (Thread names show `Thread-N` here for the one-core reason explained in example 12.)

```java title="CF14_WhichThread.java"
--8<-- "code/examples/completablefuture/CF14_WhichThread.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF14_WhichThread.out"
```

<small>Run it: `java CF14_WhichThread.java`</small>

---

## 15. Exception wrapping

`join()` throws `CompletionException`, `get()` throws `ExecutionException`; the real exception is the **cause**. Unwrap before checking its type.

```java title="CF15_ExceptionWrapping.java"
--8<-- "code/examples/completablefuture/CF15_ExceptionWrapping.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF15_ExceptionWrapping.out"
```

<small>Run it: `java CF15_ExceptionWrapping.java`</small>

---

## 16. Putting it together

An order view built from three parallel calls. One dependency takes 3 seconds, but a timeout with a sensible fallback keeps the response at about half a second.

```java title="CF16_PuttingItTogether.java"
--8<-- "code/examples/completablefuture/CF16_PuttingItTogether.java"
```

```text title="Output"
--8<-- "code/examples/completablefuture/CF16_PuttingItTogether.out"
```

<small>Run it: `java CF16_PuttingItTogether.java`</small>

---

!!! abstract "Remember"
    `thenApply` = map · `thenCompose` = flatMap · `thenCombine` = zip · `allOf` returns `Void`
    · exceptions arrive **wrapped** · pass an **executor** for blocking work · timeouts don't stop the task
    · on Java 21+, plain blocking code on **virtual threads** is often simpler ([Ch 31](../04-concurrency/31-virtual-threads.md))

For the full treatment — threading rules, cancellation, when to prefer virtual threads — see [Chapter 29](../04-concurrency/29-completable-future.md).
