import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;

/** Problem: is a string of ()[]{} (and other characters) correctly balanced? */
public class BalancedBrackets {

    private static final Map<Character, Character> OPEN_FOR = Map.of(')', '(', ']', '[', '}', '{');

    static boolean isBalanced(String s) {
        Deque<Character> stack = new ArrayDeque<>();   // ArrayDeque, not the legacy synchronized Stack
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            } else if (OPEN_FOR.containsKey(c)) {
                if (stack.isEmpty() || stack.pop() != OPEN_FOR.get(c)) return false;   // wrong or missing opener
            }
            // any other character is ignored
        }
        return stack.isEmpty();                       // leftovers mean unclosed brackets
    }

    public static void main(String[] args) {
        String[] good = {"", "()", "([]{})", "a(b[c]{d}e)f", "{[()()]}"};
        String[] bad = {"(", ")", "(]", "([)]", "((())"};
        for (String s : good) { System.out.printf("%-14s balanced=%s%n", s.isEmpty() ? "<empty>" : s, isBalanced(s)); check(isBalanced(s), s); }
        for (String s : bad) { System.out.printf("%-14s balanced=%s%n", s, isBalanced(s)); check(!isBalanced(s), s); }
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
