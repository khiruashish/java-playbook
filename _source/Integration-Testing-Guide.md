## Java Integration Testing Guide — JUnit 5, Spring Boot 3, Testcontainers (Java 8–21)

---

## 1. Purpose & Audience

- **Purpose**: Provide a practical, production-focused guide to **integration testing** in Java:
  - How integration tests differ from unit tests.
  - JUnit 5 + Maven/Gradle setup for integration tests.
  - REST API, database, and messaging integration tests with **Spring Boot 3**.
  - Using **Testcontainers** for real databases and services.
  - Java 21 considerations (virtual threads, modern language features).
- **Audience**:
  - Developers writing backend/microservice code with Spring Boot.
  - Engineers needing robust end‑to‑end and slice tests in CI.

Unit‑level testing patterns are covered in `Unit-Testing-Guide.md`.

---

## 2. What Is an Integration Test?

- **Unit test**:
  - Tests a single class or a very small set of classes in isolation.
  - Uses mocks/fakes for external dependencies.
  - Fast, no real network/DB.

- **Integration test**:
  - Tests how components work **together**:
    - REST controller + service + repository + DB.
    - Microservice A talking to microservice B.
  - Uses **real infrastructure** or realistic test equivalents:
    - In‑memory DB, or containerized real DB (PostgreSQL/MySQL) via Testcontainers.
    - Embedded servers, real HTTP calls, messaging brokers.

Typical goals:
- Validate wiring & configuration (`@Configuration`, `@Bean`, Spring Boot auto‑config).
- Validate that the service behaves correctly against **real dependencies** (SQL schema, HTTP endpoints, MQ).

---

## 3. Naming, Build Setup & Test Phases

### 3.1 Naming conventions (Maven)

By default:

- **Unit tests**: classes ending with `*Test` (run by Surefire).
- **Integration tests**:
  - Often named `*IT`, `*ITCase`, or placed in `src/integration-test/java`.
  - Run by the **Failsafe** plugin or a separate test task.

Minimal Maven setup for `*IT` tests:

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-surefire-plugin</artifactId>
      <version>3.2.5</version>
      <configuration>
        <includes>
          <include>**/*Test.java</include>
        </includes>
      </configuration>
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-failsafe-plugin</artifactId>
      <version>3.2.5</version>
      <executions>
        <execution>
          <goals>
            <goal>integration-test</goal>
            <goal>verify</goal>
          </goals>
          <configuration>
            <includes>
              <include>**/*IT.java</include>
            </includes>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

Run:

```bash
mvn test                # unit tests
mvn verify              # unit + integration tests (failsafe)
```

### 3.2 Gradle

One approach is a separate `integrationTest` source set and task.

Simple version (reuse `test` with @Tag, see §6.4) or more advanced with separate task—omitted here for brevity.

---

## 4. Spring Boot 3 Integration Tests (Overview)

Spring Boot provides multiple styles:

- `@SpringBootTest`:
  - Starts the full application context.
  - Optionally starts the embedded web server.
  - Good for **end‑to‑end** tests within a single service.

- `@WebMvcTest`:
  - Loads only MVC components (controllers, controller advice).
  - Uses `MockMvc` to test controllers with a fake HTTP layer.

- `@DataJpaTest`:
  - Loads JPA components and an in‑memory DB or test DB.
  - Focuses on repositories and persistence layer.

- `@JdbcTest`, `@RestClientTest`, etc.:
  - Slice tests for specific layers.

We’ll use:
- `@SpringBootTest(webEnvironment = RANDOM_PORT)` for full HTTP + DB integration.
- `@DataJpaTest` for repository integration.
- `Testcontainers` for real DBs.

---

## 5. REST API Integration Test with Spring Boot 3

### 5.1 Example REST service

`User` entity and simple controller:

```java
// src/main/java/com/example/users/User.java
package com.example.users;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;

@Entity
public class User {
    @Id
    @GeneratedValue
    private Long id;
    private String name;

    protected User() {} // JPA

    public User(String name) {
        this.name = name;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
}
```

