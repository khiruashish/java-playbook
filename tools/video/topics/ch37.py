"""Chapter 37 — Profiling & JFR. Source: docs/05-runtime/37-profiling-jfr.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 37 · Profiling & JFR"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="Profiling &amp; JFR",
         kicker="Runtime · Chapter 37",
         body='<p class="sub">A profiler built into the JVM, cheap enough to leave running — so you capture the incident, not the aftermath.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-seven: profiling with Java Flight Recorder.",
             "Most performance problems can't be reproduced locally. The data, the load and the heap are different. Flight Recorder is a profiler built into the JVM, cheap enough to leave running, so it records what actually happened.",
         ]),

    dict(title="It already recovered",
         kicker="The problem",
         body=code('''
14:02  p99 latency 2.4s (normally 45ms)
14:09  recovered on its own
14:11  "can you look into it?"''', lang="text", title="The incident", size=30)
              + bullets(["**Reproduce locally?** Different load and data",
                         "**Add logging?** Nothing until it happens again",
                         "**Attach a profiler?** You had to be attached at 14:02",
                         "**What's needed:** a recording that was **already running**"], start_step=1, cls="bullets sm"),
         narration=[
             "Here's the classic incident. Latency spiked to two point four seconds at two minutes past two, recovered on its own by nine past, and at eleven past someone asks you to look into it. "
             "You have graphs showing that it happened, logs showing nothing unusual, and a service now behaving normally.",
             "Reproducing locally won't work, because the load and data are different.",
             "Adding logging gives you nothing until it happens again, maybe next month.",
             "Attaching a profiler means being attached when it happened.",
             "What you need is a recording that was already running, detailed enough to answer questions you hadn't thought to ask yet.",
         ]),

    dict(title="An event recorder, not a bolted-on sampler",
         kicker="Mental model",
         body=flow(["JVM and JDK emit events at instrumented points", "Per-thread buffers — **lock-free**", "Global buffer", "Disk repository of `.jfr` chunks"], step_start=0)
              + frag('<p class="callout"><b>~1% overhead</b> with the default profile. And it records <b>semantics</b>: not just "in a socket read", '
                     'but which socket, which address, how long — with the stack.</p>', 4),
         narration=[
             "The JVM and JDK libraries are already instrumented with hundreds of event types: GC phases, lock contention, socket reads, class loading, allocations, exceptions.",
             "JFR writes the enabled ones into per-thread buffers, with no locking.",
             "Full buffers are handed to a global buffer,",
             "and a background thread writes chunks to disk.",
             "So the overhead is about one percent with the default settings. And it records meaning, not just stacks. A sampling profiler says a thread was in a socket read. JFR tells you which socket, to which address, for how long, with the stack.",
         ]),

    dict(title="Always-on recording",
         kicker="Worked example",
         body=code('''
java -XX:StartFlightRecording=settings=default,maxage=6h,maxsize=1g,disk=true,\\
dumponexit=true,filename=/var/log/jfr/exit.jfr \\
     -XX:FlightRecorderOptions=repository=/var/log/jfr \\
     -jar orders.jar

# when the incident happens — the dump holds the 6 hours BEFORE this command
jcmd <pid> JFR.dump name=1 filename=/var/log/jfr/incident-1402.jfr''', lang="bash", title="Continuous recording", size=24)
              + frag(table(["Profile", "Overhead", "Use"], [
                    ["`default`", "~1%", "Continuous production recording"],
                    ["`profile`", "~2%", "Investigation — adds **allocation** events"],
                ], cls="sm"), 1),
         narration=[
             "Here's the configuration every service should have. Start a recording at launch with the default settings, keeping a rolling six-hour window on disk, capped at a gigabyte, and dump on exit. "
             "When an incident happens, JFR dot dump writes out the six hours before the command. That's the whole point. And dump on exit captures the window before a crash.",
             "The default profile costs about one percent. For an investigation, use the profile settings at about two percent. Note that only profile includes allocation events, so default can't answer what is allocating.",
         ]),

    dict(title="Investigating the spike",
         kicker="Worked example",
         body=code('''
$ jfr summary incident-1402.jfr
 jdk.ExecutionSample      48,221
 jdk.JavaMonitorEnter      8,904     ← unusual
 jdk.GarbageCollection        61     ← rules out GC
 jdk.SocketRead            2,104''', lang="text", title="Start with the summary", size=25)
              + code('''
$ jfr print --events JavaMonitorEnter --stack-depth 15 incident-1402.jfr
  monitorClass  = com.grocery.InventoryCache
  previousOwner = "http-nio-8080-exec-42"
  duration      = 1.84 s
  stackTrace    = [ com.grocery.InventoryCache.refreshIfStale line: 88 ... ]''', lang="text", title="Then drill in", step=1, size=25),
         narration=[
             "Start with jfr summary. The event counts usually point at the problem before you look at anything else. Here, nearly nine thousand monitor contention events is the anomaly. And only sixty-one garbage collections in six hours rules GC out immediately.",
             "Then print those events with stacks. The monitor is the InventoryCache, the previous owner is named, each wait lasted nearly two seconds, and here's the exact line. "
             "A synchronized cache refresh was serialising every request thread during a reload. No reproduction, no added logging, no guessing.",
         ]),

    dict(title="Allocation, custom events, pinning",
         kicker="Worked examples",
         body=code('''
jdk.ObjectAllocationSample {  objectClass = byte[]   weight = 412 MB
  stackTrace = [ String.getBytes · AuditLogger.serialise line: 64 · OrderService.confirm ] }
// serialising every order even with audit disabled — the fix is one `if`''', lang="text", title="Allocation (profile settings)", size=23)
              + code('''
@Name("com.grocery.Reservation") @Category({"Grocery", "Inventory"})
public final class ReservationEvent extends jdk.jfr.Event { String sku; int quantity; boolean succeeded; }

event.begin(); try { ... event.succeeded = ok; } finally { event.commit(); }   // ~free when disabled''',
                     title="Your own domain events", step=1, size=23)
              + frag(code('jfr print --events VirtualThreadPinned --stack-depth 20 app.jfr', lang="bash", title="Virtual thread pinning", size=23), 2),
         narration=[
             "With the profile settings, allocation samples show what's allocating. Weight is the total allocated along that path. Here, an audit logger was serialising every order to a string even when audit logging was off. Four hundred megabytes in two minutes. The fix was one if statement.",
             "You can add your own domain events by extending jdk dot jfr dot Event. Begin, do the work, set fields, commit. Then your reservations appear on the same timeline as GC pauses and lock contention. "
             "When the event type is disabled, commit checks a flag and returns, so it's nearly free.",
             "And for virtual threads, the VirtualThreadPinned event finds what's pinning carriers. It supersedes the old trace pinned threads flag.",
         ]),

    dict(title="JFR and its neighbours",
         kicker="Choosing a tool",
         body=table(["Tool", "Strength", "Weakness"], [
                    ["**JFR**", "Always-on, ~1%, rich event semantics", "Java frames only"],
                    ["**async-profiler**", "Wall-clock, native frames, flame graphs", "Separate install"],
                    ["**Thread dump**", "Free, instant", "One moment, no history"],
                    ["**Heap dump**", "Definitive for memory", "Large; pauses the JVM"],
                    ["**APM agent**", "Traces across services", "Higher overhead, less JVM detail"],
                ], step_per_row=0, cls="sm"),
         narration=[
             "JFR is the always-on baseline, low overhead and rich, but it only sees Java frames.",
             "async-profiler adds wall-clock profiling, meaning time spent blocked, not just on CPU, plus native frames and great flame graphs. It can even read JFR files.",
             "A thread dump is free and instant, but shows one moment with no history.",
             "A heap dump is the definitive answer for memory questions, but it's large and pauses the JVM.",
             "And APM agents trace requests across services, at higher overhead with less JVM detail. These complement each other.",
         ]),

    dict(title="Reading without a GUI",
         kicker="Core reference",
         body=code('''
jfr summary app.jfr                                        # event counts — always first
jfr print --events GarbageCollection app.jfr
jfr print --events JavaMonitorEnter --stack-depth 20 app.jfr
jfr print --json --events SocketRead app.jfr | jq '...'

jcmd <pid> JFR.start name=adhoc settings=profile           # on a running JVM
jcmd <pid> JFR.check                                       # active recordings''', lang="bash", title="The jfr CLI", size=25)
              + frag(table(["Question", "Event"], [
                    ["Where is CPU going?", "`ExecutionSample`, `CPUTimeSample` (25)"],
                    ["What is contended?", "`JavaMonitorEnter`, `ThreadPark`"],
                    ["Which calls are slow?", "`SocketRead`, `FileRead`"],
                    ["Is something throwing in a loop?", "`JavaExceptionThrow`"],
                ], cls="sm"), 1),
         narration=[
             "You don't need a GUI. jfr summary first, then jfr print for specific events, with stacks, or as JSON piped into jq. And jcmd can start, dump and check recordings on a running JVM.",
             "Map your question to an event. CPU usage: execution samples, and Java 25's CPU time samples. Contention: monitor enter and thread park. Slow calls: socket and file reads. And exceptions thrown in a loop show up as JavaExceptionThrow.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Continuous JFR on every service — `maxage`, `disk=true`",
                         "`dumponexit` to catch crashes",
                         "`jfr summary` before anything else",
                         "`profile` settings for allocation questions",
                         "Custom events for key domain operations"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Wait for a reproduction",
                         "Expect allocation data from `default`",
                         "Use JFR for native-frame problems — use async-profiler",
                         "Write recordings to ephemeral container storage"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Run continuous JFR on every service, with a max age and disk enabled. Use dump on exit to catch crashes. Run jfr summary before anything else. Use the profile settings for allocation questions. "
             "And add custom events for your key domain operations.",
             "Never wait for a reproduction. Don't expect allocation data from the default settings. Don't use JFR for native-frame problems, which need async-profiler. And don't write recordings to ephemeral container storage, which vanishes with the pod.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 37 · Profiling &amp; JFR",
         body=bullets(["Built in, **~1%** — leave it running",
                       "A rolling window means you dump **the past**",
                       "`jfr summary` first; then drill into the anomaly",
                       "Custom events put your domain on the same timeline",
                       "Next: **Ch 38 · Stream Gatherers**"], cls="bullets recap"),
         narration=[
             "To recap. JFR is built in and costs about one percent, so leave it running. A rolling window means that when something happens, you dump the past. Start with jfr summary, then drill into the anomaly. "
             "And custom events put your domain operations on the same timeline as the JVM's.",
             "Next is chapter thirty-eight: stream gatherers. Thanks for watching.",
         ]),
]
