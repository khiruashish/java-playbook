/**
 * count++ is three steps (read, add, write), so two threads can lose updates. synchronized fixes it.
 * Thread.yield() widens the window so the race is visible on a single-core machine too.
 */
public class C02_RaceAndSynchronized {

    static int unsafeCount = 0, safeCount = 0;
    static final Object LOCK = new Object();

    public static void main(String[] args) throws InterruptedException {
        Runnable unsafe = () -> { for (int i = 0; i < 5_000; i++) { int v = unsafeCount; Thread.yield(); unsafeCount = v + 1; } };
        Runnable safe   = () -> { for (int i = 0; i < 5_000; i++) synchronized (LOCK) { int v = safeCount; Thread.yield(); safeCount = v + 1; } };

        runTwice(unsafe);
        runTwice(safe);
        System.out.println("expected       10000");
        System.out.println("unsynchronized " + unsafeCount + "   <- lost updates");
        System.out.println("synchronized   " + safeCount);
    }

    static void runTwice(Runnable r) throws InterruptedException {
        Thread a = new Thread(r), b = new Thread(r);
        a.start(); b.start(); a.join(); b.join();
    }
}
