"""Chapter 08 — Collectors & Stream Composition. Source: docs/02-language/08-collectors.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 08 · Collectors & Stream Composition"
SECTION = "Java 8"

SLIDES = [
    dict(kind="title",
         title="Collectors &amp; Stream Composition",
         kicker="Java 8 · Chapter 08",
         body='<p class="sub">What a <code>Collector</code> is made of, how downstream collectors compose into '
              'multi-level reports, and the traps hiding in <code>toMap</code>.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter eight: collectors and stream composition.",
             "Most developers learn three collectors, toList, toSet and toMap, and then drop out of the stream to finish the job with a loop. "
             "That's exactly where streams stop paying off, because grouping, partitioning and multi-level aggregation are what collect was designed for.",
         ]),

    dict(title="Why collect, not reduce",
         kicker="The problem",
         body=code('''
Map<String, Map<DeliverySlot, Money>> report = new HashMap<>();
for (Order order : orders) {
    for (OrderLine line : order.lines()) {
        report.computeIfAbsent(line.vendorName(), v -> new HashMap<>())
              .merge(order.slot(), line.lineTotal(), Money::plus);
    }
}''', title="ManualGrouping.java", size=27)
              + '<div class="grid2">'
              + card("reduce replaces", "Expects a **new value** each step. Building a map that way copies it per element — O(n²).", "fuchsia", 1)
              + card("collect mutates", "**Mutable reduction**: create a container once, mutate it as elements arrive.", "indigo", 2)
              + "</div>",
         narration=[
             "The task: total revenue per vendor, per delivery slot. The loop works, but it's nested container management, "
             "and every variation, a third level, a filter, a count instead of a sum, means restructuring it.",
             "Reduce can't help. It expects a brand-new value at every step, so building a map with it means copying the map for every element. That's quadratic.",
             "Collect exists for this. It's mutable reduction: create one container, then mutate it as elements arrive. "
             "Use reduce for values, like a sum or a maximum, and collect for containers.",
         ]),

    dict(title="A Collector is five things",
         kicker="Mental model",
         body=table(["Part", "Signature", "For toList()"], [
                    ["**supplier**", "`() -> A`", "`ArrayList::new`"],
                    ["**accumulator**", "`(A, T) -> void`", "`List::add`"],
                    ["**combiner**", "`(A, A) -> A`", "`a.addAll(b)` — parallel only"],
                    ["**finisher**", "`A -> R`", "identity — nothing to do"],
                    ["**characteristics**", "hints", "`IDENTITY_FINISH`"],
                ], step_per_row=0)
              + frag('<p class="callout">The combiner <b>only runs in parallel</b> — a broken one passes every sequential test.</p>', 5),
         narration=[
             "A Collector isn't one function. It's five. The supplier creates an empty container, like a new ArrayList.",
             "The accumulator folds one element into it, like list dot add.",
             "The combiner merges two containers. That's only used in parallel, when each thread has its own container.",
             "The finisher turns the container into the final result. For toList there's nothing to do.",
             "And characteristics are hints to the stream, like identity finish, meaning the container is the result.",
             "Remember this one fact: the combiner only runs in parallel. A sequential stream uses a single container throughout. "
             "So a broken combiner passes every test, then corrupts data the day someone adds parallel.",
         ]),

    dict(title="Downstream collectors compose",
         kicker="The real feature",
         body=code('groupingBy(OrderLine::vendorName, /* downstream */ ...)', size=34)
              + '<div class="grid4">'
              + card("toList()", "`Map<String, List<OrderLine>>`", "indigo", 1)
              + card("counting()", "`Map<String, Long>`", "cyan", 1)
              + card("mapping(...)", "`Map<String, Set<Sku>>`", "fuchsia", 1)
              + card("groupingBy(...)", "`Map<String, Map<Slot, …>>`", "amber", 2)
              + "</div>",
         narration=[
             "Here's the feature that makes the API compose. groupingBy takes a classifier, and an optional second collector, called the downstream, "
             "that decides what each group becomes.",
             "With toList, each vendor maps to a list of lines. With counting, to a count. With mapping, to a set of SKUs.",
             "And the downstream can be another groupingBy. That's how you nest to any depth, with no special support needed.",
         ]),

    dict(title="Grouping in one pass",
         kicker="Worked examples",
         body=code('''
Map<String, Money> revenueByVendor = lines.stream()
    .collect(groupingBy(OrderLine::vendorName,
             reducing(Money.ZERO, OrderLine::lineTotal, Money::plus)));
// {Amul=₹1,240.00, ITC=₹890.00, Tata=₹3,105.00}''', title="VendorTotals.java", size=27)
              + code('''
Map<String, Map<DeliverySlot, Money>> report = slotLines.stream()
    .collect(groupingBy(sl -> sl.line().vendorName(),
             groupingBy(SlotLine::slot,
                 reducing(Money.ZERO, sl -> sl.line().lineTotal(), Money::plus))));''',
                     title="RevenueReport.java", step=1, size=27)
              + code('''
groupingBy(OrderLine::vendorName, TreeMap::new, reducing(...))   // sorted keys, no second pass''',
                     title="SortedReport.java", step=2, size=27),
         narration=[
             "Revenue per vendor: group by vendor name, with a downstream reducing collector. "
             "The three-argument reducing is the one to remember: an identity, a mapper, and an operator. Zero, line total, plus.",
             "The two-level report from the loop is just a groupingBy inside a groupingBy. Past two levels, extract a record and a named method, "
             "because the type signature stops being readable.",
             "groupingBy returns a HashMap, so key order is unspecified. If order matters, pass a map factory like TreeMap new, instead of sorting afterwards.",
         ]),

    dict(title="Shape inside the group",
         kicker="mapping · filtering · flatMapping",
         body=code('''
groupingBy(OrderLine::vendorName, mapping(OrderLine::sku, toSet()))           // SKUs per vendor
groupingBy(OrderLine::vendorName, flatMapping(l -> l.substitutes().stream(), toList()))  // Java 9''',
                   title="DownstreamShaping.java", size=24)
              + '<div class="grid2 start">'
              + frag(code('''
lines.stream()
    .filter(OrderLine::perishable)
    .collect(groupingBy(OrderLine::vendorName));''', title="Filter first", size=22)
                     + '<p class="callout" style="margin-top:16px">Vendors with no perishables <b>disappear</b>.</p>', 1)
              + frag(code('''
lines.stream()
    .collect(groupingBy(OrderLine::vendorName,
             filtering(OrderLine::perishable, toList())));''', title="filtering downstream (9)", size=22)
                     + '<p class="callout" style="margin-top:16px">Every vendor stays — some with an <b>empty list</b>.</p>', 2)
              + "</div>",
         narration=[
             "Three downstream collectors shape elements inside each group, after classification. Mapping transforms them, like collecting each vendor's SKUs into a set. "
             "Java 9 added flatMapping, which flattens, and filtering.",
             "Filtering is the subtle one. If you filter before grouping, vendors whose lines are all non-perishable disappear from the map entirely.",
             "If you use filtering as the downstream, every vendor stays as a key, some with an empty list. "
             "Which one you want depends on whether the report should show vendors with zero perishables. The two spellings look almost identical, which is how the bug happens.",
         ]),

    dict(title="partitioningBy",
         kicker="A yes/no split",
         body=code('''
Map<Boolean, List<CartLine>> byStock = cart.lines().stream()
    .collect(partitioningBy(line -> catalogue.availableQuantity(line.sku()) > 0));

List<CartLine> fulfillable = byStock.get(true);
List<CartLine> backordered = byStock.get(false);   // never null, even if empty

Map<Boolean, Long> counts = lines.stream().collect(partitioningBy(CartLine::perishable, counting()));''',
                   title="StockSplit.java", size=26)
              + frag('<p class="callout"><code>partitioningBy</code> always has <b>both</b> keys. '
                     '<code>groupingBy</code> on a boolean leaves absent groups out — <code>get(false)</code> can be null.</p>', 1),
         narration=[
             "For a yes or no split, use partitioningBy. Split the cart into lines we can fulfil and lines that are backordered. "
             "It takes a downstream too, so you can count instead of listing.",
             "The reason to prefer it over groupingBy with a boolean: partitioningBy always returns both keys, true and false, even when one side is empty. "
             "groupingBy leaves absent groups out, so get false can return null.",
         ]),

    dict(title="toMap: three traps",
         kicker="Worked example",
         body=code('''
toMap(OrderLine::sku, identity())                        // 1. duplicate key → IllegalStateException

toMap(OrderLine::sku, identity(),
      (a, b) -> a.withQuantity(a.quantity() + b.quantity()))   // merge function decides

toMap(OrderLine::sku, identity(), (a, b) -> a, LinkedHashMap::new)   // keep encounter order''',
                   title="ToMapTraps.java", size=26)
              + bullets(["**Duplicate keys throw** at runtime — on data your tests rarely have",
                         "**Null values throw** `NullPointerException`, though `HashMap` accepts them",
                         "**The result is a `HashMap`** — order unspecified unless you pass a factory"], start_step=0, cls="bullets sm"),
         narration=[
             "toMap has three separate failure modes. First, duplicate keys throw an IllegalStateException at runtime, on whatever data triggers it, "
             "which is rarely the data in your tests. Always supply a merge function unless keys are structurally unique.",
             "Second, null values throw a NullPointerException, even though a HashMap would accept them, because toMap uses map dot merge internally. Filter or default them first.",
             "Third, the result is a HashMap, so iteration order is unspecified. Pass LinkedHashMap new as the fourth argument if order matters.",
         ]),

    dict(title="teeing &amp; collectingAndThen",
         kicker="Composition",
         body=code('''
record PriceRange(Money cheapest, Money dearest) {}

PriceRange range = lines.stream().map(OrderLine::lineTotal)
    .collect(teeing(minBy(Money::compareTo), maxBy(Money::compareTo),
                    (min, max) -> new PriceRange(min.orElse(Money.ZERO), max.orElse(Money.ZERO))));''',
                   title="Teeing.java — Java 12", size=25)
              + code('''
double perishableShare = lines.stream()
    .collect(teeing(filtering(OrderLine::perishable, counting()), counting(),
                    (p, total) -> total == 0 ? 0.0 : (double) p / total));''', title="Ratio in one pass", step=1, size=25)
              + code('''
groupingBy(OrderLine::vendorName, collectingAndThen(toList(), List::copyOf))   // immutable groups''',
                     title="Immutable.java", step=2, size=25),
         narration=[
             "Java 12's teeing feeds every element to two collectors at once, then merges their results. "
             "Here, min and max in a single pass, combined into a price range record. Before Java 12 that meant two traversals or a hand-written collector.",
             "It's also the clean way to compute a ratio: count the perishable lines and count all lines in the same pass, then divide, guarding against zero.",
             "And collectingAndThen collects, then transforms the result. Here, each group becomes an immutable list. It allocates twice, which matters on a hot path but not for a report.",
         ]),

    dict(title="Writing your own",
         kicker="Only when composition won't do",
         body=code('''
static <T> Collector<T, ?, List<T>> topN(int n, Comparator<T> cmp) {
    return Collector.of(
        () -> new PriorityQueue<T>(cmp),                       // supplier: heap of size n
        (q, item) -> { q.offer(item); if (q.size() > n) q.poll(); },   // accumulator
        (a, b) -> { b.forEach(i -> { a.offer(i); if (a.size() > n) a.poll(); }); return a; },
        q -> q.stream().sorted(cmp.reversed()).toList());      // finisher
}''', title="TopNCollector.java", size=25)
              + '<div class="grid2">'
              + card("Why it's worth it", "`sorted().limit(n)` buffers the whole stream. This keeps **O(n)** memory.", "indigo", 1)
              + card("Combiner laws", "**Associative**, and consistent with the accumulator. `(a, b) -> a` silently drops `b`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Write your own collector only when no combination of the built-ins fits. A bounded top-N is a good example. "
             "The supplier is a priority queue. The accumulator adds each item and evicts the smallest once it holds more than n. The finisher sorts what's left.",
             "It's worth it because sorted then limit buffers the entire stream. This keeps memory proportional to n.",
             "The combiner is the part people get wrong. It must be associative, and consistent with accumulating everything in one container. "
             "A combiner that just returns a silently drops everything in b, and only in parallel, so no sequential test will ever catch it.",
         ]),

    dict(title="Internals worth knowing",
         kicker="Characteristics · list flavours",
         body='<div class="grid2 start">'
              + frag(table(["Characteristic", "Effect"], [
                    ["`IDENTITY_FINISH`", "Finisher skipped"],
                    ["`UNORDERED`", "Cheaper parallel merging"],
                    ["`CONCURRENT`", "One shared container — no merge tree"],
                ], cls="sm")
                + '<p class="callout" style="margin-top:20px"><code>groupingByConcurrent</code> on a sequential stream is strictly worse.</p>', 0)
              + frag(table(["", "Mutable", "Nulls"], [
                    ["`Collectors.toList()`", "In practice", "Yes"],
                    ["`toUnmodifiableList()`", "No", "**No**"],
                    ["`Stream.toList()` (16)", "No", "Yes"],
                ], cls="sm"), 1)
              + "</div>",
         narration=[
             "Two internals worth knowing. Characteristics: identity finish skips the finisher. Unordered makes parallel merging cheaper. "
             "And concurrent lets every thread write into one shared container, skipping the merge tree. "
             "That helps only on large parallel streams with many small groups. On a sequential stream, groupingByConcurrent is strictly worse.",
             "And the three ways to get a list. Collectors dot toList is mutable in practice, but the spec doesn't promise it. "
             "toUnmodifiableList rejects nulls. Stream dot toList, from Java 16, is unmodifiable and allows nulls, which makes it the right default.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Give `toMap` a merge function",
                         "`counting()`, not `summingInt(x -> 1)`",
                         "`summarizingInt` or `teeing` for several aggregates",
                         "Pass a map factory when order matters",
                         "Name multi-level groupings as methods",
                         "Prefer `Stream.toList()`"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Build a container with `reduce`",
                         "Write a combiner you haven't thought about",
                         "Use `collect` for side effects",
                         "Assume `groupingBy` key order",
                         "Feed null values to `toMap`",
                         "Hand-write what composition already does"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Always give toMap a merge function. Use counting, not summing ones. Use summarizingInt or teeing when you need several aggregates in one pass. "
             "Pass a map factory when order matters. Name multi-level groupings as methods. And prefer Stream dot toList for simple lists.",
             "Never build a container with reduce. Never write a combiner you haven't thought through. Never use collect for side effects, like saving as you accumulate. "
             "Never assume groupingBy's key order. Never feed null values to toMap. And never hand-write a collector when mapping, filtering, teeing and collectingAndThen already cover it.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "`groupingBy`, `partitioningBy`, `toMap`, `joining`, `mapping`, `reducing`"],
                    ["**9**", "`flatMapping`, `filtering` — downstream shaping"],
                    ["**10**", "`toUnmodifiableList/Set/Map` — immutable but null-hostile"],
                    ["**12**", "`teeing` — two collectors, one pass"],
                    ["**16**", "`Stream.toList()` — a terminal op, not a collector"],
                    ["**24**", "Stream Gatherers — custom intermediate operations (Ch 38)"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 shipped the core collectors: groupingBy, partitioningBy, toMap, joining, mapping and reducing.",
             "Java 9 added flatMapping and filtering for shaping inside groups.",
             "Java 10 added the unmodifiable collectors. Immutable, but they reject nulls.",
             "Java 12 added teeing.",
             "Java 16 added Stream dot toList. When migrating, check nobody adds to the result, because the old collector's list was mutable and the new one throws at runtime.",
             "And Java 24 finalised stream gatherers, the mirror image of custom collectors, for intermediate operations. That's chapter thirty-eight.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 08 · Collectors &amp; Stream Composition",
         body=bullets(["`collect` mutates a container; `reduce` produces values",
                       "A collector = supplier, accumulator, **combiner**, finisher, characteristics",
                       "**Downstream collectors** nest to any depth",
                       "`filtering` downstream keeps empty groups; filtering first drops them",
                       "`toMap`: merge function, no nulls, `HashMap` order",
                       "Next: **Ch 09 · Optional & Null Strategy**"], cls="bullets recap"),
         narration=[
             "To recap. Collect mutates a container, while reduce produces values. A collector is five parts, and the combiner only runs in parallel. "
             "Downstream collectors let groupingBy nest to any depth. Filtering as a downstream keeps empty groups, and filtering first drops them. "
             "And toMap needs a merge function, rejects nulls, and has no order unless you ask for one.",
             "Next is chapter nine, Optional and null strategy. Thanks for watching.",
         ]),
]
