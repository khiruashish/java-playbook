---
title: Appendix C — Concurrency Interview Bank
status: review
---

# Appendix C — Concurrency Interview Bank

!!! note "Generated"
    120 questions harvested from 10 chapters by `tools/build-interview-bank.py`. Edit the chapters, not this page.

!!! tip "Use it as a self-test"
    Answer each question aloud before expanding the answer. If your answer is missing the mechanism — *why*, not just *what* — reread the chapter's Internals section.

## Most frequently asked

The 20 questions marked high-frequency across these chapters. Start here.

**What is the difference between `start()` and `run()`?** ⭐  
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    `start()` asks the JVM to create a new thread of execution, which then invokes `run()`. Calling `run()` directly is just an ordinary method call on the current thread, so nothing runs concurrently. The code compiles and executes either way, which is what makes the mistake easy to miss.

**How do you stop a running thread?** ⭐  
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    You ask it to stop and it cooperates — there is no safe way to force it. Call `interrupt()`, which sets a flag and causes blocking methods like `sleep`, `join`, and `take` to throw `InterruptedException`. The thread's own code must check `isInterrupted()` in its loops and treat the exception as a cancellation request. `Thread.stop()` existed for this and throws `UnsupportedOperationException` on modern JDKs because it released locks mid-update.

**What is a race condition?** ⭐  
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    It is when the result depends on the timing of thread interleaving rather than on the program's logic. The classic case is `count++`, which is really three operations — read, add, write — so two threads can read the same value and one increment is lost. The defining symptom is that the code is correct in isolation and wrong only under concurrency.

**Is `volatile int count; count++;` thread-safe?** ⭐  
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    No. `volatile` guarantees that each read sees the latest write and that the write is visible immediately, but `count++` is read, increment, write — three separate accesses. Two threads can read the same value and both write back the same result, losing an increment. Use `AtomicInteger.incrementAndGet()`, or `LongAdder` if writes are heavily contended.

**What is the Java Memory Model?** ⭐  
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    The specification of what values a read may return when multiple threads access shared memory. It does not describe hardware; it defines an abstract contract built on the happens-before relation, and the JVM implements that contract on each platform by inserting memory barriers where the hardware is weaker than the contract requires.

**Why can a thread see `ready == true` but `value == 0`?** ⭐  
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Because without synchronisation the two writes have no ordering visible to another thread. The compiler may reorder them, the CPU's store buffer may drain them out of order, and the reading core's cache may update one before the other — all legal. Making `ready` volatile fixes it: the earlier plain write to `value` happens-before the volatile write by program order, which happens-before the volatile read that sees it, so by transitivity the reader must see 42.

**What is the difference between `synchronized` and `ReentrantLock`?** ⭐  
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Both provide mutual exclusion and are reentrant. `ReentrantLock` adds timed acquisition with `tryLock`, interruptible waiting, optional fairness, and multiple condition variables. The cost is that you must release it yourself, in a `finally` block, whereas `synchronized` is released automatically on any exit. Default to `synchronized` and switch only when you need one of those features.

**Why must `unlock()` be in a `finally` block?** ⭐  
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Because nothing else releases a `ReentrantLock`. If an exception is thrown between `lock()` and `unlock()`, the lock stays held permanently and every other thread waiting on it blocks forever. `synchronized` does not have this problem — the JVM releases the monitor on any exit — which is one reason it should remain the default.

**Why use a thread pool instead of creating threads?** ⭐  
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Creating a platform thread is expensive — an OS thread, a megabyte of reserved stack, and noticeable latency — so reusing a fixed set amortises that cost. A pool also bounds concurrency, preventing an unbounded number of threads under load, and gives a single point to shut everything down. On Java 21+ the cost argument no longer applies to virtual threads, which should not be pooled.

**What is wrong with `Executors.newFixedThreadPool`?** ⭐  
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    It is backed by an unbounded `LinkedBlockingQueue`. When producers submit faster than the fixed number of workers can process, the queue grows without limit until the heap is exhausted — a load spike becomes an `OutOfMemoryError`. For a production service, construct a `ThreadPoolExecutor` directly with a bounded queue and an explicit rejection policy.

**What is the difference between `Future` and `CompletableFuture`?** ⭐  
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `Future` can only be waited on with `get()`, which blocks. `CompletableFuture` can be composed without blocking — transformed with `thenApply`, chained with `thenCompose`, combined with `thenCombine`, and recovered with `exceptionally` — and it can be completed manually, which makes it usable for adapting callback-based APIs.

**What executor does `supplyAsync` use by default, and why does it matter?** ⭐  
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `ForkJoinPool.commonPool()`, which is shared by the whole JVM — including parallel streams — and sized at roughly one thread per core. Blocking I/O there occupies one of a handful of workers, and enough concurrent calls exhaust the pool and stall unrelated code elsewhere in the process. Always pass an explicit executor for anything that blocks; on Java 21+ a virtual-thread executor is the natural choice.

**Why use `ConcurrentHashMap` instead of `HashMap`?** ⭐  
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    `HashMap` is not thread-safe: concurrent writes lose updates and can corrupt its internal state. `ConcurrentHashMap` makes every individual operation atomic while allowing many threads to write different parts of the map simultaneously. It does this without a global lock, so it scales with the number of threads rather than serialising them.

**Is this code thread-safe: `if (!map.containsKey(k)) map.put(k, v);`?** ⭐  
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    No. Both calls are individually atomic, but the sequence is not — two threads can both see the key absent and both write, and one write is silently lost. The correct form is a single atomic call, `map.putIfAbsent(k, v)`, whose return value tells you whether you won the race.

**What is a virtual thread?** ⭐  
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    A thread managed by the JVM rather than the operating system, scheduled onto a small pool of platform threads called carriers. Because its stack lives on the heap and grows on demand, creating one costs almost nothing and millions can exist at once. From the code's perspective it is an ordinary `Thread` — the same API, the same blocking calls.

**Why should you not pool virtual threads?** ⭐  
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Pooling exists because platform threads are expensive to create and limited in number, neither of which is true of virtual threads. A fixed pool of virtual threads caps concurrency exactly as before and adds a queue, giving back the scalability you adopted them for. If you need to limit concurrency against a downstream service, use a `Semaphore`, which expresses the real constraint.

**What is structured concurrency?** ⭐  
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    A model in which concurrent subtasks have a lifetime bounded by a lexical block, so they cannot outlive the code that started them. Forking happens inside a scope, the scope cannot be exited until every subtask completes or is cancelled, and a failure in one can cancel its siblings. The effect is that concurrent code has the same structure as sequential code.

**What happens when one subtask fails?** ⭐  
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    It depends on the policy. With `allSuccessfulOrThrow`, the scope shuts down: the remaining subtasks are interrupted, nested scopes are cancelled transitively, and `join()` throws with the original failure as the cause. With `awaitAll`, nothing is cancelled and you inspect each subtask's state yourself. Choosing the policy at the scope is the point — it is no longer scattered across `Future.get` calls.

