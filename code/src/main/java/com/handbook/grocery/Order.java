package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** The canonical order. Chapters show excerpts of it. */
public record Order(OrderId id, CustomerId customerId, List<OrderLine> lines, Instant placedAt,
                    LocalDate deliveryDate, DeliverySlot slot, OrderStatus status, Priority priority,
                    String city, String paymentReference) {
    public Order { lines = List.copyOf(lines); }
    public Money total()              { return lines.stream().map(OrderLine::lineTotal).reduce(Money.ZERO, Money::plus); }
    public long totalPaise()          { return total().paise(); }
    public boolean isConfirmed()      { return status == OrderStatus.CONFIRMED; }
    public String reference()         { return id.value(); }
    public String summary()           { return id.value() + " " + total(); }
    public LocalDate deliveryBy()     { return deliveryDate; }
    public List<Vendor> eligibleVendors() { return List.of(Vendor.DEFAULT); }
    public Order withPlacedAt(Instant t) { return new Order(id, customerId, lines, t, deliveryDate, slot, status, priority, city, paymentReference); }
    public static Order from(Cart cart, Customer customer, String paymentReference) {
        var lines = cart.lines().stream().map(l -> new OrderLine(l.sku(), l.quantity(), l.unitPrice())).toList();
        return new Order(OrderId.random(), customer.id(), lines, Instant.now(), null, null,
                         OrderStatus.CONFIRMED, Priority.NORMAL, "", paymentReference);
    }
    public static Order parse(String csvRow) { throw new UnsupportedOperationException(csvRow); }
}
