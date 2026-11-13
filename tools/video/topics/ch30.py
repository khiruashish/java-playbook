"""Chapter 30 — Concurrent Collections. Source: docs/04-concurrency/30-concurrent-collections.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 30 · Concurrent Collections"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Concurrent Collections",
         kicker="Concurrency · Chapter 30",
         body='<p class="sub"><code>ConcurrentHashMap</code> from the inside: per-bin locking, atomic compound operations, '
              'and the check-then-act bug that survives code review.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty: concurrent collections.",
             "The star is ConcurrentHashMap. Using it well comes down to two things: understanding why it's fast, and always making a compound operation a single atomic call.",
         ]),

    dict(title="One lock for 200,000 SKUs",
         kicker="The problem",
         body=code('''
private final Map<Sku, Integer> available = new HashMap<>();

public synchronized boolean reserve(Sku sku, int quantity) {   // correct — and a bottleneck
    int current = available.getOrDefault(sku, 0);
    if (current < quantity) return false;
    available.put(sku, current - quantity);
    return true;
}''', title="LockedInventory.java", size=26)
              + frag('<p class="callout">Reserving milk blocks reserving rice. <code>Collections.synchronizedMap</code> is the same single lock. '
                     'We want contention <b>per key</b>, not per map.</p>', 1),
         narration=[
             "Here's a correct inventory reservation. A plain HashMap behind a synchronized method. It works, but it's one global lock across two hundred thousand SKUs.",
             "A thread reserving milk blocks a thread reserving rice, for no reason. Under heavy checkout load, throughput collapses to about one reservation at a time. "
             "Collections dot synchronizedMap doesn't help, because it's the same single lock moved inside. What we want is contention per key, not per map.",
         ]),

    dict(title="Each bin guarded independently",
         kicker="Mental model",
         body=flow(["Empty bin?\n**CAS** in — no lock", "Occupied bin?\n**synchronized** on its first node", "Reads?\n**volatile** — never block"], step_start=0)
              + frag(bullets(["Writes to different bins **never interact**",
                              "No global state — so `size()` is approximate and iteration isn't fail-fast",
                              "**No nulls**: with concurrency, `get(k) == null` could never be disambiguated"], cls="bullets sm"), 3),
         narration=[
             "ConcurrentHashMap guards each bin independently. Writing to an empty bin is a single compare-and-swap, with no lock at all.",
             "Writing to an occupied bin synchronizes on that bin's first node only.",
             "And reads never lock. The table and node fields are volatile, so a reader always sees a consistent view, even during a write to the same bin.",
             "So writes to different bins never interact. There's no global state, which is exactly why size is approximate and iteration can't be fail-fast. "
             "And it rejects nulls. In a concurrent map, get returning null could mean absent or mapped to null, and you could never check which, because the map might change in between.",
         ]),

    dict(title="The check-then-act bug",
         kicker="Survives code review",
         body=code('''
if (!reservations.containsKey(orderId)) {      // ✗ A and B both see false
    reservations.put(orderId, reservation);    //   both write; one is lost
}

StockReservation existing = reservations.putIfAbsent(orderId, reservation);   // ✓ one atomic call''',
                   title="CheckThenAct.java", size=26)
              + frag(table(["Atomic operation", "Does"], [
                    ["`putIfAbsent`", "Insert only if absent"],
                    ["`replace(k, old, new)`", "Compare-and-set on the value"],
                    ["`remove(k, v)`", "Remove only on a key-and-value match"],
                    ["`compute`, `computeIfAbsent`, `merge`", "Read-modify-write under the bin lock"],
                ], cls="sm"), 1),
         narration=[
             "This bug survives code review because every individual call is thread-safe. Check containsKey, then put. But two atomic calls don't make an atomic sequence. "
             "Two threads both see the key missing, both put, and one is lost. The fix is one atomic call, putIfAbsent.",
             "The rule: if your logic reads the map and then writes based on what it read, use a single atomic operation. putIfAbsent, a conditional replace or remove, or compute, computeIfAbsent and merge, "
             "which run the whole read-modify-write under the bin lock.",
         ]),

    dict(title="Per-key reservation",
         kicker="Worked example",
         body=code('''
private final ConcurrentMap<Sku, Integer> available = new ConcurrentHashMap<>();

public boolean reserve(Sku sku, int quantity) {
    Integer[] reserved = {null};
    available.compute(sku, (k, current) -> {
        if (current == null || current < quantity) return current;     // refuse — unchanged
        reserved[0] = quantity;
        return current - quantity;                                     // atomic under the bin lock
    });
    return reserved[0] != null;
}''', title="InventoryReservations.java", size=25)
              + frag('<p class="callout">Different SKUs never touch each other. The same SKU serialises on one bin — exactly what the business rule requires.</p>', 1),
         narration=[
             "Here's the reservation rewritten with no lock of our own. compute runs the check and the decrement atomically, holding only the lock for this SKU's bin. If there isn't enough stock, it returns the value unchanged.",
             "Now two threads reserving different SKUs never touch each other. Two threads reserving the same SKU serialise on one bin, which is exactly the serialisation the business rule needs.",
         ]),

    dict(title="computeIfAbsent: a cache that runs once",
         kicker="Worked example",
         body=code('''
public Money priceFor(Sku sku) {
    return prices.computeIfAbsent(sku, engine::evaluate);   // at most once per key, even under a stampede
}''', title="PriceCache.java", size=25)
              + bullets(["Runs **holding the bin lock** — never touch the same map inside it (`Recursive update`)",
                         "Never do slow I/O inside it — every key in that bin waits"], start_step=1, cls="bullets sm")
              + code('''
inFlight.computeIfAbsent(sku, k -> CompletableFuture.supplyAsync(() -> engine.evaluate(k), executor));''',
                     title="FutureCache.java — lock held only to register the work", step=2, size=24),
         narration=[
             "computeIfAbsent makes a cache that loads each key at most once, even when many threads miss at the same moment. The naive get, then put, runs the expensive evaluation once per contending thread, which is the stampede a cache exists to prevent.",
             "But the mapping function runs while holding the bin's lock. So never modify the same map inside it. ConcurrentHashMap detects that and throws a recursive update exception. "
             "And never do slow I/O inside it, because every other key hashing to that bin waits on your network call.",
             "For expensive loads, store a CompletableFuture instead. The lock is held only long enough to register the in-flight work, not to complete it.",
         ]),

    dict(title="Safe map, unsafe contents",
         kicker="The mutable-value trap",
         body=code('''
board.computeIfAbsent(slot, s -> new ArrayList<>()).add(order);          // ✗ add() is OUTSIDE the lock

board.computeIfAbsent(slot, s -> new ConcurrentLinkedQueue<>()).add(order);    // ✓ concurrent value
reservationCounts.computeIfAbsent(sku, k -> new LongAdder()).increment();      // ✓ per-key counters''',
                   title="MutableValueTrap.java", size=25)
              + frag('<p class="callout"><code>ConcurrentHashMap</code> safely publishes the <b>reference</b>. It guarantees nothing about the object on the other end. '
                     'And <code>putAll</code> / <code>clear</code> are thread-safe, not atomic.</p>', 1),
         narration=[
             "A thread-safe map with unsafe contents. computeIfAbsent is atomic, but the add that follows happens outside the lock. Two threads can hold the same ArrayList and corrupt it. "
             "Use a concurrent value type, like ConcurrentLinkedQueue, or swap immutable lists with merge. For per-key counters, a LongAdder per key works well.",
             "Remember: the map safely publishes the reference it stores, but it guarantees nothing about the object on the other end of it. "
             "And bulk operations like putAll and clear are thread-safe, but not atomic. A reader can see half of a putAll.",
         ]),

    dict(title="Inside the rewrite",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Cooperative resize", "Migrated bins become `ForwardingNode`s. Writers that hit one **help** migrate a stride. Reads are redirected — **resize never blocks reads**.", "indigo", 0)
              + card("Striped size", "`baseCount` + `CounterCell[]`, like `LongAdder`. `size()` sums them — a value true at no single instant.", "cyan", 1)
              + card("Weakly consistent", "Iterators never throw CME, never skip a stable element, never repeat one — but they're **not a snapshot**.", "fuchsia", 2)
              + "</div>"
              + frag('<p class="callout">Java 8 replaced Java 7\'s 16 segments with per-bin locking — <code>concurrencyLevel</code> is now only a sizing hint.</p>', 3),
         narration=[
             "Inside, resizing is cooperative. As bins move to the new table, they're replaced by forwarding nodes. A writer that hits one helps migrate a stretch of bins itself. Readers are simply redirected, so resizing never blocks reads.",
             "There's no single size counter, because it would be a contention point on every write. Instead it's striped across cells, like LongAdder, and size sums them. So it's a value that was true at no single instant. Use it for metrics, never for correctness.",
             "And iterators are weakly consistent. They never throw ConcurrentModificationException, never skip an element that was present throughout, and never repeat one. But they're not a snapshot.",
             "This is the Java 8 rewrite. Java 7 used sixteen segments with their own locks. If you see code tuning concurrencyLevel, it's now only a sizing hint.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["One atomic call per read-modify-write",
                         "`computeIfAbsent` for load-once caches",
                         "Futures in the map for slow loads",
                         "Concurrent or immutable values",
                         "`LongAdder` values for per-key counters",
                         "`ConcurrentHashMap.newKeySet()` for a concurrent set"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`containsKey` then `put`",
                         "I/O inside `compute*`",
                         "Touch the same map inside `compute*`",
                         "Mutable values shared unsafely",
                         "Decide anything from `size()`",
                         "Null keys or values"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Make every read-modify-write a single atomic call. Use computeIfAbsent for load-once caches, and store futures for slow loads. "
             "Keep values concurrent or immutable. Use LongAdder values for per-key counters. And for a concurrent set, use ConcurrentHashMap dot newKeySet.",
             "Never write containsKey then put. Never do I/O inside compute, or touch the same map there. Never share mutable values unsafely. "
             "Never make a decision based on size. And never put nulls in it.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 30 · Concurrent Collections",
         body=bullets(["Per-bin locking: CAS on empty, `synchronized` on occupied, lock-free reads",
                       "Two atomic calls ≠ an atomic sequence — use `compute*` / `merge`",
                       "`computeIfAbsent` holds the bin lock: no I/O, no recursion",
                       "Safe map ≠ safe values",
                       "Next: **Ch 31 · Virtual Threads**"], cls="bullets recap"),
         narration=[
             "To recap. ConcurrentHashMap locks per bin: a CAS for empty bins, synchronized for occupied ones, and lock-free reads. Two atomic calls don't make an atomic sequence, so use compute and merge. "
             "computeIfAbsent holds the bin lock, so no I/O and no recursion inside it. And a safe map doesn't make its values safe.",
             "Next is chapter thirty-one: virtual threads. Thanks for watching.",
         ]),
]
