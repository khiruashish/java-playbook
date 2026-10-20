import java.util.concurrent.CompletableFuture;

/** The simplest case: start work in the background, keep going, collect the result later. */
public class CF01_SupplyAsync {

    public static void main(String[] args) {
        CompletableFuture<String> price = CompletableFuture.supplyAsync(() -> {
            sleep(300);                                   // pretend: a slow pricing service
            return "MILK-1L costs ₹60";
        });

        System.out.println("1. request sent — main thread is free");
        System.out.println("2. done yet? " + price.isDone());
        System.out.println("3. " + price.join());                 // join() waits for the result
        System.out.println("4. done yet? " + price.isDone());
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
