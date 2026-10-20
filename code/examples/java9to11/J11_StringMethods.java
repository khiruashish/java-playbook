/** Java 11: isBlank, strip, lines, repeat. */
public class J11_StringMethods {

    public static void main(String[] args) {
        System.out.println("\"   \".isBlank()   = " + "   ".isBlank());
        System.out.println("\"   \".isEmpty()   = " + "   ".isEmpty());
        System.out.println("strip():          [" + "\u2003 MILK \u2003".strip() + "]   (Unicode-aware)");
        System.out.println("trim():           [" + "\u2003 MILK \u2003".trim() + "]   (only ASCII spaces)");
        System.out.println("stripLeading():   [" + "  MILK  ".stripLeading() + "]");
        System.out.println("repeat(3):        " + "-=".repeat(3));

        String csv = "MILK,60\nRICE,450\n\nTEA,120";
        System.out.println("lines(), skipping blanks: " + csv.lines().filter(l -> !l.isBlank()).toList());
    }
}
