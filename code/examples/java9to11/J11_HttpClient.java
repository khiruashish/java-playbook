import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

/** Java 11: the standard HTTP client. A tiny local server stands in for a real vendor API. */
public class J11_HttpClient {

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);   // any free port
        server.createContext("/price", exchange -> {
            byte[] body = "{\"sku\":\"MILK-1L\",\"price\":60}".getBytes();
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, body.length);
            exchange.getResponseBody().write(body);
            exchange.close();
        });
        server.start();
        URI uri = URI.create("http://127.0.0.1:" + server.getAddress().getPort() + "/price");

        HttpClient client = HttpClient.newBuilder()               // create ONCE and reuse
            .connectTimeout(Duration.ofSeconds(2))
            .build();
        HttpRequest request = HttpRequest.newBuilder(uri)
            .timeout(Duration.ofSeconds(5))                      // set this too — it covers the whole exchange
            .GET().build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("sync:  " + response.statusCode() + " " + response.body());

        CompletableFuture<String> async = client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(HttpResponse::body);
        System.out.println("async: " + async.join());

        server.stop(0);
    }
}
