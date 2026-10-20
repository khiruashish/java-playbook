import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** 16 requests ask for the same price at once. computeIfAbsent calls the slow loader exactly once. */
public class ComputeIfAbsentOnce {

    public static void main(String[] args) throws Exception {
        AtomicInteger naiveLoads = new AtomicInteger(), atomicLoads = new AtomicInteger();
        Map<String, Integer> naive = new ConcurrentHashMap<>(), cache = new ConcurrentHashMap<>();

        concurrently(16, () -> {                                   // get, then put if missing
            if (naive.get("MILK") == null) naive.put("MILK", slowLoad(naiveLoads));
        });
        concurrently(16, () -> cache.computeIfAbsent("MILK", sku -> slowLoad(atomicLoads)));

        System.out.println("get-then-put:     loader called " + naiveLoads.get() + " times");
        System.out.println("computeIfAbsent:  loader called " + atomicLoads.get() + " time");
        System.out.println("\nRule: the loader runs while the bin is locked — keep it fast, no I/O, and never touch the same map inside it.");
    }

    static int slowLoad(AtomicInteger counter) {
        counter.incrementAndGet();
        try { Thread.sleep(50); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return 60;
    }

    static void concurrently(int n, Runnable r) throws Exception {
        CountDownLatch gate = new CountDownLatch(1);
        try (ExecutorService pool = Executors.newFixedThreadPool(n)) {
            for (int i = 0; i < n; i++) pool.submit(() -> { gate.await(); r.run(); return null; });
            gate.countDown();
        }
    }
}
