import java.util.random.RandomGenerator;

/** Java 17: one RandomGenerator interface over many algorithms; seeded runs are reproducible. */
public class J17_RandomGenerator {

    public static void main(String[] args) {
        RandomGenerator rng = RandomGenerator.of("L64X128MixRandom");
        System.out.println("algorithm: " + rng.getClass().getSimpleName());

        RandomGenerator seeded = RandomGenerator.of("Xoshiro256PlusPlus");
        System.out.println("bounded ints (1-6): " + java.util.stream.IntStream.range(0, 5)
            .map(i -> seeded.nextInt(1, 7)).allMatch(n -> n >= 1 && n <= 6));
        System.out.println("default generator: " + RandomGenerator.getDefault().getClass().getSimpleName());
    }
}
