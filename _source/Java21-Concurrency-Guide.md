---
title: Java 21 — Concurrency & Virtual Threads
tags: [java, java21, virtual-threads, structured-concurrency]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: senior → architect
related: [threading-enterprise-guide.md]
---

## Java 21 Concurrency — Virtual Threads & Structured Concurrency (Beginner → Enterprise)

---

## 1. Purpose & Audience

- **Purpose**: Provide a complete, practical guide to **Java 21 concurrency**, focused on:
  - **Virtual threads** (JEP 444, final).
  - **Structured concurrency** (JEP 453, preview).
  - How these concepts change the way we design enterprise backends.
  - How to use them in **Spring Boot 3** microservices.
- **Audience**:
  - Beginners who know classic Java (`Thread`, `ExecutorService`) and want to understand Java 21.
  - Senior/architect‑level engineers designing high‑throughput services.

For classic threading (platform threads, locks, executors, `CompletableFuture`), see `Threading-Basic-Guide.md` and `Threading-Enterprise-Guide.md`.

---

## 2. High‑Level Overview: What Changed in Java 21

### 2.1 Platform threads vs virtual threads

- **Platform thread**:
  - 1:1 mapping to an **OS thread**.
  - Expensive to create.
  - Limited in number (hundreds or thousands).
  - Blocking I/O (e.g. JDBC, HTTP) **blocks the OS thread**.

- **Virtual thread**:
  - A **user‑mode** thread managed by the JVM.
  - M:N mapping: many virtual threads scheduled onto a small pool of carrier (platform) threads.
  - Very cheap to create and park/unpark.
  - Blocking I/O **parks the virtual thread**; carrier thread is released for other tasks.

Conceptual diagram:

```text
Before Java 21 (platform threads only)

 Client  ->  Thread-1 (OS)
 Client  ->  Thread-2 (OS)
 Client  ->  Thread-3 (OS)
   ... limited by OS threads; blocking ties up OS threads


Java 21 with virtual threads

 Many Clients  ->  VirtualThread-1  \
                ->  VirtualThread-2  \
                ->  VirtualThread-3   > scheduled on small pool of carrier threads
                ->  ...              /
```

### 2.2 Structured concurrency (preview)

Traditional concurrency:
- You start child threads / tasks in multiple places.
- You often **forget to join/cancel** them.
- Errors bubble up in unpredictable ways.

**Structured concurrency**:
- Treat a group of tasks as a single **unit of work** with a bounded lifetime.
- If any subtask fails, you can **cancel siblings** and propagate errors to the parent.
- Java 21 preview API: `StructuredTaskScope` (JEP 453).

Conceptual diagram:

```text
Request Handler
  ├─ Task A: load user
  ├─ Task B: load orders
  └─ Task C: load recommendations

Structured scope ensures:
  - All 3 tasks complete (or fail) before handler returns.
  - Failures cancel the remaining tasks.
  - No orphan background threads.
```

---

## 3. Virtual Threads — Concepts & Basics

### 3.1 Definition

- In Java 21, **virtual threads** are a standard feature that enable:
  - **Thread‑per‑request** style with millions of concurrent requests.
  - Using **simple blocking code** while still scaling I/O‑bound workloads.

### 3.2 Why virtual threads were introduced

Problems in classic Java:
- To handle many concurrent blocking operations, you:
  - Either build **asynchronous** or **reactive** systems (complex).
  - Or use large thread pools (risk of exhaustion, lots of context switching).

Virtual threads:
- Solve the **“many blocking tasks”** problem with:
  - Cheap, parking/unparking of threads.
  - Project Loom‑inspired scheduler inside the JVM.

---

## 4. Creating and Using Virtual Threads

### 4.1 Direct creation with `Thread.ofVirtual`

```java
public class VirtualThreadDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread v = Thread.ofVirtual().name("vt-1").start(() -> {
            System.out.println("Running in " + Thread.currentThread());
        });
        v.join();
    }
}
```

### 4.2 Virtual thread per task executor

```java
import java.util.concurrent.*;

public class VirtualExecutorDemo {
    public static void main(String[] args) throws Exception {
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<String> f1 = executor.submit(() -> loadUser("1"));
            Future<Integer> f2 = executor.submit(() -> loadOrderCount("1"));
            System.out.println(f1.get() + " -> " + f2.get());
        }
    }

    static String loadUser(String id) throws InterruptedException {
        // Simulate blocking call (DB/HTTP)
        Thread.sleep(100);
        return "User(id=" + id + ")";
    }

    static Integer loadOrderCount(String id) throws InterruptedException {
        Thread.sleep(100);
        return 5;
    }
}
```

