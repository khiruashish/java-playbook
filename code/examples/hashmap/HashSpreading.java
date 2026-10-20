import java.util.List;

/** Step 1 of every put/get: turn the key into a bucket index — the same arithmetic as java.util.HashMap. */
public class HashSpreading {

    static int spread(Object key) {
        int h = key.hashCode();
        return h ^ (h >>> 16);                 // mix the high 16 bits into the low 16
    }

    public static void main(String[] args) {
        int capacity = 16;                     // default table size — always a power of two
        for (String key : List.of("MILK-1L", "RICE-5KG", "ATTA-10KG", "DAL-1KG", "SUGAR-1KG")) {
            int h = key.hashCode();
            int index = (capacity - 1) & spread(key);   // cheap modulo: keep the low 4 bits
            System.out.printf("%-10s hashCode=%11d  spread=%11d  bucket=%2d%n", key, h, spread(key), index);
        }

        System.out.println();
        System.out.println("Why spread? Two hash codes that differ only in their HIGH bits:");
        int a = 0x10000, b = 0x20000;          // low 16 bits identical (all zero)
        System.out.printf("  without spreading -> buckets %d and %d (they collide)%n", 15 & a, 15 & b);
        System.out.printf("  with spreading    -> buckets %d and %d%n", 15 & (a ^ (a >>> 16)), 15 & (b ^ (b >>> 16)));
    }
}
