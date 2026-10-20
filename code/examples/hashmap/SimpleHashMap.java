import java.util.List;
import java.util.Objects;

/** Build your own: a 50-line hash map with the same core ideas as java.util.HashMap. */
public class SimpleHashMap<K, V> {

    static final class Node<K, V> {
        final int hash; final K key; V value; Node<K, V> next;
        Node(int hash, K key, V value, Node<K, V> next) { this.hash = hash; this.key = key; this.value = value; this.next = next; }
    }

    private Node<K, V>[] table = newTable(4);        // tiny on purpose, so we see a resize
    private int size;

    static int hash(Object key) {                    // same spreading as HashMap
        int h;
        return key == null ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }

    public V put(K key, V value) {
        int h = hash(key), i = (table.length - 1) & h;
        for (Node<K, V> n = table[i]; n != null; n = n.next) {
            if (n.hash == h && Objects.equals(n.key, key)) {          // existing key: replace
                V old = n.value; n.value = value;
                System.out.printf("put %-5s -> bucket %d  (replaced %s)%n", key, i, old);
                return old;
            }
        }
        table[i] = new Node<>(h, key, value, table[i]);               // new key: add to the chain
        System.out.printf("put %-5s -> bucket %d%s%n", key, i, table[i].next != null ? "  (collision)" : "");
        if (++size > table.length * 0.75) resize();                   // load factor 0.75
        return null;
    }

    public V get(Object key) {
        int h = hash(key);
        for (Node<K, V> n = table[(table.length - 1) & h]; n != null; n = n.next)
            if (n.hash == h && Objects.equals(n.key, key)) return n.value;
        return null;
    }

    private void resize() {
        Node<K, V>[] old = table;
        table = newTable(old.length * 2);
        System.out.printf("      resize: %d -> %d buckets, every entry re-indexed%n", old.length, table.length);
        for (Node<K, V> head : old) {
            for (Node<K, V> n = head; n != null; ) {
                Node<K, V> next = n.next;
                int i = (table.length - 1) & n.hash;                  // the stored hash is reused, not recomputed
                n.next = table[i]; table[i] = n;
                n = next;
            }
        }
    }

    @SuppressWarnings("unchecked")
    private static <K, V> Node<K, V>[] newTable(int n) { return (Node<K, V>[]) new Node[n]; }

    public static void main(String[] args) {
        SimpleHashMap<String, Integer> map = new SimpleHashMap<>();
        for (String s : List.of("MILK", "RICE", "ATTA", "DAL", "SALT", "TEA", "OIL")) map.put(s, s.length());
        map.put("MILK", 99);
        System.out.println("\nget(MILK) = " + map.get("MILK") + ", get(DAL) = " + map.get("DAL") + ", get(JAM) = " + map.get("JAM"));
    }
}
