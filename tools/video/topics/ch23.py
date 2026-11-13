"""Chapter 23 — equals, hashCode & Comparators. Source: docs/03-collections/23-equality-and-ordering.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 23 · equals, hashCode & Comparators"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="equals, hashCode &amp; Comparators",
         kicker="Collections · Chapter 23",
         body='<p class="sub">Four methods every hash-based and sorted collection trusts completely — and what happens when they lie.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-three: equals, hashCode and comparators.",
             "Every hash-based and sorted collection is built on four methods you write yourself: equals, hashCode, compareTo and compare. The collections trust them completely. "
             "When they break their contracts, nothing throws. Entries are silently lost, duplicated or dropped, and the bug shows up far from its cause.",
         ]),

    dict(title="Four silent failures",
         kicker="The problem",
         body=code('''
skus.add(new Sku("MILK-1L")); skus.add(new Sku("MILK-1L"));
skus.size();                                       // 1. equals without hashCode → 2

new HashSet<>(List.of(new BigDecimal("1.0"), new BigDecimal("1.00"))).size();   // 2. → 2
new TreeSet<>(List.of(new BigDecimal("1.0"), new BigDecimal("1.00"))).size();   //    → 1

(a, b) -> (int) (a.totalPaise() - b.totalPaise())  // 3. overflows for large values

key.setCode("MILK-2L"); stock.get(key);            // 4. mutated key → null, size still 1''',
                   title="Failures.java", size=25),
         narration=[
             "Four failures, all from collections working exactly as designed. Override equals but not hashCode, and a HashSet keeps two identical SKUs. "
             "Put the same two BigDecimals in a HashSet and a TreeSet, and you get two different sizes. A comparator written with subtraction overflows on large values. "
             "And a mutated map key strands its entry. None of these throws. Each has a one-line cause.",
         ]),

    dict(title="Two methods vs one",
         kicker="Mental model",
         body='<div class="grid2">'
              + card("HashMap / HashSet", "`hashCode()` finds the bucket,\nthen `equals()` finds the element.", "indigo", 0)
              + card("TreeMap / TreeSet", "`compareTo()` or `compare()` **only**.\n`equals()` is never called.", "fuchsia", 1)
              + "</div>"
              + frag('<p class="callout"><code>new BigDecimal("1.0").equals(new BigDecimal("1.00"))</code> is <b>false</b> (scale differs), '
                     'but <code>compareTo</code> is <b>0</b>. Same objects, two definitions of "the same".</p>', 2),
         narration=[
             "Here's the fact that explains the BigDecimal result. Hash collections use two methods: hashCode to find the bucket, then equals to find the element.",
             "Sorted collections use only one: compareTo, or your comparator. They never call equals at all.",
             "And BigDecimal one point zero equals one point zero zero is false, because their scale differs. But compareTo says they're equal. "
             "So the HashSet sees two elements, and the TreeSet sees one.",
         ]),

    dict(title="The contracts",
         kicker="Core reference",
         body=table(["Relationship", "Strength", "If violated"], [
                    ["`a.equals(b)` ⇒ equal `hashCode`s", "**Mandatory**", "Hash collections lose or duplicate entries"],
                    ["`compareTo == 0` ⇔ `equals`", "Strongly recommended", "Hash and sorted collections disagree"],
                    ["Equal hash ⇒ equal objects", "**Not** required", "Just a collision — slower, not wrong"],
                ], step_per_row=0, cls="sm")
              + frag(bullets(["`equals`: reflexive, symmetric, transitive, consistent, `x.equals(null)` is false",
                              "Use the **same fields** in `equals` and `hashCode`",
                              "Only the **sign** of `compareTo` matters"], cls="bullets sm"), 3),
         narration=[
             "The one rule that breaks things: equal objects must have equal hash codes. That's mandatory.",
             "compareTo returning zero should agree with equals. That's strongly recommended. When it doesn't, hash and sorted collections disagree, like BigDecimal.",
             "But the converse isn't required. Unequal objects can share a hash code. That's just a collision, which every hash table handles.",
             "equals must be reflexive, symmetric, transitive and consistent, and equals of null is false. Use exactly the same fields in equals and hashCode. And for compareTo, only the sign of the result matters.",
         ]),

    dict(title="Write it correctly — or don't write it",
         kicker="Worked example",
         body=code('''
@Override public boolean equals(Object o) {
    return this == o
        || o instanceof Sku other              // null never matches; no separate cast
           && code.equals(other.code)
           && vendorId.equals(other.vendorId);
}
@Override public int hashCode() {
    return 31 * code.hashCode() + vendorId.hashCode();     // the same fields
}''', title="Sku.java", size=26)
              + code('public record Sku(String code, String vendorId) { }    // both generated, cannot drift',
                     title="SkuRecord.java — the default for value types", step=1, size=26),
         narration=[
             "If you hand-write equals, use the instanceof pattern. Null never matches a type pattern, so you get the null check and the cast for free. And use the same fields in hashCode.",
             "But for value types, the better answer is a record. It generates both methods from the same components, so they can never drift apart when someone adds a field. "
             "Hand-written equals should be the exception, with a reason.",
         ]),

    dict(title="The inheritance trap",
         kicker="Symmetry breaks",
         body=code('''
Money plain = new Money(10_000);
Money taxed = new TaxedMoney(10_000, "GST");     // subclass adds a component to equals

plain.equals(taxed);    // true  — taxed IS a Money
taxed.equals(plain);    // false — plain is NOT a TaxedMoney''', title="SymmetryViolation.java", size=27)
              + frag(table(["Option", "Trade"], [
                    ["**Composition** — `TaxedMoney` has a `Money`", "Correct; the usual answer"],
                    ["`getClass()` check in `equals`", "Symmetric, but breaks substitutability"],
                    ["`final` class or record", "Removes the problem"],
                ], cls="sm"), 1),
         narration=[
             "Here's the inheritance trap. Money compares amounts. TaxedMoney extends it and also compares a tax code. "
             "Now plain equals taxed is true, but taxed equals plain is false. Symmetry is broken, and whether a collection finds the object depends on which equals gets called.",
             "There's no way to extend an instantiable class, add a value component, and keep the contract. Use composition instead. A getClass check is symmetric, but breaks substitutability. "
             "Or make the class final, which records are by default.",
         ]),

    dict(title="Never compare by subtraction",
         kicker="Worked example",
         body=code('''
Comparator<Order> byTotal = (a, b) -> (int) (a.totalPaise() - b.totalPaise());   // ✗
// 3,000,000,000 - (-1) → cast to int → NEGATIVE → biggest sorts first

Comparator<Order> byTotal = Comparator.comparingLong(Order::totalPaise);        // ✓
Comparator<Order> byTotal = (a, b) -> Long.compare(a.totalPaise(), b.totalPaise());   // ✓''',
                   title="OverflowComparator.java", size=23)
              + code('''
public record Money(BigDecimal amount, Currency currency) {
    public Money { amount = amount.setScale(2, RoundingMode.HALF_UP); }   // one scale
}''', title="NormaliseScale.java — equals now agrees with compareTo", step=1, size=23),
         narration=[
             "Never compute a comparison by subtraction. Subtract a negative from three billion paise, cast to int, and it overflows. The sign flips, and the biggest order sorts first. "
             "It passes every test with small numbers and fails on real data. Use comparingLong, or Long dot compare.",
             "And fix BigDecimal at the boundary. Normalise the scale in the record's compact constructor, so equals and compareTo always agree, and a map keyed by price doesn't treat ten point zero and ten point zero zero as different keys.",
         ]),

    dict(title="Composed comparators &amp; TreeSet loss",
         kicker="Worked examples",
         body=code('''
Comparator<Order> dispatchOrder = Comparator
    .comparing(Order::priority).reversed()       // high priority first
    .thenComparing(Order::placedAt)               // then oldest
    .thenComparing(Order::id);                    // unique tie-breaker → a TOTAL order

Comparator.comparing(Order::priority).thenComparing(Order::placedAt).reversed();   // ✗ reverses BOTH''',
                   title="Composed.java", size=25)
              + code('''
Set<Order> byPriority = new TreeSet<>(Comparator.comparing(Order::priority));
byPriority.add(orderA);   // HIGH
byPriority.add(orderB);   // HIGH — compares equal → silently NOT added; size() == 1''',
                     title="TreeSetLoss.java", step=1, size=25),
         narration=[
             "Compose comparators with comparing and thenComparing. Careful with reversed. It reverses everything built so far, not just the last key. Put it at the end of the chain and you've reversed every key. "
             "To reverse just one, pass reverseOrder to that thenComparing.",
             "And always end with a unique tie-breaker, like the order ID, so the order is total. Here's why. A TreeSet uses the comparator as its definition of equality. "
             "Two orders with the same priority are the same element to it, so the second add is silently dropped.",
         ]),

    dict(title="Internals",
         kicker="How the collections use them",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Hash first", "`HashMap` compares cached hashes before calling `equals`. No `hashCode` override → equal keys land in different buckets.", "indigo", 0)
              + card("Objects.hash allocates", "Varargs → a new `Object[]` and boxing every call. Hand-roll it for hot keys, or use a record.", "cyan", 1)
              + card("Doubles &amp; arrays", "`NaN.equals(NaN)` is true, `0.0` ≠ `-0.0`. Arrays compare by **identity**. Keep both out of keys.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Three internals. HashMap compares the cached hashes first, and only calls equals on a hash match. So without a hashCode override, two equal keys get different identity hashes, land in different buckets, and equals is never even called.",
             "Objects dot hash is convenient but takes varargs, so it allocates an array and boxes primitives on every call. For hot keys, hand-roll it, or use a record, whose generated hashCode avoids the array.",
             "And keep doubles and arrays out of keys. Double's equals treats NaN as equal to itself and zero as different from negative zero, the opposite of the double-equals operator. "
             "Arrays compare by identity, which also silently breaks records with array components.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Records for value types",
                         "`equals` + `hashCode` together, same fields",
                         "`instanceof` patterns in hand-written `equals`",
                         "Composition over inheritance for values",
                         "Normalise `BigDecimal` scale",
                         "`Comparator.comparing`; end with a unique tie-breaker"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`equals` without `hashCode`",
                         "Compare by subtraction",
                         "Extend a value class and add to `equals`",
                         "Mutable or mutated map keys",
                         "`double` or array keys",
                         "Assume `TreeSet` and `HashSet` agree"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use records for value types. If you hand-write equals, write hashCode too, with the same fields, using the instanceof pattern. "
             "Prefer composition to inheritance for values. Normalise BigDecimal scale. And build comparators with comparing, ending with a unique tie-breaker.",
             "Never override equals without hashCode. Never compare by subtraction. Never extend a value class and add to equals. Never use or mutate mutable keys. "
             "Keep doubles and arrays out of keys. And never assume a TreeSet and a HashSet agree, unless the ordering is consistent with equals.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 23 · equals, hashCode &amp; Comparators",
         body=bullets(["Hash collections use `hashCode` + `equals`; sorted ones only `compare`",
                       "Equal objects **must** have equal hash codes",
                       "Records generate both — they can't drift",
                       "`Long.compare`, never subtraction; total orders for `TreeSet`",
                       "That completes the **Collections** section"], cls="bullets recap"),
         narration=[
             "To recap. Hash collections use hashCode and equals, while sorted collections use only compare. Equal objects must have equal hash codes. "
             "Records generate both methods, so they can't drift. Use Long dot compare, never subtraction, and make orderings total for TreeSet.",
             "That completes the Collections section of the handbook. Next comes concurrency. Thanks for watching.",
         ]),
]
