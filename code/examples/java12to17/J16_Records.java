import java.util.*;

/** Java 16: records — immutable data carriers with equals, hashCode, toString and accessors generated. */
public class J16_Records {

    record Money(long paise) {
        Money {                                             // compact constructor: validate
            if (paise < 0) throw new IllegalArgumentException("negative amount");
        }
        Money plus(Money other) { return new Money(paise + other.paise); }
        @Override public String toString() { return "₹" + paise / 100 + "." + String.format("%02d", paise % 100); }
    }

    record OrderLine(String sku, int quantity, Money unitPrice, List<String> tags) {
        OrderLine { tags = List.copyOf(tags); }             // defensive copy — records are only shallowly immutable
        Money total() { return new Money(unitPrice.paise() * quantity); }
    }

    public static void main(String[] args) {
        OrderLine line = new OrderLine("MILK", 2, new Money(6000), new ArrayList<>(List.of("dairy")));
        System.out.println(line);
        System.out.println("accessor: " + line.sku() + ", total: " + line.total());

        OrderLine same = new OrderLine("MILK", 2, new Money(6000), List.of("dairy"));
        System.out.println("equals by value: " + line.equals(same) + ", same hashCode: " + (line.hashCode() == same.hashCode()));

        Set<OrderLine> set = new HashSet<>(List.of(line, same));
        System.out.println("set size: " + set.size());

        try { new Money(-1); } catch (IllegalArgumentException e) { System.out.println("validation: " + e.getMessage()); }

        record Pair(String sku, int qty) { }                // local record, handy inside a method
        System.out.println(new Pair("RICE", 1));
    }
}
