"""Chapter 02 — JVM Runtime Model. Source: docs/01-platform/02-jvm-runtime-model.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 02 · The JVM Runtime Model"
SECTION = "Platform"

SLIDES = [
    dict(kind="title",
         title="The JVM Runtime Model",
         kicker="Platform · Chapter 02",
         body='<p class="sub">Where memory really goes, how classes load, and why the JIT makes the first thousand iterations lie.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter two: the JVM runtime model.",
             "You can write Java for years without a model of the runtime underneath it. Then a container gets killed with a healthy-looking heap, or a benchmark lies to you, and you need one.",
         ]),

    dict(title="Three failures, one root cause",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("OOMKilled", "`-Xmx2g` in a **2 GB** container. Heap peaked at 1.8 GB. Exit code 137 anyway.", "fuchsia", 0)
              + card("Two errors", "`ClassNotFoundException` and `NoClassDefFoundError` look the same. **They aren't.**", "amber", 1)
              + card("A lying benchmark", "Iteration 1: **1,240 ms**. Iteration 10,000: **8 ms**. Same code, same data.", "cyan", 2)
              + "</div>",
         narration=[
             "Three failures with the same root cause. First, a container killed with exit code one thirty-seven. The heap was capped at two gigabytes in a two gigabyte container, and it never went above one point eight. The kernel killed it anyway, because the heap is not the process.",
             "Second, two errors that look the same and aren't: ClassNotFoundException, and NoClassDefFoundError.",
             "And third, a benchmark where the same code on the same data gets a hundred and fifty times faster. Nothing changed, except how many times the JVM had watched it run.",
         ]),

    dict(title="-Xmx bounds the heap, not the process",
         kicker="Mental model · runtime data areas",
         body=table(["Region", "Holds", "Sized by", "Failure"], [
                    ["**Heap**", "Objects and arrays", "`-Xmx`", "`OOM: Java heap space`"],
                    ["Metaspace", "Class metadata", "**Unbounded** by default", "`OOM: Metaspace`"],
                    ["Thread stacks", "Frames and locals", "`-Xss` × threads", "`StackOverflowError`"],
                    ["Code cache", "JIT machine code", "`ReservedCodeCacheSize`", "**Silent** slowdown"],
                    ["Direct memory", "Direct buffers, FFM", "`MaxDirectMemorySize`", "`OOM: Direct buffer`"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">Footprint = heap + metaspace + code cache + threads × stack + direct buffers + the JVM itself.</p>', 5),
         narration=[
             "Here are the JVM's memory regions. The heap holds every object and array, and it's the only thing minus X M X controls.",
             "Metaspace holds class metadata, in native memory, and it's unbounded by default.",
             "Every thread has its own stack, about a megabyte each.",
             "The code cache holds JIT-compiled machine code. When it fills, nothing crashes. The application just gets slower, silently.",
             "And direct memory holds direct byte buffers and foreign memory segments.",
             "So the single most useful fact in this chapter: the heap flag bounds the heap, not the process. The real footprint is all of these added together, plus the JVM's own structures.",
         ]),

    dict(title="Sizing a container",
         kicker="Worked example",
         body='<div class="grid2 start">'
              + table(["Component", "Typical"], [
                    ["Heap", "2048 MB"], ["Metaspace", "100–250 MB"], ["Code cache", "50–250 MB"],
                    ["200 threads × 1 MB", "200 MB"], ["JVM internals, GC", "100–200 MB"],
                    ["**Total**", "**~2.6 GB in 2 GB**"]], cls="sm")
              + '<div>'
              + code('''
# WRONG — heap equals the limit
java -Xmx2g -jar orders.jar

# BETTER — size against the cgroup
java -XX:MaxRAMPercentage=70 \\
     -jar orders.jar''', lang="bash", title="docker run -m 2g …", step=1, size=23)
              + frag(code('''
java -XX:NativeMemoryTracking=summary …
jcmd <pid> VM.native_memory summary''', lang="bash", title="Where did it go?", size=23), 2)
              + '</div></div>',
         narration=[
             "Add it up for that two gigabyte container. Two gigabytes of heap, plus metaspace, code cache, two hundred thread stacks, and the JVM's own structures. Around two point six gigabytes, in a two gigabyte container.",
             "Instead, let the JVM size itself. Container support has been on by default since Java 10, so the JVM reads the cgroup limit. MaxRAMPercentage of about seventy leaves room for everything outside the heap. Then tune with measurements.",
             "To see where native memory goes, turn on native memory tracking and ask jcmd for a summary. The gap between the heap and the total is what your container sizing has to cover.",
         ]),

    dict(title="Load, link, initialise",
         kicker="Class loading",
         body=flow(["LOAD · read bytes", "VERIFY", "PREPARE · static defaults", "RESOLVE · lazily", "INITIALISE · static init runs"])
              + frag(table(["", "`ClassNotFoundException`", "`NoClassDefFoundError`"], [
                    ["Raised by", "`Class.forName`, `loadClass`", "The JVM while linking"],
                    ["Means", "An explicit lookup failed", "Present at compile time, unusable now"],
                    ["Typical cause", "Wrong name, missing driver JAR", "Missing dependency — **or a failed static initialiser**"],
                ], cls="sm"), 1),
         narration=[
             "Every class goes through the same pipeline. It's loaded, verified, prepared, resolved, and finally initialised, when its static initialisers run. Initialisation is lazy: it happens on first use, not at startup.",
             "Which explains the two errors. ClassNotFoundException is a checked exception from an explicit lookup like Class dot forName. NoClassDefFoundError comes from the JVM itself: the class existed at compile time but can't be used now. "
             "Usually that's a missing dependency. But it can also mean the class's static initialiser failed.",
         ]),

    dict(title="The static initialiser trap",
         kicker="Worked example",
         body=code('''
public final class ConfigHolder {
    private static final Config CONFIG = loadOrThrow();   // throws if the file is missing
}''', title="ConfigHolder.java", size=25)
              + code('''
# First use — the real error
java.lang.ExceptionInInitializerError
Caused by: java.nio.file.NoSuchFileException: /etc/orders/config.yaml

# Every use after that — useless
java.lang.NoClassDefFoundError: Could not initialize class ConfigHolder''', lang="text", title="orders.log", step=1, size=23)
              + frag('<p class="callout">See <code>Could not initialize class X</code>? Search <b>backwards</b> for the first <code>ExceptionInInitializerError</code>.</p>', 2),
         narration=[
             "Here's the trap that wastes hours. A class loads its config in a static field initialiser, and the file is missing in this environment.",
             "The first use throws ExceptionInInitializerError, with the real cause. But the class is now marked erroneous, permanently. Every use after that reports only NoClassDefFoundError: could not initialise class.",
             "So when you see that message, search backwards in the log for the first ExceptionInInitializerError. That's where the cause is. And don't do heavy work in static initialisers.",
         ]),

    dict(title="Class identity = name + loader",
         kicker="Delegation",
         body=flow(["Application loader · classpath", "Platform loader · java.sql", "Bootstrap loader · java.base"])
              + frag('<p class="callout">Parent-first: you can\'t shadow <code>java.lang.String</code>, and two copies of a JAR resolve to whichever is found first — JAR hell.</p>', 1)
              + code('''
ClassCastException: class com.grocery.Order cannot be cast to class com.grocery.Order
  (… loader 'app'; … loader 'plugin')''', lang="text", step=2, size=23),
         narration=[
             "Class loaders form a hierarchy. Your application loader, the platform loader, and the bootstrap loader that holds java dot base. Each one asks its parent first.",
             "Parent-first delegation is why you can't shadow java dot lang dot String with your own. And it's why two copies of a library on the classpath resolve to whichever the application loader finds first: the classic JAR hell.",
             "A class's identity is its name plus its loader. The same bytes loaded by two loaders are two different classes. So Order can't be cast to Order. Baffling until you know the rule, obvious afterwards.",
         ]),

    dict(title="Tiered compilation",
         kicker="Why benchmarks lie",
         body=flow(["Interpreter", "C1 · ~200 calls · adds profiling", "C2 · ~10,000 calls · aggressive"])
              + frag('<p class="callout">C2 optimises on <b>assumptions</b> — one implementation, a branch never taken. '
                     'Violate one and the code is discarded: <b>deoptimisation</b>.</p>', 1)
              + frag(code('''
1234  856 %  4  com.grocery.PricingEngine::evaluate @ 12 (86 bytes)
1890  856 %  4  com.grocery.PricingEngine::evaluate @ -2 (86 bytes)   made not entrant''',
                          lang="text", title="-XX:+PrintCompilation", size=22), 2)
              + frag('<p class="callout">No warmup, wrong measurement. That\'s why <b>JMH</b> exists.</p>', 3),
         narration=[
             "Now the lying benchmark. Code starts in the interpreter. After a few hundred calls, the C1 compiler produces quick, lightly optimised code with profiling counters. After about ten thousand, C2 produces the fast version.",
             "C2 optimises using assumptions from that profile. That a call site only ever sees one implementation, or a branch is never taken. If an assumption is later violated, the compiled code is thrown away, and execution falls back. That's deoptimisation.",
             "You can watch it happen with PrintCompilation. Tier four is C2, and made not entrant means deoptimised. If one method keeps cycling through that, something on its call path keeps breaking the JIT's assumptions.",
             "So any benchmark without a warmup phase measures the interpreter. That's why JMH exists.",
         ]),

    dict(title="Quiet costs",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Metaspace", "Freed when a **class loader** is unreachable. Hot redeploys leak it. Cap it with `MaxMetaspaceSize`.", "indigo", 0)
              + card("Escape analysis", "A short-lived `Optional` or wrapper often **isn't allocated at all**. Measure before \"avoiding allocation\".", "cyan", 1)
              + card("Object layout", "Header 12 bytes — **8 with compact headers** in Java 25. Keep heaps under **32 GB** for compressed oops.", "amber", 2)
              + "</div>",
         narration=[
             "A few quiet costs. Metaspace is reclaimed only when a whole class loader becomes unreachable. One lingering reference keeps every class that loader defined alive, which is the classic redeploy leak. So cap metaspace and fail fast.",
             "Escape analysis cuts the other way. If an object never leaves a method, the JIT may never allocate it. A short-lived Optional often costs nothing, so avoid-allocation advice needs measurement, not assumption.",
             "And object layout. Every object has a header: twelve bytes, or eight with Java 25's compact object headers. References are four bytes thanks to compressed oops, which only works up to about a thirty-two gigabyte heap.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Size containers for the **whole process**",
                         "`MaxRAMPercentage`, not a fixed `-Xmx`",
                         "Cap metaspace; dump heap on OOM",
                         "NMT where footprint matters",
                         "`jcmd` as the one diagnostic tool",
                         "Warm up before measuring"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`-Xmx` equal to the container limit",
                         "Raise `-Xss` before checking recursion",
                         "Assume `NoClassDefFoundError` = missing JAR",
                         "Ignore \"CodeCache is full\"",
                         "Heavy work in a static initialiser"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Size containers for the whole process, using MaxRAMPercentage rather than a fixed heap. Cap metaspace, and dump the heap on out-of-memory. Turn on native memory tracking where footprint matters. Use jcmd as your single diagnostic entry point. And warm up before you measure.",
             "Never set the heap equal to the container limit. Never raise the stack size before confirming the recursion is bounded. Never assume NoClassDefFoundError means a missing JAR. Never ignore code cache is full. And never do heavy work in a static initialiser.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 02 · The JVM Runtime Model",
         body=bullets(["`-Xmx` bounds the **heap**, not the process",
                       "A failed static init poisons the class **forever**",
                       "Class identity = name **+ loader**",
                       "Interpreter → C1 → C2, and back on deopt",
                       "Next: **Ch 03 · The Toolchain**"], cls="bullets recap"),
         narration=[
             "To recap. The heap flag bounds the heap, not the process, so size containers for everything. A failed static initialiser poisons its class for good, so read the first error. A class's identity is its name plus its loader. "
             "And code moves from interpreter to C1 to C2, and back again on deoptimisation, which is why benchmarks need warmup.",
             "Next is chapter three: the toolchain. Thanks for watching.",
         ]),
]
