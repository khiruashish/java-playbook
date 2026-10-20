package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class Catalogue {
    private final Map<Sku, InventoryItem> items = new HashMap<>();
    public Optional<InventoryItem> find(Sku sku)  { return Optional.ofNullable(items.get(sku)); }
    public int availableQuantity(Sku sku)         { return find(sku).map(InventoryItem::available).orElse(0); }
    public Optional<Money> priceFor(Sku sku)      { return Optional.empty(); }
    public Set<Sku> skus()                        { return Set.copyOf(items.keySet()); }
    public void index(Sku sku)                    { }
}
