package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class SkuNotFoundException extends RuntimeException {
    public SkuNotFoundException(Sku sku) { super(sku.code()); }
}
