"""Chapter 31 — Virtual Threads. Source: docs/04-concurrency/31-virtual-threads.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 31 · Virtual Threads"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Virtual Threads",
         kicker="Concurrency · Chapter 31 · Java 21",
         body='<p class="sub">Blocking syntax at non-blocking cost — what changes, what doesn\'t, and the four mistakes teams make adopting them.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-one: virtual threads, final in Java 21.",
             "Virtual threads let you keep writing plain blocking code, while the thread doing the blocking costs almost nothing. "
             "But they change what's scarce in your system, and that catches teams out.",
         ]),

    dict(title="The old dilemma",
         kicker="The problem",
         body=code('''
private final ExecutorService pool = Executors.newFixedThreadPool(200);   // ~200 MB of stack
pool.submit(() -> vendorClient.send(order));    // 199.9 ms of every 200 ms: parked, holding an OS thread''',
                   title="PooledDispatcher.java", size=24)
              + '<div class="grid2">'
              + card("Go reactive", "Scales beautifully — and costs readable stack traces, debuggability, `try`/`catch` and `for` loops.", "fuchsia", 1)
              + card("Accept the ceiling", "200 concurrent calls, and buy more machines.", "amber", 1)
              + "</div>",
         narration=[
             "A dispatcher calls a vendor API that takes two hundred milliseconds. A pool of two hundred platform threads already reserves around two hundred megabytes of stack, and caps throughput at two hundred calls. "
             "Each thread spends almost all its time parked, holding an OS thread that does nothing.",
             "Before Java 21, you had two choices. Go reactive, which scales but costs you readable stack traces, debugging, and plain loops and try-catch. Or accept the ceiling and buy more machines. Virtual threads remove the dilemma.",
         ]),

    dict(title="M:N, and unmounting",
         kicker="Mental model",
         body=flow(["Virtual thread **mounted** on a carrier", "Blocks on I/O, `sleep`, a lock, a queue", "Stack copied to the **heap** — carrier freed",
                    "Ready → copied back, resumes **on the next line**"], step_start=0)
              + frag('<p class="callout">From the code\'s point of view, <code>socket.read()</code> simply blocked and returned. '
                     '<b>Blocking syntax, non-blocking cost.</b></p>', 4),
         narration=[
             "A platform thread maps one-to-one onto an OS thread. A virtual thread is a Java object, scheduled by the JVM onto a small pool of carrier threads. Millions onto a handful.",
             "The key operation is unmounting. When a virtual thread blocks on something the JDK understands, like a socket read, sleep, a lock or a blocking queue,",
             "its stack is copied to the heap, and the carrier is released to run another virtual thread.",
             "When the data arrives, the stack is copied back onto some carrier, and execution resumes on the very next line.",
             "From the code's point of view, nothing happened. The read just blocked and returned. That's the whole design goal: blocking syntax, non-blocking cost.",
         ]),

    dict(title="What changes",
         kicker="Platform vs virtual",
         body=table(["", "Platform thread", "Virtual thread"], [
                    ["Backed by", "An OS thread", "A heap object"],
                    ["Stack", "~1 MB reserved", "Grows and shrinks on the heap"],
                    ["Creation", "Tens–hundreds of µs", "Sub-microsecond"],
                    ["Practical count", "Thousands", "**Millions**"],
                    ["Pooling", "Essential", "**Harmful**"],
                    ["CPU-bound work", "Same", "Same — no benefit"],
                ], step_per_row=None, cls="sm"),
         narration=[
             "Here's what changes. A platform thread is an OS thread with about a megabyte of reserved stack. A virtual thread is a heap object whose stack grows and shrinks as needed. "
             "Creating one is sub-microsecond, so you can have millions instead of thousands. Pooling, essential for platform threads, is harmful for virtual ones. "
             "And for CPU-bound work, nothing changes at all.",
         ]),

    dict(title="The dispatcher, rewritten",
         kicker="Worked example",
         body=code('''
public void dispatchAll(List<Order> orders) {
    try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
        for (Order order : orders) {
            executor.submit(() -> vendorClient.send(order));     // unchanged blocking code
        }
    }   // close() waits for every task (Java 19+)
}''', title="VirtualDispatcher.java", size=27)
              + frag('<p class="callout">Not a pool — one virtual thread per task. Same code, same stack traces, same <code>try</code>/<code>catch</code>. '
                     'The 200 ms of waiting no longer holds an OS thread.</p>', 1),
         narration=[
             "Here's the dispatcher with virtual threads. newVirtualThreadPerTaskExecutor, in a try-with-resources. Ten thousand orders means ten thousand concurrent virtual threads. "
             "The blocking send call is unchanged. And close waits for every task, so the method doesn't return early.",
             "That executor isn't a pool. It creates a virtual thread per task and throws it away. Same code, same stack traces, same try-catch. The waiting just no longer holds an OS thread.",
         ]),

    dict(title="Mistake 1: pooling them",
         kicker="Pool the resource, not the thread",
         body=code('''
Executors.newFixedThreadPool(200, Thread.ofVirtual().factory());   // ✗ reintroduces the ceiling

private final Semaphore vendorLimit = new Semaphore(50);           // ✓ the real constraint
vendorLimit.acquire();
try { vendorClient.send(order); } finally { vendorLimit.release(); }''', title="Semaphore.java", size=26)
              + frag('<p class="callout">10,000 virtual threads exist; 50 are in the vendor call; the rest park on the semaphore at almost no cost.</p>', 1),
         narration=[
             "Mistake one: pooling them. A fixed pool of two hundred virtual threads caps concurrency at two hundred, whatever the threads are made of. Pooling exists because platform threads are expensive, and virtual ones aren't.",
             "Pool the scarce resource instead. If the vendor tolerates fifty concurrent calls, say so with a semaphore. Ten thousand virtual threads exist, fifty are in the call, and the rest wait on the semaphore at almost no cost.",
         ]),

    dict(title="Mistakes 2–4",
         kicker="Worked examples",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("The DB is still the limit", "20 connections admit 20 queries. The other 9,980 threads just **queue cheaply**. Gains stop at your slowest shared resource.", "indigo", 0)
              + card("ThreadLocal multiplies", "An 8 KB buffer per thread: 1.6 MB at 200 threads, **8 GB at a million**. Prefer `ScopedValue` (Ch 33).", "fuchsia", 1)
              + card("CPU work gains nothing", "They multiplex **waiting**, not computing. Is the task waiting or working? Working scales with cores.", "amber", 2)
              + "</div>",
         narration=[
             "Mistake two: expecting a linear speedup. Virtual threads remove the thread ceiling and expose whatever was behind it. A connection pool of twenty still runs twenty queries. The other threads just queue cheaply. "
             "Throughput is bounded by your slowest shared resource.",
             "Mistake three: ThreadLocal. An eight-kilobyte buffer per thread was one and a half megabytes with two hundred threads. With a million virtual threads it's eight gigabytes. "
             "ThreadLocal still works, but audit anything heavy, and prefer scoped values for request context.",
             "Mistake four: CPU-bound work. Virtual threads multiplex waiting, not computing. Ten thousand of them doing arithmetic still share the same cores. "
             "Ask: is the task waiting or working? Waiting scales with virtual threads. Working scales with cores.",
         ]),

    dict(title="Pinning",
         kicker="Internals",
         body=table(["Pins the carrier", "Status"], [
                    ["Blocking inside `synchronized`", "**Fixed in Java 24** (JEP 491)"],
                    ["`Object.wait()`", "**Fixed in Java 24**"],
                    ["Native frames (JNI)", "Still pins"],
                    ["Blocking during class initialisation", "Still pins"],
                ], step_per_row=0, cls="pairs")
              + frag(code('jfr print --events jdk.VirtualThreadPinned recording.jfr', lang="bash", title="Detect it", size=25), 4),
         narration=[
             "A pinned virtual thread blocks its carrier instead of unmounting. And with only a few carriers, a few pinned threads can stall everything. On Java 21 to 23, the big cause was blocking inside synchronized. "
             "Java 24 fixed that, so the old advice to replace synchronized with ReentrantLock is obsolete there.",
             "Object dot wait was fixed too.",
             "Native frames from JNI calls still pin.",
             "And so does blocking during class initialisation.",
             "To find pinning, record with Java Flight Recorder and print the VirtualThreadPinned events.",
         ]),

    dict(title="Under the hood",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Own scheduler", "A dedicated FIFO `ForkJoinPool` — not the common pool — with one carrier per core by default.", "indigo", 0)
              + card("Freeze and thaw", "Stacks live on the heap as chunks: tiny for shallow tasks, GC-able — but copying costs CPU per frame.", "cyan", 1)
              + card("Thread dumps", "`jstack` won't show them. Use `jcmd <pid> Thread.dump_to_file -format=json`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Under the hood, virtual threads run on their own FIFO ForkJoinPool, separate from the common pool, with one carrier per core by default. The defaults are right for nearly every app.",
             "A virtual thread's stack lives on the heap. Blocking freezes live frames into a heap chunk, and resuming thaws them back. So shallow tasks cost a few hundred bytes, and stacks are garbage-collectable. "
             "But deep recursion in a task that blocks often costs more than it looks.",
             "And jstack doesn't show virtual threads. Use jcmd Thread dot dump to file, in JSON format, which also groups threads by the structured concurrency scope that created them.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`newVirtualThreadPerTaskExecutor()` in try-with-resources",
                         "Write plain blocking code",
                         "Limit the scarce resource with a `Semaphore`",
                         "Audit heavy `ThreadLocal`s; prefer `ScopedValue`",
                         "Platform pools for CPU-bound work",
                         "Check connection pools and downstream limits"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Pool virtual threads",
                         "`ThreadLocal` caches of large objects",
                         "Assume a throughput win without measuring",
                         "Virtual threads for CPU-bound parallelism",
                         "Keep Java 21 pinning workarounds on 24+ blindly"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use the per-task executor in try-with-resources. Write plain blocking code. Limit the scarce resource with a semaphore. Audit heavy ThreadLocals and prefer scoped values. "
             "Keep CPU-bound work on platform pools. And review your connection pools and downstream limits, because they become the visible ceiling.",
             "Never pool virtual threads. Never use ThreadLocal as a cache for large objects. Never assume a throughput win without checking what actually limits you. "
             "Never use them for CPU-bound parallelism. And don't carry Java 21 pinning workarounds into Java 24 without knowing why they're there.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 31 · Virtual Threads",
         body=bullets(["Blocking code, **non-blocking cost** — the stack moves to the heap",
                       "Never pool them; **limit the resource** with a Semaphore",
                       "They expose the real bottleneck — usually the database",
                       "Waiting scales; computing doesn't",
                       "`synchronized` pinning is fixed in Java 24",
                       "Next: **Ch 32 · Structured Concurrency**"], cls="bullets recap"),
         narration=[
             "To recap. Virtual threads give you blocking code at non-blocking cost, by moving the stack to the heap while it waits. Never pool them, and limit the scarce resource with a semaphore instead. "
             "They expose your real bottleneck, usually the database. Waiting scales, computing doesn't. And synchronized pinning is fixed in Java 24.",
             "Next is chapter thirty-two: structured concurrency. Thanks for watching.",
         ]),
]
