// run: --add-opens java.base/java.util=ALL-UNNAMED
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

/** Watch a bucket turn into a red-black tree — and see HashMap resize first when the table is small. */
public class TreeifyDemo {

    /** Every key collides; Comparable lets the tree order them. */
    record SameHash(int id) implements Comparable<SameHash> {
        @Override public int hashCode() { return 7; }
        @Override public int compareTo(SameHash o) { return Integer.compare(id, o.id); }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Default map (capacity 16):");
        Map<SameHash, Integer> small = new HashMap<>();
        for (int i = 1; i <= 11; i++) {
            small.put(new SameHash(i), i);
            System.out.printf("  %2d keys in one bucket -> capacity %2d, bucket type %s%n",
                              i, table(small).length, binType(small));
        }
        System.out.println("  Below 64 buckets HashMap RESIZES instead of treeifying — a long chain in a small");
        System.out.println("  table usually means the table is too small, not that the hash is bad.");

        System.out.println("\nPre-sized map (capacity 64):");
        Map<SameHash, Integer> big = new HashMap<>(64);
        for (int i = 1; i <= 9; i++) {
            big.put(new SameHash(i), i);
            if (i >= 8) System.out.printf("  %2d keys in one bucket -> capacity %2d, bucket type %s%n",
                                          i, table(big).length, binType(big));
        }
    }

    static Object[] table(Map<?, ?> m) throws Exception {
        Field f = HashMap.class.getDeclaredField("table");
        f.setAccessible(true);
        return (Object[]) f.get(m);
    }

    static String binType(Map<?, ?> m) throws Exception {
        for (Object bin : table(m)) if (bin != null) return bin.getClass().getSimpleName();
        return "-";
    }
}
