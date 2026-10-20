import java.nio.charset.Charset;

/** Java 18: UTF-8 is the default charset everywhere, instead of depending on the operating system. */
public class J18_Utf8Default {

    public static void main(String[] args) {
        System.out.println("default charset: " + Charset.defaultCharset());
        System.out.println("file.encoding:   " + System.getProperty("file.encoding"));
        System.out.println("so new FileReader(file) and String.getBytes() now mean UTF-8 on every platform.");
        System.out.println("Also in Java 18: a built-in static file server —  jwebserver -p 8000");
    }
}
