package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record Vendor(String id, String name) {
    public static final Vendor DEFAULT = new Vendor("default", "Default Vendor");
    public Quote quote(Order order) { return new Quote(this, Money.ZERO); }
}