**Why this is powerful**:
- Each `submit` gets its own virtual thread.
- `Thread.sleep`/blocking I/O **parks** the virtual thread and frees the carrier.

---

## 5. Performance & Best Practices for Virtual Threads

### 5.1 Performance characteristics

- **Creation**: thousands or millions of virtual threads per JVM.
- **Blocking cost**: cheap, because blocking is just “parking” on a scheduler, not an OS thread.
- **Context switching**: lighter than OS threads, but still not free.

### 5.2 When to use virtual threads

**Use for:**
- I/O‑bound work (DB queries, HTTP calls, messaging).
- Server request handlers using blocking style (servlets, Spring MVC).
- Background jobs with many small blocking operations.

**Avoid for:**
- Purely CPU‑bound parallelism (use a small platform thread pool).
- Heavy `ThreadLocal` usage (many threads → more memory).

### 5.3 Best practices

- Keep virtual thread tasks **short and focused**.
- Avoid sharing mutable state; treat tasks as mostly independent.
- Minimize use of `ThreadLocal`; prefer request‑scoped context mechanisms (e.g., `ScopedValue` in preview or frameworks’ context).

Common mistakes:
- Assuming virtual threads magically make all code fast — heavy CPU work will still saturate cores.
- Mixing blocking I/O with reactive pipelines in complex ways; keep the model consistent.

---

## 6. Structured Concurrency with `StructuredTaskScope` (Preview)

> **Note**: `StructuredTaskScope` is a **preview** in Java 21. You must enable preview features.

### 6.1 Key types (Java 21 preview)

- `StructuredTaskScope`: lifecycle for a group of subtasks.
- `StructuredTaskScope.ShutdownOnFailure`:
  - Cancel remaining tasks when any fails.
- `StructuredTaskScope.ShutdownOnSuccess`:
  - Return the first successful result, cancel the rest.
- `StructuredTaskScope.Subtask<T>`:
  - Handle to a forked task, with result or exception.
- `StructuredTaskScope.Subtask.State`:
  - `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`.

### 6.2 Simple structured concurrency example

```java
import java.util.concurrent.StructuredTaskScope;

public class StructuredDemo {

    static String loadUser(String id) throws InterruptedException {
        Thread.sleep(100);
        return "User(" + id + ")";
    }

    static Integer loadOrderCount(String id) throws InterruptedException {
        Thread.sleep(100);
        return 5;
    }

    public static void main(String[] args) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            StructuredTaskScope.Subtask<String> userTask =
                    scope.fork(() -> loadUser("1"));
            StructuredTaskScope.Subtask<Integer> orderTask =
                    scope.fork(() -> loadOrderCount("1"));

            scope.join();           // wait for all
            scope.throwIfFailed();  // propagate error if any

            String user = userTask.get();
            Integer orders = orderTask.get();
            System.out.println(user + " -> " + orders);
        }
    }
}
```

### 6.3 How to compile & run (preview)

```bash
javac --release 21 --enable-preview StructuredDemo.java
java --enable-preview StructuredDemo
```

**Example output**

```text
User(1) -> 5
```

### 6.4 Structured concurrency vs manual `ExecutorService`

**Without structured concurrency**:
- You submit tasks to an `ExecutorService`.
- You manually track `Future`s.
- Error handling/cancellation often ad‑hoc.

**With structured concurrency**:
- Tasks are scoped to a block.
- Lifetimes are clearly bounded.
- One place to join/wait and handle exceptions.

---

## 7. Spring Boot 3 + Java 21 Virtual Threads

### 7.1 Enabling virtual threads in Spring Boot 3.2+

`application.yml`:

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

This instructs Spring Boot (Tomcat/Jetty/Undertow, where supported) to use **virtual threads** for request handling.

### 7.2 Service layer example (blocking I/O)

```java
@Service
public class UserService {

    public String loadUser(String id) {
        // Simulate blocking DB or HTTP call
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "User(id=" + id + ")";
    }
}
```

### 7.3 Controller example

```java
@RestController
public class UserController {

    private final UserService service;

    public UserController(UserService service) {
        this.service = service;
    }

    @GetMapping("/user/{id}")
    public String getUser(@PathVariable String id) {
        return service.loadUser(id);
    }
}
```

With virtual threads enabled:
- Each HTTP request can run on its own virtual thread.
- **Blocking** inside `loadUser` no longer ties up a platform thread, allowing high concurrency.

---

## 8. Using StructuredTaskScope in a Spring Boot Service (Preview)

> Typically, you will combine virtual threads for request handling with structured concurrency in your service layer.

