"""Chapter 35 — Memory Footprint & Object Layout. Source: docs/05-runtime/35-memory-footprint.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 35 · Memory Footprint & Object Layout"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="Memory Footprint &amp; Object Layout",
         kicker="Runtime · Chapter 35",
         body='<p class="sub">What an object really costs, where the unexpected memory goes, and what genuinely reduces it.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter thirty-five: memory footprint and object layout.",
             "Java hides memory layout, which is usually a feature. It stops being one when a million small objects take four times the memory you estimated. Let's see where it goes.",
         ]),

    dict(title="50 MB estimated, 216 MB measured",
         kicker="The problem",
         body=code('''
record InventoryItem(Sku sku, int available, int reserved, long priceInPaise) { }
// "4 + 4 + 8 = 16 bytes, plus the Sku. Say 50 MB for a million."''', title="Estimate.java", size=25)
              + code('''
 num   #instances      #bytes  class name
   1:   1,000,000  48,000,000  com.grocery.InventoryItem
   2:   1,000,000  32,000,000  java.util.HashMap$Node
   3:   1,000,000  24,000,000  com.grocery.Sku
   4:   1,000,000  56,000,000  java.lang.String
   5:   1,000,000  40,000,000  [B''', lang="text", title="jcmd <pid> GC.class_histogram", step=1, size=25),
         narration=[
             "The SKU catalogue holds a million entries. The estimate: four plus four plus eight bytes of fields, plus the SKU. Say fifty megabytes.",
             "The class histogram says two hundred and sixteen megabytes. Nothing is wrong. The estimate ignored object headers, references, the map's own nodes, and the fact that a SKU wrapping a String is several objects, not one.",
         ]),

    dict(title="What an object is made of",
         kicker="Mental model",
         body=table(["Component", "Bytes (64-bit, compressed oops)"], [
                    ["Mark word", "8 — hash, lock state, GC age"],
                    ["Class pointer", "4 compressed"],
                    ["**Header total**", "**12 — 8 with compact headers (Java 25)**"],
                    ["Reference field", "4 compressed, 8 otherwise"],
                    ["Alignment", "Round up to a multiple of 8 — minimum object **16**"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout"><b>Object count matters more than field count.</b> Every reference hop is another header, and every map entry adds a node.</p>', 5),
         narration=[
             "Every object starts with a header. An eight-byte mark word, holding the hash, lock state and GC age.",
             "Then a class pointer, four bytes when compressed.",
             "That's twelve bytes of header. Java 25's compact headers make it eight.",
             "Each reference field is four bytes, compressed.",
             "And everything rounds up to a multiple of eight. So even an object with no fields takes sixteen bytes.",
             "Here's the idea that drives every optimisation: object count matters more than field count. Each reference hop adds another header, and each map entry adds a node.",
         ]),

    dict(title="Common sizes",
         kicker="Core reference",
         body=table(["Type", "Bytes"], [
                    ["`new Object()`, `Integer`", "16"],
                    ["`Long`, `Double`", "24"],
                    ["`String` (empty) — String + `byte[]`", "40"],
                    ["`int[n]`, `Object[n]`", "16 + 4n"],
                    ["`HashMap.Node`", "32"],
                    ["`LinkedList.Node`", "24 — **plus the element**"],
                ], step_per_row=None, cls="pairs")
              + frag(code('''
System.out.println(ClassLayout.parseClass(InventoryItem.class).toPrintable());   // JOL
// Instance size: 40 bytes · Space losses: 8 bytes of padding''', title="Measure one object exactly", size=24), 1),
         narration=[
             "Some sizes worth knowing. An Object or an Integer is sixteen bytes. A Long or Double, twenty-four. An empty String is forty, counting its byte array. Arrays are sixteen plus four per element. "
             "A HashMap node is thirty-two, and a LinkedList node is twenty-four, plus the element it points to.",
             "And to measure one object exactly, use JOL, the Java Object Layout library. It shows each field's offset, and the padding. Here, eight of forty bytes are padding.",
         ]),

    dict(title="Accounting for the catalogue",
         kicker="Worked example",
         body=table(["Per entry (Java 21)", "Bytes"], [
                    ["`InventoryItem`", "32"],
                    ["`Sku`", "16"],
                    ["`String` + `byte[]` for a 12-char code", "24 + 32"],
                    ["`HashMap.Node` + table slot", "32 + ~5"],
                    ["**Total**", "**~141** — vs 16 bytes of fields"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "Let's account for one catalogue entry. The InventoryItem record is thirty-two bytes.",
             "The Sku wrapping the code is sixteen.",
             "The String is twenty-four, plus thirty-two for its byte array.",
             "Then the HashMap node, thirty-two, plus about five bytes of table slot.",
             "That's around a hundred and forty-one bytes per entry, against sixteen bytes of actual fields. A nine-times multiplier, entirely headers, references and container overhead.",
         ]),

    dict(title="Remove objects, not fields",
         kicker="Worked examples",
         body=code('''
Map<Integer, Integer> counts = new HashMap<>();     // ~69 MB for 1M entries
int[] countsBySkuIndex = new int[1_000_000];        //   4 MB — same information, 17× smaller''',
                   title="Boxing.java", size=25)
              + frag(table(["Layout", "Objects / entry", "Bytes / entry"], [
                    ["Record graph in a `HashMap`", "5", "~141"],
                    ["Parallel arrays + index", "2", "~90"],
                    ["Arrays with `byte[]`-encoded keys", "~0", "~25"],
                ], cls="sm"), 1)
              + frag('<p class="callout">Flattening is harder to read and change. Do it <b>only when a measurement says footprint is the constraint</b>, '
                     'behind an API that still speaks in domain terms. For numeric maps, try a primitive-collections library first.</p>', 2),
         narration=[
             "Boxing is the most dramatic case. A HashMap of a million Integer keys and values is about sixty-nine megabytes. A plain int array holding the same counts is four. Seventeen times smaller.",
             "The general technique is removing objects, not fields. A record graph in a map is five objects per entry. Parallel arrays with an index get that down to two. Arrays with encoded keys, close to zero.",
             "But flattened data is harder to read and easy to get wrong. Only do it when a measurement says footprint is the constraint, and hide it behind an API that still speaks in domain terms. "
             "For big numeric maps, libraries like fastutil or Eclipse Collections give you primitive maps with no boxing.",
         ]),

    dict(title="Strings and compact headers",
         kicker="Worked examples",
         body='<div class="grid2">'
              + card("Compact strings (Java 9)", "ASCII text uses **one byte per char**, not two — on by default. What remains is **duplication**: try `-XX:+UseStringDeduplication` first.", "indigo", 0)
              + card("Compact headers (Java 25)", "Header 12 → 8 bytes. `HashMap.Node` 32 → 24; the catalogue entry ~141 → ~117. **Re-baseline heap sizing** after upgrading.", "cyan", 1)
              + "</div>",
         narration=[
             "Strings. Since Java 9, compact strings store ASCII text in one byte per character instead of two, roughly halving string memory, with no configuration. "
             "What's left is duplication: a million String objects with far fewer distinct values. Enabling G1 string deduplication costs nothing to try, and the measurement shows straight away whether it helped.",
             "And Java 25's compact object headers cut the header from twelve bytes to eight. A HashMap node drops from thirty-two to twenty-four, and our catalogue entry from about a hundred and forty-one to a hundred and seventeen, with no code change. "
             "So re-baseline your heap sizing after upgrading.",
         ]),

    dict(title="The 32 GB cliff",
         kicker="Internals",
         body=flow(["Heap ≤ ~32 GB\n**32-bit** compressed references", "Heap > ~32 GB\n**64-bit** references — every one doubles", "A 33 GB heap may hold **fewer objects** than 31 GB"], step_start=0)
              + frag(code('jcmd <pid> VM.flags | grep -i compressedoops', lang="bash", title="Check it", size=25), 2)
              + frag('<p class="callout">Past the threshold, scale with <b>more JVMs, not a bigger one</b>. Also: the JVM reorders fields to cut padding; '
                     'source order has no effect.</p>', 2),
         narration=[
             "Compressed references store a thirty-two-bit value scaled by the eight-byte alignment, which addresses thirty-two gigabytes of heap.",
             "Go past that, and every reference doubles to sixty-four bits.",
             "So a thirty-three gigabyte heap can hold fewer objects than a thirty-one gigabyte heap. Check the flag with jcmd. "
             "Past the threshold, the answer is usually more JVMs rather than a bigger one. And note that the JVM reorders fields to minimise padding, so declaration order in your source makes no difference.",
         ]),

    dict(title="Measuring footprint",
         kicker="Tools",
         body=table(["Tool", "Answers"], [
                    ["`jcmd <pid> GC.class_histogram`", "What's on the heap, by class"],
                    ["`jcmd <pid> GC.heap_dump <path>`", "Full dump for offline analysis"],
                    ["**JOL**", "Exact layout of one object"],
                    ["Eclipse MAT", "Retained sizes, dominator tree, leak suspects"],
                    ["`jcmd <pid> VM.native_memory summary`", "Memory **outside** the heap"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "The tools. The class histogram shows what's on the heap, by class.",
             "A heap dump captures everything for offline analysis.",
             "JOL shows the exact layout of a single object.",
             "Eclipse Memory Analyzer shows retained sizes, meaning what would be freed if an object went away, and points at likely leaks.",
             "And native memory tracking shows the memory outside the heap, like metaspace, thread stacks and code cache.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Measure with the histogram and JOL",
                         "Count objects per entry, not fields",
                         "Primitive collections for big numeric maps",
                         "Try string deduplication",
                         "Stay under ~32 GB or scale out",
                         "Re-baseline heap after Java 25"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Estimate memory from field sizes",
                         "Flatten data without a measurement",
                         "`String.intern()` as a casual fix",
                         "A 33 GB heap \"for headroom\"",
                         "Reorder fields to save padding"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Measure with the class histogram and JOL. Count objects per entry, not fields. Use primitive collections for large numeric maps. Try string deduplication. "
             "Stay under thirty-two gigabytes, or scale out. And re-baseline heap sizing after moving to Java 25.",
             "Never estimate memory from field sizes alone. Never flatten data without a measurement. Don't reach for String dot intern casually, since interned strings are effectively permanent. "
             "Never pick a thirty-three gigabyte heap for headroom. And don't reorder fields to save padding, because the JVM already does.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 35 · Memory Footprint",
         body=bullets(["Header 12 bytes (8 on Java 25), aligned to 8, minimum 16",
                       "**Object count** drives footprint — ~9× the field bytes",
                       "Boxing and map nodes are the usual culprits",
                       "Compressed oops end near **32 GB**",
                       "Next: **Ch 36 · Startup &amp; Project Leyden**"], cls="bullets recap"),
         narration=[
             "To recap. An object header is twelve bytes, eight on Java 25, everything aligns to eight, and the minimum object is sixteen. "
             "Object count drives footprint, often nine times the raw field bytes. Boxing and map nodes are the usual culprits. And compressed references end near thirty-two gigabytes.",
             "Next is chapter thirty-six: startup and Project Leyden. Thanks for watching.",
         ]),
]