**What is a `ThreadLocal`?** ⭐  
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    A variable whose value is separate per thread, stored in a map held by the `Thread` object itself. It is used for ambient context — a trace identifier, a user principal — that would otherwise have to be threaded through every method signature. Each thread reads and writes its own value with no synchronisation needed.

**Why is `ScopedValue` better than `ThreadLocal` for request context?** ⭐  
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Because the lifetime is bounded by the block rather than by someone remembering to call `remove()`, so context cannot leak into the next request on a pooled thread. The binding is immutable, so callee code cannot change what the caller established. And reads of an unbound value throw at the read site rather than returning null and failing somewhere unrelated.

---

## L1 — Foundations

30 questions.

### Threading Fundamentals

**What is the difference between `start()` and `run()`?** ⭐  
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    `start()` asks the JVM to create a new thread of execution, which then invokes `run()`. Calling `run()` directly is just an ordinary method call on the current thread, so nothing runs concurrently. The code compiles and executes either way, which is what makes the mistake easy to miss.

**What is the difference between a process and a thread?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    A process has its own memory space; the JVM is one process. Threads live inside a process and share its heap, while each keeps a private stack for local variables and call frames. Sharing the heap makes communication between threads cheap and makes unsynchronised access dangerous.

**What is a daemon thread?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    One that does not keep the JVM alive: once only daemon threads remain, the JVM exits and kills them abruptly, skipping `finally` blocks. They suit disposable background work like cache eviction or metrics sampling. Anything that writes data must be a user thread with an orderly shutdown.

### Shared State & Synchronization

**What is a race condition?** ⭐  
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    It is when the result depends on the timing of thread interleaving rather than on the program's logic. The classic case is `count++`, which is really three operations — read, add, write — so two threads can read the same value and one increment is lost. The defining symptom is that the code is correct in isolation and wrong only under concurrency.

**What does `synchronized` guarantee?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    Two things: only one thread executes the guarded region per monitor, and everything a thread did before releasing the monitor is visible to the next thread that acquires it. That second guarantee is why synchronising only writes is a bug — readers need the lock too, or they may see stale values.

**What is the difference between `synchronized` and `volatile`?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    `synchronized` provides mutual exclusion plus visibility and can protect a multi-step operation. `volatile` provides visibility and ordering for a single field but no exclusion, so it cannot make a read-modify-write safe. Use `volatile` for a flag written by one thread; use `synchronized` or an atomic when the new value depends on the old.

### The Java Memory Model

**What is the Java Memory Model?** ⭐  
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    The specification of what values a read may return when multiple threads access shared memory. It does not describe hardware; it defines an abstract contract built on the happens-before relation, and the JVM implements that contract on each platform by inserting memory barriers where the hardware is weaker than the contract requires.

**What is happens-before?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    A partial ordering between actions: if X happens-before Y, then X's effects are visible to Y and X is ordered before it. It is established by rules — program order within a thread, unlock before lock of the same monitor, a volatile write before a later read of it, thread start and join — and it is transitive, so individual rules chain into a path from a write to a read.

**What is a data race?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Two accesses to the same variable from different threads, at least one a write, with no happens-before ordering between them. A program with no data races is guaranteed to behave as if sequentially consistent, which is the model most developers assume without realising it depends on correct synchronisation.

### Locks, Atomics & java.util.concurrent

**What is the difference between `synchronized` and `ReentrantLock`?** ⭐  
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Both provide mutual exclusion and are reentrant. `ReentrantLock` adds timed acquisition with `tryLock`, interruptible waiting, optional fairness, and multiple condition variables. The cost is that you must release it yourself, in a `finally` block, whereas `synchronized` is released automatically on any exit. Default to `synchronized` and switch only when you need one of those features.

**What is an atomic variable?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    A variable whose updates are performed atomically without a lock, using a hardware compare-and-swap instruction. `AtomicInteger.incrementAndGet()` is safe across threads where `count++` is not. Atomics protect a single variable; coordinating several requires a lock.

**What is a `CountDownLatch`?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    A one-shot synchroniser initialised with a count. Threads call `countDown()` as events occur and other threads call `await()` to block until the count reaches zero. It cannot be reset — for repeated coordination use `CyclicBarrier` or `Phaser`.

### Executors & Thread Pool Design

**Why use a thread pool instead of creating threads?** ⭐  
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Creating a platform thread is expensive — an OS thread, a megabyte of reserved stack, and noticeable latency — so reusing a fixed set amortises that cost. A pool also bounds concurrency, preventing an unbounded number of threads under load, and gives a single point to shut everything down. On Java 21+ the cost argument no longer applies to virtual threads, which should not be pooled.

**What is the difference between `execute` and `submit`?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    `execute` takes a `Runnable` and returns nothing; an exception propagates to the thread's uncaught-exception handler and is at least logged. `submit` returns a `Future` and captures any exception inside it, so the failure is invisible unless someone calls `get()`. Discarding the `Future` from `submit` is a common way to lose errors silently.

**What does `shutdown()` do versus `shutdownNow()`?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    `shutdown` stops accepting new tasks but lets queued and running ones finish. `shutdownNow` additionally interrupts running tasks and returns the queued ones without running them. Interruption is cooperative, so `shutdownNow` only stops tasks that respond to it.

### CompletableFuture

**What is the difference between `Future` and `CompletableFuture`?** ⭐  
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `Future` can only be waited on with `get()`, which blocks. `CompletableFuture` can be composed without blocking — transformed with `thenApply`, chained with `thenCompose`, combined with `thenCombine`, and recovered with `exceptionally` — and it can be completed manually, which makes it usable for adapting callback-based APIs.

**What is the difference between `thenApply` and `thenCompose`?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `thenApply` transforms the value with a function returning a plain value. `thenCompose` takes a function that itself returns a `CompletableFuture` and flattens the result, so you get `CompletableFuture<T>` rather than `CompletableFuture<CompletableFuture<T>>`. It is the same distinction as `map` versus `flatMap`.

**What does `allOf` return?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `CompletableFuture<Void>`, which completes when all its inputs complete but carries none of their values. You read the values from the original futures inside the continuation, where calling `join()` does not block because `allOf` guarantees they are already complete.

### ConcurrentHashMap & Concurrent Collections

**Why use `ConcurrentHashMap` instead of `HashMap`?** ⭐  
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    `HashMap` is not thread-safe: concurrent writes lose updates and can corrupt its internal state. `ConcurrentHashMap` makes every individual operation atomic while allowing many threads to write different parts of the map simultaneously. It does this without a global lock, so it scales with the number of threads rather than serialising them.

**Why does `ConcurrentHashMap` reject null keys and values?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    Because `get` returning null would be ambiguous — absent, or mapped to null — and in a concurrent map you cannot disambiguate it. In a `HashMap` you would follow up with `containsKey`, but between the two calls another thread could change the mapping, so the answer would never be reliable. Forbidding nulls removes the ambiguity entirely.

