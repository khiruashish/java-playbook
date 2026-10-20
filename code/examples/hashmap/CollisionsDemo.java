import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** What a collision costs: keys in the same bucket are found by walking the chain with equals(). */
public class CollisionsDemo {

    static int equalsCalls = 0;

    /** A deliberately bad key: every instance has the same hashCode, so all land in one bucket. */
    record BadKey(String code) {
        @Override public int hashCode() { return 42; }
        @Override public boolean equals(Object o) {
            equalsCalls++;
            return o instanceof BadKey other && other.code.equals(code);
        }
    }

    public static void main(String[] args) {
        Map<BadKey, Integer> map = new HashMap<>();
        for (String code : List.of("MILK", "RICE", "ATTA", "DAL", "SALT", "TEA")) {
            map.put(new BadKey(code), code.length());
        }
        System.out.println("size = " + map.size() + " — all six keys share bucket " + (15 & (42 ^ (42 >>> 16))));

        equalsCalls = 0;
        System.out.println("get(TEA)  = " + map.get(new BadKey("TEA")) + "   equals() calls: " + equalsCalls);
        equalsCalls = 0;
        System.out.println("get(MILK) = " + map.get(new BadKey("MILK")) + "   equals() calls: " + equalsCalls);
        equalsCalls = 0;
        System.out.println("get(OIL)  = " + map.get(new BadKey("OIL")) + "  equals() calls: " + equalsCalls);

        System.out.println("\nWith a good hashCode each lookup needs about one equals() call.");
        System.out.println("With a constant hashCode it is a linear search — O(n) — until the bucket becomes a tree.");
    }
}
