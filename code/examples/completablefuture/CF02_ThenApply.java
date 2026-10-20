import java.util.concurrent.CompletableFuture;

/** thenApply transforms the result when it arrives — like Stream.map, but for a future value. */
public class CF02_ThenApply {

    public static void main(String[] args) {
        String receipt = CompletableFuture.supplyAsync(() -> 3)          // quantity from the cart service
            .thenApply(quantity -> quantity * 60)                        // price it
            .thenApply(total -> total + 25)                              // add delivery
            .thenApply(total -> "Total payable: ₹" + total)              // format it
            .join();
        System.out.println(receipt);
    }
}
