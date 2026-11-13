"""Chapter 15 — String Templates: A Post-Mortem. Source: docs/02-language/15-string-templates-postmortem.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 15 · String Templates: A Post-Mortem"
SECTION = "Language"

SLIDES = [
    dict(kind="title",
         title="String Templates: A Post-Mortem",
         kicker="Language · Chapter 15",
         body='<p class="sub">Previewed twice, then removed. What they were, why they didn\'t ship, and how to consume '
              'a six-month release cadence without betting on features that never arrive.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter fifteen: a post-mortem on string templates.",
             "String templates were previewed in Java 21, previewed again in 22, and then removed. They ship in no released JDK. "
             "Yet plenty of articles from 2023 and 2024 describe them as part of the language. That makes them the perfect case study in how to adopt new Java features safely.",
         ]),

    dict(title="The real problem was safety",
         kicker="The problem",
         body=code('''
String message = "Order " + order.id() + " for " + customer.name()
               + " totalling " + order.total() + " will arrive on " + order.deliveryDate();''',
                   title="Concatenation.java — readability", size=25)
              + code('''
String sql  = "select * from orders where customer_id = '" + customerId + "'";   // SQL injection
String html = "<div>" + userSuppliedName + "</div>";                            // XSS''',
                     title="Injection.java — safety", step=1, size=25)
              + frag('<p class="callout">Plain interpolation makes the <b>unsafe</b> pattern more convenient. '
                     'That tension is what String Templates tried to resolve — and what sank them.</p>', 2),
         narration=[
             "String interpolation is Java's most requested missing feature. Concatenation is readable at three pieces and unreadable at six.",
             "But the deeper problem was never readability. It was safety. Concatenating values into SQL gives you injection. Concatenating user input into HTML gives you cross-site scripting.",
             "Every language with plain interpolation makes those bugs easier to write. Making concatenation convenient without making injection convenient is the problem string templates tried to solve, and ultimately what sank them.",
         ]),

    dict(title="A template was not a string",
         kicker="What was proposed",
         body=code('''
// NOT VALID IN ANY RELEASED JDK
String message = STR."Order \\{order.id()} for \\{customer.name()}";
PreparedStatement ps = SQL."select * from orders where customer_id = \\{customerId}";''',
                   title="ProposedSyntax.java", size=26)
              + flow(["Template\nfragments + values, kept apart",
                      "Processor decides",
                      "`STR` → String\n`SQL` → bound parameters\n`JSON` → escaped values"], step_start=1)
              + frag('<p class="callout">The safe form would have been the convenient one. No mainstream language\'s interpolation does this.</p>', 3),
         narration=[
             "Here's what was proposed. Note, none of this compiles on any released JDK. You'd write STR dot, then a string with backslash-brace expressions.",
             "The key design choice: a template was not a string. It was an object holding the literal fragments and the evaluated values separately.",
             "A template processor then decided what to produce. STR would concatenate. But a SQL processor could bind the values as parameters, never letting them into the query text. A JSON processor could escape them.",
             "So the safe form would have been the convenient one. No other mainstream language's interpolation works like that.",
         ]),

    dict(title="Why it was withdrawn",
         kicker="After two previews",
         body=table(["Concern", ""], [
                    ["**Ergonomics**", "`STR.` on every template — noise for the common case"],
                    ["**Syntax**", "`\\{}` is unusual and interacts with existing escapes"],
                    ["**Scope**", "Interpolation or safe construction? It served both, excelled at neither"],
                    ["**Finality is forever**", "Once final, the syntax and processor API could never change"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">A revised design may return. Nothing has been announced — <b>assume no timeline</b>.</p>', 4),
         narration=[
             "Why was it withdrawn? First, ergonomics. Writing STR dot in front of every template, with a static import, read as noise for the common case.",
             "Second, the backslash-brace syntax was unusual among languages and tangled with existing escaping rules.",
             "Third, scope confusion. Was it about interpolation, or about safe construction? The design served both and excelled at neither.",
             "And finally, finality is forever. Once final, the syntax and the processor API could never change. The JDK team chose to withdraw rather than ship a design they expected to regret.",
             "A revised design may return, but nothing has been announced. Don't assume any timeline.",
         ]),

    dict(title="What to do instead",
         kicker="Readability today",
         body=code('''
String receipt = """
    Order:    %s
    Customer: %s
    Total:    %s
    """.formatted(order.id(), customer.name(), order.total());

log.info("order {} total {}", id, total);       // parameterised logging — lazy, too''',
                   title="TextBlockFormatted.java", size=27)
              + frag(code('''
// Was (preview, Java 21–22)              // Now
STR."Order \\{order.id()} total \\{t}"     "Order %s total %s".formatted(order.id(), t)''',
                          title="Migration", size=24), 1),
         narration=[
             "So what do you use today? For readability, a text block with dot formatted gets you very close to the templated version. "
             "For logging, use parameterised log messages, which also skip building the string when the level is off.",
             "And if you have a spike or training deck that uses STR, it won't compile on any current JDK. The conversion to formatted is mechanical.",
         ]),

    dict(title="Safety is already available",
         kicker="The real goal",
         body=code('''
PreparedStatement ps = connection.prepareStatement("select * from orders where customer_id = ?");
ps.setObject(1, customerId);                                    // SQL — always parameters

String json = objectMapper.writeValueAsString(order);           // JSON — a serializer

URI uri = URI.create(base).resolve("?sku=" + URLEncoder.encode(sku, UTF_8));   // URLs — encode''',
                   title="SafeConstruction.java", size=25)
              + frag('<p class="callout">Separate <b>structure</b> from <b>data</b>. Templates would have made the safe path convenient — '
                     'they were never the only safe path.</p>', 1),
         narration=[
             "And for safety, which was the real goal, you don't need to wait. Use prepared statement parameters for every SQL value. Use a serializer for JSON, never string assembly. "
             "Use an escaping template engine for HTML. And encode URL parameters.",
             "Every one of these separates structure from data, the same principle templates were built on. Templates would have made the safe path more convenient. They were never the only safe path.",
         ]),

    dict(title="Incubator → preview → final … or withdrawn",
         kicker="The general lesson",
         body=table(["Stage", "Stability", "Use it for"], [
                    ["**Incubator**", "API will change", "Experiments only"],
                    ["**Preview**", "Complete, but may change or **vanish**", "Code you can rewrite"],
                    ["**Final**", "Permanent", "Production"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout"><code>--enable-preview</code> class files are bound to the <b>exact</b> JDK release that built them — '
                     'Java 25 output will not load on 26.</p>', 3),
         narration=[
             "Here's the general lesson. New Java features move through stages. Incubator modules are experiments, and their APIs will change.",
             "Preview features are complete, but they may change or vanish. There's no commitment. That's what preview means, and string templates proved it.",
             "Only final features are permanent and production-ready.",
             "And preview isn't just a warning. You need enable-preview at compile and run time, and the class files are stamped so they only load on the exact JDK release that built them. "
             "Code compiled with preview on Java 25 will not run on 26.",
         ]),

    dict(title="The track record",
         kicker="Plan against the base rate",
         body=table(["Feature", "What happened"], [
                    ["String Templates", "Two previews, then **withdrawn**"],
                    ["Structured concurrency", "Five-plus previews, **redesigned** — Java 21 code doesn't compile on 25"],
                    ["Scoped values", "Incubator, several previews with API changes; final in 25"],
                    ["Vector API", "Incubating since Java 16, pending Valhalla"],
                    ["Records, sealed, patterns", "Previewed, refined, finalised — the process working"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "Preview instability isn't theoretical. String templates: two previews, then withdrawn.",
             "Structured concurrency: five or more previews, and a substantial redesign. Java 21 code using it doesn't compile on 25.",
             "Scoped values went through an incubator and several API changes before finalising in 25.",
             "The Vector API has been incubating since Java 16, waiting on Project Valhalla.",
             "And records, sealed types and pattern matching show the process working as intended: previewed, refined, then finalised. "
             "But two of these five cost real rework for early adopters. That's the base rate to plan against.",
         ]),

    dict(title="A workable policy",
         kicker="Consuming the six-month cadence",
         body=table(["Code", "Policy"], [
                    ["Published libraries", "**Never** preview features"],
                    ["Production services", "Final only; preview behind a flag you can remove"],
                    ["Internal tooling & scripts", "Preview is fine — rewriting is cheap"],
                    ["Spikes and evaluation", "Preview is the point"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">Treat any Java article <b>without a JDK version</b> as suspect. Check the JEP status before believing a tutorial.</p>', 4),
         narration=[
             "So here's a workable policy. Published libraries: never use preview features, because nobody on another JDK could load them.",
             "Production services: final features only, or preview behind a flag you can remove.",
             "Internal tooling and scripts: preview is fine, because rewriting them is cheap.",
             "And spikes and evaluation: that's exactly what preview is for.",
             "One habit matters more than any of these. Treat any Java article without a JDK version as suspect, and check a feature's JEP status before believing a tutorial about it.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Text blocks + `.formatted(...)`",
                         "Parameterised logging",
                         "`PreparedStatement` parameters for every SQL value",
                         "Serializers for JSON, escaping engines for HTML",
                         "Check JEP status before adopting",
                         "Run non-LTS releases in CI"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Use String Templates — `STR.\"...\"` won't compile",
                         "Ship preview features in a published library",
                         "Treat a much-previewed API as stable",
                         "Trust an undated Java article",
                         "Build SQL, HTML or JSON by concatenation",
                         "`--enable-preview` \"just in case\""], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use text blocks with formatted, and parameterised logging. Use prepared statement parameters for every SQL value, serializers for JSON and escaping engines for HTML. "
             "Check JEP status before adopting anything. And run non-LTS releases in CI, to catch removals before your next LTS upgrade.",
             "Never use string templates. Never ship preview features in a library. Never treat an API as stable just because it's been previewed many times. "
             "Never trust an undated article. Never build SQL, HTML or JSON by concatenation. And never turn on enable-preview just in case.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 15 · String Templates",
         body=bullets(["String Templates were **previewed twice and removed** — they exist in no JDK",
                       "The goal was **safety**: keep structure and data apart",
                       "Today: text blocks + `formatted`; parameters, serializers, escaping",
                       "Preview means **no commitment** — and class files tied to one release",
                       "Next: **Ch 16 · Generics in Depth**"], cls="bullets recap"),
         narration=[
             "To recap. String templates were previewed twice and removed, and exist in no JDK. Their real goal was safety, keeping structure and data apart. "
             "Today, use text blocks with formatted for readability, and parameters, serializers and escaping for safety. "
             "And remember that preview means no commitment, with class files tied to one release.",
             "Next is chapter sixteen, generics in depth. Thanks for watching.",
         ]),
]
