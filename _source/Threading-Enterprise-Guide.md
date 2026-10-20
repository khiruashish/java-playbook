---
title: Java Threading — Enterprise
tags: [java, threads, virtual-threads, executors]
created: 2024-01-01
updated: 2026-06-14
status: stable
level: senior → architect
related: [threading-basic-guide.md]
---

## Java Threading — Enterprise & Java 21 Guide

---

## 1. Purpose & Audience

- **Purpose**: Provide a senior-level, production-focused guide to Java threading, including:
  - Modern concurrency design patterns.
  - Java 21 **virtual threads** and **structured concurrency**.
  - Integration with **Spring Boot 3** and microservices.
- **Audience**:
  - Experienced Java developers (5–10+ years).
  - Engineers designing or reviewing concurrent systems and services.
- **Scope**:
  - Builds on basics (Thread, synchronized, ExecutorService).
  - Focuses on **best practices** and **Java 21-era APIs**.

For introductory material (Thread/Runnable, synchronized, wait/notify, classic executors), see `Threading-Basic-Guide.md`.

---

## 2. Concurrency Design in Modern Java

### 2.1 Goals of concurrency design

- **Correctness**:
  - No data races, deadlocks, or lost updates.
  - Clear ownership of mutable state.
- **Performance**:
  - Use the right level of parallelism (CPU vs I/O bound).
  - Avoid contention and oversubscription.
- **Maintainability**:
  - Local reasoning: understand a concurrent unit in isolation.
  - Avoid “fire-and-forget” threads that outlive their logical scope.

### 2.2 High-level patterns

- **Task submission**: submit `Runnable`/`Callable` to an `ExecutorService`.
- **Futures & promises**: `Future`, `CompletableFuture`, structured concurrency.
- **Pipelines**: Streams + collectors + parallel streams (for CPU-bound).
- **Cooperative cancellation**: use interrupts, `cancel(true)`, or structured task scopes.

---

## 3. Executors, Futures, and CompletableFuture

### 3.1 Thread pool design

- **Platform thread pools**:
  - Bounded pools (`newFixedThreadPool`) for CPU-bound or safe I/O concurrency.
  - Unbounded pools (cached) risk resource exhaustion.

Guidelines:
- For **CPU-bound work**:
  - Size ≈ number of cores (`Runtime.getRuntime().availableProcessors()`).
- For **I/O-bound work**:
  - Pool size can be larger, but consider blocking time and backpressure.

### 3.2 `Callable`, `Future`, `invokeAll`, `invokeAny`

```java
ExecutorService exec = Executors.newFixedThreadPool(4);

Callable<String> t1 = () -> "T1";
Callable<String> t2 = () -> "T2";

List<Future<String>> futures = exec.invokeAll(List.of(t1, t2));
for (Future<String> f : futures) {
    System.out.println(f.get());
}

String first = exec.invokeAny(List.of(t1, t2)); // returns result of first completed
System.out.println("First: " + first);

exec.shutdown();
```

### 3.3 `CompletableFuture` patterns

**Basic chain**:

```java
CompletableFuture<String> result =
    CompletableFuture.supplyAsync(() -> "Hello")
        .thenApply(s -> s + " World")
        .thenApply(String::toUpperCase);

System.out.println(result.join()); // HELLO WORLD
```

**Composition and error handling**:

```java
CompletableFuture<String> userFuture = CompletableFuture.supplyAsync(() -> loadUser("u1"));
CompletableFuture<List<String>> ordersFuture = CompletableFuture.supplyAsync(() -> loadOrders("u1"));

CompletableFuture<UserWithOrders> combined =
    userFuture.thenCombine(ordersFuture, UserWithOrders::new)
              .exceptionally(ex -> {
                  // Fallback behavior
                  return new UserWithOrders(null, List.of());
              });
```

**allOf** and `anyOf`:

```java
CompletableFuture<String> a = CompletableFuture.supplyAsync(() -> "A");
CompletableFuture<String> b = CompletableFuture.supplyAsync(() -> "B");
CompletableFuture<Void> all = CompletableFuture.allOf(a, b);
all.join();
System.out.println(a.join() + b.join()); // AB
```

---

## 4. Java 21 Virtual Threads

### 4.1 Concept and mental model

- **Platform threads**:
  - Backed by OS threads.
  - Expensive to create; limited number (hundreds to thousands typical).
  - Blocking operations tie up the OS thread.

- **Virtual threads** (JEP 444):
  - Managed by the JVM, not the OS.
  - Extremely cheap to create; can run **hundreds of thousands or millions**.
  - Blocking operations (e.g. `Socket.read`, JDBC) **park the virtual thread**, freeing the carrier platform thread.

**Key point**: Virtual threads make **blocking code scalable** for I/O-bound workloads.

### 4.2 Creating virtual threads

#### 4.2.1 Directly with `Thread.ofVirtual`

```java
public class VirtualThreadDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread v = Thread.ofVirtual().start(() -> {
            System.out.println("Virtual: " + Thread.currentThread());
        });
        v.join();
    }
}
```

