#!/usr/bin/env python3
"""Build the Examples pages (docs/07-examples/) from code/examples/.

Code and real output are INCLUDED with snippets (--8<--), never pasted, so a page can
never show code that doesn't run. Refresh outputs first:  python3 tools/run-examples.py

Usage: python3 tools/build-examples.py
"""
import pathlib, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/07-examples"
EX = ROOT / "code/examples"

CH = {  # chapter links, relative to docs/07-examples/
    "hashmap": "../03-collections/19-hashmap-internals.md", "chm": "../04-concurrency/30-concurrent-collections.md",
    "cf": "../04-concurrency/29-completable-future.md", "lambdas": "../02-language/06-lambdas-functional-interfaces.md",
    "streams": "../02-language/07-stream-api.md", "collectors": "../02-language/08-collectors.md",
    "optional": "../02-language/09-optional.md", "time": "../02-language/10-java-time.md",
    "j9": "../02-language/11-java-9-to-11.md", "j14": "../02-language/12-java-14-to-17.md",
    "patterns": "../02-language/13-pattern-matching.md", "j21": "../02-language/14-java-21-to-26.md",
    "http": "../05-runtime/40-http-client.md", "vt": "../04-concurrency/31-virtual-threads.md",
    "seq": "../03-collections/21-sequenced-collections.md", "choose": "../03-collections/17-choosing-a-collection.md",
    "immut": "../03-collections/22-immutability.md", "threads": "../04-concurrency/24-threading-fundamentals.md",
    "shared": "../04-concurrency/25-shared-state.md", "locks": "../04-concurrency/27-locks-and-atomics.md",
    "exec": "../04-concurrency/28-executors.md", "jmm": "../04-concurrency/26-java-memory-model.md",
    "equality": "../03-collections/23-equality-and-ordering.md",
}
CH_NAME = {k: re.search(r"/(\d\d)-", v).group(1) for k, v in CH.items()}

YIELD_NOTE = ("!!! note \"Why there is a `Thread.yield()`\"\n"
              "    The output was captured on a single-core machine, where threads rarely interleave on their own.\n"
              "    The `yield()` makes the switch happen exactly inside the unsafe window — which is what a real\n"
              "    multi-core server does without help. Exact numbers vary from run to run; the conclusion does not.\n")

PAGES = []

