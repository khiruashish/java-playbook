"""Chapter 28 — Executors. Source: docs/04-concurrency/28-executors.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 28 · Executors"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Executors",
         kicker="Concurrency · Chapter 28",
         body='<p class="sub">Thread pools that don\'t run out of memory, explode, or silently stop — and where virtual threads change the advice.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-eight: executors.",
             "An executor separates what to run from which thread runs it. But the convenient factory methods have defaults that cause real production incidents. Let's see three.",
         ]),

    dict(title="Three incidents, three defaults",
         kicker="The problem",
         body=code('''
Executors.newFixedThreadPool(20);       // 1. UNBOUNDED queue → grows until the heap is gone
Executors.newCachedThreadPool();        // 2. UNBOUNDED threads → a burst creates thousands

scheduler.scheduleAtFixedRate(this::reconcile, 0, 1, TimeUnit.HOURS);
// 3. reconcile() threw once → the schedule is cancelled. No log line. For a week.''',
                   title="Defaults.java", size=26)
              + frag('<p class="callout">Each is the factory method working exactly as documented.</p>', 1),
         narration=[
             "Three incidents. A fixed thread pool sits on an unbounded queue, so when producers outpace the workers, the queue grows until memory runs out. "
             "A cached thread pool has unbounded threads, so a burst of slow tasks creates thousands of platform threads. "
             "And a scheduled job threw an exception once, which cancelled every future run, with no log line. Nobody noticed for a week.",
             "Each one is the factory method working exactly as documented.",
         ]),

    dict(title="Core, then queue, then more threads",
         kicker="The counterintuitive ordering",
         body=flow(["Running < **core**?\n→ new core thread", "Queue accepts?\n→ **queue it**", "Running < **max**?\n→ new extra thread", "→ **reject**"], step_start=0)
              + frag('<p class="callout">With an <b>unbounded</b> queue, the queue never refuses — so <code>maximumPoolSize</code> is <b>never reached</b>. '
                     'Core 10, max 100, unbounded queue = exactly 10 threads forever.</p>', 4),
         narration=[
             "ThreadPoolExecutor has a core size, a maximum size, and a queue. When a task arrives, if fewer than core threads are running, it starts one.",
             "Otherwise it tries to queue the task.",
             "Only if the queue refuses does it start extra threads, up to the maximum.",
             "And past that, it rejects the task.",
             "Most people assume it grows to the maximum before queuing. It's the opposite. So with an unbounded queue, the queue never refuses, and the maximum is never reached. "
             "A pool with core ten, max a hundred, and an unbounded queue runs exactly ten threads forever while its queue grows.",
         ]),

    dict(title="Build it yourself",
         kicker="Worked example",
         body=code('''
int cores = Runtime.getRuntime().availableProcessors();   // respects container limits
ThreadPoolExecutor pricingPool = new ThreadPoolExecutor(
    cores, cores,                                    // CPU work gains nothing from more
    0L, TimeUnit.MILLISECONDS,
    new ArrayBlockingQueue<>(500),                   // BOUNDED
    Thread.ofPlatform().name("pricing-", 0).factory(),
    new ThreadPoolExecutor.CallerRunsPolicy());      // backpressure, not rejection''', title="PricingPool.java", size=26)
              + frag(table(["Rejection policy", "On saturation"], [
                    ["`AbortPolicy` (default)", "Throws `RejectedExecutionException`"],
                    ["`CallerRunsPolicy`", "**The submitter runs it** — natural backpressure"],
                    ["`Discard` / `DiscardOldest`", "Silently drops work"],
                ], cls="sm"), 1),
         narration=[
             "For a production service, construct ThreadPoolExecutor directly. Core equals max at the core count, because CPU work gains nothing from more threads. A bounded queue caps memory. "
             "A named thread factory makes thread dumps readable. availableProcessors respects container CPU limits since Java 10.",
             "And choose a rejection policy. The default throws. The discard policies silently lose work. CallerRunsPolicy is the useful one: when the pool is full, the submitting thread runs the task itself, which slows producers down automatically.",
         ]),

    dict(title="I/O-bound work: virtual threads + a Semaphore",
         kicker="Sizing",
         body=code('threads = cores × (1 + wait / compute)        // 8 cores, 5 ms compute, 95 ms wait → 160',
                   lang="text", title="The classic formula", size=26)
              + code('''
private final Semaphore warehouseLimit = new Semaphore(40);    // what the downstream tolerates

try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Sku sku : skus) {
        executor.submit(() -> {
            warehouseLimit.acquire();
            try { return warehouseClient.statusFor(sku); }
            finally { warehouseLimit.release(); }
        });
    }
}''', title="IoBound.java — Java 21+", step=1, size=25),
         narration=[
             "For I/O-bound work, the classic sizing formula says cores times one plus wait over compute. Eight cores, five milliseconds of compute, ninety-five of waiting, gives a hundred and sixty threads.",
             "On Java 21 and later, don't do that. Use virtual threads, and bound the real constraint directly with a Semaphore. "
             "The formula was always an indirect way of expressing a downstream limit through thread economics. A semaphore says it directly, and virtual threads remove the reason thread count mattered.",
         ]),

    dict(title="Where exceptions go",
         kicker="execute vs submit",
         body=code('''
pool.execute(() -> { throw new IllegalStateException("boom"); });   // → UncaughtExceptionHandler
pool.submit(()  -> { throw new IllegalStateException("boom"); });   // → captured in the Future — invisible

try {
    Receipt r = future.get(10, TimeUnit.SECONDS);
} catch (ExecutionException e) {
    log.error("dispatch failed", e.getCause());      // the real exception
} catch (TimeoutException e) {
    future.cancel(true);
}''', title="ExceptionVisibility.java", size=25),
         narration=[
             "Where do exceptions go? With execute, an exception reaches the thread's uncaught exception handler, so it's logged, at least. "
             "With submit, it's captured inside the returned Future, and if you discard that Future, which happens a lot, the failure is never seen. "
             "So consume every Future with get and a timeout, use execute for fire-and-forget work, or wrap tasks in a try-catch that logs.",
         ]),

    dict(title="Scheduled tasks die silently",
         kicker="Worked example",
         body=code('''
scheduler.scheduleAtFixedRate(this::reconcile, 0, 1, TimeUnit.HOURS);   // ✗ one throw stops it forever

scheduler.scheduleAtFixedRate(() -> {
    try { reconcile(); }
    catch (Exception e) { log.error("reconciliation failed; will retry next run", e); }
}, 0, 1, TimeUnit.HOURS);                                                 // ✓ the schedule survives''',
                   title="ScheduledSafe.java", size=25)
              + frag(table(["Method", "Timing"], [
                    ["`scheduleAtFixedRate`", "Start-to-start — slow runs bunch up"],
                    ["`scheduleWithFixedDelay`", "End-to-start — a guaranteed gap"],
                ], cls="sm"), 1),
         narration=[
             "Here's the silent schedule fix. If any run of a scheduled task throws, every later run is suppressed, and the exception sits in a ScheduledFuture nobody holds. "
             "So catch everything inside the task, log it, and the schedule survives to retry next time.",
             "And know the difference between fixed rate, which is start to start, so slow runs bunch up, and fixed delay, which guarantees a gap between the end of one run and the start of the next.",
         ]),

    dict(title="Bulkheads and shutdown",
         kicker="Worked examples",
         body=code('''
ExecutorService paymentPool = boundedPool("payment", 10, 100);   // a slow vendor saturates
ExecutorService vendorPool  = boundedPool("vendor", 20, 200);    // only its own pool
// with virtual threads: separate Semaphores instead of separate pools''', title="Bulkheads.java", size=25)
              + code('''
pool.shutdown();                                         // stop accepting
if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
    pool.shutdownNow();                                  // interrupt running tasks
}
try (ExecutorService p = Executors.newVirtualThreadPerTaskExecutor()) { ... }   // Java 19: close()''',
                     title="Shutdown.java", step=1, size=25),
         narration=[
             "Use bulkheads. Give each downstream dependency its own pool, so a slow vendor API saturates the vendor pool and payments keep flowing. "
             "With virtual threads, you get the same isolation from separate semaphores.",
             "And shut down properly. shutdown stops accepting work. Await termination with a timeout, then shutdownNow, which interrupts running tasks. That only helps if they respond to interruption. "
             "Since Java 19, short-lived executors work in try-with-resources.",
         ]),

    dict(title="Inside ThreadPoolExecutor",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("The ctl field", "Run state (3 bits) + worker count (29 bits) in **one AtomicInteger** — checked and updated in a single CAS.", "indigo", 0)
              + card("The worker loop", "Non-core threads exit after `keepAliveTime` idle. A task throwing via `execute` **kills its worker** — constant churn on failure.", "cyan", 1)
              + card("Why cached pools explode", "`SynchronousQueue` has no capacity. No idle thread → refuse → new thread, up to `Integer.MAX_VALUE`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Inside ThreadPoolExecutor, a field called ctl packs the run state and the worker count into one atomic integer, so both are checked and updated in a single compare-and-swap, with no global lock.",
             "Each worker loops, taking tasks from the queue. Non-core threads exit after sitting idle, which is how the pool shrinks. And a task that throws through execute kills its worker, which is replaced. Harmless, but failing tasks cause constant thread churn.",
             "And the cached pool explosion comes from SynchronousQueue, which has no capacity at all. If no thread is idle, the offer fails, and the pool starts a new thread, potentially without limit.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Construct `ThreadPoolExecutor` directly",
                         "Bounded queues; named thread factories",
                         "`CallerRunsPolicy` for backpressure",
                         "Virtual threads + `Semaphore` for I/O",
                         "try/catch inside every scheduled task",
                         "Bulkhead each downstream dependency"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`newFixedThreadPool` / `newCachedThreadPool` in services",
                         "Discard the `Future` from `submit`",
                         "Expect `max` to matter with an unbounded queue",
                         "One shared pool for every dependency",
                         "Skip `shutdown` and `awaitTermination`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Construct ThreadPoolExecutor directly, with a bounded queue and a named thread factory. Use CallerRunsPolicy for backpressure. Use virtual threads with a semaphore for I/O. "
             "Put a try-catch inside every scheduled task. And bulkhead each downstream dependency.",
             "Never use the fixed or cached factory methods in a service. Never discard the Future from submit. Never expect the maximum size to matter with an unbounded queue. "
             "Never share one pool across every dependency. And never skip a proper shutdown.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 28 · Executors",
         body=bullets(["Core → **queue** → extra threads → reject",
                       "Bounded queue, named threads, a chosen rejection policy",
                       "`submit` hides exceptions in the `Future`",
                       "One throw cancels a schedule — catch inside",
                       "I/O-bound on 21+: **virtual threads + a Semaphore**",
                       "Next: **Ch 29 · CompletableFuture**"], cls="bullets recap"),
         narration=[
             "To recap. A pool fills core threads, then the queue, then extra threads, then rejects. So bound the queue, name the threads, and choose a rejection policy. "
             "submit hides exceptions inside the Future. One exception cancels a schedule, so catch inside the task. And for I/O-bound work on Java 21, use virtual threads with a semaphore.",
             "Next is chapter twenty-nine: CompletableFuture. Thanks for watching.",
         ]),
]
