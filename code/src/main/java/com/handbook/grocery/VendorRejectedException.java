package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class VendorRejectedException extends RuntimeException {
    public VendorRejectedException(int status, String body) { super(status + ": " + body); }
}
