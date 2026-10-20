package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class VendorClient {
    private final HttpClient client;
    private final java.net.URI baseUri;
    public VendorClient() { this(HttpClient.newHttpClient(), java.net.URI.create("http://localhost")); }
    public VendorClient(HttpClient client, java.net.URI baseUri) { this.client = client; this.baseUri = baseUri; }
    public DispatchReceipt send(Order order) { return new DispatchReceipt(order.reference(), "sent"); }
    public DispatchReceipt dispatchBatch(List<Order> batch) { return new DispatchReceipt(null, "batch:" + batch.size()); }
}
