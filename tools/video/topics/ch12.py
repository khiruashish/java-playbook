"""Chapter 12 — Java 14–17: Records, Sealed Types, Text Blocks, Switch Expressions.
Source: docs/02-language/12-java-14-to-17.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 12 · Java 14–17: Records, Sealed Types, Text Blocks"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="Records, Sealed Types, Text Blocks",
         kicker="Language · Chapter 12 · Java 14–17",
         body='<p class="sub">Four features designed to compose — and together, they give Java algebraic data types.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twelve: Java 14 to 17.",
             "Four features arrived together and were designed to compose: switch expressions, text blocks, records, and sealed types. "
             "Each one removes boilerplate. Together they give Java algebraic data types, which is what makes pattern matching worth having.",
         ]),

    dict(title="Sixty lines that say nothing",
         kicker="The problem",
         body='<div class="grid2 start">'
              + code('''
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;
    public Money(BigDecimal a, Currency c) { ... }
    public BigDecimal getAmount() { ... }
    public Currency getCurrency() { ... }
    @Override public boolean equals(Object o) { ... }
    @Override public int hashCode() { ... }
    @Override public String toString() { ... }
}''', title="MoneyBefore.java — Java 8", size=23)
              + frag(code('''
public record Money(BigDecimal amount,
                    Currency currency) { }''', title="Money.java — Java 16", size=28)
                     + bullets(["Private final fields, canonical constructor",
                                "Accessors `amount()` — not `getAmount()`",
                                "`equals`, `hashCode`, `toString` — can't drift"], cls="bullets sm"), 1)
              + "</div>",
         narration=[
             "A value object in Java 8 is a page of mechanical code: fields, a constructor, getters, equals, hashCode and toString. "
             "Every line can be got wrong, and when you add a field, equals and hashCode quietly drift out of sync. That's a standing source of bugs in collections.",
             "In Java 16, it's one line. A record generates private final fields, a constructor, accessors, and equals, hashCode and toString, all derived from the components, so they can't drift.",
         ]),

    dict(title="Make the compiler reason about your data",
         kicker="Mental model",
         body=flow(["**Switch expressions** (14)\na switch that produces a value",
                    "**Text blocks** (15)\nmulti-line literals",
                    "**Records** (16)\nthese components are the state",
                    "**Sealed** (17)\nthese are all the cases"], step_start=0)
              + frag('<p class="callout">Sealed interface + records = <b>algebraic data types</b>. Add a case and every switch over it '
                     'becomes a <b>compile error</b> — not a runtime surprise.</p>', 4),
         narration=[
             "Here's the through-line: make the compiler able to reason about your data. Switch expressions, in Java 14, make switch produce a value.",
             "Text blocks, in 15, give you readable multi-line strings.",
             "Records, in 16, tell the compiler: these components are the whole state.",
             "And sealed types, in 17, tell it: these are all the cases.",
             "Combine a sealed interface with record implementations and you have an algebraic data type. "
             "An exhaustive switch over it needs no default, and adding a new case becomes a compile error everywhere it matters.",
         ]),

    dict(title="Records: compact constructor &amp; defensive copies",
         kicker="Worked example",
         body=code('''
public record Money(BigDecimal amount, Currency currency) {
    public Money {                                         // compact constructor
        Objects.requireNonNull(amount, "amount");
        amount = amount.setScale(2, RoundingMode.HALF_UP); // reassign the parameter
    }
    public static Money rupees(String a) { return new Money(new BigDecimal(a), INR); }
}''', title="Money.java", size=26)
              + code('''
public record Cart(CartId id, List<CartLine> lines) {
    public Cart {
        lines = List.copyOf(lines);    // without this, callers can still mutate the cart
    }
}''', title="Cart.java", step=1, size=26),
         narration=[
             "The feature people miss is the compact constructor. It has no parameter list, runs before the fields are assigned, and works on the parameters. "
             "So you validate there, and you can normalise by reassigning a parameter. Here, the amount is always stored with two decimal places.",
             "And the single most common record bug: records are only shallowly immutable. If a component is a list, whoever passed it in can still change it. "
             "Always defensively copy collections in the compact constructor. List dot copyOf also rejects nulls, which is usually what you want.",
         ]),

    dict(title="Sealed hierarchy of records",
         kicker="Worked example",
         body=code('''
public sealed interface OrderState permits Pending, Confirmed, Dispatched, Cancelled {
    Instant since();
}
public record Pending(Instant since)                                  implements OrderState { }
public record Confirmed(Instant since, String paymentReference)       implements OrderState { }
public record Dispatched(Instant since, Vendor vendor, String trackingId) implements OrderState { }
public record Cancelled(Instant since, String reason)                implements OrderState { }''',
                   title="OrderState.java", size=23)
              + code('''
return switch (state) {                    // no default needed
    case Pending p    -> "We're confirming your order.";
    case Confirmed c  -> "Confirmed — payment " + c.paymentReference();
    case Dispatched d -> "On its way with " + d.vendor().name();
    case Cancelled c  -> "Cancelled: " + c.reason();
};''', title="StatusMessage.java", step=1, size=25),
         narration=[
             "Here's the combination. OrderState is a sealed interface that permits exactly four records. "
             "Each state carries exactly its own data. A pending order has no payment reference, because it doesn't have one yet. "
             "That removes a whole class of bugs: nullable fields that are only sometimes filled in.",
             "Now a switch over the state needs no default, because the compiler knows the set is closed. "
             "Add a fifth state, and this method stops compiling, along with every other switch over OrderState. The change surfaces everywhere it needs to.",
         ]),

    dict(title="Switch expressions",
         kicker="A different construct, not nicer syntax",
         body='<div class="grid2 start">'
              + code('''
int slaHours = switch (tier) {
    case PREMIUM  -> 2;
    case STANDARD -> 24;
    default       -> 72;
};

Money fee = switch (slot.type()) {
    case EXPRESS  -> Money.rupees("99");
    case STANDARD -> {
        Money base = Money.rupees("40");
        yield bigCart ? Money.ZERO : base;
    }
    case SCHEDULED -> Money.ZERO;
};''', title="SwitchExpression.java", size=24)
              + '<div>' + bullets(["**No fall-through** — one branch runs",
                                   "An **expression** — can initialise a `final`",
                                   "**Exhaustive** on enums and sealed types",
                                   "`yield` for multi-statement branches"], start_step=0, cls="bullets sm")
              + frag('<p class="callout" style="margin-top:20px">Adding <code>default</code> to an enum or sealed switch <b>turns off</b> the exhaustiveness check.</p>', 4)
              + "</div></div>",
         narration=[
             "Switch expressions are a different construct, not just nicer syntax. The arrow form never falls through, so there's no forgotten break.",
             "It's an expression, so it can initialise a final variable. The old statement form can't, because the compiler can't prove the variable gets assigned.",
             "On enums and sealed types, it's checked for exhaustiveness. A missing case is a compile error.",
             "And when a branch needs several statements, use a block with yield to produce the value.",
             "One warning. Adding a default branch to an enum or sealed switch switches off the exhaustiveness check. A new constant silently falls into default. "
             "If you want the compiler's help, leave default out.",
         ]),

    dict(title="Text blocks",
         kicker="Java 15",
         body=code('''
private static final String FIND_RECENT = """
    select o.id, o.customer_id, o.placed_at, o.total_paise
    from orders o
    where o.customer_id = ?
      and o.placed_at >= ?
    order by o.placed_at desc
    """;''', title="TextBlocks.java", size=27)
              + bullets(["Indentation stripped up to the **closing `\"\"\"`** — move it and the string changes",
                         "`\\` at line end joins lines; `\\s` keeps a trailing space",
                         "Literals, not templates — use `.formatted(...)` (Ch 15)"], start_step=1, cls="bullets sm"),
         narration=[
             "Text blocks end the quote-counting. A SQL query is just the SQL, between triple quotes. No plus signs, no backslash n.",
             "The common leading indentation is stripped automatically, measured against the closing delimiter. So moving that delimiter changes the string. "
             "Harmless for SQL, but not for anything whitespace-sensitive like YAML.",
             "A backslash at the end of a line joins it to the next, and backslash s keeps a trailing space that would otherwise be removed.",
             "And text blocks are literals, not templates. There's no interpolation. Use the formatted method. String templates were proposed, then withdrawn. That's chapter fifteen.",
         ]),

    dict(title="When a record is the wrong choice",
         kicker="Transparent carriers for immutable data",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("JPA entity", "Entities need identity, mutable state, a no-arg constructor and proxies. Records have none — use them for **projections and DTOs**.", "fuchsia", 0)
              + card("Identity matters", "Two \"equal\" connections aren't interchangeable. Value equality is wrong here.", "amber", 1)
              + card("15 components", "Positional construction becomes unreadable. Use a builder or split the type.", "cyan", 2)
              + "</div>",
         narration=[
             "Records aren't always right. Never use one as a JPA entity. Entities have identity, mutable state, and lifecycle, and need a no-arg constructor and proxies. "
             "Records work great as JPA projections and API DTOs, just not as entities.",
             "Don't use one where identity matters more than value. Two connections to the same host aren't interchangeable.",
             "And don't let a record grow to fifteen components. Positional construction stops being readable. Use a builder, or split the type.",
         ]),

    dict(title="Internals",
         kicker="What the class file holds",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Record methods", "`equals`, `hashCode`, `toString` are `invokedynamic` sites built from the component list by `ObjectMethods`.", "indigo", 0)
              + card("PermittedSubclasses", "The JVM enforces `sealed` at class load — a **runtime** guarantee, not just a compiler hint.", "cyan", 1)
              + card("MatchException", "Exhaustive switches get a synthetic default that throws if the hierarchy changed **without recompiling** the switch.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Under the hood, a record's equals, hashCode and toString aren't ordinary generated bytecode. They're invokedynamic call sites, built from the component list at first use. "
             "So the class file stays small, and behaviour can't drift from the fields.",
             "Sealed types write a permitted subclasses attribute that the JVM enforces at class load time. It's a runtime guarantee, which is what lets the compiler treat exhaustiveness as sound.",
             "And an exhaustive switch still gets a hidden default that throws a MatchException. If someone adds a case and recompiles only the interface, your old switch fails loudly instead of returning null. "
             "That's also why libraries should be careful about sealing public API.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Records for DTOs, value objects, projections",
                         "Validate in the compact constructor",
                         "`List.copyOf` every collection component",
                         "Sealed interface of records for closed domains",
                         "Omit `default` from sealed and enum switches",
                         "Text blocks for SQL, JSON, XML"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["A record as a JPA entity",
                         "Assume a record is deeply immutable",
                         "`default` in a switch you want checked",
                         "`non-sealed` casually — it reopens the hierarchy",
                         "Records with a dozen-plus components",
                         "Trust text-block indentation through a reformat"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use records for DTOs, value objects and projections. Validate in the compact constructor, and copy every collection component. "
             "Model closed domains as a sealed interface of records. Leave default out of sealed and enum switches. And use text blocks for SQL, JSON and XML.",
             "Never use a record as a JPA entity, and never assume it's deeply immutable. Never add default to a switch you want checked. "
             "Don't use non-sealed casually, since it reopens the hierarchy. Keep records small. And don't trust text-block indentation to survive a reformat.",
         ]),

    dict(title="Java 14 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**14**", "Switch expressions; helpful NullPointerException messages"],
                    ["**15**", "Text blocks"],
                    ["**16**", "**Records**; `instanceof` patterns; local records"],
                    ["**17**", "**Sealed classes** — the last piece before pattern matching"],
                    ["**21–22**", "Pattern matching for `switch`, record patterns; `_` unnamed variables"],
                    ["**25**", "Flexible constructor bodies — statements before `super()`"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 14 made switch an expression, and gave us helpful NullPointerException messages.",
             "Java 15 finalised text blocks.",
             "Java 16 finalised records, along with instanceof patterns.",
             "Java 17 finalised sealed classes, the last piece before pattern matching.",
             "Java 21 and 22 delivered pattern matching for switch, record patterns, and the underscore for components you don't need.",
             "And Java 25 lets you run statements before calling super, so validation no longer needs static helper methods.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 12 · Java 14–17",
         body=bullets(["**Records**: transparent, value-based carriers — copy collection components",
                       "**Sealed** + records = closed, exhaustively checked domains",
                       "**Switch expressions**: no fall-through, exhaustive, `yield`",
                       "**Text blocks**: indentation follows the closing delimiter",
                       "Next: **Ch 13 · Pattern Matching**"], cls="bullets recap"),
         narration=[
             "To recap. Records are transparent carriers for immutable data, but remember to copy collection components. "
             "Sealed interfaces plus records give you closed domains the compiler checks exhaustively. Switch expressions have no fall-through and can yield values. "
             "And text blocks strip indentation according to the closing delimiter.",
             "Next is chapter thirteen, pattern matching, where all of this pays off. Thanks for watching.",
         ]),
]
