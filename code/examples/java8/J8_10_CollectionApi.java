import java.util.*;

/** removeIf, replaceAll, forEach and composable Comparators on ordinary collections. */
public class J8_10_CollectionApi {

    record Product(String name, String category, int price) { }

    public static void main(String[] args) {
        List<Integer> quantities = new ArrayList<>(List.of(3, 0, 5, 0, 2));
        quantities.removeIf(q -> q == 0);
        System.out.println("removeIf zero:   " + quantities);
        quantities.replaceAll(q -> q * 10);
        System.out.println("replaceAll x10:  " + quantities);

        List<Product> products = new ArrayList<>(List.of(
            new Product("Paneer", "dairy", 90), new Product("Rice", "grains", 450),
            new Product("Milk", "dairy", 60), new Product("Atta", "grains", 380)));

        products.sort(Comparator.comparing(Product::category)
                                .thenComparing(Product::price, Comparator.reverseOrder()));
        products.forEach(p -> System.out.println("  " + p.category() + "  " + p.name() + "  ₹" + p.price()));
    }
}
