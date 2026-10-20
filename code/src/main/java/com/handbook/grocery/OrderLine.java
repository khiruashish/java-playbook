package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record OrderLine(Sku sku, String vendorName, int quantity, Money unitPrice,
                        boolean perishable, List<Sku> substitutes) {
    public OrderLine { substitutes = List.copyOf(substitutes); }
    public OrderLine(Sku sku, int quantity, Money unitPrice) { this(sku, "", quantity, unitPrice, false, List.of()); }
    public Money lineTotal()  { return unitPrice.times(quantity); }
    public Money total()      { return lineTotal(); }
}
