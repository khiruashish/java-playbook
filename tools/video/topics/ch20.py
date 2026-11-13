"""Chapter 20 — Set, Queue & Deque. Source: docs/03-collections/20-set-queue-deque.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 20 · Set, Queue & Deque"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="Set, Queue &amp; Deque",
         kicker="Collections · Chapter 20",
         body='<p class="sub">Membership, deduplication, stacks, work queues and "most urgent next" — the jobs code '
              'routinely does badly with a <code>List</code>.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty: sets, queues and deques.",
             "List and Map get most of the attention. These three interfaces cover jobs that code often solves badly with a list: "
             "membership tests, deduplication, stacks, work queues, and give me the most urgent item next.",
         ]),

    dict(title="Four jobs, four wrong structures",
         kicker="The problem",
         body=code('''
if (!unique.contains(sku)) unique.add(sku);   // dedupe with a List — O(n²)

Stack<Action> undo = new Stack<>();            // synchronised, iterates bottom-up

Queue<Order> pending = new LinkedList<>();     // a node per element

orders.add(order);
orders.sort(comparing(Order::priority));       // re-sort per insert — O(n log n) each
Order next = orders.remove(0);''', title="WrongStructures.java", size=27),
         narration=[
             "Four jobs, each done with the wrong structure. Deduplicating with List dot contains, which is quadratic. A java dot util Stack, which is synchronised and iterates from the bottom. "
             "A LinkedList as a queue, allocating a node per element. And re-sorting a whole list on every insert, just to find the most urgent order. "
             "Each one works. Each is slower than it needs to be by an order of magnitude, and two carry correctness traps besides.",
         ]),

    dict(title="Every Set is a Map in disguise",
         kicker="Mental model",
         body=table(["Set", "Backed by", "So it has"], [
                    ["`HashSet`", "`HashMap` with a dummy value", "O(1) average, unspecified order"],
                    ["`LinkedHashSet`", "`LinkedHashMap`", "Insertion order"],
                    ["`TreeSet`", "`TreeMap`", "O(log n), sorted, equality via `compareTo`"],
                    ["`EnumSet`", "A **bit vector**", "One `long` for ≤ 64 constants"],
                ], step_per_row=0, cls="sm")
              + frag(code('''
private transient HashMap<E, Object> map;
private static final Object PRESENT = new Object();
public boolean add(E e) { return map.put(e, PRESENT) == null; }''', title="java.util.HashSet (simplified)", size=25), 4),
         narration=[
             "Every Set is a Map in disguise. HashSet is a HashMap whose values are one shared dummy object. So it inherits O of one lookups and unspecified order.",
             "LinkedHashSet is a LinkedHashMap, so it keeps insertion order.",
             "TreeSet is a TreeMap: log n, sorted, and it uses compareTo, not equals, to decide duplicates.",
             "The exception is EnumSet, which is a bit vector. Up to sixty-four constants fit in a single long.",
             "Here's the actual HashSet add. It puts the element as a key, mapped to PRESENT. So everything from the HashMap chapter applies, including the mutable-key trap.",
         ]),

    dict(title="Queue has two methods for everything",
         kicker="Mental model",
         body=table(["", "Throws", "Returns a special value"], [
                    ["**Insert**", "`add(e)` — if full", "`offer(e)` → `false`"],
                    ["**Remove**", "`remove()` — if empty", "`poll()` → `null`"],
                    ["**Examine**", "`element()` — if empty", "`peek()` → `null`"],
                ], step_per_row=None)
              + frag('<p class="callout">Empty or full is often <b>normal</b>: a worker expects its queue to run dry. '
                     'Use <code>offer</code> / <code>poll</code> / <code>peek</code> for ordinary control flow.</p>', 1),
         narration=[
             "Queue has two methods for every operation. Add, remove and element throw when the queue is full or empty. "
             "Offer, poll and peek return false or null instead.",
             "The split exists because empty or full is often normal, not exceptional. A worker draining a queue expects it to run dry. "
             "So use offer, poll and peek for ordinary control flow.",
         ]),

    dict(title="Deduplicate and reconcile",
         kicker="Worked examples",
         body=code('''
Set<Sku> unique = new LinkedHashSet<>(incoming);              // O(n), keeps first-seen order
List<Sku> unique2 = incoming.stream().distinct().toList();    // same thing''', title="Dedupe.java", size=25)
              + code('''
Set<Sku> unstocked = new HashSet<>(inCatalogue);  unstocked.removeAll(inWarehouse);   // difference
Set<Sku> matched   = new HashSet<>(inCatalogue);  matched.retainAll(inWarehouse);     // intersection''',
                     title="Reconciliation.java", step=1, size=24)
              + frag('<p class="callout"><code>addAll</code>, <code>retainAll</code>, <code>removeAll</code> <b>mutate the receiver</b> — copy first. '
                     'Two lists of 200,000 SKUs with nested <code>contains</code>: 40 billion comparisons.</p>', 2),
         narration=[
             "To deduplicate while keeping the order things arrived in, use a LinkedHashSet. That's the real requirement far more often than a plain HashSet, which scrambles order. "
             "Stream dot distinct does the same thing internally.",
             "Set algebra makes reconciliation easy. SKUs we sell but the warehouse doesn't stock is a difference. SKUs in both is an intersection.",
             "Two catches. These methods mutate the set you call them on, so copy first. And doing this with two lists of two hundred thousand SKUs would mean forty billion comparisons.",
         ]),

    dict(title="TreeSet for neighbour queries",
         kicker="NavigableSet",
         body=code('''
NavigableSet<LocalTime> slotStarts = new TreeSet<>(List.of(
    LocalTime.of(9, 0), LocalTime.of(11, 0), LocalTime.of(14, 0), LocalTime.of(17, 0)));

slotStarts.ceiling(LocalTime.of(12, 30));    // 14:00 — next available slot
slotStarts.floor(LocalTime.of(12, 30));      // 11:00 — latest already started
slotStarts.subSet(LocalTime.of(10, 0), LocalTime.of(15, 0));   // [11:00, 14:00] — a VIEW''',
                   title="Slots.java", size=26)
              + frag('<p class="callout">Choose <code>TreeSet</code> for these queries, not for sorted iteration — '
                     'and remember it <b>silently drops</b> an element that compares equal to one already present.</p>', 1),
         narration=[
             "TreeSet's real superpower is neighbour queries. Ceiling gives the next slot at or after twelve thirty. Floor gives the latest one that's already started. "
             "subSet gives a range, as a live view. Each is log n. A HashSet would have to check every element.",
             "So choose TreeSet for these queries, not for sorted iteration, which you could get by sorting once. "
             "And remember: it uses compareTo, so an element that compares equal to one already there is silently dropped.",
         ]),

    dict(title="ArrayDeque: stack and queue",
         kicker="Worked example",
         body='<div class="grid2 start">'
              + code('''
Deque<CartAction> undo = new ArrayDeque<>();
undo.push(new AddLine(line));
undo.push(new ChangeQuantity(line, 3));
undo.pop();     // ChangeQuantity — LIFO

Queue<Order> pending = new ArrayDeque<>();
pending.offer(order1);
pending.offer(order2);
pending.poll(); // order1 — FIFO''', title="ArrayDequeUsage.java", size=24)
              + frag(table(["", "`ArrayDeque`", "`Stack`", "`LinkedList`"], [
                    ["Synchronised", "No", "**Every method**", "No"],
                    ["Bytes / element", "~4", "~4", "~24"],
                    ["Iterates as stack", "Top first", "**Bottom first**", "Top first"],
                    ["Nulls", "Rejected", "Allowed", "Allowed"],
                ], cls="sm"), 1)
              + "</div>",
         narration=[
             "ArrayDeque is the right answer for both a stack and a queue. Push and pop for last-in, first-out undo history. Offer and poll for first-in, first-out pending dispatches.",
             "Compared to the alternatives: Stack synchronises every method, and iterates from the bottom, the opposite of pop order. "
             "LinkedList costs about twenty-four bytes per element. ArrayDeque costs about four. The one rule: ArrayDeque rejects nulls.",
         ]),

    dict(title="PriorityQueue &amp; top-K",
         kicker="Worked examples",
         body=code('''
Queue<Order> byUrgency = new PriorityQueue<>(
    comparing(Order::priority).reversed().thenComparing(Order::placedAt));   // a MIN-heap: reverse for max
while (!byUrgency.isEmpty()) dispatch(byUrgency.poll());''', title="DispatchPriority.java", size=24)
              + code('''
PriorityQueue<Order> topTen = new PriorityQueue<>(comparing(Order::total));   // min-heap of size k
for (Order o : allOrders) {
    topTen.offer(o);
    if (topTen.size() > 10) topTen.poll();       // evict the smallest of the top eleven
}''', title="TopK.java — O(n log k) time, O(k) memory", step=1, size=24),
         narration=[
             "PriorityQueue is a min-heap by its comparator. Poll always returns the smallest. So for the most urgent first, reverse the comparator. "
             "Use it when items arrive over time and you repeatedly need the next most urgent one, at log n per operation.",
             "And here's a classic: the top ten orders by value, from a million. Keep a min-heap of size ten. After each insert, if it holds eleven, evict the smallest. "
             "That's n log k time and k memory, instead of sorting all million. Just remember to sort the ten at the end, because the heap isn't sorted.",
         ]),

    dict(title="Inside the heap and the deque",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Binary heap", "Children of i at 2i+1, 2i+2. Only rule: parent ≤ children. So **iteration is heap order**, not sorted.", "indigo", 0)
              + card("Circular buffer", "`ArrayDeque` moves two indices around an array — O(1) at both ends, no shifting. `null` means an empty slot.", "cyan", 1)
              + card("O(n) traps", "`PriorityQueue.remove(Object)` and `contains` scan linearly. Many cancellations? Mark-and-skip, or use a `TreeSet`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Inside PriorityQueue is a binary heap stored in an array. The only invariant is that each parent is less than or equal to its children. "
             "So the root is the minimum, but siblings are in no particular order. That's why iterating it gives heap order, which looks nearly sorted on small inputs and clearly isn't on large ones.",
             "ArrayDeque is a circular buffer. Two indices move around a fixed array and wrap at the end, so both ends are O of one with nothing shifted. "
             "It forbids nulls because a null slot means empty.",
             "And watch for PriorityQueue's linear operations. Remove of an object and contains both scan the whole array. "
             "If dispatches often get cancelled, mark them and skip on poll, or use a TreeSet.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`Set` for membership and dedupe",
                         "`LinkedHashSet` when order matters",
                         "Copy before `retainAll` / `removeAll`",
                         "`TreeSet` for `ceiling`, `floor`, `subSet`",
                         "`ArrayDeque` for every stack and queue",
                         "Size-k min-heap for top-k; `EnumSet` for enums"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`java.util.Stack`",
                         "`LinkedList` as a queue",
                         "Iterate a `PriorityQueue` expecting sorted",
                         "`PriorityQueue.remove(Object)` in a hot loop",
                         "`null` in an `ArrayDeque`",
                         "Share a deque or heap across threads — use a `BlockingQueue`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use a Set for membership and deduplication, and LinkedHashSet when order matters. Copy before retainAll or removeAll. "
             "Use TreeSet for neighbour queries, ArrayDeque for every stack and queue, a size-k min-heap for top-k, and EnumSet for enums.",
             "Never use java dot util Stack, or LinkedList as a queue. Never iterate a PriorityQueue expecting sorted order, or call its remove in a hot loop. "
             "Never put null in an ArrayDeque. And never share a deque or heap across threads. That's what blocking queues are for, in chapter thirty.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 20 · Set, Queue &amp; Deque",
         body=bullets(["Every `Set` is a `Map` — same costs, same traps",
                       "`offer` / `poll` / `peek` when empty or full is normal",
                       "`ArrayDeque` for stacks and queues; never `Stack`",
                       "`PriorityQueue` is a min-heap: `poll` is ordered, iteration isn't",
                       "Next: **Ch 21 · Sequenced Collections**"], cls="bullets recap"),
         narration=[
             "To recap. Every Set is a Map underneath, with the same costs and the same traps. Use offer, poll and peek when empty or full is normal. "
             "ArrayDeque is the answer for stacks and queues, never Stack. And PriorityQueue is a min-heap: poll is ordered, iteration isn't.",
             "Next is chapter twenty-one, sequenced collections. Thanks for watching.",
         ]),
]
