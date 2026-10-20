/** Start threads, wait for them with join(), and see that start() and run() are different. */
public class C01_ThreadBasics {

    public static void main(String[] args) throws InterruptedException {
        Runnable pack = () -> System.out.println("packing order on " + Thread.currentThread().getName());

        Thread t1 = new Thread(pack, "packer-1");
        Thread t2 = Thread.ofPlatform().name("packer-2").unstarted(pack);   // Java 21 builder
        t1.start();                                   // start(): a NEW thread runs the task
        t2.start();
        t1.join();                                    // wait for both to finish
        t2.join();

        new Thread(pack, "never-started").run();      // run(): just a method call on THIS thread
        System.out.println("state after finishing: " + t1.getState());
    }
}
