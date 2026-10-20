import java.util.*;
import java.util.function.*;

/** The four kinds of method reference — each is shorthand for a lambda. */
public class J8_02_MethodReferences {

    record Product(String name, int price) {
        static Product parse(String csv) { String[] p = csv.split(","); return new Product(p[0], Integer.parseInt(p[1])); }
    }

    public static void main(String[] args) {
        Function<String, Integer> parse = Integer::parseInt;          // static:   s -> Integer.parseInt(s)
        Function<String, String> upper  = String::toUpperCase;        // unbound:  s -> s.toUpperCase()
        String prefix = "SKU-";
        Predicate<String> hasPrefix     = prefix::equals;             // bound:    s -> prefix.equals(s)
        Function<String, StringBuilder> make = StringBuilder::new;    // constructor: s -> new StringBuilder(s)

        System.out.println(parse.apply("42") + 1);
        System.out.println(upper.apply("milk"));
        System.out.println(hasPrefix.test("SKU-"));
        System.out.println(make.apply("rice").reverse());

        List<Product> products = List.of("Milk,60", "Rice,450", "Tea,120").stream().map(Product::parse).toList();
        products.forEach(System.out::println);
    }
}
