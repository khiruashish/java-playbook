import java.util.concurrent.*;

/** A BlockingQueue hands work from producers to consumers; put() waits when full, take() when empty. */
public class C09_ProducerConsumer {

    static final String POISON = "DONE";

    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<String> dispatchQueue = new ArrayBlockingQueue<>(2);   // small, so put() has to wait

        Thread producer = Thread.ofPlatform().start(() -> {
            try {
                for (int i = 1; i <= 5; i++) {
                    dispatchQueue.put("ORD-" + i);
                    System.out.println("placed    ORD-" + i);
                }
                dispatchQueue.put(POISON);                                  // tell the consumer to stop
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });

        Thread consumer = Thread.ofPlatform().start(() -> {
            try {
                for (String order = dispatchQueue.take(); !order.equals(POISON); order = dispatchQueue.take()) {
                    Thread.sleep(50);
                    System.out.println("dispatched " + order);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });

        producer.join();
        consumer.join();
        System.out.println("all orders dispatched, in order");
    }
}
