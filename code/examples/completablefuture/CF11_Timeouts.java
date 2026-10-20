import java.util.concurrent.*;

/** Java 9+: orTimeout fails the future; completeOnTimeout substitutes a default. */
public class CF11_Timeouts {

    static CompletableFuture<String> slowQuote() {
        return CompletableFuture.supplyAsync(() -> { sleep(2_000); return "₹58 from the slow vendor"; });
    }

    public static void main(String[] args) {
        try {
            slowQuote().orTimeout(300, TimeUnit.MILLISECONDS).join();
        } catch (CompletionException e) {
            System.out.println("orTimeout:         " + e.getCause().getClass().getSimpleName());
        }

        String quote = slowQuote().completeOnTimeout("₹60 standard rate", 300, TimeUnit.MILLISECONDS).join();
        System.out.println("completeOnTimeout: " + quote);
        System.out.println("(in both cases the slow task itself keeps running — the future completes, the work is not stopped)");
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
