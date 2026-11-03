import java.util.*;
import java.util.function.Predicate;

/** Problem: write generic utilities with the right bounds: max(), copy(), filter(); explain PECS. */
public class GenericsPecs {

    /** T extends Comparable<? super T>: works for types that inherit compareTo from a supertype. */
    static <T extends Comparable<? super T>> T max(Collection<? extends T> items) {
        Iterator<? extends T> it = items.iterator();
        if (!it.hasNext()) throw new NoSuchElementException("empty");
        T best = it.next();
        while (it.hasNext()) { T x = it.next(); if (x.compareTo(best) > 0) best = x; }
        return best;
    }

    /** PECS: Producer Extends (we read from src), Consumer Super (we write into dst). */
    static <T> void copy(List<? super T> dst, List<? extends T> src) {
        for (T t : src) dst.add(t);
    }

    static <T> List<T> filter(Collection<? extends T> items, Predicate<? super T> keep) {
        List<T> out = new ArrayList<>();
        for (T t : items) if (keep.test(t)) out.add(t);
        return out;
    }

    // A class hierarchy where compareTo is defined on the supertype only
    static class Fruit implements Comparable<Fruit> {
        final int weight;
        Fruit(int weight) { this.weight = weight; }
        public int compareTo(Fruit o) { return Integer.compare(weight, o.weight); }
        public String toString() { return getClass().getSimpleName() + "(" + weight + ")"; }
    }
    static class Apple extends Fruit { Apple(int w) { super(w); } }

    public static void main(String[] args) {
        List<Apple> apples = List.of(new Apple(120), new Apple(180), new Apple(150));
        Apple heaviest = max(apples);                  // needs Comparable<? super T>: Apple is Comparable<Fruit>
        System.out.println("max(apples) = " + heaviest);
        check(heaviest.weight == 180, "max");

        List<Fruit> basket = new ArrayList<>();
        List<Object> anything = new ArrayList<>();
        copy(basket, apples);                          // List<Fruit> consumes Apples
        copy(anything, apples);                        // List<Object> too
        System.out.println("copy into List<Fruit>  = " + basket);
        System.out.println("copy into List<Object> = " + anything);

        Predicate<Object> notNull = Objects::nonNull;  // a Predicate<Object> can filter apples (? super T)
        Predicate<Fruit> heavy = f -> f.weight > 130;
        System.out.println("filter(heavy)          = " + filter(apples, heavy));
        check(filter(apples, notNull).size() == 3 && filter(apples, heavy).size() == 2, "filter with supertype predicates");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
