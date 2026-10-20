/** Java 15: text blocks — multi-line strings without escapes or concatenation. */
public class J15_TextBlocks {

    public static void main(String[] args) {
        String json = """
            {
              "orderId": "O1",
              "items": ["MILK", "RICE"],
              "note": "leave at "the gate""
            }
            """;                                 // closing delimiter's position sets the indentation
        System.out.print(json);

        String sql = """
            SELECT id, total
            FROM orders
            WHERE customer_id = ? \
            AND placed_at >= ?""";              // backslash joins lines: no newline inserted
        System.out.println(sql);

        System.out.println("""
            Hello %s, your order %s is on its way.""".formatted("Asha", "O1"));
    }
}
