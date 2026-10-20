import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** ConcurrentHashMap rejects null keys and values — so get() returning null always means "absent". */
public class NoNulls {

    public static void main(String[] args) {
        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put("MILK", null);
        System.out.println("HashMap.get(MILK) = " + hashMap.get("MILK") + ", containsKey = " + hashMap.containsKey("MILK")
                           + "   <- null is ambiguous");

        Map<String, Integer> chm = new ConcurrentHashMap<>();
        try { chm.put("MILK", null); } catch (NullPointerException e) { System.out.println("ConcurrentHashMap.put(MILK, null) -> NullPointerException"); }
        try { chm.put(null, 1); }      catch (NullPointerException e) { System.out.println("ConcurrentHashMap.put(null, 1)    -> NullPointerException"); }

        System.out.println("\nWhy: between get() == null and containsKey(), another thread may change the map,");
        System.out.println("so a concurrent map cannot let null mean two things. Swapping HashMap for");
        System.out.println("ConcurrentHashMap breaks code that stored null values.");
    }
}
