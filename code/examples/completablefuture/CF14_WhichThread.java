import java.util.concurrent.CompletableFuture;

/** Which thread runs a stage? Non-async stages run on whichever thread completes the future. */
public class CF14_WhichThread {

    public static void main(String[] args) {
        // Already complete when thenApply is attached -> runs right here, on main
        CompletableFuture.completedFuture("x")
            .thenApply(v -> report("thenApply on an already-completed future"))
            .join();

        // Not yet complete -> runs on the thread that completes it (a pool thread)
        CompletableFuture.supplyAsync(() -> { sleep(200); return "x"; })
            .thenApply(v -> report("thenApply on a pending future"))
            .join();

        // Async variant -> always handed to an executor
        CompletableFuture.completedFuture("x")
            .thenApplyAsync(v -> report("thenApplyAsync"))
            .join();
    }

    static String report(String what) {
        String name = Thread.currentThread().getName().replaceAll("\\d+$", "N");
        System.out.printf("%-42s runs on: %s%n", what, name);
        return what;
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
