package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record Quote(Vendor vendor, Money price) {
    public static Quote standardRate() { return new Quote(Vendor.DEFAULT, Money.ZERO); }
}
