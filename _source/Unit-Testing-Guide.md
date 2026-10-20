## Java Unit Testing Guide — JUnit 5 (Java 8–21)

---

## 1. Purpose & Audience

- **Purpose**: Provide a practical, end‑to‑end guide for **unit testing** in Java using **JUnit 5** (Jupiter), from beginner to advanced:
  - Setup with Maven/Gradle and Java 8–21.
  - Testing methods with and without parameters/return values.
  - Testing exceptions, static methods, private methods.
  - Parameterized tests, nested tests, lifecycle, tagging.
  - Using **Mockito** for mocking and verifying interactions.
- **Audience**:
  - Beginners needing concrete examples.
  - Intermediate/senior engineers looking for a reference of “latest” JUnit 5 patterns.

Integration & Spring Boot tests are covered separately in `Integration-Testing-Guide.md`.

---

## 2. Setup (Java 21 + JUnit 5)

### 2.1 Maven

```xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.2</version>
        <scope>test</scope>
    </dependency>

    <!-- Mockito JUnit 5 integration -->
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <version>5.11.0</version>
        <scope>test</scope>
    </dependency>

    <!-- Optional: Mockito inline for static mocking -->
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-inline</artifactId>
        <version>5.2.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.2.5</version>
            <configuration>
                <useModulePath>false</useModulePath>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 2.2 Gradle (Groovy DSL)

```groovy
dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
    testImplementation 'org.mockito:mockito-junit-jupiter:5.11.0'
    testImplementation 'org.mockito:mockito-inline:5.2.0' // optional, for static mocking
}

test {
    useJUnitPlatform()
}
```

### 2.3 Modules (optional)

```java
module com.example.app {
    requires org.junit.jupiter.api;
    // tests are usually in a separate test module, or you open packages to test module
}
```

---

## 3. Core JUnit 5 Annotations & Lifecycle

| Annotation | Purpose |
|-----------|---------|
| `@Test` | Marks a test method |
| `@BeforeEach` | Run before each test (setup) |
| `@AfterEach` | Run after each test (cleanup) |
| `@BeforeAll` | Run once before all tests in class (static by default) |
| `@AfterAll` | Run once after all tests in class |
| `@DisplayName` | Custom name for test/reporting |
| `@Nested` | Group related tests inside inner classes |
| `@Disabled` | Temporarily disable a test/class |
| `@Tag` | Categorize tests (e.g. `@Tag("slow")`) |
| `@Timeout` | Fail test if it runs longer than given duration |

Example:

```java
import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("UserService unit tests")
class UserServiceTest {

    private UserService userService;

    @BeforeAll
    static void initAll() {
        System.out.println("Run once before all tests");
    }

    @BeforeEach
    void init() {
        userService = new UserService();
    }

    @Test
    @DisplayName("createUser returns user with ID")
    void createUser_returnsUserWithId() {
        User user = userService.createUser("alice");
        assertNotNull(user.getId());
        assertEquals("alice", user.getName());
    }

    @AfterEach
    void tearDown() {
        // cleanup
    }

    @AfterAll
    static void tearDownAll() {
        System.out.println("Run once after all tests");
    }
}
```

---

## 4. Assertions & Assumptions

### 4.1 Core assertions

Static imports recommended:

```java
import static org.junit.jupiter.api.Assertions.*;
```

Common assertions:

- `assertEquals(expected, actual)`
- `assertNotEquals(unexpected, actual)`
- `assertTrue(condition)`
- `assertFalse(condition)`
- `assertNull(actual)`
- `assertNotNull(actual)`
- `assertSame(expectedRef, actualRef)`
- `assertNotSame(unexpectedRef, actualRef)`
- `assertThrows(ExceptionClass, executable)`
- `assertDoesNotThrow(executable)`
- `assertAll(...)` to group multiple assertions.

Example with `assertAll`:

```java
@Test
void createUser_setsAllFields() {
    User u = new User("id-1", "alice", "alice@example.com");
    assertAll(
        () -> assertEquals("id-1", u.getId()),
        () -> assertEquals("alice", u.getName()),
        () -> assertEquals("alice@example.com", u.getEmail())
    );
}
```

### 4.2 Assumptions

Skip tests when environment assumptions are not met (e.g. only run on CI, or only if DB is available).

```java
import static org.junit.jupiter.api.Assumptions.*;

@Test
void runsOnlyOnCi() {
    assumeTrue("true".equals(System.getenv("CI")));
    // test body
}
```

---

## 5. Testing Methods with Parameters and Return Values

Example from your reference:

```java
public class Calculator {

    public int add(int a, int b) {
        return a + b;
    }

    public double divide(double a, double b) {
        if (b == 0) throw new IllegalArgumentException("Cannot divide by zero");
        return a / b;
    }

    public String greet(String name) {
        if (name == null || name.isBlank()) {
            return "Hello, Guest";
        }
        return "Hello, " + name.trim();
    }
}
```

```java
class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    void add_positiveNumbers_returnsSum() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    void divide_validInputs_returnsQuotient() {
        assertEquals(5.0, calculator.divide(10.0, 2.0));
    }

    @Test
    void divide_byZero_throwsException() {
        Exception ex = assertThrows(IllegalArgumentException.class,
            () -> calculator.divide(10.0, 0.0));
        assertEquals("Cannot divide by zero", ex.getMessage());
    }
}
```

---

## 6. Parameterized Tests (Beginner → Advanced)

Parameterized tests let you run the same test logic over multiple inputs.

### 6.1 Basic @ParameterizedTest with @ValueSource

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class StringUtilsParameterizedTest {

    @ParameterizedTest
    @ValueSource(strings = { "a", "b", "hello" })
    void isBlank_returnsFalseForNonBlank(String input) {
        assertFalse(StringUtils.isBlank(input));
    }
}
```

