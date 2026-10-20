---
title: Java Threading — Basics
tags: [java, threads, concurrency, synchronized]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: beginner → intermediate
related: [threading-enterprise-guide.md]
---

## Java Threading — Basics Guide (Java 21)

---

## 1. Purpose & Audience

- **Purpose**: Introduce Java threading from first principles:
  - What a thread is and how it runs.
  - How to create and coordinate threads safely.
  - How to avoid the most common pitfalls (race conditions, deadlocks).
- **Audience**:
  - Developers who know basic Java and want a solid mental model of threads.
  - People preparing for interviews where classic Java threading is expected.
- **Scope**:
  - Focus on **core concepts** and **classic APIs** (`Thread`, `Runnable`, `synchronized`, `wait/notify`, `ExecutorService`).
  - Java 21 is the target runtime, but this guide avoids advanced topics like virtual threads (see the enterprise guide for that).

---

## 2. What Is a Thread?

- A **thread** is a single sequence of execution inside a process.
- A Java program always starts with at least one thread: **`main`**.
- More threads allow **concurrency**:
  - Run tasks in parallel on multiple cores.
  - Keep the application responsive while doing work in the background.

### 2.1 Thread vs process

- **Process**: Has its own memory space; the JVM process is one example.
- **Thread**: Shares memory with other threads in the same process.
  - Advantage: fast communication through shared memory.
  - Risk: race conditions if shared state is not synchronized properly.

---

## 3. Creating Threads

### 3.1 Extending `Thread`

Override `run()`, then call `start()` to run in a new thread.

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Running in " + Thread.currentThread().getName());
    }
}

public class ThreadDemo1 {
    public static void main(String[] args) throws InterruptedException {
        MyThread t = new MyThread();
        t.start();  // runs in a new thread
        t.join();   // wait for completion
        System.out.println("Done in " + Thread.currentThread().getName());
    }
}
```

**Key points**:
- `start()` creates a new OS/platform thread and eventually calls `run()`.
- Calling `run()` directly will **not** start a new thread; it runs in the current thread.

### 3.2 Implementing `Runnable`

Preferred for composition (your class can still extend another class). Use a lambda for brevity.

```java
public class ThreadDemo2 {
    public static void main(String[] args) throws InterruptedException {
        Runnable task = () -> {
            System.out.println("Hello from " + Thread.currentThread().getName());
        };

        Thread t = new Thread(task);
        t.start();
        t.join();
    }
}
```

---

## 4. Thread Lifecycle & Coordination

### 4.1 Lifecycle states

Conceptually, a thread goes through these states:

- **NEW** – constructed but not started.
- **RUNNABLE** – ready or running on a CPU.
- **BLOCKED** – waiting to acquire a monitor (e.g. enters `synchronized` block).
- **WAITING / TIMED_WAITING** – waiting for another thread (e.g. `wait`, `join`, `sleep`).
- **TERMINATED** – `run()` method has returned or thrown an uncaught exception.

### 4.2 `join()` — waiting for completion

`join()` makes the current thread wait until another thread finishes.

```java
public class JoinDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t = new Thread(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            System.out.println("Worker finished");
        });

        t.start();
        System.out.println("Main waiting");
        t.join();
        System.out.println("Main continues");
    }
}
```

Possible output:
```
Main waiting
Worker finished
Main continues
```

### 4.3 Sleeping & interrupting

- `Thread.sleep(ms)` pauses the current thread.
- `interrupt()` sets an interrupt flag and may wake blocking calls like `sleep()`, `wait()`, or blocking I/O.

```java
public class InterruptDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t = new Thread(() -> {
            try {
                Thread.sleep(5_000);
                System.out.println("Finished sleep");
            } catch (InterruptedException e) {
                System.out.println("Interrupted during sleep");
                Thread.currentThread().interrupt();
            }
        });

        t.start();
        Thread.sleep(100);
        t.interrupt();
        t.join();
    }
}
```

**Output:** `Interrupted during sleep`

### 4.4 Daemon vs user threads

- **User threads** keep the JVM alive.
- **Daemon threads** do not; when only daemon threads remain, the JVM exits.

```java
Thread daemon = new Thread(() -> {
    while (true) {
        System.out.println("Daemon running");
        try { Thread.sleep(100); } catch (InterruptedException e) { break; }
    }
});
daemon.setDaemon(true);
daemon.start();
Thread.sleep(300);
System.out.println("Main done"); // JVM may exit shortly after
```

Use daemon threads for background housekeeping, not for critical work.

---

## 5. Shared State & Synchronization

### 5.1 Race conditions

A **race condition** occurs when outcome depends on the interleaving of threads accessing shared state.

Example: non-thread-safe counter:

```java
class Counter {
    private int count;

    void increment() {
        count++; // not atomic
    }

    int get() {
        return count;
    }
}

public class RaceDemo {
    public static void main(String[] args) throws InterruptedException {
        Counter c = new Counter();
        Thread t1 = new Thread(() -> { for (int i = 0; i < 10_000; i++) c.increment(); });
        Thread t2 = new Thread(() -> { for (int i = 0; i < 10_000; i++) c.increment(); });
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println("Result: " + c.get());
    }
}
```

Expected value is `20000`, but actual result is usually less due to lost updates.

### 5.2 `synchronized`

`synchronized` enforces mutual exclusion and establishes a **happens-before** relationship for visibility.

```java
class SyncCounter {
    private int count;