# ---------------------------------------------------------------- HashMap
PAGES.append(dict(file="hashmap-internals.md", title="How HashMap Works Inside", nav="HashMap — how it works inside",
intro=r"""
A `HashMap` is an **array of buckets**. Every `put` and `get` does the same few steps to decide which bucket a key
belongs in. Once you can follow those steps, every HashMap behaviour — fast lookups, resizing, collisions, the
mutable-key bug — follows from them.

## `put(key, value)` step by step

```mermaid
flowchart TD
    A["put(key, value)"] --> B["1. h = key.hashCode()"]
    B --> C["2. spread: h ^ (h >>> 16)"]
    C --> D["3. index = (capacity - 1) & hash"]
    D --> E{"4. bucket empty?"}
    E -->|yes| F["place a new Node"]
    E -->|no| G{"same key in the bucket?<br/>hash equal AND equals()"}
    G -->|yes| H["replace the value"]
    G -->|no| I["append a Node to the chain"]
    I --> J{"chain has 8+ nodes?"}
    J -->|"yes, capacity ≥ 64"| K["convert bucket to a red-black tree"]
    J -->|"yes, capacity < 64"| L["resize instead"]
    F --> M{"5. ++size > threshold?"}
    I --> M
    M -->|yes| N["resize: double the array,<br/>move every entry"]
```

| Step | What happens | Why |
|---|---|---|
| **1. hashCode** | Ask the key for its `int` hash | Equal keys must give equal hashes — the `equals`/`hashCode` contract ([Ch 23]({equality})) |
| **2. spread** | `h ^ (h >>> 16)` mixes high bits into low bits | The index uses only the low bits; this stops keys that differ only in high bits from colliding |
| **3. index** | `(capacity - 1) & hash` | Capacity is a power of two, so this is a fast modulo |
| **4. bucket** | Empty → store. Occupied → compare with each node | Compare the stored `hash` first (cheap), then `equals()` |
| **5. resize** | When `size > capacity × 0.75`, double the array | Keeps chains short so lookups stay O(1) |

`get(key)` repeats steps 1–3, then walks that one bucket comparing `hash` and `equals()`. That is why a lookup is
O(1) on average: it examines one short bucket, not the whole map.

## The numbers to remember

| Constant | Value | Meaning |
|---|---|---|
| Default capacity | 16 | Buckets in a new map (allocated on the first `put`) |
| Load factor | 0.75 | Resize when size exceeds 75% of capacity |
| First threshold | 12 | 16 × 0.75 — the 13th `put` triggers a resize |
| Treeify threshold | 8 | A bucket with 8+ nodes becomes a tree… |
| Min treeify capacity | 64 | …but only if the table has 64+ buckets; otherwise it resizes |
| Untreeify threshold | 6 | A tree that shrinks to 6 nodes becomes a list again |

The examples below take you through this in order: the index arithmetic, a working hash map you can read in one
screen, and then the real `java.util.HashMap` observed from the inside.
""", deep="hashmap",
examples=[
 ("hashmap/HashSpreading", "From key to bucket", "Steps 1–3 — the exact arithmetic `HashMap` uses. The second half shows why spreading matters: two hashes that differ only in their high bits would land in the same bucket without it."),
 ("hashmap/SimpleHashMap", "Build your own hash map in 50 lines", "The same core ideas as `java.util.HashMap` — array of buckets, chaining, replace-on-equal-key, resize at 0.75 — small enough to read in one sitting. It starts with 4 buckets so you can watch two resizes happen."),
 ("hashmap/PeekInsideHashMap", "Inside the real HashMap: lazy table and resize", "Reflection opens up a real `HashMap`. The table does not exist until the first `put`, and the 13th `put` doubles it from 16 to 32 buckets — exactly the threshold rule above. Note that keys land in scattered buckets, not in insertion order."),
 ("hashmap/CollisionsDemo", "What a collision costs", "A key with a constant `hashCode()` sends every entry to one bucket. Counting `equals()` calls shows the lookup becoming a linear search — which is why a good `hashCode` matters."),
 ("hashmap/TreeifyDemo", "When a bucket becomes a tree", "Watch the 8-and-64 rule happen. With the default table, a long chain triggers **resizes** first (16 → 32 → 64); only then does the bucket become a `TreeNode`. A map created with capacity 64 treeifies straight away."),
 ("hashmap/NullKeyAndOrder", "The null key, and why iteration order looks random", "`HashMap` allows one `null` key (it is stored in bucket 0). Iteration follows bucket order, not insertion order — use `LinkedHashMap` for insertion order or `TreeMap` for sorted order ([Ch 17]({choose}))."),
 ("hashmap/MutableKeyBug", "Why keys must be immutable", "Change a field used by `hashCode()` after inserting the key and the entry is still in its **old** bucket, so every lookup searches the wrong one. The entry cannot be found or removed. Records make ideal keys ([Ch 22]({immut}))."),
],
outro="""
!!! abstract "Remember"
    **Array of buckets** · index = `(capacity - 1) & (h ^ h >>> 16)` · compare `hash` then `equals()`
    · resize at **size > capacity × 0.75** · bucket → tree at **8 nodes and 64+ buckets**
    · keys must be **immutable** · iteration order is **not** insertion order

For the full treatment — resize splitting, memory per entry, Java 8 changes — see [Chapter 19]({hashmap}).
"""))

