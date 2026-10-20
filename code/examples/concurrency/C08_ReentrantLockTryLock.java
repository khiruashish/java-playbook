import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

/** ReentrantLock can give up after a timeout — synchronized cannot. unlock() always goes in finally. */
public class C08_ReentrantLockTryLock {

    static final ReentrantLock stockLock = new ReentrantLock();

    public static void main(String[] args) throws InterruptedException {
        Thread slow = Thread.ofPlatform().start(() -> {
            stockLock.lock();
            try { Thread.sleep(1_000); } catch (InterruptedException ignored) { }
            finally { stockLock.unlock(); }
        });
        Thread.sleep(100);                                      // let the slow thread grab the lock

        if (stockLock.tryLock(200, TimeUnit.MILLISECONDS)) {
            try { System.out.println("reserved stock"); }
            finally { stockLock.unlock(); }
        } else {
            System.out.println("could not get the lock in 200 ms — tell the customer to retry instead of hanging");
        }
        slow.join();
    }
}
