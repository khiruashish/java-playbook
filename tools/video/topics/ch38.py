"""Chapter 38 — Stream Gatherers. Source: docs/05-runtime/38-stream-gatherers.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 38 · Stream Gatherers"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="Stream Gatherers",
         kicker="Runtime · Chapter 38 · Java 24",
         body='<p class="sub">Custom intermediate operations — batching, running totals, sliding windows, and bounded concurrent I/O inside a stream.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-eight: stream gatherers, final in Java 24.",
             "Since Java 8, you could extend the end of a stream with a custom collector, but the middle was closed. Filter, map, flatMap, and that's it. So batching, running totals and deduplicating by key all meant abandoning the stream. Gatherers close that gap.",
         ]),

    dict(title="Four jobs that needed a loop",
         kicker="The problem",
         body=code('''
List<List<Order>> batches = new ArrayList<>();          // 1. batches of 100
List<Order> current = new ArrayList<>();
for (Order order : orders) {
    current.add(order);
    if (current.size() == 100) { batches.add(current); current = new ArrayList<>(); }
}
if (!current.isEmpty()) batches.add(current);           //    the line everyone forgets''',
                   title="BatchingBefore.java", size=24)
              + frag(bullets(["2. A **running total** of cart value",
                              "3. **Distinct by SKU**, keeping the first",
                              "4. Call a vendor API per SKU, **at most 20 at a time** — `parallelStream` blocks the common pool"],
                             cls="bullets sm"), 1),
         narration=[
             "Here's batching orders into groups of a hundred before Java 24. A loop, a current batch, and a check at the end for the trailing partial batch, which is the line most hand-written versions forget.",
             "Same story for a running total, deduplicating by SKU, and calling a vendor API per SKU at most twenty at a time. parallelStream can't do that last one, because it blocks the shared common pool. "
             "Each needed state carried between elements, and the stream API had nowhere to put it.",
         ]),

    dict(title="Gatherer is to the middle as Collector is to the end",
         kicker="Mental model",
         body=table(["", "`Collector`", "`Gatherer`"], [
                    ["Position", "Terminal", "**Intermediate**"],
                    ["Produces", "One value", "A stream"],
                    ["Components", "supplier, accumulator, combiner, finisher", "initializer, integrator, combiner, finisher"],
                    ["Invoked by", "`collect(...)`", "`gather(...)`"],
                ], step_per_row=None, cls="sm")
              + frag(flow(["`integrator(state, element, downstream)`", "`downstream.push(v)` → **false** = downstream is done", "integrator returns **false** = this gatherer is done"]), 1)
              + frag('<p class="callout">Those two booleans preserve <b>laziness and short-circuiting</b> — exactly what a hand-written loop gives up.</p>', 1),
         narration=[
             "A Gatherer is to intermediate operations what a Collector is to terminal ones. It has four matching parts: an initializer for state, an integrator per element, a combiner for parallel streams, and a finisher. "
             "The difference is that a gatherer pushes elements downstream as it goes, instead of accumulating into a container.",
             "Control flows through two booleans. Pushing downstream returns false when nothing downstream wants more, say a limit was satisfied. And the integrator returns false to say this gatherer is finished. "
             "That's what keeps laziness and short-circuiting working through a custom operation.",
         ]),

    dict(title="The built-ins",
         kicker="java.util.stream.Gatherers",
         body=table(["Gatherer", "Produces"], [
                    ["`windowFixed(n)`", "Lists of size n — **including** the trailing partial one"],
                    ["`windowSliding(n)`", "Overlapping windows, one step at a time"],
                    ["`fold(init, f)`", "One accumulated value at the end"],
                    ["`scan(init, f)`", "The running accumulation, one per input"],
                    ["`mapConcurrent(limit, fn)`", "`fn` on **virtual threads**, ≤ limit at once, **order preserved**"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "There are five built-ins. windowFixed groups elements into lists of n, including the trailing partial one.",
             "windowSliding produces overlapping windows that advance one element at a time.",
             "fold accumulates everything into one value at the end.",
             "scan emits the running accumulation, one value per input.",
             "And mapConcurrent applies a function on virtual threads, at most limit at a time, preserving order. That's the one that changes how you write I/O-bound pipelines.",
         ]),

    dict(title="Batching, running totals, windows",
         kicker="Worked examples",
         body=code('''
orders.stream().filter(Order::isConfirmed)
      .gather(Gatherers.windowFixed(100))          // trailing partial batch handled
      .map(vendorClient::dispatchBatch)
      .toList();''', title="Batching.java", size=24)
              + code('''
cart.lines().stream()
    .gather(Gatherers.scan(() -> Money.ZERO, (total, line) -> total.plus(line.lineTotal())))
    .toList();                                       // [₹120.00, ₹570.00, ₹610.00]''', title="RunningTotal.java", step=1, size=24)
              + code('''
ordersPerMinute.stream().gather(Gatherers.windowSliding(5))
    .map(w -> w.stream().mapToInt(Integer::intValue).average().orElse(0))
    .toList();                                       // 5-minute moving average''', title="MovingAverage.java", step=2, size=24),
         narration=[
             "Batching becomes one line in the pipeline. windowFixed of a hundred, then dispatch each batch. The trailing partial batch is emitted by its finisher, so that bug is gone.",
             "A running total is scan, starting from zero and adding each line. It emits the total so far for every line.",
             "And a five-minute moving average is windowSliding of five, then averaging each window. Before gatherers, that needed an indexed loop over a materialised list.",
         ]),

    dict(title="mapConcurrent — the important one",
         kicker="Worked example",
         body=code('''
List<InventoryStatus> statuses = skus.stream()
    .gather(Gatherers.mapConcurrent(20, warehouseClient::statusFor))   // 200 ms blocking call each
    .toList();''', title="ConcurrentLookup.java", size=26)
              + '<div class="grid2">'
              + card("✗ parallelStream", "Runs on the shared common pool, sized for CPU. Blocking I/O there **starves every parallel stream** in the JVM, with no per-call limit.", "fuchsia", 1)
              + card("✓ mapConcurrent", "≤ 20 at once, on **virtual threads**, **order preserved**, and a failure cancels the rest. The default for I/O fan-out on 24+.", "indigo", 1)
              + "</div>",
         narration=[
             "Here's the important one. For each SKU, call the warehouse, a two-hundred-millisecond blocking request. mapConcurrent of twenty runs at most twenty at once, on virtual threads, and keeps the results in order, inside an ordinary stream.",
             "Compare parallelStream, which runs on the shared common pool, sized for CPU work. Blocking I/O there starves every other parallel stream in the JVM, and you can't bound concurrency per call. "
             "mapConcurrent gives you a bound, order preservation, and cancellation when one fails. For I/O fan-out in a stream on Java 24, it's the right default.",
         ]),

    dict(title="Write your own: distinctBy",
         kicker="Worked example",
         body=code('''
public static <T, K> Gatherer<T, ?, T> distinctBy(Function<? super T, ? extends K> keyFn) {
    return Gatherer.ofSequential(
        HashSet::new,                                   // initializer: private state
        (seen, element, downstream) -> {                 // integrator
            if (seen.add(keyFn.apply(element))) {
                return downstream.push(element);         // propagate short-circuit
            }
            return true;                                  // skipped — keep going
        });
}

lines.stream().gather(distinctBy(OrderLine::sku)).toList();''', title="DistinctBy.java", size=24)
              + frag(bullets(["`ofSequential` — mutable state, no combiner, never parallelised (correctly)",
                              "Return `downstream.push(...)`, not `true` — so a `limit(10)` stops everything"], cls="bullets sm"), 1),
         narration=[
             "Writing your own is short. Here's distinctBy, the most-wanted missing operation. The initializer creates a HashSet of seen keys. The integrator adds each element's key, and pushes the element only if the key is new.",
             "Two details matter. It uses ofSequential, because a mutable set has no sensible combiner, so it's never parallelised. That's correct, not a limitation. "
             "And it returns the result of push, not true, so if a limit of ten downstream is satisfied, the whole pipeline stops.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Built-ins first: `windowFixed`, `scan`, `fold`",
                         "`mapConcurrent` for I/O fan-out in a stream",
                         "`ofSequential` for mutable state",
                         "Return `downstream.push(...)`",
                         "Package reusable gatherers as static factories"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`parallelStream` for blocking I/O",
                         "A gatherer where `map` or `filter` will do",
                         "Shared mutable state outside the initializer",
                         "Ignore `push` returning false"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Reach for the built-ins first. Use mapConcurrent for I/O fan-out inside a stream. Use ofSequential for mutable state. Return the result of push. And package reusable gatherers as static factory methods.",
             "Never use parallelStream for blocking I/O. Don't write a gatherer where map or filter would do. Keep state inside the initializer, never shared outside it. And never ignore push returning false.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 38 · Stream Gatherers",
         body=bullets(["A `Gatherer` extends the **middle** of a stream",
                       "initializer, integrator, combiner, finisher",
                       "`windowFixed`, `windowSliding`, `scan`, `fold`",
                       "`mapConcurrent`: bounded, ordered I/O on virtual threads",
                       "Next: **Ch 39 · FFM &amp; the Vector API**"], cls="bullets recap"),
         narration=[
             "To recap. A gatherer extends the middle of a stream, with an initializer, integrator, combiner and finisher. The built-ins handle windows, scans and folds. "
             "And mapConcurrent gives bounded, ordered I/O on virtual threads, right inside a pipeline.",
             "Next is chapter thirty-nine: the foreign function and memory API, and the Vector API. Thanks for watching.",
         ]),
]
