import java.util.List;

/** Java 16: instanceof with a binding — test and cast in one step. */
public class J16_PatternMatchingInstanceof {

    record Card(String last4) { }
    record Upi(String handle) { }
    record CashOnDelivery() { }

    static String describe(Object payment) {
        if (payment instanceof Card c) return "card ending " + c.last4();          // c is already a Card
        if (payment instanceof Upi u && u.handle().endsWith("@okbank")) return "UPI (trusted bank) " + u.handle();
        if (payment instanceof Upi u) return "UPI " + u.handle();
        return "cash on delivery";
    }

    public static void main(String[] args) {
        for (Object p : List.of(new Card("4417"), new Upi("asha@okbank"), new Upi("ravi@other"), new CashOnDelivery())) {
            System.out.println(describe(p));
        }
    }
}
