import java.util.concurrent.CompletableFuture;

/** thenAccept consumes the value; thenRun just runs afterwards. Both end the value chain. */
public class CF03_ThenAcceptThenRun {

    public static void main(String[] args) {
        CompletableFuture
            .supplyAsync(() -> "ORD-1001")
            .thenAccept(orderId -> System.out.println("send confirmation email for " + orderId))   // uses the value
            .thenRun(() -> System.out.println("log: confirmation step finished"))                // ignores it
            .join();
    }
}