```java
// src/main/java/com/example/users/UserRepository.java
package com.example.users;

import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
}
```

```java
// src/main/java/com/example/users/UserController.java
package com.example.users;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/users")
public class UserController {

    private final UserRepository userRepository;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@RequestBody User user) {
        return userRepository.save(new User(user.getName()));
    }

    @GetMapping
    public List<User> all() {
        return userRepository.findAll();
    }
}
```

### 5.2 Full-stack integration test with @SpringBootTest

We’ll use:
- Embedded server (`RANDOM_PORT`).
- `TestRestTemplate` for HTTP calls.
- H2 in‑memory DB (or Postgres via Testcontainers in §7).

```java
// src/test/java/com/example/users/UserControllerIT.java
package com.example.users;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.*;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserControllerIT {

    @LocalServerPort
    int port;

    @Autowired
    TestRestTemplate restTemplate;

    @Test
    void createAndListUsers() {
        String base = "http://localhost:" + port + "/users";

        User newUser = new User("alice");
        ResponseEntity<User> createResponse =
                restTemplate.postForEntity(base, newUser, User.class);

        assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        User created = createResponse.getBody();
        assertThat(created).isNotNull();
        assertThat(created.getId()).isNotNull();
        assertThat(created.getName()).isEqualTo("alice");

        ResponseEntity<User[]> listResponse =
                restTemplate.getForEntity(base, User[].class);
        assertThat(listResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(listResponse.getBody()).extracting(User::getName).contains("alice");
    }
}
```

---

## 6. Slice Tests: @WebMvcTest and @DataJpaTest

### 6.1 @WebMvcTest — controller layer only

`@WebMvcTest` loads only MVC components. Use `MockMvc` for HTTP simulation.

```java
// src/test/java/com/example/users/UserControllerWebMvcTest.java
package com.example.users;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerWebMvcTest {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    UserRepository userRepository;

    @Test
    void getUsers_returnsList() throws Exception {
        when(userRepository.findAll()).thenReturn(List.of(new User("alice")));

        mockMvc.perform(get("/users"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("alice"));
    }
}
```

### 6.2 @DataJpaTest — repository integration

`@DataJpaTest` configures JPA repositories, entity manager, and a test database.

```java
// src/test/java/com/example/users/UserRepositoryIT.java
package com.example.users;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class UserRepositoryIT {

    @Autowired
    UserRepository userRepository;

    @Test
    void saveAndFindById() {
        User user = new User("bob");
        User saved = userRepository.save(user);

        assertThat(saved.getId()).isNotNull();
        assertThat(userRepository.findById(saved.getId()))
            .isPresent()
            .get()
            .extracting(User::getName)
            .isEqualTo("bob");
    }
}
```

---

## 7. Database Integration with Testcontainers

### 7.1 Why Testcontainers?

Testcontainers runs real services (e.g. PostgreSQL, Kafka) in Docker containers for tests:
- Avoids differences between in‑memory H2 and production DB.
- Reproducible, self‑contained tests for CI.

### 7.2 Maven dependencies

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>1.19.7</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <version>1.19.7</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

### 7.3 Spring Boot + Postgres container

```java
// src/test/java/com/example/users/PostgresIntegrationIT.java
package com.example.users;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ExtendWith(SpringExtension.class)
@Testcontainers
class PostgresIntegrationIT {

    @Container
    static final PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void overrideProps(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    UserRepository userRepository;

    @Test
    void persistUser_inRealPostgres() {
        User u = new User("postgres-user");
        User saved = userRepository.save(u);
        assertThat(saved.getId()).isNotNull();
    }
}
```

---

## 8. Multi‑Service Integration (Microservices)

### 8.1 Strategy

