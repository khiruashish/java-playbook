import java.util.concurrent.*;

/** A realistic order-confirmation fan-out: three calls in parallel, a timeout, fallbacks, one result. */
public class CF16_PuttingItTogether {

    record OrderView(String stock, String price, String slot) { }

    public static void main(String[] args) {
        long start = System.currentTimeMillis();
        try (ExecutorService io = Executors.newVirtualThreadPerTaskExecutor()) {

            CompletableFuture<String> stock = CompletableFuture.supplyAsync(() -> call("in stock", 200), io)
                .exceptionally(ex -> "stock unknown");
            CompletableFuture<String> price = CompletableFuture.supplyAsync(() -> call("₹60", 300), io)
                .completeOnTimeout("₹60 (cached)", 500, TimeUnit.MILLISECONDS);
            CompletableFuture<String> slot = CompletableFuture.supplyAsync(() -> call("6-8 pm", 3_000), io)  // too slow
                .completeOnTimeout("next available slot", 500, TimeUnit.MILLISECONDS);

            OrderView view = stock
                .thenCombine(price, (s, p) -> new String[] {s, p})
                .thenCombine(slot, (sp, sl) -> new OrderView(sp[0], sp[1], sl))
                .join();

            long ms = Math.round((System.currentTimeMillis() - start) / 100.0) * 100;
            System.out.println(view);
            System.out.println("answered in about " + ms + " ms even though one dependency took 3 s");
        }
    }

    static String call(String result, long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return result;
    }
}
