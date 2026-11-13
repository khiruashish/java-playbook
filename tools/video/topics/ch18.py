"""Chapter 18 — List Internals & CustomArrayList. Source: docs/03-collections/18-list-internals.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 18 · List Internals & CustomArrayList"
SECTION = "Collections"

SLIDES = [
    dict(kind="title",
         title="List Internals &amp; CustomArrayList",
         kicker="Collections · Chapter 18",
         body='<p class="sub">How <code>ArrayList</code> grows, why <code>LinkedList</code> loses the benchmarks it should win, '
              'and the view types that bite.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter eighteen: list internals.",
             "List is the collection you reach for without thinking. That reflex is usually right, and occasionally expensive. "
             "Let's look at how ArrayList really grows, why LinkedList loses benchmarks it should win on paper, and which list-like views will bite you.",
         ]),

    dict(title="Contiguous vs scattered",
         kicker="Mental model",
         body='<div class="grid2">'
              + card("ArrayList", "One array of references in **one block** of memory. Walking it streams through CPU cache lines.", "indigo", 0)
              + card("LinkedList", "One `Node` object per element, **anywhere on the heap**. Every step is a potential cache miss.", "fuchsia", 1)
              + "</div>"
              + frag(table(["1M elements", "Overhead", "Locality"], [
                    ["`ArrayList`", "~5 MB", "Contiguous; prefetcher-friendly"],
                    ["`LinkedList`", "~24 MB", "1M scattered objects"],
                ], cls="sm"), 2)
              + frag('<p class="callout">Use <code>ArrayList</code> by default and <code>ArrayDeque</code> for queues. '
                     '<code>LinkedList</code> almost never.</p>', 3),
         narration=[
             "The distinction that predicts performance isn't array versus nodes. It's contiguous versus scattered. "
             "An ArrayList keeps its element references in one block of memory, so walking it streams cleanly through the CPU cache.",
             "A LinkedList allocates a separate Node object for every element, scattered across the heap. Every step can be a cache miss.",
             "For a million elements, that's around five megabytes of overhead for ArrayList, and around twenty-four for LinkedList, spread over a million objects.",
             "So LinkedList loses even where the complexity table says it should win. Use ArrayList by default, ArrayDeque for queues and stacks, and LinkedList almost never.",
         ]),

    dict(title="How ArrayList grows",
         kicker="Internals",
         body=code('''
transient Object[] elementData;   // the backing store
private int size;                 // elements in use, <= elementData.length

int newCapacity = oldCapacity + (oldCapacity >> 1);   // grow by 1.5×''', title="java.util.ArrayList", size=27)
              + frag('<div class="pipeline"><span>10</span>→<span>15</span>→<span>22</span>→<span>33</span>→<span>49</span>→<span>73</span>→<span>109</span>→<span>…</span></div>', 1)
              + frag('<p class="callout">Reaching 1,000 elements: <b>12 grow copies</b>. <code>new ArrayList&lt;&gt;(1000)</code>: <b>zero</b>. '
                     'And <code>new ArrayList&lt;&gt;(0)</code> grows 0 → 1 → 2 → 3 — the worst profile.</p>', 2),
         narration=[
             "Inside, ArrayList is just an array and a size. A default ArrayList doesn't even allocate until the first add. It shares a static empty array, so empty lists are nearly free. "
             "When it fills up, it grows by one and a half times.",
             "So capacity walks ten, fifteen, twenty-two, thirty-three, and so on. One and a half wastes less memory than doubling, and lets the allocator reuse earlier blocks.",
             "Reaching a thousand elements takes twelve grow-and-copy operations. Sizing it up front takes zero. "
             "And a trap: passing zero to save memory gives the worst growth profile of all. Zero, one, two, three.",
         ]),

    dict(title="O(n) insert is cheaper than it sounds",
         kicker="Internals",
         body=code('''
System.arraycopy(elementData, index, elementData, index + 1, size - index);   // one bulk move
elementData[index] = element;
size++;''', title="ArrayList.add(int, E)", size=26)
              + bullets(["`System.arraycopy` is a JIT **intrinsic** — a vectorised memory move, not a loop",
                         "Removal nulls the vacated slot for GC — but the array **never shrinks** (`trimToSize()`)",
                         "Every structural change bumps `modCount`; iterators check it — **fail-fast**, best-effort"], start_step=1, cls="bullets sm"),
         narration=[
             "Inserting in the middle is O of n, but that's misleading. It's a single System dot arraycopy.",
             "And arraycopy is a JIT intrinsic, compiled to a vectorised memory move. Shifting ten thousand references takes microseconds, "
             "which often beats a LinkedList that first has to walk to the right position.",
             "Removal nulls out the vacated slot so the element can be collected. But the array itself never shrinks. A list that peaked at a million entries keeps that array until you call trimToSize.",
             "And every structural change increments a modCount field. Iterators compare it on each step and throw ConcurrentModificationException if it changed. "
             "That's best-effort bug detection, not a guarantee. Set doesn't count as structural, which is why replacing elements during iteration is fine.",
         ]),

    dict(title="Filter in one pass",
         kicker="Worked example",
         body='<div class="grid2 start">'
              + code('''
lines.removeIf(line ->
    catalogue.availableQuantity(line.sku()) == 0);''', title="✓ Single pass", size=25)
              + frag(code('''
for (CartLine line : lines) {
    if (catalogue.availableQuantity(
            line.sku()) == 0) {
        lines.remove(line);   // CME
    }
}''', title="✗ O(n²) and a ConcurrentModificationException", size=25), 1)
              + "</div>"
              + frag('<p class="callout"><code>removeIf</code> marks doomed indices in a bit set, then compacts the array in one copy.</p>', 2),
         narration=[
             "To remove every out-of-stock line, use removeIf. One pass.",
             "The loop version calls remove inside a for-each. It shifts the tail on every removal, which is quadratic, and it breaks the iterator with a ConcurrentModificationException besides.",
             "removeIf marks the doomed indices in a bit set, then compacts the array in a single copy.",
         ]),

    dict(title="Three traps",
         kicker="Worked examples",
         body=code('''
List<Order> firstTen = allOrders.subList(0, 10);   // a VIEW: pins the parent's whole array
allOrders = null;                                   // 200 MB stays reachable
lines.add(newLine); window.size();                  // parent changed → ConcurrentModificationException''',
                   title="1 · subList is a live view", size=24)
              + code('''
List<Integer> qty = new ArrayList<>(List.of(10, 20, 30));
qty.remove(1);                     // remove(int index)  → removes 20
qty.remove(Integer.valueOf(10));   // remove(Object)     → removes 10''', title="2 · The remove overload", step=1, size=24)
              + code('''
List<String> skus = Arrays.asList("MILK-1L", "RICE-5KG");
skus.set(0, "MILK-2L");   // works — writes through to the array
skus.add("ATTA-10KG");    // UnsupportedOperationException''', title="3 · Arrays.asList is fixed-size", step=2, size=24),
         narration=[
             "Three traps. First, subList returns a live view that holds a reference to its parent. Store ten elements from a million-element list, and the whole backing array stays reachable. "
             "And any structural change to the parent breaks the view. Treat subList as short-lived, and copy it if it escapes the method.",
             "Second, the remove overload. On a list of Integer, remove with an int literal removes by index, not by value. "
             "To remove the value, box it explicitly. This is the most common List bug in code that stores Integers.",
             "Third, Arrays dot asList isn't an ArrayList. It's a fixed-size view over the array. Set works, but add and remove throw.",
         ]),

    dict(title="Copies vs views",
         kicker="What you get back",
         body=table(["Expression", "Mutable?", "Nulls?", "Kind"], [
                    ["`new ArrayList<>(c)`", "Yes", "Yes", "Copy"],
                    ["`List.of(...)` / `List.copyOf(c)`", "No", "**No**", "Immutable"],
                    ["`stream.toList()` (16)", "No", "Yes", "Unmodifiable"],
                    ["`Arrays.asList(...)`", "`set` only", "Yes", "**View** over array"],
                    ["`Collections.unmodifiableList(l)`", "No", "Yes", "**View** — sees later changes"],
                    ["`subList` / `reversed()` (21)", "Yes", "Yes", "**Live view**"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">From an accessor, return <code>List.copyOf(lines)</code> — a snapshot, not a window into your state.</p>', 1),
         narration=[
             "Here's the whole family in one table. A new ArrayList is a mutable copy. List dot of and copyOf are immutable and reject nulls. Stream dot toList is unmodifiable but allows nulls. "
             "Arrays dot asList, unmodifiableList, subList and Java 21's reversed are all views, connected to the original.",
             "So from an accessor, return List dot copyOf. A view stops callers writing, but still leaks your later changes into their reference.",
         ]),

    dict(title="Build your own: CustomArrayList",
         kicker="The interview exercise",
         body=code('''
public void add(int index, E element) {
    rangeCheckForAdd(index);                 // index == size is legal (append)
    ensureCapacity(size + 1);
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    elementData[index] = element;
    size++;
}

public E remove(int index) {
    rangeCheck(index);                       // index == size is NOT legal
    E old = (E) elementData[index];
    System.arraycopy(elementData, index + 1, elementData, index, size - index - 1);
    elementData[--size] = null;              // let GC reclaim it
    return old;
}

private void grow(int min) {
    int cap = Math.max(elementData.length + (elementData.length >> 1), min);
    elementData = Arrays.copyOf(elementData, cap == 0 ? 10 : cap);
}''', title="CustomArrayList.java", size=23),
         narration=[
             "Writing your own ArrayList is a standard interview exercise, and the quickest way to understand the real one. The key points: capacity is not size. "
             "There are two range checks. Inserting at size is a legal append, but reading at size isn't. Removal shifts the tail and nulls the vacated slot for the garbage collector. "
             "And grow uses the same one-and-a-half factor, with a fallback for zero capacity.",
         ]),

    dict(title="What the real ArrayList adds",
         kicker="What interviewers probe",
         body=table(["Feature", "Why it matters"], [
                    ["Implements `List<E>`, `RandomAccess`", "Works with the ecosystem; algorithms branch on the marker"],
                    ["Fail-fast iterators via `modCount`", "Detects concurrent modification"],
                    ["`subList`, `ListIterator`, `Spliterator`", "Views, bidirectional cursors, parallel streams"],
                    ["`removeIf` with a bit set", "Single-pass bulk removal"],
                    ["Custom `writeObject`", "`elementData` is `transient` — serializes only `size` elements"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "Here's what separates I wrote a dynamic array from I understand the JDK class. The real one implements List and RandomAccess, so the whole ecosystem works with it.",
             "Its iterators are fail-fast, using modCount.",
             "It has subList views, bidirectional list iterators, and a spliterator for parallel streams.",
             "removeIf uses a bit set for a single-pass removal.",
             "And a nice detail: elementData is transient, with a hand-written writeObject that serializes only the elements in use, not the empty tail of the array.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Size the list when the count is known",
                         "Default to `ArrayList`; `ArrayDeque` for queues",
                         "`removeIf` for conditional removal",
                         "Return `List.copyOf(...)` from accessors",
                         "Prefer `stream.toList()` (16)",
                         "`trimToSize()` on lists that shrank for good"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Store a `subList`",
                         "`remove(int)` on `List<Integer>` without deciding",
                         "Index a `LinkedList` in a counted loop",
                         "Treat `Arrays.asList` as mutable",
                         "Assume `unmodifiableList` is a snapshot",
                         "Share a `List` across threads unsynchronised"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Size the list when you know the count. Default to ArrayList, and ArrayDeque for queues. Use removeIf for conditional removal. "
             "Return List dot copyOf from accessors. Prefer stream dot toList. And trim lists that shrank for good.",
             "Never store a subList. Never call remove with an int on a list of Integer without deciding which overload you mean. Never index a LinkedList in a counted loop. "
             "Don't treat Arrays dot asList as mutable, or unmodifiableList as a snapshot. And never share a list across threads without synchronisation.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 18 · List Internals",
         body=bullets(["**Contiguous beats scattered** — `ArrayList` by default",
                       "Grows 1.5× — size it when you know the count",
                       "`arraycopy` makes \"O(n)\" inserts cheap in practice",
                       "`subList`, `Arrays.asList`, `unmodifiableList` are **views**",
                       "Next: **Ch 19 · HashMap Internals**"], cls="bullets recap"),
         narration=[
             "To recap. Contiguous memory beats scattered nodes, so use ArrayList by default. It grows by one and a half times, so size it when you know the count. "
             "arraycopy makes O of n inserts cheap in practice. And subList, Arrays dot asList and unmodifiableList are views, not copies.",
             "Next is chapter nineteen, HashMap internals. Thanks for watching.",
         ]),
]