For two services (e.g. `orders-service` and `payments-service`):
- **Service‑level integration**:
  - Use `@SpringBootTest` with `RANDOM_PORT`.
  - Call the local service over HTTP using `TestRestTemplate` or `WebTestClient`.
  - For cross-service calls:
    - Prefer **contract tests** and/or
    - Use Testcontainers to spin up the dependent service image (or mock it with WireMock).

Due to scope, we’ll show a simplified single‑service test that calls a **mocked downstream HTTP server** (WireMock); same pattern applies to real services.

### 8.2 HTTP client integration with WireMock (conceptual)

```xml
<dependency>
    <groupId>com.github.tomakehurst</groupId>
    <artifactId>wiremock-jre8</artifactId>
    <version>2.35.1</version>
    <scope>test</scope>
</dependency>
```

```java
// Example: service that calls external /payments API
public class PaymentClient {
    private final RestClient restClient;

    public PaymentClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public Map<String, Object> pay(String userId, int amount) {
        return restClient.post()
                .uri("/payments")
                .body(Map.of("userId", userId, "amount", amount))
                .retrieve()
                .body(Map.class);
    }
}
```

```java
// Integration test using WireMock to simulate external service
class PaymentClientIT {

    private static WireMockServer server;

    @BeforeAll
    static void startServer() {
        server = new WireMockServer(0);
        server.start();
    }

    @AfterAll
    static void stopServer() {
        server.stop();
    }

    @Test
    void pay_callsRemoteService() {
        server.stubFor(post(urlEqualTo("/payments"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"PAID\"}")));

        RestClient client = RestClient.builder()
                .baseUrl("http://localhost:" + server.port())
                .build();
        PaymentClient paymentClient = new PaymentClient(client);

        Map<String, Object> response = paymentClient.pay("u1", 100);
        assertThat(response.get("status")).isEqualTo("PAID");
    }
}
```

---

## 9. Tags, Profiles, and Running Integration Tests

### 9.1 JUnit 5 tags

Tag integration tests with `@Tag("integration")` and configure build to include/exclude.

```java
@SpringBootTest
@Tag("integration")
class SomeIntegrationTest { ... }
```

Maven Surefire example:

```xml
<configuration>
  <groups>!integration</groups> <!-- run everything except @Tag("integration") -->
</configuration>
```

Failsafe (or another profile) can include them explicitly.

### 9.2 Spring profiles

Use `@ActiveProfiles("test")` to use test‑specific config:

```java
@SpringBootTest
@ActiveProfiles("test")
class MyServiceIT { ... }
```

Configuration in `application-test.yml`:

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
```

---

## 10. Java 21 Considerations (Virtual Threads & Modern Language Features)

- **Virtual threads**:
  - In integration tests, you typically do not need to change anything: Spring Boot tests will use whatever thread model your app is configured with.
  - For load or concurrency tests, you can explicitly use virtual threads in test code:

    ```java
    @Test
    void manyConcurrentRequests_virtualThreads() throws Exception {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Callable<String>> tasks = IntStream.range(0, 1000)
                    .mapToObj(i -> (Callable<String>) () -> callEndpoint(i))
                    .toList();
            executor.invokeAll(tasks);
        }
    }
    ```

- **Language features**:
  - Use `record` for simple DTOs in tests.
  - Use pattern matching for `switch` in assertion logic if it clarifies code.

---

## 11. Quick Reference Table

| Scenario | Recommended approach |
|----------|----------------------|
| Test REST controller + DB | `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`/WebTestClient |
| Test only controller layer | `@WebMvcTest` + `MockMvc` (mock service layer) |
| Test JPA repository with real DB | `@DataJpaTest` + Testcontainers/Postgres |
| Test external HTTP client | WireMock or Testcontainers with real service |
| Isolate slow tests | Use `@Tag("integration")` and a separate Maven/Gradle phase |
| CI friendly DB tests | Testcontainers + reusable containers or per‑test containers |

Together with `Unit-Testing-Guide.md`, this guide gives you a structured approach for testing from **small, isolated units** up to **full-stack, cross-service integration** in modern Java and Spring Boot applications. 

