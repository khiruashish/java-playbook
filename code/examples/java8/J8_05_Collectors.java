import java.util.*;
import java.util.stream.Collectors;

/** The collectors that do most real work: grouping, partitioning, joining, toMap, statistics. */
public class J8_05_Collectors {

    record Product(String name, String category, int price) { }

    public static void main(String[] args) {
        List<Product> catalogue = List.of(
            new Product("Milk", "dairy", 60), new Product("Paneer", "dairy", 90),
            new Product("Rice", "grains", 450), new Product("Atta", "grains", 380), new Product("Tea", "beverages", 120));

        Map<String, List<String>> byCategory = catalogue.stream().collect(Collectors.groupingBy(
            Product::category, TreeMap::new, Collectors.mapping(Product::name, Collectors.toList())));
        System.out.println("groupingBy:     " + byCategory);

        Map<String, Long> countPerCategory = catalogue.stream().collect(
            Collectors.groupingBy(Product::category, TreeMap::new, Collectors.counting()));
        System.out.println("counting:       " + countPerCategory);

        Map<String, Integer> totalPerCategory = catalogue.stream().collect(
            Collectors.groupingBy(Product::category, TreeMap::new, Collectors.summingInt(Product::price)));
        System.out.println("summingInt:     " + totalPerCategory);

        Map<Boolean, List<String>> premium = catalogue.stream().collect(
            Collectors.partitioningBy(p -> p.price() >= 200, Collectors.mapping(Product::name, Collectors.toList())));
        System.out.println("partitioningBy: " + premium);

        System.out.println("joining:        " + catalogue.stream().map(Product::name).collect(Collectors.joining(", ", "[", "]")));

        Map<String, Integer> priceByName = catalogue.stream().collect(
            Collectors.toMap(Product::name, Product::price, (a, b) -> a, TreeMap::new));
        System.out.println("toMap:          " + priceByName);

        IntSummaryStatistics stats = catalogue.stream().collect(Collectors.summarizingInt(Product::price));
        System.out.println("statistics:     min=" + stats.getMin() + " max=" + stats.getMax() + " avg=" + stats.getAverage());
    }
}
