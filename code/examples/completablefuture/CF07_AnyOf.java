import java.util.concurrent.CompletableFuture;

/** anyOf completes with whichever future finishes first — e.g. the fastest of three vendors. */
public class CF07_AnyOf {

    public static void main(String[] args) {
        CompletableFuture<String> vendorA = CompletableFuture.supplyAsync(() -> { sleep(600); return "Vendor A: ₹58"; });
        CompletableFuture<String> vendorB = CompletableFuture.supplyAsync(() -> { sleep(150); return "Vendor B: ₹61"; });
        CompletableFuture<String> vendorC = CompletableFuture.supplyAsync(() -> { sleep(400); return "Vendor C: ₹59"; });

        Object first = CompletableFuture.anyOf(vendorA, vendorB, vendorC).join();   // note: Object, needs a cast
        System.out.println("first quote: " + first);
        System.out.println("(the other two keep running — anyOf does not cancel them)");
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
