import java.util.concurrent.CompletableFuture;

/** thenCombine runs two independent calls in parallel and merges their results. */
public class CF05_ThenCombine {

    public static void main(String[] args) {
        long start = System.currentTimeMillis();

        CompletableFuture<Integer> price    = CompletableFuture.supplyAsync(() -> { sleep(400); return 60; });
        CompletableFuture<Integer> discount = CompletableFuture.supplyAsync(() -> { sleep(400); return 10; });

        int finalPrice = price.thenCombine(discount, (p, d) -> p - d).join();

        long ms = Math.round((System.currentTimeMillis() - start) / 100.0) * 100;
        System.out.println("final price: ₹" + finalPrice);
        System.out.println("took about " + ms + " ms — two 400 ms calls ran at the same time, not one after another");
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
