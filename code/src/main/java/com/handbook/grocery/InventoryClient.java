package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public interface InventoryClient {
    boolean reserveAll(List<CartLine> lines);
    void releaseAll(List<CartLine> lines);
    StockStatus statusFor(Cart cart);
    boolean reserve(Sku sku, int quantity);
}
