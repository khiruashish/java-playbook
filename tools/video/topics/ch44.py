"""Chapter 44 — Testing Concurrent Code. Source: docs/06-testing/44-testing-concurrency.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 44 · Testing Concurrent Code"
SECTION = "Testing"

SLIDES = [
    dict(kind="title",
         title="Testing Concurrent Code",
         kicker="Testing · Chapter 44",
         body='<p class="sub">Less concurrent code, deterministic executors, Awaitility instead of sleep, stress tests that really overlap, and jcstress for the memory model.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter forty-four, the final chapter: testing concurrent code.",
             "Concurrency bugs are the hardest to test for, because a race needs two threads inside a window a few nanoseconds wide at the same moment. A test that passes proves very little. So the goal is to make that coincidence as likely as possible, and to need it as rarely as possible.",
         ]),

    dict(title="Three reasonable-looking tests",
         kicker="The problem",
         body=code('''
orderService.confirm(cart, customer);
Thread.sleep(500);                                   // hope 500 ms is enough
assertThat(dispatchQueue.pending()).hasSize(1);''', title="SleepyTest.java — slow AND flaky", size=23)
              + code('''
t1.start(); t2.start();                              // 1,000 increments each
t1.join();  t2.join();
assertEquals(2000, counter.get());                   // passes with NO synchronisation''',
                     title="NaiveRaceTest.java — the threads never overlap", step=1, size=23)
              + code('''
when(inventory.reserve(any(), anyInt())).thenReturn(true);
assertTrue(service.reserve(sku, 1));                 // the mock is what had the race''',
                     title="MockedConcurrency.java — tests nothing", step=2, size=23),
         narration=[
             "Three tests that look reasonable. The first sleeps half a second and hopes the work is done. It's slow on every run, and flaky whenever CI is loaded enough that half a second isn't enough.",
             "The second starts two threads that each increment a counter a thousand times, and checks for two thousand. It passes against a counter with no synchronisation at all, most of the time, because the first thread often finishes before the second one starts.",
             "And the third mocks the inventory and asserts reserve returns true. It tests nothing about concurrency. The mock is the thing that would have had the race.",
         ]),

    dict(title="Four layers",
         kicker="Mental model",
         body=table(["Layer", "Finds", "Cost"], [
                    ["1 · **Design**", "Nothing — it **prevents**", "Upfront thought"],
                    ["2 · **Deterministic**", "Logic bugs", "Cheap, fast, reliable"],
                    ["3 · Stress", "Races, lost updates, deadlocks", "Slower; probabilistic"],
                    ["4 · jcstress", "Visibility and reordering", "Specialist"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">Most of the value is in the first two. <b>The most effective concurrency-testing technique is having less concurrent code.</b></p>', 4),
         narration=[
             "Think in four layers. First, design: shrink the concurrent surface. It finds nothing, because it prevents.",
             "Second, deterministic tests of the logic, with no threads at all. Cheap, fast and reliable.",
             "Third, stress tests of the genuinely concurrent part: many threads, released together, checking invariants.",
             "And fourth, specialised tools like jcstress for memory-model behaviour.",
             "Most of the value is in the first two layers. If concurrency is confined to a few small components and the business logic is testable synchronously, you need stress tests for a handful of classes, not everywhere.",
         ]),

    dict(title="Separate the logic from the threading",
         kicker="Worked example",
         body=code('''
public final class ReservationPolicy {                       // pure — ordinary unit tests
    public ReservationResult decide(int available, int requested) {
        if (requested <= 0) return ReservationResult.invalid();
        if (requested > available) return ReservationResult.insufficient(available);
        return ReservationResult.reserved(requested);
    }
}
public final class InventoryItem {                          // the only part needing stress tests
    public synchronized ReservationResult reserve(int requested) {
        ReservationResult result = policy.decide(available, requested);
        if (result.succeeded()) available -= requested;
        return result;
    }
}''', title="Separated.java", size=22),
         narration=[
             "Here's the design layer in practice. ReservationPolicy holds the decision: invalid, insufficient, or reserved. It's pure, so it gets ordinary unit tests for every boundary and branch, with no threads. "
             "InventoryItem is small, and asks only one concurrent question: does synchronized keep the available count consistent? That's the only class that needs a stress test.",
         ]),

    dict(title="Deterministic: a same-thread executor",
         kicker="Worked example",
         body=code('''
public DispatchService(Executor executor, VendorClient vendorClient) { … }   // inject it

@Test
void dispatchAll_sendsEveryOrder() {
    Executor sameThread = Runnable::run;                  // runs each task inline
    var service = new DispatchService(sameThread, vendorClient);
    service.dispatchAll(List.of(order1, order2, order3));
    verify(vendorClient, times(3)).send(any());           // no waiting — it already happened
}''', title="DirectExecutorTest.java", size=23)
              + frag('<p class="callout">Inject the <code>Executor</code>, the <code>Clock</code> and the scheduler — tests swap in deterministic versions.</p>', 1),
         narration=[
             "If a class takes its Executor as a constructor parameter, a test can pass Runnable colon colon run, an executor that runs each task immediately on the calling thread. "
             "Dispatch three orders, and verify three sends, with no sleeping and no polling, because it's already happened. That tests the logic of dispatching. Whether the real pool is concurrent is a separate question.",
             "The same idea applies to time and scheduling. Inject the Executor, the Clock and the scheduler, and tests can substitute deterministic versions.",
         ]),

    dict(title="Awaitility instead of sleep",
         kicker="Worked example",
         body=code('''
orderService.confirm(cart, customer);
await().atMost(Duration.ofSeconds(5))
       .pollInterval(Duration.ofMillis(20))
       .untilAsserted(() -> assertThat(dispatchQueue.pending()).hasSize(1));''', title="AwaitilityTest.java", size=24)
              + frag(table(["", "Fast machine", "Loaded CI runner"], [
                    ["`Thread.sleep(500)`", "Wastes ~490 ms", "**Fails** intermittently"],
                    ["`await().atMost(5s)`", "Returns in **milliseconds**", "Waits as long as needed"],
                ], cls="sm"), 1),
         narration=[
             "When something genuinely is asynchronous, poll with Awaitility. Wait at most five seconds, checking every twenty milliseconds, until the assertion passes.",
             "A sleep encodes a guess about how long the work takes, and it's wrong both ways: too long on a fast machine, too short on a loaded one. Polling with a deadline is right in both cases. And set the deadline generously; it only costs time when the test is failing.",
         ]),

    dict(title="A stress test that actually stresses",
         kicker="Worked example",
         body=code('''
@RepeatedTest(20) @Timeout(30)
void reserve_neverOversells() throws Exception {
    InventoryItem item = new InventoryItem(new Sku("MILK-1L"), 1_000);
    CountDownLatch startGate = new CountDownLatch(1);
    AtomicInteger reserved = new AtomicInteger();
    try (ExecutorService pool = Executors.newFixedThreadPool(32)) {
        for (int t = 0; t < 32; t++) pool.submit(() -> {
            startGate.await();                                       // everyone waits…
            for (int i = 0; i < 100; i++) if (item.reserve(1).succeeded()) reserved.incrementAndGet();
            return null;
        });
        startGate.countDown();                                       // …then all start together
    }
    assertEquals(1_000, reserved.get());                             // invariants, not timings
    assertEquals(0, item.available());
}''', title="StressTest.java", size=20)
              + frag('<p class="callout">Start gate · more threads than cores · <b>invariants</b> · repeat with a timeout. Remove <code>synchronized</code> and it fails within a few runs.</p>', 1),
         narration=[
             "Now a stress test that really stresses. A thousand units of stock, thirty-two threads, a hundred attempts each, so three thousand two hundred attempts. Every thread waits on a latch, the start gate, and then they're all released at the same instant.",
             "Four details make this work. The start gate forces real overlap. More threads than cores keeps the race windows busy. It asserts invariants, exactly a thousand reservations and nothing left, which must hold for any interleaving. "
             "And it repeats twenty times with a timeout, so a deadlock fails instead of hanging the build. Remove synchronized, and it fails within a few repetitions.",
         ]),

    dict(title="Deadlocks and the memory model",
         kicker="Specialised tools",
         body=code('''
ThreadMXBean mx = ManagementFactory.getThreadMXBean();
await().during(Duration.ofSeconds(2)).atMost(Duration.ofSeconds(5))
       .until(() -> mx.findDeadlockedThreads() == null);       // a hang becomes a precise failure''',
                   title="DeadlockDetection.java", size=22)
              + frag(code('''
  RESULT      SAMPLES     FREQ       EXPECT  DESCRIPTION
    0, 0   48,221,004   61.43%   Acceptable  reader ran first
   1, 42   30,262,117   38.55%   Acceptable  reader saw the publish
    1, 0       14,882    0.02%    Forbidden  saw ready but not value — REORDERED''',
                          lang="text", title="jcstress · non-volatile `ready` flag, on ARM", size=21), 1),
         narration=[
             "For code that takes several locks, check ThreadMXBean's findDeadlockedThreads during the stress run. It turns a hang into a precise failure that names the threads and the locks.",
             "And for memory-model bugs, use jcstress, OpenJDK's own harness. It runs two actors hundreds of millions of times across fresh JVMs and counts each outcome. "
             "Here, a non-volatile ready flag was seen as true while the value was still zero fourteen thousand times on ARM. An ordinary test would essentially never catch that. Use it for low-level primitives, not application code.",
         ]),

    dict(title="Flaky tests are findings",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("The JIT changes races", "Some bugs only exist in **compiled** code — run enough iterations to reach C2.", "indigo", 0)
              + card("Hardware matters", "A 2-core x86 CI box is the **least likely** place to see a race. ARM exposes reorderings.", "amber", 0)
              + card("Don't retry", "An intermittent failure is usually a **real race**. Quarantine, reproduce, fix.", "fuchsia", 1)
              + "</div>",
         narration=[
             "Two reasons races hide. The JIT changes them: hoisting a read out of a loop, or reordering writes, so some bugs exist only in compiled code. That's why stress tests need many iterations. And hardware matters. A two-core x86 CI container is about the least likely place to expose a race, and ARM exposes reorderings that x86 hides.",
             "Which means a concurrent test that fails intermittently is usually correctly detecting a real race. Retrying it until it passes converts a detected bug into a hidden one. Quarantine it, raise the threads and iterations until it fails reliably, and fix the code.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Shrink the concurrent surface",
                         "Inject executors, clocks, schedulers",
                         "`Runnable::run` for logic tests",
                         "Awaitility or latches with timeouts",
                         "A start gate; assert invariants",
                         "`@RepeatedTest` + `@Timeout`"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`Thread.sleep` to wait for work",
                         "Stress threads without a start gate",
                         "Mock the thing whose safety you test",
                         "Retry a flaky concurrent test",
                         "Call it thread-safe because a test passed"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Shrink the concurrent surface. Inject executors, clocks and schedulers. Use a same-thread executor to test logic. Use Awaitility or latches with timeouts. Use a start gate, and assert invariants. And repeat stress tests, with a timeout on every one.",
             "Never sleep to wait for asynchronous work. Never start stress threads without a start gate. Never mock the component whose thread safety you're testing. Never retry a flaky concurrent test until it passes. And never conclude code is thread-safe because a test passed.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 44 · Testing Concurrent Code",
         body=bullets(["Less concurrent code beats more concurrent tests",
                       "Same-thread executors make logic deterministic",
                       "Poll with a deadline — never sleep",
                       "Start gate + invariants + repetition",
                       "Intermittent failure = probable **real race**"], cls="bullets recap"),
         narration=[
             "To recap. Less concurrent code beats more concurrent tests. A same-thread executor makes logic deterministic. Poll with a deadline, never sleep. Stress tests need a start gate, invariants and repetition. "
             "And an intermittent failure is probably a real race.",
             "That completes the handbook's video series, from the JDK landscape to testing concurrent code. Thanks for watching.",
         ]),
]
