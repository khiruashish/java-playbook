"""Chapter 16 — Generics in Depth. Source: docs/02-language/16-generics.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 16 · Generics in Depth"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="Generics in Depth",
         kicker="Language · Chapter 16",
         body='<p class="sub">Erasure, invariance and PECS — the model underneath, and why every restriction follows from one decision.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter sixteen: generics in depth.",
             "Most developers use generics fluently for years without learning the model underneath. That's fine until you write an API. "
             "Then the questions arrive all at once. Why isn't a list of strings a list of objects? Why is new T array illegal? And what is capture?",
         ]),

    dict(title="The error moved to the mistake",
         kicker="The problem",
         body='<div class="grid2 start">'
              + code('''
// Java 1.4
List orders = new ArrayList();
orders.add(new Order(...));
orders.add("oops");          // compiles

Order a = (Order) orders.get(0);
Order b = (Order) orders.get(1);
// ClassCastException — far from the add''', title="PreGenerics.java", size=24)
              + frag(code('''
List<Order> orders = new ArrayList<>();
orders.add("oops");   // compile error, at the mistake
Order a = orders.get(0);   // no cast''', title="WithGenerics.java", size=24)
                     + '<p class="callout" style="margin-top:20px">The constraint: <b>binary compatibility</b> with pre-generics code. '
                       'That produced erasure — and erasure produced every restriction.</p>', 1)
              + "</div>",
         narration=[
             "Before generics, every collection was a bag of Object. You cast on every read, and when someone added the wrong type, "
             "the ClassCastException surfaced at the get, possibly in a different class, far from the real mistake.",
             "Generics moved the check to compile time, right at the mistake, and removed the casts. "
             "But Java 5 had to stay binary compatible with existing libraries and VMs. That constraint produced erasure, and erasure produced every restriction in this chapter.",
         ]),

    dict(title="Erasure",
         kicker="Mental model",
         body=flow(["`List<Order> orders`", "Compiler checks every use", "Erase: `List<Order>` → `List`, `T` → `Object`",
                    "Insert casts at read sites"], step_start=0)
              + frag(table(["Illegal", "Because"], [
                    ["`new T()` · `new T[10]`", "No type exists at runtime"],
                    ["`x instanceof List<String>`", "Erased — nothing to test"],
                    ["`static T field`", "One class shared by every instantiation"],
                    ["`f(List<String>)` + `f(List<Order>)`", "Same erasure, same signature"],
                ], cls="sm"), 4),
         narration=[
             "Here's erasure. You write a List of Order.",
             "The compiler checks every use of it.",
             "Then it throws the type arguments away. List of Order becomes plain List, and T becomes Object, or its bound.",
             "And it inserts casts wherever you read a value. So at runtime, a list of strings and a list of orders are the same class.",
             "Every restriction follows. You can't write new T, or a new T array, because there's no type at runtime. You can't test instanceof a List of String. "
             "A static field can't be of type T, because one class is shared by every instantiation. And two overloads that differ only in type arguments clash.",
         ]),

    dict(title="Invariance — and why it's safe",
         kicker="Mental model",
         body=code('''
List<Order>  orders  = new ArrayList<>();
List<Object> objects = orders;      // if this compiled...
objects.add("a string");             // ...this would poison the list
Order o = orders.get(0);             // ClassCastException''', title="WhyInvariant.java", size=28)
              + frag('<p class="callout">A <code>List&lt;Order&gt;</code> is <b>not</b> a <code>List&lt;Object&gt;</code>. '
                     'Invariance makes generics safe. <b>Wildcards</b> give back flexibility without losing that safety.</p>', 1),
         narration=[
             "Generics are invariant. A List of Order is not a List of Object, even though Order is an Object. "
             "Here's why. If you could assign it, you could add a string through the object view, and poison the list of orders.",
             "So invariance is what makes generics safe. And wildcards are how you get flexibility back without giving up that safety.",
         ]),

    dict(title="PECS: Producer Extends, Consumer Super",
         kicker="Choosing a wildcard",
         body='<div class="grid2">'
              + card("Producer — you READ from it", "`? extends T`\nYou can get. You can't add.", "indigo", 0)
              + card("Consumer — you WRITE to it", "`? super T`\nYou can add. `get` returns `Object`.", "fuchsia", 0)
              + "</div>"
              + code('''
static Money sum(Collection<? extends CartLine> lines) { ... }            // reads
static void collectSkus(Cart cart, Collection<? super Sku> dest) { ... }  // writes

Money total = CartTotals.sum(perishableLines);     // List<PerishableLine> — works
CartTotals.collectSkus(cart, auditList);           // List<Object> — works''', title="PecsExample.java", step=1, size=25)
              + frag('<p class="callout">Both? Use <code>T</code> exactly. The JDK does this everywhere: '
                     '<code>Collections.copy(List&lt;? super T&gt; dest, List&lt;? extends T&gt; src)</code>.</p>', 2),
         narration=[
             "The rule for wildcards is PECS: producer extends, consumer super. A parameter you read from is a producer, so give it question mark extends T. "
             "A parameter you write to is a consumer, so give it question mark super T.",
             "The payoff is at the call site. Sum reads cart lines, so it accepts a list of any CartLine subtype. collectSkus writes SKUs, so it accepts a list of Object as its destination. "
             "Without the wildcards, both calls fail.",
             "If you both read and write, use T exactly. The JDK follows this everywhere. Collections dot copy uses both wildcards in a single signature.",
         ]),

    dict(title="PECS on functions",
         kicker="Worked example",
         body=code('''
public sealed interface Result<T> permits Success, Failure {
    default <R> Result<R> map(Function<? super T, ? extends R> mapper) {
        return switch (this) {
            case Success<T>(var value)  -> Result.success(mapper.apply(value));
            case Failure<T>(var reason) -> Result.failure(reason);
        };
    }
}''', title="Result.java", size=26)
              + frag('<p class="callout">The function <b>consumes</b> <code>T</code> → <code>? super T</code>. It <b>produces</b> '
                     '<code>R</code> → <code>? extends R</code>. That\'s how every <code>map</code> in the JDK is declared.</p>', 1),
         narration=[
             "PECS applies to functional parameters too. Here's a generic Result type: a sealed interface with success and failure records, and a map method.",
             "Look at map's parameter: a Function of question mark super T, question mark extends R. The function consumes a T, so super. It produces an R, so extends. "
             "That way a function from Object to String is a perfectly good mapper for a Result of Order. Every map in the JDK is declared like this.",
         ]),

    dict(title="Arrays and generics don't mix",
         kicker="Covariant vs invariant",
         body=code('''
Object[] objects = new Order[10];
objects[0] = "a string";                  // compiles — ArrayStoreException at runtime

T[] items = new T[10];                    // ✗ compile error
@SuppressWarnings("unchecked")
T[] items = (T[]) new Object[10];         // what ArrayList does — keep it private
List<T> items = new ArrayList<>();        // ✓ preferred''', title="GenericArray.java", size=26)
              + frag(code('''
@SafeVarargs static <T> T[] unsafe(T... items) { return items; }   // ✗ a lie — the array escapes
String[] s = unsafe("a", "b");                                     // ClassCastException''',
                          title="HeapPollution.java", size=24), 1),
         narration=[
             "Arrays and generics disagree. Arrays are covariant, so an Order array can be viewed as an Object array, and storing a string compiles, then throws at runtime. "
             "Generics chose compile-time safety instead. So new T array is illegal. The workaround is casting an Object array, which is what ArrayList does internally, "
             "but only in a private field, never returned. Usually, just use a List.",
             "Varargs of T create exactly such an array, which is why the compiler warns about heap pollution. SafeVarargs suppresses it, but it's a promise. "
             "If the array escapes, like returning it here, the caller gets a ClassCastException.",
         ]),

    dict(title="Type tokens",
         kicker="When a method needs its own T",
         body=code('''
public <T> T readConfig(Path path, Class<T> type) throws IOException {
    return mapper.readValue(Files.readString(path), type);
}''', title="TypeToken.java", size=26)
              + code('''
public abstract class TypeRef<T> {
    private final Type type;
    protected TypeRef() {
        type = ((ParameterizedType) getClass().getGenericSuperclass()).getActualTypeArguments()[0];
    }
}
var ref = new TypeRef<List<Order>>() { };   // anonymous subclass captures List<Order>''',
                     title="SuperTypeToken.java", step=1, size=24),
         narration=[
             "Because of erasure, a method can't know its own T unless you pass it. A Class of T works for simple types, like reading a Config.",
             "But List dot class loses its type argument. So libraries use a super type token. Generic information about a superclass is kept in the class file. "
             "Create an anonymous subclass, note the braces, and reflection can read List of Order back. That's exactly how Jackson's TypeReference works.",
         ]),

    dict(title="Internals",
         kicker="Signature · bridges · capture",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Signature attribute", "Declarations keep their generic types — `getGenericReturnType()` sees `List<Order>`. Instances don't.", "indigo", 0)
              + card("Bridge methods", "`compare(Object, Object)` is generated to call `compare(Order, Order)` — how polymorphism survives erasure.", "cyan", 1)
              + card("capture#1 of ?", "Each wildcard gets a fresh name, so a read and a write can't be unified. **Fix:** delegate to a generic helper method.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Three internals. Erasure removes type arguments from bytecode, but declarations keep a Signature attribute. "
             "So reflection can see that a method returns a List of Order. An instance's type arguments, though, genuinely don't exist.",
             "Bridge methods. A Comparator of Order erases to compare of two Objects. So the compiler generates a bridge that casts and calls your real method. "
             "That's how polymorphism survives erasure, and why stack traces sometimes show methods you never wrote.",
             "And capture. The compiler names each wildcard occurrence separately, so it can't prove that what you read and what you write are the same type. "
             "The fix is always to delegate to a generic helper method, which names the type once.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["PECS on every parameter",
                         "Wildcards in parameters, concrete types in returns",
                         "Bound `T` only when the bound does work",
                         "`List<T>` over `T[]`",
                         "Comment every `@SuppressWarnings(\"unchecked\")`",
                         "Turn on `-Xlint:rawtypes,unchecked`"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Raw types — they disable checking for the whole expression",
                         "Return a `T[]` built from `Object[]`",
                         "Overload on erasure-identical signatures",
                         "Wildcards in field types",
                         "Mix arrays and generics in an API",
                         "`@SafeVarargs` when the array escapes"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Apply PECS to every parameter. Use wildcards in parameters, but concrete types in return values, so callers don't inherit capture problems. "
             "Only bound T when the bound does real work. Prefer lists over generic arrays. Comment every unchecked suppression. And turn on the raw types and unchecked lint warnings.",
             "Never use raw types. They switch off generic checking for the whole expression. Never return a T array built from an Object array. "
             "Never overload on signatures that erase to the same thing. Don't put wildcards in field types, or mix arrays and generics in an API. And never use SafeVarargs when the array escapes.",
         ]),

    dict(title="Java 5 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**5**", "Generics, erasure, wildcards, bridge methods"],
                    ["**7–9**", "Diamond operator; diamond on anonymous classes"],
                    ["**10**", "`var` — never with a bare diamond"],
                    ["**16–21**", "Generic records, sealed types, record patterns with inference"],
                    ["**26**", "No change; Valhalla's specialised generics remain future work"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 5 introduced the whole model: generics, erasure, wildcards and bridge methods.",
             "Java 7 added the diamond operator, and Java 9 allowed it on anonymous classes.",
             "Java 10's var works with generics, but never with a bare diamond, which infers Object.",
             "Records, sealed types and record patterns all work with generics, as the Result example showed.",
             "And Project Valhalla is working on value types and specialised generics, which would allow a List of int without boxing. It isn't delivered, and any timeline is speculation.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 16 · Generics in Depth",
         body=bullets(["**Erasure**: types checked, then discarded — the source of every restriction",
                       "**Invariance** keeps generics safe; wildcards add flexibility",
                       "**PECS**: read → `? extends T`, write → `? super T`, both → `T`",
                       "Arrays are covariant and unsound — prefer `List<T>`",
                       "Next: **Collections · Ch 17 · Choosing the Right Collection**"], cls="bullets recap"),
         narration=[
             "To recap. Erasure means types are checked at compile time, then discarded, and that one decision explains every restriction. "
             "Invariance keeps generics safe, and wildcards add flexibility back. Remember PECS: read with extends, write with super, and use T when you do both. "
             "And arrays are covariant and unsound, so prefer lists.",
             "That completes the Language section. Next is the Collections section, starting with chapter seventeen: choosing the right collection. Thanks for watching.",
         ]),
]
