import java.util.List;
import java.util.stream.Collectors;

/** Java 12: Collectors.teeing runs two collectors in one pass and combines their results. */
public class J12_Teeing {

    record Range(int min, int max) { }

    public static void main(String[] args) {
        List<Integer> prices = List.of(60, 450, 120, 90, 380);
        Range range = prices.stream().collect(Collectors.teeing(
            Collectors.minBy(Integer::compare),
            Collectors.maxBy(Integer::compare),
            (min, max) -> new Range(min.orElseThrow(), max.orElseThrow())));
        System.out.println(range);

        double avg = prices.stream().collect(Collectors.teeing(
            Collectors.summingInt(p -> p), Collectors.counting(), (sum, n) -> (double) sum / n));
        System.out.println("average = " + avg);
    }
}
