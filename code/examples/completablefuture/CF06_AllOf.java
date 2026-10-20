import java.util.List;
import java.util.concurrent.CompletableFuture;

/** allOf waits for many futures. It returns CompletableFuture<Void>, so read results from the originals. */
public class CF06_AllOf {

    public static void main(String[] args) {
        long start = System.currentTimeMillis();

        CompletableFuture<String> stock    = CompletableFuture.supplyAsync(() -> { sleep(300); return "in stock"; });
        CompletableFuture<String> price    = CompletableFuture.supplyAsync(() -> { sleep(500); return "₹60"; });
        CompletableFuture<String> delivery = CompletableFuture.supplyAsync(() -> { sleep(400); return "slot 6-8 pm"; });

        List<String> summary = CompletableFuture.allOf(stock, price, delivery)
            .thenApply(done -> List.of(stock.join(), price.join(), delivery.join()))   // join() won't block now
            .join();

        long ms = Math.round((System.currentTimeMillis() - start) / 100.0) * 100;
        System.out.println(summary);
        System.out.println("took about " + ms + " ms — the slowest call, not the sum (1200 ms)");
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
