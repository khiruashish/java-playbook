/** Java 21: record patterns destructure a record — even nested ones — right in the pattern. */
public class J21_RecordPatterns {

    record Point(double lat, double lon) { }
    sealed interface Delivery permits HomeDelivery, StorePickup { }
    record HomeDelivery(String customer, Point location) implements Delivery { }
    record StorePickup(String customer, String storeCode) implements Delivery { }

    static String route(Delivery d) {
        return switch (d) {
            case HomeDelivery(String who, Point(double lat, double lon)) when lat > 13.0 ->
                who + ": north zone van (" + lat + ", " + lon + ")";
            case HomeDelivery(String who, Point(var lat, var lon)) ->                // var inside patterns
                who + ": south zone van (" + lat + ", " + lon + ")";
            case StorePickup(String who, String store) ->
                who + ": ready at store " + store;
        };
    }

    public static void main(String[] args) {
        System.out.println(route(new HomeDelivery("Asha", new Point(13.04, 77.59))));
        System.out.println(route(new HomeDelivery("Ravi", new Point(12.91, 77.64))));
        System.out.println(route(new StorePickup("Meera", "BLR-07")));

        Object o = new Point(12.97, 77.59);
        if (o instanceof Point(double lat, double lon)) {                         // also works with instanceof
            System.out.println("instanceof destructured: lat=" + lat + " lon=" + lon);
        }
    }
}
