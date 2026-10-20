import java.util.*;
import java.util.concurrent.*;

/** Submit work to a pool, get Futures back, and collect results — including a failed task. */
public class C05_ExecutorAndFutures {

    public static void main(String[] args) throws Exception {
        try (ExecutorService pool = Executors.newFixedThreadPool(3)) {
            List<Callable<String>> lookups = List.of(
                () -> "MILK: 40 units",
                () -> "RICE: 12 units",
                () -> { throw new IllegalStateException("TEA: warehouse offline"); });

            for (Future<String> f : pool.invokeAll(lookups)) {      // runs all, waits for all
                try {
                    System.out.println("ok     " + f.get(1, TimeUnit.SECONDS));
                } catch (ExecutionException e) {
                    System.out.println("failed " + e.getCause().getMessage());   // the real exception
                }
            }
            String fastest = pool.invokeAny(List.of(() -> { Thread.sleep(300); return "slow vendor"; }, () -> "fast vendor"));
            System.out.println("invokeAny -> " + fastest);
        }
        System.out.println("Warning: submit() hides exceptions inside the Future — always call get() or they vanish.");
    }
}