### 6.2 @CsvSource

```java
import org.junit.jupiter.params.provider.CsvSource;

@ParameterizedTest
@CsvSource({
    "2, 3, 5",
    "-2, -3, -5",
    "0, 5, 5"
})
void add_variousInputs(int a, int b, int expected) {
    Calculator c = new Calculator();
    assertEquals(expected, c.add(a, b));
}
```

### 6.3 @MethodSource

```java
import org.junit.jupiter.params.provider.MethodSource;

class DiscountServiceTest {

    static Stream<Arguments> discountCases() {
        return Stream.of(
            Arguments.of(100.0, 0.1, 90.0),
            Arguments.of(200.0, 0.2, 160.0)
        );
    }

    @ParameterizedTest
    @MethodSource("discountCases")
    void calculateDiscount(double price, double rate, double expected) {
        DiscountService svc = new DiscountService();
        assertEquals(expected, svc.applyDiscount(price, rate));
    }
}
```

### 6.4 Other sources

- `@EnumSource(MyEnum.class)`
- `@NullSource`
- `@EmptySource`
- `@NullAndEmptySource`

---

## 7. Testing Void Methods & Side Effects

### 7.1 Internal state change

```java
public class Counter {
    private int value = 0;
    public void increment() { value++; }
    public void reset() { value = 0; }
    public int getValue() { return value; }
}
```

```java
class CounterTest {
    @Test
    void increment_increasesValue() {
        Counter c = new Counter();
        assertEquals(0, c.getValue());
        c.increment();
        assertEquals(1, c.getValue());
    }
}
```

### 7.2 Void method that throws

```java
public class Validator {
    public void validateNotEmpty(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Value cannot be empty");
        }
    }
}
```

```java
class ValidatorTest {
    private final Validator validator = new Validator();

    @Test
    void validateNotEmpty_null_throws() {
        var ex = assertThrows(IllegalArgumentException.class,
            () -> validator.validateNotEmpty(null));
        assertEquals("Value cannot be empty", ex.getMessage());
    }
}
```

### 7.3 Void method with dependencies – Mockito

```java
public interface EmailSender {
    void send(String to, String subject, String body);
}

public class NotificationService {
    private final EmailSender emailSender;
    public NotificationService(EmailSender emailSender) {
        this.emailSender = emailSender;
    }
    public void sendWelcomeEmail() {
        emailSender.send("user@example.com", "Welcome", "Welcome to the app!");
    }
}
```

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {

    @Mock
    EmailSender emailSender;

    @InjectMocks
    NotificationService notificationService;

    @Test
    void sendWelcomeEmail_invokesEmailSender() {
        notificationService.sendWelcomeEmail();

        verify(emailSender, times(1)).send(
            eq("user@example.com"),
            eq("Welcome"),
            eq("Welcome to the app!")
        );
    }
}
```

---

## 8. Testing Static Methods

### 8.1 Prefer testing real static methods (pure functions)

```java
public final class StringUtils {
    private StringUtils() {}
    public static boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }
}
```

```java
class StringUtilsTest {
    @Test
    void isBlank_nullOrEmpty_true() {
        assertTrue(StringUtils.isBlank(null));
        assertTrue(StringUtils.isBlank(""));
    }
}
```

### 8.2 Mock static methods (Mockito inline)

Use when static method calls external systems (UUID, time, network).

```java
public final class IdGenerator {
    private IdGenerator() {}
    public static String generate() {
        return UUID.randomUUID().toString();
    }
}

public class OrderService {
    public String createOrder(String product) {
        return IdGenerator.generate() + ":" + product;
    }
}
```

```java
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class OrderServiceTest {

    @Test
    void createOrder_usesGeneratedId() {
        try (MockedStatic<IdGenerator> staticMock = mockStatic(IdGenerator.class)) {
            staticMock.when(IdGenerator::generate).thenReturn("fixed-id");

            OrderService service = new OrderService();
            String result = service.createOrder("Widget");

            assertEquals("fixed-id:Widget", result);
            staticMock.verify(IdGenerator::generate, times(1));
        }
    }
}
```

---

## 9. Testing Private Logic

### 9.1 Preferred: test via public API

Write tests that call public methods which use private helpers; assert overall behaviour. If you can’t, consider refactoring.

### 9.2 Reflection (last resort)

```java
Method m = MyClass.class.getDeclaredMethod("privateMethod", String.class);
m.setAccessible(true);
Object result = m.invoke(instance, "input");
```

Use sparingly; fragile under refactoring.

### 9.3 Package‑private helpers

Put logic in package‑private methods or classes and keep tests in the same package. This is usually cleaner than reflection.

---

## 10. Test Structure, Naming, and Organization

- **Pattern**: Arrange–Act–Assert (AAA):
  - Arrange (setup data & mocks)
  - Act (call method under test)
  - Assert (check result & side‑effects)
- **Naming**:
  - `methodName_scenario_expectedResult`, e.g. `divide_byZero_throwsException`.
- **Packages**:
  - Mirror main source structure: `src/main/java/com/example/...` and `src/test/java/com/example/...`.
- **Spring Boot apps**:
  - Unit tests for pure logic (no Spring context).
  - Integration tests for controllers, repositories, external resources (see `Integration-Testing-Guide.md`).

---

## 11. Running Tests

```bash
# Maven
mvn test

# Gradle
gradlew test
```

JUnit 5 runs fine on **Java 8+**; with **Java 21** you can use records, pattern matching, `var`, and other language features in your tests as desired. 

