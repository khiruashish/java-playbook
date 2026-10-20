import java.nio.file.*;
import java.util.List;

/** Java 11: Files.writeString and Files.readString — one line each. */
public class J11_Files {

    public static void main(String[] args) throws Exception {
        Path file = Files.createTempFile("orders", ".csv");
        Files.writeString(file, "O1,MILK,2\nO2,RICE,1\n");                 // UTF-8 by default
        String content = Files.readString(file);
        System.out.print(content);

        List<String> lines = Files.readAllLines(file);
        System.out.println(lines.size() + " lines, first order: " + lines.get(0).split(",")[0]);
        Files.delete(file);
    }
}