    public synchronized void increment() {
        count++;
    }

    public synchronized int get() {
        return count;
    }
}

public class SyncDemo {
    public static void main(String[] args) throws InterruptedException {
        SyncCounter c = new SyncCounter();
        Thread t1 = new Thread(() -> { for (int i = 0; i < 10_000; i++) c.increment(); });
        Thread t2 = new Thread(() -> { for (int i = 0; i < 10_000; i++) c.increment(); });
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println("Result: " + c.get()); // always 20000
    }
}
```

You can synchronize methods or blocks:

```java
void increment() {
    synchronized (this) {
        count++;
    }
}
```

### 5.3 `volatile`

- `volatile` guarantees **visibility**, not atomicity.
- Writes to a volatile variable are visible to other threads that subsequently read it.

```java
class Flag {
    volatile boolean running = true;
}

public class VolatileDemo {
    public static void main(String[] args) throws InterruptedException {
        Flag flag = new Flag();

        Thread t = new Thread(() -> {
            while (flag.running) {
                // busy loop
            }
            System.out.println("Stopped");
        });

        t.start();
        Thread.sleep(100);
        flag.running = false; // visible to t
        t.join();
    }
}
```

**Important**: For compound actions like `count++`, `volatile` alone is **not enough**. Use `synchronized` or `AtomicInteger`.

### 5.4 Wait/notify basics

Use `wait()` and `notify()` to coordinate producer/consumer-like workflows.

```java
class Buffer {
    private String value;
    private boolean hasValue = false;

    public synchronized void put(String v) throws InterruptedException {
        while (hasValue) {
            wait();
        }
        value = v;
        hasValue = true;
        notifyAll();
    }

    public synchronized String take() throws InterruptedException {
        while (!hasValue) {
            wait();
        }
        hasValue = false;
        notifyAll();
        return value;
    }
}

public class WaitNotifyDemo {
    public static void main(String[] args) throws InterruptedException {
        Buffer buffer = new Buffer();

        Thread producer = new Thread(() -> {
            try {
                buffer.put("hello");
                System.out.println("Produced");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        Thread consumer = new Thread(() -> {
            try {
                String v = buffer.take();
                System.out.println("Consumed: " + v);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        consumer.start();
        Thread.sleep(50);
        producer.start();
        producer.join();
        consumer.join();
    }
}
```

---

## 6. Deadlocks — Basics & Prevention

### 6.1 Simple deadlock

```java
public class DeadlockBasic {
    private static final Object A = new Object();
    private static final Object B = new Object();

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            synchronized (A) {
                sleep(50);
                synchronized (B) {
                    System.out.println("T1 got both");
                }
            }
        });

        Thread t2 = new Thread(() -> {
            synchronized (B) {
                sleep(50);
                synchronized (A) {
                    System.out.println("T2 got both");
                }
            }
        });

        t1.start();
        t2.start();
        t1.join(1000);
        t2.join(1000);
        System.out.println("If you don't see 'got both', likely deadlock");
    }

    private static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) {}
    }
}
```

### 6.2 Prevention via lock ordering

Always acquire locks in the same global order:

```java
Object A = new Object();
Object B = new Object();

Runnable task = () -> {
    synchronized (A) {
        synchronized (B) {
            System.out.println(Thread.currentThread().getName() + " safe");
        }
    }
};

Thread t1 = new Thread(task, "T1");
Thread t2 = new Thread(task, "T2");
t1.start(); t2.start();
```

---

## 7. Executors & Thread Pools (Classic)

### 7.1 Why executors?

- Managing raw threads manually is error-prone.
- Thread pools:
  - Reuse threads across tasks.
  - Limit concurrency (avoid creating thousands of OS threads).

### 7.2 Fixed thread pool example

```java
import java.util.concurrent.*;

public class ExecutorBasic {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService exec = Executors.newFixedThreadPool(2);

        for (int i = 0; i < 5; i++) {
            int id = i;
            exec.submit(() -> {
                System.out.println("Task " + id + " on " + Thread.currentThread().getName());
            });
        }

        exec.shutdown();
        exec.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println("All tasks done");
    }
}
```

### 7.3 `Callable` and `Future`

```java
ExecutorService exec = Executors.newSingleThreadExecutor();
Future<Integer> f = exec.submit(() -> {
    Thread.sleep(100);
    return 42;
});
System.out.println("Result: " + f.get()); // blocks until result is ready
exec.shutdown();
```

---

## 8. Best Practices (Basics)

- **Prefer `ExecutorService` over manual thread creation** for many tasks.
- **Avoid shared mutable state**; if you must share, use `synchronized`, `java.util.concurrent` utilities, or atomics.
- **Never ignore `InterruptedException`**:
  - Restore interrupt status with `Thread.currentThread().interrupt()`.
- **Keep critical sections small**:
  - Minimize code inside `synchronized` blocks.
- **Use higher-level concurrency utilities**:
  - `BlockingQueue`, `Semaphore`, `CountDownLatch`, `ConcurrentHashMap`, etc.

For virtual threads, structured concurrency, and Spring Boot integration, see the **enterprise threading guide**. 

