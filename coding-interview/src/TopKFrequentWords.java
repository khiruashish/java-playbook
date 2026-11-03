import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/** Problem: return the k most frequent words; ties broken alphabetically. */
public class TopKFrequentWords {

    private static final Comparator<Map.Entry<String, Long>> BY_FREQ_THEN_ALPHA =
            Map.Entry.<String, Long>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey());

    // Approach 1: count, then a size-k min-heap. O(n log k): good when k << distinct words.
    static List<String> withHeap(String text, int k) {
        Map<String, Long> counts = count(text);
        PriorityQueue<Map.Entry<String, Long>> heap = new PriorityQueue<>(BY_FREQ_THEN_ALPHA.reversed()); // worst on top
        for (var e : counts.entrySet()) {
            heap.offer(e);
            if (heap.size() > k) heap.poll();          // drop the current worst
        }
        List<String> result = new ArrayList<>();
        while (!heap.isEmpty()) result.add(heap.poll().getKey());
        Collections.reverse(result);
        return result;
    }

    // Approach 2: count, then sort everything. O(m log m) for m distinct words: simplest to write.
    static List<String> withSort(String text, int k) {
        return count(text).entrySet().stream().sorted(BY_FREQ_THEN_ALPHA).limit(k).map(Map.Entry::getKey).toList();
    }

    static Map<String, Long> count(String text) {
        return Arrays.stream(text.toLowerCase(Locale.ROOT).split("[^a-z']+"))
                .filter(w -> !w.isBlank())
                .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
    }

    public static void main(String[] args) {
        String text = "the quick brown fox jumps over the lazy dog. The dog sleeps; the fox runs. A fox, a dog.";
        System.out.println("counts (sorted) = " + new TreeMap<>(count(text)));
        for (int k : new int[]{1, 3, 5}) {
            List<String> h = withHeap(text, k);
            System.out.println("top " + k + " = " + h);
            check(h.equals(withSort(text, k)), "heap and sort agree for k=" + k);
        }
        check(withHeap(text, 3).equals(List.of("the", "dog", "fox")), "tie dog/fox broken alphabetically");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
