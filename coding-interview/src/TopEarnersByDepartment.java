import java.util.*;
import java.util.stream.Collectors;

/** Problem (Streams round): for each department, the top 2 earners, the average salary, and the highest paid. */
public class TopEarnersByDepartment {

    record Employee(String name, String dept, long salary) { }

    static Map<String, List<String>> topNNames(List<Employee> staff, int n) {
        return staff.stream().collect(Collectors.groupingBy(
                Employee::dept,
                TreeMap::new,                                                  // sorted keys = deterministic output
                Collectors.collectingAndThen(Collectors.toList(), list -> list.stream()
                        .sorted(Comparator.comparingLong(Employee::salary).reversed().thenComparing(Employee::name))
                        .limit(n)
                        .map(Employee::name)
                        .toList())));
    }

    static Map<String, Double> averageSalary(List<Employee> staff) {
        return staff.stream().collect(Collectors.groupingBy(Employee::dept, TreeMap::new, Collectors.averagingLong(Employee::salary)));
    }

    static Map<String, Optional<Employee>> highestPaid(List<Employee> staff) {
        return staff.stream().collect(Collectors.groupingBy(Employee::dept, TreeMap::new,
                Collectors.maxBy(Comparator.comparingLong(Employee::salary))));
    }

    /** Bonus: partitioningBy always returns both keys (true and false), even if one side is empty. */
    static Map<Boolean, Long> countAbove(List<Employee> staff, long threshold) {
        return staff.stream().collect(Collectors.partitioningBy(e -> e.salary() > threshold, Collectors.counting()));
    }

    public static void main(String[] args) {
        List<Employee> staff = List.of(
                new Employee("Asha", "ENG", 210), new Employee("Ben", "ENG", 180), new Employee("Chen", "ENG", 240),
                new Employee("Dev", "OPS", 120), new Employee("Eva", "OPS", 150),
                new Employee("Femi", "SALES", 90));

        var top = topNNames(staff, 2);
        var avg = averageSalary(staff);
        var max = highestPaid(staff);
        System.out.println("top 2      = " + top);
        System.out.println("average    = " + avg);
        max.forEach((d, e) -> System.out.println("highest " + d + " = " + e.map(Employee::name).orElse("-")));
        System.out.println("above 150  = " + countAbove(staff, 150));

        check(top.get("ENG").equals(List.of("Chen", "Asha")), "ENG top 2");
        check(top.get("SALES").equals(List.of("Femi")), "fewer than N is fine");
        check(avg.get("OPS") == 135.0, "OPS average");
        check(countAbove(staff, 150).get(true) == 3, "partitioning");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
