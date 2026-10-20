package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record ReservationResult(boolean succeeded, int quantity, String reason) {
    public static ReservationResult reserved(int q)     { return new ReservationResult(true, q, null); }
    public static ReservationResult insufficient(int a) { return new ReservationResult(false, a, "insufficient"); }
    public static ReservationResult invalid()           { return new ReservationResult(false, 0, "invalid"); }
    public static ReservationResult busy()              { return new ReservationResult(false, 0, "busy"); }
}