**What is the difference between `ConcurrentHashMap` and `Collections.synchronizedMap`?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    `synchronizedMap` wraps a map and guards every method with one global lock, so only one thread operates on it at a time and iteration still needs external synchronisation. `ConcurrentHashMap` locks individual bins, leaves reads lock-free, and provides atomic compound methods like `putIfAbsent` and `merge`. Throughput under concurrency is not comparable.

### Virtual Threads

**What is a virtual thread?** ⭐  
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    A thread managed by the JVM rather than the operating system, scheduled onto a small pool of platform threads called carriers. Because its stack lives on the heap and grows on demand, creating one costs almost nothing and millions can exist at once. From the code's perspective it is an ordinary `Thread` — the same API, the same blocking calls.

**Do virtual threads make code faster?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Not per task — a single request takes exactly as long. They increase how many tasks can be in flight simultaneously, so they improve throughput for I/O-bound work rather than latency. For CPU-bound work they give no benefit at all, since the limit is cores.

**How do you create one?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    `Thread.ofVirtual().start(task)` for a single thread, or `Executors.newVirtualThreadPerTaskExecutor()` for fan-out, used in a try-with-resources so `close()` waits for the submitted tasks. The executor is not a pool: it creates one virtual thread per task and discards it afterwards.

### Structured Concurrency

**What is structured concurrency?** ⭐  
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    A model in which concurrent subtasks have a lifetime bounded by a lexical block, so they cannot outlive the code that started them. Forking happens inside a scope, the scope cannot be exited until every subtask completes or is cancelled, and a failure in one can cancel its siblings. The effect is that concurrent code has the same structure as sequential code.

**What problem does it solve that `ExecutorService` does not?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    `ExecutorService` has no relationship between the tasks it runs, so nothing cancels siblings when one fails, nothing prevents a task outliving the method that submitted it, and nothing records that several threads belong to one operation. Structured concurrency makes that relationship explicit and enforces it, which removes an entire category of leaks and wasted work.

**What runs the subtasks?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    Virtual threads, by default. That is what makes the model practical — forking a hundred subtasks costs a hundred small heap allocations rather than a hundred OS threads. The two features were designed together and are most useful together.

### ThreadLocal → ScopedValue

**What is a `ThreadLocal`?** ⭐  
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    A variable whose value is separate per thread, stored in a map held by the `Thread` object itself. It is used for ambient context — a trace identifier, a user principal — that would otherwise have to be threaded through every method signature. Each thread reads and writes its own value with no synchronisation needed.

**Why does `ThreadLocal` leak memory?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    The per-thread map holds weak references to the `ThreadLocal` keys but strong references to the values. When the key is collected, the value remains until the map happens to clean stale entries during a later operation, so on a pooled thread that sees no further activity the value is retained for the thread's lifetime. Calling `remove()` in a `finally` block is the fix, and forgetting it is the common bug.

**What is a `ScopedValue`?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    An immutable value bound for the duration of a block: `ScopedValue.where(KEY, value).run(() -> ...)`. Anything the block calls can read it, and the binding disappears automatically when the block exits, including on exceptions. There is no `set` and no `remove` — the lifetime is the code structure.

---

## L2 — Professional

30 questions.

### Threading Fundamentals

**How do you stop a running thread?** ⭐  
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    You ask it to stop and it cooperates — there is no safe way to force it. Call `interrupt()`, which sets a flag and causes blocking methods like `sleep`, `join`, and `take` to throw `InterruptedException`. The thread's own code must check `isInterrupted()` in its loops and treat the exception as a cancellation request. `Thread.stop()` existed for this and throws `UnsupportedOperationException` on modern JDKs because it released locks mid-update.

**What should you do when you catch `InterruptedException`?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    Prefer to let it propagate so the caller can decide. If the method signature cannot throw it, restore the flag with `Thread.currentThread().interrupt()` and stop doing work. Swallowing it is a real bug: the throwing method clears the interrupt flag, so ignoring the exception erases the cancellation signal for every caller above you.

**Does `Thread.sleep()` release the lock?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    No. `sleep` pauses the thread while holding every monitor it owns, so anyone waiting on those monitors waits for the full duration. `Object.wait()` is the method that releases the monitor and reacquires it on wake. Confusing the two produces stalls that look like deadlock in a thread dump.

### Shared State & Synchronization

**Is `volatile int count; count++;` thread-safe?** ⭐  
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    No. `volatile` guarantees that each read sees the latest write and that the write is visible immediately, but `count++` is read, increment, write — three separate accesses. Two threads can read the same value and both write back the same result, losing an increment. Use `AtomicInteger.incrementAndGet()`, or `LongAdder` if writes are heavily contended.

**Why must `wait()` be called inside a `while` loop?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    Because a thread can wake without a matching `notify` — the specification explicitly permits spurious wakeups — and because another thread may consume the condition between the notify and this thread reacquiring the monitor. Re-checking in a loop makes the code correct under both. An `if` produces failures that appear rarely and only under load.

**Why is locking on `this` considered poor practice?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    It makes your lock part of your public API: any caller holding a reference to the object can synchronise on it, block your methods, or deadlock against your internals, and you have no way to prevent it. A `private final Object lock` cannot be acquired from outside, so the locking policy stays under the class's control.

### The Java Memory Model

**Why can a thread see `ready == true` but `value == 0`?** ⭐  
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Because without synchronisation the two writes have no ordering visible to another thread. The compiler may reorder them, the CPU's store buffer may drain them out of order, and the reading core's cache may update one before the other — all legal. Making `ready` volatile fixes it: the earlier plain write to `value` happens-before the volatile write by program order, which happens-before the volatile read that sees it, so by transitivity the reader must see 42.

**What does safe publication mean?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Making an object's reference and its fully-constructed state visible to other threads together. The standard idioms are a static initialiser, a `volatile` or `AtomicReference` field, a `final` field of a properly constructed object, a field guarded by a lock, or a handoff through a `java.util.concurrent` structure. Publishing through a plain field risks another thread seeing a non-null reference to an object whose fields are still defaults.

**Why does double-checked locking require `volatile`?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Because a thread on the fast path reads the field without taking the lock, so nothing orders the constructor's writes against the assignment of the reference. It can see the reference before the object is initialised. The volatile write establishes the happens-before edge: constructor writes precede it by program order, and it precedes any volatile read that observes the reference. The holder-class idiom avoids the problem entirely.

### Locks, Atomics & java.util.concurrent

**Why must `unlock()` be in a `finally` block?** ⭐  
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Because nothing else releases a `ReentrantLock`. If an exception is thrown between `lock()` and `unlock()`, the lock stays held permanently and every other thread waiting on it blocks forever. `synchronized` does not have this problem — the JVM releases the monitor on any exit — which is one reason it should remain the default.

**When would you use `LongAdder` instead of `AtomicLong`?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    For counters with heavy concurrent writes and occasional reads, such as metrics. `AtomicLong` has every thread CAS the same memory location, so under contention most attempts fail and retry. `LongAdder` stripes updates across cells and sums on read, which scales far better, at the cost of `sum()` not being a point-in-time snapshot. Use `AtomicLong` where each operation needs an exact value, such as allocating IDs.

