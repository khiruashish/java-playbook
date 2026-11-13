"""Chapter 10 — java.time. Source: docs/02-language/10-java-time.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 10 · java.time"
SECTION = "Java 8"

SLIDES = [
    dict(kind="title",
         title="java.time",
         kicker="Java 8 · Chapter 10",
         body='<p class="sub">Which type to use, what happens across a daylight-saving change, '
              'and how to make time testable.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter ten: java dot time.",
             "java dot time replaced an API so badly designed that its flaws are a standard interview question. "
             "The replacement is good, but only if you pick the right type. Most date bugs in modern Java are a LocalDateTime where an Instant belonged.",
         ]),

    dict(title="Four defects in six lines",
         kicker="The problem",
         body=code('''
Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("Asia/Kolkata"));
cal.set(2026, 8, 20, 14, 30, 0);       // 8 means September — zero-based
Date slotStart = cal.getTime();        // mutable, and not actually a date
SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm");   // not thread-safe''',
                   title="LegacyDate.java — Java 7", size=26)
              + code('''
ZonedDateTime slotStart = ZonedDateTime.of(
    LocalDate.of(2026, Month.SEPTEMBER, 20), LocalTime.of(14, 30), ZoneId.of("Asia/Kolkata"));
String label = slotStart.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"));''',
                     title="ModernTime.java — Java 8", step=1, size=26),
         narration=[
             "Here's a delivery slot in Java 7. Four defects in a few lines. Months are zero-based, so eight means September. "
             "Date is mutable, so callers can change it under you. Date isn't even a date. It's a millisecond instant with a misleading name. "
             "And SimpleDateFormat isn't thread-safe. A shared static formatter silently produces wrong output, one of the classic Java production bugs.",
             "In Java 8, it's a ZonedDateTime built from a LocalDate, a LocalTime and a ZoneId. Months are one-based, and you can use the Month enum. "
             "Everything is immutable, the types say what they mean, and the formatter is thread-safe.",
         ]),

    dict(title="Machine time vs human time",
         kicker="Mental model",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Machine time", "A point on the timeline\n`Instant` — nanos since epoch, UTC\n`Duration` — exact elapsed time", "indigo", 0)
              + card("Human time", "What a calendar and clock show\n`LocalDate` · `LocalTime`\n`LocalDateTime` · `Period`", "cyan", 1)
              + card("The bridge", "Human time + a zone\n`ZonedDateTime` — with DST rules\n`OffsetDateTime` — fixed offset", "fuchsia", 2)
              + "</div>"
              + frag('<p class="callout"><code>LocalDateTime</code> has no zone, so it is <b>not a timestamp</b>. '
                     'It\'s for recurring wall-clock ideas — "the warehouse opens at 09:00 every day".</p>', 3),
         narration=[
             "The most useful distinction in this API is machine time versus human time. Machine time is a point on the timeline. "
             "An Instant is nanoseconds since the epoch in UTC, and a Duration is an exact amount of elapsed time.",
             "Human time is what a calendar and a clock show. LocalDate, LocalTime, LocalDateTime, and Period, a calendar amount like two months and three days.",
             "And the bridge between them is a zone. ZonedDateTime is human time plus a region with daylight-saving rules. OffsetDateTime uses a fixed offset.",
             "Here's the key warning. LocalDateTime has no time zone, so it is not a timestamp. You can't compare two across zones. "
             "Storing one for an event that happened is the most common mistake in this whole area. It's only right for recurring wall-clock ideas, like the warehouse opens at nine every day.",
         ]),

    dict(title="Pick the type by meaning",
         kicker="Worked example",
         body=code('''
public record Order(
    OrderId id,
    Instant placedAt,          // when it happened — machine time
    LocalDate deliveryDate,    // a calendar date the customer chose
    DeliverySlot slot) { }

public record DeliverySlot(LocalTime start, LocalTime end, ZoneId zone) {
    public ZonedDateTime startOn(LocalDate date) {
        return ZonedDateTime.of(date, start, zone);
    }
}''', title="OrderTypes.java", size=28)
              + frag('<p class="callout"><b>Instant</b> in the core and the database. <b>ZonedDateTime</b> only at the presentation edge.</p>', 1),
         narration=[
             "Pick each type by what it means. placedAt is an Instant, because it's a fact about the timeline. "
             "deliveryDate is a LocalDate, because the customer picked a date, not an instant. "
             "And the slot's start is a LocalTime with a zone, because it means two thirty every day, in a particular city.",
             "The rule for the whole system: store and transmit Instants. Convert to a ZonedDateTime only at the last moment, for display. "
             "Convert early, and every comparison downstream has to reason about zones.",
         ]),

    dict(title="Daylight saving: Period vs Duration",
         kicker="Where the bugs live",
         body=code('''
ZoneId london = ZoneId.of("Europe/London");
ZonedDateTime before = ZonedDateTime.of(LocalDate.of(2026, Month.MARCH, 28), LocalTime.of(14, 0), london);''',
                   title="DstArithmetic.java", size=25)
              + '<div class="grid2">'
              + frag(code('''
before.plus(Period.ofDays(1));
// 2026-03-29T14:00+01:00  ← still 14:00''', title="Period — one calendar day", size=25)
                     + card("Tomorrow at 2 pm", "A delivery date", "indigo"), 1)
              + frag(code('''
before.plus(Duration.ofHours(24));
// 2026-03-29T15:00+01:00  ← 15:00''', title="Duration — exactly 24 hours", size=25)
                     + card("In 24 hours", "A token expiry or timeout", "fuchsia"), 2)
              + "</div>",
         narration=[
             "Daylight saving is where the bugs live. India has no daylight saving, so let's use London. "
             "Start at two pm on the twenty-eighth of March, the day before the clocks go forward.",
             "Add a Period of one day, and you get two pm the next day. Same wall-clock time. That's what a delivery scheduled for tomorrow at two needs.",
             "Add a Duration of twenty-four hours, and you get three pm, because an hour vanished when the clocks changed. That's right for a token that expires in twenty-four hours. "
             "Both are correct. They answer different questions. Use the wrong one and you get a bug that shows up twice a year.",
         ]),

    dict(title="Gaps &amp; overlaps",
         kicker="Silent resolution",
         body=code('''
// 01:30 does not exist on 29 March in London — moved forward by the gap
ZonedDateTime.of(LocalDate.of(2026, Month.MARCH, 29), LocalTime.of(1, 30), london);
// 2026-03-29T02:30+01:00[Europe/London]

// 01:30 happens twice on 25 October — the EARLIER offset is chosen
ZonedDateTime.of(LocalDate.of(2026, Month.OCTOBER, 25), LocalTime.of(1, 30), london);
// 2026-10-25T01:30+01:00[Europe/London]    withLaterOffsetAtOverlap() picks the second''',
                   title="DstEdges.java", size=26)
              + frag('<p class="callout">No exception — a scheduling bug gives a <b>wrong time</b>. If a gap is an error in your domain, '
                     'check <code>zone.getRules().getValidOffsets(ldt)</code>.</p>', 1),
         narration=[
             "When the clocks spring forward, some wall-clock times don't exist. One thirty on the twenty-ninth of March never happens in London, "
             "so ZonedDateTime moves it forward to two thirty. When the clocks fall back, one thirty happens twice, and the earlier offset is chosen. "
             "withLaterOffsetAtOverlap picks the second occurrence instead.",
             "Neither case throws. That's usually what you want, but it means a scheduling bug produces a wrong time rather than an exception. "
             "If a gap should be an error in your domain, check the zone rules' valid offsets explicitly.",
         ]),

    dict(title="Calendar arithmetic",
         kicker="Worked examples",
         body=code('''
LocalDate nextMonday = today.with(TemporalAdjusters.next(DayOfWeek.MONDAY));
LocalDate billingEnd = today.with(TemporalAdjusters.lastDayOfMonth());

List<LocalDate> deliveryDates = start.datesUntil(end)          // Java 9
    .filter(d -> d.getDayOfWeek() != DayOfWeek.SUNDAY)
    .toList();

long daysOpen = ChronoUnit.DAYS.between(order.deliveryDate(), today);''', title="BusinessDates.java", size=27)
              + frag('<p class="callout"><code>Period.between(31 Jan, 1 Mar)</code> is <code>P1M1D</code> — a calendar description, '
                     'not a count. For a count, use <code>ChronoUnit.DAYS.between</code>.</p>', 1),
         narration=[
             "Calendar questions that people used to write loops for are one-liners. TemporalAdjusters give you next Monday, or the last day of the billing month. "
             "Java 9's datesUntil streams every date in a range, so excluding Sundays is just a filter. And ChronoUnit dot DAYS dot between counts whole days.",
             "Careful with Period dot between. From the thirty-first of January to the first of March is one month and one day, not twenty-nine days. "
             "It describes the gap in calendar terms. When you want a count, use ChronoUnit.",
         ]),

    dict(title="Make time testable",
         kicker="Inject a Clock",
         body='<div class="grid2 start">'
              + code('''
public final class OrderService {
    private final Clock clock;

    public OrderService(Clock clock) {
        this.clock = clock;
    }

    public Order confirm(Cart cart, Customer c) {
        Instant placedAt = Instant.now(clock);
        LocalDate deliveryBy =
            LocalDate.now(clock).plusDays(2);
        // ...
    }
}''', title="ClockInjection.java", size=24)
              + frag(code('''
Clock fixed = Clock.fixed(
    Instant.parse("2026-09-20T09:00:00Z"),
    ZoneOffset.UTC);

Order order = new OrderService(fixed)
    .confirm(cart, customer);

assertEquals(LocalDate.of(2026, 9, 22),
             order.deliveryBy());''', title="ClockInTest.java", size=24)
                     + bullets(["Production: `Clock.systemUTC()`",
                                "Tests: `Clock.fixed`, `Clock.offset`"], cls="bullets sm"), 1)
              + "</div>",
         narration=[
             "To make time testable, don't call Instant dot now with no arguments. Every now method in java dot time accepts a Clock. "
             "Inject one through the constructor, and call Instant dot now of clock.",
             "In a test, pass Clock dot fixed at nine am on the twentieth of September, and you can assert the delivery date is exactly the twenty-second. "
             "No static mocking needed, and time becomes an explicit dependency. In production, inject Clock dot systemUTC.",
         ]),

    dict(title="Internals that bite",
         kicker="Immutability · precision · zones",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Immutable", "`date.plusDays(1);` as a statement does **nothing** — the result is discarded.", "indigo", 0)
              + card("Precision", "`Instant` holds nanos; Postgres `timestamptz` keeps **micros**. Truncate before persisting.", "cyan", 1)
              + card("ZoneId, not offset", "Store a future event as `Europe/London` + local time. A fixed `+01:00` breaks when DST rules change.", "fuchsia", 2)
              + "</div>"
              + frag('<p class="callout">JDBC 4.2 reads and writes <code>java.time</code> directly — <code>setObject(1, instant)</code>. '
                     'Convert legacy <code>Date</code> only at the boundary.</p>', 3),
         narration=[
             "Three internals that bite. Everything is immutable. So calling date dot plusDays one as a statement does nothing. The result is thrown away, and the compiler won't warn you.",
             "Precision. An Instant holds nanoseconds, but Postgres timestamptz keeps microseconds. Round-trip through the database and equality assertions break. "
             "Truncate to micros before persisting, so the loss is explicit.",
             "And zones. For a future event, store the zone ID, like Europe slash London, plus the local time. "
             "Store a fixed offset instead, and when a government changes its daylight-saving rules, which happens, your meeting moves.",
             "For legacy code, JDBC 4.2 reads and writes java dot time types directly, so convert Date and Timestamp only at the boundary.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Store and transmit `Instant`",
                         "`LocalDate` for genuine dates",
                         "Inject a `Clock`",
                         "`Period` for calendar, `Duration` for elapsed",
                         "`ZoneId` for future events",
                         "`static final DateTimeFormatter`",
                         "`Month` / `DayOfWeek` enums, not ints"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`LocalDateTime` as a timestamp",
                         "`Date`, `Calendar`, `SimpleDateFormat` in new code",
                         "Discard the result of `plusDays`",
                         "Rely on the JVM default time zone",
                         "Store a fixed offset for a future event",
                         "`Duration.ofDays` for calendar days",
                         "Assume nanos survive persistence"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Store and transmit Instants. Use LocalDate for genuine dates. Inject a Clock. Period for calendar arithmetic, Duration for elapsed time. "
             "ZoneId for future events. Declare formatters static final, since they're thread-safe. And use the Month and DayOfWeek enums instead of integers.",
             "Never use LocalDateTime as a timestamp. Never use Date, Calendar or SimpleDateFormat in new code. Never discard the result of plusDays. "
             "Never rely on the JVM's default time zone in server code. Never store a fixed offset for a future event. "
             "Never use Duration of days for calendar days. And never assume nanoseconds survive a trip through the database.",
         ]),

    dict(title="Java 8 → 26",
         kicker="Version evolution",
         body=table(["Version", "What changed"], [
                    ["**8**", "`java.time` (JSR-310) + legacy conversion methods"],
                    ["**9**", "`LocalDate.datesUntil`, better `Duration` arithmetic"],
                    ["**12**", "`Duration.toHoursPart()` and friends"],
                    ["**16**", "Day-period formatting — the `B` pattern"],
                    ["**19+**", "tz database updates every release — keep the JDK current"],
                ], step_per_row=0, cls="wide"),
         narration=[
             "Java 8 delivered java dot time, plus methods to convert to and from the legacy types.",
             "Java 9 added datesUntil and better Duration arithmetic.",
             "Java 12 added toHoursPart and friends, so you can format a duration without manual modulo maths.",
             "Java 16 added locale-correct day periods, like in the morning.",
             "And every release ships time zone database updates, because zone rules change by law several times a year. That's a real reason to keep your JDK current.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 10 · java.time",
         body=bullets(["**Machine time** (`Instant`, `Duration`) vs **human time** (`Local*`, `Period`)",
                       "`LocalDateTime` is **not** a timestamp",
                       "`Instant` in the core; zone it only for display",
                       "`Period` = tomorrow at 2 pm · `Duration` = in 24 hours",
                       "Inject a `Clock`; store `ZoneId` for future events",
                       "That completes the **Java 8** tab"], cls="bullets recap"),
         narration=[
             "To recap. Separate machine time, Instant and Duration, from human time, the Local types and Period. LocalDateTime is not a timestamp. "
             "Keep Instants in the core and add a zone only for display. Period means tomorrow at two, Duration means in twenty-four hours. "
             "Inject a Clock, and store a zone ID for future events.",
             "That completes the Java 8 chapters of the handbook. The full chapter, with interview questions, is on the site. Thanks for watching.",
         ]),
]
