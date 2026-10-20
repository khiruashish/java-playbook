package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record CartLine(Sku sku, String productName, String vendorName, int quantity,
                       Money unitPrice, boolean perishable, DeliverySlot deliverySlot) {
    public CartLine(Sku sku, int quantity, Money unitPrice) { this(sku, sku.code(), "", quantity, unitPrice, false, null); }
    public Money lineTotal()                 { return unitPrice.times(quantity); }
    public boolean isGift()                  { return false; }
    public CartLine withQuantity(int q)      { return new CartLine(sku, productName, vendorName, q, unitPrice, perishable, deliverySlot); }
}
