import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

/** Problem: LRU cache with O(1) get/put and a fixed capacity. */
public class LruCache {

    // ---- Approach 1: hand-written HashMap + doubly linked list (what interviewers usually want)
    static final class Lru<K, V> {
        private final class Node { K key; V value; Node prev, next; }
        private final int capacity;
        private final Map<K, Node> index = new HashMap<>();
        private final Node head = new Node(), tail = new Node();   // sentinels: no null checks at the ends

        Lru(int capacity) { this.capacity = capacity; head.next = tail; tail.prev = head; }

        V get(K key) {
            Node n = index.get(key);
            if (n == null) return null;
            moveToFront(n);
            return n.value;
        }

        void put(K key, V value) {
            Node n = index.get(key);
            if (n != null) { n.value = value; moveToFront(n); return; }
            if (index.size() == capacity) {           // evict least recently used = node before tail
                Node lru = tail.prev;
                unlink(lru);
                index.remove(lru.key);
            }
            n = new Node(); n.key = key; n.value = value;
            index.put(key, n);
            addFirst(n);
        }

        private void moveToFront(Node n) { unlink(n); addFirst(n); }
        private void unlink(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
        private void addFirst(Node n) { n.next = head.next; n.prev = head; head.next.prev = n; head.next = n; }

        String order() {
            StringBuilder sb = new StringBuilder("[");
            for (Node n = head.next; n != tail; n = n.next) sb.append(n.key).append(n.next == tail ? "" : ", ");
            return sb.append("]").toString();
        }
    }

    // ---- Approach 2: the JDK one-liner (LinkedHashMap in access order + removeEldestEntry)
    static <K, V> Map<K, V> jdkLru(int capacity) {
        return new LinkedHashMap<>(16, 0.75f, true) {
            @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) { return size() > capacity; }
        };
    }

    public static void main(String[] args) {
        Lru<Integer, String> lru = new Lru<>(3);
        Map<Integer, String> jdk = jdkLru(3);
        int[][] ops = {{1}, {2}, {3}, {-1}, {4}, {-3}, {5}};       // positive = put, negative = get
        for (int[] op : ops) {
            int k = op[0];
            if (k > 0) { lru.put(k, "v" + k); jdk.put(k, "v" + k); System.out.println("put " + k + "  MRU->LRU " + lru.order()); }
            else { lru.get(-k); jdk.get(-k); System.out.println("get " + (-k) + "  MRU->LRU " + lru.order()); }
        }
        check(lru.get(2) == null && lru.get(1) == null, "1 and 2 evicted");
        check(jdk.keySet().equals(java.util.Set.of(3, 4, 5)), "JDK version agrees");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
