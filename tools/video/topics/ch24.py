"""Chapter 24 — Threading Fundamentals. Source: docs/04-concurrency/24-threading-fundamentals.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 24 · Threading Fundamentals"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Threading Fundamentals",
         kicker="Concurrency · Chapter 24",
         body='<p class="sub">What a thread is and costs, how to stop one (you ask), and why its exceptions vanish without a trace.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-four, the start of the concurrency section: threading fundamentals.",
             "Almost nobody writes new Thread in application code any more. Executors and virtual threads sit on top. But every abstraction leaks. "
             "Thread dumps show states, interruption flows through pool APIs, and a thread that dies silently takes your background job with it.",
         ]),

    dict(title="Own stack, shared heap",
         kicker="Mental model",
         body='<div class="grid2">'
              + card("Each thread owns", "Its **stack** and program counter. Local variables are private — no protection needed.", "indigo", 0)
              + card("All threads share", "The **heap**: orders, inventory, the catalogue map. That's where all the danger lives.", "fuchsia", 1)
              + "</div>"
              + frag('<p class="callout">Why bother? Dispatching 500 orders at 200 ms each takes <b>100 seconds</b> sequentially — '
                     'with the CPU idle, waiting on sockets.</p>', 2),
         narration=[
             "A process owns memory, and a thread is one path of execution through it. Each thread has its own stack, so local variables are private and need no protection.",
             "But the heap is shared by every thread. That's where all the danger lives.",
             "Why have threads at all? Sending five hundred orders to vendors at two hundred milliseconds each takes a hundred seconds one by one, and the CPU sits idle the whole time, waiting on network sockets. "
             "A thread lets the program do something else while one path waits.",
         ]),

    dict(title="Lifecycle states",
         kicker="Mental model",
         body=table(["State", "Meaning"], [
                    ["`NEW`", "Constructed, not started"],
                    ["`RUNNABLE`", "Running, ready — **or blocked in OS-level I/O**"],
                    ["`BLOCKED`", "Waiting to enter a `synchronized` region"],
                    ["`WAITING` / `TIMED_WAITING`", "`wait()`, `join()`, `park()`, `sleep(n)`"],
                    ["`TERMINATED`", "`run()` returned or threw"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">A service waiting on 200 HTTP calls shows <b>200 RUNNABLE threads</b>. '
                     '<code>BLOCKED</code> means contending for a Java monitor — nothing else.</p>', 5),
         narration=[
             "A thread moves through six states. NEW, before start is called.",
             "RUNNABLE means running or ready to run. But it also covers a thread blocked in operating-system I/O, like reading a socket.",
             "BLOCKED means waiting to enter a synchronized block.",
             "WAITING and TIMED_WAITING mean waiting for another thread, through wait, join, park or sleep.",
             "And TERMINATED, once run has returned or thrown.",
             "That second row surprises people reading thread dumps. A service doing nothing but waiting on two hundred HTTP calls shows two hundred RUNNABLE threads. "
             "BLOCKED only ever means contending for a Java lock.",
         ]),

    dict(title="Creating and starting",
         kicker="Core API",
         body=code('''
Thread t = Thread.ofPlatform()               // Java 21 builder — named, configurable
                 .name("dispatch-" + order.id())
                 .start(() -> vendorClient.send(order));
t.join(Duration.ofSeconds(5));               // bounded wait (Java 19)''', title="ParallelDispatcher.java", size=27)
              + code('''
new Thread(task, "worker-1").start();   // running on worker-1
new Thread(task, "worker-2").run();     // running on main — just a method call!''', title="StartVsRun.java", step=1, size=27)
              + frag('<p class="callout">Prefer <code>Runnable</code> over extending <code>Thread</code>. '
                     '<code>Thread.stop</code>, <code>suspend</code>, <code>resume</code> throw since Java 20 — they were never safe.</p>', 2),
         narration=[
             "Since Java 21, create threads with a builder. Give it a name, then start it with a task. join with a duration waits, but not forever.",
             "A classic bug: calling run instead of start. run is just an ordinary method, so the task runs on the current thread. No concurrency, and no error, which is what makes it a real bug.",
             "Prefer passing a Runnable over extending Thread. And Thread dot stop, suspend and resume throw since Java 20. "
             "stop threw an exception at an arbitrary point, releasing every lock with data half-updated. It was never safe.",
         ]),

    dict(title="Stopping a thread: you ask",
         kicker="Cooperative interruption",
         body=code('''
public void run() {
    try {
        while (!Thread.currentThread().isInterrupted()) {   // check 1: between iterations
            Order order = queue.take();                     // check 2: while blocked → throws
            vendorClient.send(order);
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();                 // restore the flag
    }
}

worker.interrupt();
worker.join(Duration.ofSeconds(5));''', title="DispatchWorker.java", size=25),
         narration=[
             "There's no way to kill a thread. You ask it to stop, and it cooperates. You call interrupt, which sets a flag. "
             "This worker checks twice. The loop condition catches interruption between orders. And take throws InterruptedException if it's interrupted while waiting for the queue. "
             "A worker that does only one of these either ignores interruption while it waits, or spins. Then shut down with interrupt, and a bounded join.",
         ]),

    dict(title="The swallowed interrupt",
         kicker="The most common concurrency bug",
         body='<div class="grid2 start">'
              + code('''
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // ignored  ← the cancellation is destroyed
}''', title="✗ SwallowedInterrupt.java", size=25)
              + frag(code('''
void dispatch() throws InterruptedException {
    Thread.sleep(1000);   // propagate (preferred)
}

catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    return;               // restore AND stop
}''', title="✓ Two correct responses", size=25), 1)
              + "</div>"
              + frag('<p class="callout">A blocking method that throws <code>InterruptedException</code> <b>clears the flag</b>. '
                     'Swallow it, and a shutdown that should take milliseconds hangs until a timeout.</p>', 2),
         narration=[
             "This is the most common concurrency bug in enterprise Java, usually written by an IDE quick-fix. Catch InterruptedException and ignore it.",
             "The fix: propagate it, which is preferred. Or, if you can't, restore the flag by calling interrupt on the current thread, and stop working. Restoring without stopping is only half a fix.",
             "Here's why it matters. When a blocking method throws InterruptedException, it clears the interrupt flag. "
             "Swallow it and all evidence of the cancellation request is gone, so every caller carries on. A shutdown that should take milliseconds hangs until something times out.",
         ]),

    dict(title="How interruption actually works",
         kicker="Internals",
         body=flow(["`t.interrupt()`", "**Blocked** in sleep, wait, join, take?\n→ clear flag, throw", "**Running** code?\n→ set the flag only", "Never checks?\n→ **runs forever**"], step_start=0)
              + frag(bullets(["`Thread.interrupted()` **clears** the flag; `isInterrupted()` doesn't",
                              "Socket `InputStream.read` ignores interruption — **close the socket** to cancel",
                              "`sleep` does **not** release locks — only `wait` does"], cls="bullets sm"), 4),
         narration=[
             "Interruption is a single boolean per thread, plus a convention. You call interrupt.",
             "If the thread is blocked in an interruptible method, like sleep, wait, join or take, the flag is cleared and InterruptedException is thrown.",
             "If it's running ordinary code, only the flag is set, and the thread keeps going.",
             "So if your loop never checks the flag and never blocks, interrupt does nothing at all. The JVM can't stop running code.",
             "Three traps. The static Thread dot interrupted reads and clears the flag, while isInterrupted just reads it. "
             "Blocking socket reads mostly ignore interruption, so to cancel one you close the socket. And sleep never releases a lock. Only wait does.",
         ]),

    dict(title="Exceptions vanish; daemons die mid-write",
         kicker="Internals",
         body=code('''
Thread.ofPlatform().start(() -> { throw new IllegalStateException("vendor unreachable"); });
// main continues. Your application logs nothing.

Thread.ofPlatform()
      .uncaughtExceptionHandler((t, e) -> log.error("thread {} died", t.getName(), e))
      .start(task);
Thread.setDefaultUncaughtExceptionHandler((t, e) -> log.error("uncaught in {}", t.getName(), e));''',
                   title="ExceptionHandling.java", size=24)
              + frag('<p class="callout"><b>Daemon threads</b> are killed at JVM exit with no <code>finally</code>. '
                     'Fine for cache eviction — never for anything that writes data.</p>', 1),
         narration=[
             "An uncaught exception terminates only that thread. The default handler prints to standard error, which in a containerised service often goes nowhere anyone watches. "
             "Your worker is dead and monitoring shows nothing. Set an uncaught exception handler on each worker, plus a JVM-wide default as a safety net.",
             "And daemon threads. The JVM exits when the last non-daemon thread ends, and daemons are killed abruptly, with no finally blocks. "
             "Use them for disposable work, like cache eviction, never for anything that writes data.",
         ]),

    dict(title="What a platform thread costs",
         kicker="Internals",
         body=table(["Cost", ""], [
                    ["Stack reservation", "~1 MB each — 10,000 threads reserve **10 GB** of address space"],
                    ["Creation", "Tens to hundreds of µs — measurable per request"],
                    ["Context switch", "~1–10 µs through the OS, and it pollutes CPU caches"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">This arithmetic is why pools exist (Ch 28) — and why virtual threads were built (Ch 31). '
                     '<b>Name every thread</b>: <code>dispatch-7 BLOCKED, owned by dispatch-3</code> beats <code>Thread-7</code>.</p>', 3),
         narration=[
             "Each platform thread is a real OS thread. It reserves around a megabyte of stack, so ten thousand threads reserve ten gigabytes of address space.",
             "Creating one takes tens to hundreds of microseconds, enough to notice per request.",
             "And context switches go through the operating system, and pollute the CPU caches.",
             "That arithmetic is why thread pools exist, and why virtual threads were built. One more operational tip: name every thread. "
             "A thread dump saying dispatch seven is blocked, owned by dispatch three, tells you everything. Thread seven tells you nothing.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Name every thread and pool factory",
                         "Set uncaught exception handlers",
                         "Propagate `InterruptedException`",
                         "Check `isInterrupted()` in long loops",
                         "`join(Duration)` during shutdown",
                         "Prefer executors and virtual threads"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Call `run()` when you meant `start()`",
                         "Swallow `InterruptedException`",
                         "`Thread.stop`, `suspend`, `resume`",
                         "Daemon threads that write data",
                         "One platform thread per request",
                         "`sleep` for coordination"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Name every thread, including every pool's factory. Set uncaught exception handlers. Propagate InterruptedException. "
             "Check isInterrupted in long loops. Use a bounded join during shutdown. And prefer executors and virtual threads over raw threads.",
             "Never call run when you meant start. Never swallow InterruptedException. Never use stop, suspend or resume. Never make a thread that writes data a daemon. "
             "Never create a platform thread per request. And never use sleep for coordination. Use join, a latch or a queue.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 24 · Threading Fundamentals",
         body=bullets(["Own **stack**, shared **heap**",
                       "`RUNNABLE` includes blocked I/O; `BLOCKED` means a monitor",
                       "Interruption is a **request** — propagate or restore it",
                       "Uncaught exceptions vanish — set handlers",
                       "Next: **Ch 25 · Shared State**"], cls="bullets recap"),
         narration=[
             "To recap. Each thread has its own stack, and they all share the heap. RUNNABLE includes threads blocked in I/O, and BLOCKED only means waiting for a lock. "
             "Interruption is a request, so propagate it or restore it, never swallow it. And uncaught exceptions vanish unless you set handlers.",
             "Next is chapter twenty-five, shared state, where two threads touch the same data. Thanks for watching.",
         ]),
]
