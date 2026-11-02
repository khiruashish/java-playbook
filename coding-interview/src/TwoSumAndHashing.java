import java.util.*;

/** Problem set: Two Sum, first duplicate, longest substring without repeats: the "use a HashMap" family. */
public class TwoSumAndHashing {

    /** One pass: for each x, have we already seen target - x? O(n) time, O(n) space (brute force is O(n^2)). */
    static Optional<int[]> twoSum(int[] nums, int target) {
        Map<Integer, Integer> indexOf = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            Integer j = indexOf.get(target - nums[i]);
            if (j != null) return Optional.of(new int[]{j, i});
            indexOf.put(nums[i], i);
        }
        return Optional.empty();
    }

    /** Set.add returns false when the element was already present. */
    static OptionalInt firstDuplicate(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        for (int n : nums) if (!seen.add(n)) return OptionalInt.of(n);
        return OptionalInt.empty();
    }

    /** Sliding window: map each char to its last index; jump the window start past a repeat. O(n). */
    static int longestUniqueSubstring(String s) {
        Map<Character, Integer> last = new HashMap<>();
        int best = 0, start = 0;
        for (int end = 0; end < s.length(); end++) {
            char c = s.charAt(end);
            Integer prev = last.put(c, end);
            if (prev != null && prev >= start) start = prev + 1;
            best = Math.max(best, end - start + 1);
        }
        return best;
    }

    public static void main(String[] args) {
        int[] nums = {2, 7, 11, 15};
        System.out.println("twoSum([2,7,11,15], 9) = " + twoSum(nums, 9).map(Arrays::toString).orElse("none"));
        System.out.println("twoSum([3,3], 6)       = " + twoSum(new int[]{3, 3}, 6).map(Arrays::toString).orElse("none"));
        System.out.println("twoSum([1,2], 7)       = " + twoSum(new int[]{1, 2}, 7).map(Arrays::toString).orElse("none"));
        check(Arrays.equals(twoSum(nums, 9).orElseThrow(), new int[]{0, 1}), "two sum");
        check(Arrays.equals(twoSum(new int[]{3, 3}, 6).orElseThrow(), new int[]{0, 1}), "same value twice");

        System.out.println("firstDuplicate([4,1,3,1,4]) = " + firstDuplicate(new int[]{4, 1, 3, 1, 4}).getAsInt());
        check(firstDuplicate(new int[]{4, 1, 3, 1, 4}).getAsInt() == 1, "first duplicate is the first REPEAT");

        for (String s : new String[]{"abcabcbb", "bbbbb", "pwwkew", "abba", ""}) {
            System.out.printf("longestUnique(%-10s) = %d%n", '"' + s + '"', longestUniqueSubstring(s));
        }
        check(longestUniqueSubstring("abba") == 2, "window start never moves backwards");
        check(longestUniqueSubstring("pwwkew") == 3, "pwwkew");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
