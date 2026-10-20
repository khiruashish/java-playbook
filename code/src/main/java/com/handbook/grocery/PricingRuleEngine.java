package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class PricingRuleEngine {
    public Money evaluate(Sku sku) { return basePriceFor(sku); }
    public Money basePriceFor(Sku sku) { return Money.ZERO; }
    public PricingSnapshot snapshot(Cart cart) { return new PricingSnapshot(cart.total()); }
}