**What is the risk in `AtomicReference.updateAndGet`?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    The function passed to it may run more than once, because it is a compare-and-set loop that retries on contention. It must therefore be pure — no logging, no I/O, no mutation of anything else — or those effects will happen a variable number of times. The same applies to `accumulateAndGet` and the equivalent methods on every atomic class.

### Executors & Thread Pool Design

**What is wrong with `Executors.newFixedThreadPool`?** ⭐  
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    It is backed by an unbounded `LinkedBlockingQueue`. When producers submit faster than the fixed number of workers can process, the queue grows without limit until the heap is exhausted — a load spike becomes an `OutOfMemoryError`. For a production service, construct a `ThreadPoolExecutor` directly with a bounded queue and an explicit rejection policy.

**In what order does a `ThreadPoolExecutor` add threads and queue tasks?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Core threads first, then the queue, then extra threads up to the maximum — only when the queue refuses a task. That is counterintuitive, and it means that with an unbounded queue, which never refuses, the pool never grows beyond its core size and `maximumPoolSize` has no effect at all.

**Why did my scheduled job stop running?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Because one execution threw an exception. `ScheduledExecutorService` documents that an exception suppresses all subsequent executions, and the exception is stored in the returned `ScheduledFuture`, which usually nobody holds — so the job stops silently. The fix is to catch exceptions inside the task body so the schedule survives a failed run.

### CompletableFuture

**What executor does `supplyAsync` use by default, and why does it matter?** ⭐  
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    `ForkJoinPool.commonPool()`, which is shared by the whole JVM — including parallel streams — and sized at roughly one thread per core. Blocking I/O there occupies one of a handful of workers, and enough concurrent calls exhaust the pool and stall unrelated code elsewhere in the process. Always pass an explicit executor for anything that blocks; on Java 21+ a virtual-thread executor is the natural choice.

**Why is the exception in `exceptionally` a `CompletionException`?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Because exceptions thrown inside a stage are wrapped in `CompletionException` as they propagate to dependent stages, and `join()` throws it too, while `get()` wraps in `ExecutionException`. Code that matches on the original exception type silently fails to match. Always unwrap via `getCause()` before inspecting.

**What is the difference between `handle` and `whenComplete`?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Both run whether the stage succeeded or failed and receive both the value and the exception. `handle` returns a new result, so it can recover from a failure. `whenComplete` returns nothing and passes the original outcome through unchanged, so it is for side effects such as metrics or logging — using it expecting to swallow an error leaves the failure propagating downstream.

### ConcurrentHashMap & Concurrent Collections

**Is this code thread-safe: `if (!map.containsKey(k)) map.put(k, v);`?** ⭐  
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    No. Both calls are individually atomic, but the sequence is not — two threads can both see the key absent and both write, and one write is silently lost. The correct form is a single atomic call, `map.putIfAbsent(k, v)`, whose return value tells you whether you won the race.

**What does "weakly consistent iterator" mean?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    It means the iterator never throws `ConcurrentModificationException` and never exposes corrupt state, but it reflects the map at some point at or after creation and may or may not see concurrent updates. It is not a snapshot. Code that needs a consistent view must copy, or use a structure like `CopyOnWriteArrayList` whose iterator genuinely is a snapshot.

**Why is `size()` unreliable, and what should you use instead?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    The count is striped across multiple counter cells to avoid contention on a single field, and `size()` sums them without taking a global lock, so the result corresponds to no single instant. Use it for metrics and logging. For correctness — capacity limits, emptiness checks that gate behaviour — restructure the logic so it does not depend on a count, or hold an explicit lock.

### Virtual Threads

**Why should you not pool virtual threads?** ⭐  
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Pooling exists because platform threads are expensive to create and limited in number, neither of which is true of virtual threads. A fixed pool of virtual threads caps concurrency exactly as before and adds a queue, giving back the scalability you adopted them for. If you need to limit concurrency against a downstream service, use a `Semaphore`, which expresses the real constraint.

**What happens when a virtual thread blocks on I/O?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Its stack is copied from the carrier to the heap and the carrier is released to run another virtual thread. When the I/O completes, the stack is copied back onto some carrier and execution resumes on the next line. The JDK rewired its blocking operations — sockets, locks, `sleep`, blocking queues — to do this, which is why the calling code needs no changes.

**What is pinning?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    A situation where a virtual thread blocks without unmounting, so it holds its carrier and reduces the scheduler's effective parallelism. Historically the main cause was blocking inside a `synchronized` block, which JEP 491 fixed in Java 24; native frames from JNI still pin. Because the carrier pool is small — one per core by default — a handful of pinned threads can stall a service.

### Structured Concurrency

**What happens when one subtask fails?** ⭐  
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    It depends on the policy. With `allSuccessfulOrThrow`, the scope shuts down: the remaining subtasks are interrupted, nested scopes are cancelled transitively, and `join()` throws with the original failure as the cause. With `awaitAll`, nothing is cancelled and you inspect each subtask's state yourself. Choosing the policy at the scope is the point — it is no longer scattered across `Future.get` calls.

**Why can't you call `Subtask.get()` before `join()`?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    Because the result may not exist yet, and returning null or blocking implicitly would both hide that. The API throws `IllegalStateException` instead, forcing the code to reach `join()` first. The same rule prevents forking after `join()` — both are ways the structure could be broken, closed off at the API rather than left as a convention.

**How is cancellation implemented?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    By interruption, the same mechanism as `Thread.interrupt`. That means subtasks must be interruptible for cancellation to work: a subtask blocked in a non-interruptible native call will not stop, and the scope will wait for it at `close()`. Cooperative cancellation is still cooperative — structured concurrency organises it, it does not make it forceful.

### ThreadLocal → ScopedValue

**Why is `ScopedValue` better than `ThreadLocal` for request context?** ⭐  
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Because the lifetime is bounded by the block rather than by someone remembering to call `remove()`, so context cannot leak into the next request on a pooled thread. The binding is immutable, so callee code cannot change what the caller established. And reads of an unbound value throw at the read site rather than returning null and failing somewhere unrelated.

**How do you provide a different value for part of a scope?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Nest another `where(...).run(...)`. The inner binding shadows the outer one for the duration of that block and the outer value is restored on exit — no save-and-restore, no `finally`. With `ThreadLocal` the same thing requires reading the old value, setting the new one, and restoring it in a `finally`, which is three lines and a refactoring hazard.

**Can you still use `ThreadLocal` after Java 25?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Yes, and for some things you must. `ScopedValue` bindings are immutable, so it cannot express a mutable per-thread cache such as a reusable buffer. Those remain `ThreadLocal` — though under virtual threads the per-thread-cache pattern needs rethinking anyway, since one buffer per thread stops being cheap at a million threads.

---

## L3 — Enterprise

30 questions.

### Threading Fundamentals

