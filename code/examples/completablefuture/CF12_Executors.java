import java.util.concurrent.*;

/** Pass your own executor for blocking work. The default common pool is shared by the whole JVM. */
public class CF12_Executors {

    public static void main(String[] args) {
        String onDefault = CompletableFuture.supplyAsync(() -> Thread.currentThread().getName()).join();
        System.out.println("default executor:  " + onDefault.replaceAll("\\d+$", "N"));

        try (ExecutorService io = Executors.newFixedThreadPool(4, Thread.ofPlatform().name("io-", 1).factory())) {
            String onPool = CompletableFuture.supplyAsync(() -> Thread.currentThread().getName(), io).join();
            System.out.println("own fixed pool:    " + onPool);
        }

        try (ExecutorService virtual = Executors.newVirtualThreadPerTaskExecutor()) {   // Java 21
            boolean isVirtual = CompletableFuture.supplyAsync(() -> Thread.currentThread().isVirtual(), virtual).join();
            System.out.println("virtual threads:   isVirtual = " + isVirtual + "  <- best choice for blocking I/O on Java 21+");
        }
    }
}
