package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record Cart(CartId id, List<CartLine> lines) {
    public Cart { lines = List.copyOf(lines); }
    public String expensiveSummary() { return lines.toString(); }
    public Money total() { return lines.stream().map(CartLine::lineTotal).reduce(Money.ZERO, Money::plus); }
    public Cart withLine(CartLine line) { var l = new ArrayList<>(lines); l.add(line); return new Cart(id, l); }
}
