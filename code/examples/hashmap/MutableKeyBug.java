import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/** Why map keys must be immutable: change a key after put() and the entry is stranded. */
public class MutableKeyBug {

    static final class MutableSku {
        private String code;
        MutableSku(String code) { this.code = code; }
        void setCode(String code) { this.code = code; }
        @Override public boolean equals(Object o) { return o instanceof MutableSku s && Objects.equals(code, s.code); }
        @Override public int hashCode() { return Objects.hash(code); }
        @Override public String toString() { return code; }
    }

    public static void main(String[] args) {
        MutableSku key = new MutableSku("MILK-1L");
        Map<MutableSku, Integer> stock = new HashMap<>();
        stock.put(key, 40);
        System.out.println("before: get = " + stock.get(key) + ", size = " + stock.size());

        key.setCode("MILK-2L");                     // hashCode changes; the entry does NOT move buckets

        System.out.println("after:  get = " + stock.get(key) + ", containsKey = " + stock.containsKey(key)
                           + ", size = " + stock.size());
        System.out.println("remove(key) returned " + stock.remove(key) + " — the entry can no longer be reached.");
        System.out.println("\nFix: use an immutable key, e.g.  record Sku(String code) { }");
    }
}
