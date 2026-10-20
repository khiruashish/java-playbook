package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class VendorUnavailableException extends RuntimeException {
    public VendorUnavailableException() { }
    public VendorUnavailableException(int status) { super("HTTP " + status); }
    public VendorUnavailableException(Throwable cause) { super(cause); }
}
