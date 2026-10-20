import java.util.*;
import java.util.stream.Collectors;

/** Java 10: List.copyOf for snapshots, and collectors that produce unmodifiable results. */
public class J10_CopyOf {

    public static void main(String[] args) {
        List<String> mutable = new ArrayList<>(List.of("MILK", "RICE"));
        List<String> snapshot = List.copyOf(mutable);
        List<String> view = Collections.unmodifiableList(mutable);

        mutable.add("TEA");
        System.out.println("snapshot (copyOf):        " + snapshot + "  <- unaffected");
        System.out.println("view (unmodifiableList):  " + view + "  <- sees the change");

        List<String> upper = mutable.stream().map(String::toUpperCase).collect(Collectors.toUnmodifiableList());
        try { upper.add("JAM"); } catch (UnsupportedOperationException e) { System.out.println("toUnmodifiableList() result is immutable"); }
    }
}
