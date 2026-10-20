import java.util.concurrent.CompletableFuture;

/** exceptionally recovers from a failure with a fallback value. */
public class CF08_Exceptionally {

    public static void main(String[] args) {
        String price = CompletableFuture
            .supplyAsync(() -> {
                if (true) throw new IllegalStateException("pricing service down");
                return "₹60";
            })
            .exceptionally(ex -> {
                System.out.println("caught: " + ex.getClass().getSimpleName() + " caused by " + ex.getCause().getMessage());
                return "₹65 (last known price)";
            })
            .join();
        System.out.println("price: " + price);
    }
}