# ---------------------------------------------------------------- ConcurrentHashMap
PAGES.append(dict(file="concurrenthashmap-internals.md", title="How ConcurrentHashMap Works Inside", nav="ConcurrentHashMap — how it works inside",
intro=r"""
`ConcurrentHashMap` has the **same shape as `HashMap`** — an array of bins, chains, and trees for long chains.
What differs is how it lets many threads use that array at once **without one big lock**.

## `put(key, value)` step by step

```mermaid
flowchart TD
    A["put(key, value)"] --> B["hash and find the bin — same as HashMap"]
    B --> C{"table not created yet?"}
    C -->|yes| D["initialise it (one thread wins a CAS)"]
    C -->|no| E{"bin empty?"}
    E -->|yes| F["CAS a new node into the bin<br/>NO LOCK"]
    E -->|no| G{"bin is being moved by a resize?"}
    G -->|yes| H["help with the resize, then retry"]
    G -->|no| I["synchronized on the bin's FIRST node<br/>— only this bin is locked"]
    I --> J["replace or append, like HashMap"]
    F --> K["add to the size counter (LongAdder-style cells)"]
    J --> K
    K --> L{"size ≥ threshold?"}
    L -->|yes| M["resize — other threads can help"]
```

| Operation | How it stays thread-safe | Cost |
|---|---|---|
| `get` | Volatile reads only — **no lock at all** | As fast as `HashMap` |
| `put` into an **empty** bin | One CAS (compare-and-swap) | No blocking |
| `put` into an **occupied** bin | `synchronized` on that bin's first node | Blocks only threads using the **same bin** |
| `compute`, `merge`, `putIfAbsent` | Run entirely under that bin's lock | **Atomic** read-modify-write |
| Resize | Threads that hit a moved bin help copy | Work is shared |
| `size()` | Summed from striped counter cells | An estimate while updates are running |

## Why it beats the alternatives

| Map | Locking | Two threads writing different keys |
|---|---|---|
| `Hashtable` | One lock for the whole map | Wait for each other |
| `Collections.synchronizedMap` | One lock for the whole map | Wait for each other |
| `ConcurrentHashMap` (Java 7) | 16 fixed segments | Usually parallel |
| **`ConcurrentHashMap` (Java 8+)** | **One lock per bin**, CAS for empty bins | **Parallel** unless they hash to the same bin |

## The lesson that catches everyone

A thread-safe map does **not** make your *logic* thread-safe. Each single method is atomic — but
`get()` followed by `put()` is two calls, and another thread can run in between. The first two examples show this;
the third shows the atomic methods that fix it.
""", deep="chm",
examples=[
 ("concurrenthashmap/LostUpdates", "Thread-safe map ≠ thread-safe logic", "Eight threads count orders. `HashMap` loses updates — and so does `ConcurrentHashMap` when you use `get` then `put`. Only the single atomic `merge` gets the right total.\n\n" + YIELD_NOTE),
 ("concurrenthashmap/CheckThenAct", "The check-then-act race", "\"If absent, then put\" lets several threads all believe they won. `putIfAbsent` does the check and the insert as one atomic step, so exactly one wins.\n\n" + YIELD_NOTE),
 ("concurrenthashmap/AtomicOperations", "The atomic methods, one by one", "`putIfAbsent`, `merge`, `compute`, `computeIfPresent` and `replace(key, old, new)` — each is one call that runs under the bin's lock, so no other thread can interleave."),
 ("concurrenthashmap/ComputeIfAbsentOnce", "Load a value exactly once", "Sixteen requests ask for the same uncached price at the same moment. Get-then-put calls the slow loader sixteen times; `computeIfAbsent` calls it once. Because the loader runs while the bin is locked, keep it fast and never touch the same map inside it."),
 ("concurrenthashmap/IterationWhileModifying", "Iterating while the map changes", "`HashMap` iterators are **fail-fast** and throw. `ConcurrentHashMap` iterators are **weakly consistent**: they never throw, and may or may not see changes made during iteration."),
 ("concurrenthashmap/NoNulls", "Why nulls are not allowed", "With concurrent updates, `get() == null` followed by `containsKey()` can give inconsistent answers, so `ConcurrentHashMap` forbids `null` entirely — `null` from `get` always means *absent*. This also means swapping `HashMap` for it can break code that stored nulls."),
 ("concurrenthashmap/PeekInsideConcurrentHashMap", "Inside the real ConcurrentHashMap", "The same lazy table as `HashMap`, with `sizeCtl` holding the next resize threshold. One real difference shows up here: `ConcurrentHashMap` resizes when the size **reaches** the threshold (the 12th `put`), while `HashMap` waits until it is **exceeded** (the 13th)."),
],
outro="""
!!! abstract "Remember"
    **Same array of bins as HashMap** · empty bin → **CAS, no lock** · occupied bin → **lock that one bin**
    · `get` never locks · `compute`/`merge`/`putIfAbsent` are **atomic** · `get` + `put` is **not**
    · iterators never throw · **no nulls** · `size()` is an estimate under load

For the full treatment — resize internals, `computeIfAbsent` rules, `LongAdder` — see [Chapter 30]({chm}).
"""))

