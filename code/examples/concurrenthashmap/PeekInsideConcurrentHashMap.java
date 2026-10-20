// run: --add-opens java.base/java.util.concurrent=ALL-UNNAMED
import java.lang.reflect.Field;
import java.util.concurrent.ConcurrentHashMap;

/** Look inside a real ConcurrentHashMap: lazy table, sizeCtl as the resize threshold, and a resize. */
public class PeekInsideConcurrentHashMap {

    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
        System.out.println("new ConcurrentHashMap<>() -> table is " + get(map, "table") + ", sizeCtl " + get(map, "sizeCtl"));
        for (int i = 1; i <= 13; i++) {
            map.put("SKU-" + i, i);
            if (i == 1 || i == 12 || i == 13) {
                Object[] tab = (Object[]) get(map, "table");
                System.out.printf("after %2d puts -> capacity %d, sizeCtl (next resize at) %s%n", i, tab.length, get(map, "sizeCtl"));
            }
        }
        System.out.println("\nSame shape as HashMap — an array of bins — but each bin is locked separately,");
        System.out.println("empty bins are filled with a CAS (no lock), and resizing is shared between threads.");
    }

    static Object get(ConcurrentHashMap<?, ?> m, String name) throws Exception {
        Field f = ConcurrentHashMap.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(m);
    }
}
