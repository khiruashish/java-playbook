"""Chapter 39 — FFM & the Vector API. Source: docs/05-runtime/39-ffm-and-vector-api.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 39 · FFM & the Vector API"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="FFM &amp; the Vector API",
         kicker="Runtime · Chapter 39",
         body='<p class="sub">Calling native code and managing off-heap memory safely — and why SIMD from Java is still incubating.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-nine: the foreign function and memory API, and the Vector API.",
             "Java had two long-standing gaps. Calling native code was so painful that people used sun dot misc dot Unsafe instead. And the SIMD instructions in every modern CPU were out of reach. The first gap is now closed. The second is still incubating.",
         ]),

    dict(title="JNI, Unsafe, and invisible SIMD",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("JNI", "A C file, a generated header, a per-platform build. Every mistake is a **JVM crash**, not an exception.", "fuchsia", 0)
              + card("Off-heap", "`allocateDirect`: 2 GB cap, freed whenever the GC gets round to it. `Unsafe`: no bounds, no lifetime — use-after-free crashes.", "amber", 1)
              + card("SIMD", "A CPU can add eight ints in one instruction. Java could only write a loop and **hope** the JIT vectorised it.", "cyan", 2)
              + "</div>",
         narration=[
             "Calling a native library meant JNI: a C file, a generated header, a shared library built per platform, and a build pipeline for all of it. And every mistake was a JVM crash rather than an exception.",
             "Off-heap memory meant a direct ByteBuffer, capped at two gigabytes and freed only when the GC got round to it, or Unsafe, with no bounds checks and no lifetimes. A use-after-free crashed the JVM.",
             "And SIMD was invisible. A CPU can add eight integers in one instruction, but Java could only write a loop and hope the JIT vectorised it.",
         ]),

    dict(title="FFM: safety isn't optional",
         kicker="Mental model · final in Java 22",
         body=table(["Concept", "What it is"], [
                    ["`Arena`", "A lifetime — when memory is freed, and who may touch it"],
                    ["`MemorySegment`", "A bounded region, on or off heap"],
                    ["`MemoryLayout`", "The shape of what's in it — fields, padding, arrays"],
                    ["`VarHandle`", "Typed access with bounds **and** lifetime checks"],
                    ["`Linker`", "Binds a native function to a method handle"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">Every access checks bounds and that the arena is alive — a use-after-free becomes an <b>exception</b>, '
                     'not a corrupted heap. That\'s the real difference from <code>Unsafe</code>.</p>', 5),
         narration=[
             "The foreign function and memory API, final in Java 22, has five concepts. An Arena is a lifetime: when memory is freed and who can touch it.",
             "A MemorySegment is a region with a known size and lifetime, on or off the heap.",
             "A MemoryLayout describes its structure: fields, padding and arrays.",
             "A VarHandle gives typed access derived from the layout, with checks.",
             "And the Linker binds a native function to a Java method handle.",
             "The design point is that safety isn't optional. Every access checks bounds and checks that the arena is still alive. So a use-after-free becomes an exception, not a corrupted heap. That's the real difference from Unsafe.",
         ]),

    dict(title="Off-heap with a deterministic lifetime",
         kicker="Worked example",
         body=code('''
try (Arena arena = Arena.ofConfined()) {
    MemorySegment prices = arena.allocate(ValueLayout.JAVA_LONG, 1_000_000);
    for (int i = 0; i < 1_000_000; i++) prices.setAtIndex(ValueLayout.JAVA_LONG, i, priceOf(i));
    ...
}   // freed HERE — not when the GC decides''', title="OffHeapIndex.java", size=25)
              + code('''
MemorySegment escaped;
try (Arena arena = Arena.ofConfined()) { escaped = arena.allocate(1024); }
escaped.get(ValueLayout.JAVA_INT, 0);     // IllegalStateException: Already closed''', title="UseAfterFree.java", step=1, size=25)
              + frag(table(["Arena", "Freed", "Threads"], [
                    ["`ofConfined()`", "`close()`", "One — the default choice"],
                    ["`ofShared()`", "`close()`", "Any"],
                    ["`ofAuto()`", "GC decides", "Any"],
                ], cls="sm"), 2),
         narration=[
             "Allocate eight megabytes of off-heap longs in a confined arena, inside try-with-resources. They're freed at the closing brace, deterministically, not whenever the GC decides.",
             "And if a segment escapes its arena and you touch it afterwards, you get an IllegalStateException, already closed. With Unsafe, the same mistake corrupts memory or crashes the JVM.",
             "Confined arenas are the default choice: deterministic freeing, and single-thread confinement that makes the lifetime check cheap. Shared arenas allow any thread, and automatic arenas leave freeing to the GC.",
         ]),

    dict(title="Structs and native calls",
         kicker="Worked examples",
         body=code('''
static final MemoryLayout RECORD = MemoryLayout.structLayout(
    ValueLayout.JAVA_LONG.withName("skuId"), ValueLayout.JAVA_INT.withName("available"),
    ValueLayout.JAVA_INT.withName("reserved"), ValueLayout.JAVA_DOUBLE.withName("price"));
static final VarHandle AVAILABLE = RECORD.varHandle(PathElement.groupElement("available"));''',
                   title="StructLayout.java — offsets computed, never hard-coded", size=23)
              + code('''
static final MethodHandle STRLEN = Linker.nativeLinker().downcallHandle(
    Linker.nativeLinker().defaultLookup().find("strlen").orElseThrow(),
    FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));

try (Arena arena = Arena.ofConfined()) { return (long) STRLEN.invokeExact(arena.allocateFrom(s)); }''',
                     title="NativeCall.java — no C file, no header, no build step", step=1, size=23)
              + frag(code('jextract --output src/main/java -t com.grocery.native /usr/include/zlib.h',
                          lang="bash", title="Real libraries: generate bindings from headers", size=23), 2),
         narration=[
             "A C struct is described once as a layout, with named fields. VarHandles then give typed, checked access to each field, with offsets computed from the layout. So adding a field doesn't silently shift every read after it.",
             "Calling native code needs no C file, no generated header and no platform build. Describe the function's signature, look up the symbol, and call it through a method handle. Here, the C library's strlen.",
             "For a real library, jextract reads the C headers and generates all the layouts and handles, removing the most error-prone step: transcribing signatures by hand.",
         ]),

    dict(title="Native access is restricted",
         kicker="Integrity by default",
         body=code('''
java --enable-native-access=ALL-UNNAMED -jar orders.jar
java --enable-native-access=com.grocery.orders -jar orders.jar      # modular''', lang="bash", title="Java 24+ warns without it", size=26)
              + frag(table(["", "`byte[]`", "`allocateDirect`", "`MemorySegment`"], [
                    ["Size limit", "2 GB", "2 GB", "None"],
                    ["Deterministic free", "GC", "**No**", "**Yes**"],
                    ["Struct layouts", "No", "No", "Yes"],
                    ["Native interop", "JNI", "Limited", "First class"],
                ], cls="sm"), 1)
              + frag('<p class="callout">The honest default is still an array. Go off-heap when data is large, long-lived, and GC pressure is <b>measured</b> — or it must be shared with native code.</p>', 2),
         narration=[
             "Native access is a restricted operation. From Java 24, using it without permission prints a warning, and it's heading towards an error. Grant it with enable-native-access. It's the same integrity-by-default direction as the encapsulation changes in chapter eleven.",
             "Compared to the alternatives, memory segments have no two-gigabyte limit, free deterministically, describe struct layouts, and make native interop first class.",
             "But the honest default is still a plain array. Go off-heap only when the data is large, long-lived, and GC pressure is measured to be the problem, or when you must share it with native code.",
         ]),

    dict(title="The Vector API — still incubating",
         kicker="SIMD from Java",
         body=code('''
static final VectorSpecies<Integer> SPECIES = IntVector.SPECIES_PREFERRED;
IntVector acc = IntVector.zero(SPECIES);
int upper = SPECIES.loopBound(values.length);
for (; i < upper; i += SPECIES.length()) {
    acc = acc.add(IntVector.fromArray(SPECIES, values, i));   // 8 ints per instruction on AVX2
}
int total = acc.reduceLanes(VectorOperators.ADD);
for (; i < values.length; i++) total += values[i];            // the tail''', title="VectorSum.java", size=24)
              + frag('<p class="callout">In <code>jdk.incubator.vector</code> since Java 16, waiting on <b>Valhalla</b> value types. '
                     'Incubator APIs will change — keep it behind your own interface, out of shared libraries.</p>', 1),
         narration=[
             "The Vector API makes SIMD explicit. Pick the CPU's preferred vector species, load a vector's worth of integers at a time, add, and reduce the lanes at the end. Then handle the leftover tail with a plain loop. "
             "On AVX2, that's eight integers per instruction.",
             "But it's still in an incubator module, jdk dot incubator dot vector, where it has been since Java 16. It's waiting on Project Valhalla's value types, so vectors don't cost an object each. "
             "Incubator APIs will change, so keep it behind your own interface and out of shared libraries.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["FFM instead of JNI and `Unsafe`",
                         "Confined arenas in try-with-resources",
                         "Layouts + VarHandles, not offset arithmetic",
                         "`jextract` for real libraries",
                         "Grant `--enable-native-access` explicitly"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["New code on `sun.misc.Unsafe`",
                         "Off-heap without a measured reason",
                         "Let segments escape their arena",
                         "Incubator APIs in published libraries"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Use FFM instead of JNI and Unsafe. Use confined arenas in try-with-resources. Describe memory with layouts and VarHandles, not offset arithmetic. Use jextract for real libraries. And grant native access explicitly.",
             "Never write new code on Unsafe. Never go off-heap without a measured reason. Never let segments escape their arena. And never put incubator APIs in published libraries.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 39 · FFM &amp; Vector API",
         body=bullets(["FFM (final in 22) replaces JNI and `Unsafe`",
                       "Arenas give **deterministic** lifetimes; access is checked",
                       "Layouts describe structs; `jextract` generates bindings",
                       "Vector API: explicit SIMD, still **incubating**",
                       "Next: **Ch 40 · The HTTP Client**"], cls="bullets recap"),
         narration=[
             "To recap. The foreign function and memory API, final in Java 22, replaces JNI and Unsafe. Arenas give deterministic lifetimes, and every access is checked. Layouts describe structs, and jextract generates bindings. "
             "And the Vector API makes SIMD explicit, but it's still incubating.",
             "Next is chapter forty, the last in this batch: the HTTP client. Thanks for watching.",
         ]),
]