#### 4.2.2 Using `Executors.newVirtualThreadPerTaskExecutor`

```java
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Callable<String>> tasks = List.of(
        () -> Thread.currentThread().toString(),
        () -> Thread.currentThread().toString()
    );

    List<Future<String>> futures = exec.invokeAll(tasks);
    for (Future<String> f : futures) {
        System.out.println(f.get());
    }
}
```

### 4.3 When to use virtual threads

**Good fit**:
- I/O-bound services: HTTP calls, JDBC, messaging, file I/O.
- “Thread-per-request” programming model (e.g., traditional servlet-style web apps).
- Migrating from reactive back to blocking style when complexity is high and hardware is sufficient.

**Less benefit**:
- Heavy CPU-bound parallel work (still constrained by cores).
- When existing thread pools and reactive stacks are already well-tuned and simple.

### 4.4 Caveats and best practices with virtual threads

- Avoid **ThreadLocal-heavy designs** — virtual threads are cheap and numerous; many ThreadLocals can waste memory. Prefer **ScopedValue** for scoped context.
- Ensure **blocking calls are “virtual-thread-friendly”** (most JDK I/O APIs are; legacy native calls may not be).
- Keep the **thread-per-task style**:
  - You generally **do not** need a bounded pool for virtual threads.
  - Use `newVirtualThreadPerTaskExecutor()` or `Thread.ofVirtual().start(...)` directly.

---

## 5. Structured Concurrency (Java 21)

### 5.1 Motivation

Without structure:
- Tasks are spawned in different places.
- Cancellation and failures are hard to manage.
- “Child” threads may outlive the operation that spawned them (leaks).

Structured concurrency:
- Treat multiple concurrent tasks as a single **unit of work**.
- **Lifespan of child tasks is bounded** by their scope (like local variables).

### 5.2 `StructuredTaskScope` basics

#### 5.2.1 `ShutdownOnFailure`

Run tasks in parallel, cancel all if one fails:

```java
import java.util.concurrent.StructuredTaskScope;

public class ScopeDemo {
    record User(String id) {}
    record Orders(List<String> items) {}
    record UserProfile(User user, Orders orders) {}

    static User loadUser() { return new User("u1"); }
    static Orders loadOrders() { return new Orders(List.of("item1", "item2")); }

    public static UserProfile fetchProfile() throws InterruptedException {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var userTask = scope.fork(ScopeDemo::loadUser);
            var ordersTask = scope.fork(ScopeDemo::loadOrders);

            scope.join();            // wait for both
            scope.throwIfFailed();   // propagate exceptions, cancel others

            return new UserProfile(userTask.resultNow(), ordersTask.resultNow());
        }
    }
}
```

#### 5.2.2 `ShutdownOnSuccess`

Return when **any** task succeeds; cancel the rest.

```java
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
    var fromCache = scope.fork(() -> loadFromCache());
    var fromDb = scope.fork(() -> loadFromDatabase());

    scope.join();
    return scope.result(); // first successful result
}
```

---

## 6. Thread-Context Management: ThreadLocal vs ScopedValue

### 6.1 ThreadLocal (classic)

Stores data per-thread; virtual threads make this less attractive because:
- There can be many more threads.
- ThreadLocals must be cleaned up carefully to avoid leaks.

Example:

```java
static final ThreadLocal<String> requestId = new ThreadLocal<>();

void handle(String id) {
    requestId.set(id);
    try {
        // use requestId.get() in this thread
    } finally {
        requestId.remove();
    }
}
```

### 6.2 ScopedValue (Java 21)

- Bind a value to a **lexical scope** that child virtual threads can inherit.
- Automatically cleaned up at the end of the scope.

Conceptual example (not full code):

```java
import jdk.incubator.concurrent.ScopedValue; // preview in 21

static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();

void handle(String id) {
    ScopedValue.where(REQUEST_ID, id).run(() -> {
        // Inside this scope, REQUEST_ID.get() returns id
        doWork();
    });
}
```

Best practice:
- Prefer **ScopedValue** for contextual data with virtual threads.

---

## 7. Spring Boot 3 + Virtual Threads (Microservices)

This section shows a simple **two-microservice** setup:
- `orders-service` — HTTP endpoint that performs blocking calls (DB, external API).
- `payments-service` — downstream service called by `orders-service`.
- Both are configured to run **on virtual threads**.

### 7.1 orders-service: configuration & controller

#### 7.1.1 Maven/Gradle assumptions

- Spring Boot **3.2+**.
- Java **21**.

#### 7.1.2 Enable virtual threads (application.yml)

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

This tells Spring Boot to use **virtual threads** for request handling where supported.

#### 7.1.3 Application & configuration

```java
package com.example.orders;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class OrdersApplication {

    public static void main(String[] args) {
        SpringApplication.run(OrdersApplication.class, args);
    }

    @Bean
    RestClient paymentsClient() {
        return RestClient.builder()
                .baseUrl("http://localhost:8081") // payments-service
                .build();
    }
}
```

