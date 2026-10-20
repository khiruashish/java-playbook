/** Java 14: switch as an expression — arrows, no fall-through, several labels, and yield. */
public class J14_SwitchExpressions {

    enum Slot { EXPRESS, SAME_DAY, NEXT_DAY, SCHEDULED }

    public static void main(String[] args) {
        for (Slot slot : Slot.values()) {
            int fee = switch (slot) {                         // the switch produces a value
                case EXPRESS -> 99;
                case SAME_DAY, NEXT_DAY -> 49;                // several labels, no fall-through
                case SCHEDULED -> {
                    int base = 25;
                    yield base + 10;                          // yield returns from a block
                }
            };                                                // no default: the compiler checks every constant
            System.out.printf("%-10s ₹%d%n", slot, fee);
        }

        // The old statement form, for comparison — easy to forget a break
        String old;
        switch (Slot.EXPRESS) {
            case EXPRESS: old = "fast"; break;
            default: old = "normal";
        }
        System.out.println("old style: " + old);
    }
}
