package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** Lifecycle labels. The richer sealed model with per-state data is {@code OrderState} in Ch 12. */
public enum OrderStatus { PENDING, CONFIRMED, DISPATCHED, DELIVERED, CANCELLED }
