import java.util.List;

/** filter -> map -> terminal operation. Nothing runs until the terminal operation is called. */
public class J8_04_StreamBasics {

    record Product(String name, String category, int price) { }

    public static void main(String[] args) {
        List<Product> catalogue = List.of(
            new Product("Milk", "dairy", 60), new Product("Paneer", "dairy", 90),
            new Product("Rice", "grains", 450), new Product("Atta", "grains", 380), new Product("Tea", "beverages", 120));

        List<String> cheapDairy = catalogue.stream()
            .filter(p -> p.category().equals("dairy"))       // keep some
            .filter(p -> p.price() < 100)
            .map(Product::name)                              // transform each
            .sorted()
            .toList();                                       // terminal (Java 16; collect(toList()) on Java 8)
        System.out.println("cheap dairy: " + cheapDairy);

        System.out.println("count > ₹100:   " + catalogue.stream().filter(p -> p.price() > 100).count());
        System.out.println("any over ₹400:  " + catalogue.stream().anyMatch(p -> p.price() > 400));
        System.out.println("most expensive: " + catalogue.stream().max((a, b) -> Integer.compare(a.price(), b.price())).get().name());
        System.out.println("first 2 names:  " + catalogue.stream().map(Product::name).limit(2).toList());

        System.out.println("\nLaziness — watch the order of the prints:");
        catalogue.stream()
            .filter(p -> { System.out.println("  filter " + p.name()); return p.price() > 100; })
            .map(p -> { System.out.println("  map    " + p.name()); return p.name(); })
            .findFirst()
            .ifPresent(n -> System.out.println("  found  " + n));
    }
}
