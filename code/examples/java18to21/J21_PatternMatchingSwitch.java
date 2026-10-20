import java.util.List;

/** Java 21: switch on types, with guards (when), a null case, and exhaustiveness over sealed types. */
public class J21_PatternMatchingSwitch {

    sealed interface Payment permits Card, Upi, Wallet { }
    record Card(String last4, boolean international) implements Payment { }
    record Upi(String handle) implements Payment { }
    record Wallet(String provider, long balancePaise) implements Payment { }

    static long feePaise(Payment payment) {
        return switch (payment) {
            case null -> throw new IllegalArgumentException("no payment");   // explicit null handling
            case Card c when c.international() -> 350;                        // guard: more specific first
            case Card c -> 200;
            case Upi u -> 0;
            case Wallet w when w.balancePaise() > 100_000 -> 0;
            case Wallet w -> 100;
        };                                                                    // no default: sealed + exhaustive
    }

    static String describe(Object o) {                    // works on any type, not just enums and strings
        return switch (o) {
            case Integer i when i > 100 -> "large quantity " + i;
            case Integer i -> "quantity " + i;
            case String s -> "SKU " + s;
            default -> "unknown " + o;
        };
    }

    public static void main(String[] args) {
        List<Payment> payments = List.of(new Card("4417", true), new Card("1234", false),
                                         new Upi("asha@okbank"), new Wallet("PayQuick", 50_000));
        for (Payment p : payments) System.out.println(feePaise(p) + " paise  <- " + p);
        System.out.println(describe(250) + " | " + describe(3) + " | " + describe("MILK-1L") + " | " + describe(4.5));
    }
}
