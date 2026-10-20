package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

@FunctionalInterface
public interface PricingRule {
    Money apply(Money subtotal);
    default PricingRule andThen(PricingRule next) { return s -> next.apply(apply(s)); }
    default Money evaluateExpensively(Cart cart) { return apply(cart.total()); }
    static PricingRule none() { return s -> s; }
}
