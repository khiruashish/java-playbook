package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record CustomerId(String value) {
    public static final CustomerId NONE = new CustomerId("");
    public static CustomerId of(String value) { return new CustomerId(value); }
}
