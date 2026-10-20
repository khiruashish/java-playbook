import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Four checkout threads race to claim the same order. "if absent, then put" lets several win;
 * putIfAbsent lets exactly one win. Thread.yield() widens the gap between check and act.
 */
public class CheckThenAct {

    public static void main(String[] args) throws Exception {
        int trials = 500, brokenCheckThenAct = 0, brokenPutIfAbsent = 0;

        for (int t = 0; t < trials; t++) {
            if (winners(false) > 1) brokenCheckThenAct++;
            if (winners(true) > 1)  brokenPutIfAbsent++;
        }
        System.out.printf("containsKey() then put(): %3d of %d trials had MORE THAN ONE winner%n", brokenCheckThenAct, trials);
        System.out.printf("putIfAbsent():            %3d of %d trials had more than one winner%n", brokenPutIfAbsent, trials);
    }

    static int winners(boolean atomic) throws Exception {
        ConcurrentHashMap<String, String> claims = new ConcurrentHashMap<>();
        AtomicInteger winners = new AtomicInteger();
        CyclicBarrier lineUp = new CyclicBarrier(4);
        Thread[] threads = new Thread[4];
        for (int i = 0; i < 4; i++) {
            String worker = "worker-" + i;
            threads[i] = Thread.ofPlatform().start(() -> {
                try { lineUp.await(); } catch (Exception e) { return; }
                if (atomic) {
                    if (claims.putIfAbsent("ORD-1", worker) == null) winners.incrementAndGet();
                } else if (!claims.containsKey("ORD-1")) {
                    Thread.yield();                               // the gap between check and act
                    claims.put("ORD-1", worker);
                    winners.incrementAndGet();
                }
            });
        }
        for (Thread th : threads) th.join();
        return winners.get();
    }
}
