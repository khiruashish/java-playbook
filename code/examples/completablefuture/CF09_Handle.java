import java.util.concurrent.CompletableFuture;

/** handle sees BOTH outcomes — the value or the exception — and returns a replacement result. */
public class CF09_Handle {

    static CompletableFuture<Integer> stockFor(String sku) {
        return CompletableFuture.supplyAsync(() -> {
            if (sku.startsWith("X")) throw new IllegalArgumentException("unknown SKU " + sku);
            return 40;
        });
    }

    public static void main(String[] args) {
        for (String sku : new String[] {"MILK-1L", "XYZ-9"}) {
            String result = stockFor(sku)
                .handle((qty, ex) -> ex == null ? sku + ": " + qty + " units" : sku + ": unavailable (" + ex.getCause().getMessage() + ")")
                .join();
            System.out.println(result);
        }
    }
}
