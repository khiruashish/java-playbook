/** Java 14: helpful NullPointerException messages name exactly what was null. */
public class J14_HelpfulNullPointers {

    record Address(String city) { }
    record Customer(String name, Address address) { }
    record Order(String id, Customer customer) { }

    public static void main(String[] args) {
        Order order = new Order("O1", new Customer("Asha", null));
        try {
            System.out.println(order.customer().address().city().toUpperCase());
        } catch (NullPointerException e) {
            System.out.println(e.getMessage());
        }
        System.out.println("\nBefore Java 14 the message was just null — you had to guess which call in the chain failed.");
    }
}
