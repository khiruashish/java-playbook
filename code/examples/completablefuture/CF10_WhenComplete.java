import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

/** whenComplete observes (logging, metrics) but does NOT change the result — a failure still propagates. */
public class CF10_WhenComplete {

    public static void main(String[] args) {
        CompletableFuture<String> order = CompletableFuture
            .<String>supplyAsync(() -> { throw new IllegalStateException("payment declined"); })
            .whenComplete((value, ex) -> System.out.println("metrics: order " + (ex == null ? "succeeded" : "failed")));

        try {
            order.join();
        } catch (CompletionException e) {
            System.out.println("still failed after whenComplete: " + e.getCause().getMessage());
        }
    }
}
