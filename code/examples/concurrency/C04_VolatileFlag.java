/** volatile makes one thread's write visible to another — the standard "please stop" flag. */
public class C04_VolatileFlag {

    static volatile boolean running = true;      // without volatile the worker might never see the change

    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            long processed = 0;
            while (running) processed++;
            System.out.println("worker saw running=false and stopped");
        });
        worker.start();
        Thread.sleep(200);
        running = false;                          // visible to the worker immediately
        worker.join(2_000);
        System.out.println("worker alive? " + worker.isAlive());
        System.out.println("Note: volatile gives visibility, NOT atomicity — count++ on a volatile still loses updates.");
    }
}
