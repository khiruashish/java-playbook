import java.util.*;

/** Java 10: var infers the local variable type from the right-hand side. It is still static typing. */
public class J10_Var {

    public static void main(String[] args) {
        var ordersByCustomer = new HashMap<String, List<String>>();     // type is on the right — no repetition
        ordersByCustomer.put("asha", new ArrayList<>(List.of("O1", "O2")));

        for (var entry : ordersByCustomer.entrySet()) {                 // var in enhanced for
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }

        var total = 0;                                                  // int
        for (var i = 1; i <= 3; i++) total += i * 60;
        System.out.println("total = " + total);

        var trap = new ArrayList<>();       // bare diamond: this is ArrayList<Object>!
        trap.add("MILK");
        trap.add(42);                       // compiles — probably not what you meant
        System.out.println("bare diamond gives " + trap + " — always give the type argument with var");
    }
}
