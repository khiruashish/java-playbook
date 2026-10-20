package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public record Config(Map<String, String> values) {
    public static Config parse(String text) { return new Config(Map.of()); }
}
