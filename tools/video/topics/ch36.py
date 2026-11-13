"""Chapter 36 — Startup & Project Leyden. Source: docs/05-runtime/36-startup-and-leyden.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 36 · Startup & Project Leyden"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="Startup &amp; Project Leyden",
         kicker="Runtime · Chapter 36",
         body='<p class="sub">Where the seconds before the first request go, what CDS, the AOT cache, native image and CRaC each buy — '
              'and when startup isn\'t worth optimising at all.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-six: startup and Project Leyden.",
             "Java's slow start was fine when a JVM ran for months. It stopped being fine when JVMs started launching per autoscaling event, per CI job, and per serverless call.",
         ]),

    dict(title="Startup vs warmup",
         kicker="The problem",
         body=code('''
[0.000s] JVM starts
[2.400s] classes loaded and linked        ← 12,000 classes
[3.300s] first request served             ← STARTUP
[  ...  ] interpreted, then C1
[38.0s ] peak throughput reached          ← WARMUP''', lang="text", title="A typical service", size=26)
              + frag(table(["Deployment shape", "What hurts"], [
                    ["Long-running, rare restarts", "Neither — skip this chapter"],
                    ["Autoscaling under bursts", "Both — new instances slow when most needed"],
                    ["Serverless / scale-to-zero", "Startup dominates"],
                    ["30-second batch jobs", "Warmup never finishes"],
                ], cls="sm"), 1),
         narration=[
             "There are two separate numbers that get conflated. Startup: three point three seconds to the first request. Warmup: another thirty-five seconds to peak throughput, while the JIT profiles and compiles.",
             "Which one hurts depends on how you deploy. A long-running service with rare restarts? Neither. Skip this chapter. Autoscaling under bursts? Both, because new instances are slow exactly when you need them. "
             "Serverless is dominated by startup. And a thirty-second batch job never finishes warming up, so it runs interpreted.",
         ]),

    dict(title="Each fix targets a phase",
         kicker="Mental model",
         body=table(["Phase", "Dominated by", "Mitigated by"], [
                    ["Class loading + verification", "Thousands of classes parsed and verified", "**CDS**"],
                    ["Linking + initialisation", "Constant-pool resolution", "**AOT cache**"],
                    ["Interpreted → C1 → C2", "Waiting for invocation counts", "**AOT method profiles**"],
                    ["All of it", "—", "Native image · CRaC"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">CDS and the AOT cache change <b>nothing</b> about how your app behaves. Native image changes the execution model.</p>', 4),
         narration=[
             "Each mitigation targets a different phase. Class loading and verification, reading and checking thousands of classes, is attacked by class data sharing.",
             "Linking and initialisation is attacked by the AOT cache from Project Leyden.",
             "The slow climb from interpreter to compiled code is attacked by recorded method profiles.",
             "And native image and CRaC attack all of it, in very different ways.",
             "The key asymmetry: CDS and the AOT cache change nothing about how your application behaves. Native image changes the execution model itself.",
         ]),

    dict(title="Measure first",
         kicker="Worked example",
         body=code('''
java -Xlog:startuptime -jar orders.jar

[0.187s] Initializing VM                     187 ms
[2.401s] Loading classes                   2,214 ms      ← the target
[3.102s] Application initialization          701 ms''', lang="text", title="Where does the time go?", size=27)
              + frag('<p class="callout">Class loading dominates → CDS and the AOT cache help. <b>App initialisation</b> dominates — building caches, '
                     'scanning the classpath, opening pools → no JVM feature helps; the work is in your code.</p>', 1),
         narration=[
             "Before choosing anything, measure which phase dominates. Here, loading classes is over two seconds of a three-second startup.",
             "If class loading dominates, CDS and the AOT cache are the answer. If application initialisation dominates, like building caches, scanning the classpath or opening connection pools, no JVM feature helps. The work is in your application.",
         ]),

    dict(title="AppCDS, the easy win",
         kicker="Worked example",
         body=code('''
java -XX:+AutoCreateSharedArchive \\
     -XX:SharedArchiveFile=/var/cache/orders.jsa \\
     -jar orders.jar            # first run writes it; later runs use it; stale → regenerated''',
                   lang="bash", title="Java 19+", size=25)
              + code('''
FROM eclipse-temurin:25-jre AS builder
COPY orders.jar /app/orders.jar
RUN java -XX:ArchiveClassesAtExit=/app/orders.jsa -jar /app/orders.jar --exit-after-startup
FROM eclipse-temurin:25-jre
COPY --from=builder /app/orders.jar /app/orders.jsa /app/
ENTRYPOINT ["java", "-XX:SharedArchiveFile=/app/orders.jsa", "-jar", "/app/orders.jar"]''',
                     lang="docker", title="Dockerfile — build the archive into the image", step=1, size=23),
         narration=[
             "Class data sharing stores classes pre-parsed and pre-verified, memory-mapped straight into the JVM. JDK classes are shared by default since Java 12. "
             "For your own classes, since Java 19, one flag creates the archive on first run, uses it after, and regenerates it if the jar changes.",
             "In containers, build the archive at image build time so it ships in a layer. It must be built on the same JDK version that uses it, so a base image bump invalidates it. Another reason to build it inside the image.",
         ]),

    dict(title="The AOT cache",
         kicker="Project Leyden · Java 24–25",
         body=code('''
# 1. Training run — exercise a REAL path, not just startup
java -XX:AOTMode=record -XX:AOTConfiguration=orders.aotconf -jar orders.jar --run-smoke-test

# 2. Build the cache
java -XX:AOTMode=create -XX:AOTConfiguration=orders.aotconf -XX:AOTCache=orders.aot -jar orders.jar

# 3. Production
java -XX:AOTCache=orders.aot -jar orders.jar''', lang="bash", title="Three steps", size=24)
              + frag('<p class="callout">Classes pre-loaded <b>and</b> pre-linked; with Java 25\'s method profiling, the JIT starts from recorded profiles. '
                     'Invalidated by any JDK, classpath or app change — build it in CI.</p>', 1),
         narration=[
             "The AOT cache goes further. First, a training run records what was actually loaded and linked. The training run is what matters: one that only starts and exits captures nothing about the request path, so run a real smoke test. "
             "Second, build the cache. Third, run with it in production.",
             "Classes come pre-loaded and pre-linked. And with Java 25's method profiling, the cache also carries JIT profile data, so the compiler can skip straight to higher tiers. That attacks warmup, not just startup. "
             "Any JDK, classpath or application change invalidates it, so build it in CI as part of the artifact.",
         ]),

    dict(title="Native image, CRaC, short-lived JVMs",
         kicker="The other options",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Native image", "Starts in **milliseconds**. But lower peak throughput, slow builds, and a **closed world**: reflection and proxies must be declared.", "fuchsia", 0)
              + card("CRaC", "Snapshot a warm JVM, restore it already at peak. Skips startup **and** warmup — but sockets and pools need close/reopen hooks.", "cyan", 1)
              + card("Seconds-long JVMs", "`-XX:TieredStopAtLevel=1 -XX:+UseSerialGC` — skip C2. Right for CLIs and CI steps; **wrong** for services.", "amber", 2)
              + "</div>",
         narration=[
             "The other options. Native image starts in milliseconds and uses less memory. But peak throughput is usually lower, builds take minutes, and it's a closed world: anything found at runtime, like reflection or dynamic proxies, must be declared at build time. "
             "Choose it when startup is the product requirement, like serverless or command-line tools. Not to save a few seconds on a long-running service.",
             "CRaC, checkpoint and restore, snapshots a warmed-up JVM and restores it later, already at peak. It's the only option that skips both startup and warmup. "
             "The cost is coordination: open files, sockets and pools can't survive a snapshot, so you need hooks to close and reopen them.",
             "And for a JVM that lives a few seconds, stop at the C1 compiler and use Serial GC. Right for CLI tools and CI steps, clearly wrong for a long-running service.",
         ]),

    dict(title="How to decide",
         kicker="Decision",
         body=table(["Need", "Choose"], [
                    ["Startup doesn't matter (weekly deploys)", "**Nothing** — most services stop here"],
                    ["20–50% faster, cheaply", "AppCDS + AOT cache"],
                    ["Milliseconds; startup is the product", "Native image"],
                    ["Milliseconds **and** full peak throughput", "CRaC"],
                    ["Process lives seconds", "`TieredStopAtLevel=1`"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "So how do you decide? First: does startup actually matter? For a service restarted during a weekly deploy, no. Do nothing. That's the branch most often skipped.",
             "For a cheap twenty to fifty percent improvement, use AppCDS and the AOT cache.",
             "If startup in milliseconds is the product requirement, native image.",
             "If you need milliseconds and full peak throughput, CRaC.",
             "And for processes that live only seconds, stop at C1.",
         ]),

    dict(title="Why the JIT can't just compile everything",
         kicker="Internals",
         body='<div class="grid2">'
              + card("Verification is the cost", "Proving bytecode type-safe is a dataflow analysis per method. CDS stores classes **already verified**, so loading becomes memory-mapping.", "indigo", 0)
              + card("C2 needs runtime profiles", "Which branch is taken, which implementation a call site sees. Compiling blind loses devirtualisation and inlining — hence **recorded** profiles.", "cyan", 1)
              + "</div>",
         narration=[
             "Two internals. Class loading is slow mostly because of verification: proving each method's bytecode is type-safe is a real dataflow analysis, and with twelve thousand classes that's seconds. "
             "CDS stores classes already verified, so loading becomes memory-mapping.",
             "And why not just compile everything ahead of time? Because C2's best optimisations depend on runtime profiles: which branch is taken, which implementation a call site actually sees. "
             "Compile blind and you lose devirtualisation and the inlining that follows. That's why native image trades peak throughput, and why recording real profiles, as Leyden does, is the more promising path.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Ask first whether startup matters",
                         "Measure with `-Xlog:startuptime`",
                         "AppCDS with auto-create — nearly free",
                         "Build archives and AOT caches in CI / the image",
                         "Train the AOT cache on a real request path"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Native image for a long-running service \"to be faster\"",
                         "Reuse an archive across JDK versions",
                         "`TieredStopAtLevel=1` on a service",
                         "Optimise JVM startup when app init dominates"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. First ask whether startup matters. Measure with the startup time log. Use AppCDS with auto-create, which is nearly free. Build archives and AOT caches in CI or the image, never by hand on a server. "
             "And train the AOT cache on a real request path.",
             "Never move a long-running service to native image just to start faster. Never reuse an archive across JDK versions. Never stop at C1 on a service. And don't tune JVM startup when your own initialisation is what dominates.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 36 · Startup &amp; Leyden",
         body=bullets(["**Startup** (first request) ≠ **warmup** (peak throughput)",
                       "CDS and the AOT cache: faster, same behaviour",
                       "Native image: milliseconds, but a closed world and lower peak",
                       "CRaC skips both — with coordination",
                       "Next: **Ch 37 · Profiling &amp; JFR**"], cls="bullets recap"),
         narration=[
             "To recap. Startup and warmup are different numbers. CDS and the AOT cache make startup faster without changing behaviour. Native image starts in milliseconds, at the cost of a closed world and lower peak throughput. "
             "And CRaC skips both startup and warmup, with some coordination.",
             "Next is chapter thirty-seven: profiling and Java Flight Recorder. Thanks for watching.",
         ]),
]
