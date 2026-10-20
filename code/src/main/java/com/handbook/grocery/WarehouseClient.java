package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public interface WarehouseClient {
    InventoryStatus statusFor(Sku sku);
    int fetchStock(Sku sku);
}
