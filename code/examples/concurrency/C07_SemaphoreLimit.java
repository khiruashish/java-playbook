import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** A Semaphore caps concurrent use of a resource — here, at most 3 calls to a fragile warehouse API. */
public class C07_SemaphoreLimit {

    public static void main(String[] args) {
        Semaphore permits = new Semaphore(3);
        AtomicInteger inFlight = new AtomicInteger(), peak = new AtomicInteger();

        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {   // 20 tasks, cheap threads
            for (int i = 0; i < 20; i++) {
                executor.submit(() -> {
                    permits.acquire();
                    try {
                        peak.accumulateAndGet(inFlight.incrementAndGet(), Math::max);
                        Thread.sleep(50);                                               // the API call
                    } finally {
                        inFlight.decrementAndGet();
                        permits.release();
                    }
                    return null;
                });
            }
        }
        System.out.println("20 requests, peak concurrent calls to the API: " + peak.get());
    }
}
