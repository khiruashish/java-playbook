"""Chapter 43 — Integration Testing & Testcontainers. Source: docs/06-testing/43-integration-testing.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 43 · Integration Testing & Testcontainers"
SECTION = "Testing"

SLIDES = [
    dict(kind="title",
         title="Integration Testing &amp; Testcontainers",
         kicker="Testing · Chapter 43",
         body='<p class="sub">Testing against real Postgres and real HTTP peers: constraints, type round-trips, retries and timeouts — and why H2 isn\'t a substitute.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter forty-three: integration testing and Testcontainers.",
             "Unit tests prove your logic. But some of the most expensive production bugs aren't in logic at all. They're in your assumptions about the database, the driver, and the services you call.",
         ]),

    dict(title="What a mocked DataSource can't tell you",
         kicker="The problem",
         body=code('''
select id, customer_id, placed_at, total_paise
from orders
where customer_id = ? and placed_at >= ?
order by placed_at desc''', lang="sql", title="OrderJdbcRepository — FIND_RECENT", size=25)
              + frag(bullets(["Does the SQL run against the **current schema**?",
                              "Does the unique constraint on `(customer_id, idempotency_key)` **fire**?",
                              "Does an `Instant` survive `timestamptz` **without shifting**?",
                              "Does `setObject(UUID)` work on **this driver**?"], cls="bullets sm"), 1),
         narration=[
             "Here's a repository query: recent orders for a customer. A unit test with a mocked DataSource stubs executeQuery to return a fake result set, and passes whether the SQL is valid, references a dropped column, or binds the timestamp wrong.",
             "Only a real database answers the real questions. Does the SQL run against the current schema? Does the unique constraint actually fire? Does an Instant survive the round trip without losing precision? Does the driver accept a UUID? "
             "Each of those has shipped as a production incident, in codebases with excellent unit-test coverage.",
         ]),

    dict(title="Crossing a boundary you don't control",
         kicker="Mental model",
         body=table(["Level", "Proves", "Scale"], [
                    ["Unit", "Is the calculation right?", "Thousands · milliseconds"],
                    ["**Integration**", "Does the SQL work? Do types round-trip?", "Hundreds · seconds"],
                    ["End-to-end", "Does checkout work?", "Tens · minutes"],
                ], step_per_row=None, cls="sm")
              + frag(flow(["Test JVM", "Testcontainers", "Docker: `postgres:16-alpine` → **random port**", "Ryuk reaps it on exit"]), 1),
         narration=[
             "Unit tests prove logic, end-to-end tests prove the system, and integration tests prove your assumptions. The useful definition: an integration test crosses at least one boundary you don't control. A database, a broker, an HTTP service.",
             "Testcontainers makes that practical. From the test JVM, it asks Docker for real Postgres, mapped to a random host port, and a sidecar called Ryuk removes it when the JVM exits, even after a kill. No shared test database, and no who broke staging.",
         ]),

    dict(title="A repository test against real Postgres",
         kicker="Worked example",
         body=code('''
@Testcontainers
class OrderJdbcRepositoryIT {
    @Container
    static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @BeforeAll static void createSchema() {
        dataSource = dataSourceFor(postgres);                   // getJdbcUrl(), never a fixed port
        Flyway.configure().dataSource(dataSource).locations("classpath:db/migration").load().migrate();
    }
    @BeforeEach void clean() { truncate("orders", "order_lines"); }

    @Test void findRecent_returnsOnlyOrdersAfterCutoff() {
        insertOrder(customerId, Instant.parse("2026-09-01T10:00:00Z"));
        insertOrder(customerId, Instant.parse("2026-09-18T10:00:00Z"));
        assertThat(repository.findRecent(customerId, Instant.parse("2026-09-15T00:00:00Z"))).hasSize(1);
    }
}''', title="OrderJdbcRepositoryIT.java", size=20)
              + frag('<p class="callout">Running the real Flyway migrations makes the <b>migration scripts themselves</b> a tested artifact.</p>', 1),
         narration=[
             "Here's the shape. A static container, so it starts once per class, not once per test. Before all tests, build a DataSource from the container's JDBC URL, and run the real Flyway migrations. Truncate the tables before each test. Then insert two orders and check the cutoff.",
             "Running the real migrations isn't incidental. It makes the migration scripts a tested artifact. A migration that fails on an empty database fails this test, not a deployment.",
         ]),

    dict(title="Constraints and round trips",
         kicker="The bugs nobody tests for",
         body=code('''
SQLException ex = assertThrows(SQLException.class,
    () -> repository.save(orderWithKey(customerId, "IDEM-1")));     // second save, same key
assertEquals("23505", ex.getSQLState());                             // unique_violation''',
                   title="Test the constraint, not the code", size=23)
              + code('''
Instant original = Instant.parse("2026-09-20T14:30:45.123456Z");
repository.save(orderPlacedAt(original));
assertEquals(original, repository.findById(orderId).orElseThrow().placedAt());''',
                     title="timestamptz keeps microseconds; Instant carries nanoseconds", step=1, size=23),
         narration=[
             "Test the constraint, not the code. Save twice with the same idempotency key, and assert the SQL state is twenty-three five oh five, the standard code for a unique violation. A state code stays stable across driver versions; a message string doesn't.",
             "And test type round trips. Postgres timestamp with time zone stores microseconds, but an Instant can carry nanoseconds, so a value can be silently truncated. The same kind of test catches money stored as a double and coming back with floating-point drift.",
         ]),

    dict(title="Real HTTP peers: retries and timeouts",
         kicker="Worked example",
         body=code('''
@Container
static final GenericContainer<?> wiremock = new GenericContainer<>("wiremock/wiremock:3.9.1")
    .withExposedPorts(8080)
    .waitingFor(Wait.forHttp("/__admin/mappings").forStatusCode(200));

@Test void send_vendorReturns503_retriesThreeTimesThenFails() {
    stubFor(post("/dispatch").willReturn(serviceUnavailable()));
    assertThrows(VendorUnavailableException.class, () -> client.send(anOrder()));
    verify(exactly(3), postRequestedFor(urlEqualTo("/dispatch")));
}
@Test void send_vendorRespondsSlowly_timesOut() {
    stubFor(post("/dispatch").willReturn(ok().withFixedDelay(5_000)));
    assertThrows(HttpTimeoutException.class, () -> client.send(anOrder()));
}''', title="VendorClientIT.java", size=21)
              + frag('<p class="callout">A Mockito mock can\'t express "responds after five seconds". Never call the <b>real</b> vendor from a test.</p>', 1),
         narration=[
             "For an outbound HTTP client, run a stub server in a container. Here WireMock, with an explicit wait strategy. Stub the dispatch endpoint to return five oh three, and verify the client retried exactly three times. Stub it to respond after five seconds, and assert a timeout.",
             "Retries, timeouts and circuit breakers only exist in the interaction with a slow or failing peer. A Mockito mock can't say responds after five seconds. And never call a real third-party service from a test: it's slow, rate-limited, sometimes billed, and your build goes red when they deploy.",
         ]),

    dict(title="Speed without losing the point",
         kicker="Internals",
         body=table(["Isolation", "Speed", "Catches commit-time failures"], [
                    ["Container per method", "Slowest", "Yes"],
                    ["**Truncate before each test**", "Fast", "**Yes**"],
                    ["Transaction + rollback", "Fastest", "**No** — commit never happens"],
                ], step_per_row=None, cls="sm")
              + frag(bullets(["**Static** `@Container`, or one singleton container per JVM",
                              "Explicit **wait strategy** — the default port check is the classic CI-only timeout",
                              "`*Test` in Surefire, `*IT` in Failsafe — keep `mvn test` fast",
                              "`await().atMost(5s).untilAsserted(…)` — **never** `Thread.sleep`"], cls="bullets sm"), 1),
         narration=[
             "Isolation is a trade-off. A container per method is perfectly isolated and slow. Rolling back a transaction is fastest, but constraint violations and deferred checks surface at commit, which never happens, so the test passes on code that fails in production. Truncating before each test is the sweet spot.",
             "To keep it fast: use static containers, or one singleton container for the whole JVM. Set an explicit wait strategy, because started isn't ready, and the default check is the classic works-locally, times-out-in-CI bug. Run integration tests in Failsafe, so the fast loop stays fast. And for asynchronous effects, poll with Awaitility. Never sleep.",
         ]),

    dict(title="Why not H2?",
         kicker="Different engine, different bugs",
         body=table(["", "H2", "Real Postgres"], [
                    ["Dialect", "Compatibility mode", "Exact"],
                    ["`jsonb`, arrays", "Absent or emulated", "Native"],
                    ["SQLState codes", "**Different**", "Same as production"],
                    ["Locking, isolation", "**Different**", "Same as production"],
                    ["Startup", "Instant", "~2 s, once per run"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">The two seconds you save buy a suite that validates a database <b>you don\'t run</b>. Match the production version, and pin the image tag.</p>', 1),
         narration=[
             "Why not H2? It's an approximation. Its dialect is a compatibility mode, JSON and arrays are missing or emulated, and its error codes, locking and isolation all differ from production.",
             "The two seconds of startup you save buy a suite that validates a database you don't run. Match the production database and version, and pin the image tag, never latest. Moving a suite off H2 will surface real bugs it was masking. Do it one repository at a time, starting with the most hand-written SQL.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Match the production DB **and version**",
                         "Pin image tags",
                         "Run the real migrations",
                         "Static or singleton containers",
                         "Assert on SQLState codes",
                         "Truncate, don't roll back"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["H2 as a stand-in",
                         "Hard-coded container ports",
                         "Real third-party services",
                         "Container reuse in CI",
                         "Integration tests in the inner loop"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Match the production database and its version. Pin image tags. Run the real migrations. Use static or singleton containers. Assert on SQL state codes. And truncate between tests rather than rolling back.",
             "Never use H2 as a stand-in. Never hard-code a container port; ask the container. Never call real third-party services. Never enable container reuse in CI, where a fresh container per run is the point. And never let integration tests run in the inner loop.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 43 · Integration Testing",
         body=bullets(["Integration tests prove your **assumptions**",
                       "Real Postgres, real migrations, random ports",
                       "Test constraints and type round trips",
                       "Stub HTTP peers to test retries and timeouts",
                       "Next: **Ch 44 · Testing Concurrent Code**"], cls="bullets recap"),
         narration=[
             "To recap. Integration tests prove the assumptions unit tests can't: SQL, constraints, types and drivers. Run real Postgres with your real migrations on random ports. Test constraints and type round trips explicitly. "
             "And stub HTTP peers in containers to test retries and timeouts.",
             "Next is chapter forty-four, the last chapter: testing concurrent code. Thanks for watching.",
         ]),
]
