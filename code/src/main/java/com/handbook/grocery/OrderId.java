package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record OrderId(String value) implements Comparable<OrderId> {
    @Override public int compareTo(OrderId o) { return value.compareTo(o.value); }
    public static OrderId random() { return new OrderId(UUID.randomUUID().toString()); }
    public static OrderId of(String value) { return new OrderId(value); }
}
