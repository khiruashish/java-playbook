package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record RequestContext(TenantId tenant, String traceId, CustomerId customer) {
    public static final RequestContext ANONYMOUS = new RequestContext(TenantId.SYSTEM, "", CustomerId.NONE);
    public RequestContext withTenant(TenantId t) { return new RequestContext(t, traceId, customer); }
    public Cart cart() { return new Cart(new CartId(""), List.of()); }
}
