package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record OrderContext(StockStatus stock, PricingSnapshot pricing, DeliveryProfile profile, List<Sku> recommendations) {
    public OrderContext(StockStatus s, PricingSnapshot p, DeliveryProfile d) { this(s, p, d, List.of()); }
    public OrderContext(StockStatus s, List<Sku> recs) { this(s, null, null, recs); }
    public OrderContext(StockStatus s, PricingSnapshot p) { this(s, p, null, List.of()); }
    public static OrderContext unavailable() { return new OrderContext(null, null, null, List.of()); }
}
