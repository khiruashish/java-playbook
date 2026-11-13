"""Chapter 09 — Optional & Null Strategy. Source: docs/02-language/09-optional.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 09 · Optional & Null Strategy"
SECTION = "Java 8"

SLIDES = [
    dict(kind="title",
         title="Optional &amp; Null Strategy",
         kicker="Java 8 · Chapter 09",
         body='<p class="sub">What <code>Optional</code> actually solves, how to compose it instead of unwrapping it, '
              'and the rest of a null strategy.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter nine: Optional and null strategy.",
             "Optional was added to solve one problem. A method that may have nothing to return should be able to say so in its signature. "
             "It was not added to eliminate null from Java. Treat it that way and you end up with Optional fields, Optional parameters and Optional lists, all worse than the null they replaced.",
         ]),

    dict(title="The signature was silent",
         kicker="The problem",
         body='<div class="grid2 start">'
              + code('''
// Java 7 — does this return null?
InventoryItem item = catalogue.find(sku);
if (item != null) {
    Vendor vendor = item.vendor();
    if (vendor != null) {
        Address address = vendor.warehouseAddress();
        if (address != null) {
            return address.pincode();
        }
    }
}
return "UNKNOWN";''', title="CallerBefore.java", size=26)
              + frag(code('''
// Java 8 — the signature says so
public Optional<InventoryItem> find(Sku sku) {
    return Optional.ofNullable(bySku.get(sku));
}

return catalogue.find(sku)
    .map(InventoryItem::vendor)
    .map(Vendor::warehouseAddress)
    .map(Address::pincode)
    .orElse("UNKNOWN");''', title="CallerAfter.java", size=26), 1)
              + "</div>",
         narration=[
             "In Java 7, a catalogue lookup that might find nothing just returns an InventoryItem. The signature is silent, so every caller has to guess. "
             "And the null checks nest deeper at every level: item, vendor, address.",
             "In Java 8, the return type says it: Optional of InventoryItem. And the caller becomes a flat chain. "
             "Map to the vendor, then the address, then the pincode, or else unknown. A missing SKU, vendor or address all end up at unknown, with no branching.",
         ]),

    dict(title="Short-circuit, then exit deliberately",
         kicker="Mental model",
         body=flow(["`Optional<InventoryItem>`",
                    "**present?** `map` · `flatMap` · `filter` transform it",
                    "**empty?** every operation stays empty — functions never run",
                    "**exit** `orElse` · `orElseGet` · `orElseThrow`"], step_start=0)
              + frag('<p class="callout">There is no implicit unwrap. You decide what absence means, at the point where you know.</p>', 3),
         narration=[
             "Optional is a return type that says possibly nothing, plus a vocabulary for handling that without branching.",
             "If a value is present, map, flatMap and filter transform it.",
             "If it's empty, every operation just returns empty, without calling your function. That's what collapses the nested ifs into a flat pipeline.",
             "And at the end you must exit deliberately, with orElse, orElseGet or orElseThrow. There's no implicit unwrap. You choose what absence means, at the point where you know.",
         ]),

    dict(title="Return types only",
         kicker="Where Optional belongs",
         body='<div class="grid4" style="grid-template-columns:repeat(5,1fr)">'
              + card("Return type", "✓ the use case", "indigo", 0)
              + card("Field", "✗ null or a default", "fuchsia", 1)
              + card("Parameter", "✗ use overloads", "fuchsia", 1)
              + card("Element", "✗ filter it out", "fuchsia", 1)
              + card("Optional<List>", "✗ return an empty list", "fuchsia", 1)
              + "</div>"
              + frag('<p class="callout">The JDK is the guide: <code>Optional</code> appears as a return type on '
                     '<code>findFirst</code>, <code>min</code>, <code>max</code>, <code>reduce</code> — and nowhere else. '
                     'No JDK class has an <code>Optional</code> field or parameter.</p>', 2),
         narration=[
             "Where does Optional belong? On return types. That's the use case.",
             "Not on fields: use null or a sensible default. Not on parameters: use overloads. Not inside collections: filter the empties out. "
             "And never Optional of a list, because then there are two ways to say nothing. Just return an empty list.",
             "The JDK itself is the guide. Optional appears as a return type on findFirst, min, max and reduce, and nowhere else. No JDK class has an Optional field or parameter.",
         ]),

    dict(title="The API in two halves",
         kicker="Core API",
         body='<div class="grid2 start">'
              + frag(table(["Create & transform", ""], [
                    ["`Optional.of(v)`", "**Throws** if null — an assertion"],
                    ["`Optional.ofNullable(v)`", "Empty if null — a conversion"],
                    ["`map` / `flatMap`", "Transform; `flatMap` if fn returns `Optional`"],
                    ["`filter`", "Empty if the predicate fails"],
                    ["`or(...)` (9)", "Fall back to another `Optional`"],
                    ["`stream()` (9)", "Zero or one element"],
                ], cls="sm"), 0)
              + frag(table(["Exit", ""], [
                    ["`orElse(v)`", "Default — **always evaluated**"],
                    ["`orElseGet(() -> ...)`", "Lazy default"],
                    ["`orElseThrow(() -> ...)`", "Your exception"],
                    ["`orElseThrow()` (10)", "`NoSuchElementException`"],
                    ["`ifPresentOrElse` (9)", "Both branches"],
                    ["`get()`", "**Avoid** — same as `orElseThrow()`"],
                ], cls="sm"), 1)
              + "</div>",
         narration=[
             "The API has two halves. To create one, use Optional dot of when null would be a bug, because it throws immediately. "
             "Use ofNullable at the boundary with code that returns null. Using ofNullable everywhere hides bugs that of would surface. "
             "Then stay inside the Optional with map, flatMap, filter, and Java 9's or and stream.",
             "To leave, choose deliberately. orElse with a default value, orElseGet with a lazy one, orElseThrow with your own exception, or ifPresentOrElse for both branches. "
             "And avoid get. It throws on empty, exactly like the null dereference Optional was meant to prevent.",
         ]),

    dict(title="orElse vs orElseGet",
         kicker="Worked example",
         body=code('''
// computeFallbackPrice() runs EVERY TIME — even when a price is present
Money price = catalogue.priceFor(sku).orElse(computeFallbackPrice(sku));

// runs only when empty
Money price = catalogue.priceFor(sku).orElseGet(() -> computeFallbackPrice(sku));

// exceptions too: pass a supplier
.orElseThrow(() -> new SkuNotFoundException(sku));''', title="EagerDefault.java", size=28)
              + frag('<p class="callout"><code>orElse</code> for literals and constants. <code>orElseGet</code> for anything computed.</p>', 1),
         narration=[
             "Here's a cost hiding in plain sight. orElse takes a value, so its argument is evaluated before the call, every time. "
             "Here, the fallback price is computed on every lookup, even when the real price was found. With a side-effecting call, that's a bug, not just waste. "
             "orElseGet takes a supplier, so it only runs when the Optional is empty. The same goes for exceptions: pass a supplier to orElseThrow.",
             "The rule is simple. orElse for literals and constants, orElseGet for anything computed.",
         ]),

    dict(title="Compose, don't unwrap",
         kicker="Worked examples",
         body=code('''
catalogue.find(sku).map(InventoryItem::vendor);             // Optional<Vendor>
catalogue.find(sku).flatMap(InventoryItem::preferredVendor); // fn returns Optional → flatMap

catalogue.find(sku).filter(item -> item.available() > 0)
                   .filter(item -> !item.discontinued());''', title="MapFlatMapFilter.java", size=26)
              + code('''
skus.stream().map(catalogue::find).flatMap(Optional::stream).toList();   // Java 9''',
                     title="Look up many, keep the ones that exist", step=1, size=26)
              + code('''
primaryVendorFor(sku).or(() -> backupVendorFor(sku))
                     .or(() -> Optional.of(Vendor.DEFAULT));''', title="Fallback.java — or() chains sources", step=2, size=26),
         narration=[
             "Composition follows the same rules as streams. Map when the function returns a plain value. FlatMap when it already returns an Optional, "
             "otherwise you'd get an Optional of an Optional. And filter turns a present but unsuitable value into empty, so a check joins the chain instead of interrupting it.",
             "To look up many things and keep the ones that exist, map each SKU to an Optional, then flatMap with Optional colon colon stream. Empties disappear, values are unwrapped.",
             "And or chains alternative sources: try the primary vendor, then the backup, then a default. Use or while you still want an Optional, and orElseGet when you're leaving.",
         ]),

    dict(title="Four anti-patterns",
         kicker="What not to do",
         body='<div class="grid2 start">'
              + frag(code('''
private Optional<DeliverySlot> slot; // ✗
private DeliverySlot slot;  // ✓ null = unscheduled''', title="1 · Field", size=24), 0)
              + frag(code('''
confirm(Cart c, Optional<Coupon> k) // ✗
confirm(Cart c)                     // ✓ overload
confirm(Cart c, Coupon k)           // ✓''', title="2 · Parameter", size=24), 1)
              + frag(code('''
Optional<List<OrderLine>> lines()      // ✗
List<OrderLine> lines()                // ✓ empty list''', title="3 · Wrapped collection", size=24), 2)
              + frag(code('''
if (found.isPresent())          // ✗
    process(found.get());
found.ifPresent(this::process); // ✓''', title="4 · isPresent + get", size=24), 3)
              + "</div>",
         narration=[
             "Four anti-patterns. One: Optional as a field. It allocates a wrapper per instance, and Optional isn't Serializable, deliberately. Null or a default says the same thing.",
             "Two: Optional as a parameter. The caller has to wrap, and you still have to handle null. "
             "If you see a caller writing Optional dot empty as an argument, it's doing work an overload should have done.",
             "Three: Optional of a list. Is nothing an empty Optional, or an empty list? Return an empty list.",
             "Four: isPresent followed by get. That's the null check you were trying to avoid, plus an allocation. Use ifPresent or map.",
         ]),

    dict(title="Internals",
         kicker="Value-based · allocation · get()",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Value-based", "Identity unspecified: never `==`, never lock on it, not `Serializable`.", "indigo", 0)
              + card("It allocates", "Each `Optional` is an object. Escape analysis **often** removes it in hot paths — not always.", "cyan", 1)
              + card("get() was a mistake", "As unsafe as a null dereference. Java 10 added `orElseThrow()` with an honest name.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Three internals. Optional is a value-based class. Its identity is unspecified, so never compare two with double equals, never synchronise on one, and it isn't Serializable.",
             "Every Optional is an object. In a hot loop, the JIT's escape analysis often removes the allocation, but not always. "
             "In a measured hot path, returning a nullable value with a documented contract is a legitimate choice. Everywhere else, clarity wins.",
             "And get is a design regret. It's as unsafe as the null dereference it replaced, and its name makes it look like the normal way in. "
             "Java 10 added orElseThrow with no arguments as the honestly named equivalent.",
         ]),

    dict(title="The rest of a null strategy",
         kicker="Optional covers one quarter",
         body=table(["Situation", "Tool"], [
                    ["Method may return nothing", "`Optional<T>`"],
                    ["Parameter must not be null", "`Objects.requireNonNull(x, \"sku\")` at the top"],
                    ["Collection result", "An **empty collection**, never null"],
                    ["Field that may be absent", "`null` + a nullability annotation, or a default"],
                    ["Absence has behaviour", "Null Object — `Vendor.NONE`"],
                    ["Null-returning API", "Convert at the boundary with `ofNullable`"],
                ], step_per_row=0, cls="wide pairs"),
         narration=[
             "Optional covers return types. A real null strategy needs more tools.",
             "For parameters that must not be null, call Objects dot requireNonNull with the parameter name at the top of the method, so it fails at the boundary instead of fifteen frames later.",
             "For collections, return an empty collection, never null.",
             "For fields, null plus a nullability annotation, or a default value. Pick one annotation library per codebase and use it consistently.",
             "When absence has behaviour, use a null object, like a vendor dot none with no-op methods.",
             "And at the boundary with older code that returns null, convert once with ofNullable.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Return `Optional` where absence is normal",
                         "`of` for bugs, `ofNullable` at boundaries",
                         "Chain `map` / `flatMap` / `filter`",
                         "`orElseGet` for anything computed",
                         "`orElseThrow(() -> ...)` with the missing key",
                         "`requireNonNull` on public parameters"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`Optional` fields or parameters",
                         "`Optional<List<T>>` or `List<Optional<T>>`",
                         "`get()` — use `orElseThrow()`",
                         "`isPresent()` + `get()`",
                         "Compare with `==`",
                         "Wrap a value whose default is obvious"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Return Optional where absence is a normal outcome, like a lookup that may miss. Use of when null is a bug and ofNullable at boundaries. "
             "Chain with map, flatMap and filter. Use orElseGet for anything computed. When absence really is an error, orElseThrow with an exception that names the missing key. "
             "And requireNonNull on public parameters.",
             "Never use Optional for fields or parameters. Never wrap a collection in an Optional, or put Optionals in a collection. "
             "Never call get, use orElseThrow. Never write isPresent then get. Never compare Optionals with double equals. "
             "And don't wrap a value whose default is obvious.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "`Optional`, `OptionalInt/Long/Double`"],
                    ["**9**", "`stream()`, `or()`, `ifPresentOrElse`"],
                    ["**10–11**", "`orElseThrow()`, `isEmpty()`"],
                    ["**14**", "Helpful NullPointerException messages (JEP 358)"],
                    ["**16–21**", "Records; sealed `Found` / `NotFound` results with pattern matching"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 introduced Optional and its primitive versions.",
             "Java 9 added stream, or, and ifPresentOrElse, which made composition much smoother.",
             "Java 10 added orElseThrow with no arguments, and Java 11 added isEmpty, which reads better than not isPresent.",
             "Java 14's helpful NullPointerException messages name the exact expression that was null, which narrowed the gap Optional was filling.",
             "And with records, sealed types and pattern matching, a sealed result like found or not found is now a good alternative when absence needs to carry a reason.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 09 · Optional &amp; Null Strategy",
         body=bullets(["`Optional` is for **return types** — absence in the signature",
                       "Chain with `map` / `flatMap` / `filter`; exit deliberately",
                       "`orElse` is eager — use `orElseGet` for computed defaults",
                       "No `Optional` fields, parameters or wrapped collections",
                       "`requireNonNull`, empty collections and null objects do the rest",
                       "Next: **Ch 10 · java.time**"], cls="bullets recap"),
         narration=[
             "To recap. Optional is for return types, so absence shows up in the signature. Chain it with map, flatMap and filter, and exit deliberately. "
             "orElse is eager, so use orElseGet for anything computed. Keep Optional out of fields, parameters and collections. "
             "And complete your null strategy with requireNonNull, empty collections and null objects.",
             "Next is chapter ten, java dot time. Thanks for watching.",
         ]),
]
