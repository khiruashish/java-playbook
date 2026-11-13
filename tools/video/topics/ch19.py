"""Chapter 19 — HashMap Internals. Source: docs/03-collections/19-hashmap-internals.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 19 · HashMap Internals"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="HashMap Internals",
         kicker="Collections · Chapter 19",
         body='<p class="sub">What <code>put</code> and <code>get</code> really do, when O(1) breaks, '
              'and how to size, key and tune a map for production.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter nineteen: HashMap internals.",
             "HashMap is the most used data structure in enterprise Java, and the most misunderstood. Most developers say it's O of one, and stop there. "
             "That answer misses the production incidents: maps that silently lose entries, lookups that degrade to scans, and rehashing storms under load.",
         ]),

    dict(title="An array of bins",
         kicker="Mental model",
         body=flow(["`key.hashCode()`", "**spread**\n`h ^ (h >>> 16)`", "**index**\n`(n - 1) & hash`",
                    "**bin**: empty · list · red-black tree"], step_start=0)
              + frag(table(["Constant", "Value", "Meaning"], [
                    ["`DEFAULT_INITIAL_CAPACITY`", "16", "Allocated lazily on first `put`"],
                    ["`DEFAULT_LOAD_FACTOR`", "0.75", "Resize when size > capacity × 0.75"],
                    ["`TREEIFY_THRESHOLD`", "8", "Bin becomes a tree at this length"],
                    ["`UNTREEIFY_THRESHOLD`", "6", "…and a list again at this — hysteresis"],
                    ["`MIN_TREEIFY_CAPACITY`", "64", "Below this, **resize instead** of treeify"],
                ], cls="sm"), 4),
         narration=[
             "A HashMap is an array of bins. It starts with the key's hashCode.",
             "That hash is spread: the high sixteen bits are mixed into the low sixteen.",
             "Then the index is computed with a bitmask, table length minus one, AND the hash.",
             "And the bin at that index is either empty, a short linked list, or, under heavy collision, a red-black tree.",
             "Five constants govern its behaviour. Default capacity sixteen, allocated lazily. Load factor point seven five. "
             "Bins become trees at eight entries and turn back into lists at six, so a bin at the boundary doesn't flip back and forth. "
             "And below a table length of sixty-four, the map grows instead of making trees.",
         ]),

    dict(title="Why spread the hash?",
         kicker="Internals",
         body=code('''
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}

int index = (table.length - 1) & hash;     // a table of 16 looks at only the bottom 4 bits''',
                   title="java.util.HashMap", size=27)
              + bullets(["**null hashes to 0** — exactly one null key, always in bin 0",
                         "The mask sees only low bits, so high-bit entropy is **XORed down**",
                         "Works only because capacity is a **power of two** — `new HashMap<>(17)` gets 32"], start_step=1, cls="bullets sm"),
         narration=[
             "Here's the hash function from the JDK source.",
             "A null key hashes to zero. That's why a HashMap supports exactly one null key, always in bin zero.",
             "The index is a bitmask, and for a sixteen-slot table it only looks at the bottom four bits. A hashCode that varies only in its high bits would put every key in the same bin. "
             "So the high bits are XORed down into the low ones. One shift, one XOR.",
             "And that bitmask is a cheap modulo that only works because the table length is always a power of two. Ask for seventeen and you get thirty-two.",
         ]),

    dict(title="Treeification — and its trap",
         kicker="Internals",
         body=code('''
if (tab == null || tab.length < MIN_TREEIFY_CAPACITY)   // 64
    resize();          // a long bin probably means the table is too small
else
    treeify(bin);      // red-black tree: O(log k) inside the bin''', title="HashMap.treeifyBin (paraphrased)", size=27)
              + frag('<p class="callout"><b>O(1) average, O(log n) worst case</b> since Java 8. "O(n) worst case" describes Java 7 — '
                     'and the hash-collision DoS this fixed.</p>', 1),
         narration=[
             "When a bin reaches eight nodes, the map considers making it a tree. But below a table length of sixty-four, it resizes instead, "
             "because a long bin in a small table more likely means the table is too small than that the hash function is bad. Inside a tree bin, lookup is log k.",
             "That's the honest complexity statement: O of one on average, and O of log n in the worst case, since Java 8. "
             "The old O of n answer describes Java 7, when attackers could send thousands of colliding keys and turn every lookup into a linear scan.",
         ]),

    dict(title="Resize: the one O(n) operation",
         kicker="Internals",
         body=code('''
if ((e.hash & oldCap) == 0) {
    // stays at index j            → "lo" list
} else {
    // moves to index j + oldCap   → "hi" list
}''', title="HashMap.resize — splitting a bin", size=28)
              + bullets(["Capacity doubles; each entry stays put **or** moves by exactly `oldCap`",
                         "One bit decides — **no rehashing**, cached `hash` reused, order preserved",
                         "Java 7 reversed lists → concurrent resize could loop forever. Still **not thread-safe**."], start_step=1, cls="bullets sm"),
         narration=[
             "When size passes the threshold, capacity doubles and every entry moves. Java 8 does this with a neat trick.",
             "Because capacity is a power of two and exactly doubles, each entry either stays at the same index, or moves by exactly the old capacity.",
             "A single bit of the cached hash decides which. So each bin splits into a low list and a high list in one pass, with no rehashing, and the order is preserved.",
             "That order preservation matters. Java 7 reversed the lists, and two threads resizing at once could build a cycle that spun at a hundred percent CPU. "
             "Java 8 removed that failure, but HashMap is still not thread-safe. Concurrent writes still lose updates.",
         ]),

    dict(title="The mutable-key bug",
         kicker="Worked example",
         body=code('''
var key = new MutableSku("MILK-1L");
stock.put(key, 40);

key.setCode("MILK-2L");                 // hash changes; the entry does NOT move

stock.get(key);           // null
stock.containsKey(key);   // false
stock.size();             // 1  ← stranded: unreachable, unremovable''', title="MutableKeyDemo.java", size=27)
              + frag('<p class="callout">Keys must be immutable in every field used by <code>hashCode</code> and <code>equals</code>. '
                     'Use records: <code>record Sku(String code) {}</code>.</p>', 1),
         narration=[
             "This is the HashMap bug that reaches production most often. Put an entry with a mutable key, then change the key. "
             "The hash changes, but the entry stays in the bin computed from the old hash. "
             "So get returns null, containsKey returns false, but size still says one. The entry is unreachable, unremovable, and leaked forever.",
             "So keys must be immutable in every field used by hashCode and equals. Records are the cleanest way to guarantee that.",
         ]),

    dict(title="Size it, and use merge",
         kicker="Worked examples",
         body=code('''
this.bySku = HashMap.newHashMap(items.size());   // Java 19: fits n without a resize
// new HashMap<>(200_000) takes a CAPACITY — it still resizes at 75%''', title="SkuCatalogue.java", size=25)
              + code('''
totals.merge(line.sku(), line.quantity(), Integer::sum);             // aggregate

board.computeIfAbsent(order.slot(), slot -> new ArrayList<>())       // group
     .add(order);''', title="CartAggregator.java · DispatchBoard.java", step=1, size=25)
              + frag('<p class="callout"><code>putIfAbsent(slot, new ArrayList&lt;&gt;())</code> allocates a list on <b>every</b> call. '
                     'The lambda runs only on first encounter.</p>', 2),
         narration=[
             "Size the map when you know the count. Building a two-hundred-thousand-entry catalogue from a default map triggers fifteen resizes. "
             "Java 19's HashMap dot newHashMap sizes it so all entries fit with none. Remember, the plain constructor takes a capacity, not an expected size.",
             "And use merge and computeIfAbsent instead of get, check, put. Merge collapses duplicate SKUs by summing quantities. computeIfAbsent groups orders by delivery slot.",
             "Compare putIfAbsent with a new ArrayList, which allocates a list on every single call and throws most of them away. The computeIfAbsent lambda only runs the first time.",
         ]),

    dict(title="Fail-fast iteration",
         kicker="Removing while iterating",
         body='<div class="grid2 start">'
              + code('''
for (Sku sku : stock.keySet()) {
    if (stock.get(sku) == 0) {
        stock.remove(sku);   // CME
    }
}''', title="✗ ConcurrentModificationException", size=25)
              + frag(code('''
stock.entrySet()
     .removeIf(e -> e.getValue() == 0);''', title="✓ removeIf", size=25), 1)
              + "</div>"
              + frag('<p class="callout">Fail-fast is a <b>best-effort bug detector</b>, not synchronisation. Never depend on it firing.</p>', 2),
         narration=[
             "Every structural change bumps a modCount, and iterators check it. So removing entries inside a for-each over the key set throws a ConcurrentModificationException.",
             "Use removeIf on the entry set, or an explicit iterator's remove.",
             "And remember, fail-fast is a best-effort bug detector, not a synchronisation mechanism. Never write logic that depends on it.",
         ]),

    dict(title="What it costs",
         kicker="Memory footprint",
         body=table(["Per entry (64-bit, compressed oops)", "Bytes"], [
                    ["`Node`: header + hash + key, value, next", "32"],
                    ["Table slot at load factor 0.75", "~5.3"],
                    ["`Node` with Java 25 compact headers", "24"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">A 1M-entry map costs ~<b>37 MB</b> of overhead before a single key or value object.</p>', 3),
         narration=[
             "Each entry is a Node object: a header, the cached hash, and three references. That's thirty-two bytes on a typical 64-bit JVM.",
             "Add the table array, about five bytes per entry at the default load factor.",
             "Java 25's compact object headers shrink the Node to twenty-four bytes.",
             "So a million-entry map costs around thirty-seven megabytes of overhead before a single key or value object. On map-heavy heaps, that adds up.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`HashMap.newHashMap(n)` when the count is known",
                         "Records as keys",
                         "`merge` and `computeIfAbsent` over get-check-put",
                         "Return `Map.copyOf(...)` from accessors",
                         "Declare `Map<K,V>`, not `HashMap<K,V>`",
                         "`EnumMap` for enum keys"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Share a `HashMap` across threads unsafely",
                         "Mutable keys",
                         "Tune the load factor without measuring",
                         "Rely on iteration order",
                         "`containsValue` in a hot path — it's O(n)",
                         "Mutate the map inside `compute*`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Size maps with newHashMap when you know the count. Use records as keys. Prefer merge and computeIfAbsent. "
             "Return Map dot copyOf from accessors. Declare fields as Map. And use EnumMap for enum keys.",
             "Never share a HashMap across threads without safe publication. Never use mutable keys. Don't tune the load factor without measuring, because the default is well chosen. "
             "Never rely on iteration order. Avoid containsValue in hot paths, since it scans everything. And never modify the map inside a compute function.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "Treeified bins; order-preserving resize; `merge`, `compute*`, `getOrDefault`"],
                    ["**9–10**", "`Map.of`, `Map.copyOf`; recursive `computeIfAbsent` throws"],
                    ["**19**", "`HashMap.newHashMap(n)`"],
                    ["**21**", "`SequencedMap` — for `LinkedHashMap` and `TreeMap`, **not** `HashMap`"],
                    ["**25**", "Compact object headers: `Node` 32 → 24 bytes"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 brought treeified bins, the order-preserving resize, and merge, compute and getOrDefault.",
             "Java 9 and 10 added Map dot of and copyOf, and made recursive updates inside computeIfAbsent throw instead of silently corrupting the map.",
             "Java 19 added newHashMap.",
             "Java 21 added SequencedMap. And here's a correction to common notes: it applies to LinkedHashMap and TreeMap, not HashMap, because HashMap has no defined order.",
             "And Java 25's compact headers shrink each Node by a quarter.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 19 · HashMap Internals",
         body=bullets(["Spread → index → bin: **list, or tree at 8** (table ≥ 64)",
                       "O(1) average, **O(log n) worst** since Java 8",
                       "Resize splits bins by **one bit** — size maps up front",
                       "**Immutable keys** — mutated keys strand entries forever",
                       "Next: **Ch 20 · Set, Queue &amp; Deque**"], cls="bullets recap"),
         narration=[
             "To recap. The hash is spread, masked to an index, and lands in a bin that's a list, or a tree once it reaches eight in a large enough table. "
             "Lookups are O of one on average and log n at worst since Java 8. Resizing splits each bin by a single bit, so size maps up front. "
             "And keys must be immutable, or entries get stranded forever.",
             "Next is chapter twenty: sets, queues and deques. Thanks for watching.",
         ]),
]
