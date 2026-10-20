import java.util.*;

/** The Map methods Java 8 added — they replace most get/check/put boilerplate. */
public class J8_09_MapApi {

    public static void main(String[] args) {
        Map<String, Integer> stock = new TreeMap<>(Map.of("MILK", 40, "RICE", 12));

        System.out.println("getOrDefault(JAM, 0)    = " + stock.getOrDefault("JAM", 0));
        stock.putIfAbsent("TEA", 25);
        stock.putIfAbsent("MILK", 999);                       // ignored: MILK exists
        System.out.println("after putIfAbsent       = " + stock);

        stock.merge("RICE", 5, Integer::sum);                 // add to existing
        stock.merge("DAL", 5, Integer::sum);                  // or insert
        System.out.println("after merge             = " + stock);

        stock.computeIfPresent("TEA", (k, v) -> v - 25 == 0 ? null : v - 25);   // null removes
        System.out.println("computeIfPresent -> null= " + stock);

        Map<String, List<String>> ordersByCustomer = new TreeMap<>();
        ordersByCustomer.computeIfAbsent("asha", k -> new ArrayList<>()).add("O1");
        ordersByCustomer.computeIfAbsent("asha", k -> new ArrayList<>()).add("O2");
        ordersByCustomer.computeIfAbsent("ravi", k -> new ArrayList<>()).add("O3");
        System.out.println("computeIfAbsent (multimap) = " + ordersByCustomer);

        stock.replaceAll((sku, qty) -> qty * 2);
        stock.forEach((sku, qty) -> System.out.print(sku + "=" + qty + " "));
        System.out.println();
    }
}
