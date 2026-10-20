import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** HashMap iterators are fail-fast; ConcurrentHashMap iterators are weakly consistent and never throw. */
public class IterationWhileModifying {

    public static void main(String[] args) {
        Map<String, Integer> hashMap = new HashMap<>(Map.of("MILK", 1, "RICE", 2, "DAL", 3));
        try {
            for (String sku : hashMap.keySet()) hashMap.put(sku + "-NEW", 0);
        } catch (ConcurrentModificationException e) {
            System.out.println("HashMap:           ConcurrentModificationException");
        }

        Map<String, Integer> chm = new ConcurrentHashMap<>(Map.of("MILK", 1, "RICE", 2, "DAL", 3));
        int visited = 0;
        for (String sku : chm.keySet()) {
            if (!sku.endsWith("-NEW")) chm.put(sku + "-NEW", 0);
            visited++;
        }
        System.out.println("ConcurrentHashMap: no exception; visited " + visited + " keys, map now has " + chm.size());
        System.out.println("                   (keys added during iteration may or may not be seen — 'weakly consistent')");
    }
}
