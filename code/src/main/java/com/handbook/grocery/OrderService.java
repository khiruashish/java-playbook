package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** Confirms orders. A class with injectable collaborators (Ch 10 injects a Clock; Ch 42 injects mocks). */
public class OrderService {
    private final Clock clock;
    public OrderService() { this(Clock.systemUTC()); }
    public OrderService(Clock clock) { this.clock = clock; }
    public Order confirm(Cart cart, Customer customer) {
        return Order.from(cart, customer, "PAY-" + Instant.now(clock).toEpochMilli());
    }
    public Order confirm(Cart cart) { throw new UnsupportedOperationException(); }
}
