"""Chapter 26 — The Java Memory Model. Source: docs/04-concurrency/26-java-memory-model.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 26 · The Java Memory Model"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="The Java Memory Model",
         kicker="Concurrency · Chapter 26",
         body='<p class="sub">Why writes appear out of order, the happens-before relation that tames it, '
              'and how to publish objects safely.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-six: the Java memory model.",
             "This chapter explains why the rules in the last one work. Once you understand one relation, called happens-before, "
             "you can prove concurrent code correct instead of hoping it is.",
         ]),

    dict(title="This program can print 0",
         kicker="The problem",
         body=code('''
int value;
boolean ready;

void publish() {             // thread A
    value = 42;
    ready = true;
}
void consume() {             // thread B
    if (ready) System.out.println(value);    // may print 0
}''', title="Reordering.java", size=28)
              + frag('<p class="callout">Compiler, CPU store buffer and caches may all reorder legally. Rare on <b>x86</b>, real on <b>ARM</b> '
                     '— cloud instances and Apple Silicon. Tested on one, deployed to the other.</p>', 1),
         narration=[
             "This program can print zero. Thread A sets value to forty-two, then ready to true. Thread B sees ready is true, yet value is still zero. "
             "The writes appear to happen in the wrong order.",
             "Nothing is broken. The compiler may reorder the two writes, because within thread A their order is invisible. The CPU may reorder them through its store buffer. And B's cache may update ready before value. "
             "All legal. Worse, it's platform-dependent. On x86 this almost never shows up. On ARM, including cloud instances and Apple Silicon laptops, it does.",
         ]),

    dict(title="There is no global \"now\"",
         kicker="Mental model",
         body='<div class="grid2">'
              + card("Hardware", "Each core has its own **store buffer and caches**. Writes become visible eventually — not necessarily in program order.", "fuchsia", 0)
              + card("The JMM", "Not a hardware description. A **contract**: which values a read is permitted to return. The JVM adds barriers where hardware is weaker.", "indigo", 1)
              + "</div>",
         narration=[
             "There's no global now. Each core has its own store buffer and caches. A write becomes visible to other cores eventually, and not necessarily in program order.",
             "The Java Memory Model doesn't describe hardware. It's an abstract contract that defines which values a read is allowed to return. "
             "The JVM then implements that contract on any hardware, inserting barriers wherever the hardware is weaker than the contract.",
         ]),

    dict(title="Happens-before",
         kicker="The one relation",
         body=flow(["Thread A: `value = 42`", "Thread A: unlock(m)", "Thread B: lock(m)", "Thread B: reads `value` → **42 guaranteed**"], step_start=0)
              + frag('<p class="callout"><b>DRF-SC:</b> a program with no data races behaves as if <b>sequentially consistent</b>. '
                     'Remove every race, and the intuitive model holds — no store buffers required.</p>', 4),
         narration=[
             "Everything is built on one relation. If X happens-before Y, X's effects are visible to Y. Within a thread, program order gives it: setting value happens before the unlock.",
             "The monitor rule says an unlock happens before every later lock of the same monitor.",
             "Then program order again in thread B.",
             "And happens-before is transitive. Chain the rules into a path from a write to a read, and the read is guaranteed to see it.",
             "Here's the payoff, called DRF-SC. A data race is two accesses to the same variable, at least one a write, from different threads, with no happens-before between them. "
             "Eliminate every data race, and your program behaves as if statements ran one at a time. You don't need to reason about store buffers and caches at all.",
         ]),

    dict(title="The happens-before rules",
         kicker="Core reference",
         body='<div class="grid2 start">'
              + frag(table(["Language rule", "Guarantee"], [
                    ["Program order", "Earlier → later in one thread"],
                    ["Monitor", "unlock m → later lock of m"],
                    ["Volatile", "write v → later read of v"],
                    ["Thread start", "`start()` → everything in the thread"],
                    ["Termination", "everything in t → `join()` returns"],
                ], cls="sm"), 0)
              + frag(table(["java.util.concurrent", "Edge"], [
                    ["`BlockingQueue.put(x)`", "→ the `take()` of x"],
                    ["`executor.submit(task)`", "→ the task runs"],
                    ["Task completes", "→ `Future.get()` returns"],
                    ["`latch.countDown()`", "→ `await()` returns"],
                    ["`CHM.put(k, v)`", "→ `get(k)` sees v"],
                ], cls="sm"), 1)
              + "</div>",
         narration=[
             "The language rules: program order within a thread. Unlocking a monitor before any later lock of it. A volatile write before any later read. Starting a thread before everything it does. "
             "And everything a thread does before another thread's join on it returns.",
             "And java dot util dot concurrent documents its own edges, which is what makes it composable. Putting into a blocking queue happens before the take that retrieves it. "
             "Submitting a task happens before it runs, and completion happens before get returns. That's why handing an object through a queue is safe with no other synchronisation.",
         ]),

    dict(title="Fix it with one volatile",
         kicker="Worked example",
         body=code('''
int value;
volatile boolean ready;          // the only change

void publish()  { value = 42;  ready = true; }               // (1) then (2) volatile write
void consume()  { if (ready) System.out.println(value); }    // (3) volatile read, then (4) → 42''',
                   title="VolatilePublisher.java", size=25)
              + frag(flow(["(1) `value = 42`", "(2) volatile write", "(3) volatile read", "(4) read `value`"]), 0)
              + frag('<p class="callout"><code>value</code> isn\'t volatile — the volatile write <b>piggybacks</b> everything before it. '
                     'That\'s how nearly all correct concurrent code works.</p>', 1),
         narration=[
             "Fix the publisher by making just ready volatile. Here's the proof. One happens before two by program order. Two happens before three by the volatile rule, since three read what two wrote. "
             "Three happens before four by program order. So by transitivity, one happens before four, and four must see forty-two.",
             "Notice value didn't need to be volatile. The volatile write piggybacks every plain write before it. That's how nearly all correct concurrent code works: one synchronised access carrying the visibility of everything before it.",
         ]),

    dict(title="Safe publication",
         kicker="Worked examples",
         body=code('''
class PriceTable {
    private final Map<Sku, Money> prices;      // final → safe however it's published
    PriceTable(Map<Sku, Money> p) { this.prices = new HashMap<>(p); }
}''', title="SafePublication.java", size=25)
              + frag(table(["Safe publication idiom", "Example"], [
                    ["Static initialiser", "`static final Config CONFIG = load();`"],
                    ["`volatile` / `AtomicReference`", "`private volatile Config config;`"],
                    ["`final` field", "Set in the constructor"],
                    ["Guarded by a lock", "Read and written under the same lock"],
                ], cls="sm"), 1),
         narration=[
             "An object is safely published when its reference and its state become visible together. Without that, another thread can see a non-null PriceTable whose map is still null, or half-built. "
             "Making the field final fixes it, and fixes it however the object is published.",
             "The four safe publication idioms: a static initialiser, a volatile or atomic reference, a final field set in the constructor, or a field always read and written under the same lock. "
             "Plus any handoff through java dot util dot concurrent.",
         ]),

    dict(title="Double-checked locking &amp; this-escape",
         kicker="Worked examples",
         body=code('''
private volatile PricingEngine engine;    // remove volatile → another thread may see a half-built engine

private static class Holder { static final PricingEngine ENGINE = new PricingEngine(); }
static PricingEngine engine() { return Holder.ENGINE; }    // simpler: lazy, thread-safe, no volatile''',
                   title="DoubleCheckedLocking.java", size=24)
              + code('''
OrderMonitor(EventBus bus) {
    bus.register(this);                  // ✗ `this` escapes before construction finishes
    this.tracked = new HashMap<>();
}
static OrderMonitor create(EventBus bus) { var m = new OrderMonitor(); bus.register(m); return m; }   // ✓''',
                     title="ThisEscape.java", step=1, size=24),
         narration=[
             "Double-checked locking is correct only with volatile. Without it, another thread can see the reference before the constructor's writes, a non-null engine with default fields. "
             "But usually there's a simpler answer: the holder idiom. Class initialisation is lazy and thread-safe by JVM guarantee. No volatile, no lock.",
             "And never let this escape the constructor. Registering yourself with an event bus inside the constructor means events can arrive before tracked is assigned. "
             "Final-field guarantees don't apply then. Construct first, then register, with a static factory. Java 21's this-escape lint warns about this.",
         ]),

    dict(title="Final fields &amp; barriers",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("The freeze", "At the end of the constructor, final fields — and what they reference — are frozen and visible to **any** thread, however published.", "indigo", 0)
              + card("Barriers", "x86: volatile read is a plain load, write is a locked instruction. ARM: barriers on both. The JMM is the same; the forgiveness isn't.", "cyan", 1)
              + card("\"Benign\" races", "`String.hashCode` races correctly. Change `int` to `long`, or read twice, and it breaks. The JDK can justify it — you probably can't.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Three internals. Final field semantics. At the end of the constructor, final fields are frozen. Any thread that gets the reference, by any means, sees them as the constructor left them. "
             "That's why immutable objects need no synchronisation, as long as this didn't escape.",
             "Barriers. On x86, a volatile read is just a plain load, and a write is a locked instruction. On ARM, both need barriers. The memory model is identical. What differs is how much the hardware forgives missing synchronisation.",
             "And beware benign race arguments. String's cached hashCode races, correctly. But change the int to a long and it can tear, or read the field twice and get two answers. The JDK authors can justify it. Most application code can't.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Remove every data race — then reason simply",
                         "Hand off through `java.util.concurrent`",
                         "`final` fields for anything shared",
                         "Holder idiom for lazy singletons",
                         "Construct, then publish",
                         "Test on ARM if you deploy to ARM"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Double-checked locking without `volatile`",
                         "Let `this` escape a constructor",
                         "Publish through a plain field",
                         "Trust \"works on my x86 laptop\"",
                         "Argue a race is benign without proof"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Remove every data race, and then you can reason simply. Hand objects between threads through java dot util dot concurrent. Use final fields for anything shared. "
             "Use the holder idiom for lazy singletons. Construct first, then publish. And if you deploy to ARM, test on ARM.",
             "Never write double-checked locking without volatile. Never let this escape a constructor. Never publish through a plain field. Never trust works on my x86 laptop. "
             "And never argue a race is benign without a real proof.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 26 · The Java Memory Model",
         body=bullets(["The JMM is a **contract**, not a hardware description",
                       "**Happens-before** chains a write to a read",
                       "No data races ⇒ sequentially consistent",
                       "One volatile write publishes everything before it",
                       "Final fields + no this-escape = safe sharing",
                       "Next: **Ch 27 · Locks &amp; Atomics**"], cls="bullets recap"),
         narration=[
             "To recap. The memory model is a contract about which values reads may return. Happens-before chains a write to a read. "
             "Remove every data race and the program behaves sequentially. One volatile write publishes everything before it. And final fields, with no this-escape, make sharing safe.",
             "Next is chapter twenty-seven: locks and atomics. Thanks for watching.",
         ]),
]