**A background thread stopped working and nothing was logged. What happened?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    An uncaught exception terminated it. Only that thread dies, and the default handler prints to `System.err`, which in a container with structured logging often goes unmonitored. Set an `UncaughtExceptionHandler` on the thread and a JVM-wide default as a backstop. Inside an executor the failure mode differs — the exception is trapped in the `Future` and never surfaces unless something calls `get()`.

**In a thread dump, what does `RUNNABLE` actually tell you?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    Less than people assume. It covers threads executing, threads ready to execute, and threads blocked in OS-level I/O such as a socket read, because the JVM cannot distinguish the last case from running code. `BLOCKED` specifically means contending for a Java monitor. A service waiting on hundreds of HTTP calls shows hundreds of `RUNNABLE` threads while using almost no CPU.

**How much does a platform thread cost, and why does it matter?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    Roughly 1 MB of reserved stack by default, tens to hundreds of microseconds to create, plus a context switch of about 1–10 µs each time it is scheduled. That arithmetic caps a typical service at a few thousand threads, which is why blocking thread-per-request architectures hit a concurrency ceiling well below what the hardware could handle. It is the entire motivation for pooling, for reactive programming, and ultimately for virtual threads.

### Shared State & Synchronization

**How do you prevent deadlock?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    The practical answer is a global lock ordering: every code path that acquires more than one lock acquires them in the same defined order, which makes a circular wait impossible. Alternatives break one of the other three conditions — `tryLock` with a timeout allows preemption, acquiring all locks at once removes hold-and-wait, and immutable data removes the lock entirely. Ordering is preferred because it is a static property you can review rather than a behaviour you must test for.

**Explain double-checked locking and why `volatile` is required.**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    It checks the field without a lock, takes the lock only on the null path, and re-checks inside — so the common case costs one read instead of a lock acquisition. Without `volatile`, the writes initialising the new object can be reordered after the write that publishes its reference, so another thread can see a non-null field pointing at an object whose fields are still default values. The `volatile` write establishes the ordering that makes the published object fully constructed.

**A service is at 100% CPU but processing nothing. What are you looking for?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    Not deadlock — deadlocked threads consume no CPU and are reported explicitly by `jcmd Thread.print`. This pattern points at livelock, where threads detect contention, back off, and retry in lockstep without progressing, or at a spin loop reading a non-volatile flag that the JIT hoisted out of the loop. Take several thread dumps a few seconds apart and compare stacks; threads stuck at the same line while burning CPU identify both cases.

### The Java Memory Model

**What do final fields guarantee?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    That any thread obtaining a reference to a properly constructed object sees its final fields — and everything reachable through them as of the end of the constructor — fully initialised, regardless of how the reference was published. The JMM specifies a freeze at constructor end. The conditions matter: `this` must not escape during construction, the guarantee covers only final fields, and it does not extend to mutations after the freeze.

**Why does concurrent code that works on x86 fail on ARM?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Because x86 has a strong memory model — Total Store Order — that already provides most of the ordering the JMM requires, so missing synchronisation frequently goes unpunished. ARM has a weak model that reorders freely, so the same data race manifests. The JMM is identical on both; what differs is how much the hardware forgives. Migrating to ARM instances is effectively a concurrency audit.

**Why might a loop polling a non-volatile flag never terminate?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Because the JIT may observe that nothing in the loop writes the flag, hoist the read out of the loop, and compile it as an infinite loop. That is permitted: the program has a data race, so the JMM places no constraint on what the read returns. It typically appears only after the method is JIT-compiled — in production, after warmup — and never in a debugger running interpreted code, which is why it is so hard to reproduce.

### Locks, Atomics & java.util.concurrent

**What is the ABA problem?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    A compare-and-set checks only that a value equals what was previously read, not that it was never changed. If another thread changes it from A to B and back to A, the CAS succeeds and the first thread proceeds on a stale assumption. It matters chiefly in lock-free structures that recycle nodes; `AtomicStampedReference` solves it by pairing the reference with a version counter so the CAS fails when the stamp has moved.

**How does `StampedLock`'s optimistic read work?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    `tryOptimisticRead` returns a stamp without taking any lock; you read fields into locals, then call `validate(stamp)` to check that no write occurred meanwhile. If validation succeeds, the reads are consistent and no locking happened at all; if it fails, you fall back to a real read lock and re-read. It is the fastest read-mostly option but it is not reentrant, has no condition support, and requires reading into locals before validating because the data may be inconsistent until then.

**What is AQS and why does it matter?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    `AbstractQueuedSynchronizer` is the framework under `ReentrantLock`, `Semaphore`, `CountDownLatch`, `ReentrantReadWriteLock`, and `FutureTask`. It provides a single atomic `int` state, whose meaning each synchroniser defines — hold count, permits, remaining count — plus a FIFO queue of parked threads. Parking, queuing, interruption, and timeouts are implemented once and inherited by all of them, which is why they behave so consistently.

### Executors & Thread Pool Design

**How do you size a thread pool?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    For CPU-bound work, roughly the number of cores — more threads add context switching without throughput. For I/O-bound work, the classic answer is cores × (1 + wait time / compute time), derived from Little's law. But on Java 21+ the better answer for I/O-bound work is not to size a pool at all: use virtual threads and bound the real constraint — the downstream service's capacity — with a `Semaphore`. The formula was always an indirect way of expressing that limit.

**What is `CallerRunsPolicy` and when would you use it?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    A rejection policy that, when the pool is saturated, runs the task on the submitting thread instead of rejecting it. That slows the producer down by occupying it with the work, which throttles submission naturally — backpressure without dropping tasks or throwing. It suits cases where producers can tolerate being slowed, and is unsuitable where the submitting thread is itself latency-critical, such as a request-handling thread.

**What is a bulkhead and how do you implement one?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Isolation of capacity per dependency, so a slow or failing downstream exhausts only its own resources rather than a shared pool. Traditionally that meant a separate thread pool per dependency. With virtual threads it is cheaper to use a separate `Semaphore` per dependency, which bounds concurrent calls to each downstream while sharing the essentially free virtual-thread capacity.

### CompletableFuture

**Which thread runs a non-async stage like `thenApply`?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Either the calling thread, if the future is already complete when the stage is registered, or whichever thread completes the future. That means a stage attached to a future completed by an HTTP client callback runs on the client's I/O thread, where slow work blocks the client. Using the `...Async` variant with an explicit executor makes the thread deterministic.

**Does `cancel(true)` stop the running task?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    No. It completes the future with a `CancellationException` so dependent stages see cancellation, but the `mayInterruptIfRunning` argument is ignored — `CompletableFuture` holds no reference to the executing thread and cannot interrupt it. The same applies to `orTimeout` and the losers of `anyOf`: the future completes, the work keeps running. Structured concurrency's cancellation does interrupt subtasks, which is a concrete advantage.

**Why is calling `join()` inside a stage dangerous?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Because it blocks a pool thread waiting for another task that may need a pool thread to run. In a small pool — especially the common pool — enough such stages occupy every worker, and the tasks they are waiting on can never start. It is a classic route to pool exhaustion and outright deadlock. Compose with `thenCompose` or `thenCombine` instead of waiting inside a stage.

