/** Java 9: private methods in interfaces let default methods share code without exposing it. */
public class J09_PrivateInterfaceMethods {

    interface PriceFormatter {
        default String retail(int paise)    { return format("MRP", paise); }
        default String wholesale(int paise) { return format("WHOLESALE", paise); }

        private String format(String label, int paise) {          // shared helper, not part of the API
            return label + " ₹" + paise / 100 + "." + String.format("%02d", paise % 100);
        }
    }

    public static void main(String[] args) {
        PriceFormatter f = new PriceFormatter() { };
        System.out.println(f.retail(6050));
        System.out.println(f.wholesale(5800));
    }
}
