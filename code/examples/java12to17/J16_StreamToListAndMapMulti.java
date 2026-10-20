import java.util.*;
import java.util.stream.Collectors;

/** Java 16: Stream.toList() and mapMulti. */
public class J16_StreamToListAndMapMulti {

    record Order(String id, List<String> skus) { }

    public static void main(String[] args) {
        List<String> upper = List.of("milk", "rice").stream().map(String::toUpperCase).toList();
        try { upper.add("TEA"); } catch (UnsupportedOperationException e) { System.out.println("toList() is unmodifiable"); }

        List<String> mutable = List.of("milk").stream().collect(Collectors.toList());
        mutable.add("tea");
        System.out.println("collect(toList()) is mutable: " + mutable);

        List<Order> orders = List.of(new Order("O1", List.of("MILK", "RICE")), new Order("O2", List.of("TEA")));
        List<String> pairs = orders.stream()
            .<String>mapMulti((order, downstream) -> order.skus().forEach(sku -> downstream.accept(order.id() + ":" + sku)))
            .toList();
        System.out.println("mapMulti: " + pairs);
    }
}