### ConcurrentHashMap & Concurrent Collections

**How does `ConcurrentHashMap` achieve concurrent writes without a global lock?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    The table is an array of bins and each bin is guarded independently. Inserting into an empty bin is a single compare-and-swap on the table slot with no lock at all; inserting into an occupied bin synchronises on that bin's first node. Reads take no lock because the table reference and each node's value and next pointer are volatile. Two threads writing different bins never interact.

**What are the constraints on the `computeIfAbsent` mapping function, and why?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    It runs while the bin's lock is held, so it must be fast and must not block. It must not access the same map — `ConcurrentHashMap` detects this and throws `IllegalStateException`, because it would otherwise deadlock or corrupt. It should not perform I/O or acquire other locks, since that blocks every other key hashing to the same bin. For slow loads, cache a `CompletableFuture` so only its creation happens under the lock.

**How does resizing work without blocking readers?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    Migrated bins are replaced with a `ForwardingNode` that points to the new table. Readers hitting one are redirected and complete normally against the new table. Writers hitting one call `helpTransfer`, claim a stride of bins from a shared index, and migrate them — so resizing is cooperative across whichever threads happen to be active, rather than one thread doing all the work while everyone waits.

### Virtual Threads

**You switched to virtual threads and throughput barely improved. Why?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Because the thread count was not the bottleneck. Virtual threads remove the thread ceiling and expose whatever was behind it — usually a connection pool, a rate-limited downstream service, or a lock. Ten thousand threads waiting on twenty connections still yields twenty concurrent queries. The work is to identify the real limiting resource and decide whether it can or should be raised.

**What is the risk of `ThreadLocal` with virtual threads?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Memory. A `ThreadLocal` holding an 8 KB buffer across 200 platform threads costs 1.6 MB; across a million virtual threads it is 8 GB. The mechanism still works correctly — each thread has its own value, cleaned up when the thread ends — but the assumption that thread count is small no longer holds. `ScopedValue`, final in Java 25, shares an immutable binding instead and is the right tool for request context.

**How do you observe a service running millions of virtual threads?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Not with `jstack`, which only reports platform threads. Use `jcmd <pid> Thread.dump_to_file -format=json`, which includes virtual threads and groups them by structured-concurrency scope where one exists. For pinning specifically, the `jdk.VirtualThreadPinned` JFR event identifies where a carrier was held, replacing the older `jdk.tracePinnedThreads` flag.

### Structured Concurrency

**How does this change what you see in a thread dump?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    Each scope records its owner and its subtasks, so the runtime holds a real task tree. `jcmd <pid> Thread.dump_to_file -format=json` groups virtual threads by scope, turning what would be ten thousand flat entries into a readable call tree that shows which request each thread belongs to. With unstructured fan-out onto virtual threads, the dump is technically complete and practically useless.

**What is the difference between this and `CompletableFuture`?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    `CompletableFuture` composes asynchronous results but imposes no lifetime: nothing prevents a stage outliving its caller, `anyOf` leaves losers running, and stack traces typically start in the ForkJoinPool with no path back to the request. Structured concurrency binds lifetime to a block, cancels siblings by policy, and preserves the full stack including the fork site. It also reads as sequential code, which `CompletableFuture` chains never do.

**The API changed between Java 21 and Java 25. What changed and why does it matter?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    Java 21 chose the policy by subclass — `ShutdownOnFailure`, `ShutdownOnSuccess` — and required `join()` followed by `throwIfFailed()`. Java 25 replaced that with `StructuredTaskScope.open(Joiner...)`, where the policy is a value and `join()` throws directly. It matters practically because the majority of tutorials and blog posts still show the Java 21 shape, and that code does not compile on 25 — so anyone adopting it needs to know which era a sample comes from.

### ThreadLocal → ScopedValue

**Why does `ScopedValue` matter specifically for virtual threads?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Two reasons. `InheritableThreadLocal` copies the parent's map into every child thread at creation, which is negligible at two hundred threads and a real memory and allocation cost at a million. And `ThreadLocal` values are per thread, so any non-trivial value — an 8 KB buffer, a cached formatter — multiplies by the thread count. `ScopedValue` bindings are immutable and therefore shared rather than copied, with nothing stored per thread at all.

**How does a `ScopedValue` reach a forked subtask?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Subtasks forked inside a `StructuredTaskScope` inherit the bindings in effect where the scope was opened. Because the value is immutable, they share the same reference — no copy, no synchronisation. This is the intended pairing: structured concurrency provides the task tree and `ScopedValue` provides the context that flows down it. A thread started with `new Thread(...)` outside a scope does *not* inherit bindings.

**What does `ScopedValue` not guarantee?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    That the object you bound is immutable. The binding cannot be reassigned, but nothing stops code calling a setter on the bound object, and since forked subtasks share the reference that becomes a data race. Bind records or otherwise deeply immutable values — the guarantee is about the binding, not the graph behind it.

---

## L4 — Architect

30 questions.

### Threading Fundamentals

**Why was `Thread.stop()` unsafe, and what is the correct model?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    It threw an asynchronous `ThreadDeath` at an arbitrary bytecode boundary and released every monitor the thread held — so other threads immediately observed data that was half-updated, with no way to detect it. There is no safe point the caller can choose from outside. The correct model is cooperative: the thread defines its own safe cancellation points, checks a flag or handles `InterruptedException` there, and unwinds cleanly with its invariants intact.

**Your service must shut down within 30 seconds. How do you structure thread termination?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    Signal first, wait second, escalate third: interrupt every worker, then `join` each with a bounded duration rather than indefinitely, and log anything still alive at the deadline. Workers must treat interruption as a cancellation request and must not hold unbounded blocking calls that ignore it — notably socket reads, which need the socket closed rather than the thread interrupted. Anything that writes data must be a user thread, so the JVM does not exit out from under it.

**When is a raw `Thread` still the right choice on Java 21+?**   
<small>[Threading Fundamentals](../04-concurrency/24-threading-fundamentals.md)</small>

??? success "Answer"
    For a small number of long-lived, dedicated, always-running workers — a log shipper, a scheduler loop, a single consumer pinned to one resource — where you want explicit lifecycle control and no pool semantics. For anything request-scoped or bursty, an executor or a virtual thread is better, because the cost model and the cancellation semantics are already solved. The deciding question is whether the thread's lifetime matches the application's or the task's.

### Shared State & Synchronization

**How would you eliminate locking from a hot path entirely?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    Remove the sharing rather than guard it. Confine mutable state to a single thread and communicate by passing immutable messages through a queue; or make the state immutable and publish new versions by atomic reference swap; or partition by key so each partition is owned by one thread, which is how per-SKU inventory would be structured. Where a single variable must be shared, a compare-and-swap loop over an atomic avoids blocking altogether. Each of these trades a lock for a design constraint, which is usually the better trade.

