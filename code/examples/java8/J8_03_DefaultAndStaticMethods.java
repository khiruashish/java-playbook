/** Interfaces can carry behaviour: default methods (overridable) and static methods (utilities). */
public class J8_03_DefaultAndStaticMethods {

    interface Discount {
        int apply(int price);                                  // the one abstract method

        default Discount then(Discount next) {                 // shared behaviour, no subclass needed
            return price -> next.apply(apply(price));
        }

        static Discount percent(int pct) {                     // factory on the interface itself
            return price -> price - price * pct / 100;
        }
    }

    public static void main(String[] args) {
        Discount festive = Discount.percent(10);
        Discount coupon  = price -> price - 50;
        System.out.println("₹1000 after 10% then ₹50 coupon = ₹" + festive.then(coupon).apply(1000));
        System.out.println("₹1000 after coupon then 10%     = ₹" + coupon.then(festive).apply(1000));
    }
}
