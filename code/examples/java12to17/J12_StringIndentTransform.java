/** Java 12: String.indent and String.transform. */
public class J12_StringIndentTransform {

    public static void main(String[] args) {
        String items = "MILK x2\nRICE x1";
        System.out.print("Order:\n" + items.indent(4));

        String slug = " Fresh Milk 1L ".transform(String::strip).transform(String::toLowerCase)
                                       .transform(s -> s.replace(' ', '-'));
        System.out.println("slug = " + slug);
    }
}
