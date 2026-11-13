"""Chapter 40 — The HTTP Client. Source: docs/05-runtime/40-http-client.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 40 · The HTTP Client"
SECTION = "Runtime"

SLIDES = [
    dict(kind="title",
         title="The HTTP Client",
         kicker="Runtime · Chapter 40",
         body='<p class="sub">Configuring the JDK client correctly, sync versus async now that virtual threads exist, '
              'and what HTTP/2 and HTTP/3 change.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter forty: the HTTP client.",
             "Java 11 standardised a real HTTP client, and by Java 26 it speaks HTTP/3. Two things have changed since: virtual threads made the simple synchronous call the right default again, "
             "and HTTP/2 multiplexing means connection pool sizing no longer works the way people assume.",
         ]),

    dict(title="HttpURLConnection",
         kicker="The problem",
         body=code('''
HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
conn.setRequestMethod("POST");  conn.setDoOutput(true);
conn.setConnectTimeout(5000);   conn.setReadTimeout(10000);
try (OutputStream os = conn.getOutputStream()) { os.write(body.getBytes(UTF_8)); }
int status = conn.getResponseCode();
InputStream in = status >= 400 ? conn.getErrorStream() : conn.getInputStream();   // two streams!''',
                   title="LegacyClient.java", size=24)
              + frag('<p class="callout">Mutable, not thread-safe, errors on a <b>different stream</b>, no HTTP/2, no async. '
                     'So teams added OkHttp or Apache HttpClient — and their dependency trees and CVE feeds.</p>', 1),
         narration=[
             "Here's HttpURLConnection, designed around 1997 assumptions. Set the method, enable output, set two timeouts, write the body, read the status. Then errors come back on a different stream from successes, so forgetting that ternary loses every error body.",
             "It's mutable, not thread-safe, with no HTTP/2 and no async. So most teams added OkHttp or Apache HttpClient, along with a dependency tree and its own vulnerability feed, for something the platform should have provided.",
         ]),

    dict(title="Expensive and shared vs cheap and per-call",
         kicker="Mental model",
         body=table(["Object", "Lifetime", "Note"], [
                    ["`HttpClient`", "**Application**", "Owns connections, executor, SSL — one per app"],
                    ["`HttpRequest`", "Per call", "Immutable"],
                    ["`BodyPublisher`", "Per call", "Supplies the request body"],
                    ["`BodyHandler`", "Per call", "Decides how to read the response"],
                    ["`HttpResponse<T>`", "Per call", "Status, headers, body as `T`"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">A client per request <b>leaks connection pools</b> and defeats HTTP/2 entirely.</p>', 5),
         narration=[
             "There are a few objects. The HttpClient lives for the whole application. It owns the connections, the executor and the SSL context. One per app.",
             "An HttpRequest is per call, and immutable.",
             "A BodyPublisher supplies the request body.",
             "A BodyHandler decides how the response is read: as a string, a stream, a file.",
             "And the HttpResponse holds the status, headers and body.",
             "The asymmetry matters. The client is expensive and shared, everything else is cheap and per call. Creating a client per request leaks connection pools and defeats HTTP/2 entirely.",
         ]),

    dict(title="HTTP/1.1 → 2 → 3",
         kicker="What the protocol changes",
         body=table(["", "HTTP/1.1", "HTTP/2", "HTTP/3"], [
                    ["Transport", "TCP", "TCP", "**QUIC over UDP**"],
                    ["Concurrency", "A connection per in-flight request", "Many streams, **one** connection", "Many streams"],
                    ["Head-of-line blocking", "Per connection", "At the TCP layer", "**None**"],
                    ["Survives a network change", "No", "No", "Yes"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">Under HTTP/2 one connection carries hundreds of concurrent streams — so tuning the pool size <b>does nothing</b>.</p>', 1),
         narration=[
             "What does the protocol version change? HTTP/1.1 carries one request at a time per connection, so you pool many connections. HTTP/2 multiplexes many streams over one TCP connection, though a lost packet still blocks everything at the TCP layer. "
             "HTTP/3 runs over QUIC on UDP, with fully independent streams, faster setup, and connections that survive a network change. Java 26's client speaks HTTP/3.",
             "The consequence: under HTTP/2, a single connection carries hundreds of concurrent requests, so the pool hardly matters, and tuning its size does nothing.",
         ]),

    dict(title="A correctly configured client",
         kicker="Worked example",
         body=code('''
private static final HttpClient CLIENT = HttpClient.newBuilder()         // one per application
    .version(HttpClient.Version.HTTP_2)
    .connectTimeout(Duration.ofSeconds(5))                               // connecting only
    .followRedirects(HttpClient.Redirect.NORMAL)                         // default is NEVER
    .build();

HttpRequest request = HttpRequest.newBuilder(baseUri.resolve("/v2/dispatch"))
    .header("Idempotency-Key", order.id().toString())
    .timeout(Duration.ofSeconds(10))                                     // the WHOLE exchange
    .POST(HttpRequest.BodyPublishers.ofString(toJson(order)))
    .build();

HttpResponse<String> response = CLIENT.send(request, BodyHandlers.ofString());
return switch (response.statusCode() / 100) {                          // a 500 is NOT an exception
    case 2 -> parse(response.body());
    case 4 -> throw new VendorRejectedException(response.statusCode(), response.body());
    default -> throw new VendorUnavailableException(response.statusCode());
};''', title="VendorHttpClient.java", size=22),
         narration=[
             "Here's a correctly configured client, with four things doing real work. It's static final, owning the pool and executor. It sets both timeouts: connectTimeout covers only connecting, and the request timeout covers the whole exchange. "
             "Setting only the first leaves a hung read waiting forever, the most common misconfiguration. It sets follow redirects explicitly, because the default is never. "
             "And it checks the status code, because a five hundred is a perfectly successful send, not an exception.",
         ]),

    dict(title="Retry and streaming",
         kicker="Worked examples",
         body=code('''
for (int attempt = 1; attempt <= 3; attempt++) {
    try {
        var response = CLIENT.send(request(order), BodyHandlers.ofString());
        if (response.statusCode() < 500) return handle(response);      // never retry a 4xx
    } catch (IOException e) { last = e; }                                // connection failure: retryable
    Thread.sleep(Duration.ofMillis(200L << (attempt - 1)));             // 200, 400, 800 ms
}''', title="Retry.java — idempotent requests only", size=23)
              + code('''
HttpResponse<Stream<String>> response = CLIENT.send(request, BodyHandlers.ofLines());
try (Stream<String> lines = response.body()) {          // MUST close, or the connection isn't returned
    lines.map(Sku::parse).forEach(catalogue::index);
}''', title="Streaming.java — ofString would buffer a 2 GB export", step=1, size=23),
         narration=[
             "There's no built-in retry, so write it carefully. Retry connection failures and server errors with backoff. Never retry a four hundred, because the request itself was wrong. "
             "And only retry idempotent operations, which is why the request carries an idempotency key. Without one, a retried POST can create two orders.",
             "For large responses, don't use ofString, which buffers everything in memory. Stream with ofLines or ofInputStream. And close the stream, or the connection never goes back to the pool.",
         ]),

    dict(title="Sync or async? The answer changed",
         kicker="Virtual threads",
         body='<div class="grid2 start">'
              + code('''
// pre-21: async to spare a platform thread
CLIENT.sendAsync(request, BodyHandlers.ofString())
      .thenApply(HttpResponse::body)
      .thenApply(this::parse)
      .exceptionally(this::handleFailure);''', title="Then", size=23)
              + frag(code('''
// 21+: blocking on a virtual thread is ~free
HttpResponse<String> r =
    CLIENT.send(request, BodyHandlers.ofString());
DispatchReceipt receipt = parse(r.body());
// real stack traces, try/catch, loops''', title="Now", size=23), 1)
              + "</div>"
              + frag('<p class="callout">Default to <code>send()</code> on virtual threads. Keep <code>sendAsync</code> for genuinely event-driven pipelines.</p>', 2),
         narration=[
             "Sync or async? Before Java 21, sendAsync with a chain of stages avoided blocking an expensive platform thread.",
             "On Java 21 and later, blocking on a virtual thread costs almost nothing. So the plain send call is the right default again, with real stack traces, try-catch, and ordinary loops.",
             "Keep sendAsync for pipelines that are genuinely event-driven.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["One `static final HttpClient`",
                         "Both `connectTimeout` and request `timeout`",
                         "Set `followRedirects` explicitly",
                         "Check `statusCode()` on every response",
                         "Idempotency keys on retried writes",
                         "Stream large bodies — and close them"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["A client per request",
                         "Assume a 500 throws",
                         "Retry a 4xx, or a non-idempotent POST",
                         "`ofString` for multi-GB responses",
                         "Tune pool size under HTTP/2"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. One static final client. Set both timeouts. Set follow redirects explicitly. Check the status code on every response. Put idempotency keys on retried writes. And stream large bodies, and close them.",
             "Never create a client per request. Never assume a five hundred throws. Never retry a four hundred, or a non-idempotent POST. Never use ofString for multi-gigabyte responses. And don't bother tuning pool size under HTTP/2.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 40 · The HTTP Client",
         body=bullets(["One client, **two timeouts**, explicit redirects",
                       "4xx and 5xx are **responses**, not exceptions",
                       "Retry only idempotent requests, with backoff",
                       "HTTP/2 multiplexes; HTTP/3 removes head-of-line blocking",
                       "`send()` on virtual threads is the new default"], cls="bullets recap"),
         narration=[
             "To recap. One shared client, two timeouts, and explicit redirects. Error status codes are responses, not exceptions. Retry only idempotent requests, with backoff. HTTP/2 multiplexes, and HTTP/3 removes head-of-line blocking. "
             "And on virtual threads, the plain send call is the default again.",
             "That completes the runtime section. Thanks for watching.",
         ]),
]
