package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record DeliverySlot(LocalTime start, LocalTime end, ZoneId zone, SlotType type) implements Comparable<DeliverySlot> {
    @Override public int compareTo(DeliverySlot o) { return start.compareTo(o.start); }
    public DeliverySlot(LocalTime start, LocalTime end, ZoneId zone) { this(start, end, zone, SlotType.STANDARD); }
    public ZonedDateTime startOn(LocalDate date) { return ZonedDateTime.of(date, start, zone); }
}
