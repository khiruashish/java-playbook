import java.util.List;
import java.util.stream.LongStream;

/** Parallel streams: same result for CPU work on large data — but order and side effects need care. */
public class J8_12_ParallelStreams {

    public static void main(String[] args) {
        long sequential = LongStream.rangeClosed(1, 5_000_000).sum();
        long parallel   = LongStream.rangeClosed(1, 5_000_000).parallel().sum();
        System.out.println("sums equal: " + (sequential == parallel) + " (" + parallel + ")");

        List<Integer> nums = List.of(1, 2, 3, 4, 5, 6, 7, 8);
        System.out.println("forEachOrdered keeps encounter order: ");
        nums.parallelStream().forEachOrdered(n -> System.out.print(n + " "));
        System.out.println("\ncollected results keep order too:     " + nums.parallelStream().map(n -> n * n).toList());

        System.out.println("\nRules: use parallel() only for large, CPU-bound work with no shared mutable state.");
        System.out.println("Never for blocking I/O — it runs on the shared ForkJoinPool.commonPool().");
    }
}
