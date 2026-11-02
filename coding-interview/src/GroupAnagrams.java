import java.util.*;
import java.util.stream.Collectors;

/** Problem: group words that are anagrams of each other. ["eat","tea","tan","ate","nat","bat"]. */
public class GroupAnagrams {

    // Key = the word's letters sorted. O(n * k log k) for n words of length k.
    static Collection<List<String>> bySortedKey(List<String> words) {
        Map<String, List<String>> groups = new LinkedHashMap<>();
        for (String w : words) {
            char[] letters = w.toCharArray();
            Arrays.sort(letters);
            groups.computeIfAbsent(new String(letters), k -> new ArrayList<>()).add(w);
        }
        return groups.values();
    }

    // Key = a 26-letter count signature. O(n * k), better for long words.
    static Collection<List<String>> byCountKey(List<String> words) {
        return words.stream().collect(Collectors.groupingBy(w -> {
            int[] counts = new int[26];
            for (char c : w.toCharArray()) counts[c - 'a']++;
            return Arrays.toString(counts);
        }, LinkedHashMap::new, Collectors.toList())).values();
    }

    public static void main(String[] args) {
        List<String> words = List.of("eat", "tea", "tan", "ate", "nat", "bat");
        Collection<List<String>> a = bySortedKey(words);
        Collection<List<String>> b = byCountKey(words);
        System.out.println("sorted-key groups: " + a);
        System.out.println("count-key groups : " + b);
        check(new ArrayList<>(a).equals(new ArrayList<>(b)), "both keys give the same groups");
        check(a.size() == 3, "three groups");
        check(a.contains(List.of("eat", "tea", "ate")), "eat/tea/ate grouped");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