**What changed for `synchronized` with virtual threads, and how does it affect design?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    On Java 21 and 22 a virtual thread blocking inside `synchronized` pinned its carrier platform thread, so heavy monitor contention could exhaust the small carrier pool and stall the whole scheduler — the guidance then was to replace those blocks with `ReentrantLock`, which parks without pinning. JEP 491 in Java 24 removed the restriction, so `synchronized` is once again the simpler default. The design consequence is version-dependent, which makes it worth knowing which baseline a codebase targets before reviewing its locking.

**How do you decide between `synchronized`, `ReentrantLock`, and atomics?**   
<small>[Shared State & Synchronization](../04-concurrency/25-shared-state.md)</small>

??? success "Answer"
    Start with atomics when the state is a single variable and the operation is a compare-and-swap — no blocking, no deadlock possible. Use `synchronized` for anything more complex, because it is scoped to a block, released automatically on exception, and the only form the JVM reports in deadlock detection. Reach for `ReentrantLock` when you specifically need what it adds: timed or interruptible acquisition, fairness, multiple condition variables, or a lock whose scope is not a block. Choosing `ReentrantLock` by default trades automatic release for features most code never uses.

### The Java Memory Model

**Someone argues a data race in your codebase is benign. How do you evaluate it?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Require the argument to hold under every permitted behaviour, not just the likely one. `String.hashCode` is benign because the field is an `int` that cannot tear, the computation is deterministic, the value is read once into a local, and the worst outcome is redundant recomputation. Change any of those — a `long`, two reads of the field, a computation depending on mutable state — and it is simply wrong. The practical position is that application code should not contain intentional races: the analysis is subtle, fragile under refactoring, and the cost of synchronising is almost always negligible.

**How would you review a piece of lock-free code?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    Demand a happens-before argument for every shared access, naming the rule at each step, because lock-free code has no lock to provide the edges implicitly. Check that every compare-and-set loop handles contention and the ABA problem where references are reused, that weaker `VarHandle` modes are justified by measurement and accompanied by a proof, and that there is a stress test — ideally with a tool that exposes reorderings — run on weakly-ordered hardware. Then ask whether it needs to be lock-free at all, since a `ConcurrentHashMap` or a lock is usually fast enough and far easier to verify.

**What is the most important consequence of DRF-SC for day-to-day engineering?**   
<small>[The Java Memory Model](../04-concurrency/26-java-memory-model.md)</small>

??? success "Answer"
    That you do not have to reason about caches, store buffers, and compiler reordering — provided you eliminate data races. Every shared variable accessed under a happens-before relationship, whether through a lock, a volatile, a final field, or a concurrent collection, restores the intuitive model where statements execute one at a time in some interleaving. That turns concurrency correctness from a hardware question into a discipline question: identify shared mutable state, and ensure every access to it is ordered. Everything subtler is only necessary when you deliberately step outside that discipline.

### Locks, Atomics & java.util.concurrent

**How do you choose between a lock, an atomic, and an immutable swap?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    An atomic when the state is a single variable and the update is a compare-and-set — it cannot deadlock and never blocks. An immutable object behind a volatile reference when updates replace the whole value, because readers take no lock at all and writers swap atomically, which beats any read-write lock for read-mostly data. A lock when an invariant spans several variables, since neither alternative can protect a multi-variable invariant. The ordering reflects increasing cost and increasing generality.

**Should locks be fair?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Rarely. A fair lock grants access in arrival order, preventing starvation, but it forces a context switch on every handoff that barging would avoid, and it commonly costs an order of magnitude in throughput under contention. Starvation is seldom the actual failure mode, so fairness should be introduced in response to observed starvation rather than as a precaution. It is also worth noting `synchronized` offers no fairness guarantee at all, so fairness is a positive reason to choose `ReentrantLock`, not a default.

**How did virtual threads change the choice between `synchronized` and `ReentrantLock`?**   
<small>[Locks, Atomics & java.util.concurrent](../04-concurrency/27-locks-and-atomics.md)</small>

??? success "Answer"
    Briefly, and then back again. On Java 21 to 23, a virtual thread blocking inside `synchronized` pinned its carrier platform thread, while `ReentrantLock` parked through AQS and unmounted correctly — so the guidance was to convert contended `synchronized` blocks. Java 24's JEP 491 removed pinning for `synchronized`, restoring it as the simpler default. The lasting lesson is that platform constraints produce workarounds that outlive them, so conversions made for Java 21 should be reverted where they bought nothing else.

### Executors & Thread Pool Design

**How did virtual threads change thread pool design?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    They split it in two. For I/O-bound work, pool sizing becomes obsolete: blocking is cheap, so one virtual thread per task is correct and pooling them is harmful, while the actual constraint — a downstream's capacity — is expressed directly with a semaphore. For CPU-bound work nothing changed, since cores remain the limit and a fixed platform pool is still right. Scheduled work still needs a `ScheduledExecutorService`. The practical consequence is that most of the pool-sizing folklore in older codebases can be deleted, and the remaining pools become simpler to reason about.

**How would you make a service's executors observable?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    Expose active count, pool size, queue depth, and completed-task count as gauges for each pool, and alert on sustained queue growth rather than on rejection — growth is the leading indicator that producers are outpacing consumers, while rejection is the lagging one. Name every thread through the factory so dumps attribute work to the right pool. And override `afterExecute` to log exceptions from `execute`-submitted tasks centrally, since the default handler writes to standard error, which in a container is often unmonitored.

**What is the risk of `ForkJoinPool.commonPool()`?**   
<small>[Executors & Thread Pool Design](../04-concurrency/28-executors.md)</small>

??? success "Answer"
    It is shared by the whole JVM — parallel streams and `CompletableFuture`'s default async executor both use it — and it is sized for CPU work at roughly one thread per core. Any blocking operation submitted to it occupies one of a small number of workers, so a single slow call inside a parallel stream or an unqualified `supplyAsync` can starve unrelated code elsewhere in the process. The mitigation is never to block there: pass an explicit executor to `CompletableFuture` methods, and use virtual threads or `mapConcurrent` rather than parallel streams for I/O.

### CompletableFuture

**Is `CompletableFuture` still relevant on Java 21+?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Yes, for a narrower set of problems. Its original main job — fanning out I/O without holding a platform thread per call — is now done better by blocking code on virtual threads, which keeps stack traces and ordinary control flow, and by structured concurrency, which adds lifetimes and real cancellation. What remains is genuine composition: adapting callback-based SDKs, racing alternatives with `anyOf`, timeouts with fallback values, and chains of dependent asynchronous steps. The decision is whether the code is asynchronous by nature or only to avoid blocking.

**What is the observability cost of asynchronous composition?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Stack traces stop at a pool worker. A stage is registered on one thread and executed on another, so the trace shows the worker and the failing line but nothing about which request initiated the chain or which method composed it. Correlating a failure with its cause then depends on explicit context propagation — trace IDs passed through or bound with `ScopedValue` — rather than the call stack. That cost, more than performance, is the strongest argument for moving straightforward fan-out to virtual threads.

**How would you audit a codebase's use of `CompletableFuture`?**   
<small>[CompletableFuture](../04-concurrency/29-completable-future.md)</small>

