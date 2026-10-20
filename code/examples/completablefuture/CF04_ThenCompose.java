import java.util.concurrent.CompletableFuture;

/** thenCompose chains a call that itself returns a future — like flatMap. thenApply would nest them. */
public class CF04_ThenCompose {

    static CompletableFuture<String> findCustomer(String orderId) {
        return CompletableFuture.supplyAsync(() -> "CUST-42");
    }

    static CompletableFuture<String> findAddress(String customerId) {
        return CompletableFuture.supplyAsync(() -> "12 MG Road, Bengaluru");
    }

    public static void main(String[] args) {
        CompletableFuture<CompletableFuture<String>> nested =
            findCustomer("ORD-1001").thenApply(CF04_ThenCompose::findAddress);      // future inside a future
        CompletableFuture<String> flat =
            findCustomer("ORD-1001").thenCompose(CF04_ThenCompose::findAddress);    // flattened

        System.out.println("thenApply   -> needs join().join(): " + nested.join().join());
        System.out.println("thenCompose -> one join():          " + flat.join());
    }
}
