"""Chapter 14 — Java 21–26 Language Features. Source: docs/02-language/14-java-21-to-26.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 14 · Java 21–26 Language Features"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="Java 21–26 Language Features",
         kicker="Language · Chapter 14",
         body='<p class="sub">The smaller changes in the LTS releases you\'ll run this decade — which to adopt everywhere, '
              'and which belong only in scripts.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter fourteen: the language features of Java 21 to 26.",
             "Java 21 and 25 are the long-term releases most teams will run for the rest of the decade. Virtual threads and pattern matching have their own chapters. "
             "This one covers the smaller changes that remove long-standing papercuts, and one big shift in what a Java source file can look like.",
         ]),

    dict(title="Two motivations",
         kicker="Mental model",
         body='<div class="grid2 start">'
              + frag('<div><div class="col-h ok">Remove ceremony — adopt everywhere</div>'
                     + bullets(["Unnamed variables _ (underscore) (22)",
                                "Markdown doc comments `///` (23)",
                                "Flexible constructor bodies (25)"], cls="bullets") + "</div>", 0)
              + frag('<div><div class="col-h bad">Lower the on-ramp — scripts &amp; learning</div>'
                     + bullets(["Compact source files, instance `main` (25)",
                                "Module import declarations (25)"], cls="bullets bad") + "</div>", 1)
              + "</div>",
         narration=[
             "Two different motivations run through these features. Some remove ceremony: unnamed variables, Markdown doc comments, and flexible constructor bodies. "
             "Those apply everywhere and should become normal practice.",
             "Others lower the on-ramp for learners and scripts: compact source files and module imports. They're useful there, but mostly wrong in a large codebase. Let's see why.",
         ]),

    dict(title="Unnamed variables: _",
         kicker="Final in Java 22",
         body=code('''
// Before — three bindings named and never used
case DispatchFailed(var occurredAt, var orderId, var reason, var retryable) -> alerting.raise(reason);

// After — the shape is still checked; the intent is explicit
case DispatchFailed(_, _, var reason, _) -> alerting.raise(reason);''', title="UnnamedPatterns.java", size=24)
              + code('''
catch (NumberFormatException _) { return defaultValue; }      // the type is the information
try (var _ = tenantContext.bind(tenant)) { process(order); }  // acquired for its side effect
map.forEach((_, item) -> audit.record(item));                 // only the value matters''',
                     title="UnnamedElsewhere.java", step=1, size=24),
         narration=[
             "Unnamed variables, final in Java 22. In a record pattern, every component used to need a name, even ones you never use. Now an underscore says, I don't need this part. "
             "The pattern still checks the component count, so it's not ignoring the shape.",
             "It works elsewhere too. A catch where only the exception type matters. A resource acquired for its side effect. A lambda that only uses its second parameter. "
             "The old convention of naming things ignored was invisible to tooling. Underscore tells the compiler.",
         ]),

    dict(title="Flexible constructor bodies",
         kicker="Final in Java 25",
         body=code('''
public DiscountedMoney(Money original, int percent) {
    Objects.requireNonNull(original, "original");           // prologue — now legal
    if (percent < 0 || percent > 100)
        throw new IllegalArgumentException("percent out of range: " + percent);

    super(original.amount().multiply(BigDecimal.valueOf(100 - percent))
                           .divide(BigDecimal.valueOf(100)));
    this.original = original;                                // epilogue
}''', title="Validation.java", size=25)
              + frag(table(["Before super()", ""], [
                    ["Validate arguments; compute values for `super()`", "✓"],
                    ["Assign this class's own fields", "✓"],
                    ["Read fields, call instance methods, use `this`", "✗"],
                ], cls="sm"), 1),
         narration=[
             "Flexible constructor bodies, final in Java 25. Until now, nothing could come before the call to super. "
             "So validating an argument meant a private static helper, called inside the super arguments, purely to satisfy the rule. Now you just validate first, then call super.",
             "There are limits, and they're why the rule existed. A superclass constructor can call an overridden method before the subclass is ready. "
             "So the prologue can validate, compute values, and assign the class's own fields, but it can't read fields, call instance methods, or use this.",
         ]),

    dict(title="Markdown doc comments",
         kicker="Final in Java 23",
         body=code('''
/// Reserves stock for every line in the cart.
///
/// Reservation is all-or-nothing: if any line cannot be satisfied, nothing is reserved.
///
/// | Outcome | Meaning                 |
/// |---------|-------------------------|
/// | `true`  | every line reserved     |
/// | `false` | at least one line short |
///
/// @param lines the cart lines to reserve
public boolean reserveAll(List<CartLine> lines) { ... }''', title="MarkdownDoc.java", size=26)
              + frag('<p class="callout">No more <code>&lt;p&gt;</code>, <code>&lt;pre&gt;</code> and <code>&lt;table&gt;</code>. '
                     '<code>///</code> and <code>/** */</code> coexist — convert as you touch files.</p>', 1),
         narration=[
             "Markdown doc comments, final in Java 23. Triple-slash comments use Markdown instead of HTML: paragraphs, code fences, even tables. Javadoc tags like at param still work.",
             "Compare that with the old HTML tags, which is why most Java documentation is one unformatted paragraph. "
             "The two styles coexist, so convert files as you touch them. It's not worth a dedicated pass.",
         ]),

    dict(title="Compact source files",
         kicker="Final in Java 25 · for scripts",
         body=code('''
void main() {
    var orders = loadOrders(Path.of("orders.csv"));
    var total  = orders.stream().map(Order::total).reduce(Money.ZERO, Money::plus);
    IO.println("Reconciled " + orders.size() + " orders, total " + total);
}

List<Order> loadOrders(Path path) throws IOException {
    return Files.readAllLines(path).stream().skip(1).map(Order::parse).toList();
}''', title="Reconcile.java  →  java Reconcile.java", size=26)
              + '<div class="grid2">'
              + card("Great for", "Operational scripts: a reconciliation check, a data fix, a one-off migration. A **replacement for Bash**.", "indigo", 1)
              + card("Not for application code", "It lives in the **unnamed package** — nothing can import it, and the first test forces a rewrite.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Compact source files, final in Java 25. No class declaration, and main doesn't need to be static, public, or take arguments. "
             "java dot base is imported automatically, and IO dot println replaces System dot out. Run it directly with java Reconcile dot java.",
             "That's genuinely useful for operational scripts, like a reconciliation check or a one-off data fix, where you'd otherwise write a shell script. It's ordinary Java, with types and your IDE.",
             "But it's not for application code. Everything lives in the unnamed package, so nothing else can import it, and as soon as it needs a test it becomes a normal class anyway.",
         ]),

    dict(title="Module import declarations",
         kicker="Final in Java 25 · use with care",
         body=code('''
import module java.base;      // every package java.base exports
import module java.sql;

Date d = ...;                 // ✗ ambiguous: java.util.Date or java.sql.Date?

import java.sql.Date;         // ✓ a single-type import wins''', title="ModuleImport.java", size=27)
              + frag('<p class="callout">Ambiguity appears <b>at the point of use</b> — so a future JDK adding a class can break code that compiled yesterday. '
                     'Keep explicit imports in long-lived code.</p>', 1),
         narration=[
             "Module import declarations, also final in Java 25. One line imports every package a module exports. "
             "The risk is ambiguity. Import java dot base and java dot sql, and the simple name Date is ambiguous. A single-type import resolves it, because it takes precedence.",
             "Here's the catch. That ambiguity only shows up where the name is used. So a future JDK that adds a class to an exported package can break code that compiled yesterday. "
             "In a long-lived codebase, keep explicit imports. Tooling maintains them, and they document your dependencies.",
         ]),

    dict(title="Internals",
         kicker="Why the rules are shaped this way",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("_ took 15 years", "Java 9 made _ (underscore) alone a compile error to reserve it. That's why Java 22's meaning is source-compatible.", "indigo", 0)
              + card("A language rule", "The JVM always allowed code before `super()`. Java 25 relaxed the **language** rule, keeping the safety property.", "cyan", 1)
              + card("Implicit class", "A compact source file becomes a final class in the unnamed package; the launcher instantiates it and calls `main()`.", "fuchsia", 2)
              + "</div>",
         narration=[
             "A few internals. The underscore change took fifteen years. Java 9 made a lone underscore a compile error, to reserve it. "
             "So by the time Java 22 gave it a meaning, no working code could be using it as a name.",
             "The rule about super was always a language rule, not a JVM rule. Bytecode could always run before super. Java 25 relaxed the language rule while keeping the safety it was there for.",
             "And a compact source file compiles to a real, final class in the unnamed package. The launcher creates an instance and calls main on it, which is why instance fields and methods just work.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["_ (underscore) for unused components, catches, resources",
                         "Validate in the constructor prologue",
                         "Markdown javadoc for new and touched docs",
                         "Compact source files for operational scripts",
                         "Explicit imports in application code"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Compact source files for application code",
                         "Module imports in a long-lived codebase",
                         "Assume the prologue makes constructors safe",
                         "_ (underscore) where a name would inform the reader",
                         "Primitive type patterns in production — still preview"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use underscore for unused components, catch parameters and resources. Validate in the constructor prologue instead of static helpers. "
             "Write Markdown javadoc for new and touched docs. Use compact source files for operational scripts. And keep explicit imports in application code.",
             "Never use compact source files for application code, or module imports in a long-lived codebase. Don't assume the prologue makes constructors safe, since calling overridable methods from a constructor is still a design error. "
             "Don't use underscore where a name would help the reader. And don't use primitive type patterns in production yet. They're still preview.",
         ]),

    dict(title="Java 21 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**21 LTS**", "Virtual threads, pattern matching for `switch`, record patterns, sequenced collections"],
                    ["**22**", "Unnamed variables and patterns"],
                    ["**23**", "Markdown doc comments; String Templates dropped (Ch 15)"],
                    ["**25 LTS**", "Flexible constructors, module imports, compact source files, `ScopedValue`"],
                    ["**26**", "Structured concurrency, primitive patterns, lazy constants — **preview**"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 21, a long-term release, brought virtual threads, pattern matching for switch, record patterns and sequenced collections.",
             "Java 22 finalised unnamed variables.",
             "Java 23 finalised Markdown doc comments, and dropped string templates. That's the next chapter.",
             "Java 25, the current long-term release, brought flexible constructors, module imports, compact source files, and scoped values.",
             "And Java 26 continues previews of structured concurrency, primitive patterns and lazy constants. Preview features need enable-preview, so check their status against your JDK.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 14 · Java 21–26",
         body=bullets(["_ (underscore) says \"not needed\" — to the compiler, not just the reader",
                       "Validate **before** `super()`; still no `this` in the prologue",
                       "`///` Markdown javadoc as you touch files",
                       "Compact source files replace scripts, not classes",
                       "Module imports: fine in scripts, risky in long-lived code",
                       "Next: **Ch 15 · String Templates: A Post-Mortem**"], cls="bullets recap"),
         narration=[
             "To recap. Underscore tells the compiler a binding isn't needed. Constructors can now validate before calling super, but still can't touch this. "
             "Adopt Markdown javadoc as you go. Compact source files replace scripts, not classes. And module imports are fine in scripts but risky in long-lived code.",
             "Next is chapter fifteen, a post-mortem on string templates: the feature that was previewed, then withdrawn. Thanks for watching.",
         ]),
]
