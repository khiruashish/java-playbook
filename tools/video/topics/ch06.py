"""Chapter 06 — Lambdas & Functional Interfaces. Source: docs/02-language/06-lambdas-functional-interfaces.md"""
from kit import code, frag, bullets, table, card, flow, md

CHAPTER = "Ch 06 · Lambdas & Functional Interfaces"
SECTION = "Java 8"

SLIDES = [
    dict(kind="title",
         title="Lambdas &amp; Functional Interfaces",
         kicker="Java 8 · Chapter 06",
         body='<p class="sub">How behaviour became a value in Java, what a lambda really compiles to, '
              'and how to compose behaviour instead of rewriting it.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter six: lambdas and functional interfaces.",
             "Java 8 added lambdas, and most codebases treated them as shorter anonymous classes. That undersells them. "
             "Lambdas made behaviour a value you can pass, store and compose. That's what streams, CompletableFuture, "
             "and the modern Map API are built on. Let's see how it works.",
         ]),

    dict(title="The problem: ceremony",
         kicker="Before Java 8",
         body=code('''
// Java 7 — six lines to express "by line total"
Collections.sort(lines, new Comparator<CartLine>() {
    @Override
    public int compare(CartLine a, CartLine b) {
        return a.lineTotal().compareTo(b.lineTotal());
    }
});''', title="SortingBefore.java")
              + code('''
// Java 8
lines.sort(Comparator.comparing(CartLine::lineTotal));''', title="SortingAfter.java", step=1)
              + frag('<p class="callout">Five of six lines were ceremony. Cheap syntax made passing behaviour normal.</p>', 2),
         narration=[
             "Our order engine needs to sort cart lines by price. Before Java 8, you wrote an anonymous Comparator class. "
             "That's six lines, and the only real instruction, compare by line total, is buried inside a type, a method, and two sets of braces.",
             "In Java 8 it's a single line. Comparator dot comparing, with a method reference to line total.",
             "That ratio matters. When passing behaviour was expensive, people wrote if-else chains instead. "
             "Once it became cheap, passing behaviour became the normal way to write Java.",
         ]),

    dict(title="Mental model: target typing",
         kicker="What a lambda is",
         body=flow(["`Comparator<CartLine> c = (a, b) -> ...`",
                    "Target type: `Comparator<CartLine>`",
                    "Single abstract method: `int compare(CartLine, CartLine)`",
                    "Compiler infers the parameter types"], step_start=0)
              + '<div class="grid2">'
              + card("A lambda has no type of its own",
                     "It takes its type from context: the variable, parameter or return it appears in.", "indigo", 4)
              + card("Functional interface = one abstract method",
                     "Default and static methods don't count. That's how `Comparator` has 20 helpers and is still a lambda target.", "fuchsia", 5)
              + "</div>",
         narration=[
             "Here's the mental model. A lambda is an instance of a functional interface, created from an expression instead of a class declaration.",
             "When you assign a lambda to a Comparator of CartLine, that's its target type.",
             "The compiler looks up that interface's single abstract method: compare, which takes two cart lines and returns an int.",
             "The lambda's parameters and return value have to match that signature, so the compiler can infer every type for you.",
             "Two consequences. First, a lambda has no type of its own. The same text can be a Comparator in one place and a BiFunction in another. This is called target typing.",
             "Second, a functional interface is simply any interface with exactly one abstract method. Default and static methods don't count. "
             "That's how Comparator carries around twenty helper methods and is still a valid lambda target.",
         ]),

    dict(title="Four shapes to memorise",
         kicker="java.util.function",
         body='<div class="grid4">'
              + card("Function<T,R>", "takes one, returns one\n`Sku → Money`", "indigo", 0)
              + card("Predicate<T>", "takes one, returns boolean\n`CartLine → in stock?`", "cyan", 1)
              + card("Consumer<T>", "takes one, returns nothing\n`Order → send email`", "fuchsia", 2)
              + card("Supplier<T>", "takes nothing, returns one\n`() → new OrderId`", "amber", 3)
              + "</div>"
              + bullets(["Two arguments → add **Bi**: `BiFunction`, `BiPredicate`, `BiConsumer`",
                         "Primitives → `IntPredicate`, `ToIntFunction`, `IntSupplier`… no boxing",
                         "Same in and out type → `UnaryOperator<T>`, `BinaryOperator<T>`"], start_step=4),
         narration=[
             "Java ships more than forty functional interfaces, but nearly all of them are variations on four shapes. "
             "Function takes one value and returns one, like turning a SKU into a price.",
             "Predicate takes one value and returns a boolean. Is this cart line in stock?",
             "Consumer takes one value and returns nothing. It's for side effects, like sending an order email.",
             "And Supplier takes nothing and returns a value, like generating a new order ID.",
             "Learn those four and the rest is mechanical. Add Bi for two arguments.",
             "Add Int, Long or Double for primitive versions that avoid boxing. These matter in hot loops and streams.",
             "And UnaryOperator and BinaryOperator are just the special cases where the input and output types are the same.",
         ]),

    dict(title="Syntax &amp; method references",
         kicker="Core API",
         body='<div class="grid2 start">'
              + frag(table(["Form", "Example"], [
                    ["No parameters", "`() -> OrderId.random()`"],
                    ["One parameter", "`line -> line.quantity() > 0`"],
                    ["Several", "`(a, b) -> a.plus(b)`"],
                    ["Explicit / var (11)", "`(var a, var b) -> ...`"],
                    ["Block body", "`line -> { ...; return q; }`"],
                ], cls="sm"), 0)
              + frag(table(["Method reference", "Equivalent lambda"], [
                    ["Static `Integer::parseInt`", "`s -> Integer.parseInt(s)`"],
                    ["Bound `catalogue::priceFor`", "`sku -> catalogue.priceFor(sku)`"],
                    ["Unbound `CartLine::lineTotal`", "`line -> line.lineTotal()`"],
                    ["Constructor `ArrayList::new`", "`() -> new ArrayList<>()`"],
                ], cls="sm"), 1)
              + "</div>"
              + frag('<p class="callout">Unbound reference: the receiver becomes the first parameter, so '
                     '<code>CartLine::lineTotal</code> fits <code>Function&lt;CartLine, Money&gt;</code>.</p>', 2),
         narration=[
             "The syntax has a few forms. Empty parentheses for no parameters, a bare name for one, parentheses for several. "
             "You can add explicit types, or since Java 11, var, which lets you annotate parameters. "
             "An expression body returns its value implicitly. A block body needs braces and an explicit return.",
             "When a lambda just calls an existing method, use a method reference instead. There are four kinds: "
             "static, bound to a particular instance, unbound, and constructor references.",
             "The unbound kind is the one that confuses people. CartLine colon colon line total takes the receiver as its first parameter, "
             "so it fits a Function from CartLine to Money.",
         ]),

    dict(title="Compose behaviour",
         kicker="Worked example · pricing rules",
         body=code('''
@FunctionalInterface
public interface PricingRule {
    Money apply(Money subtotal);

    default PricingRule andThen(PricingRule next) {
        return subtotal -> next.apply(this.apply(subtotal));
    }
}''', title="PricingRule.java", size=24)
              + code('''
PricingRule bulkDiscount = subtotal -> subtotal.minusPercent(10);
PricingRule deliveryFee  = subtotal -> subtotal.plus(Money.rupees(40));
PricingRule festiveOffer = subtotal -> subtotal.minus(Money.rupees(100));

PricingRule checkout = bulkDiscount.andThen(deliveryFee).andThen(festiveOffer);
checkout.apply(Money.rupees(1000));   // ₹840.00''', title="PricingRules.java", step=1, size=24)
              + frag('<div class="pipeline"><span>₹1000</span>→<span>₹900</span>→<span>₹940</span>→<span class="hl">₹840</span></div>', 2),
         narration=[
             "Here's where it gets powerful. A pricing rule is our own functional interface. One abstract method, apply, which takes a subtotal and returns money. "
             "Its default andThen method returns a new lambda that runs this rule, then the next one. "
             "Mark it at FunctionalInterface, so the compiler rejects anyone who adds a second abstract method.",
             "Now each business rule is a one-line lambda: a ten percent bulk discount, a forty rupee delivery fee, and a hundred rupees off for the festive offer. "
             "Chain them with andThen into one checkout rule.",
             "Apply it to a thousand rupees. The discount takes it to nine hundred, delivery adds forty, and the offer brings it to eight hundred and forty. "
             "The built-in interfaces work the same way: Function has andThen and compose, Predicate has and, or and negate, and Comparator has thenComparing.",
         ]),

    dict(title="Predicates, comparators, laziness",
         kicker="Worked examples",
         body=code('''
Predicate<CartLine> needsColdChain = inStock.and(perishable);
Predicate<CartLine> backordered    = inStock.negate();''', title="CartFilters.java", size=28)
              + code('''
lines.sort(Comparator.comparing(CartLine::vendorName)
                     .thenComparing(CartLine::productName)
                     .thenComparing(CartLine::lineTotal, Comparator.reverseOrder()));
lines.sort(Comparator.comparingInt(CartLine::quantity));   // no boxing''', title="Sorting.java", step=1, size=28)
              + code('''
vendorNames.getOrDefault(sku, expensiveLookup(sku));       // eager: always runs
vendorNames.computeIfAbsent(sku, this::expensiveLookup);   // lazy: runs on a miss''', title="Laziness.java", step=2, size=28),
         narration=[
             "Predicates compose too. Name each condition, in stock, perishable, then combine them. Needs cold chain is in stock and perishable. "
             "Each one is named, testable on its own, and reusable. An inline boolean expression is none of those.",
             "Comparators lose all their ceremony. Sort by vendor, then by product name, then by price descending. "
             "When the key is a number, use comparingInt, comparingLong or comparingDouble, so you don't box every key on every comparison.",
             "And a Supplier, or any function argument, gives you laziness. getOrDefault evaluates the expensive lookup every time, even on a hit. "
             "computeIfAbsent only runs it on a miss. Optional's orElseGet versus orElse is the same idea.",
         ]),

    dict(title="Two sharp edges",
         kicker="Capture &amp; checked exceptions",
         body='<div class="grid2 start">'
              + frag(code('''
int discountPercent = 10;
PricingRule rule =
    s -> s.minusPercent(discountPercent);  // fine

discountPercent = 20;  // COMPILE ERROR:
                       // must be effectively final

int[] count = {0};
lines.forEach(l -> count[0]++);  // compiles,
                                 // bad idea''', title="Capture.java", size=26), 0)
              + frag(code('''
// Does not compile
Function<Path, String> read =
    path -> Files.readString(path);

// Often the right answer:
for (Path path : paths) {
    contents.add(Files.readString(path));
}''', title="CheckedException.java", size=26), 2)
              + "</div>",
         narration=[
             "Two sharp edges. First, capture. A lambda captures the value of a local variable, not the variable itself. "
             "So the variable must be effectively final, and reassigning it is a compile error. Fields don't have this restriction.",
             "The classic workaround is a one-element array you mutate from inside the lambda. It compiles, but it isn't thread-safe, "
             "and it's a sign you really wanted a loop or a reduce.",
             "Second, checked exceptions. None of the standard functional interfaces declare them, so a lambda calling Files dot readString won't compile. "
             "You can catch and rethrow as unchecked, or write your own throwing interface. But often the honest answer is to keep it a plain loop.",
         ]),

    dict(title="Internals: not an anonymous class",
         kicker="What javac and the JVM do",
         body=flow(["Body → private method `lambda$confirm$0`",
                    "Call site → `invokedynamic`",
                    "First call → `LambdaMetafactory` spins a class",
                    "CallSite linked for good"], step_start=0)
              + bullets(["**No class file per lambda** — 200 lambdas, one `.class`",
                         "**Non-capturing lambdas are singletons**; capturing ones allocate",
                         "**`this` is the enclosing instance** — lambdas are lexically scoped",
                         "Stack traces show `lambda$confirm$2` — extract real logic to a named method"], start_step=4),
         narration=[
             "Under the hood, a lambda is not an anonymous class. javac compiles the lambda body into a private method with a synthetic name.",
             "The call site becomes an invokedynamic instruction.",
             "The first time it runs, the JVM calls the lambda metafactory, which spins up an implementation class at runtime.",
             "Then the call site is linked permanently, so later calls jump straight there. Because the strategy is decided at runtime, lambda performance has improved across JDK versions without recompiling.",
             "Practical consequences. There's no class file per lambda, so jars stay small and class loading stays fast.",
             "A lambda that captures nothing is a singleton. One that captures a variable allocates a new instance each time it's evaluated.",
             "Inside a lambda, this means the enclosing instance, not the lambda. Remember that when converting anonymous classes, because it can silently change behaviour.",
             "And lambdas appear in stack traces with positional names. If a lambda has real logic you'll need to debug, extract it into a named method and use a method reference.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Annotate your interfaces `@FunctionalInterface`",
                         "Prefer method references when a lambda just delegates",
                         "Name non-trivial predicates and functions",
                         "Use `comparingInt`, `ToIntFunction`, `IntPredicate` for numbers",
                         "Compose: `a.andThen(b).andThen(c)`",
                         "Extract lambdas longer than ~3 lines"], cls="bullets sm")
              + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Mutate captured state via arrays or holders",
                         "Side effects inside `map` or `computeIfAbsent`",
                         "try/catch wrapped around every lambda",
                         "Overload on different functional interfaces of the same arity",
                         "Rely on lambda identity (`==`, map keys, listeners)"], cls="bullets sm bad")
              + "</div></div>",
         narration=[
             "Let's turn that into production rules. Do: annotate your own interfaces with at FunctionalInterface. Prefer method references when a lambda just delegates. "
             "Name non-trivial predicates. Use the primitive specialisations for numbers. Compose rather than nest. And extract any lambda longer than about three lines into a named method.",
             "Never: mutate captured state through arrays or holder objects. Never put side effects in a function that's expected to be pure, like one passed to map or computeIfAbsent. That's a race waiting for a parallel stream. "
             "Don't wrap every lambda in try catch. Don't overload a method on two functional interfaces with the same number of parameters, because callers hit ambiguity errors. "
             "And never rely on lambda identity. Comparing two lambdas with double equals is unspecified, which also makes them bad map keys or listeners you plan to remove.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "Lambdas, method references, `java.util.function`, default & static interface methods"],
                    ["**9**", "Private interface methods"],
                    ["**10–11**", "`var` locals; `var` lambda parameters; `Predicate.not`"],
                    ["**16–17**", "Records; sealed interfaces are still valid lambda targets"],
                    ["**21**", "Pattern matching for `switch` replaces some `Map<Type, Function>` dispatch"],
                    ["**26**", "No change to the lambda model"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 introduced the whole model: lambdas, method references, the java util function package, and default and static interface methods.",
             "Java 9 added private interface methods, so default methods can share code without exposing it.",
             "Java 10 and 11 brought var, including in lambda parameters, plus Predicate dot not, which reads better than negate with a method reference.",
             "Records and sealed interfaces in 16 and 17 fit the model well. A sealed interface with one abstract method is still a lambda target.",
             "Java 21's pattern matching for switch replaces some old dispatch tables built from maps of functions.",
             "And as of Java 26, the lambda model itself is unchanged.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 06 · Lambdas &amp; Functional Interfaces",
         body=bullets(["A lambda is an instance of a **functional interface**, typed by its target",
                       "Learn four shapes: **Function, Predicate, Consumer, Supplier**",
                       "**Compose** behaviour with `andThen`, `and`, `thenComparing`",
                       "Compiled via **invokedynamic**, not anonymous classes",
                       "Next: **Ch 07 · The Stream API**"], cls="bullets recap"),
         narration=[
             "To recap. A lambda is an instance of a functional interface, and it takes its type from its target. "
             "Learn the four shapes: function, predicate, consumer, and supplier. Compose behaviour instead of nesting it. "
             "And under the hood, lambdas use invokedynamic, not anonymous classes.",
             "The full chapter, with interview questions from foundation to architect level, is in the handbook. "
             "Next up is chapter seven, the Stream API. Thanks for watching.",
         ]),
]
