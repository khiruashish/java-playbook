/** Java 9: an effectively final resource can be used in try-with-resources without redeclaring it. */
public class J09_TryWithResources {

    static class Connection implements AutoCloseable {
        final String name;
        Connection(String name) { this.name = name; System.out.println("open  " + name); }
        @Override public void close() { System.out.println("close " + name); }
    }

    public static void main(String[] args) {
        Connection primary = new Connection("orders-db");
        Connection replica = new Connection("orders-replica");

        try (primary; replica) {                         // Java 7/8 needed: try (Connection c = primary)
            System.out.println("querying " + primary.name + " and " + replica.name);
        }                                                // closed in REVERSE order
    }
}
