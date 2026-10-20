import java.util.List;
import java.util.stream.IntStream;

/** flatMap flattens nested lists; reduce folds many values into one; primitive streams avoid boxing. */
public class J8_06_FlatMapAndReduce {

    record Line(String sku, int qty, int price) { }
    record Order(String id, List<Line> lines) { }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("O1", List.of(new Line("MILK", 2, 60), new Line("RICE", 1, 450))),
            new Order("O2", List.of(new Line("MILK", 1, 60), new Line("TEA", 3, 120))));

        List<String> skus = orders.stream()
            .flatMap(o -> o.lines().stream())             // Stream<Order> -> Stream<Line>
            .map(Line::sku).distinct().sorted().toList();
        System.out.println("distinct SKUs across orders: " + skus);

        int revenue = orders.stream().flatMap(o -> o.lines().stream())
            .mapToInt(l -> l.qty() * l.price())           // IntStream: no boxing
            .sum();
        System.out.println("total revenue: ₹" + revenue);

        int product = IntStream.rangeClosed(1, 5).reduce(1, (a, b) -> a * b);   // identity 1 for multiplication
        System.out.println("5! via reduce: " + product);
        System.out.println("average line value: " + orders.stream().flatMap(o -> o.lines().stream())
            .mapToInt(l -> l.qty() * l.price()).average().orElse(0));
    }
}
