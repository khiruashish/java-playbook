import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;

/** Turn a callback-style API into a CompletableFuture by completing it yourself. */
public class CF13_ManualComplete {

    /** A legacy SDK that reports results through callbacks. */
    static void legacySend(String orderId, Consumer<String> onSuccess, Consumer<Exception> onFailure) {
        Thread.ofPlatform().start(() -> {
            if (orderId.isBlank()) onFailure.accept(new IllegalArgumentException("blank order id"));
            else onSuccess.accept("RECEIPT-" + orderId);
        });
    }

    static CompletableFuture<String> send(String orderId) {
        CompletableFuture<String> result = new CompletableFuture<>();
        legacySend(orderId, result::complete, result::completeExceptionally);   // bridge
        return result;
    }

    public static void main(String[] args) {
        System.out.println(send("ORD-1001").thenApply(String::toLowerCase).join());
        System.out.println(send(" ").exceptionally(ex -> "failed: " + ex.getMessage()).join());
    }
}
