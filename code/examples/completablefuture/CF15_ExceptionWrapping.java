import java.util.concurrent.*;

/** Exceptions arrive wrapped: join() throws CompletionException, get() throws ExecutionException. */
public class CF15_ExceptionWrapping {

    public static void main(String[] args) throws InterruptedException {
        CompletableFuture<String> failing = CompletableFuture.supplyAsync(() -> {
            throw new IllegalStateException("vendor unavailable");
        });

        try { failing.join(); }
        catch (CompletionException e) { System.out.println("join(): " + e.getClass().getSimpleName() + " -> cause: " + e.getCause().getMessage()); }

        try { failing.get(); }
        catch (ExecutionException e) { System.out.println("get():  " + e.getClass().getSimpleName() + " -> cause: " + e.getCause().getMessage()); }

        String handled = failing.exceptionally(ex -> {
            Throwable cause = ex instanceof CompletionException && ex.getCause() != null ? ex.getCause() : ex;
            return cause instanceof IllegalStateException ? "fallback vendor" : "give up";
        }).join();
        System.out.println("unwrap before matching on the type -> " + handled);
    }
}
