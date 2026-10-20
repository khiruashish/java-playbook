import java.time.*;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

/** java.time: immutable, clear types for dates, times, instants, durations and zones. */
public class J8_08_DateTime {

    public static void main(String[] args) {
        LocalDate orderDate = LocalDate.of(2026, 3, 28);
        LocalDate delivery = orderDate.plusDays(3);
        System.out.println("order " + orderDate + ", delivery " + delivery + " (" + delivery.getDayOfWeek() + ")");
        System.out.println("days between: " + ChronoUnit.DAYS.between(orderDate, delivery));
        System.out.println("period to year end: " + Period.between(orderDate, LocalDate.of(2026, 12, 31)));

        LocalDateTime slotStart = LocalDateTime.of(2026, 3, 28, 18, 0);
        Duration slot = Duration.ofMinutes(90);
        System.out.println("slot " + slotStart.toLocalTime() + " - " + slotStart.plus(slot).toLocalTime() + " (" + slot + ")");

        ZonedDateTime bengaluru = slotStart.atZone(ZoneId.of("Asia/Kolkata"));
        System.out.println("same instant in London: " + bengaluru.withZoneSameInstant(ZoneId.of("Europe/London")).toLocalTime());
        System.out.println("as an Instant (UTC):    " + bengaluru.toInstant());

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("dd MMM yyyy, hh:mm a");
        System.out.println("formatted: " + slotStart.format(fmt));
        System.out.println("parsed:    " + LocalDate.parse("2026-04-01").plusMonths(1));

        // Immutability: plusDays returns a NEW object
        LocalDate d = LocalDate.of(2026, 1, 31);
        d.plusDays(1);
        System.out.println("d after d.plusDays(1) without assigning: " + d + "   <- unchanged");
        System.out.println("Jan 31 + 1 month = " + d.plusMonths(1) + "   <- clamps to end of February");
    }
}
