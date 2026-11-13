"""Chapter 32 — Structured Concurrency. Source: docs/04-concurrency/32-structured-concurrency.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 32 · Structured Concurrency"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Structured Concurrency",
         kicker="Concurrency · Chapter 32 · Preview",
         body='<p class="sub">Make a subtask\'s lifetime visible in the code that starts it — no orphans, no leaks, no forgotten cancellation.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-two: structured concurrency.",
             "It does for concurrent tasks what blocks and braces did for goto. A scope can't be exited while its subtasks are still running. "
             "One warning first: this is still a preview API, and its shape changed between Java 21 and Java 25. Check signatures against your JDK before copying any sample, including these.",
         ]),

    dict(title="Every line is a hazard",
         kicker="The problem",
         body=code('''
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
Future<StockStatus>     stock   = executor.submit(() -> inventory.statusFor(cart));
Future<PricingSnapshot> pricing = executor.submit(() -> pricingEngine.snapshot(cart));
Future<DeliveryProfile> profile = executor.submit(() -> customers.profile(customerId));
return new OrderContext(stock.get(), pricing.get(), profile.get());''', title="UnstructuredFanOut.java", size=24)
              + bullets(["**No cancellation** — if stock fails, the others keep running",
                         "**Leaked executor** on the exception path",
                         "**Sequential discovery** — a pricing failure is found last",
                         "**No relationship** — a thread dump shows three unrelated threads"], start_step=1, cls="bullets sm"),
         narration=[
             "Loading an order context needs three independent lookups, and all must succeed. The usual approach submits three tasks to an executor and gets each result. It looks fine. Every line is a hazard.",
             "If stock fails, pricing and profile keep running to completion, wasting their load on downstream services.",
             "The executor is never shut down on the exception path.",
             "Results are fetched in order, so a pricing failure is discovered last.",
             "And at runtime, nothing records that these three threads belong to one request.",
         ]),

    dict(title="A block with a lifetime",
         kicker="Mental model",
         body=flow(["`try (var scope = open(...))`", "**fork** stock · pricing · profile", "**join()** — until the policy is met", "**close()** — cancels anything still running"], step_start=0)
              + frag(table(["", "Executor", "CompletableFuture", "Structured"], [
                    ["Lifetime", "Unbounded", "Unbounded", "**Lexically scoped**"],
                    ["Cancel siblings on failure", "Manual", "Manual", "**Automatic**"],
                    ["Stack traces", "Partial", "Poor", "**Complete**"],
                    ["Reads like sequential code", "No", "No", "**Yes**"],
                ], cls="sm"), 4),
         narration=[
             "A scope is a block with a lifetime. Open it in a try-with-resources.",
             "Fork the subtasks inside it.",
             "join waits until the scope's policy is satisfied.",
             "And close is guaranteed, cancelling anything still running. The opening brace starts concurrency, and the closing brace ends it.",
             "Compared to executors and CompletableFuture, the lifetime is lexically scoped, siblings are cancelled automatically on failure, stack traces are complete, and the code reads sequentially.",
         ]),

    dict(title="Fan-out with fail-fast",
         kicker="Java 25 shape",
         body=code('''
try (var scope = StructuredTaskScope.open(Joiner.<Object>allSuccessfulOrThrow())) {
    Subtask<StockStatus>     stock   = scope.fork(() -> inventory.statusFor(cart));
    Subtask<PricingSnapshot> pricing = scope.fork(() -> pricingEngine.snapshot(cart));
    Subtask<DeliveryProfile> profile = scope.fork(() -> customers.profile(customerId));

    scope.join();      // returns when all succeed; throws on the first failure
    return new OrderContext(stock.get(), pricing.get(), profile.get());
}''', title="OrderContextLoader.java", size=25)
              + frag('<p class="callout">Pricing fails at 40 ms → stock and profile are <b>cancelled immediately</b>. The scope closes on every path. '
                     'Subtasks are virtual threads, grouped under this scope in a dump.</p>', 1),
         narration=[
             "Here's the loader, structured, using the Java 25 shape. Open a scope with a joiner that requires all subtasks to succeed. Fork three subtasks. join returns when they all succeed, or throws on the first failure. Then read the results.",
             "If pricing fails at forty milliseconds, stock and profile are cancelled immediately. The scope closes on every path, including exceptions. "
             "The subtasks are virtual threads, and a thread dump groups them under this scope. And it reads like sequential code.",
         ]),

    dict(title="Policies are Joiners",
         kicker="Core API",
         body=table(["Joiner", "Semantics"], [
                    ["`allSuccessfulOrThrow()`", "All must succeed; first failure cancels the rest and throws"],
                    ["`anySuccessfulResultOrThrow()`", "First success wins; others cancelled"],
                    ["`awaitAll()`", "Wait for every subtask; inspect each outcome"],
                    ["`allUntil(predicate)`", "Stop when the predicate says so — partial results"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "The policy is a Joiner. allSuccessfulOrThrow: everything must succeed, and the first failure cancels the rest.",
             "anySuccessfulResultOrThrow: the first success wins, and the others are cancelled.",
             "awaitAll: wait for every subtask without throwing, and inspect each outcome yourself.",
             "And allUntil, with a predicate, for collecting partial results.",
         ]),

    dict(title="First success · partial results",
         kicker="Worked examples",
         body=code('''
try (var scope = StructuredTaskScope.open(Joiner.<DispatchQuote>anySuccessfulResultOrThrow())) {
    order.eligibleVendors().forEach(v -> scope.fork(() -> v.quote(order)));
    return scope.join();             // first success — the losers are cancelled mid-flight
}''', title="FastestVendor.java", size=24)
              + code('''
try (var scope = StructuredTaskScope.open(Joiner.<Object>awaitAll())) {
    var stock = scope.fork(() -> inventory.statusFor(cart));       // required
    var recs  = scope.fork(() -> recommender.forCart(cart));       // optional
    scope.join();
    if (stock.state() != Subtask.State.SUCCESS) throw new InventoryUnavailableException(stock.exception());
    var recommendations = recs.state() == Subtask.State.SUCCESS ? recs.get() : List.<Sku>of();   // degrade
}''', title="PartialResults.java", step=1, size=23),
         narration=[
             "Take the fastest of three vendors. Fork a quote request to each, and join returns the first success. The losers are cancelled mid-flight. "
             "With CompletableFuture dot anyOf, you'd get the first result, but the others would keep running.",
             "And for required plus optional work, use awaitAll. Join waits for both and throws nothing. Then decide per subtask: a missing stock status is an error, but missing recommendations just degrade to an empty list.",
         ]),

    dict(title="The API changed — know which you're reading",
         kicker="Java 21 vs Java 25",
         body=table(["", "Java 21–23 (obsolete)", "Java 25 (current preview)"], [
                    ["Construction", "`new ShutdownOnFailure()`", "`StructuredTaskScope.open(joiner)`"],
                    ["Policy", "Chosen by **subclass**", "Chosen by **Joiner**"],
                    ["Await", "`join()` then `throwIfFailed()`", "`join()` throws directly"],
                    ["First success", "`ShutdownOnSuccess`", "`anySuccessfulResultOrThrow()`"],
                ], step_per_row=0, cls="sm")
              + frag(code('javac --release 25 --enable-preview ...   &&   java --enable-preview ...',
                          lang="bash", title="Preview needs the flag at compile AND run time", size=24), 4),
         narration=[
             "The API changed, so know which version you're reading. Java 21 constructed a subclass like ShutdownOnFailure. Java 25 uses a static open method.",
             "The policy moved from choosing a subclass to passing a Joiner, so common policies are values rather than types you extend.",
             "In Java 21 you called join, then throwIfFailed. In Java 25, join throws directly.",
             "And ShutdownOnSuccess became anySuccessfulResultOrThrow. Java 21 code using the old shape won't compile on 25.",
             "As a preview feature, it needs enable-preview at compile and run time, and the class files only load on that exact JDK release. That alone is a reason to keep it out of shared libraries.",
         ]),

    dict(title="The rules it enforces",
         kicker="Structure, checked",
         body=code('''
try (var scope = StructuredTaskScope.open(Joiner.<String>allSuccessfulOrThrow())) {
    Subtask<String> task = scope.fork(() -> load());
    task.get();                  // ✗ IllegalStateException — join() hasn't run
    scope.join();
    scope.fork(() -> more());    // ✗ IllegalStateException — can't fork after join
}
// ✗ only the OWNER thread may fork and join''', title="Violations.java", size=26)
              + frag('<p class="callout">Each restriction closes off a way the structure could break. And scopes nest: cancelling the outer scope '
                     'cancels every inner one, transitively.</p>', 1),
         narration=[
             "The API enforces the structure. Calling get before join throws, because the result may not exist yet. Forking after join throws. And only the owner thread can fork and join.",
             "These aren't arbitrary. Each one closes off a way the structure could break. And scopes nest, so cancelling an outer scope cancels every inner scope, transitively, with no bookkeeping.",
         ]),

    dict(title="Internals",
         kicker="A real tree",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("A tree the runtime sees", "`jcmd Thread.dump_to_file -format=json` groups virtual threads **by scope** — a call tree, not 10,000 flat entries.", "indigo", 0)
              + card("Cancellation is interruption", "Subtasks must be **interruptible**. A non-interruptible native call won't stop; `close()` waits for it.", "cyan", 1)
              + card("ScopedValue flows in", "Bindings made with `ScopedValue.where(...)` are inherited by forked subtasks — **no copying** (Ch 33).", "fuchsia", 2)
              + "</div>",
         narration=[
             "Each scope records its owner and its subtasks, so the runtime sees a real tree. A JSON thread dump groups virtual threads by scope, giving you a call tree instead of ten thousand unrelated entries.",
             "Cancellation is interruption. So subtasks must respond to interruption for it to work. One stuck in a non-interruptible native call won't stop, and close will wait for it. Cooperative cancellation is still cooperative.",
             "And scoped values flow into subtasks. A binding made before opening the scope is inherited by every forked subtask, with no copying. That's the next chapter.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Scopes for request-scoped fan-out",
                         "`allSuccessfulOrThrow` when all inputs are required",
                         "`awaitAll` for required-plus-optional",
                         "Keep subtasks interruptible",
                         "Verify the API against your JDK"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Preview APIs in shared libraries",
                         "Copy Java 21 samples onto Java 25",
                         "`get()` before `join()`",
                         "Pass a scope to another thread",
                         "Swallow interruption inside a subtask"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use scopes for request-scoped fan-out. Use allSuccessfulOrThrow when every input is required, and awaitAll for required plus optional. "
             "Keep subtasks interruptible. And verify the API against your JDK.",
             "Never use this preview API in shared libraries. Never copy Java 21 samples onto Java 25. Never call get before join, or pass a scope to another thread. "
             "And never swallow interruption inside a subtask, or cancellation stops working.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 32 · Structured Concurrency",
         body=bullets(["A scope is a **block with a lifetime** — no orphans, no leaks",
                       "Failure **cancels siblings**; `join()` surfaces it",
                       "Policies are **Joiners**",
                       "Still **preview** — the API changed between 21 and 25",
                       "Next: **Ch 33 · Scoped Values**"], cls="bullets recap"),
         narration=[
             "To recap. A scope is a block with a lifetime, so subtasks can't be orphaned or leaked. A failure cancels the siblings, and join surfaces it where you can handle it. "
             "Policies are Joiners. And it's still a preview API, which changed shape between Java 21 and 25.",
             "That's the last chapter in this batch. The concurrency section finishes with chapter thirty-three, scoped values. Thanks for watching.",
         ]),
]
