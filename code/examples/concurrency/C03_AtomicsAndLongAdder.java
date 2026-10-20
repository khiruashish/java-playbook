import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Atomic counters without locks: AtomicInteger for exact values, LongAdder for busy metrics. */
public class C03_AtomicsAndLongAdder {

    public static void main(String[] args) throws Exception {
        AtomicInteger orderNumber = new AtomicInteger(1000);
        LongAdder pageViews = new LongAdder();

        try (ExecutorService pool = Executors.newFixedThreadPool(8)) {
            for (int i = 0; i < 1_000; i++) {
                pool.submit(() -> { orderNumber.incrementAndGet(); pageViews.increment(); });
            }
        }
        System.out.println("order number: " + orderNumber.get() + " (exact — use for IDs)");
        System.out.println("page views:   " + pageViews.sum() + " (scales under contention — use for metrics)");

        AtomicReference<String> status = new AtomicReference<>("PENDING");
        System.out.println("CAS PENDING->PAID:  " + status.compareAndSet("PENDING", "PAID") + ", now " + status.get());
        System.out.println("CAS PENDING->FAILED: " + status.compareAndSet("PENDING", "FAILED") + " (it is no longer PENDING)");

        AtomicInteger highest = new AtomicInteger();
        for (int bid : new int[] {60, 450, 120}) highest.accumulateAndGet(bid, Math::max);
        System.out.println("accumulateAndGet(max): " + highest.get());
    }
}
