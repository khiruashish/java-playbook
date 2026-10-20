package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/**
 * The variables handbook snippets assume already exist. Test harness only:
 * tools/check-code-blocks.py makes each wrapped snippet extend this class.
 */
public abstract class SnippetContext {
    protected Cart cart; protected List<CartLine> lines; protected Sku sku, milk, rice, atta;
    protected Catalogue catalogue; protected Order order; protected List<Order> orders;
    protected OrderRepository repository; protected Customer customer; protected CustomerId customerId;
    protected InventoryClient inventory; protected Log log; protected List<Sku> skus, incoming, mutableList;
    protected OrderService orderService; protected HttpClient CLIENT; protected VendorClient vendorClient;
    protected WarehouseClient warehouseClient; protected HttpRequest request; protected OrderId orderId, id;
    protected Ledger ledger; protected Alerting alerting; protected Queue<OrderId> retryQueue;
    protected Map<OrderId, Order> reservations; protected Path path; protected Deque<Order> deque;
    protected NavigableSet<Sku> sortedSkus; protected Map<Sku, Money> prices; protected Instant since;
    protected LocalDate today; protected PaymentGateway payments; protected EmailSender emailSender;
    protected PricingRuleEngine engine; protected PricingEngine pricingEngine; protected CustomerDirectory customers;
    protected Clock clock; protected ExecutorService executor, ioExecutor; protected InventoryItem item;
    protected List<Vendor> vendors; protected Vendor vendor; protected DeliverySlot slot; protected String input;
}
