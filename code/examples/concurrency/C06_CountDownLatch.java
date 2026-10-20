import java.util.List;
import java.util.concurrent.*;

/** Wait until N things have happened — e.g. all vendor connections are ready before taking orders. */
public class C06_CountDownLatch {

    public static void main(String[] args) throws InterruptedException {
        List<String> vendors = List.of("FreshFarm", "DailyDairy", "GrainHub");
        CountDownLatch ready = new CountDownLatch(vendors.size());

        for (String v : vendors) {
            Thread.ofPlatform().start(() -> {
                sleep(100 + v.length() * 20);
                System.out.println("connected: " + v);
                ready.countDown();
            });
        }
        boolean allReady = ready.await(5, TimeUnit.SECONDS);
        System.out.println("all vendors ready = " + allReady + " — start accepting orders");
    }

    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
}
