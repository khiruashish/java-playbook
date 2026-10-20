import java.util.*;

/** Optional makes "no result" explicit in a return type. */
public class J8_07_Optional {

    static final Map<String, Integer> PRICES = Map.of("MILK", 60, "RICE", 450);

    static Optional<Integer> priceOf(String sku) {
        return Optional.ofNullable(PRICES.get(sku));
    }

    public static void main(String[] args) {
        System.out.println("MILK present? " + priceOf("MILK").isPresent());
        System.out.println("JAM  with orElse:    " + priceOf("JAM").orElse(0));
        System.out.println("MILK mapped:         " + priceOf("MILK").map(p -> "₹" + p).orElse("n/a"));
        System.out.println("RICE filtered > 100: " + priceOf("RICE").filter(p -> p > 100).isPresent());

        priceOf("MILK").ifPresent(p -> System.out.println("ifPresent ran with " + p));

        // orElse evaluates its argument ALWAYS; orElseGet only when empty
        System.out.println("orElse:    " + priceOf("MILK").orElse(expensiveDefault()));
        System.out.println("orElseGet: " + priceOf("MILK").orElseGet(J8_07_Optional::expensiveDefault));

        try {
            priceOf("JAM").orElseThrow(() -> new NoSuchElementException("no price for JAM"));
        } catch (NoSuchElementException e) {
            System.out.println("orElseThrow: " + e.getMessage());
        }
    }

    static int expensiveDefault() {
        System.out.println("   (expensiveDefault() was called)");
        return -1;
    }
}
