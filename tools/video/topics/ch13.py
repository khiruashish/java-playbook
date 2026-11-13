"""Chapter 13 — Pattern Matching. Source: docs/02-language/13-pattern-matching.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 13 · Pattern Matching"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="Pattern Matching",
         kicker="Language · Chapter 13",
         body='<p class="sub">Dispatch on shape, destructure in the same step, and let the compiler prove you handled every case.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirteen: pattern matching.",
             "It arrived in three instalments: instanceof patterns in Java 16, then switch patterns and record patterns in 21. "
             "It only becomes compelling when all three combine with sealed types. Then Java can dispatch on shape, destructure, and prove you handled every case.",
         ]),

    dict(title="Test, cast, repeat",
         kicker="The problem",
         body='<div class="grid2 start">'
              + code('''
if (event instanceof StockReserved) {
    StockReserved e = (StockReserved) event;
    ledger.record(e.sku(), e.quantity());
} else if (event instanceof DispatchFailed) {
    DispatchFailed e = (DispatchFailed) event;
    if (e.retryable()) retryQueue.add(e.orderId());
    else alerting.raise(e.reason());
} else {
    throw new IllegalArgumentException(
        "unknown event: " + event);
}''', title="EventHandlerBefore.java — Java 8", size=23)
              + '<div>' + bullets(["The type is written **twice** per branch",
                                   "**Nothing checks completeness** — a new event compiles, then throws",
                                   "Components need a second step after the cast",
                                   "The `else throw` is a confession the compiler couldn't help"], start_step=0, cls="bullets sm")
              + "</div></div>",
         narration=[
             "Here's an event handler in Java 8. Test the type, cast it, then use it. The type is written twice in every branch.",
             "Nothing checks completeness. Add a fifth event type and this still compiles, then throws in production.",
             "Getting at the event's fields needs a separate step after the cast.",
             "And that else throw at the bottom is a confession that the compiler couldn't help. Pattern matching fixes all four.",
         ]),

    dict(title="A pattern is a test plus a binding",
         kicker="Mental model",
         body=table(["Pattern", "Example", "Binds"], [
                    ["Type pattern", "`case Confirmed c`", "The value, typed"],
                    ["Record pattern", "`case Confirmed(Instant at, String ref)`", "The components"],
                    ["Nested pattern", "`case Dispatched(var at, Vendor(var name, _), var id)`", "Components of components"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout"><b>Sealed</b> = exhaustiveness. <b>Records</b> = destructuring. Without sealed types, '
                     'pattern matching is just a nicer <code>instanceof</code>.</p>', 3),
         narration=[
             "A pattern is a test plus a binding. It asks, does this value have this shape, and if so, names the parts. A type pattern binds the value with its type.",
             "A record pattern goes further and binds the record's components directly.",
             "And patterns nest, so you can bind the components of components, using underscore for parts you don't need.",
             "Remember the two pillars. Sealed types give you exhaustiveness. Records give you destructuring. Without sealed types, pattern matching is just a nicer instanceof.",
         ]),

    dict(title="The handler, rewritten",
         kicker="Worked example",
         body=code('''
public sealed interface OrderEvent
        permits StockReserved, PaymentCaptured, DispatchFailed, OrderCancelled { }

switch (event) {
    case StockReserved(var at, var sku, var qty)              -> ledger.record(sku, qty);
    case PaymentCaptured(var at, var ref, var amount)         -> ledger.credit(ref, amount);
    case DispatchFailed(var at, var id, var why, var retry) when retry -> retryQueue.add(id);
    case DispatchFailed(var at, var id, var why, var retry)   -> alerting.raise(why);
    case OrderCancelled(var at, var id, var why)              -> ledger.reverse(id);
}''', title="EventHandler.java — Java 21", size=24)
              + frag('<p class="callout">No casts, no <code>else throw</code>, <b>no default</b>. Add a fifth event and this stops compiling.</p>', 1),
         narration=[
             "Here's the same handler in Java 21. The events are a sealed interface of records, and each case destructures its record directly into variables. "
             "The guard, when retry, handles the retryable failures, at the same level as every other branch, instead of a nested if.",
             "No casts, no else throw, and no default. The compiler proves the switch is complete. Add a fifth event type and this method stops compiling, along with every other switch over it.",
         ]),

    dict(title="Guards, ordering &amp; dominance",
         kicker="Cases are tested in order",
         body=code('''
return switch (event) {
    case DispatchFailed f when !f.retryable()                  -> "P1";
    case DispatchFailed f when f.occurredAt().isBefore(cutoff) -> "P2";
    case DispatchFailed f                                      -> "P3";
    case OrderCancelled c                                      -> "P4";
    case StockReserved _, PaymentCaptured _                    -> "INFO";   // Java 22: _
};''', title="Guards.java", size=25)
              + code('''
case DispatchFailed f                     -> "P3";
case DispatchFailed f when !f.retryable() -> "P1";   // ✗ dominated by a preceding case label''',
                     title="Dominance.java — compile error", step=1, size=25),
         narration=[
             "Cases are tested in order, so guarded patterns come before the unguarded pattern for the same type. "
             "And when one label lists several patterns, you can't name bindings, since only one will match. Use underscore, from Java 22.",
             "Get the order wrong and the compiler rejects it: this case label is dominated by a preceding case label. "
             "In an if-else chain, that unreachable branch would just silently never run. Here it's a compile error.",
         ]),

    dict(title="Nested destructuring",
         kicker="Test and bind in one pattern",
         body=code('''
record Approved(String ref, Money amount, Card card) implements PaymentResult { }
record Declined(String reason, Card card)            implements PaymentResult { }
record Card(String network, String lastFour) { }

return switch (result) {
    case Approved(var ref, var amount, Card("VISA", var last4))  -> "Visa ..." + last4 + " charged " + amount;
    case Approved(var ref, var amount, Card(var net, var last4)) -> net + " ..." + last4 + " charged " + amount;
    case Declined(var reason, Card(_, var last4))                -> "Declined on ..." + last4 + ": " + reason;
};''', title="Nested.java", size=23)
              + frag('<p class="callout"><code>Card("VISA", var last4)</code> matches a constant component and binds another. '
                     'Past about two levels deep, it becomes write-only code.</p>', 1),
         narration=[
             "Patterns nest. Here, a payment result contains a card. The first case matches only approved payments on a Visa card, and binds the last four digits, all in one pattern. "
             "The last case uses underscore for the card network it doesn't care about.",
             "That's powerful, but keep it shallow. Past about two levels of nesting, a pattern becomes write-only code.",
         ]),

    dict(title="instanceof patterns &amp; flow scoping",
         kicker="Java 16",
         body=code('''
@Override public boolean equals(Object o) {
    return o instanceof Sku other && code.equals(other.code);    // no cast, no null check
}''', title="EqualsWithPattern.java", size=26)
              + code('''
if (!(payload instanceof Cart cart)) {
    throw new IllegalArgumentException("expected a cart");
}
return cart.total();          // cart IS in scope — the only way here is a match

if (event instanceof DispatchFailed f || f.retryable()) { }   // ✗ compile error''',
                     title="FlowScoping.java", step=1, size=26),
         narration=[
             "In everyday code, the instanceof pattern is the big win. An equals method becomes one line, with no separate cast and no null check, because null never matches a type pattern.",
             "The binding follows flow scoping, not normal block scoping. It's in scope wherever the compiler can prove the pattern matched. "
             "So with a negated test and an early throw, cart is in scope for the rest of the method. That makes guard clauses natural. "
             "But with an or, the right side runs when the pattern didn't match, so using the binding there is a compile error.",
         ]),

    dict(title="Null is always explicit",
         kicker="Behaviour",
         body=table(["Construct", "Null behaviour"], [
                    ["`x instanceof T t`", "`false` — never matches"],
                    ["Pattern `switch`, no `case null`", "Throws `NullPointerException`"],
                    ["`case null ->`", "Matches that branch"],
                    ["`case null, default ->`", "Null joins the default branch"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "Null handling is always explicit. instanceof with a pattern simply returns false for null.",
             "A pattern switch with no case null throws a NullPointerException, just like the old switch did.",
             "Write case null to handle it in its own branch.",
             "Or case null comma default to treat it like anything else. Either way, you decided. Nothing is silent.",
         ]),

    dict(title="When not to use it",
         kicker="The expression problem",
         body='<div class="grid2 start">'
              + code('''
// ✗ behaviour the types should own
Money fee(PricingRule rule) {
  return switch (rule) {
    case FlatDiscount f    -> f.amount();
    case PercentDiscount p -> sub.times(p.pct());
    case FreeDelivery fd   -> Money.ZERO;
  };
}''', title="Dispatch table", size=24)
              + frag(code('''
// ✓ polymorphism
interface PricingRule {
    Money apply(Money subtotal);
}''', title="Interface method", size=24), 1)
              + "</div>"
              + frag('<p class="callout">Polymorphism makes <b>adding types</b> easy. Pattern matching makes <b>adding operations</b> easy. '
                     'Choose by which axis actually changes.</p>', 2),
         narration=[
             "Pattern matching isn't always the answer. If every branch does the same kind of thing with each type's own data, like computing a fee, that's a dispatch table for behaviour the types should own.",
             "An interface method is better there. New pricing rules need no change to existing code.",
             "This is the classic expression problem. Polymorphism makes adding new types easy. Pattern matching makes adding new operations easy, like rendering, serialising or reporting over a closed set. "
             "Choose based on which one actually changes in your domain.",
         ]),

    dict(title="Internals",
         kicker="How a pattern switch runs",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("invokedynamic", "Compiles to `SwitchBootstraps.typeSwitch` — a matcher built once and cached, not a chain of `instanceof`.", "indigo", 0)
              + card("Accessors run", "Record patterns **call the accessors** to bind. Keep them trivial and side-effect free.", "cyan", 1)
              + card("MatchException", "The hidden default throws if a library adds a subtype **without** your switch being recompiled.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Under the hood, a pattern switch compiles to an invokedynamic call. A bootstrap builds an efficient matcher once and caches it. It's not a linear chain of instanceof checks.",
             "Record patterns bind by calling the accessor methods. So an accessor with side effects runs during matching. Keep accessors trivial.",
             "And the compiler still adds a hidden default that throws a MatchException. If a library adds a new subtype and your switch isn't recompiled, you get a loud failure instead of a silent wrong answer. "
             "That's why sealing a public library type makes adding a subtype a breaking change.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`instanceof` patterns in `equals`",
                         "Negated `instanceof` for guard clauses",
                         "Sealed interface + records for closed sets",
                         "No `default` in sealed switches",
                         "Guarded cases before unguarded",
                         "`var` in record patterns; _ (underscore) for unused parts",
                         "`case null` where null is possible"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Pattern matching where polymorphism fits",
                         "`default` in a switch you want checked",
                         "Destructure more than ~2 levels deep",
                         "Side effects in record accessors",
                         "Assume a pattern switch handles null",
                         "Seal a public library type casually"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use instanceof patterns in equals, and the negated form for guard clauses. Pair sealed interfaces with records. "
             "Leave default out of sealed switches. Put guarded cases first. Use var in record patterns and underscore for unused parts. And write case null wherever null is possible.",
             "Never use pattern matching where polymorphism fits. Never add default to a switch you want checked. Don't nest more than about two levels. "
             "Keep side effects out of accessors. Don't assume a pattern switch handles null. And don't seal a public library type casually.",
         ]),

    dict(title="Java 14 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**16**", "`instanceof` patterns final; records final"],
                    ["**17**", "Sealed classes final"],
                    ["**21**", "**Pattern matching for `switch`** and **record patterns** final"],
                    ["**22**", "Unnamed variables and patterns — _ (underscore)"],
                    ["**23–26**", "Primitive patterns (`case int i`) — **still preview**"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 16 finalised instanceof patterns, along with records.",
             "Java 17 finalised sealed classes.",
             "Java 21 delivered the complete feature: pattern matching for switch, and record patterns.",
             "Java 22 added the underscore for unnamed variables and patterns.",
             "And patterns over primitive types, like case int i, are still in preview. They need enable-preview and may change. Everything else in this chapter is final.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 13 · Pattern Matching",
         body=bullets(["A pattern = **a test plus a binding**",
                       "Sealed + records → **exhaustive, destructuring** switches",
                       "Guards first; the compiler rejects **dominated** cases",
                       "Bindings follow **flow scoping**; null is always explicit",
                       "Polymorphism when types change; patterns when operations change",
                       "Next: **Ch 14 · Java 21–26 Language Features**"], cls="bullets recap"),
         narration=[
             "To recap. A pattern is a test plus a binding. With sealed types and records, you get exhaustive switches that destructure as they match. "
             "Put guarded cases first, and the compiler will reject any that are dominated. Bindings follow flow scoping, and null handling is always explicit. "
             "And use polymorphism when the types change, pattern matching when the operations do.",
             "Next is chapter fourteen, the language features of Java 21 to 26. Thanks for watching.",
         ]),
]
