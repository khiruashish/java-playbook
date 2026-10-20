import java.util.List;
import java.util.function.*;

/** Java 11: Predicate.not reads better in method-reference chains; var is allowed in lambda parameters. */
public class J11_PredicateNotAndVarLambdas {

    public static void main(String[] args) {
        List<String> skus = List.of("MILK", "", "RICE", " ", "TEA");
        System.out.println(skus.stream().filter(Predicate.not(String::isBlank)).toList());

        // var in lambda parameters mainly exists so you can annotate them, e.g. (@NonNull var s)
        BiFunction<Integer, Integer, Integer> total = (var qty, var price) -> qty * price;
        System.out.println("total = " + total.apply(3, 60));
    }
}
