package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record DispatchReceipt(String reference, String status) {
    public static DispatchReceipt deferred() { return new DispatchReceipt(null, "deferred"); }
    public static DispatchReceipt timedOut() { return new DispatchReceipt(null, "timed-out"); }
    public static DispatchReceipt failed(Throwable t) { return new DispatchReceipt(null, "failed"); }
}
