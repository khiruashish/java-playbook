import java.util.*;

/** Java 9: List.of, Set.of, Map.of — compact, immutable, null-hostile. */
public class J09_CollectionFactories {

    public static void main(String[] args) {
        List<String> skus = List.of("MILK", "RICE", "TEA");
        Map<String, Integer> prices = Map.of("MILK", 60, "RICE", 450);
        Map<String, Integer> many = Map.ofEntries(Map.entry("TEA", 120), Map.entry("DAL", 140));
        System.out.println(skus + "  " + new TreeMap<>(prices) + "  " + new TreeMap<>(many));

        try { skus.add("JAM"); } catch (UnsupportedOperationException e) { System.out.println("add()  -> UnsupportedOperationException (immutable)"); }
        try { List.of("MILK", null); } catch (NullPointerException e) { System.out.println("null   -> NullPointerException"); }
        try { Set.of("MILK", "MILK"); } catch (IllegalArgumentException e) { System.out.println("dup    -> IllegalArgumentException: " + e.getMessage()); }
        try { skus.contains(null); } catch (NullPointerException e) { System.out.println("contains(null) -> NullPointerException, not false"); }
    }
}