# ---------------------------------------------------------------- CompletableFuture
PAGES.append(dict(file="completablefuture.md", title="CompletableFuture by Example", nav="CompletableFuture by example",
intro=r"""
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
""", deep="cf",
examples=[
 ("completablefuture/CF01_SupplyAsync", "Start work in the background", "`supplyAsync` runs the task on another thread and returns immediately. `join()` waits for the result."),
 ("completablefuture/CF02_ThenApply", "Transform the result", "`thenApply` is to a future what `map` is to a stream: each step receives the previous result."),
 ("completablefuture/CF03_ThenAcceptThenRun", "Consume the result", "`thenAccept` uses the value and returns nothing; `thenRun` runs afterwards without seeing it."),
 ("completablefuture/CF04_ThenCompose", "Chain dependent calls", "When the next step is itself asynchronous, `thenApply` nests a future inside a future. `thenCompose` flattens it — the same idea as `flatMap`."),
 ("completablefuture/CF05_ThenCombine", "Run two calls in parallel", "Two independent 400 ms calls, merged with `thenCombine`, finish in about 400 ms — not 800."),
 ("completablefuture/CF06_AllOf", "Wait for many calls", "`allOf` completes when every future has. It returns `CompletableFuture<Void>`, so read each result from its original future — `join()` no longer blocks at that point."),
 ("completablefuture/CF07_AnyOf", "Take the fastest answer", "`anyOf` completes with the first result. It returns `Object`, and it does not cancel the slower calls."),
 ("completablefuture/CF08_Exceptionally", "Recover with a fallback", "`exceptionally` runs only on failure and supplies a replacement value. Notice the exception arrives **wrapped** in a `CompletionException`."),
 ("completablefuture/CF09_Handle", "Handle success and failure in one place", "`handle` always runs and receives both the value and the exception (one of them is `null`)."),
 ("completablefuture/CF10_WhenComplete", "Observe without changing the result", "`whenComplete` is for side effects like metrics. It cannot recover — the failure still reaches `join()`."),
 ("completablefuture/CF11_Timeouts", "Timeouts", "Java 9 added `orTimeout` (fail) and `completeOnTimeout` (use a default). Neither stops the underlying task."),
 ("completablefuture/CF12_Executors", "Choose the executor", "Without an executor, async stages use the shared `ForkJoinPool.commonPool()`. For blocking work pass your own — on Java 21, a virtual-thread executor.\n\n!!! note \"Why the output says `Thread-N`\"\n    The output was captured on a one-core machine. When the common pool's parallelism is below 2, `CompletableFuture` starts **a new thread per task** instead of using the pool. On a multi-core machine the first line reads `ForkJoinPool.commonPool-worker-N`.\n"),
 ("completablefuture/CF13_ManualComplete", "Wrap a callback API", "Create an incomplete future and complete it from the callback. This is how you adapt older SDKs that report results through listeners."),
 ("completablefuture/CF14_WhichThread", "Which thread runs a stage?", "A non-async stage runs on the thread that completes the future — or on **your** thread if it is already complete. The `...Async` variants always hand off to an executor. (Thread names show `Thread-N` here for the one-core reason explained in example 12.)"),
 ("completablefuture/CF15_ExceptionWrapping", "Exception wrapping", "`join()` throws `CompletionException`, `get()` throws `ExecutionException`; the real exception is the **cause**. Unwrap before checking its type."),
 ("completablefuture/CF16_PuttingItTogether", "Putting it together", "An order view built from three parallel calls. One dependency takes 3 seconds, but a timeout with a sensible fallback keeps the response at about half a second."),
],
outro="""
!!! abstract "Remember"
    `thenApply` = map · `thenCompose` = flatMap · `thenCombine` = zip · `allOf` returns `Void`
    · exceptions arrive **wrapped** · pass an **executor** for blocking work · timeouts don't stop the task
    · on Java 21+, plain blocking code on **virtual threads** is often simpler ([Ch 31]({vt}))

For the full treatment — threading rules, cancellation, when to prefer virtual threads — see [Chapter 29]({cf}).
"""))

