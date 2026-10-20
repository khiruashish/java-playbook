/** Java 21: small additions — Math.clamp, StringBuilder.repeat, ranged indexOf, splitWithDelimiters, isEmoji. */
public class J21_NewStringAndMathMethods {

    public static void main(String[] args) {
        System.out.println("Math.clamp(150, 1, 100) = " + Math.clamp(150, 1, 100) + "   (cap a requested quantity)");
        System.out.println("StringBuilder.repeat:    " + new StringBuilder("|").repeat("-", 10).append("|"));
        System.out.println("indexOf('-', 5, 12):     " + "SKU-MILK-1L-AMUL".indexOf('-', 5, 12));
        System.out.println("splitWithDelimiters:     " + String.join(" ", "10+5-3".splitWithDelimiters("[+-]", 0)));
        System.out.println("Character.isEmoji('🛒'): " + Character.isEmoji("🛒".codePointAt(0)));
    }
}
