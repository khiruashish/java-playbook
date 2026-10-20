import java.util.*;
import java.util.concurrent.*;

/** Java 19: HashMap.newHashMap sizes correctly; Future.state() and resultNow() inspect finished futures. */
public class J19_SizedMapsAndFutureState {

    public static void main(String[] args) throws Exception {
        // new HashMap<>(100) takes a CAPACITY: it resizes before 100 entries. newHashMap takes an entry COUNT.
        Map<String, Integer> sized = HashMap.newHashMap(100);          // holds 100 entries with no resize
        for (int i = 0; i < 100; i++) sized.put("SKU-" + i, i);
        System.out.println("newHashMap(100) holds " + sized.size() + " entries without resizing");

        try (ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<String> ok = pool.submit(() -> "RECEIPT-1");
            Future<String> bad = pool.submit(() -> { throw new IllegalStateException("vendor down"); });
            Thread.sleep(100);
            System.out.println("ok.state()  = " + ok.state() + ", resultNow()    = " + ok.resultNow());
            System.out.println("bad.state() = " + bad.state() + ", exceptionNow() = " + bad.exceptionNow().getMessage());
        }
    }
}
