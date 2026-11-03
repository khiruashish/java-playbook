/** Problem: reverse a singly linked list (iteratively and recursively), find the middle, detect a cycle. */
public class LinkedListOps {

    static final class Node {
        int val; Node next;
        Node(int val, Node next) { this.val = val; this.next = next; }
    }

    static Node of(int... values) {
        Node head = null;
        for (int i = values.length - 1; i >= 0; i--) head = new Node(values[i], head);
        return head;
    }

    /** Three pointers: prev, current, next. O(n) time, O(1) space. */
    static Node reverseIterative(Node head) {
        Node prev = null, curr = head;
        while (curr != null) {
            Node next = curr.next;   // 1. remember the rest
            curr.next = prev;        // 2. flip the arrow
            prev = curr;             // 3. advance prev
            curr = next;             // 4. advance curr
        }
        return prev;
    }

    /** O(n) time but O(n) stack: can StackOverflowError on very long lists. */
    static Node reverseRecursive(Node head) {
        if (head == null || head.next == null) return head;
        Node newHead = reverseRecursive(head.next);
        head.next.next = head;
        head.next = null;
        return newHead;
    }

    /** Slow/fast pointers: when fast reaches the end, slow is in the middle. */
    static Node middle(Node head) {
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
        return slow;
    }

    /** Floyd's tortoise and hare: if there is a cycle, fast eventually laps slow. */
    static boolean hasCycle(Node head) {
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    static String str(Node n) {
        StringBuilder sb = new StringBuilder();
        for (; n != null; n = n.next) sb.append(n.val).append(n.next == null ? "" : " -> ");
        return sb.length() == 0 ? "<empty>" : sb.toString();
    }

    public static void main(String[] args) {
        System.out.println("original           : " + str(of(1, 2, 3, 4, 5)));
        System.out.println("reverse iterative  : " + str(reverseIterative(of(1, 2, 3, 4, 5))));
        System.out.println("reverse recursive  : " + str(reverseRecursive(of(1, 2, 3, 4, 5))));
        System.out.println("middle of 1..5     : " + middle(of(1, 2, 3, 4, 5)).val);
        System.out.println("middle of 1..6     : " + middle(of(1, 2, 3, 4, 5, 6)).val + " (second middle)");
        check(str(reverseIterative(of(1, 2, 3))).equals("3 -> 2 -> 1"), "iterative");
        check(str(reverseRecursive(of(1, 2, 3))).equals("3 -> 2 -> 1"), "recursive");
        check(reverseIterative(null) == null, "empty list");

        Node cyclic = of(1, 2, 3, 4);
        cyclic.next.next.next.next = cyclic.next;          // 4 -> 2
        System.out.println("hasCycle(1..4)     : " + hasCycle(of(1, 2, 3, 4)));
        System.out.println("hasCycle(4 -> 2)   : " + hasCycle(cyclic));
        check(hasCycle(cyclic) && !hasCycle(of(1, 2, 3, 4)), "Floyd");
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
