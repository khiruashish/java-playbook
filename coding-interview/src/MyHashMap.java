import java.util.Objects;

/** Problem: implement a HashMap (put/get/remove/size) without java.util maps. Separate chaining + resize. */
public class MyHashMap<K, V> {

    private static final class Node<K, V> {
        final int hash; final K key; V value; Node<K, V> next;
        Node(int hash, K key, V value, Node<K, V> next) { this.hash = hash; this.key = key; this.value = value; this.next = next; }
    }

    private static final float LOAD_FACTOR = 0.75f;
    private Node<K, V>[] table = newTable(16);
    private int size;

    @SuppressWarnings("unchecked")
    private static <K, V> Node<K, V>[] newTable(int n) { return (Node<K, V>[]) new Node[n]; }

    /** Spread high bits into low bits (like java.util.HashMap) because the index uses only the low bits. */
    private static int hash(Object key) { int h = Objects.hashCode(key); return h ^ (h >>> 16); }

    private static int indexFor(int hash, int length) { return hash & (length - 1); }   // length is a power of two

    public V put(K key, V value) {
        int h = hash(key);
        int i = indexFor(h, table.length);
        for (Node<K, V> n = table[i]; n != null; n = n.next) {
            if (n.hash == h && Objects.equals(n.key, key)) { V old = n.value; n.value = value; return old; }
        }
        table[i] = new Node<>(h, key, value, table[i]);     // insert at bucket head
        if (++size > table.length * LOAD_FACTOR) resize();
        return null;
    }

    public V get(K key) {
        int h = hash(key);
        for (Node<K, V> n = table[indexFor(h, table.length)]; n != null; n = n.next) {
            if (n.hash == h && Objects.equals(n.key, key)) return n.value;
        }
        return null;
    }

    public V remove(K key) {
        int h = hash(key);
        int i = indexFor(h, table.length);
        Node<K, V> prev = null;
        for (Node<K, V> n = table[i]; n != null; prev = n, n = n.next) {
            if (n.hash == h && Objects.equals(n.key, key)) {
                if (prev == null) table[i] = n.next; else prev.next = n.next;
                size--;
                return n.value;
            }
        }
        return null;
    }

    private void resize() {
        Node<K, V>[] old = table;
        table = newTable(old.length * 2);
        for (Node<K, V> head : old) {
            for (Node<K, V> n = head; n != null; ) {
                Node<K, V> next = n.next;
                int i = indexFor(n.hash, table.length);     // reuse the cached hash
                n.next = table[i];
                table[i] = n;
                n = next;
            }
        }
    }

    public int size() { return size; }

    int capacity() { return table.length; }

    /** A key whose hashCode always collides, to prove chaining works. */
    record BadKey(String id) { @Override public int hashCode() { return 42; } }

    public static void main(String[] args) {
        MyHashMap<String, Integer> map = new MyHashMap<>();
        for (int i = 0; i < 1000; i++) map.put("k" + i, i);
        System.out.println("size=" + map.size() + " capacity=" + map.capacity());
        check(map.size() == 1000 && map.get("k500") == 500, "1000 entries retrievable after resizes");
        check(map.put("k1", 99) == 1 && map.get("k1") == 99 && map.size() == 1000, "put replaces value");
        check(map.remove("k1") == 99 && map.get("k1") == null && map.size() == 999, "remove");
        map.put(null, -1);
        check(map.get(null) == -1, "null key supported");

        MyHashMap<BadKey, String> colliding = new MyHashMap<>();
        for (int i = 0; i < 50; i++) colliding.put(new BadKey("b" + i), "v" + i);
        System.out.println("50 keys with identical hashCode -> all found: " + (colliding.get(new BadKey("b37")).equals("v37")));
        check(colliding.size() == 50 && "v37".equals(colliding.get(new BadKey("b37"))), "collisions chained");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
