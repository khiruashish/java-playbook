package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record TenantId(String value) {
    public static final TenantId SYSTEM = new TenantId("system");
    public static TenantId of(String value) { return new TenantId(value); }
}
