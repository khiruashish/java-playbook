import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/** Problem: write an immutable class correctly, and show what breaks when equals/hashCode are wrong. */
public class ImmutableMoney {

    /** 1) final class  2) private final fields  3) validate  4) defensive copies  5) no setters  6) equals+hashCode */
    static final class Invoice {
        private final String number;
        private final long totalCents;
        private final List<String> lines;

        Invoice(String number, long totalCents, List<String> lines) {
            this.number = Objects.requireNonNull(number);
            if (totalCents < 0) throw new IllegalArgumentException("negative total");
            this.totalCents = totalCents;
            this.lines = List.copyOf(lines);                   // defensive copy, and itself unmodifiable
        }

        String number() { return number; }
        long totalCents() { return totalCents; }
        List<String> lines() { return lines; }                 // safe: already unmodifiable

        /** "Withers" return a new object instead of mutating. */
        Invoice withTotal(long newTotal) { return new Invoice(number, newTotal, lines); }

        @Override public boolean equals(Object o) {
            return o instanceof Invoice other && totalCents == other.totalCents && number.equals(other.number) && lines.equals(other.lines);
        }
        @Override public int hashCode() { return Objects.hash(number, totalCents, lines); }
        @Override public String toString() { return "Invoice[" + number + ", " + totalCents + ", " + lines + "]"; }
    }

    /** The modern equivalent: a record gives final fields, accessors, equals, hashCode, toString. */
    record InvoiceRecord(String number, long totalCents, List<String> lines) {
        InvoiceRecord {
            Objects.requireNonNull(number);
            lines = List.copyOf(lines);                        // records are only shallowly immutable without this
        }
    }

    /** BROKEN: overrides equals but not hashCode. */
    static final class BrokenKey {
        final String id;
        BrokenKey(String id) { this.id = id; }
        @Override public boolean equals(Object o) { return o instanceof BrokenKey b && b.id.equals(id); }
    }

    public static void main(String[] args) {
        List<String> source = new ArrayList<>(List.of("apples", "pears"));
        Invoice inv = new Invoice("INV-1", 500, source);
        source.add("injected later");
        System.out.println("caller mutated its list; invoice still has " + inv.lines());
        check(inv.lines().size() == 2, "defensive copy on the way in");
        try { inv.lines().add("x"); check(false, "should be unmodifiable"); }
        catch (UnsupportedOperationException e) { System.out.println("lines() is unmodifiable"); }

        Invoice bigger = inv.withTotal(900);
        System.out.println("withTotal -> new object " + bigger + ", original unchanged " + inv.totalCents());
        check(inv.totalCents() == 500 && bigger.totalCents() == 900, "wither");

        Set<Invoice> set = new HashSet<>(List.of(inv));
        check(set.contains(new Invoice("INV-1", 500, List.of("apples", "pears"))), "equal value found in HashSet");

        Set<BrokenKey> broken = new HashSet<>();
        broken.add(new BrokenKey("a"));
        boolean found = broken.contains(new BrokenKey("a"));
        System.out.println("equals without hashCode: HashSet.contains(equal key) = " + found);
        check(!found, "broken contract is demonstrated (almost certainly a different bucket)");

        var rec = new InvoiceRecord("INV-2", 100, source);
        check(rec.equals(new InvoiceRecord("INV-2", 100, new ArrayList<>(source))), "record equality");
        System.out.println("record: " + rec);
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
