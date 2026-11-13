"""Chapter 17 — Choosing the Right Collection. Source: docs/03-collections/17-choosing-a-collection.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 17 · Choosing the Right Collection"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="Choosing the Right Collection",
         kicker="Collections · Chapter 17",
         body='<p class="sub">Four questions that pick the implementation — and what each one actually guarantees about '
              'order, nulls and speed.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter seventeen: choosing the right collection.",
             "Most Java code uses ArrayList, HashMap, and occasionally HashSet. That's usually right, which is why the habit persists. "
             "And it's why the cases where it's wrong go unnoticed, until something is slow, iterates in a surprising order, or throws on a null.",
         ]),

    dict(title="Four defects, four unasked questions",
         kicker="The problem",
         body=code('''
List<Sku> discontinued = loadDiscontinued();       // 40,000 entries
if (discontinued.contains(line.sku())) { ... }     // 1. scans 40,000 per cart line

prices.forEach((sku, price) -> writeCsvRow(sku, price));   // 2. HashMap: order changes

Map.of(milk, price1).get(null);                    // 3. throws — Map.of is null-hostile

List<Order> queue = new LinkedList<>();
queue.get(queue.size() - 1);                       // 4. O(n) on a linked list''', title="Defects.java", size=26),
         narration=[
             "Here are four defects. A membership test on a forty-thousand-element list, inside a loop, so it's quadratic overall. "
             "A HashMap exported to CSV, whose order changes between runs. A lookup of null on Map dot of, which throws. "
             "And indexed access on a LinkedList, which walks the list every time. None of these is subtle. Each is just one question nobody asked.",
         ]),

    dict(title="The four questions, in order",
         kicker="Mental model",
         body=flow(["**1. Key-value or values?**\n`Map` vs `Collection`",
                    "**2. Duplicates?**\n`List` vs `Set`",
                    "**3. What order?**\ninsertion · sorted · unspecified",
                    "**4. Concurrent?**\nplain · concurrent · immutable"], step_start=0)
              + frag('<p class="callout">Most wrong choices skip question 3 — mistaking <b>unspecified</b> for <b>insertion</b> order.</p>', 4),
         narration=[
             "Ask four questions, in order. First: key-value pairs, or just values? That decides Map versus Collection. "
             "Map isn't a Collection at all, because it holds pairs, not elements.",
             "Second: are duplicates allowed? That decides List versus Set.",
             "Third: what order do you need? Insertion order, sorted order, or don't care.",
             "Fourth: will it be accessed concurrently? Plain, concurrent, or immutable.",
             "Answer those and the implementation is almost always decided. Most wrong choices come from skipping question three, and mistaking unspecified order for insertion order.",
         ]),

    dict(title="Pick by intent",
         kicker="Core reference",
         body=table(["You need", "Use"], [
                    ["A sequence, indexed access", "`ArrayList`"],
                    ["A queue, stack or deque", "`ArrayDeque`"],
                    ["Uniqueness — any order · insertion order · sorted", "`HashSet` · `LinkedHashSet` · `TreeSet`"],
                    ["Key-value — any order · insertion order · sorted", "`HashMap` · `LinkedHashMap` · `TreeMap`"],
                    ["Enum keys", "`EnumMap` / `EnumSet`"],
                    ["Highest priority next", "`PriorityQueue`"],
                    ["Shared mutable map", "`ConcurrentHashMap`"],
                    ["Small, fixed, never modified", "`List.of` / `Set.of` / `Map.of`"],
                ], step_per_row=None, cls="pairs"),
         narration=[
             "Here's the cheat sheet by intent. A sequence with indexed access: ArrayList. A queue, stack or deque: ArrayDeque. "
             "For uniqueness, HashSet when order doesn't matter, LinkedHashSet for insertion order, TreeSet for sorted. The same three-way split applies to maps. "
             "EnumMap and EnumSet for enum keys. PriorityQueue when you always want the highest priority item next. ConcurrentHashMap for a shared mutable map. "
             "And List dot of, Set dot of and Map dot of for small fixed collections.",
         ]),

    dict(title="Nulls and order: the traps",
         kicker="Core reference",
         body='<div class="grid2 start">'
              + frag(table(["Rejects null", ""], [
                    ["`TreeSet`, `TreeMap` keys", "Need to compare"],
                    ["`ArrayDeque`", "null means empty"],
                    ["`ConcurrentHashMap`", "Keys **and** values"],
                    ["`List.of` / `Set.of` / `Map.of`", "Even `contains(null)` throws"],
                ], cls="sm"), 0)
              + frag(table(["Order surprise", ""], [
                    ["`HashMap`, `HashSet`", "**Unspecified** — changes with capacity"],
                    ["`Set.of`, `Map.of`", "**Randomised** per JVM run"],
                    ["`PriorityQueue`", "Iteration is **heap** order — only `poll()` is sorted"],
                ], cls="sm"), 1)
              + "</div>",
         narration=[
             "Two tables people actually need. Nulls: TreeSet and TreeMap keys reject null, because they must be compared. ArrayDeque rejects it. "
             "ConcurrentHashMap rejects null keys and values, so swapping it in for a HashMap can break code that stored nulls. "
             "And the immutable factories reject nulls so strictly that even contains null throws instead of returning false.",
             "Order: HashMap and HashSet order is unspecified, and changes as the map grows. Set dot of and Map dot of randomise it on every JVM run, on purpose. "
             "And PriorityQueue is the sneaky one. It's a heap, so iterating it gives heap order. Only repeated poll gives you sorted order. That often looks right on small inputs.",
         ]),

    dict(title="Membership → Set · ranges → TreeMap",
         kicker="Worked examples",
         body=code('''
Set<Sku> discontinued = Set.copyOf(loadDiscontinued());
boolean stopped = discontinued.contains(line.sku());        // O(1), not a 40,000-element scan''',
                   title="MembershipTest.java", size=25)
              + code('''
NavigableMap<LocalTime, DeliverySlot> slots = new TreeMap<>();
slots.subMap(LocalTime.of(9, 0), LocalTime.of(12, 0));      // every slot in the morning
slots.ceilingEntry(LocalTime.of(10, 15));                    // next slot at or after 10:15
slots.lowerEntry(LocalTime.of(21, 0));                       // last slot before closing''',
                     title="RangeQueries.java", step=1, size=25),
         narration=[
             "Two fixes. If a collection exists only to answer, is this in it, make it a Set. Change one word, and a forty-thousand-element scan per cart line becomes a hash lookup.",
             "And choose TreeMap for range queries, not just sorted iteration. Every slot between nine and twelve. The next slot at or after ten fifteen. The last one before closing. "
             "A HashMap can't answer any of those without scanning everything. The log n cost buys a whole category of query.",
         ]),

    dict(title="EnumMap, EnumSet &amp; copies vs views",
         kicker="Worked examples",
         body=code('''
Map<OrderStatus, Integer> counts = new EnumMap<>(OrderStatus.class);   // array by ordinal
Set<OrderStatus> terminal = EnumSet.of(DELIVERED, CANCELLED);           // a bitset — one long''',
                   title="EnumCollections.java", size=25)
              + code('''
List<Sku> b = List.copyOf(mutableList);                    // immutable snapshot
List<Sku> c = Collections.unmodifiableList(mutableList);   // read-only VIEW

mutableList.add(atta);    // b unchanged — c now has three elements''', title="Immutability.java", step=1, size=25)
              + frag('<p class="callout">For accessors, <b>copy</b>. An unmodifiable view still leaks every later change.</p>', 1),
         narration=[
             "For enum keys, EnumMap and EnumSet are strictly better than the hash versions. EnumMap is an array indexed by ordinal, with no hashing. "
             "EnumSet is a bitset, so a set of up to sixty-four constants is a single long, and contains is one bit test. They're underused only because habit wins.",
             "And know the difference between a copy and a view. List dot copyOf is a real snapshot. Collections dot unmodifiableList is a read-only view, "
             "so the caller can't write, but sees every later change to the original. For accessors, return a copy.",
         ]),

    dict(title="Never use these",
         kicker="Legacy",
         body=table(["Legacy", "Why", "Use instead"], [
                    ["`Vector`", "Synchronises every method; Java 1.0", "`ArrayList`"],
                    ["`Hashtable`", "Same, plus null-hostile", "`HashMap` / `ConcurrentHashMap`"],
                    ["`Stack`", "Extends `Vector`; **iterates bottom-to-top**", "`ArrayDeque`"],
                    ["`LinkedList`", "Almost always slower; poor cache locality", "`ArrayList` / `ArrayDeque`"],
                ], step_per_row=0, cls="sm"),
         narration=[
             "Four collections never to use in new code. Vector synchronises every single method. It's from Java 1.0. Use ArrayList.",
             "Hashtable has the same problem, and rejects nulls too. Use HashMap, or ConcurrentHashMap if it's shared.",
             "Stack extends Vector, and iterates from the bottom up, the opposite of pop order. Use ArrayDeque.",
             "And LinkedList is almost always slower than ArrayList, because of poor cache locality. The next chapter shows why.",
         ]),

    dict(title="Internals worth knowing",
         kicker="Interfaces · RandomAccess · fail-fast · sizing",
         body='<div class="grid2">'
              + card("Program to the interface", "`List<CartLine> lines = new ArrayList<>()` — swap to `LinkedHashMap` or `ConcurrentHashMap` without touching callers.", "indigo", 0)
              + card("RandomAccess", "Index-looping an arbitrary `List` is O(n²) on a linked list. Check the marker, or iterate.", "cyan", 1)
              + card("Fail-fast is best-effort", "`ConcurrentModificationException` is a **bug detector**, not synchronisation. Never depend on it.", "fuchsia", 2)
              + card("Size it", "`new HashMap<>(n)` takes a **capacity**. Use `HashMap.newHashMap(n)` (Java 19).", "amber", 3)
              + "</div>",
         narration=[
             "A few internals. Declare fields as interfaces, like List or Map. Then you can switch to LinkedHashMap when order starts to matter, or ConcurrentHashMap when it becomes shared, without touching callers.",
             "ArrayList implements a marker interface called RandomAccess, and LinkedList doesn't. Generic code that index-loops over any List is quadratic on a linked list.",
             "Fail-fast iterators throw ConcurrentModificationException on a best-effort basis. It's a bug detector, not a synchronisation mechanism.",
             "And sizing. new HashMap of n takes a capacity, not a count, so it resizes at seventy-five percent. Java 19's HashMap dot newHashMap of n does the arithmetic for you.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Ask the four questions",
                         "A `Set` for membership tests",
                         "`TreeMap` / `TreeSet` for range queries",
                         "`EnumMap` / `EnumSet` for enum keys",
                         "Return `List.copyOf(...)` from accessors",
                         "`ArrayDeque` for stacks and queues"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Rely on `HashMap` / `HashSet` order",
                         "Assume `Set.of` / `Map.of` order",
                         "`contains(null)` on `List.of`",
                         "Iterate a `PriorityQueue` expecting sorted",
                         "`Vector`, `Hashtable`, `Stack`",
                         "`LinkedList` by default"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Ask the four questions. Use a Set for membership tests, TreeMap and TreeSet for range queries, and EnumMap and EnumSet for enum keys. "
             "Return copies from accessors. And use ArrayDeque for stacks and queues.",
             "Never rely on HashMap or HashSet order, or on Set dot of and Map dot of order. Never call contains null on List dot of. "
             "Never iterate a PriorityQueue expecting sorted output. Never use Vector, Hashtable or Stack. And don't reach for LinkedList by default.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 17 · Choosing the Right Collection",
         body=bullets(["Four questions: **key-value · duplicates · order · concurrency**",
                       "Membership → `Set`; ranges → `TreeMap`; enums → `EnumMap`",
                       "Unspecified order is **not** insertion order",
                       "Know which collections reject `null`",
                       "Next: **Ch 18 · List Internals**"], cls="bullets recap"),
         narration=[
             "To recap. Ask four questions: key-value, duplicates, order, and concurrency. Use a Set for membership, TreeMap for ranges, and EnumMap for enum keys. "
             "Remember that unspecified order is not insertion order, and know which collections reject null.",
             "Next is chapter eighteen, list internals, where we look inside ArrayList and LinkedList. Thanks for watching.",
         ]),
]
