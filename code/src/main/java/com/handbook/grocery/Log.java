package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** Minimal SLF4J-shaped logger so snippets that log can compile. */
public interface Log {
    void info(String msg, Object... args);
    void warn(String msg, Object... args);
    void error(String msg, Object... args);
    void debug(String msg, Object... args);
    void debug(String msg, Supplier<?> lazy);
}
