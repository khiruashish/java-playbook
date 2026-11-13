"""Chapter 42 — Mockito & Test Doubles. Source: docs/06-testing/42-mockito.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 42 · Mockito & Test Doubles"
SECTION = "Testing"

SLIDES = [
    dict(kind="title",
         title="Mockito &amp; Test Doubles",
         kicker="Testing · Chapter 42",
         body='<p class="sub">Stubs, mocks, spies and fakes; when to verify behaviour; strict stubs; and the mocking habits that produce coverage without confidence.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter forty-two: Mockito and test doubles.",
             "Most real classes have collaborators: a payment gateway, a warehouse API, a database. Test doubles let you test a class's own logic without them. Used well, they're precise. Used everywhere, they produce a green suite that catches nothing.",
         ]),

    dict(title="Four collaborators, one rule",
         kicker="The problem",
         body=code('''
public Order confirm(Cart cart, Customer customer) {
    if (!inventory.reserveAll(cart.lines())) throw new OutOfStockException(cart.id());
    PaymentResult result = payments.charge(customer.id(), cart.total());
    if (!result.successful()) {
        inventory.releaseAll(cart.lines());                 // ← the rule worth testing
        throw new PaymentFailedException(result.reason());
    }
    Order order = repository.save(Order.from(cart, customer, result.reference()));
    emailSender.send(customer.email(), "Order confirmed", order.summary());
    return order;
}''', title="OrderService.java", size=23)
              + frag('<p class="callout">For real: a warehouse API, a payment gateway, a database and SMTP — slow, flaky, and the charge is <b>actually expensive</b>.</p>', 1),
         narration=[
             "OrderService confirms an order. It reserves stock, charges the customer, saves the order, and emails a confirmation. And there's one rule that really matters: if payment fails, the reserved stock must be released.",
             "Testing it for real means a warehouse API, a payment gateway, a database and a mail server. Slow, flaky, and for the payment, actually expensive. A test double stands in for each collaborator, so you can test this class's logic.",
         ]),

    dict(title="Five kinds of double",
         kicker="Mental model",
         body=table(["Kind", "Behaviour", "Example"], [
                    ["Dummy", "Fills a parameter; never called", "a bare `mock()`"],
                    ["**Stub**", "Returns canned answers", "`when(…).thenReturn(true)`"],
                    ["Spy", "Real object, some methods overridden", "`spy(new PricingRuleEngine())`"],
                    ["**Mock**", "A stub you also **verify**", "`verify(emailSender).send(…)`"],
                    ["**Fake**", "A simplified working implementation", "`InMemoryOrderRepository`"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">Prefer <b>state</b> verification — assert the result. <code>verify</code> pins the test to how the code works; '
                     'use it for effects invisible from the outside.</p>', 1),
         narration=[
             "There are five kinds of double. A dummy just fills a parameter. A stub returns canned answers. A spy is a real object with some methods overridden. A mock is a stub you also verify against. And a fake is a simplified, working implementation, like an in-memory repository. "
             "Mockito's mock covers the first four roles. Fakes, you write yourself.",
             "Prefer state verification: assert on the result. Verifying interactions pins the test to how the code works, so harmless refactoring breaks it. Verify is for effects that are invisible from the outside, like an email sent or stock released.",
         ]),

    dict(title="The happy path",
         kicker="Worked example",
         body=code('''
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock InventoryClient inventory;   @Mock PaymentGateway payments;
    @Mock OrderRepository repository;  @Mock EmailSender emailSender;
    @InjectMocks OrderService orderService;

    @Test
    void confirm_stockAvailableAndPaymentSucceeds_savesOrder() {
        when(inventory.reserveAll(cart.lines())).thenReturn(true);
        when(payments.charge(customer.id(), cart.total())).thenReturn(PaymentResult.success("PAY-1001"));
        when(repository.save(any(Order.class))).thenAnswer(inv -> inv.getArgument(0));

        Order order = orderService.confirm(cart, customer);

        assertEquals("PAY-1001", order.paymentReference());
    }
}''', title="OrderServiceTest.java", size=21),
         narration=[
             "Here's the happy path. The Mockito extension creates a mock for each field, and InjectMocks builds the service with them. Stub stock reservation to succeed and the charge to return a reference. "
             "The save stub uses thenAnswer to echo back its argument, a common idiom, because repositories usually return what they're given. Then confirm, and assert on the result. That's state verification.",
         ]),

    dict(title="The compensation path",
         kicker="Where verify earns its place",
         body=code('''
@Test
void confirm_paymentFails_releasesReservedStock() {
    when(inventory.reserveAll(cart.lines())).thenReturn(true);
    when(payments.charge(any(), any())).thenReturn(PaymentResult.declined("insufficient funds"));

    assertThrows(PaymentFailedException.class, () -> orderService.confirm(cart, customer));

    verify(inventory).releaseAll(cart.lines());       // the rule under test
    verify(repository, never()).save(any());
    verifyNoInteractions(emailSender);
}''', title="OrderServiceTest.java", size=22)
              + frag('<p class="callout">Matchers are <b>all or nothing</b>: <code>send(eq("a@b.com"), "Subject", any())</code> throws — wrap the literal in <code>eq()</code>.</p>', 1),
         narration=[
             "Now the rule that matters. Stock is reserved, payment is declined. Assert that confirm throws. Then verify that releaseAll was called, that nothing was saved, and that no email went out. "
             "Releasing stock returns nothing and leaves no state the caller can see. Verifying the interaction is the only way to assert it, and that's exactly what verify is for.",
             "One rule about matchers. If one argument uses a matcher, every argument must. Mixing any with a raw string throws InvalidUseOfMatchersException. Wrap the literal in eq.",
         ]),

    dict(title="Captors, spies and strict stubs",
         kicker="Worked examples",
         body=code('''
verify(repository).save(orderCaptor.capture());
Order saved = orderCaptor.getValue();              // assert on the real object, with a real diff''',
                   title="ArgumentCaptor", size=23)
              + code('''
PricingRuleEngine engine = spy(new PricingRuleEngine(remoteCatalogue));
doReturn(Money.rupees(500)).when(engine).basePriceFor(any());   // NOT when(...).thenReturn(...)''',
                     title="Spy — when() would call the real remote method", step=1, size=23)
              + code('''
when(emailSender.isAvailable()).thenReturn(true);   // never called → UnnecessaryStubbingException
when(inventory.reserveAll(cartA.lines()))...;      // called with cartB → PotentialStubbingProblem''',
                     title="Strict stubs — the default; keep them on", step=2, size=23),
         narration=[
             "Three tools. An argument captor grabs the object the code built internally, so you can assert on it after the fact and get a proper diff. Better than argThat, which only reports no matching invocation.",
             "A spy wraps a real object. On a spy, always stub with doReturn dot when. The when dot thenReturn form calls the real method while setting up the stub, hitting the remote catalogue you were trying to avoid. And a spy usually means the class does too much.",
             "And strict stubs, the extension's default. An unused stub fails the test, because either the test is wrong or the code changed. A stub called with different arguments fails too, showing both. Under lenient mode it would quietly return false and you'd debug the wrong thing.",
         ]),

    dict(title="Inject the clock; write the fake",
         kicker="Better than mocking",
         body=code('''
try (MockedStatic<OrderReferences> refs = mockStatic(OrderReferences.class)) { … }   // thread-local, must close''',
                   title="Possible…", size=22)
              + code('''
Instant placedAt = Instant.now(clock);       // production code
Clock fixed = Clock.fixed(Instant.parse("2026-09-20T10:00:00Z"), ZoneOffset.UTC);   // test''',
                     title="…but better: make time a dependency", step=1, size=22)
              + code('''
public final class InMemoryOrderRepository implements OrderRepository {
    private final Map<OrderId, Order> store = new ConcurrentHashMap<>();
    public Order save(Order o) { store.put(o.id(), o); return o; }
    public Optional<Order> findById(OrderId id) { return Optional.ofNullable(store.get(id)); }
}''', title="A fake repository — save, find, and the test reads like the domain", step=2, size=22),
         narration=[
             "Mockito 5 can mock static methods, but it's thread-local, and a leaked one breaks later tests intermittently. Mocking a static is nearly always a design smell.",
             "The usual culprits are the current time, random UUIDs and the system clock. Inject them instead. A Clock field is testable without static mocks, and it's better production code, because time becomes an explicit dependency.",
             "And for stateful collaborators with small interfaces, write a fake. A mocked repository needs a stub for every query and breaks when the service calls a different finder. A fake behaves like a repository: save something, find it.",
         ]),

    dict(title="How a mock works",
         kicker="Internals",
         body=flow(["`mock(X.class)`", "ByteBuddy redefines the class (**inline**, default since 5)", "every call → MockHandler", "stub? value : **type default**"])
              + frag(bullets(["Unstubbed methods return `null`, `0`, `false` — an NPE in a mocked test is usually a **missing stub**",
                              "Every call is recorded — which is why `verify` works after the fact",
                              "Inline maker mocks `final` classes; drop `mockito-inline`"], cls="bullets sm"), 1),
         narration=[
             "Under the hood, Mockito uses ByteBuddy to redefine the class. Since Mockito 5, the inline mock maker is the default, so final classes and static methods are mockable with no extra dependency. Every call goes to a handler, which returns a stubbed value if there is one, and the type's default otherwise.",
             "Two consequences. Unstubbed methods return null, zero or false, not errors, so a NullPointerException in a mocked test usually means a missing stub. And every invocation is recorded, which is why verify works after the fact. And remove mockito inline from your build: it's obsolete.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Mock at the **architectural boundary**",
                         "Prefer state verification",
                         "Constructor injection",
                         "Fakes for repositories",
                         "Inject `Clock` and ID generators",
                         "Keep strict stubs on"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Mock value objects — build real ones",
                         "Mock types you don't own — wrap them",
                         "`RETURNS_DEEP_STUBS`",
                         "Stub a spy with `when().thenReturn()`",
                         "`reset(mock)` — write two tests"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Mock at the architectural boundary: things that are slow, remote, non-deterministic or expensive. Prefer state verification. Use constructor injection. Write fakes for repositories. Inject the clock and ID generators. And keep strict stubs on.",
             "Never mock value objects like Money or an Order; construct real ones. Never mock types you don't own: wrap the third-party client in your own interface and mock that. Never use deep stubs. Never stub a spy with when thenReturn. And never call reset; it means one test is testing two things.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 42 · Mockito",
         body=bullets(["Stub for inputs; **verify** only invisible effects",
                       "Matchers all-or-nothing; `doReturn` on spies",
                       "Strict stubs catch dead and mismatched stubs",
                       "Inject time; fake your repositories",
                       "Next: **Ch 43 · Integration Testing &amp; Testcontainers**"], cls="bullets recap"),
         narration=[
             "To recap. Stub to supply inputs, and verify only the effects you can't see from outside. Matchers are all or nothing, and spies need doReturn. Strict stubs catch dead and mismatched stubs. "
             "And rather than mocking statics or repositories, inject time and write fakes. A suite where every test ends in verify has high coverage and almost no defect detection.",
             "Next is chapter forty-three: integration testing and Testcontainers. Thanks for watching.",
         ]),
]
