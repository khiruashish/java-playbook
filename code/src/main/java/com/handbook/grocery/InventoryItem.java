package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** Mutable stock record — the shared state in the concurrency chapters. */
public class InventoryItem {
    private final Sku sku;
    private int available;
    private final Vendor vendor;
    public InventoryItem(Sku sku, int available) { this(sku, available, Vendor.DEFAULT); }
    public InventoryItem(Sku sku, int available, Vendor vendor) { this.sku = sku; this.available = available; this.vendor = vendor; }
    public Sku sku()                        { return sku; }
    public synchronized int available()     { return available; }
    public Vendor vendor()                  { return vendor; }
    public Optional<Vendor> preferredVendor() { return Optional.ofNullable(vendor); }
    public boolean perishable()             { return false; }
    public boolean discontinued()           { return false; }
    public synchronized ReservationResult reserve(int q) {
        if (q <= 0) return ReservationResult.invalid();
        if (q > available) return ReservationResult.insufficient(available);
        available -= q; return ReservationResult.reserved(q);
    }
    public synchronized void decrease(int q) { available -= q; }
    public synchronized void increase(int q) { available += q; }
}
