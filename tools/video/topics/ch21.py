"""Chapter 21 — Sequenced Collections. Source: docs/03-collections/21-sequenced-collections.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 21 · Sequenced Collections"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="Sequenced Collections",
         kicker="Collections · Chapter 21 · Java 21",
         body='<p class="sub">A common vocabulary for the ends of every ordered collection — why <code>reversed()</code> is a view, '
              'and why <code>HashMap</code> isn\'t included.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-one: sequenced collections.",
             "For twenty-five years, Java had ordered collections but no common way to talk about their ends. Java 21 fixed that by retrofitting three interfaces. "
             "The feature is small, the retrofit is interesting, and there's one correction that circulating notes get wrong.",
         ]),

    dict(title="Four collections, four spellings",
         kicker="The problem",
         body=code('''
CartLine lastLine = lines.get(lines.size() - 1);       // List — off-by-one risk
Order lastOrder   = deque.getLast();                   // Deque
Sku lastSku = null;
for (Sku sku : skus) { lastSku = sku; }                // LinkedHashSet — O(n) loop!
Sku highest = sortedSkus.last();                       // SortedSet''', title="EndsBefore.java", size=26)
              + code('''
List<Order> reversed = new ArrayList<>(orders);
Collections.reverse(reversed);                         // copy the whole list to go backwards
// LinkedHashMap in reverse: no supported way at all''', title="ReverseBefore.java", step=1, size=26),
         narration=[
             "Before Java 21, the last element of four ordered collections needed four spellings. A List used get of size minus one. A Deque had getLast. "
             "A LinkedHashSet had no accessor at all, so you looped through every element. And a SortedSet had last.",
             "Going backwards was worse. You copied the whole list and reversed the copy. And for a LinkedHashMap, there was no supported way at all. "
             "Each type had some idea of first and last, but no shared interface, so no generic code could use it.",
         ]),

    dict(title="Three retrofitted interfaces",
         kicker="Mental model",
         body=table(["Interface", "Adds", "Implemented by"], [
                    ["`SequencedCollection`", "`getFirst` `getLast` `addFirst` `addLast` `removeFirst` `removeLast` `reversed`", "`List`, `Deque`"],
                    ["`SequencedSet`", "`reversed()` returns a `Set`", "`LinkedHashSet`, `TreeSet`"],
                    ["`SequencedMap`", "`firstEntry` `lastEntry` `putFirst` `putLast` `pollFirstEntry` `reversed`", "`LinkedHashMap`, `TreeMap`"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout"><b><code>HashMap</code> and <code>HashSet</code> are NOT sequenced.</b> They have no encounter order — '
                     'so there is no "first". Notes claiming otherwise are wrong.</p>', 3),
         narration=[
             "Java 21 added three interfaces. SequencedCollection gives every ordered collection getFirst, getLast, addFirst, addLast, removeFirst, removeLast, and reversed. List and Deque extend it.",
             "SequencedSet adds nothing new, except that reversed returns a Set. LinkedHashSet and TreeSet implement it.",
             "And SequencedMap gives firstEntry, lastEntry, putFirst, putLast, poll methods, and reversed. LinkedHashMap and TreeMap implement it.",
             "The defining property is an encounter order. And here's the correction. HashMap and HashSet are not sequenced. Their iteration order is unspecified, so there's no meaningful first. "
             "Notes and blog posts claiming Java 21 gave HashMap a firstEntry method are wrong. PriorityQueue is excluded too, because its iteration is heap order.",
         ]),

    dict(title="One vocabulary — and generic code",
         kicker="Worked examples",
         body=code('''
lines.getLast();        deque.getLast();        skus.getLast();     sortedSkus.getLast();
//  List                Deque                   LinkedHashSet: O(1)  TreeSet''', title="EndsAfter.java", size=25)
              + code('''
public static <T> Optional<T> mostRecent(SequencedCollection<T> collection) {
    return collection.isEmpty() ? Optional.empty() : Optional.of(collection.getLast());
}
mostRecent(recentOrders);     // ArrayList
mostRecent(dispatchQueue);    // ArrayDeque
mostRecent(uniqueSkusSeen);   // LinkedHashSet''', title="Generic.java", step=1, size=25),
         narration=[
             "Now it's one vocabulary. getLast works on a list, a deque, a LinkedHashSet and a TreeSet. The LinkedHashSet case is the big win: it's O of one now, because it keeps a doubly-linked list internally.",
             "And the real payoff is generic code. A method can accept any SequencedCollection and take its last element, whether you pass an ArrayList, an ArrayDeque or a LinkedHashSet. "
             "Before Java 21, that method couldn't be written, because no type meant ordered collection.",
         ]),

    dict(title="reversed() is a live view",
         kicker="The thing to remember",
         body=code('''
List<Order> orders = new ArrayList<>(List.of(a, b, c));
List<Order> backwards = orders.reversed();      // [c, b, a] — O(1), no copy

backwards.set(0, d);    // writes through:  orders is now [a, b, d]
orders.add(e);          // the view sees it: backwards is now [e, d, b, a]

List<Order> independent = new ArrayList<>(orders.reversed());   // need a copy? wrap it''',
                   title="ReversedView.java", size=26)
              + code('''
for (Order order : orders.reversed()) { ... }                     // no copy, no allocation
for (var entry : slotsByStart.reversed().entrySet()) { ... }      // LinkedHashMap — finally''',
                     title="ReverseIteration.java", step=1, size=26),
         narration=[
             "The single most important thing about this feature: reversed returns a live, writable view, not a copy. It's O of one to create, however big the collection. "
             "But writing through the view changes the original, and changes to the original show up in the view. Exactly like subList. If you need an independent copy, wrap it in a new ArrayList.",
             "That makes reverse iteration free. No copy, no allocation. And it finally works on a LinkedHashMap, which had no supported way to iterate backwards before.",
         ]),

    dict(title="A most-recently-used map",
         kicker="putFirst on a LinkedHashMap",
         body=code('''
public final class RecentSkus {
    private final SequencedMap<Sku, Instant> recent = new LinkedHashMap<>();

    public void record(Sku sku) {
        recent.putFirst(sku, Instant.now());    // insert — or MOVE to the front
        while (recent.size() > capacity) {
            recent.pollLastEntry();              // evict the oldest
        }
    }
    public List<Sku> mostRecent(int n) {
        return recent.sequencedKeySet().stream().limit(n).toList();
    }
}''', title="RecentlyUsed.java", size=26),
         narration=[
             "Here's a practical use. putFirst on a LinkedHashMap inserts a new key at the front, or moves an existing key to the front. "
             "Combine it with pollLastEntry to evict the oldest, and a most-recently-used structure is a few readable lines. "
             "Before, it meant LinkedHashMap's access-order constructor plus overriding removeEldestEntry.",
         ]),

    dict(title="What throws, and why",
         kicker="Unsupported operations",
         body=code('''
SortedSet<Sku> sorted = new TreeSet<>(Set.of(milk, rice));
sorted.getFirst();        // ✓ lowest
sorted.reversed();        // ✓ descending view
sorted.addFirst(atta);    // ✗ UnsupportedOperationException

List.of(milk, rice).addFirst(atta);   // ✗ immutable''', title="Unsupported.java", size=26)
              + frag('<p class="callout">A sorted collection decides position by its comparator. "Insert at the front" is a contradiction — '
                     'an honest exception beats a method that means something different per implementation.</p>', 1)
              + frag('<p class="callout">Also: <code>getFirst()</code> <b>throws</b> when empty; the map\'s <code>firstEntry()</code> <b>returns null</b>.</p>', 2),
         narration=[
             "Some operations throw. A TreeSet happily gives you getFirst and a reversed view, but addFirst throws UnsupportedOperationException. And of course immutable lists reject every mutator.",
             "That's correct. A sorted collection decides position with its comparator, so insert at the front is a contradiction. "
             "Putting it in sorted position instead would make addFirst mean different things on different collections, which defeats a shared interface.",
             "And note an asymmetry. getFirst on an empty collection throws, while firstEntry on an empty map returns null, following the older NavigableMap convention.",
         ]),

    dict(title="How the retrofit works",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Default methods", "`getFirst()` defaults to `get(0)`, `getLast()` to `get(size() - 1)` — every third-party `List` keeps compiling.", "indigo", 0)
              + card("Deque was ready", "It has had `addFirst`, `getLast` since Java 6. Mostly a matter of declaring `extends SequencedCollection`.", "cyan", 1)
              + card("Views everywhere", "`subList`, `keySet`, `unmodifiableList`, `reversed` — almost every derived collection in `java.util` is a **view**.", "fuchsia", 2)
              + "</div>",
         narration=[
             "How do you add methods to List in 2023 without breaking every implementation out there? Default methods. getFirst defaults to get zero, and getLast to get size minus one. "
             "Third-party lists keep compiling. JDK classes override where they can do better. It's the same mechanism that made Java 8's stream method possible.",
             "Deque was already most of the way there. It's had addFirst and getLast since Java 6, with exactly the right signatures.",
             "And reversed joins a family. subList, keySet, values, unmodifiableList, Arrays dot asList. Almost everything in java dot util that returns a derived collection returns a view. "
             "The copies are the ones with copy, or a constructor, in their name.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`getFirst()` / `getLast()` over index arithmetic",
                         "`reversed()` for reverse iteration",
                         "Accept `SequencedCollection` in generic code",
                         "`putFirst` + `pollLastEntry` for MRU maps",
                         "Wrap `reversed()` when you need a copy"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Expect these methods on `HashMap` / `HashSet`",
                         "Treat `reversed()` as a copy",
                         "Store a `reversed()` view in a field",
                         "`addFirst` on a `TreeSet`",
                         "`getFirst()` on a possibly-empty collection unchecked"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use getFirst and getLast instead of index arithmetic. Use reversed for reverse iteration. Accept SequencedCollection in generic code. "
             "Use putFirst and pollLastEntry for most-recently-used maps. And wrap reversed in a constructor when you need a copy.",
             "Never expect these methods on HashMap or HashSet. Never treat reversed as a copy, or store the view in a field unless you want the aliasing. "
             "Don't call addFirst on a TreeSet. And check for empty before calling getFirst.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 21 · Sequenced Collections",
         body=bullets(["One vocabulary for **every ordered collection**",
                       "`HashMap` and `HashSet` are **not** sequenced — no encounter order",
                       "`reversed()` is an O(1) **live view**",
                       "Sorted collections throw on `addFirst` — correctly",
                       "Next: **Ch 22 · Immutability &amp; Defensive Copying**"], cls="bullets recap"),
         narration=[
             "To recap. Java 21 gave every ordered collection one vocabulary for its ends. HashMap and HashSet aren't included, because they have no encounter order. "
             "reversed is an O of one live view, not a copy. And sorted collections correctly throw on addFirst.",
             "Next is chapter twenty-two: immutability and defensive copying. Thanks for watching.",
         ]),
]
