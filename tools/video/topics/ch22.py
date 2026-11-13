"""Chapter 22 — Immutability & Defensive Copying. Source: docs/03-collections/22-immutability.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 22 · Immutability & Defensive Copying"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="Immutability &amp; Defensive Copying",
         kicker="Collections · Chapter 22",
         body='<p class="sub">What immutable really requires, where the defensive copies go, and why most "immutable" classes have a hole.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-two: immutability and defensive copying.",
             "Immutability removes whole categories of bugs at once. Nothing can corrupt the object, no thread can see it half-updated, and its invariants can't drift. "
             "The cost is mostly discipline. And that's where it goes wrong. Most supposedly immutable classes in real codebases have a hole.",
         ]),

    dict(title="final is not immutable",
         kicker="The problem",
         body=code('''
public final class Order {
    private final List<OrderLine> lines;         // final — so it's immutable?
    public Order(OrderId id, List<OrderLine> lines) { this.lines = lines; }   // stores caller's list
    public List<OrderLine> lines() { return lines; }                         // hands it out
}''', title="LeakyOrder.java", size=25)
              + code('''
input.add(line2);                  // 1. the caller kept a reference to the stored list
order.lines().add(line3);          // 2. the accessor handed out the internal list
order.lines().get(0).setQty(99);   // 3. the elements themselves are mutable''', title="Mutations.java", step=1, size=25),
         narration=[
             "Here's an order that looks safe. The class is final, the field is final. But the constructor stores the caller's list, and the accessor hands it straight back out.",
             "So there are three ways to change it without touching the class. The caller still holds the list it passed in. The accessor exposes the internal list. And the line items themselves are mutable. "
             "final stops you reassigning the reference. It does nothing about what the reference points to.",
         ]),

    dict(title="Four things called \"immutable\"",
         kicker="Mental model",
         body=table(["", "Modify via it?", "Others' changes visible?", "Elements mutable?"], [
                    ["`final List` field", "Yes", "Yes", "Yes"],
                    ["`Collections.unmodifiableList(l)`", "No", "**Yes**", "Yes"],
                    ["`List.copyOf(l)`", "No", "No", "**Yes**"],
                    ["`List.copyOf(l)` of records", "No", "No", "No ✓"],
                ], step_per_row=0, cls="sm"),
         narration=[
             "There are four different things people call immutable. A final field: you can still modify the list through it, and so can anyone else.",
             "An unmodifiable view: you can't modify it, but the owner can, and you'll see those changes.",
             "List dot copyOf: a real snapshot, but if the elements are mutable, they can still change.",
             "Only a copied list of immutable elements, like records, is actually immutable. The rest are useful, but each one has a hole.",
         ]),

    dict(title="The recipe",
         kicker="Mental model",
         body=flow(["`final` class or record", "`private final` fields, no setters", "**Copy mutable inputs** in the constructor",
                    "Store immutable types — accessors need no copy", "Immutable components all the way down"], step_start=0),
         narration=[
             "Here's the recipe. Make the class final, or use a record, so a subclass can't add mutable state.",
             "Private final fields, and no setters.",
             "Copy every mutable input inside the constructor, so the caller can't keep a handle on your state.",
             "Store immutable types, so your accessors don't need to copy on the way out.",
             "And make sure the components are immutable all the way down.",
         ]),

    dict(title="The order, fixed",
         kicker="Worked example",
         body=code('''
public record Order(OrderId id, CustomerId customer, List<OrderLine> lines, Instant placedAt) {
    public Order {
        Objects.requireNonNull(id, "id");
        lines = List.copyOf(lines);                       // copy IN — also rejects nulls
        if (lines.isEmpty()) throw new IllegalArgumentException("order has no lines");
    }
}
public record OrderLine(Sku sku, int quantity, Money unitPrice) { }    // immutable elements''',
                   title="Order.java", size=25)
              + frag('<p class="callout"><b>Copy on the way in, store an immutable type, and the way out takes care of itself.</b></p>', 1)
              + frag(code('''
List<OrderLine> immutable = List.of(line1, line2);
List.copyOf(immutable) == immutable;     // true — no copy needed, so defensive copying is nearly free''',
                          title="CopyOfIdentity.java", size=24), 2),
         narration=[
             "Here's the order fixed. It's a record. The compact constructor validates, then copies the lines with List dot copyOf, which also rejects nulls. And OrderLine is a record of immutable parts.",
             "All three mutations are now impossible. And no copy is needed in the accessor, because what's stored is already immutable. Copy on the way in, store an immutable type, and the way out takes care of itself.",
             "Better still, List dot copyOf doesn't copy if its argument is already an immutable JDK list. It just returns it. "
             "So in a codebase that uses records and List dot of throughout, defensive copying is nearly free. It does copy an unmodifiable view, correctly, since a view can still change.",
         ]),

    dict(title="Arrays break records",
         kicker="Worked example",
         body=code('''
public record Signature(byte[] bytes) {
    public Signature { bytes = bytes.clone(); }            // copy in
    @Override public byte[] bytes() { return bytes.clone(); }  // copy out
    // and override equals/hashCode — generated ones compare array IDENTITY
}''', title="ArrayComponentFixed.java", size=26)
              + frag('<p class="callout">Records are only <b>shallowly</b> immutable. Arrays are <b>never</b> immutable — prefer a <code>List</code> or a dedicated type.</p>', 1),
         narration=[
             "Records don't help with arrays. A byte array component can be changed by the caller who passed it in, and by anyone calling the accessor. "
             "So you'd have to clone on the way in, clone on the way out by overriding the accessor, and override equals and hashCode, because the generated ones compare arrays by identity.",
             "Records are only shallowly immutable, and arrays are never immutable. Usually the better answer is a list, or a dedicated immutable type.",
         ]),

    dict(title="Change = a new instance",
         kicker="Withers and builders",
         body=code('''
public record CartLine(Sku sku, int quantity, Money unitPrice) {
    public CartLine withQuantity(int q) { return new CartLine(sku, q, unitPrice); }
}
CartLine updated = line.withQuantity(line.quantity() + 1);    // original untouched''',
                   title="Withers.java", size=25)
              + code('''
DispatchRequest req = DispatchRequest.builder(orderId)
    .vendor(vendor).slot(slot).note("fragile").priority(Priority.HIGH)
    .build();          // builder mutable and single-threaded → product immutable and shareable''',
                     title="Builder.java", step=1, size=25),
         narration=[
             "You change an immutable object by making a new one. A wither, like withQuantity, returns a new CartLine and leaves the original untouched. "
             "And since the compact constructor runs every time, validation can't be bypassed.",
             "When there are many optional parts, positional construction gets unreadable, so use a builder. The builder is mutable and single-threaded. "
             "The product is immutable and safe to share. The record's constructor still validates and copies, so the builder can't produce a leaky object.",
         ]),

    dict(title="Free thread safety",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Final-field semantics", "A properly constructed object with all-final fields is safe to share **with no synchronisation**.", "indigo", 0)
              + card("Two conditions", "`this` must not escape the constructor, and copies must happen **inside** it — that's what gets frozen.", "cyan", 1)
              + card("Often smaller", "`List.of(a, b)` is one object with two fields — no array. Immutable can be cheaper than `ArrayList`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Here's the big payoff. Under the Java Memory Model, an object with all-final fields, properly constructed, can be shared between threads with no synchronisation at all. No locks, no volatile.",
             "Two conditions. The reference to this must not escape during construction. And the guarantee covers the state as of the end of the constructor, which is exactly why the defensive copy must happen inside it.",
             "And immutable isn't necessarily more expensive. List dot of with two elements is a single small object with two fields, no backing array. That's smaller than an ArrayList.",
         ]),

    dict(title="What it costs, and the holes",
         kicker="Internals",
         body=table(["Operation", "Cost"], [
                    ["`List.copyOf` of an already-immutable list", "**Zero**"],
                    ["A wither on a record", "One small allocation"],
                    ["Append one element to an immutable list of 1M", "**O(n)** — copy everything"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">Non-final classes are a hole: a subclass can override accessors. That\'s why <code>BigDecimal</code> '
                     '(not final) is a known wart. Use <code>final</code> classes or records.</p>', 3),
         narration=[
             "What does it cost? Copying an already-immutable list costs nothing.",
             "A wither is one small, short-lived allocation.",
             "The real cost is appending to a huge immutable collection, which copies everything. For a million elements that's prohibitive. "
             "Most domain objects have tens of items, so it doesn't matter. For large, frequently-updated collections, use a mutable builder, or a persistent collection library.",
             "And remember the inheritance hole. If the class isn't final, a subclass can override an accessor and return changing values. That's why records, which are implicitly final, are the safest default.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Records, with `List.copyOf` in the compact constructor",
                         "Copy inputs **in** the constructor",
                         "Store immutable types",
                         "Withers for change; builders for many options",
                         "`java.time` instead of `Date`",
                         "Return snapshots, not views"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Assume `final` means immutable",
                         "Return a mutable internal collection",
                         "Store a caller's collection uncopied",
                         "Arrays in records without copying both ways",
                         "Treat `unmodifiableList` as a snapshot",
                         "Let `this` escape the constructor"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Default to records, with List dot copyOf in the compact constructor. Copy inputs inside the constructor. Store immutable types. "
             "Use withers for change and builders for many options. Replace Date with java dot time. And return snapshots, not views.",
             "Never assume final means immutable. Never return a mutable internal collection, or store a caller's collection without copying it. "
             "Never put arrays in a record without copying both ways. Never treat unmodifiableList as a snapshot. And never let this escape the constructor.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 22 · Immutability",
         body=bullets(["`final` fixes the **reference**, not the object",
                       "Copy in, store immutable — the way out takes care of itself",
                       "`List.copyOf` is free when the input is already immutable",
                       "All-final, properly constructed objects need **no locks**",
                       "Next: **Ch 23 · equals, hashCode &amp; Comparators**"], cls="bullets recap"),
         narration=[
             "To recap. final fixes the reference, not the object. Copy on the way in and store immutable types, and the way out takes care of itself. "
             "List dot copyOf is free when its input is already immutable. And properly constructed immutable objects need no locks at all.",
             "Next is chapter twenty-three: equals, hashCode and comparators. Thanks for watching.",
         ]),
]
