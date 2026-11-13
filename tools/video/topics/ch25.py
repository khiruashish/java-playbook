"""Chapter 25 — Shared State. Source: docs/04-concurrency/25-shared-state.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 25 · Shared State"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Shared State",
         kicker="Concurrency · Chapter 25",
         body='<p class="sub">Atomicity, visibility and ordering — three different problems — and the <code>synchronized</code>, '
              '<code>volatile</code> and lock-order rules that fix them.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-five: shared state.",
             "The moment two threads touch the same data, three different things can go wrong. Telling them apart is the key to fixing them, "
             "because each needs a different tool.",
         ]),

    dict(title="One line, three steps",
         kicker="The problem",
         body=code('''
private int available = 100;

public void reserve(int quantity) {
    available = available - quantity;   // read, subtract, write — three steps
}

// two threads × 10,000 single-unit reservations
System.out.println(inventory.available());   // -19847 — expected -19900, varies every run''',
                   title="UnsafeInventory.java", size=27)
              + frag('<p class="callout">Two threads read the same value before either writes. In the inventory engine, that\'s <b>overselling</b>.</p>', 1),
         narration=[
             "Here's an inventory counter. Reserving stock is one line: available equals available minus quantity. "
             "Run it from two threads, ten thousand reservations each, and the result is wrong, and different every run.",
             "That one line is really three steps: read, subtract, write. Two threads can both read the same value before either writes, so an update is lost. "
             "In the inventory engine, that means overselling: two customers both reserve the last unit.",
         ]),

    dict(title="Three separate problems",
         kicker="Mental model",
         body=table(["Problem", "Looks like", "Fixed by"], [
                    ["**Atomicity**", "Lost updates; `count++` losing increments", "`synchronized`, `Lock`, atomics"],
                    ["**Visibility**", "A loop never sees `running = false`", "`volatile`, `synchronized`, `final`"],
                    ["**Ordering**", "A half-constructed object seen by another thread", "`volatile`, `synchronized`"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout"><code>volatile</code> fixes visibility and ordering — <b>not atomicity</b>. '
                     'Most misuse of <code>volatile</code> comes from not separating these.</p>', 3),
         narration=[
             "There are three separate problems. Atomicity: a compound action gets interleaved, like the lost update. Fixed by synchronized, locks or atomic classes.",
             "Visibility: one thread's write is never seen by another. A loop keeps running after another thread sets running to false. Fixed by volatile, synchronized or final.",
             "Ordering: the compiler or CPU reorders operations, so another thread sees a half-built object. Fixed by volatile or synchronized.",
             "The key point: volatile fixes visibility and ordering, but not atomicity. Most misuse of volatile comes from not separating these three.",
         ]),

    dict(title="Why visibility is real",
         kicker="Mental model",
         body=code('''
private boolean running = true;            // ✗ may loop forever
public void stop() { running = false; }
public void run() {
    while (running) {                       // JIT may hoist this read → while (true)
        processNextOrder();
    }
}''', title="NeverStops.java", size=27)
              + frag(code('private volatile boolean running = true;   // ✓ one writer, many readers, no read-modify-write',
                          title="DispatchLoop.java", size=26), 1)
              + frag('<p class="callout">Legal optimisation — which is why it works under a debugger and fails in production.</p>', 2),
         narration=[
             "Visibility sounds theoretical, but it isn't. Cores have their own caches, and the JIT keeps values in registers. "
             "Here, the JIT sees that nothing in this thread writes running, so it's allowed to read it once and compile the loop to while true. The stop call is never seen.",
             "Marking the flag volatile fixes it. This is the canonical correct use of volatile: one writer, many readers, and the new value doesn't depend on the old one.",
             "And because the hoisting is a legal optimisation, the bug usually disappears under a debugger or the interpreter, and appears only in production.",
         ]),

    dict(title="synchronized, done right",
         kicker="Worked example",
         body=code('''
private final Object lock = new Object();    // private lock — not `this`
private int available = 100;

public boolean reserve(int quantity) {
    synchronized (lock) {
        if (available < quantity) return false;
        available -= quantity;
        return true;
    }
}
public int available() {
    synchronized (lock) { return available; }   // reads need the lock too
}''', title="SafeInventory.java", size=26)
              + bullets(["**Synchronise reads** — the lock gives visibility, not just exclusion",
                         "**Private lock object** — `this` lets any caller stall or deadlock you"], start_step=1, cls="bullets sm"),
         narration=[
             "Here's the fix. A synchronized block makes the check and the update one atomic step, so the result is right every run. "
             "synchronized is reentrant, and it creates a happens-before edge: everything done before releasing the lock is visible to the next thread that takes it.",
             "Notice the read is synchronized too. Without it, available could return a stale value. Synchronizing only writes is a half-fix that appears to work.",
             "And the lock is a private object, not this. Locking on this publishes your lock, so any caller can synchronize on your object and stall your internals, or deadlock against you.",
         ]),

    dict(title="volatile is not atomic",
         kicker="Worked examples",
         body=code('''
private volatile int reservationCount;
reservationCount++;                                    // ✗ STILL read, increment, write

private final AtomicInteger count = new AtomicInteger();
count.incrementAndGet();                               // ✓ atomic
private final LongAdder hot = new LongAdder();  hot.increment();   // ✓ high contention''',
                   title="VolatileNotAtomic.java", size=26)
              + code('''
if (!reservations.containsKey(orderId)) {      // ✗ check-then-act: both threads pass
    reservations.put(orderId, reservation);
}
reservations.putIfAbsent(orderId, reservation);   // ✓ one atomic operation''', title="CheckThenAct.java", step=1, size=26),
         narration=[
             "volatile doesn't make plus plus safe. It makes each read and each write visible, but does nothing about the gap between them. "
             "Use an AtomicInteger, or a LongAdder when many threads hammer the same counter.",
             "The same race hides in check-then-act code, with no arithmetic at all. Two threads can both see the key is missing, and both put. "
             "Any test followed by an act on shared state must be atomic as a whole. Use one operation, like putIfAbsent or compute.",
         ]),

    dict(title="wait / notify",
         kicker="Producer–consumer",
         body=code('''
public synchronized Order take() throws InterruptedException {
    while (queue.isEmpty()) {     // WHILE, never if — spurious wakeups are legal
        wait();                   // releases the monitor while waiting
    }
    Order order = queue.remove();
    notifyAll();
    return order;
}''', title="OrderBuffer.java", size=27)
              + frag('<p class="callout">Hold the monitor to call them. Prefer <code>notifyAll</code>. And in production this class is just '
                     '<code>new ArrayBlockingQueue&lt;&gt;(capacity)</code>.</p>', 1),
         narration=[
             "wait and notify build producer-consumer buffers. wait releases the monitor while it waits. The whole lesson is the while loop. "
             "On waking, a thread must re-check its condition, because the spec allows spurious wakeups, and another thread may have taken the item first. "
             "An if here gives you an exception about once a month.",
             "You must hold the monitor to call these, and prefer notifyAll. But in practice, almost every correct use of wait and notify is reimplementing a blocking queue, less well. Use ArrayBlockingQueue.",
         ]),

    dict(title="Deadlock",
         kicker="Worked example",
         body=code('''
synchronized (from) { synchronized (to) { ... } }   // ✗ order depends on the arguments
// A: transfer(milk, rice)  holds milk, wants rice
// B: transfer(rice, milk)  holds rice, wants milk  → neither proceeds

InventoryItem first  = from.sku().code().compareTo(to.sku().code()) < 0 ? from : to;
InventoryItem second = (first == from) ? to : from;
synchronized (first) { synchronized (second) { ... } }   // ✓ a global lock order''',
                   title="TransferDeadlock.java", size=25)
              + frag(table(["Deadlock needs all four", "Break one"], [
                    ["Mutual exclusion", "Immutable data or atomics"],
                    ["Hold and wait", "Acquire everything at once"],
                    ["No preemption", "`tryLock(timeout)`"],
                    ["Circular wait", "**A global lock order** — the usual fix"],
                ], cls="sm"), 1),
         narration=[
             "Here's a deadlock you can reproduce. A transfer locks from, then to. Thread A transfers milk to rice, and thread B transfers rice to milk. "
             "A holds milk and wants rice, B holds rice and wants milk, and neither ever proceeds. "
             "The fix is a global lock order. Sort the two items, here by SKU code, and every thread locks them in the same order.",
             "A deadlock needs four conditions at once, and breaking any one prevents it. Lock ordering is the practical answer, because it's something you can see in code review rather than have to catch in a test. "
             "And when one happens, jcmd Thread dot print reports monitor deadlocks by name.",
         ]),

    dict(title="Internals",
         kicker="What it costs",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("synchronized", "Uncontended: one **CAS** on the header — nanoseconds. Only **contention** is expensive.", "indigo", 0)
              + card("volatile", "Reads are essentially free on x86; writes cost about a CAS. Makes double-checked locking correct.", "cyan", 1)
              + card("Word tearing", "Non-volatile `long`/`double` writes may be split in two — a reader can see a value never written.", "fuchsia", 2)
              + "</div>",
         narration=[
             "What does it cost? An uncontended synchronized block is a single compare-and-swap on the object header. Nanoseconds. Synchronized is slow is outdated advice. It's contention that's expensive, and no lock avoids that.",
             "A volatile read is essentially free on x86, and a write costs about a compare-and-swap. The barrier also stops reordering, which is what makes double-checked locking correct, but only with volatile.",
             "And a subtle one. The spec lets a non-volatile long or double write happen as two thirty-two-bit halves, so a reader could see a value that was never written. Volatile prevents that.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Avoid shared mutable state altogether",
                         "Lock on a private final object",
                         "Synchronise reads as well as writes",
                         "Keep critical sections short — no I/O",
                         "A global lock order",
                         "Comment each field: \"guarded by lock\""], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Assume `volatile` makes `count++` safe",
                         "`wait()` inside an `if`",
                         "Lock on strings, boxed values, foreign classes",
                         "Hold a lock across a network call",
                         "Lock order that depends on arguments",
                         "`Thread.sleep` to \"avoid\" a race"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Best of all, avoid shared mutable state: immutable objects, confinement to one thread, or message passing. Every lock you don't need is a bug you can't have. "
             "Lock on a private final object. Synchronize reads too. Keep critical sections short, with no I/O inside. Impose a global lock order. And comment which lock guards each field.",
             "Never assume volatile makes plus plus safe. Never wait inside an if. Never lock on string literals or boxed values, which are shared JVM-wide. "
             "Never hold a lock across a network call. Never let lock order depend on the arguments. And never use sleep to avoid a race. It just hides the bug until load changes.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 25 · Shared State",
         body=bullets(["Three problems: **atomicity, visibility, ordering**",
                       "`volatile` — visibility only; atomics for read-modify-write",
                       "Synchronise reads too, on a private lock",
                       "`wait` in a `while`; better, a `BlockingQueue`",
                       "Deadlock → a global lock order",
                       "Next: **Ch 26 · The Java Memory Model**"], cls="bullets recap"),
         narration=[
             "To recap. Shared state has three problems: atomicity, visibility and ordering. volatile solves visibility, not atomicity, so use atomics for read-modify-write. "
             "Synchronize reads too, on a private lock. Wait in a while loop, or better, use a blocking queue. And prevent deadlock with a global lock order.",
             "Next is chapter twenty-six, the Java memory model, which explains why all of this works. Thanks for watching.",
         ]),
]
