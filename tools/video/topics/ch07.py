"""Chapter 07 — The Stream API. Source: docs/02-language/07-stream-api.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 07 · The Stream API"
SECTION = "Java 8"

SLIDES = [
    dict(kind="title",
         title="The Stream API",
         kicker="Java 8 · Chapter 07",
         body='<p class="sub">What a stream really does, when it beats a loop, and why '
              '<code>parallel()</code> usually doesn\'t help.</p>',
         narration=[
             "Welcome back to the Modern Java Enterprise Handbook. This is chapter seven: the Stream API.",
             "Streams are the most used, and most misused, part of Java 8. The API is easy to learn, but the mental model isn't. "
             "Get it wrong and you write pipelines that are slower than the loop they replaced, or that nobody can read. Let's fix the mental model first.",
         ]),

    dict(title="What, not how",
         kicker="The problem",
         body=code('''
Map<String, BigDecimal> totalsByVendor = new HashMap<>();
for (CartLine line : cart.lines()) {
    if (!line.perishable()) continue;
    BigDecimal current = totalsByVendor.get(line.vendorName());
    if (current == null) current = BigDecimal.ZERO;
    totalsByVendor.put(line.vendorName(), current.add(line.lineTotal().amount()));
}''', title="ImperativeTotals.java — Java 7", size=27)
              + code('''
Map<String, BigDecimal> totalsByVendor = cart.lines().stream()
    .filter(CartLine::perishable)
    .collect(groupingBy(CartLine::vendorName,
             reducing(BigDecimal.ZERO, l -> l.lineTotal().amount(), BigDecimal::add)));''',
                     title="StreamTotals.java — Java 8", step=1, size=27),
         narration=[
             "Here's the task: total the value of perishable cart lines, grouped by vendor. In Java 7, that's a loop with a continue, "
             "a map lookup, a null check, and a put. Only two ideas matter, filter to perishable and sum by vendor. Everything else is mechanics, and every line is a place to make a mistake.",
             "The stream version states those two ideas directly: filter, then group by vendor and add up the totals. "
             "The win isn't fewer lines. It's that the what is visible and the how is gone.",
         ]),

    dict(title="A stream is a pipeline, not a collection",
         kicker="Mental model",
         body=flow(["**Source**\ncollection · array · generator · file",
                    "**Intermediate**\n`filter` · `map` · `sorted` — lazy",
                    "**Terminal**\n`collect` · `reduce` · `forEach` — runs it all"], step_start=0)
              + table(["", "Collection", "Stream"], [
                    ["Stores elements", "Yes", "No"],
                    ["Reusable", "Yes", "**No** — one terminal operation"],
                    ["Evaluation", "Eager", "Lazy"],
                    ["Size", "Known", "May be infinite"],
                ], step_per_row=3),
         narration=[
             "A stream is not a collection. It's a pipeline description. It starts with a source: a collection, an array, a generator, or a file.",
             "Then come intermediate operations, like filter, map and sorted. These are lazy. Calling them just builds up the pipeline. Nothing runs yet.",
             "Nothing happens until a terminal operation, like collect, reduce or forEach, pulls elements through the whole pipeline.",
             "So compared with a collection, a stream stores nothing.",
             "It can't be reused. Call a second terminal operation and you get an IllegalStateException.",
             "It's evaluated lazily, not eagerly.",
             "And it can even be infinite, as long as something downstream stops it.",
         ]),

    dict(title="Laziness changes the order",
         kicker="Mental model · one element at a time",
         body='<div class="grid2 start">'
              + code('''
List<String> skus = List.of(
    "MILK-1L", "RICE-5KG",
    "ATTA-10KG", "DAL-1KG");

skus.stream()
    .peek(s -> print("filter sees " + s))
    .filter(s -> s.startsWith("A"))
    .peek(s -> print("map sees " + s))
    .map(String::toLowerCase)
    .findFirst();''', title="LazinessDemo.java", size=28)
              + frag(code('''
filter sees MILK-1L
filter sees RICE-5KG
filter sees ATTA-10KG
map sees ATTA-10KG''', lang="text", title="Output", size=30)
                     + '<div style="height:24px"></div>'
                     + bullets(["`DAL-1KG` is **never examined** — `findFirst` short-circuits",
                                "`map` runs on element 3 **before** `filter` sees element 4"], cls="bullets sm"), 1)
              + "</div>",
         narration=[
             "The most important idea in this chapter: elements flow through the whole pipeline one at a time, not stage by stage. "
             "Here we print what filter sees and what map sees, then ask for the first SKU starting with A.",
             "Look at the output. Filter sees milk, then rice, then atta. Atta passes, map sees it, and we're done. "
             "Two surprises. Dal is never examined at all, because findFirst short-circuits. "
             "And map runs on the third element before filter has even seen the fourth. "
             "If you picture filter everything, then map everything, you'd predict neither.",
         ]),

    dict(title="The operations that matter",
         kicker="Core API",
         body='<div class="grid2 start">'
              + frag(table(["Intermediate", "Kind"], [
                    ["`filter`, `map`, `flatMap`", "Stateless"],
                    ["`peek`", "Debugging only"],
                    ["`distinct`, `sorted`, `skip`", "**Stateful**"],
                    ["`limit`, `takeWhile` (9)", "Short-circuiting"],
                    ["`mapMulti` (16)", "Fewer allocations than `flatMap`"],
                ], cls="sm"), 0)
              + frag(table(["Terminal", "Returns"], [
                    ["`collect`, `toList()` (16)", "A collection — `toList` is unmodifiable"],
                    ["`reduce`, `count`", "A single value"],
                    ["`min`, `max`, `findFirst`", "`Optional<T>`"],
                    ["`anyMatch`, `allMatch`", "`boolean`, short-circuits"],
                    ["`mapToInt(...).sum()`", "Primitive — no boxing"],
                ], cls="sm"), 1)
              + "</div>"
              + frag('<p class="callout">Stateful operations break laziness: <code>sorted()</code> must read the '
                     'entire stream before it emits anything.</p>', 2),
         narration=[
             "A quick tour of the API. Filter, map and flatMap are stateless. Each element is handled on its own. "
             "Distinct, sorted and skip are stateful, because they have to remember what they've seen. "
             "Limit and takeWhile short-circuit, and peek is for debugging only. We'll see why.",
             "On the terminal side, collect and Java 16's toList build collections, and toList is unmodifiable. "
             "Reduce and count give a single value. Min, max and findFirst return an Optional, because the stream might be empty. "
             "And for numbers, mapToInt then sum avoids boxing every element.",
             "One thing to remember: stateful operations break laziness. Sorted has to consume the entire stream before it can emit a single element.",
         ]),

    dict(title="map vs flatMap",
         kicker="Worked example",
         body=code('''
// map: one order → one list.            Result: Stream<List<OrderLine>>
Stream<List<OrderLine>> nested = orders.stream().map(Order::lines);

// flatMap: one order → many lines, merged. Result: Stream<OrderLine>
List<Sku> allSkus = orders.stream()
    .flatMap(order -> order.lines().stream())
    .map(OrderLine::sku)
    .distinct()
    .toList();''', title="MapVsFlatMap.java", size=28)
              + code('''
skus.stream()
    .map(catalogue::find)          // Stream<Optional<InventoryItem>>
    .flatMap(Optional::stream)     // Stream<InventoryItem>  — Java 9
    .toList();''', title="Flattening Optionals", step=1, size=28),
         narration=[
             "Map versus flatMap. Map is one in, one out. Mapping each order to its lines gives you a stream of lists, which usually isn't what you want. "
             "FlatMap takes a function that returns a stream, and merges all those streams into one. Now you have a flat stream of order lines you can map to SKUs and de-duplicate.",
             "The same trick flattens Optionals. Look up each SKU in the catalogue to get a stream of Optionals, "
             "then flatMap with Optional colon colon stream. Empty results simply disappear.",
         ]),

    dict(title="Infinite streams &amp; takeWhile",
         kicker="Worked examples",
         body=code('''
List<OrderId> ids = Stream.generate(OrderId::random).limit(5).toList();

Stream.iterate(10, n -> n <= 1000, n -> n * 2).toList();
// [10, 20, 40, 80, 160, 320, 640]''', title="InfiniteStream.java", size=28)
              + code('''
// newest first
byDateDesc.stream().filter(o -> o.placedAt().isAfter(monthStart)).toList();     // checks every order
byDateDesc.stream().takeWhile(o -> o.placedAt().isAfter(monthStart)).toList();  // stops at first old one''',
                     title="TakeWhile.java", step=1, size=25)
              + frag('<p class="callout"><code>takeWhile</code> on an <b>unsorted</b> stream is a bug — it silently drops later matches.</p>', 2),
         narration=[
             "Infinite streams are safe as long as something short-circuits. Stream dot generate with a limit of five gives five order IDs. "
             "Java 9's three-argument iterate takes a seed, a condition and a step, so the stream ends when the condition fails.",
             "TakeWhile is like filter, but it stops at the first element that fails. On a list sorted newest first, "
             "filter checks every order, while takeWhile stops at the first order from last month. Much cheaper.",
             "But only because the list is sorted. On an unsorted stream, takeWhile silently drops every later match. That's a bug no compiler will catch.",
         ]),

    dict(title="Two silent bugs",
         kicker="reduce identity · toMap duplicates",
         body=code('''
Money total = lines.stream().map(CartLine::lineTotal).reduce(Money.ZERO, Money::plus);
// identity op x must equal x — ZERO with plus ✓   ZERO with times ✗ (always zero)''',
                   title="Reduction.java", size=26)
              + code('''
// Throws IllegalStateException on a duplicate SKU — at runtime, on production data
lines.stream().collect(Collectors.toMap(CartLine::sku, line -> line));

// Always supply the merge function
lines.stream().collect(Collectors.toMap(CartLine::sku, line -> line,
        (a, b) -> a.withQuantity(a.quantity() + b.quantity())));''',
                     title="ToMapTrap.java", step=1, size=26),
         narration=[
             "Two bugs that tests rarely catch. First, reduce. The identity value must really be an identity: combining it with any x must give back x. "
             "Zero with plus is fine. But zero with times returns zero for every input. Silently.",
             "Second, Collectors dot toMap. A cart can legitimately have the same SKU on two lines. The two-argument toMap throws an IllegalStateException when that happens, "
             "at runtime, on data that's rarely in your tests. Always pass a merge function, here adding the quantities together, "
             "unless your keys are guaranteed unique. toMap also throws on null values, which a plain HashMap would accept.",
         ]),

    dict(title="Internals",
         kicker="Spliterator · fusion · peek",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Spliterator", "Traverses elements and **splits itself** for parallel work. Reports `SIZED`, `ORDERED`, `SORTED`…", "indigo", 0)
              + card("Fusion", "All stages run in **one pass**. No intermediate collections — one loop with function calls the JIT can inline.", "cyan", 1)
              + card("peek can vanish", "`peek(...).count()` may print nothing: since Java 9, `count()` can answer from `SIZED` without traversing.", "fuchsia", 2)
              + "</div>"
              + frag('<p class="callout">Use <code>peek</code> to observe while debugging. Never use it to do work.</p>', 2),
         narration=[
             "Under the hood, every stream is driven by a Spliterator. It traverses elements, and it can split itself in half for parallel work. "
             "It also reports characteristics, like sized, ordered and sorted, that let the pipeline skip work. If the source is already sorted, sorted becomes a no-op.",
             "Intermediate operations are fused into a single pass. Each element is pushed through every stage before the next one is read. "
             "So a three-stage stream isn't three loops. It's one loop with three function calls, which the JIT often inlines.",
             "And that's why peek is unreliable. The JDK may skip work it can prove unnecessary. Since Java 9, count can answer straight from the source's size, "
             "so a peek before it may never run. Use peek to observe while debugging. Never use it to do real work.",
         ]),

    dict(title="parallel(): measure first",
         kicker="The common ForkJoinPool",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Helps when…</div>'
              + bullets(["Large data — 10,000+ elements",
                         "CPU-bound, non-trivial work per element",
                         "Source splits cheaply: array, `ArrayList`",
                         "Operations are stateless and associative"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Hurts when…</div>'
              + bullets(["Work blocks on I/O — use virtual threads",
                         "The stream is small",
                         "`LinkedList` or generator sources",
                         "Inside a server request: the common pool is **shared JVM-wide**"], cls="bullets sm bad") + "</div>"
              + "</div>"
              + frag('<p class="callout">Default to sequential. Add <code>parallel()</code> when you have measured, not when the data looks big.</p>', 2),
         narration=[
             "Parallel streams run on the common ForkJoinPool, which has one thread fewer than your CPU cores and is shared by the whole JVM. "
             "Parallelism helps when the data is large, think ten thousand elements or more, when the work per element is real CPU work, "
             "when the source splits cheaply, like an array or ArrayList, and when the operations are stateless.",
             "It hurts when the work blocks on I/O, because the small pool just sits waiting. Use virtual threads or an executor for that. "
             "It hurts on small streams, on sources like LinkedList that split badly, and especially inside a server, "
             "where every request's parallel stream competes for that one shared pool.",
             "So the default answer is sequential. Add parallel when you've measured, not when the data looks big.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Use streams where the loop was ceremony",
                         "Prefer `toList()` (16) — but it's unmodifiable",
                         "Primitive streams for numbers",
                         "Always give `toMap` a merge function",
                         "Close `Files.lines` with try-with-resources",
                         "Extract long pipelines into named methods"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Reuse a stream",
                         "Use `peek` for side effects",
                         "Mutate a shared collection from `forEach`",
                         "Block inside a parallel stream",
                         "Infinite source without a short-circuit",
                         "Chain more than ~5 operations unnamed"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use streams where the loop was just ceremony around a filter, a transform or an aggregation. "
             "Prefer toList, but remember it's unmodifiable. Use primitive streams for numbers. Always give toMap a merge function. "
             "Close file streams like Files dot lines with try-with-resources, or you'll leak file handles. And extract long pipelines into well-named methods.",
             "Never reuse a stream. Never use peek for side effects. Never mutate a shared collection from forEach. Use collect instead, which is correct even in parallel. "
             "Never block inside a parallel stream. Never use an infinite source without a short-circuit. "
             "And if a pipeline is more than about five operations, give it a name. If you can't read it in one breath, the loop was better.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "Streams, primitive streams, `Collectors`, `parallelStream`"],
                    ["**9**", "`takeWhile`, `dropWhile`, bounded `iterate`, `Optional.stream()`; `count()` may skip traversal"],
                    ["**10–12**", "`toUnmodifiableList/Set/Map`; `Collectors.teeing`"],
                    ["**16**", "`Stream.toList()`, `mapMulti`"],
                    ["**21**", "Virtual threads — blocking work leaves parallel streams"],
                    ["**24**", "**Stream Gatherers** final — custom intermediate operations (Ch 38)"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 delivered streams, primitive streams, collectors and parallel streams.",
             "Java 9 added takeWhile, dropWhile, the bounded iterate, and Optional dot stream. It also let count skip traversal, which is what makes peek unreliable.",
             "Java 10 added unmodifiable collectors, and Java 12 added teeing, which runs two collectors in a single pass.",
             "Java 16 brought Stream dot toList and mapMulti. When migrating, check that nobody mutates the list, because the old collector returned a mutable ArrayList.",
             "Java 21's virtual threads gave blocking work a proper home, off parallel streams.",
             "And Java 24 finalised stream gatherers, so you can write your own intermediate operations, like windowing and running totals. That's chapter thirty-eight.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 07 · The Stream API",
         body=bullets(["A stream is a **lazy pipeline**: source → intermediate → terminal",
                       "Elements flow **one at a time**; short-circuits stop early",
                       "`flatMap` merges; `takeWhile` needs sorted input",
                       "Give `toMap` a merge function; check `reduce`'s identity",
                       "Sequential by default — `parallel()` only after measuring",
                       "Next: **Ch 08 · Collectors & Stream Composition**"], cls="bullets recap"),
         narration=[
             "To recap. A stream is a lazy pipeline: a source, intermediate operations, and a terminal operation that runs everything. "
             "Elements flow through one at a time, and short-circuiting operations stop early. "
             "FlatMap merges nested streams, and takeWhile only works on sorted input. "
             "Give toMap a merge function, and check that reduce's identity really is one. "
             "And stay sequential until you've measured that parallel helps.",
             "Next is chapter eight, collectors and stream composition, where most of the real work in collect happens. Thanks for watching.",
         ]),
]
