import java.nio.charset.StandardCharsets;
import java.util.*;

/** String.join, StringJoiner and java.util.Base64 — small Java 8 additions used constantly. */
public class J8_11_StringsAndBase64 {

    public static void main(String[] args) {
        System.out.println(String.join(" | ", "MILK", "RICE", "TEA"));

        StringJoiner csv = new StringJoiner(",", "{", "}");
        csv.add("O1").add("O2").add("O3");
        System.out.println(csv);

        String token = Base64.getEncoder().encodeToString("asha:secret".getBytes(StandardCharsets.UTF_8));
        String back = new String(Base64.getDecoder().decode(token), StandardCharsets.UTF_8);
        System.out.println("Base64: " + token + "  ->  " + back);
        System.out.println("URL-safe: " + Base64.getUrlEncoder().withoutPadding().encodeToString(new byte[] {(byte) 0xfb, (byte) 0xff}));
    }
}
