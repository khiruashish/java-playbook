import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.*;

/**
 * 8 threads each record 2,000 orders. Only an ATOMIC operation on a concurrent map gets the right total.
 * Thread.yield() widens the race window so it shows up even on a single-core machine;
 * on a real multi-core server it happens without help.
 */
public class LostUpdates {

    static final int THREADS = 8, PER_THREAD = 2_000, EXPECTED = THREADS * PER_THREAD;

    public static void main(String[] args) throws Exception {
        Map<String, Integer> hashMap = new HashMap<>();
        Map<String, Integer> chmGetPut = new ConcurrentHashMap<>();
        Map<String, Integer> chmMerge = new ConcurrentHashMap<>();

        runConcurrently(() -> { int v = hashMap.getOrDefault("orders", 0); Thread.yield(); hashMap.put("orders", v + 1); });
        runConcurrently(() -> { int v = chmGetPut.getOrDefault("orders", 0); Thread.yield(); chmGetPut.put("orders", v + 1); });
        runConcurrently(() -> chmMerge.merge("orders", 1, Integer::sum));

        System.out.printf("expected                          %,6d%n", EXPECTED);
        System.out.printf("HashMap, get then put             %,6d   <- lost updates%n", hashMap.get("orders"));
        System.out.printf("ConcurrentHashMap, get then put   %,6d   <- STILL lost: two calls, not one%n", chmGetPut.get("orders"));
        System.out.printf("ConcurrentHashMap.merge           %,6d   <- exact: one atomic operation%n", chmMerge.get("orders"));
    }

    static void runConcurrently(Runnable increment) throws Exception {
        CountDownLatch startGate = new CountDownLatch(1);
        try (ExecutorService pool = Executors.newFixedThreadPool(THREADS)) {
            for (int t = 0; t < THREADS; t++) {
                pool.submit(() -> { startGate.await(); for (int i = 0; i < PER_THREAD; i++) increment.run(); return null; });
            }
            startGate.countDown();                      // release all threads at once
        }                                               // close() waits for them to finish
    }
}
