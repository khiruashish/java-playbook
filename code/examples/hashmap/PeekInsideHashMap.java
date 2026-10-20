// run: --add-opens java.base/java.util=ALL-UNNAMED
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

/** Look inside a real HashMap: the bucket array, where each key landed, and a resize happening. */
public class PeekInsideHashMap {

    public static void main(String[] args) throws Exception {
        Map<String, Integer> stock = new HashMap<>();
        System.out.println("new HashMap<>()  -> table is " + table(stock) + "  (allocated lazily on the first put)");

        for (int i = 1; i <= 13; i++) {
            stock.put("SKU-" + i, i);
            if (i == 1 || i == 12 || i == 13) {
                System.out.printf("after %2d puts    -> capacity %d, threshold %d%n",
                                  i, table(stock).length, intField(stock, "threshold"));
            }
        }
        System.out.println("\nThe 13th put crossed the threshold (16 x 0.75 = 12), so the table doubled to 32.\n");
        printBuckets(stock);
    }

    static Object[] table(Map<?, ?> map) throws Exception {
        Field f = HashMap.class.getDeclaredField("table");
        f.setAccessible(true);
        return (Object[]) f.get(map);
    }

    static int intField(Map<?, ?> map, String name) throws Exception {
        Field f = HashMap.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.getInt(map);
    }

    static void printBuckets(Map<?, ?> map) throws Exception {
        Object[] tab = table(map);
        for (int i = 0; i < tab.length; i++) {
            StringBuilder chain = new StringBuilder();
            for (Object node = tab[i]; node != null; node = field(node, "next")) {
                chain.append(chain.isEmpty() ? "" : " -> ").append(field(node, "key"));
            }
            if (!chain.isEmpty()) System.out.printf("bucket %2d: %s%n", i, chain);
        }
    }

    static Object field(Object node, String name) throws Exception {
        for (Class<?> c = node.getClass(); c != null; c = c.getSuperclass()) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(node);
            } catch (NoSuchFieldException ignored) { }
        }
        throw new NoSuchFieldException(name);
    }
}