# ---------------------------------------------------------------- Concurrency toolkit
PAGES.append(dict(file="concurrency-toolkit.md", title="Concurrency Toolkit by Example", nav="Concurrency toolkit by example",
intro="""
The everyday building blocks of concurrent Java, one small runnable example each: threads, locks, atomics,
visibility, executors, and the coordination tools in `java.util.concurrent`.
""", deep="threads",
examples=[
 ("concurrency/C01_ThreadBasics", "Threads: start, join, and start() vs run()", "`start()` runs the task on a new thread; `run()` is only a method call on the current one. `join()` waits for a thread to finish. See [Ch 24]({threads})."),
 ("concurrency/C02_RaceAndSynchronized", "A race condition, and synchronized", "`count++` is read–add–write, so two threads can overwrite each other's update. `synchronized` makes the whole step exclusive. See [Ch 25]({shared}).\n\n" + YIELD_NOTE),
 ("concurrency/C03_AtomicsAndLongAdder", "Atomics: counters without locks", "`AtomicInteger` for exact values such as IDs, `LongAdder` for busy metrics, and compare-and-set for state transitions. See [Ch 27]({locks})."),
 ("concurrency/C04_VolatileFlag", "volatile: making a write visible", "Without `volatile`, the worker thread may never see the flag change. `volatile` guarantees visibility — but not atomicity. See [Ch 26]({jmm})."),
 ("concurrency/C05_ExecutorAndFutures", "ExecutorService and Futures", "`invokeAll` runs a batch and waits; `invokeAny` returns the first success. A task's exception is kept inside its `Future` until you call `get()`. See [Ch 28]({exec})."),
 ("concurrency/C06_CountDownLatch", "CountDownLatch: wait for N events", "Start taking orders only after every vendor connection is ready."),
 ("concurrency/C07_SemaphoreLimit", "Semaphore: cap concurrent access", "Twenty tasks, but never more than three calls to a fragile API at once — the right way to limit a resource when using virtual threads."),
 ("concurrency/C08_ReentrantLockTryLock", "ReentrantLock: give up instead of hanging", "`tryLock` with a timeout lets a thread fail fast. `synchronized` can only wait forever. Always `unlock()` in `finally`."),
 ("concurrency/C09_ProducerConsumer", "BlockingQueue: producer and consumer", "The queue hands orders from a producer to a consumer; a full queue makes the producer wait. A \"poison pill\" value tells the consumer to stop."),
], outro=""))

# ---------------------------------------------------------------- Version pages
def version_page(file, title, nav, intro, examples, outro=""):
    PAGES.append(dict(file=file, title=title, nav=nav, intro=intro, deep=None, examples=examples, outro=outro))

