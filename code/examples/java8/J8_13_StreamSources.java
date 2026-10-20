import java.util.*;
import java.util.stream.*;

/** Where streams come from: collections, arrays, ranges, and generated or iterated sequences. */
public class J8_13_StreamSources {

    public static void main(String[] args) {
        System.out.println(Stream.of("MILK", "RICE").toList());
        System.out.println(Arrays.stream(new int[] {3, 1, 2}).sorted().boxed().toList());
        System.out.println(IntStream.range(0, 5).boxed().toList() + "  range excludes the end");
        System.out.println(IntStream.rangeClosed(1, 5).boxed().toList() + "  rangeClosed includes it");
        System.out.println(Stream.iterate(1, n -> n * 2).limit(8).toList() + "  iterate (infinite, so limit)");
        System.out.println(Stream.generate(() -> "ORD").limit(3).collect(Collectors.joining("-")));
        System.out.println("chars: " + "MILK".chars().mapToObj(c -> String.valueOf((char) c)).toList());
    }
}