```java
@Service
public class UserProfileService {

    public UserProfile loadProfile(String id) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var userTask = scope.fork(() -> loadUser(id));
            var ordersTask = scope.fork(() -> loadOrders(id));
            var recommendationsTask = scope.fork(() -> loadRecommendations(id));

            scope.join();
            scope.throwIfFailed();

            return new UserProfile(
                userTask.get(),
                ordersTask.get(),
                recommendationsTask.get()
            );
        }
    }

    private User loadUser(String id) {
        // blocking DB/HTTP call
        return new User(id, "Alice");
    }

    private List<Order> loadOrders(String id) {
        // blocking DB/HTTP call
        return List.of(new Order("order-1"));
    }

    private List<String> loadRecommendations(String id) {
        // blocking remote call
        return List.of("item-1", "item-2");
    }
}
```

**Benefits**:
- Reads naturally: “fork 3 tasks, wait, fail fast, aggregate”.
- No orphaned tasks; all are cancelled when scope closes or on failure.

---

## 9. Internal Mechanics (High‑Level)

### 9.1 Virtual threads scheduler

- Implementation uses:
  - A small pool of **carrier (platform) threads**.
  - A scheduler to run many virtual threads cooperatively.
- Blocking API calls (e.g. `SocketChannel.read`, `sleep`, `park`) are integrated so they **unmount** the virtual thread from its carrier.

High‑level pseudo‑diagram:

```text
Carrier Pool: [C1, C2, C3, C4]

Ready Queue: [VT-1, VT-2, VT-3, ... VT-N]

Scheduler:
  - Pick VT from Ready Queue, run on a carrier.
  - If VT blocks on I/O or sleep, park VT and put it back when ready.
```

### 9.2 StructuredTaskScope under the hood

- Creates **child tasks** (usually virtual threads) tied to the lifespan of the scope.
- `join()`:
  - Waits for all subtasks to complete (or be cancelled).
- `throwIfFailed()`:
  - Propagates first failure as an exception.
  - Cancels other subtasks (if using `ShutdownOnFailure`).

---

## 10. Migration & Design Guidance (Enterprise)

### 10.1 Migrating from classic thread pools

**Before**:

```java
ExecutorService pool = Executors.newFixedThreadPool(200);
Future<User> userF = pool.submit(() -> loadUser(id));
Future<List<Order>> ordersF = pool.submit(() -> loadOrders(id));
User user = userF.get();
List<Order> orders = ordersF.get();
```

**After (Java 21)**:

```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    Future<User> userF = executor.submit(() -> loadUser(id));
    Future<List<Order>> ordersF = executor.submit(() -> loadOrders(id));
    User user = userF.get();
    List<Order> orders = ordersF.get();
}
```

Or, in a structured scope (preview):

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var userTask = scope.fork(() -> loadUser(id));
    var ordersTask = scope.fork(() -> loadOrders(id));
    scope.join();
    scope.throwIfFailed();
    return new UserWithOrders(userTask.get(), ordersTask.get());
}
```

### 10.2 Choosing concurrency models

| Model | When to use |
|-------|-------------|
| Classic thread pool | Legacy code, CPU‑bound tasks, Java < 21 |
| Virtual threads | High‑concurrency, blocking I/O, thread‑per‑request style |
| Structured concurrency | Complex operations requiring parallel substeps with unified lifetime |
| CompletableFuture | When you need fine‑grained async composition or non‑blocking style |
| Reactive (WebFlux, Project Reactor) | End‑to‑end non‑blocking with backpressure; highly concurrent edge services |

### 10.3 Common pitfalls in enterprise migration

- Overloading the **common ForkJoinPool** (used by parallel streams and some CF methods) instead of using dedicated virtual thread executors.
- Forgetting that **database connection pools** or external limits still bound throughput, even if you have millions of virtual threads.
- Mixing too many concurrency paradigms (virtual threads, reactive, CF) in one service without clear boundaries.

---

## 11. Interview Positioning Summary

When discussing Java 21 in interviews:

- **Virtual threads**:
  - “They decouple the number of concurrent tasks from the number of OS threads, making blocking I/O scalable again.”
  - Show an example with `Executors.newVirtualThreadPerTaskExecutor()` and explain parking/unparking.

- **Structured concurrency**:
  - “It gives a structured way to fork and join multiple tasks as one unit, improving error handling and cancellation.”
  - Mention `StructuredTaskScope.ShutdownOnFailure` and how it simplifies multi‑call orchestration.

- **Spring Boot integration**:
  - “In Spring Boot 3.2+, I can enable virtual threads via `spring.threads.virtual.enabled=true` and keep my blocking service code, but scale concurrent requests.”

Combine this guide with your existing `Threading-Basic-Guide.md` and `Threading-Enterprise-Guide.md` to present a modern, end‑to‑end concurrency story in Java 21. 

