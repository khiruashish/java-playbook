import java.util.List;
import java.util.stream.Stream;

/** Java 9: takeWhile, dropWhile, a bounded iterate, and ofNullable. */
public class J09_StreamAdditions {

    public static void main(String[] args) {
        List<Integer> hourlyOrders = List.of(5, 9, 14, 30, 12, 4);

        System.out.println("takeWhile < 20: " + hourlyOrders.stream().takeWhile(n -> n < 20).toList() + "  (stops at the first failure)");
        System.out.println("filter    < 20: " + hourlyOrders.stream().filter(n -> n < 20).toList() + "  (checks every element)");
        System.out.println("dropWhile < 20: " + hourlyOrders.stream().dropWhile(n -> n < 20).toList());

        System.out.println("iterate with a condition: " + Stream.iterate(1, n -> n <= 100, n -> n * 3).toList());

        String maybeCoupon = null;
        System.out.println("ofNullable(null) count: " + Stream.ofNullable(maybeCoupon).count());
    }
}
