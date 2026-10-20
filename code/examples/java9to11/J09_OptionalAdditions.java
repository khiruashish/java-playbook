import java.util.*;

/** Java 9: Optional.or, ifPresentOrElse and stream. Java 10: orElseThrow() with no argument. */
public class J09_OptionalAdditions {

    static Optional<String> fromCache(String sku) { return Optional.empty(); }
    static Optional<String> fromDatabase(String sku) { return Optional.of("₹60"); }

    public static void main(String[] args) {
        String price = fromCache("MILK").or(() -> fromDatabase("MILK")).orElse("unknown");
        System.out.println("or(): " + price);

        fromCache("MILK").ifPresentOrElse(
            p -> System.out.println("cached: " + p),
            () -> System.out.println("ifPresentOrElse: cache miss"));

        List<Optional<String>> lookups = List.of(Optional.of("₹60"), Optional.empty(), Optional.of("₹450"));
        System.out.println("stream() flattens: " + lookups.stream().flatMap(Optional::stream).toList());

        System.out.println("orElseThrow(): " + fromDatabase("MILK").orElseThrow());
    }
}
