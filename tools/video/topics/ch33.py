"""Chapter 33 — Scoped Values. Source: docs/04-concurrency/33-scoped-values.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 33 · Scoped Values"
SECTION = "Concurrency"

SLIDES = [
    dict(kind="title",
         title="Scoped Values",
         kicker="Concurrency · Chapter 33 · Java 25",
         body='<p class="sub">Carrying request context through the call stack — an immutable binding with a lifetime you can see, '
              'replacing most uses of <code>ThreadLocal</code>.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-three: scoped values, final in Java 25.",
             "Every server needs to carry context, like a trace ID, a tenant, or the logged-in user, through layers that shouldn't take it as a parameter. "
             "For twenty years the answer was ThreadLocal. Virtual threads broke its assumptions, and ScopedValue is the replacement.",
         ]),

    dict(title="ThreadLocal's four problems",
         kicker="The problem",
         body=code('''
RequestContextHolder.set(contextFrom(request));
try {
    handle(request);
} finally {
    RequestContextHolder.clear();      // forget this and you have a bug
}''', title="Filter.java", size=23)
              + '<div class="grid2">'
              + card("Unbounded lifetime", "Set until someone removes it — and any refactor can drop the `finally`.", "fuchsia", 1)
              + card("Leaks across requests", "A pooled thread outlives the request: the next one sees the **previous tenant**.", "amber", 1)
              + card("Anyone can write", "`set()` is public — context can change three layers down.", "cyan", 2)
              + card("Inheritance copies", "`InheritableThreadLocal` copies the map into every child. At a million threads, that matters.", "indigo", 2)
              + "</div>",
         narration=[
             "Here's the classic ThreadLocal pattern. Set the request context, handle the request, and clear it in a finally block.",
             "It has four compounding problems. Its lifetime is unbounded. It stays set until someone removes it, and any refactor can drop that finally. "
             "And on a pooled thread, if remove is missed, the next request sees the previous tenant's context. That's a correctness bug that is also a security incident.",
             "Anyone can write to it, so context can be changed three layers down without the caller knowing. "
             "And InheritableThreadLocal copies the whole map into every child thread. Invisible at two hundred threads, not at a million.",
         ]),

    dict(title="Immutable and bounded",
         kicker="Mental model",
         body=code('''
private static final ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();

ScopedValue.where(CONTEXT, ctx).run(() -> handle(request));   // bound here, and only here''',
                   title="Basic.java", size=26)
              + frag(table(["", "`ThreadLocal`", "`ScopedValue`"], [
                    ["Mutability", "`set` anywhere, any time", "Bound once per scope"],
                    ["Lifetime", "Until `remove()`", "The enclosing block"],
                    ["Cleanup", "Manual, easy to miss", "**Automatic**"],
                    ["Inheritance", "Copied per child thread", "**Shared**, no copy"],
                ], cls="sm"), 1),
         narration=[
             "A ScopedValue is bound for the duration of a block. Create a static final key, then call where with a value, and run. Everything that block calls can read it, and when the block returns, the binding is gone. "
             "There's no set and no remove.",
             "Compared to ThreadLocal: it's bound once per scope instead of mutable anywhere. Its lifetime is the enclosing block. Cleanup is automatic, even on exceptions. "
             "And because the value can't change, child tasks share it instead of copying it. That's what makes it viable at a million threads.",
         ]),

    dict(title="Request context, four layers deep",
         kicker="Worked example",
         body=code('''
public static RequestContext current() {
    return CURRENT.orElseThrow(() -> new IllegalStateException("no request context bound"));
}

ScopedValue.where(Context.CURRENT, ctx)
           .run(() -> orderService.confirm(cartFrom(exchange)));     // handler

TenantId tenant = Context.current().tenant();                        // repository, four layers down''',
                   title="RequestHandler.java", size=25)
              + frag(table(["API", "Purpose"], [
                    ["`where(key, v).run(...)` / `.call(...)`", "Execute with the binding"],
                    ["`get()`", "Read — **throws** if unbound, never null"],
                    ["`isBound()`, `orElse(d)`, `orElseThrow(...)`", "Test or fall back"],
                ], cls="sm"), 1),
         narration=[
             "Here's request context in practice. The handler binds the context and runs the order service. Four layers down, the repository reads the tenant. "
             "No finally, no remove, and nothing in between carries a parameter it doesn't use.",
             "That's essentially the whole API. where, then run or call. get reads the value, and throws if it's unbound, so it's never null. And isBound, orElse and orElseThrow for testing and fallbacks. There's deliberately no set.",
         ]),

    dict(title="Rebinding and subtasks",
         kicker="Worked examples",
         body=code('''
ScopedValue.where(Context.CURRENT, system).run(() -> {
    for (TenantId tenant : allTenants()) {
        ScopedValue.where(Context.CURRENT, system.withTenant(tenant))
                   .run(() -> reconcile(tenant));          // shadows — outer restored on exit
    }
});''', title="Rebinding.java", size=25)
              + code('''
ScopedValue.where(Context.CURRENT, ctx).run(() -> {
    try (var scope = StructuredTaskScope.open(Joiner.<Object>allSuccessfulOrThrow())) {
        scope.fork(() -> inventory.statusFor(cart));      // sees CURRENT — nothing copied
        scope.fork(() -> pricingEngine.snapshot(cart));   // sees CURRENT
        scope.join();
    }
});''', title="WithStructuredConcurrency.java", step=1, size=25),
         narration=[
             "Rebinding shadows instead of mutating. A nightly job binds a system context, then for each tenant binds a narrower one for that iteration. "
             "When the inner run returns, the outer binding is back. With ThreadLocal that's save, set, and restore in a finally.",
             "And it's designed to fit structured concurrency. Every subtask forked inside the scope reads the same binding. Nothing is copied, because the value is immutable, so all three share one reference.",
         ]),

    dict(title="Migrating — and what stays",
         kicker="ThreadLocal → ScopedValue",
         body=table(["`ThreadLocal`", "`ScopedValue`"], [
                    ["`set(v)` + `try` / `finally` + `remove()`", "`where(KEY, v).run(...)`"],
                    ["`get()` returning null", "`get()` throwing, or `orElse(default)`"],
                    ["`get() != null`", "`isBound()`"],
                    ["`InheritableThreadLocal`", "Automatic inheritance into subtasks"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">Not replaceable: anything written <b>more than once</b> per request — like a reusable per-thread buffer. '
                     'That\'s mutable state, and on virtual threads it needs rethinking anyway.</p>', 4),
         narration=[
             "Migration is mechanical where a ThreadLocal is set once per request. Set, try, finally, remove becomes where, then run.",
             "get returning null becomes get throwing, or orElse with a default.",
             "Checking for null becomes isBound.",
             "And InheritableThreadLocal becomes automatic inheritance into subtasks.",
             "What doesn't map is anything written more than once during a request, like a reusable per-thread buffer. That's mutable per-thread state, which ScopedValue deliberately can't express. "
             "And on virtual threads, a buffer per thread needs rethinking anyway.",
         ]),

    dict(title="Internals",
         kicker="Why one leaks and one can't",
         body='<div class="grid2">'
              + card("ThreadLocalMap", "Weak keys, **strong values**. When the key is collected, the value lingers — pinning whole classloaders after a redeploy.", "fuchsia", 0)
              + card("Binding chain", "A small immutable node pushed on entry, popped on exit. **No cleanup possible or needed**; reads are cached, near field-access cost.", "indigo", 1)
              + "</div>"
              + frag('<p class="callout">Final in Java 25 (JEP 506). Samples with <code>ScopedValue.callWhere</code> or a three-argument <code>where</code> are from old previews.</p>', 2),
         narration=[
             "Why does one leak and the other can't? Each thread holds a ThreadLocalMap with weak keys and strong values. When the ThreadLocal itself becomes unreachable, the key is collected but the value lingers until the map happens to clean up. "
             "On an idle pooled thread, that's forever. That's how one ThreadLocal pins a whole classloader after a hot redeploy.",
             "A scoped binding is a small immutable node pushed when run is entered and popped when it exits, tied to that stack frame. It can't outlive the frame, so there's nothing to clean up. "
             "And reads are cached, approaching the cost of a field access.",
             "It's final in Java 25. Samples using callWhere, or a three-argument where, are from earlier previews and won't compile.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`ScopedValue` for request context on Java 25+",
                         "Keys `static final`; values immutable records",
                         "`orElseThrow` with a clear message",
                         "Rebind to narrow, never to mutate",
                         "Pair with structured concurrency"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`ThreadLocal` for context without `remove()` in `finally`",
                         "Mutable objects as scoped values",
                         "`InheritableThreadLocal` with virtual threads",
                         "Per-thread caches of large objects"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use ScopedValue for request context on Java 25. Keep keys static final, and values immutable, ideally records. Use orElseThrow with a clear message. "
             "Rebind to narrow the context, never to mutate it. And pair it with structured concurrency.",
             "Never use ThreadLocal for context without remove in a finally. Never bind mutable objects, which defeats the point. Avoid InheritableThreadLocal with virtual threads. "
             "And never keep per-thread caches of large objects.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 33 · Scoped Values",
         body=bullets(["Bound for a **block**, then gone — no `remove`, no leaks",
                       "**Immutable**: callees can't change what the caller bound",
                       "Subtasks **share** the binding — no copying",
                       "`ThreadLocal` remains for genuinely mutable per-thread state",
                       "Next: **Runtime · Ch 34 · Garbage Collection**"], cls="bullets recap"),
         narration=[
             "To recap. A scoped value is bound for a block, then gone, so there's no remove and no leak. It's immutable, so callees can't change what the caller bound. "
             "Subtasks share the binding without copying. And ThreadLocal remains only for genuinely mutable per-thread state.",
             "That completes the concurrency section. Next, the runtime section, starting with chapter thirty-four: garbage collection. Thanks for watching.",
         ]),
]
