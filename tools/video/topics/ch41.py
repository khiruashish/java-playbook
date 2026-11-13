"""Chapter 41 — JUnit 5. Source: docs/06-testing/41-junit5.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 41 · JUnit 5"
SECTION = "Testing"

SLIDES = [
    dict(kind="title",
         title="JUnit 5",
         kicker="Testing · Chapter 41",
         body='<p class="sub">Platform, Jupiter and Vintage; tests that fail usefully; parameterized boundaries; nested specifications; and the traps in timeouts and parallelism.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter forty-one, the first of the testing section: JUnit 5.",
             "Pure logic with no dependencies is the easiest code there is to test. And yet it's often checked with a main method and a human comparing printed numbers, which doesn't run in CI and doesn't tell you which of eleven pricing rules just broke.",
         ]),

    dict(title="Why not just a main method?",
         kicker="The problem",
         body=code('''
public Money total(Cart cart, List<PricingRule> rules) {
    if (cart.lines().isEmpty()) throw new IllegalArgumentException("Cart is empty");
    Money subtotal = cart.lines().stream().map(CartLine::lineTotal).reduce(Money.ZERO, Money::plus);
    return rules.stream().reduce(subtotal, (running, rule) -> rule.apply(running), Money::plus);
}''', title="CartTotalCalculator.java", size=23)
              + frag('<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
                     + card("Declare", "A standard way to say **what** should be checked", "indigo")
                     + card("Isolate", "One failure doesn't **hide** the next", "cyan")
                     + card("Report", "A **machine-readable** result a build can act on", "amber")
                     + "</div>", 1),
         narration=[
             "Here's a cart total calculator: line totals, then a chain of pricing rules. Pure logic, exactly the code that should be trivially testable.",
             "A test framework gives you three things a main method can't. A standard way to declare what should be checked. Isolation, so one failure doesn't hide the next. And a machine-readable result that a build can fail on.",
         ]),

    dict(title="Platform, Jupiter, Vintage",
         kicker="Mental model",
         body=table(["Component", "Role"], [
                    ["**Platform**", "Discovers and launches tests — what Maven, Gradle and IDEs talk to"],
                    ["**Jupiter**", "The programming model you write: `@Test`, `@ParameterizedTest`, extensions"],
                    ["**Vintage**", "Runs existing JUnit 3 and 4 tests on the Platform"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout"><code>@RunWith</code> allowed <b>one</b> runner. <code>@ExtendWith</code> composes — Mockito, Spring and Testcontainers in the same class.</p>', 3),
         narration=[
             "JUnit 5 is three components released together. The Platform discovers and launches tests. It's the API build tools and IDEs talk to.",
             "Jupiter is the programming model you actually write against.",
             "And Vintage runs your existing JUnit 4 tests on the same platform. So you can migrate gradually, with no big-bang cutover.",
             "The other big change is extensions. JUnit 4's RunWith gave you exactly one runner, so Mockito's and Spring's couldn't coexist. ExtendWith composes, which is why Mockito, Spring and Testcontainers all work in the same test class.",
         ]),

    dict(title="A test that fails usefully",
         kicker="Worked example",
         body=code('''
@Test
@DisplayName("rejects an empty cart")
void total_emptyCart_throws() {
    Cart empty = cartWith();                                         // Arrange

    var ex = assertThrows(IllegalArgumentException.class,           // Act
                          () -> calculator.total(empty, List.of()));

    assertEquals("Cart is empty", ex.getMessage());                 // Assert
}''', title="CartTotalCalculatorTest.java", size=24)
              + frag(bullets(["`method_scenario_expectedResult` — the CI line **is** the diagnosis",
                              "`assertThrows` **returns** the exception — check the message, or a typo's NPE passes",
                              "A new instance per test — fields can't leak between tests"], cls="bullets sm"), 1),
         narration=[
             "Here's a test that fails usefully. Arrange an empty cart. Act, by calling total inside assertThrows. And assert on the exception's message.",
             "Three things are doing real work. The name, method, scenario, expected result, means that when CI reports total empty cart throws, you know what broke before opening anything. "
             "assertThrows returns the exception, so you can check you triggered the path you meant to. Otherwise a NullPointerException from a typo would pass. "
             "And JUnit creates a new instance of the class for every test, so a field mutated in one test can't leak into the next.",
         ]),

    dict(title="assertAll — every failure at once",
         kicker="Worked example",
         body=code('''
assertAll("confirmed order",
    () -> assertNotNull(order.id()),
    () -> assertEquals(OrderStatus.CONFIRMED, order.status()),
    () -> assertEquals(customer.id(), order.customerId()),
    () -> assertEquals(3, order.lines().size()));''', title="OrderTest.java", size=25)
              + frag('<p class="callout">Without it, the first failure hides the other three. Knowing <b>status and lines</b> are both wrong is usually a different diagnosis.</p>', 1),
         narration=[
             "When one behaviour has several observable parts, use assertAll. Every assertion runs, and every failure is reported.",
             "Without it, the first failing assertion stops the method and hides the rest. Knowing that both the status and the lines are wrong is usually a different diagnosis from either one alone.",
         ]),

    dict(title="Parameterized: boundaries are the point",
         kicker="Worked example",
         body='<div class="grid2 start">'
              + code('''
@ParameterizedTest(name = "{0} units → {1}%")
@CsvSource({
    "1,   0",  "9,   0",
    "10,  5",  "49,  5",
    "50,  10", "500, 10" })
void discountPercent(int qty, int pct) {
    assertEquals(pct,
        BulkDiscountRule.percentFor(qty));
}''', title="BulkDiscountRuleTest.java", size=23)
              + frag(code('''
✓ 1 units → 0%
✓ 9 units → 0%
✓ 10 units → 5%
✗ 49 units → 5%   ← boundary bug''', lang="text", title="Report", size=24), 1)
              + "</div>"
              + frag('<p class="callout">Objects, not literals? <code>@MethodSource</code> returning <code>Stream&lt;Arguments&gt;</code>.</p>', 2),
         narration=[
             "Parameterized tests turn one test into many. Each CSV row is an independent test with its own result, named from the parameters.",
             "The boundary values, nine and ten, forty-nine and fifty, are the entire point. Off-by-one bugs live there. A loop inside one test would report a single failure and leave you hunting for which iteration.",
             "When the arguments are objects rather than literals, use MethodSource, with a static method returning a stream of arguments.",
         ]),

    dict(title="@Nested reads as a specification",
         kicker="Worked example",
         body='<div class="grid2 start">'
              + code('''
class StockReservationTest {
  @BeforeEach void setUp() { item = stock(10); }

  @Nested class WhenStockInsufficient {
    @BeforeEach void drain() { item.reserve(10); }

    @Test void refuses() {
      assertFalse(item.reserve(1).succeeded());
    }
  }
}''', title="StockReservationTest.java", size=22)
              + frag(code('''
StockReservation
  when stock is available
    ✓ reserves the requested quantity
  when stock is insufficient
    ✓ refuses the reservation
    ✓ leaves available quantity unchanged''', lang="text", size=22), 1)
              + "</div>",
         narration=[
             "Nested classes group tests by precondition. The outer setup creates ten units of stock. The inner class, when stock is insufficient, drains it first. Lifecycle methods run outside in: the outer before-each, then the inner one.",
             "And the report reads like a specification. When stock is available, it reserves the quantity. When stock is insufficient, it refuses, and leaves the quantity unchanged.",
         ]),

    dict(title="The traps",
         kicker="Internals",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("@Disabled vs assume", "`@Disabled`: broken. `assumeTrue`: fine, but preconditions **absent here** — reported as skipped.", "indigo", 0)
              + card("Preemptive timeouts", "`assertTimeoutPreemptively` runs on **another thread**: no transaction, security context or MDC.", "fuchsia", 1)
              + card("Parallel execution", "Classes concurrent, methods sequential. It exposes **every** static field, temp file and fixed port.", "amber", 2)
              + "</div>",
         narration=[
             "A few traps. Disabled means the test is broken or irrelevant. An assumption means the test is fine, but its preconditions aren't met here, like a missing sandbox URL. It's reported as skipped, not passed, so it doesn't inflate your green count.",
             "assertTimeoutPreemptively runs the code on a different thread. So thread-local state, like a Spring transaction, security context, or logging MDC, isn't visible. Prefer plain assertTimeout unless you must abort a hang.",
             "And parallel execution. The conservative setting runs classes concurrently and methods within a class sequentially. Turning it on surfaces every hidden dependency in the suite. A good audit, but not the day before a release.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["`method_scenario_expectedResult` names",
                         "Arrange · Act · Assert",
                         "Parameterize the boundaries",
                         "`@Nested` by precondition",
                         "Assert on exception messages",
                         "Use the BOM; tag slow tests"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Depend on test order",
                         "`assertTrue(a.equals(b))`",
                         "`@Disabled` without a reason",
                         "Loops or conditionals in a test",
                         "The system clock — inject a `Clock`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Name tests method, scenario, expected result. Follow arrange, act, assert. Parameterize the boundaries. Group with nested classes by precondition. Assert on exception messages. Use the BOM, and tag slow tests.",
             "Never depend on test order. Never write assertTrue of a dot equals b, which prints expected true, was false. Use assertEquals, which prints both values. Never disable a test without a reason. Never put loops or conditionals in a test. And never depend on the system clock: inject a Clock.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 41 · JUnit 5",
         body=bullets(["Platform launches; Jupiter is what you write; Vintage migrates",
                       "`@ExtendWith` composes — one runner is history",
                       "`assertThrows` + message; `assertAll` for parts",
                       "Parameterize boundaries; `@Nested` for context",
                       "Next: **Ch 42 · Mockito &amp; Test Doubles**"], cls="bullets recap"),
         narration=[
             "To recap. The Platform launches tests, Jupiter is what you write, and Vintage lets you migrate gradually. Extensions compose. Use assertThrows with a message check, and assertAll for several parts of one behaviour. "
             "Parameterize the boundaries, and use nested classes for context.",
             "Next is chapter forty-two: Mockito and test doubles. Thanks for watching.",
         ]),
]
