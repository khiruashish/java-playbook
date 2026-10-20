/** Java 17: sealed types — a closed set of subtypes the compiler knows about. */
public class J17_SealedClasses {

    sealed interface Payment permits Card, Upi, Wallet { }
    record Card(String last4) implements Payment { }
    record Upi(String handle) implements Payment { }
    record Wallet(String provider, long balancePaise) implements Payment { }

    // record Crypto() implements Payment { }   // would not compile: Crypto is not in the permits list

    static long fee(Payment p) {
        // On Java 17 you test each case; on Java 21 a pattern switch makes this exhaustive (see the Java 21 page)
        if (p instanceof Card) return 200;
        if (p instanceof Upi) return 0;
        if (p instanceof Wallet w) return w.balancePaise() > 100_000 ? 0 : 100;
        throw new AssertionError("unreachable — the hierarchy is sealed");
    }

    public static void main(String[] args) {
        Payment[] payments = { new Card("4417"), new Upi("asha@okbank"), new Wallet("PayQuick", 50_000) };
        for (Payment p : payments) System.out.println(p + " -> fee " + fee(p) + " paise");
        System.out.println("permitted subclasses: " + java.util.Arrays.stream(Payment.class.getPermittedSubclasses())
            .map(Class::getSimpleName).toList());
    }
}
