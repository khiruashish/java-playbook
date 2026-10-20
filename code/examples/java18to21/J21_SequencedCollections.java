import java.util.*;

/** Java 21: getFirst, getLast, reversed and friends — one vocabulary for every ordered collection. */
public class J21_SequencedCollections {

    public static void main(String[] args) {
        List<String> orders = new ArrayList<>(List.of("O1", "O2", "O3"));
        System.out.println("first " + orders.getFirst() + ", last " + orders.getLast()
                           + "   (was get(0) and get(size() - 1))");

        LinkedHashSet<String> skus = new LinkedHashSet<>(List.of("MILK", "RICE", "TEA"));
        System.out.println("LinkedHashSet last: " + skus.getLast() + "   (used to need a full loop)");

        List<String> reversed = orders.reversed();              // a VIEW, not a copy
        orders.add("O4");
        System.out.println("reversed view sees the new order: " + reversed);

        LinkedHashMap<String, Integer> recent = new LinkedHashMap<>();
        for (String sku : List.of("MILK", "RICE", "TEA")) recent.putLast(sku, 1);
        recent.putFirst("RICE", 2);                              // moves RICE to the front
        System.out.println("putFirst moves an existing key: " + recent);
        System.out.println("pollLastEntry: " + recent.pollLastEntry() + ", remaining " + recent);

        Map<String, Integer> plain = new HashMap<>();
        System.out.println("HashMap is a SequencedMap? " + (plain instanceof SequencedMap)
                           + "  (no defined order, so no first or last)");
    }
}