version_page("java-8.md", "Java 8 by Example", "Java 8 by example", """
Java 8 (2014) changed how Java is written: lambdas, streams, `Optional`, the `java.time` API and default methods.
Every example is a complete program. Where a line uses a later feature for brevity — such as `Stream.toList()`
(Java 16) or records (Java 16) — the Java 8 equivalent is noted in a comment.
""", [
 ("java8/J8_01_Lambdas", "Lambdas and functional interfaces", "A lambda is a short way to pass behaviour. `Predicate`, `Function`, `Consumer` and `Supplier` cover most needs, and they compose with `and`, `negate` and `andThen`. See [Ch 06]({lambdas})."),
 ("java8/J8_02_MethodReferences", "Method references", "Four forms — static, unbound, bound and constructor — each a shorthand for a lambda."),
 ("java8/J8_03_DefaultAndStaticMethods", "Default and static interface methods", "Interfaces can now carry behaviour: default methods that implementers inherit, and static factory methods."),
 ("java8/J8_04_StreamBasics", "Streams: filter, map, collect", "Build a pipeline, then run it with a terminal operation. The laziness demo shows that elements flow one at a time and processing stops as soon as `findFirst` is satisfied. See [Ch 07]({streams})."),
 ("java8/J8_05_Collectors", "Collectors: group, partition, join, map", "The collectors that do most real work. `TreeMap::new` keeps the output order stable. See [Ch 08]({collectors})."),
 ("java8/J8_06_FlatMapAndReduce", "flatMap, reduce and primitive streams", "`flatMap` flattens nested lists; `mapToInt` avoids boxing; `reduce` folds values together."),
 ("java8/J8_07_Optional", "Optional", "A return type that says \"there may be no result\". Note that `orElse` evaluates its argument even when a value is present — `orElseGet` does not. See [Ch 09]({optional})."),
 ("java8/J8_08_DateTime", "java.time", "Immutable types for dates, times, durations and time zones. See [Ch 10]({time})."),
 ("java8/J8_09_MapApi", "The new Map methods", "`getOrDefault`, `putIfAbsent`, `merge`, `compute*` and `replaceAll` replace most get-check-put code."),
 ("java8/J8_10_CollectionApi", "removeIf, replaceAll and Comparator chains", "Bulk operations on collections, and comparators built by composition instead of hand-written `compare` methods."),
 ("java8/J8_11_StringsAndBase64", "String.join, StringJoiner and Base64", "Small additions that removed a lot of utility code."),
 ("java8/J8_12_ParallelStreams", "Parallel streams", "Same result for CPU-bound work — but only worthwhile for large data, and never for blocking I/O."),
 ("java8/J8_13_StreamSources", "Where streams come from", "Collections, arrays, ranges, and generated or iterated sequences."),
])
version_page("java-9-11.md", "Java 9 to 11 by Example", "Java 9–11 by example", """
Java 9 brought collection factories and stream additions; Java 10 added `var`; Java 11 — the first LTS after
Java 8 — added string and file helpers and the standard HTTP client.
""", [
 ("java9to11/J09_CollectionFactories", "Java 9 · List.of, Set.of, Map.of", "Compact, **immutable** collections that reject `null` and duplicate set elements. See [Ch 11]({j9})."),
 ("java9to11/J09_StreamAdditions", "Java 9 · takeWhile, dropWhile, iterate, ofNullable", "`takeWhile` stops at the first element that fails; `filter` checks them all."),
 ("java9to11/J09_OptionalAdditions", "Java 9 · Optional.or, ifPresentOrElse, stream", "Chain fallbacks with `or`, and flatten a list of Optionals with `Optional::stream`."),
 ("java9to11/J09_PrivateInterfaceMethods", "Java 9 · private interface methods", "Default methods can share a helper without exposing it."),
 ("java9to11/J09_TryWithResources", "Java 9 · try-with-resources on existing variables", "Effectively final resources can be listed directly; they close in reverse order."),
 ("java9to11/J10_Var", "Java 10 · var", "Type inference for local variables. Beware the bare diamond: `var list = new ArrayList<>()` is an `ArrayList<Object>`."),
 ("java9to11/J10_CopyOf", "Java 10 · List.copyOf and unmodifiable collectors", "A copy is a snapshot; `unmodifiableList` is a view that still reflects changes. See [Ch 22]({immut})."),
 ("java9to11/J11_StringMethods", "Java 11 · isBlank, strip, lines, repeat", "`strip()` understands Unicode whitespace; `trim()` only ASCII."),
 ("java9to11/J11_Files", "Java 11 · Files.readString and writeString", "Read or write a whole file in one call, as UTF-8."),
 ("java9to11/J11_PredicateNotAndVarLambdas", "Java 11 · Predicate.not and var in lambdas", "`Predicate.not(String::isBlank)` keeps method references readable."),
 ("java9to11/J11_HttpClient", "Java 11 · the HTTP client", "Synchronous and asynchronous calls. A tiny local server stands in for a real API, so this runs offline. Create one client and reuse it; set both timeouts. See [Ch 40]({http})."),
])
version_page("java-12-17.md", "Java 12 to 17 by Example", "Java 12–17 by example", """
The releases leading to Java 17 LTS reshaped everyday code: switch expressions, text blocks, records, pattern
matching for `instanceof`, and sealed classes.
""", [
 ("java12to17/J12_Teeing", "Java 12 · Collectors.teeing", "Two collectors in one pass, combined at the end."),
 ("java12to17/J12_StringIndentTransform", "Java 12 · String.indent and transform", "`transform` lets you chain your own functions onto a string."),
 ("java12to17/J14_SwitchExpressions", "Java 14 · switch expressions", "Arrows, several labels per case, no fall-through, and `yield` for blocks. Over an enum, the compiler checks every constant is handled. See [Ch 12]({j14})."),
 ("java12to17/J14_HelpfulNullPointers", "Java 14 · helpful NullPointerExceptions", "The message names exactly which call returned `null` — this is the JVM's real output."),
 ("java12to17/J15_TextBlocks", "Java 15 · text blocks", "Multi-line strings for JSON, SQL and templates. A trailing `\\` joins lines."),
 ("java12to17/J16_Records", "Java 16 · records", "Data carriers with generated `equals`, `hashCode`, `toString` and accessors. Validate in the compact constructor, and copy collections to keep the record immutable."),
 ("java12to17/J16_PatternMatchingInstanceof", "Java 16 · pattern matching for instanceof", "Test and cast in one step; the binding is usable in the same condition. See [Ch 13]({patterns})."),
 ("java12to17/J16_StreamToListAndMapMulti", "Java 16 · Stream.toList and mapMulti", "`toList()` returns an **unmodifiable** list — unlike `collect(Collectors.toList())`."),
 ("java12to17/J17_SealedClasses", "Java 17 · sealed classes", "A closed set of subtypes. The compiler rejects any class not in `permits`. On Java 21 a pattern switch over it needs no `default` — see the next page."),
 ("java12to17/J17_RandomGenerator", "Java 17 · RandomGenerator", "One interface over many random-number algorithms."),
])
version_page("java-18-21.md", "Java 18 to 21 by Example", "Java 18–21 by example", """
Java 21 LTS is the biggest release since Java 8: virtual threads, pattern matching for `switch`, record patterns
and sequenced collections are all **final**.

!!! info "Preview features are not shown here"
    Java 21 also previewed structured concurrency, scoped values, unnamed patterns and string templates. Their
    APIs changed afterwards (and string templates were withdrawn), so they are covered in their current form in
    [Chapter 32](../04-concurrency/32-structured-concurrency.md), [Chapter 33](../04-concurrency/33-scoped-values.md),
    [Chapter 14]({j21}) and [Chapter 15](../02-language/15-string-templates-postmortem.md).
""", [
 ("java18to21/J18_Utf8Default", "Java 18 · UTF-8 by default", "File and string APIs now default to UTF-8 on every operating system."),
 ("java18to21/J19_SizedMapsAndFutureState", "Java 19 · HashMap.newHashMap and Future.state", "`newHashMap(n)` takes the number of **entries**, not the capacity. `state()`, `resultNow()` and `exceptionNow()` inspect a finished future."),
 ("java18to21/J21_VirtualThreads", "Java 21 · virtual threads", "Ten thousand blocking tasks finish in under a second on virtual threads, against 25 seconds on a pool of 200 platform threads. Never pool virtual threads — limit resources with a `Semaphore` instead. See [Ch 31]({vt})."),
 ("java18to21/J21_PatternMatchingSwitch", "Java 21 · pattern matching for switch", "Switch on types, add guards with `when`, handle `null` explicitly — and over a sealed type, omit `default` so the compiler checks every case. See [Ch 13]({patterns})."),
 ("java18to21/J21_RecordPatterns", "Java 21 · record patterns", "Destructure records — including nested ones — directly in a `case` or `instanceof`."),
 ("java18to21/J21_SequencedCollections", "Java 21 · sequenced collections", "`getFirst`, `getLast`, `reversed()`, `putFirst` — one vocabulary for ordered collections. `reversed()` is a live view, and `HashMap` is not sequenced. See [Ch 21]({seq})."),
 ("java18to21/J21_NewStringAndMathMethods", "Java 21 · Math.clamp and new String methods", "Small additions: `Math.clamp`, `StringBuilder.repeat`, ranged `indexOf`, `splitWithDelimiters`, `Character.isEmoji`."),
])


