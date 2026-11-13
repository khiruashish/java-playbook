"""Chapter 29 — CompletableFuture. Source: docs/04-concurrency/29-completable-future.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 29 · CompletableFuture"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="CompletableFuture",
         kicker="Concurrency · Chapter 29",
         body='<p class="sub">Composing asynchronous work without a waiting thread — and the threads, exceptions and cancellations that surprise people.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter twenty-nine: CompletableFuture.",
             "The Java 5 Future could only be waited on. CompletableFuture makes combining, falling back and timing out operations on the future itself, with no thread blocked waiting.",
         ]),

    dict(title="A Future you can only wait on",
         kicker="The problem",
         body=code('''
Future<StockStatus>     stock   = pool.submit(() -> inventory.statusFor(cart));
Future<PricingSnapshot> pricing = pool.submit(() -> pricingEngine.snapshot(cart));
OrderContext ctx = new OrderContext(stock.get(), pricing.get());     // blocks, blocks''',
                   title="PlainFuture.java", size=25)
              + code('''
CompletableFuture<OrderContext> context =
    supplyAsync(() -> inventory.statusFor(cart), ioPool)
        .thenCombine(supplyAsync(() -> pricingEngine.snapshot(cart), ioPool), OrderContext::new)
        .orTimeout(2, TimeUnit.SECONDS)
        .exceptionally(e -> OrderContext.unavailable());     // no thread waits for any of it''',
                     title="Composed.java", step=1, size=25),
         narration=[
             "With a plain Future, you can only call get, which blocks. There's no way to say, when both are done, combine them, or if this fails, use a fallback, without blocking a thread and writing it by hand.",
             "CompletableFuture makes each of those an operation. Run stock and pricing lookups, combine them into an order context, time out after two seconds, and fall back if anything fails. No thread waits for any of it.",
         ]),

    dict(title="A promise, completed once",
         kicker="Mental model",
         body='<div class="grid2">'
              + card("Completes exactly once", "With a value, an exception, or cancellation. Later attempts are ignored. Dependent stages run on completion.", "indigo", 0)
              + card("Each method returns a new stage", "A chain is a **dependency graph** — each stage triggered by its inputs completing.", "cyan", 1)
              + "</div>"
              + frag(table(["Method", "Shape"], [
                    ["`thenApply`", "Transform — like `map`"],
                    ["`thenCompose`", "Function returns a future — like `flatMap`"],
                    ["`thenCombine`", "Combine with another future's value"],
                    ["`...Async(fn, executor)`", "Run the stage on **this** executor"],
                ], cls="sm"), 2),
         narration=[
             "A CompletableFuture is a container that's completed exactly once: with a value, an exception, or cancellation. Stages registered on it run when it completes.",
             "Each method returns a new future for that stage, so a chain is really a dependency graph, with each stage triggered by its inputs.",
             "The naming has a grammar. thenApply transforms the value, like map. thenCompose is for a function that returns a future, like flatMap. thenCombine joins two futures. "
             "And every stage has an Async variant, optionally with an executor, which decides where it runs. That turns out to matter a lot.",
         ]),

    dict(title="Fan-out and combine",
         kicker="Worked example",
         body=code('''
var stock   = supplyAsync(() -> inventory.statusFor(cart), ioExecutor);
var pricing = supplyAsync(() -> pricingEngine.snapshot(cart), ioExecutor);
var profile = supplyAsync(() -> customers.profile(customer), ioExecutor);

return CompletableFuture.allOf(stock, pricing, profile)
    .thenApply(_ -> new OrderContext(stock.join(), pricing.join(), profile.join()));
    //                                  join() here never blocks — allOf already guaranteed it''',
                   title="OrderContextLoader.java", size=25)
              + code('''
loadOrder(id).thenApply(order -> dispatchAsync(order));     // CompletableFuture<CompletableFuture<Receipt>>
loadOrder(id).thenCompose(order -> dispatchAsync(order));   // CompletableFuture<Receipt>''',
                     title="ApplyVsCompose.java", step=1, size=25),
         narration=[
             "Here's the standard fan-out. Start three lookups in parallel. allOf completes when they all do, but it carries no values, so read them from the original futures. Calling join there doesn't block, because allOf already guaranteed they're done.",
             "And the classic mistake. If the function already returns a future, thenApply gives you a future of a future. Use thenCompose to flatten it. A nested CompletableFuture in a signature is always a missed thenCompose.",
         ]),

    dict(title="Exceptions arrive wrapped",
         kicker="Worked example",
         body=code('''
.exceptionally(e -> {
    Throwable cause = (e instanceof CompletionException && e.getCause() != null) ? e.getCause() : e;
    return switch (cause) {
        case VendorUnavailableException _ -> DispatchReceipt.deferred();
        case TimeoutException _           -> DispatchReceipt.timedOut();
        default -> throw new CompletionException(cause);
    };
});''', title="Unwrapping.java", size=25)
              + frag(table(["Method", "Runs", "Can recover?"], [
                    ["`exceptionally`", "On failure", "Yes — a replacement value"],
                    ["`handle`", "Always", "Yes — sees value **and** exception"],
                    ["`whenComplete`", "Always", "**No** — observes; the failure continues"],
                ], cls="sm"), 1),
         narration=[
             "Exceptions arrive wrapped. Throw a VendorUnavailableException inside a stage, and the next stage sees a CompletionException. So code that matches on the exception type silently fails. "
             "Always unwrap the cause first, then match. join and get wrap the cause too.",
             "And know the three error methods. exceptionally runs only on failure and returns a replacement. handle always runs, sees both value and exception, and returns a result. "
             "whenComplete always runs too, but only observes. It can't change the outcome, so a failure keeps flowing down the chain. Use it for metrics, not recovery.",
         ]),

    dict(title="Timeouts don't stop work",
         kicker="Worked example",
         body=code('''
quoteFrom(vendor).orTimeout(2, SECONDS);                                // fail after 2 s
quoteFrom(vendor).completeOnTimeout(Quote.standardRate(), 2, SECONDS);  // or use a default
CompletableFuture.anyOf(quoteFrom(a), quoteFrom(b), quoteFrom(c));      // first to answer → Object

future.cancel(true);     // mayInterruptIfRunning is IGNORED — the task keeps running''',
                   title="Timeouts.java", size=25)
              + frag('<p class="callout"><code>orTimeout</code>, <code>anyOf</code> losers and <code>cancel</code> complete the <b>future</b> — '
                     'the underlying work <b>keeps running</b>. Structured concurrency (Ch 32) actually cancels.</p>', 1),
         narration=[
             "Timeouts. orTimeout fails the future after two seconds. completeOnTimeout uses a default value instead. And anyOf returns whichever vendor answers first, typed as Object, so you'll need a cast.",
             "But here's the catch. All of these complete the future. None of them stop the work. A timed-out call keeps running, using its thread and the downstream's capacity, and so do anyOf's losers. "
             "Even cancel ignores its interrupt flag, because a CompletableFuture has no reference to the thread running its task. Structured concurrency, in chapter thirty-two, actually cancels.",
         ]),

    dict(title="Which thread runs a stage?",
         kicker="Internals",
         body=table(["You write", "The stage runs on"], [
                    ["`thenApply(fn)` — future already complete", "The **calling** thread, immediately"],
                    ["`thenApply(fn)` — not yet complete", "Whichever thread **completes** it — e.g. the HTTP client's I/O thread"],
                    ["`thenApplyAsync(fn)`", "`ForkJoinPool.commonPool()`"],
                    ["`thenApplyAsync(fn, executor)`", "**Your executor** ✓"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "Which thread runs a stage? This is what most people get wrong. A non-async stage on an already-complete future runs right away, on the calling thread.",
             "If the future isn't complete yet, it runs on whichever thread completes it. If that's an HTTP client's callback thread, your slow stage now blocks the client.",
             "The Async variant without an executor runs on the common ForkJoinPool.",
             "And with an executor, it runs exactly where you choose. For anything non-trivial, pass an executor.",
         ]),

    dict(title="The common pool trap",
         kicker="The most common production incident",
         body=code('''
supplyAsync(() -> warehouseClient.statusFor(sku));      // ✗ no executor → commonPool()
// shared JVM-wide with parallel streams, ~one thread per core:
// enough blocking calls exhaust it, and every parallel stream stalls

private static final Executor IO = Executors.newVirtualThreadPerTaskExecutor();
supplyAsync(() -> warehouseClient.statusFor(sku), IO);   // ✓ Java 21+''', title="CommonPool.java", size=26)
              + frag('<p class="callout">Still the right tool for <b>bridging callback APIs</b>: '
                     '<code>new CompletableFuture&lt;&gt;()</code> + <code>complete</code> / <code>completeExceptionally</code>.</p>', 1),
         narration=[
             "Without an executor argument, supplyAsync runs on the common pool. It's shared by the whole JVM, including parallel streams, and has roughly one thread per core. "
             "Blocking I/O there ties up those few threads. Enough concurrent calls exhaust the pool, and everything else using it stalls. "
             "So always pass an executor for anything that blocks. On Java 21, a virtual-thread executor is the natural choice.",
             "And one place CompletableFuture remains the clearest tool: adapting a callback-based SDK. Create an incomplete future, then complete it from the success and failure callbacks.",
         ]),

    dict(title="The same fan-out on Java 21+",
         kicker="Structured concurrency (preview)",
         body=code('''
try (var scope = StructuredTaskScope.open(Joiner.<Object>allSuccessfulOrThrow())) {
    var stock   = scope.fork(() -> inventory.statusFor(cart));
    var pricing = scope.fork(() -> pricingEngine.snapshot(cart));
    var profile = scope.fork(() -> customers.profile(customer));
    scope.join();
    return new OrderContext(stock.get(), pricing.get(), profile.get());
}''', title="VirtualThreadEquivalent.java", size=26)
              + frag(bullets(["Reads as **sequential code**, with real stack traces",
                              "A failure **cancels the siblings**",
                              "Blocks the caller — nearly free on a virtual thread"], cls="bullets sm"), 1),
         narration=[
             "Compare the same fan-out with structured concurrency, which is still a preview feature. Open a scope, fork three subtasks, join, and read the results.",
             "It reads like sequential code, with useful stack traces. If one subtask fails, the siblings are cancelled. Those are exactly the things CompletableFuture is weakest at. "
             "The trade-off is that it blocks the calling thread, which on a virtual thread costs almost nothing.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Always pass an executor for blocking work",
                         "`thenCompose` when the function returns a future",
                         "Unwrap `CompletionException` before matching",
                         "`orTimeout` / `completeOnTimeout` on remote calls",
                         "Use it to bridge callback APIs"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Blocking I/O on the common pool",
                         "Expect `cancel(true)` to interrupt",
                         "Assume a timeout stops the work",
                         "Recover with `whenComplete`",
                         "Slow non-async stages on someone else's thread"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Always pass an executor for blocking work. Use thenCompose when the function returns a future. Unwrap CompletionException before matching. "
             "Put timeouts on remote calls. And use CompletableFuture to bridge callback APIs.",
             "Never run blocking I/O on the common pool. Never expect cancel to interrupt, or a timeout to stop the work. Never try to recover with whenComplete. "
             "And never put slow non-async stages where they'll run on someone else's thread.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 29 · CompletableFuture",
         body=bullets(["Compose async work — **no thread waits**",
                       "`thenApply` = map, `thenCompose` = flatMap",
                       "Exceptions arrive as `CompletionException` — unwrap",
                       "Timeouts and `cancel` don't stop the work",
                       "Always pass an executor; never block the common pool",
                       "Next: **Ch 30 · Concurrent Collections**"], cls="bullets recap"),
         narration=[
             "To recap. CompletableFuture composes async work with no thread waiting. thenApply is map, and thenCompose is flatMap. Exceptions arrive wrapped, so unwrap them. "
             "Timeouts and cancel don't stop the underlying work. And always pass an executor, never blocking the common pool.",
             "Next is chapter thirty: concurrent collections. Thanks for watching.",
         ]),
]
