import java.util.*;

/** Problem: implement a growable list with a fail-fast iterator (like java.util.ArrayList). */
public class MyArrayList<E> implements Iterable<E> {

    private Object[] elements = new Object[4];
    private int size;
    private int modCount;              // bumped on every structural change

    public void add(E e) {
        if (size == elements.length) elements = Arrays.copyOf(elements, size + (size >> 1) + 1);  // grow ~1.5x
        elements[size++] = e;
        modCount++;
    }

    @SuppressWarnings("unchecked")
    public E get(int i) {
        Objects.checkIndex(i, size);
        return (E) elements[i];
    }

    public E remove(int i) {
        E old = get(i);
        System.arraycopy(elements, i + 1, elements, i, size - i - 1);
        elements[--size] = null;       // let GC reclaim the reference (avoid a memory leak)
        modCount++;
        return old;
    }

    public int size() { return size; }

    int capacity() { return elements.length; }

    @Override
    public Iterator<E> iterator() {
        return new Iterator<>() {
            int cursor;
            int lastReturned = -1;
            int expectedModCount = modCount;

            public boolean hasNext() { return cursor < size; }

            public E next() {
                checkForComodification();
                if (cursor >= size) throw new NoSuchElementException();
                lastReturned = cursor;
                return get(cursor++);
            }

            /** The safe way to remove while iterating: keeps expectedModCount in sync. */
            public void remove() {
                if (lastReturned < 0) throw new IllegalStateException();
                checkForComodification();
                MyArrayList.this.remove(lastReturned);
                cursor = lastReturned;
                lastReturned = -1;
                expectedModCount = modCount;
            }

            private void checkForComodification() {
                if (modCount != expectedModCount) throw new ConcurrentModificationException();
            }
        };
    }

    public static void main(String[] args) {
        MyArrayList<Integer> list = new MyArrayList<>();
        for (int i = 1; i <= 10; i++) list.add(i);
        System.out.println("size=" + list.size() + " capacity=" + list.capacity());

        try {
            for (Integer x : list) if (x == 3) list.remove(0);     // structural change behind the iterator's back
            check(false, "expected CME");
        } catch (ConcurrentModificationException e) {
            System.out.println("for-each + list.remove -> ConcurrentModificationException (fail-fast)");
        }

        for (Iterator<Integer> it = list.iterator(); it.hasNext(); ) if (it.next() % 2 == 0) it.remove();
        StringBuilder sb = new StringBuilder();
        for (Integer x : list) sb.append(x).append(' ');
        System.out.println("after iterator.remove of evens: " + sb.toString().trim());
        check(list.size() == 4 && list.get(0) == 3 && list.get(3) == 9, "iterator.remove");
        try { list.get(4); check(false, "bounds"); } catch (IndexOutOfBoundsException e) { System.out.println("get(4) -> " + e.getClass().getSimpleName()); }
        System.out.println("PASS");
    }

    static void check(boolean ok, String what) { if (!ok) { System.out.println("FAILED: " + what); System.exit(1); } }
}