def run_command(path):
    first = (EX / f"{path}.java").read_text().splitlines()[0]
    flags = first.split("run:", 1)[1].strip() + " " if first.startswith("// run:") else ""
    return f"java {flags}{pathlib.Path(path).name}.java"


def anchor(n, title):
    return f"{n}-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def sub(text):
    """Replace only known {chapter} placeholders — Mermaid also uses braces."""
    for key, link in CH.items():
        text = text.replace("{" + key + "}", link)
    return text


def render(page):
    out = ["---", f"title: {page['title']}", "status: review", "---", "", f"# {page['title']}", ""]
    out.append(sub(page["intro"].strip()))
    out += ["", "!!! tip \"Every example here is real\"",
            "    Each program below compiles and runs as shown, and the output is exactly what it printed on JDK 21.",
            "    Copy one into a file and run it with the command shown underneath — no build tool needed.", ""]
    for n, (path, title, text) in enumerate(page["examples"], 1):
        name = pathlib.Path(path).name
        out += ["---", "", f"## {n}. {title}", "", sub(text), "",
                f'```java title="{name}.java"', f'--8<-- "code/examples/{path}.java"', "```", "",
                '```text title="Output"', f'--8<-- "code/examples/{path}.out"', "```", "",
                f"<small>Run it: `{run_command(path)}`</small>", ""]
    if page.get("outro"):
        out += ["---", "", sub(page["outro"].strip()), ""]
    return "\n".join(out)


