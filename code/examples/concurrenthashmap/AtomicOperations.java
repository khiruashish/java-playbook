import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

/** The atomic compound operations — each is ONE call, so no other thread can interleave. */
public class AtomicOperations {

    public static void main(String[] args) {
        ConcurrentHashMap<String, Integer> stock = new ConcurrentHashMap<>();

        // putIfAbsent: insert only if missing; returns the existing value otherwise
        System.out.println("putIfAbsent(MILK, 40) -> " + stock.putIfAbsent("MILK", 40) + "   (was absent)");
        System.out.println("putIfAbsent(MILK, 99) -> " + stock.putIfAbsent("MILK", 99) + "     (kept 40)");

        // merge: the counter idiom — insert 1, or add 1 to what is there
        for (String sku : List.of("RICE", "MILK", "RICE", "DAL", "RICE")) stock.merge(sku, 1, Integer::sum);
        System.out.println("after merges          -> " + new java.util.TreeMap<>(stock));

        // compute: read-modify-write on one key, atomically
        stock.compute("DAL", (sku, qty) -> qty == null ? 10 : qty + 10);
        System.out.println("compute(DAL, +10)     -> DAL=" + stock.get("DAL"));

        // computeIfPresent returning null REMOVES the entry
        stock.computeIfPresent("DAL", (sku, qty) -> qty > 5 ? null : qty);
        System.out.println("computeIfPresent->null-> DAL present? " + stock.containsKey("DAL"));

        // replace(key, expected, new): compare-and-set on a map entry
        System.out.println("replace(RICE, 3, 2)   -> " + stock.replace("RICE", 3, 2) + "  RICE=" + stock.get("RICE"));
        System.out.println("replace(RICE, 3, 1)   -> " + stock.replace("RICE", 3, 1) + " (RICE is 2, not 3)");
    }
}
