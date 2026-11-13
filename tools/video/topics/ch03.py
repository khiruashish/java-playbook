"""Chapter 03 — The Toolchain. Source: docs/01-platform/03-toolchain.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 03 · The Toolchain"
SECTION = "Platform"

SLIDES = [
    dict(kind="title",
         title="The Toolchain",
         kicker="Platform · Chapter 03",
         body='<p class="sub">The JDK tools that answer questions in seconds: jshell, javap, jdeps, source launch, and the compiler flags that matter.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter three: the toolchain.",
             "Every JDK ships a set of tools most developers never touch, because Maven, Gradle and the IDE stand in front of them. But some questions only those tools can answer, and they answer them in seconds.",
         ]),

    dict(title="Questions the IDE can't answer",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("In production", "Which version of this dependency is **actually loaded** — and is it a multi-release JAR?", "fuchsia", 0)
              + card("In review", "What does a lambda **compile to**? You think it's not an anonymous class. Have you looked?", "amber", 1)
              + card("At your desk", "A one-line hypothesis about `Collectors.teeing`. A scratch project? A throwaway test?", "cyan", 2)
              + "</div>",
         narration=[
             "Three situations. A dependency behaves oddly in production, and you need to know which version is really loaded, and whether it's a multi-release JAR resolving differently on this JDK.",
             "A colleague asks what a lambda compiles to. You believe it isn't an anonymous class, but you've never actually looked.",
             "Or you want to test a one-line idea about Collectors dot teeing, and the options seem to be a scratch project or a test nobody will keep. Each of these has a JDK tool that answers it in seconds.",
         ]),

    dict(title="Five groups of tools",
         kicker="Mental model",
         body=table(["Group", "Tools", ""], [
                    ["Build", "`javac` · `jar` · `javadoc`", "You use these through Maven/Gradle"],
                    ["Run", "`java` · `jshell`", "Source launch and a REPL"],
                    ["**Inspect**", "`javap` · `jdeps` · `jdeprscan`", "**Worth learning deliberately**"],
                    ["**Diagnose**", "`jcmd` · `jfr`", "**The production entry points**"],
                    ["Package", "`jlink` · `jpackage`", "Minimal runtimes and installers"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">Build and run you already use. <b>Inspect and diagnose</b> answer questions nothing else can.</p>', 1),
         narration=[
             "The tools fall into five groups. Build tools like javac and jar. Run tools: java and jshell. Inspection: javap, jdeps and jdeprscan. Diagnostics: jcmd and jfr. And packaging: jlink and jpackage.",
             "Build and run, you already use through your build tool. Inspect and diagnose are the groups worth learning on purpose, because they answer questions nothing else can.",
         ]),

    dict(title="jshell — try it in seconds",
         kicker="Worked example",
         body=code('''
jshell> var lines = List.of("MILK-1L", "RICE-5KG", "ATTA-10KG")
jshell> lines.stream().collect(Collectors.teeing(
   ...>     Collectors.counting(), Collectors.joining(", "),
   ...>     (count, joined) -> count + ": " + joined))
$2 ==> "3: MILK-1L, RICE-5KG, ATTA-10KG"''', lang="text", title="jshell", size=24)
              + frag(table(["Command", "Does"], [
                    ["`/env --class-path app.jar`", "**Load your own classes**"],
                    ["`/vars` · `/methods` · `/list`", "What's defined"],
                    ["`/save` · `/open session.jsh`", "Save and replay"],
                ], cls="sm"), 1),
         narration=[
             "jshell is the REPL, since Java 9. Define a list, try teeing, and see the answer immediately, without a project or a test.",
             "The command that makes it a real tool is slash env with a class path. Load your application's JAR, and you can interrogate your actual classes, not toy examples.",
         ]),

    dict(title="javap — what did the compiler produce?",
         kicker="Worked example",
         body=code('''
Runnable r = () -> System.out.println("dispatch");''', title="LambdaExample.java", size=25)
              + code('''
$ javap -c -p LambdaExample
   0: invokedynamic #7, 0     // InvokeDynamic #0:run:()Ljava/lang/Runnable;
private static void lambda$main$0();   // the body, as a private static method''',
                     lang="text", title="No LambdaExample$1.class", step=1, size=23)
              + frag(code('''
Java 8 :  new StringBuilder … append, append, append, toString
Java 9+:  invokedynamic  makeConcatWithConstants''', lang="text", title="\"Order \" + id + \" total \" + total", size=23), 2),
         narration=[
             "javap disassembles a class. Take a one-line lambda.",
             "javap minus c minus p shows the truth. The body became a private static method, and the call site is an invokedynamic instruction, not a new. No inner class file is generated at all.",
             "It also settles arguments about string concatenation. Java 8 compiled it to a StringBuilder chain. Since Java 9 it's a single invokedynamic, built into an optimised strategy at runtime. So always use StringBuilder is outdated advice for simple expressions.",
         ]),

    dict(title="Source launch: scripts with types",
         kicker="java Script.java",
         body=code('''
void main() {
    var count = Files.readAllLines(Path.of("orders.csv")).size() - 1;
    IO.println("Rows: " + count);
}''', title="Reconcile.java — Java 25 compact source file", size=25)
              + code('''
java Reconcile.java                 # compiles in memory, runs, leaves nothing behind
java Reconcile.java Helper.java     # several files (22+)
#!/usr/bin/java --source 25         # or make it executable''', lang="bash", step=1, size=24),
         narration=[
             "Since Java 11, java can run a source file directly. With Java 25's compact source files, there's no class to declare. Just a main method, reading a CSV and printing a count.",
             "Run it with java Reconcile dot java. It compiles in memory, runs, and leaves no artifacts. Java 22 added multiple files, and a shebang line makes it an executable script. For operational scripts, that replaces a throwaway Maven module, with types.",
         ]),

    dict(title="jdeps — before any upgrade",
         kicker="Worked example",
         body=code('''
$ jdeps -jdkinternals orders.jar
   com.grocery.UnsafeCache -> sun.misc.Unsafe   JDK internal API (JDK removed internal API)
   sun.misc.Unsafe -> Use java.lang.invoke.VarHandle @since 9

$ jdeps --print-module-deps orders.jar
java.base,java.sql,java.net.http''', lang="text", title="Names the problem AND the replacement", size=23)
              + frag(code('''
jlink --add-modules $(jdeps --print-module-deps app.jar) \\
      --strip-debug --no-man-pages --output runtime        # 200 MB JDK → ~45 MB''',
                          lang="bash", title="A minimal runtime", size=23), 1),
         narration=[
             "jdeps is the cheapest first step of any migration. Minus jdkinternals lists every internal API your JAR touches, and names the supported replacement. Print module deps tells you which JDK modules the application actually needs.",
             "Feed that list to jlink, and you get a runtime containing only those modules. A two-hundred-megabyte JDK typically becomes about forty-five.",
         ]),

    dict(title="Compiler flags that matter",
         kicker="javac",
         body=table(["Flag", "Why"], [
                    ["`-parameters`", "Keep parameter names — or JSON, DI and binding see **arg0**"],
                    ["`-Xlint:removal,unchecked`", "Highest ratio of real findings to noise"],
                    ["`-proc:full` / explicit processor path", "Implicit annotation processing is **going away**"],
                    ["`@jvm.args`", "Options in a reviewable, diffable file"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">Flag ignored? Check <code>_JAVA_OPTIONS</code> — it silently <b>overrides the command line</b>. '
                     'Use <code>JAVA_TOOL_OPTIONS</code> instead.</p>', 4),
         narration=[
             "Four compiler and launcher settings matter. Minus parameters keeps parameter names in the bytecode. Without it, JSON binding, dependency injection and validation see arg zero, arg one.",
             "Enable lint for removal and unchecked at minimum. Those two categories have the best ratio of real findings to noise.",
             "Declare annotation processor paths explicitly. Java 21 warns about implicit processing, and later releases turn it off, so Lombok and MapStruct builds suddenly stop generating code.",
             "And put JVM options in an argument file, so they're reviewable in version control.",
             "One last trap. If a flag seems ignored, check underscore JAVA OPTIONS. It silently overrides the command line. Use JAVA TOOL OPTIONS instead, which appears in the startup log.",
         ]),

    dict(title="Multi-release JARs",
         kicker="Internals",
         body=code('''
orders.jar
├── com/grocery/Cache.class              ← baseline
└── META-INF/versions/
    ├── 11/com/grocery/Cache.class       ← used on 11+
    └── 21/com/grocery/Cache.class       ← used on 21+''', lang="text", size=26)
              + frag('<p class="callout">The class you\'re debugging may <b>not</b> be the one you decompiled. '
                     '<code>jar tf</code> first, then <code>javap</code> the right entry.</p>', 1),
         narration=[
             "Multi-release JARs let a library ship different versions of a class for different JDKs. The JVM picks the highest versioned directory that doesn't exceed the running release.",
             "The consequence for debugging: the class you're looking at may not be the one that runs. List the JAR with jar t f first, then disassemble the right versioned entry.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Learn `javap -c -p`",
                         "`jdeps -jdkinternals` before upgrades",
                         "`-parameters` in every build",
                         "Explicit annotation processor paths",
                         "`@argfile` for JVM options",
                         "`java Script.java` for ops scripts"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Assume the IDE compiles like the build",
                         "Rely on implicit annotation processing",
                         "Set `_JAVA_OPTIONS`",
                         "Debug a JAR without checking `META-INF/versions`",
                         "Ship with `-g:none`"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Learn javap. Run jdeps minus jdkinternals before every major upgrade. Enable minus parameters in every build. Declare annotation processor paths explicitly. Keep JVM options in an argument file. And use source launch for operational scripts.",
             "Never assume the IDE compiles the same way as the build. Never rely on implicit annotation processing. Never set underscore JAVA OPTIONS. Never debug a JAR without checking its versioned entries. And never ship without debug info, or you lose line numbers in every stack trace.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 03 · The Toolchain",
         body=bullets(["`jshell` + `/env` to interrogate real classes",
                       "`javap -c -p` settles \"what does this compile to\"",
                       "`jdeps` → work list; `jlink` → small runtime",
                       "`-parameters`, lint, explicit processors",
                       "Next: **Ch 04 · Builds, Release Flags &amp; Preview**"], cls="bullets recap"),
         narration=[
             "To recap. jshell with your own classpath for quick experiments. javap to see what the compiler really produced. jdeps for an upgrade work list, and jlink for a small runtime. And in the build: parameters, lint, and explicit annotation processors.",
             "Next is chapter four: builds, release flags and preview features. Thanks for watching.",
         ]),
]