def main():
    OUT.mkdir(exist_ok=True)
    total = 0
    for page in PAGES:
        for path, *_ in page["examples"]:
            for ext in (".java", ".out"):
                if not (EX / f"{path}{ext}").exists():
                    raise SystemExit(f"missing {path}{ext} — run tools/run-examples.py first")
        (OUT / page["file"]).write_text(render(page))
        total += len(page["examples"])
    rows = "\n".join(f"| [{p['title']}]({p['file']}) | {len(p['examples'])} |" for p in PAGES)
    (OUT / "index.md").write_text(f"""---
title: Examples
status: review
---

# Examples

Short, complete programs you can run — **{total} examples**, each shown with the exact output it produced.
The chapters explain *why*; these pages show *what happens*.

!!! tip "Java 8 examples are in the Java 8 tab"
    [Java 8 by Example](java-8.md) is listed under the **[Java 8](../java8/index.md)** tab, next to the
    Java 8 chapters and interview workbook. It is included in the table below for completeness.

| Page | Examples |
|---|---|
{rows}

## How to run an example

Every example is a single file. With JDK 21 or later, no build tool is needed:

```bash
java HashSpreading.java
```

The sources live in `code/examples/` in this repository. A few examples look inside JDK classes and need an
`--add-opens` flag; the exact command is printed under each one.

!!! note "About the captured output"
    Outputs were captured on JDK 21 in a single-core container. Timings and the numbers in the race-condition
    demos vary between runs; where that matters, the page says so.
""")
    print(f"wrote {len(PAGES)} pages + index · {total} examples")


if __name__ == "__main__":
    main()
