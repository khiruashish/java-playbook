"""Chapter 34 — Garbage Collection. Source: docs/05-runtime/34-garbage-collection.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 34 · Garbage Collection"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="Garbage Collection",
         kicker="Runtime · Chapter 34",
         body='<p class="sub">Choose the collector, set the heap and a pause target, and measure. Almost everything else is automatic — or a mistake.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-four, the start of the runtime section: garbage collection.",
             "GC is the part of the JVM most surrounded by folklore. Flags get copied between projects for years after the collector they configured was removed. "
             "The modern reality is simpler: choose the right collector, set the heap size and a pause target, and measure.",
         ]),

    dict(title="Three things called \"a GC problem\"",
         kicker="The problem",
         body=code('''
p50:   12 ms     p99:  840 ms     p999: 2,100 ms        ← 1. latency spikes

[45.2s] GC(412) Pause Full 3890M->3878M(4096M) 8420ms   ← 2. gradual death
java.lang.OutOfMemoryError: GC overhead limit exceeded

"The upgrade made it slower"  — default changed Parallel → G1 in Java 9   ← 3.''', lang="text", title="Symptoms", size=25),
         narration=[
             "Three symptoms all get called a GC problem. Latency spikes at the ninety-ninth percentile, when unlucky requests land during a pause. "
             "Gradual death, where full collections run back to back, each reclaiming almost nothing, until GC overhead limit exceeded. "
             "And the upgrade made it slower, because Java 9 switched the default collector from Parallel to G1, and that workload preferred throughput.",
         ]),

    dict(title="Pick two of three",
         kicker="Mental model",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Throughput", "Total work done.\n**Parallel**: highest throughput, longest pauses.", "indigo", 0)
              + card("Latency", "Pause length.\n**ZGC / Shenandoah**: sub-millisecond pauses, more CPU and memory.", "cyan", 0)
              + card("Footprint", "Memory overhead.\n**Serial**: smallest, single-threaded.", "amber", 0)
              + "</div>"
              + frag('<p class="callout"><b>Most objects die young.</b> A young collection costs in proportion to the <b>survivors</b>, '
                     'not the garbage — so lots of short-lived allocation is cheap, and medium-lived objects are what hurt.</p>', 1),
         narration=[
             "Every collector trades three things: throughput, latency, and memory footprint. You can optimise for two. Parallel maximises throughput, with long pauses. "
             "ZGC and Shenandoah minimise pauses, at the cost of some CPU and memory. Serial minimises footprint. G1 is the default because it sits in the middle.",
             "And collection works because most objects die young. A young collection copies out the few survivors, so its cost depends on survivors, not on garbage. "
             "That's why a high rate of short-lived allocation is far cheaper than it sounds, while medium-lived objects can be much worse.",
         ]),

    dict(title="The collectors",
         kicker="Core reference",
         body=table(["Collector", "Pause", "Best for"], [
                    ["**Serial**", "Long", "Tiny heaps, single core, CLI tools"],
                    ["**Parallel**", "Long", "Batch and throughput-bound jobs"],
                    ["**G1** (default since 9)", "~10–200 ms", "Most services"],
                    ["**ZGC** (generational since 21)", "**< 1 ms**", "Large heaps, latency-critical"],
                    ["**Shenandoah** (generational in 25)", "< 10 ms", "Latency-critical, mid-size heaps"],
                ], step_per_row=0, cls="sm"),
         narration=[
             "The collectors. Serial: long pauses, but smallest overhead, for tiny heaps and command-line tools.",
             "Parallel: long pauses, but the highest throughput, for batch jobs.",
             "G1, the default since Java 9: predictable pauses of roughly ten to two hundred milliseconds. Right for most services.",
             "ZGC: pauses under a millisecond, regardless of heap size, generational since Java 21. For large heaps and latency-critical work.",
             "And Shenandoah, also very low pause, generational since Java 25. Between ZGC and Shenandoah, measure both.",
         ]),

    dict(title="What to set — and what not to",
         kicker="Configuration",
         body=code('''
java -XX:MaxRAMPercentage=70 \\
     -XX:MaxGCPauseMillis=200 \\
     -Xlog:gc*:file=/var/log/gc.log:time,uptime:filecount=5,filesize=20M \\
     -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/ \\
     -jar orders.jar''', lang="bash", title="The honest default", size=25)
              + frag(table(["Don't set", "Why"], [
                    ["`NewRatio`, `SurvivorRatio`", "G1 sizes generations adaptively"],
                    ["`UseConcMarkSweepGC`", "CMS removed in Java 14 — the JVM won't start"],
                    ["`MaxPermSize`", "PermGen is gone"],
                    ["Flags copied from a blog", "Often older than your collector"],
                ], cls="sm"), 1),
         narration=[
             "Here's the honest default. Size the heap as seventy percent of the container's memory. Set a pause target. Always log GC, with rotation. And dump the heap on out of memory. Then change nothing else until a measurement tells you to.",
             "And what not to set. Don't fix generation ratios under G1, because it sizes them adaptively. Don't enable CMS, which was removed in Java 14, so the JVM won't even start. "
             "PermGen flags are dead too. And never paste a block of flags from a blog, which often configures a collector older than yours.",
         ]),

    dict(title="Reading a GC log",
         kicker="Worked example",
         body=code('''
[12.345s][info][gc] GC(42) Pause Young (Normal) (G1 Evacuation Pause) 512M->48M(2048M) 14.221ms
#   uptime                type                    cause              before→after(capacity) pause''',
                   lang="text", title="Anatomy", size=24)
              + code('''
GC(8842) Pause Young 1840M->1612M(2048M) 412ms     ← live set climbing, pauses over target
GC(8843) Pause Young 1900M->1698M(2048M) 448ms        → heap too small for the live set
GC(8844) Pause Young 1950M->1801M(2048M) 502ms''', lang="text", title="Unhealthy", step=1, size=24)
              + code('''
GC(101) Pause Young 2048M->24M(4096M) 8ms         ← frequent, but reclaims 2 GB in 8 ms
GC(102) Pause Young 2048M->26M(4096M) 8ms            → healthy''', lang="text", title="Healthy", step=2, size=24),
         narration=[
             "Reading a GC log line: uptime, collection type, cause, heap before and after, capacity, and the pause. Look first at the size after collection, the live set. Then the pause distribution, frequency, and any full pause.",
             "Here's a problem. Pauses of four to five hundred milliseconds against a two-hundred target, and the live set climbing after each collection. The diagnosis isn't slow GC. It's a heap too small for the live set. "
             "Find out why the live set is so large with a heap dump, then raise the heap. Adding flags would change nothing.",
             "And here's healthy. Collections every few hundred milliseconds, but each reclaims two gigabytes in eight milliseconds. Almost everything dies young. Frequency alone means nothing.",
         ]),

    dict(title="Two specific failures",
         kicker="Worked examples",
         body='<div class="grid2">'
              + card("Humongous allocation", "In G1, an object over **half a region** goes straight to contiguous old regions — fragmentation and full GCs. Stream or chunk instead.", "fuchsia", 0)
              + card("GC overhead limit exceeded", ">98% of time collecting, <2% reclaimed. Not a GC failure — a **leak or undersized heap**.", "amber", 1)
              + "</div>"
              + frag(code('''
jcmd <pid> GC.heap_dump /var/log/heap.hprof
jcmd <pid> GC.class_histogram | head -20     # usually names the culprit''', lang="bash", title="Diagnose", size=25), 1),
         narration=[
             "Two specific failures. Humongous allocations: in G1, an object larger than half a region goes straight into contiguous old regions, causing fragmentation and full collections. "
             "The log says G1 Humongous Allocation. Usually the fix is to stream or chunk the data, rather than materialise a big array.",
             "And GC overhead limit exceeded means over ninety-eight percent of time is going to collection, reclaiming under two percent. It's not a GC failure. It's a leak, or an undersized heap. "
             "Take a heap dump, or a class histogram, which usually names the culprit immediately: an unbounded cache, a growing collection, or a ThreadLocal on a pooled thread.",
         ]),

    dict(title="How G1 and ZGC work",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("G1: regions", "Heap split into 1–32 MB regions. Collects the regions with the **most garbage first** — hence the name.", "indigo", 0)
              + card("Pause target = budget", "G1 picks how much to evacuate to fit `MaxGCPauseMillis`. An impossible target means tiny, constant collections.", "cyan", 1)
              + card("ZGC: coloured pointers", "Load barriers fix references lazily as the app touches them, so objects **move while the app runs**. Pauses stop depending on heap size.", "fuchsia", 2)
              + "</div>",
         narration=[
             "Inside G1, the heap is divided into regions of one to thirty-two megabytes. Generations are sets of regions, and G1 collects the regions with the most garbage first. That's the name: garbage first.",
             "The pause target is a budget. G1 chooses how many regions to evacuate to fit it. Set an impossible target, like five milliseconds on a large live set, and you get tiny collections run constantly, with worse throughput.",
             "ZGC stores metadata in spare bits of each pointer, and every reference load passes through a barrier that repairs the reference if the object has moved. "
             "So the application fixes references as it uses them, and ZGC can relocate objects while it runs. Pauses become independent of heap size, for a few percent of throughput.",
         ]),

    dict(title="Allocation is nearly free",
         kicker="Internals",
         body=flow(["`new Order(...)`", "Thread-local allocation buffer", "**Bump a pointer**, return", "TLAB full → new one; Eden full → young GC"], step_start=0)
              + frag('<p class="callout">What\'s expensive is an object that <b>survives</b> — copied, maybe several times, then promoted. '
                     'And <code>System.gc()</code> usually triggers a full collection: the JVM knows better than you when to collect.</p>', 4),
         narration=[
             "Allocation is nearly free. Creating an object,",
             "comes from a thread-local allocation buffer, a chunk of Eden owned by that thread,",
             "so it's usually just a pointer bump and a bounds check. A handful of instructions, with no synchronisation.",
             "When the buffer fills, the thread gets a new one, and when Eden fills, a young collection runs.",
             "So what's expensive isn't allocating. It's an object that survives and gets copied and promoted. And System dot gc usually triggers a full collection, the most expensive thing the JVM can do. Don't call it.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Always log GC, with rotation",
                         "Start with G1; change only on evidence",
                         "Heap via `MaxRAMPercentage`, plus a pause target",
                         "Watch the **live set after GC**",
                         "Heap dump on OOM to a writable volume",
                         "Treat any `Pause Full` under G1 as a signal"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Copy GC flags from a blog",
                         "`UseConcMarkSweepGC` — removed",
                         "Pin `NewRatio` / `SurvivorRatio` under G1",
                         "An unachievable pause target",
                         "Call `System.gc()`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Always log GC, with rotation. Start with G1 and change only on evidence. Set the heap and a pause target. Watch the live set after collection, which reveals leaks. "
             "Dump the heap on out of memory. And treat any full pause under G1 as a signal, not routine.",
             "Never copy GC flags from a blog. Never enable CMS. Never pin generation ratios under G1. Never set an unachievable pause target. And never call System dot gc.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 34 · Garbage Collection",
         body=bullets(["Throughput, latency, footprint — **pick two**",
                       "G1 by default; ZGC when pauses bind; Parallel for batch",
                       "Heap size + pause target + logging — then measure",
                       "The **live set after GC** reveals leaks",
                       "Next: **Ch 35 · Memory Footprint &amp; Object Layout**"], cls="bullets recap"),
         narration=[
             "To recap. Collectors trade throughput, latency and footprint. Use G1 by default, ZGC when pauses are the constraint, and Parallel for batch work. "
             "Set the heap size, a pause target and logging, then measure. And the live set after collection is what reveals a leak.",
             "Next is chapter thirty-five: memory footprint and object layout. Thanks for watching.",
         ]),
]