??? success "Answer"
    Start with executor choice, since it produces the most incidents: every `supplyAsync` or `...Async` without an executor argument that performs blocking work is a latent common-pool exhaustion. Then check exception handling for unwrapped `CompletionException` type matches, discarded futures whose failures are never observed, and `join()` or `get()` inside stages. Finally, classify chains by whether they are compositional or merely avoiding blocking, and plan to migrate the second group to virtual threads as the code is touched. The first three are bugs; the last is modernisation.

### ConcurrentHashMap & Concurrent Collections

**Your service uses `ConcurrentHashMap` as a cache and memory grows without bound. Diagnose it.**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    `ConcurrentHashMap` has no eviction policy, no size bound, and no TTL — it is a map, not a cache. Every distinct key ever requested is retained for the life of the map, so any unbounded or attacker-influenced key space grows forever. The fix is a real cache with a size or time policy such as Caffeine, or an explicit bound enforced on write. A weak-value map is rarely the answer, because it makes eviction timing depend on GC.

**When would you choose `ConcurrentSkipListMap` over `ConcurrentHashMap`?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    When you need ordering: sorted iteration, range queries, floor or ceiling lookups — the concurrent equivalent of `TreeMap`. It costs O(log n) instead of O(1) per operation and uses more memory per entry, so it is a deliberate trade for the ordering. It is also the only concurrent map in the JDK that implements `SequencedMap`, since `ConcurrentHashMap` has no defined encounter order.

**A team replaced `synchronizedMap` with `ConcurrentHashMap` and now sees intermittent data corruption. What is the likely cause?**   
<small>[ConcurrentHashMap & Concurrent Collections](../04-concurrency/30-concurrent-collections.md)</small>

??? success "Answer"
    Almost certainly compound operations that used to be protected by an external `synchronized` block around several map calls. Swapping the implementation removed the global lock, so those multi-call sequences are now races even though each individual call is atomic. The fix is to rewrite each sequence as a single atomic `compute`, `merge`, or `putIfAbsent`. The same bug appears when a mutable value stored in the map is mutated outside any lock.

### Virtual Threads

**When would you still choose reactive over virtual threads?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    When backpressure is a first-class requirement rather than an afterthought — a streaming pipeline where a slow consumer must signal upstream — or where the domain is genuinely event-driven rather than request-shaped. Reactive also remains the answer where an existing system is already built that way and the rewrite cost exceeds the benefit. For ordinary request-per-thread services with blocking clients, virtual threads deliver the scalability without giving up stack traces, debuggers, and `try`/`catch`.

**How would you decide whether to adopt virtual threads in a large service?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    Start by classifying the workload: if threads spend most of their time waiting on I/O, the gain is real; if they are computing, there is none. Then find the true bottleneck, because virtual threads only move the ceiling to the next constraint, and if that is a shared database the change may increase queueing rather than throughput. Audit `ThreadLocal` usage and any `synchronized` blocks that block, and check the JDK version — on 21 to 23 pinning needs profiling, on 24+ it largely does not. The code change is usually small; the review is about what breaks when concurrency rises by two orders of magnitude.

**What is the design trade-off Loom made, and what did it cost?**   
<small>[Virtual Threads](../04-concurrency/31-virtual-threads.md)</small>

??? success "Answer"
    It chose to preserve the blocking programming model and change the runtime underneath, rather than change the programming model as reactive did. The cost was a substantial rewiring of the JDK's blocking operations, a period where `synchronized` pinned carriers, and an ongoing obligation that any code reaching native frames still blocks a carrier. What it bought is that existing blocking code, debuggers, profilers, and stack traces all continue to work — which is why adoption is a configuration change rather than a rewrite, and why it is likely to displace reactive for the majority of server workloads.

### Structured Concurrency

**Would you use structured concurrency in production today, and how would you bound the risk?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    The model is sound and worth using, but the API is still preview and has changed across five successive previews, so code written against it may need rewriting on the next JDK. The pragmatic position is to adopt virtual threads freely — they are final — and confine structured concurrency to a small number of bounded, easily-rewritten call sites where the fan-out is genuinely complex. Never put it in a shared library: preview class files refuse to load on a different JDK version, which turns an internal choice into everyone's problem.

**How does structured concurrency interact with observability and tracing?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    It helps in two directions. The scope tree gives thread dumps and profilers a grouping that flat virtual threads lack, so a hung request can be traced to the subtask holding it up. And `ScopedValue` bindings established outside a scope are inherited by its subtasks, so trace identifiers, tenant context, and security principals propagate into forked work without `ThreadLocal` inheritance or manual passing. Together they restore the request-scoped reasoning that fan-out onto raw executors destroys.

**What does this model borrow, and what remains unsolved?**   
<small>[Structured Concurrency](../04-concurrency/32-structured-concurrency.md)</small>

??? success "Answer"
    It is the same argument Dijkstra made about `goto`: unrestricted transfer of control — here, unrestricted task lifetime — makes programs hard to reason about, and the fix is to make control flow follow lexical structure. Kotlin's coroutine scopes and Trio's nurseries are the direct precedents. What remains unsolved is anything genuinely unstructured: long-lived background workers, pub/sub consumers, and fire-and-forget tasks do not fit a block-scoped lifetime, and forcing them into one produces worse code than an executor. Structured concurrency is for fan-out within an operation, not for every use of a thread.

### ThreadLocal → ScopedValue

**When is ambient context the wrong design?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    When the dependency is real and shallow. Two layers deep, an explicit parameter is clearer, testable without setup, and visible in the signature — ambient context hides a dependency that the type system could have shown. It earns its place for genuinely cross-cutting concerns that most of the stack does not care about: tracing, tenancy, security principal, locale. The test is whether the intermediate layers would ever act on the value; if they would, pass it.

**How would you plan a migration from `ThreadLocal` to `ScopedValue` in a large service?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Classify first, because the three kinds of `ThreadLocal` have different answers: set-once request context migrates mechanically, mutable per-thread caches stay, and anything written repeatedly during a request is shared mutable state that needs redesigning rather than porting. Then migrate the first kind at the binding boundary — the request filter or job runner — and let the compiler find every read site. The part the compiler will not find is code that depended on `get()` returning null when unbound, so each read needs a decision between `get()`, `orElse`, and `isBound()`. Finally, check for any reliance on `InheritableThreadLocal` propagating into manually-created threads, since that path only works through a structured scope now.

**What is the underlying design principle here, and where else does it appear?**   
<small>[ThreadLocal → ScopedValue](../04-concurrency/33-scoped-values.md)</small>

??? success "Answer"
    Replacing unbounded mutable state with an immutable binding whose lifetime follows lexical structure — the same argument as structured concurrency, applied to data rather than tasks. In both cases the old mechanism gave power with no guarantees (a task could outlive its caller; a value could persist past its request) and the fix was to make the code's shape enforce the lifetime. The cost is that genuinely unstructured cases no longer fit, which is why mutable per-thread caches keep `ThreadLocal` and long-lived background workers keep executors. The gain is that the common case becomes impossible to get wrong.

