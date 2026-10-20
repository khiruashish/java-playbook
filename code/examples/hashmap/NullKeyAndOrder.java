import java.util.*;

/** One null key is allowed (it lives in bucket 0), and HashMap iteration order is not insertion order. */
public class NullKeyAndOrder {

    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put(null, 0);
        map.put(null, 1);                                  // same key — replaces
        System.out.println("null key -> " + map.get(null) + ", size " + map.size());

        List<String> inserted = List.of("TEA", "OIL", "SALT", "RICE", "MILK", "ATTA", "DAL");
        Map<String, Integer> hash = new HashMap<>(), linked = new LinkedHashMap<>(), tree = new TreeMap<>();
        for (String s : inserted) { hash.put(s, 1); linked.put(s, 1); tree.put(s, 1); }

        System.out.println("\ninserted:      " + inserted);
        System.out.println("HashMap:       " + hash.keySet() + "   <- bucket order, not insertion order");
        System.out.println("LinkedHashMap: " + linked.keySet() + "   <- insertion order");
        System.out.println("TreeMap:       " + tree.keySet() + "   <- sorted");
    }
}
