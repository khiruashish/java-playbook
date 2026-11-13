"""Chapter 11 — Java 9–11: Modules, var, HttpClient. Source: docs/02-language/11-java-9-to-11.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 11 · Java 9–11: Modules, var, HttpClient"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="Java 9–11: Modules, var, HttpClient",
         kicker="Language · Chapter 11",
         body='<p class="sub">What the module system changed even if you never opted in, where <code>var</code> helps '
              'and hurts, and what in 9–11 you should be using.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter eleven: Java 9 to 11.",
             "Most teams skipped straight through this range to Java 11, the long-term release everyone ran. "
             "So its features are widely used and rarely understood. Let's fix that.",
         ]),

    dict(title="Three old pains",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("No encapsulation", "Anything `public` was reachable — including JDK internals like `sun.misc.Unsafe`. Every upgrade broke something.", "fuchsia", 0)
              + card("Whole JRE, every time", "A service needing `java.base` and `java.sql` still shipped CORBA, Swing and applets — **200 MB** for what needed 40.", "amber", 1)
              + card("HTTP needed a library", "`HttpURLConnection` or a dependency. No HTTP/2, no async.", "cyan", 2)
              + "</div>",
         narration=[
             "Java 9 to 11 fixed three unrelated pains. First, the classpath had no encapsulation. Anything public was reachable, including JDK internals never meant for you. "
             "Libraries built on them, so every JDK upgrade broke something.",
             "Second, every deployment shipped the whole runtime. Over two hundred megabytes for a service that needed forty.",
             "And third, HTTP meant the clunky HttpURLConnection or an extra library, with no HTTP/2 and no async.",
         ]),

    dict(title="Modules: public is no longer enough",
         kicker="Mental model",
         body=code('''
module com.grocery.orders {
    requires com.grocery.inventory;     // readability
    exports  com.grocery.orders.api;    // accessibility
}''', title="module-info.java", size=30)
              + '<div class="grid2">'
              + card("Readability", "Module A can use B only if A **requires** B.", "indigo", 1)
              + card("Accessibility", "A public type in B is visible only if B **exports** its package.", "cyan", 1)
              + "</div>"
              + frag('<p class="callout">You can\'t opt out: <b>the JDK itself is modularised</b>. Most apps still run on the classpath — '
                     'and still feel the consequences.</p>', 2),
         narration=[
             "A module declares what it needs and what it exposes, in a module-info file. Requires and exports.",
             "That gives two rules instead of one. Readability: A can use B only if A requires B. "
             "Accessibility: a public type in B is visible only if B exports its package. Public is no longer enough.",
             "Most applications never write a module-info, and that's a defensible choice. But you can't opt out of the fact that the JDK itself is modularised. "
             "Its internals are now behind boundaries the JVM enforces.",
         ]),

    dict(title="What strong encapsulation looks like",
         kicker="Even without module-info",
         body=code('''
java.lang.reflect.InaccessibleObjectException: Unable to make field private final
java.util.ArrayList.elementData accessible: module java.base does not "opens java.util"
to unnamed module @0x4b1c1ea0''', lang="text", title="Since Java 16–17", size=24)
              + code('java --add-opens java.base/java.util=ALL-UNNAMED -jar orders.jar', lang="bash", title="Stopgap", step=1, size=26)
              + frag(table(["", "Compile against", "Deep reflection"], [
                    ["`exports p`", "Yes", "**No**"],
                    ["`opens p`", "No", "Yes — what JPA, Jackson and DI need"],
                ], cls="sm"), 2),
         narration=[
             "Here's what that feels like. Java 16 strongly encapsulated JDK internals, and Java 17 removed the escape hatch. "
             "So a library that reflects into java dot util now fails with an InaccessibleObjectException, even in an app that never modularised.",
             "The add-opens flag grants access. But treat it as a temporary measure. Each one is a library reaching into JDK internals, and the real fix is upgrading that library. "
             "A startup script that collects add-opens flags over the years is a to-do list.",
             "And know the difference. Exports lets other code compile against your types. Opens permits deep reflection, which is what JPA, Jackson and dependency injection need.",
         ]),

    dict(title="jlink: the benefit teams actually collect",
         kicker="A smaller runtime",
         body=code('''
jdeps --print-module-deps --ignore-missing-deps orders.jar
# java.base,java.sql,java.net.http

jlink --add-modules java.base,java.sql,java.net.http \\
      --strip-debug --no-man-pages --no-header-files --compress=2 \\
      --output runtime''', lang="bash", title="Build a minimal runtime", size=28)
              + frag('<div class="pipeline"><span>200 MB+ JDK</span>→<span class="hl">~45 MB runtime</span></div>', 1),
         narration=[
             "Here's the module-system benefit most teams actually collect. jdeps lists the JDK modules your jar needs. "
             "jlink builds a runtime containing only those.",
             "The result is about forty-five megabytes instead of a two-hundred-megabyte JDK. That's smaller container layers and faster cold starts. "
             "And it works for a plain classpath application. jlink builds the runtime, not your app.",
         ]),

    dict(title="HttpClient (Java 11)",
         kicker="Worked example",
         body=code('''
private static final HttpClient CLIENT = HttpClient.newBuilder()      // one per application
    .version(HttpClient.Version.HTTP_2)
    .connectTimeout(Duration.ofSeconds(5))                            // timeout 1: connecting
    .build();

HttpRequest request = HttpRequest.newBuilder(baseUri.resolve("/dispatch"))
    .header("Content-Type", "application/json")
    .timeout(Duration.ofSeconds(10))                                  // timeout 2: whole exchange
    .POST(HttpRequest.BodyPublishers.ofString(toJson(order)))
    .build();

HttpResponse<String> response = CLIENT.send(request, BodyHandlers.ofString());''',
                   title="VendorClient.java", size=25)
              + bullets(["`HttpClient` is immutable and thread-safe — **never create one per request**",
                         "Set **both** timeouts, or a hung read waits forever"], start_step=1, cls="bullets sm"),
         narration=[
             "Java 11 standardised a modern HTTP client, with HTTP/2 by default and both blocking and async calls. Build a request with a URI, headers, a timeout and a body, then send it.",
             "The client is immutable and thread-safe, so keep one per application in a static final field. Creating one per request leaks connection pools.",
             "And notice the two timeouts. Connect timeout on the client only covers opening the connection. The request timeout covers the whole exchange. "
             "Set only the first, and a hung read can wait forever.",
         ]),

    dict(title="var: inference, not dynamic typing",
         kicker="Java 10",
         body='<div class="grid2 start">'
              + code('''
// ✓ the line names the type
var catalogue = new HashMap<Sku, InventoryItem>();
var line = new CartLine(sku, 2, Money.rupees("60"));
for (var entry : totals.entrySet()) { }''', title="Helps", size=24)
              + frag(code('''
// ✗ type is invisible
var result = process(input);
var data = service.fetch();

// ✗ infers ArrayList<Object>!
var lines = new ArrayList<>();''', title="Hurts", size=24), 1)
              + "</div>"
              + frag('<p class="callout"><b>The test:</b> can a reader name the type from this line alone? '
                     'If not, <code>var</code> removed information, not noise.</p>', 2),
         narration=[
             "var is type inference, resolved at compile time. The variable still has exactly one static type, and the bytecode is identical. "
             "It helps when the right-hand side already names the type, like a constructor call, or a loop over map entries.",
             "It hurts when the type disappears. var result equals process input tells the reader nothing. "
             "And here's the real trap: var lines equals new ArrayList with an empty diamond. There's nothing to infer from, so you get an ArrayList of Object, and every add compiles.",
             "So use this test. Can a reader name the type from that line alone? If not, var has removed information, not noise.",
         ]),

    dict(title="Small APIs worth using",
         kicker="Java 9–11",
         body=code('''
List<Sku> featured  = List.of(milk, rice, atta);
Map<Sku, Money> prices = Map.of(milk, Money.rupees("60"), rice, Money.rupees("450"));''',
                   title="Collection factories (9)", size=26)
              + bullets(["**Truly immutable** — not a view over something mutable",
                         "**Reject nulls** — even `List.of(\"a\").contains(null)` throws",
                         "`Set.of` / `Map.of` **randomise iteration order** per JVM run"], start_step=0, cls="bullets sm")
              + code('''
"  ".isBlank();   "  text  ".strip();   "-".repeat(40);   "a\\nb".lines();
String config = Files.readString(path);   Files.writeString(path, content, UTF_8);''',
                     title="String & file helpers (11)", step=3, size=26),
         narration=[
             "Some small APIs worth using. Java 9's collection factories, List dot of, Set dot of and Map dot of, give you truly immutable collections, not a read-only view over something mutable.",
             "They reject nulls, not only on creation but on lookup. Even asking whether the list contains null throws.",
             "And Set dot of and Map dot of deliberately randomise their iteration order on every JVM run, so your code can't depend on it.",
             "Java 11 added isBlank, strip, repeat and lines on strings, plus Files dot readString and writeString. Prefer strip over trim, because trim predates Unicode and misses non-breaking spaces.",
         ]),

    dict(title="What breaks from Java 8",
         kicker="Migration",
         body=table(["Symptom", "Cause", "Fix"], [
                    ["`NoClassDefFoundError: javax/xml/bind/...`", "Java EE modules removed in 11", "Add Jakarta artifacts as dependencies"],
                    ["`InaccessibleObjectException`", "Strong encapsulation (16–17)", "Upgrade the library; `--add-opens` as a stopgap"],
                    ["`sun.misc.Unsafe`, `com.sun.*`", "Internal APIs", "`VarHandle` or the FFM API (Ch 39)"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">Modularising a service is optional and usually not worth it. Shipping a <b>library</b>? '
                     'Publish <code>Automatic-Module-Name</code> at minimum.</p>', 3),
         narration=[
             "Three things actually break when you move off Java 8. First, NoClassDefFoundError on javax dot xml dot bind. Java 11 removed JAXB and the other Java EE modules. Add them back as ordinary Jakarta dependencies.",
             "Second, InaccessibleObjectException from reflection libraries. Upgrade the library, using add-opens only as a stopgap.",
             "Third, anything using sun dot misc dot Unsafe or com dot sun internals. Find the supported replacement, usually VarHandle or the foreign function and memory API.",
             "Modularising a service itself is optional, and usually not worth it. But if you ship a library, publish an Automatic-Module-Name, so consumers who do modularise get a stable name.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["One `static final HttpClient`; set both timeouts",
                         "`var` only where the line names the type",
                         "`List.of` / `Map.of` for constants; `strip()` over `trim()`",
                         "`jdeps` + `jlink` for container images",
                         "Treat each `--add-opens` as a ticket"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["An `HttpClient` per request",
                         "`var x = new ArrayList<>()`",
                         "Assume `List.of` tolerates null",
                         "Depend on `Set.of` / `Map.of` order",
                         "Split a package across modules or jars"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. One static final HttpClient, with both timeouts set. var only where the line names the type. List dot of and Map dot of for constants, and strip over trim. "
             "Use jdeps and jlink for container images. And treat every add-opens flag as a ticket, with a note on which library needs it.",
             "Never create an HttpClient per request. Never write var with an empty diamond. Never assume the new factories tolerate null, or depend on their iteration order. "
             "And never split a package across modules, which fails at launch on the module path.",
         ]),

    dict(title="Java 9 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**9**", "Modules; `List/Set/Map.of`; private interface methods; JShell"],
                    ["**10**", "`var`; `List.copyOf`"],
                    ["**11 LTS**", "`HttpClient`; String/Files helpers; single-file launch; **Java EE removed**"],
                    ["**16–17**", "JDK internals strongly encapsulated; `--illegal-access` gone"],
                    ["**21**", "Virtual threads — blocking `HttpClient.send` is the natural style"],
                    ["**26**", "HTTP/3 in `HttpClient` (Ch 40)"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 9 brought modules, the collection factories, private interface methods and JShell.",
             "Java 10 brought var.",
             "Java 11, the long-term release, standardised HttpClient, added the string and file helpers and single-file source launch, and removed the Java EE modules.",
             "Java 16 and 17 closed off JDK internals for good.",
             "With Java 21's virtual threads, the simple blocking send call is the natural style again.",
             "And Java 26 adds HTTP/3 to the client. That's chapter forty.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 11 · Java 9–11",
         body=bullets(["The **JDK is modularised** — encapsulation applies to everyone",
                       "`exports` to compile against; `opens` for reflection",
                       "`jlink` shrinks container runtimes, even for classpath apps",
                       "One `HttpClient`, two timeouts",
                       "`var` only where the line names the type",
                       "Next: **Ch 12 · Records, Sealed Types, Text Blocks**"], cls="bullets recap"),
         narration=[
             "To recap. The JDK is modularised, so strong encapsulation applies whether you opted in or not. Exports is for compiling against, opens is for reflection. "
             "jlink shrinks your runtime, even for classpath apps. Keep one HttpClient with two timeouts. And use var only where the line names the type.",
             "Next is chapter twelve: records, sealed types and text blocks. Thanks for watching.",
         ]),
]
