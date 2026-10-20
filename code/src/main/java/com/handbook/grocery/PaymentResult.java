package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record PaymentResult(boolean successful, String reference, String reason) {
    public static PaymentResult success(String ref) { return new PaymentResult(true, ref, null); }
    public static PaymentResult declined(String why) { return new PaymentResult(false, null, why); }
}
