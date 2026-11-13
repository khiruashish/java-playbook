"""Chapter 27 — Locks & Atomics. Source: docs/04-concurrency/27-locks-and-atomics.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 27 · Locks & Atomics"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Locks &amp; Atomics",
         kicker="Concurrency · Chapter 27",
         body='<p class="sub">Timeouts, read-mostly data, counters under contention and thread coordination — '
              'the purpose-built tools beyond <code>synchronized</code>.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-seven: locks and atomics.",
             "synchronized is the right default. But there are four requirements it can't express, and each one has a purpose-built tool in java dot util dot concurrent.",
         ]),

    dict(title="Four things synchronized can't do",
         kicker="The problem",
         body='<div class="grid2">'
              + card("Give up after a timeout", "Checkout must not block forever — the customer is waiting.", "indigo", 0)
              + card("Concurrent readers", "Prices are read thousands of times a second, updated once a minute.", "cyan", 0)
              + card("Wait for events", "Start dispatching only after all five vendor connections are up.", "fuchsia", 0)
              + card("Limit concurrency", "At most 20 concurrent calls to the warehouse API.", "amber", 0)
              + "</div>"
              + frag('<p class="callout">Building these from <code>synchronized</code> + <code>wait</code>/<code>notify</code> gives code that is longer, slower, and wrong more often.</p>', 1),
         narration=[
             "Four requirements synchronized can't express. Give up after a timeout, because checkout can't block forever while a customer waits. Let readers proceed concurrently, because prices are read constantly and updated rarely. "
             "Wait for something to happen, like all vendor connections being ready. And limit concurrency, say to twenty calls against a warehouse API.",
             "You could build each from synchronized and wait-notify. The result would be longer, slower, and wrong more often.",
         ]),

    dict(title="Locks wait; atomics retry",
         kicker="Mental model",
         body=table(["", "Lock", "Atomic (CAS)"], [
                    ["Scope", "Any block of code", "One variable"],
                    ["On contention", "Threads **wait** (park)", "Threads **retry**"],
                    ["Deadlock possible", "Yes", "No"],
                    ["Best under", "High contention, long sections", "Low–moderate, one-variable updates"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">Nearly everything — <code>ReentrantLock</code>, <code>Semaphore</code>, <code>CountDownLatch</code> — is built on '
                     '<b>AbstractQueuedSynchronizer</b>: one atomic int plus a FIFO queue of parked threads.</p>', 1),
         narration=[
             "The core distinction. A lock protects any block of code, and under contention threads wait, parked by the OS. An atomic protects one variable, using compare-and-swap, and under contention threads retry. "
             "So atomics can't deadlock and never park, but under heavy contention every thread spins retrying and burns CPU. Locks are cheaper when sections are long or contention is high.",
             "And almost everything here is built on one class, AbstractQueuedSynchronizer. It's an atomic int that means something different to each tool, plus a queue of parked threads. Understand that, and you understand them all.",
         ]),

    dict(title="ReentrantLock with a timeout",
         kicker="Worked example",
         body=code('''
private final ReentrantLock lock = new ReentrantLock();

public ReservationResult reserve(int quantity) throws InterruptedException {
    if (!lock.tryLock(200, TimeUnit.MILLISECONDS)) {
        return ReservationResult.busy();          // fail fast — the customer is waiting
    }
    try {
        if (available < quantity) return ReservationResult.insufficient(available);
        available -= quantity;
        return ReservationResult.reserved(quantity);
    } finally {
        lock.unlock();                             // ALWAYS in finally
    }
}''', title="StockReservation.java", size=25)
              + bullets(["`tryLock(timeout)` turns a hang into a reportable failure — and breaks a deadlock condition",
                         "Nothing releases a `ReentrantLock` **unless you do** — miss `unlock()` and it's held forever"], start_step=1, cls="bullets sm"),
         narration=[
             "ReentrantLock adds what synchronized lacks: timeouts, interruptible waits, fairness, and multiple conditions. Here, tryLock waits at most two hundred milliseconds, then reports busy instead of hanging.",
             "That turns an indefinite hang into a bounded, reportable failure. It also breaks one of the four deadlock conditions, because a thread that can't acquire gives up instead of waiting while holding what it has.",
             "And the finally is non-negotiable. synchronized releases its monitor on any exit, even an exception. A ReentrantLock is released only when you call unlock. Miss it on an exception path, and the lock is held forever.",
         ]),

    dict(title="Read-mostly data",
         kicker="StampedLock — or no lock at all",
         body=code('''
long stamp = lock.tryOptimisticRead();     // no lock taken
Map<Sku, Money> snapshot = prices;
if (!lock.validate(stamp)) {                // a write happened meanwhile
    stamp = lock.readLock();                // fall back to a real read lock
    try { snapshot = prices; } finally { lock.unlockRead(stamp); }
}
return snapshot.get(sku);                   // careful: StampedLock is NOT reentrant''', title="PriceTable.java", size=25)
              + code('''
private volatile Map<Sku, Money> prices = Map.of();
public Money priceFor(Sku sku) { return prices.get(sku); }                   // readers: no lock
public void replace(Map<Sku, Money> updated) { prices = Map.copyOf(updated); }  // writers: swap''',
                     title="VolatileSwap.java — often the better answer", step=1, size=25),
         narration=[
             "For read-mostly data, StampedLock offers an optimistic read that takes no lock at all. Read a stamp, read the data, then validate that no write happened in between. Only on a conflict do you fall back to a real read lock. "
             "Two cautions: it's not reentrant, so taking it twice on one thread deadlocks. And validate before using what you read.",
             "But when updates replace the whole value, there's often a simpler answer. An immutable map behind a volatile reference. Readers take no lock, writers swap atomically. That beats any lock.",
         ]),

    dict(title="Atomics and LongAdder",
         kicker="Worked examples",
         body=code('''
nextOrderNumber.incrementAndGet();                          // AtomicLong — exact sequence numbers
highestOrder.updateAndGet(current -> current.max(value));   // a CAS loop
counter.updateAndGet(c -> { auditLog.record(c); return c + 1; });   // ✗ fn may run several times''',
                   title="AtomicCounters.java", size=24)
              + frag(table(["", "`AtomicLong`", "`LongAdder`"], [
                    ["Writes under contention", "Degrade — everyone CASes one address", "**Scale** — striped cells"],
                    ["Read", "Exact, cheap", "Sums every cell"],
                    ["Use for", "IDs, exact values", "Metrics, statistics"],
                ], cls="sm"), 1),
         narration=[
             "Atomics. incrementAndGet gives exact sequence numbers. updateAndGet runs a compare-and-swap loop with a function. Under contention that function runs more than once, so it must be pure. "
             "No logging, no side effects, or your audit log records things several times.",
             "And for counters many threads hammer, use LongAdder. With AtomicLong, every thread CASes the same memory and most retry. LongAdder spreads writes across cells and sums them on read. "
             "So AtomicLong for exact values like IDs, LongAdder for metrics you read occasionally.",
         ]),

    dict(title="Coordinating threads",
         kicker="Synchronisers",
         body=code('''
CountDownLatch ready = new CountDownLatch(vendors.size());       // one-shot
vendors.forEach(v -> executor.submit(() -> { v.connect(); ready.countDown(); }));
if (!ready.await(30, TimeUnit.SECONDS)) throw new IllegalStateException("vendors not ready");

Semaphore warehouseSlots = new Semaphore(20);                     // at most 20 concurrent calls
warehouseSlots.acquire();
try { return warehouseClient.statusFor(sku); } finally { warehouseSlots.release(); }''',
                   title="Synchronisers.java", size=24)
              + frag(table(["Synchroniser", "Pattern"], [
                    ["`CountDownLatch`", "Wait for n events — **one-shot**"],
                    ["`CyclicBarrier` / `Phaser`", "Threads meet repeatedly"],
                    ["`Semaphore`", "Bound concurrency against a downstream limit"],
                ], cls="sm"), 1),
         narration=[
             "For coordination, a CountDownLatch waits for n events. Each vendor connection counts down, and await blocks until all are ready, with a timeout. "
             "A Semaphore bounds concurrency: acquire a permit, call the warehouse, release in finally. At most twenty calls at once.",
             "CountDownLatch is one-shot and can't be reset. For threads that meet repeatedly, use CyclicBarrier or Phaser. "
             "And Semaphore pairs naturally with virtual threads: ten thousand can exist while only twenty hold permits.",
         ]),

    dict(title="The ABA problem",
         kicker="Internals",
         body=flow(["Thread 1 reads **A**", "Thread 2: A → **B**", "Thread 2: B → **A**", "Thread 1: CAS A → C **succeeds**"], step_start=0)
              + frag('<p class="callout">CAS checks the value is <b>equal</b>, not that it never changed. It bites lock-free structures that recycle nodes. '
                     'Fix: <code>AtomicStampedReference</code> — a version stamp alongside the value.</p>', 4),
         narration=[
             "One subtle trap: the ABA problem. Thread one reads A.",
             "Thread two changes it to B.",
             "Then back to A.",
             "Thread one's compare-and-swap succeeds, assuming nothing changed. It changed twice.",
             "CAS only checks that the value is equal, not that it was never modified. It matters mostly in lock-free structures that recycle nodes. "
             "The fix is AtomicStampedReference, which pairs the value with a version stamp. For immutable values that are never reused, it doesn't arise.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`synchronized` by default",
                         "`unlock()` in `finally`, always",
                         "`tryLock(timeout)` where callers wait",
                         "Immutable value + volatile swap for read-mostly",
                         "`LongAdder` for contended metrics",
                         "`Semaphore` to respect downstream limits"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Side effects inside `updateAndGet`",
                         "Re-acquire a `StampedLock` on one thread",
                         "Fair locks without measuring",
                         "Reuse a `CountDownLatch`",
                         "Build your own synchroniser from wait/notify"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use synchronized by default. Always unlock in finally. Use tryLock with a timeout where a caller is waiting. "
             "For read-mostly data, try an immutable value behind a volatile reference first. Use LongAdder for contended metrics, and Semaphore to respect downstream limits.",
             "Never put side effects inside updateAndGet. Never re-acquire a StampedLock on the same thread. Don't make locks fair without measuring, because fairness costs a lot of throughput. "
             "Never reuse a CountDownLatch. And never build your own synchroniser from wait and notify when one already exists.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 27 · Locks &amp; Atomics",
         body=bullets(["Locks **wait**; atomics **retry**",
                       "`ReentrantLock`: timeouts and interruption — unlock in `finally`",
                       "Read-mostly: optimistic `StampedLock`, or a volatile swap",
                       "`LongAdder` for hot counters; pure functions in CAS loops",
                       "Latches, barriers, semaphores — don't hand-roll them",
                       "Next: **Ch 28 · Executors**"], cls="bullets recap"),
         narration=[
             "To recap. Locks wait and atomics retry. ReentrantLock adds timeouts and interruption, but you must unlock in finally. For read-mostly data, use an optimistic StampedLock, or just a volatile swap. "
             "Use LongAdder for hot counters, and keep CAS functions pure. And use the built-in latches, barriers and semaphores rather than hand-rolling them.",
             "Next is chapter twenty-eight: executors. Thanks for watching.",
         ]),
]