#### 7.1.4 Service using blocking HTTP + DB

```java
package com.example.orders;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Service
public class OrderService {

    private final JdbcTemplate jdbcTemplate;
    private final RestClient paymentsClient;

    public OrderService(JdbcTemplate jdbcTemplate, RestClient paymentsClient) {
        this.jdbcTemplate = jdbcTemplate;
        this.paymentsClient = paymentsClient;
    }

    public Map<String, Object> createOrder(String userId, int amount) {
        // Blocking DB call
        jdbcTemplate.update("INSERT INTO orders(user_id, amount) VALUES (?, ?)", userId, amount);

        // Blocking HTTP call to payments-service
        var paymentResponse = paymentsClient.post()
                .uri("/payments")
                .body(Map.of("userId", userId, "amount", amount))
                .retrieve()
                .body(Map.class);

        return Map.of(
                "status", "OK",
                "payment", paymentResponse
        );
    }
}
```

#### 7.1.5 Controller

```java
package com.example.orders;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping("/orders")
    public Map<String, Object> createOrder(@RequestBody Map<String, Object> request) {
        String userId = (String) request.get("userId");
        int amount = (int) request.get("amount");
        return orderService.createOrder(userId, amount);
    }
}
```

**Key idea**: This is **classic blocking** code (JDBC + blocking HTTP client) but runs on **virtual threads**, allowing high concurrency without a huge platform thread pool.

### 7.2 payments-service: simple blocking service

#### 7.2.1 Configuration

`application.yml`:

```yaml
server:
  port: 8081

spring:
  threads:
    virtual:
      enabled: true
```

#### 7.2.2 Application & controller

```java
package com.example.payments;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@SpringBootApplication
public class PaymentsApplication {
    public static void main(String[] args) {
        SpringApplication.run(PaymentsApplication.class, args);
    }
}

@RestController
class PaymentController {

    @PostMapping("/payments")
    public Map<String, Object> payment(@RequestBody Map<String, Object> request) throws InterruptedException {
        // Simulate blocking I/O
        Thread.sleep(200); // blocked virtual thread; carrier is free

        return Map.of(
                "status", "PAID",
                "userId", request.get("userId"),
                "amount", request.get("amount")
        );
    }
}
```

With virtual threads enabled:
- Each request to `/payments` can block (e.g., `Thread.sleep`, DB, external APIs).
- The **carrier pool** is reused efficiently; many concurrent requests are supported.

---

## 8. Putting It Together: Design Recommendations

### 8.1 General guidance

- **Keep application logic blocking and simple** where possible; use **virtual threads** for scalability.
- For **CPU-bound** work:
  - Use platform-thread pools sized to CPU count.
  - Consider `ForkJoinPool` or parallel streams.
- Use **structured concurrency** for multi-call operations:
  - E.g., fetch user, profile, and recommendations in parallel, cancel all if any fails.

### 8.2 Migration path to Java 21 style

1. Identify services that are I/O-bound and currently use large thread pools or async primitives.
2. Switch request handling to **virtual threads**:
   - Spring Boot: `spring.threads.virtual.enabled=true`.
   - Plain Java: `Executors.newVirtualThreadPerTaskExecutor()`.
3. Replace ad-hoc task handling with **`StructuredTaskScope`** where appropriate.
4. Gradually replace `ThreadLocal`-heavy designs with **ScopedValue** for contextual data.

### 8.3 Interview-level talking points

- Explain **difference between platform and virtual threads** and why virtual threads scale blocking I/O.
- Describe **structured concurrency** and how it simplifies error handling and cancellation.
- Compare **CompletableFuture**-based designs vs **StructuredTaskScope**.
- Discuss when to keep/reactively handle requests vs using virtual threads (backpressure, ecosystem).

---

## 9. Quick Reference Table

| Topic | Best-practice API (Java 21) | Notes |
|-------|-----------------------------|-------|
| I/O-bound concurrency | `Executors.newVirtualThreadPerTaskExecutor()` | Use thread-per-task style with virtual threads |
| Multi-call operation | `StructuredTaskScope.ShutdownOnFailure/Success` | Scoped, cancellable concurrency |
| Async pipelines | `CompletableFuture` | For composition and non-blocking continuation style |
| Thread context | `ScopedValue` (over ThreadLocal) | Lexically scoped, better with virtual threads |
| CPU-bound tasks | Platform thread pools, `ForkJoinPool`, parallel streams | Keep pools small (≈ cores) |
| Web apps | Spring Boot 3 + virtual threads | `spring.threads.virtual.enabled=true` |
| Shared mutable state | `java.util.concurrent` collections and locks | Avoid manual low-level concurrency when possible |

This enterprise guide, together with `Threading-Basic-Guide.md`, gives you a complete, modern reference for Java threading through Java 21, from fundamentals to large-scale, production-ready designs. 

