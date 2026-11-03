import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/** Problem: return the first character in a string that occurs exactly once. */
public class FirstNonRepeating {

    // Approach 1: two passes over an int[] histogram. O(n) time, O(1) extra space for a fixed alphabet.
    static Optional<Character> withArray(String s) {
        int[] counts = new int[Character.MAX_VALUE + 1];
        for (char c : s.toCharArray()) counts[c]++;
        for (char c : s.toCharArray()) if (counts[c] == 1) return Optional.of(c);
        return Optional.empty();
    }

    // Approach 2: LinkedHashMap keeps insertion order, so the first entry with count 1 is the answer.
    static Optional<Character> withStreams(String s) {
        Map<Character, Long> counts = s.chars()
                .mapToObj(c -> (char) c)
                .collect(Collectors.groupingBy(Function.identity(), LinkedHashMap::new, Collectors.counting()));
        return counts.entrySet().stream().filter(e -> e.getValue() == 1).map(Map.Entry::getKey).findFirst();
    }

    public static void main(String[] args) {
        String[] inputs = {"swiss", "aabbcc", "programming", "x", ""};
        for (String in : inputs) {
            var a = withArray(in);
            var b = withStreams(in);
            System.out.printf("%-12s -> %s%n", '"' + in + '"', a.map(String::valueOf).orElse("none"));
            check(a.equals(b), "both approaches agree for " + in);
        }
        check(withArray("swiss").orElseThrow() == 'w', "swiss -> w");
        check(withArray("aabbcc").isEmpty(), "no unique char");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
