import java.time.Duration;
import java.util.concurrent.*;
import java.util.stream.IntStream;

/** Java 21: virtual threads make blocking cheap — 10,000 concurrent blocking tasks finish in about the time of one. */
public class J21_VirtualThreads {

    public static void main(String[] args) throws Exception {
        int tasks = 10_000;
        Duration io = Duration.ofMillis(500);                  // each task "waits on a network call"

        long vt = time(() -> {
            try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
                IntStream.range(0, tasks).forEach(i -> executor.submit(() -> { Thread.sleep(io); return i; }));
            }
        });
        System.out.printf("%,d tasks on virtual threads:            ~%.1f s%n", tasks, vt / 1000.0);

        long platform = time(() -> {
            try (ExecutorService executor = Executors.newFixedThreadPool(200)) {
                IntStream.range(0, tasks).forEach(i -> executor.submit(() -> { Thread.sleep(io); return i; }));
            }
        });
        System.out.printf("%,d tasks on a pool of 200 platform threads: ~%.1f s%n", tasks, platform / 1000.0);

        Thread t = Thread.ofVirtual().name("order-1001").start(() -> {});
        t.join();
        System.out.println("\nThread.ofVirtual(): isVirtual = " + t.isVirtual() + ", name = " + t.getName());
        System.out.println("Rule: never pool virtual threads. To limit a resource (e.g. 20 DB connections), use a Semaphore.");
    }

    static long time(Runnable r) {
        long start = System.nanoTime();
        r.run();
        return Math.round((System.nanoTime() - start) / 1e8) * 100;   // rounded to 0.1 s
    }
}
