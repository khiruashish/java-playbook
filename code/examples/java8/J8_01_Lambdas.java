import java.util.*;
import java.util.function.*;

/** Lambdas and the built-in functional interfaces. */
public class J8_01_Lambdas {

    public static void main(String[] args) {
        // Before Java 8: an anonymous class just to pass one piece of behaviour
        Comparator<String> oldWay = new Comparator<String>() {
            @Override public int compare(String a, String b) { return a.length() - b.length(); }
        };
        // Java 8: the same behaviour as a lambda
        Comparator<String> byLength = (a, b) -> a.length() - b.length();

        List<String> skus = new ArrayList<>(List.of("RICE-5KG", "TEA", "MILK-1L"));
        skus.sort(byLength);
        System.out.println("sorted by length: " + skus);

        // The four you use most
        Predicate<Integer> inStock   = qty -> qty > 0;             // T -> boolean
        Function<Integer, Integer> gst = price -> price * 105 / 100; // T -> R
        Consumer<String> notify      = msg -> System.out.println("notify: " + msg);  // T -> void
        Supplier<String> newOrderId  = () -> "ORD-1001";           // () -> T

        System.out.println("inStock.test(0)   = " + inStock.test(0));
        System.out.println("gst.apply(100)    = " + gst.apply(100));
        notify.accept("order placed");
        System.out.println("newOrderId.get()  = " + newOrderId.get());

        // Composition
        Predicate<String> isLong = s -> s.length() > 5;
        Predicate<String> isRice = s -> s.startsWith("RICE");
        System.out.println("long AND rice: " + isLong.and(isRice).test("RICE-5KG") + ", NOT long: " + isLong.negate().test("TEA"));
        Function<Integer, Integer> discount = p -> p - 10;
        System.out.println("discount then gst: " + discount.andThen(gst).apply(110));
    }
}
