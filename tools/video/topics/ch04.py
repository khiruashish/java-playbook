"""Chapter 04 — Builds, Release Flags & Preview Features. Source: docs/01-platform/04-builds-and-preview-features.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 04 · Builds, Release Flags & Preview Features"
SECTION = "Platform"

SLIDES = [
    dict(kind="title",
         title="Builds, Release Flags &amp; Preview Features",
         kicker="Platform · Chapter 04",
         body='<p class="sub">Declaring the JDK, resolving dependency conflicts, reproducible builds, and using preview features without getting trapped.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter four: builds, release flags and preview features.",
             "A surprising share of Java production failures aren't code at all. They're build configuration: something left undeclared and inherited from whatever machine happened to run the build.",
         ]),

    dict(title="Three failures that are all build config",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(3,1fr)">'
              + card("Works on my machine", "Laptop on 25, CI on 21. Or both pass and **production** fails — nothing declared a target.", "fuchsia", 0)
              + card("NoSuchMethodError", "Two libraries want `vendor-client` 1.0 and 1.2. One won **silently** — not the one you compiled against.", "amber", 1)
              + card("Preview escapes", "`class file version 69.65535` — compiled with `--enable-preview`, run without it.", "cyan", 2)
              + "</div>",
         narration=[
             "Three failures. Works on my machine: a developer builds on Java 25 and CI fails on 21. Or worse, both pass and production fails, because nothing declared a target.",
             "A NoSuchMethodError at runtime. Two libraries depend on the same vendor client at different versions. One of them won, silently, and it wasn't the one your code was compiled against.",
             "And a preview feature that escapes. Compiled with enable preview, then deployed onto a runtime without the flag, or onto a different JDK where it will never load.",
         ]),

    dict(title="Three separate version decisions",
         kicker="Mental model",
         body=table(["Question", "Declare it with"], [
                    ["Which JDK **runs the build**?", "A **toolchain** — declared, not inherited"],
                    ["Which Java do we **target**?", "`--release` — language, bytecode **and** API"],
                    ["Which JDK runs in **production**?", "The image, **pinned** to a patch version"],
                ], step_per_row=0, cls="pairs")
              + frag(code('''
java {
    toolchain { languageVersion = JavaLanguageVersion.of(25); vendor = JvmVendorSpec.ADOPTIUM }
}                                                  // Gradle downloads it if absent''',
                          lang="groovy", title="build.gradle", size=23), 3),
         narration=[
             "There are three separate version decisions, and they're often confused. First, which JDK runs the build. Declare it with a toolchain, rather than inheriting whatever the machine has.",
             "Second, which Java version you target. That's the release flag, covering language, bytecode, and the API.",
             "And third, which JDK runs in production: the container image, pinned to a patch version. You can build on 25, target 21, and deploy onto 21. What breaks things is leaving any of the three undeclared.",
             "Gradle's toolchain is the strongest form: it downloads the declared JDK if it's missing, so a fresh machine produces the same result. Maven toolchains need the JDK already installed and registered.",
         ]),

    dict(title="Nearest wins vs highest wins",
         kicker="Dependency resolution",
         body=code('''
app
├── vendor-client 1.0          ← depth 1
└── dispatch-sdk 2.3
    └── vendor-client 1.2      ← depth 2''', lang="text", size=26)
              + '<div class="grid2">'
              + card("Maven: 1.0", "**Nearest** to the root wins. Ties go to **declaration order** — reorder two deps and the winner changes.", "fuchsia", 1)
              + card("Gradle: 1.2", "**Highest** version requested wins. Can pull in a newer version with a breaking change.", "indigo", 1)
              + "</div>",
         narration=[
             "Here's the conflict. The app depends on vendor client 1.0 directly, and on dispatch SDK, which needs 1.2.",
             "Maven picks the version nearest the root, so 1.0 wins, and ties at the same depth go to declaration order in the POM. Gradle picks the highest version anyone asked for, so 1.2 wins. "
             "Neither considers compatibility. The same graph can resolve differently in each tool, and the failure is a NoSuchMethodError at runtime, not a build error.",
         ]),

    dict(title="Diagnose, then state the version",
         kicker="Worked example",
         body=code('''
$ mvn dependency:tree -Dincludes=com.vendor:vendor-client
+- com.vendor:vendor-client:jar:1.0:compile
\\- com.partner:dispatch-sdk:jar:2.3:compile
   \\- (com.vendor:vendor-client:jar:1.2:compile - omitted for conflict with 1.0)''',
                   lang="text", title="./gradlew dependencyInsight --dependency vendor-client", size=22)
              + code('''
dependencies {
    constraints {
        implementation('com.vendor:vendor-client:1.2') {
            because 'dispatch-sdk 2.3 requires 1.2'
        }
    }
}''', lang="groovy", title="Gradle constraints · Maven: <dependencyManagement>", step=1, size=23),
         narration=[
             "To diagnose, ask the tool. Maven's dependency tree with an includes filter shows that 1.2 was omitted for conflict with 1.0. Gradle's dependency insight shows the same from its side.",
             "Then state the version explicitly. Gradle constraints, or Maven's dependency management, set the version without adding a dependency, and the because clause records why. "
             "Adding a direct dependency to fix a conflict works by accident, and hides the reason.",
         ]),

    dict(title="BOMs and reproducible builds",
         kicker="Worked example",
         body=code('''
testImplementation platform('org.junit:junit-bom:5.11.4')
testImplementation 'org.junit.jupiter:junit-jupiter'        // no version — the BOM decides''',
                   lang="groovy", title="Import a BOM", size=24)
              + frag(table(["Reproducible needs", ""], [
                    ["Pinned plugin versions", "`requirePluginVersions`"],
                    ["No ranges, no `SNAPSHOT`s", "`requireReleaseDeps`"],
                    ["A fixed output timestamp", "`project.build.outputTimestamp`"],
                    ["The wrapper", "`./mvnw` · `./gradlew` — never bare `mvn`"],
                ], cls="sm"), 1),
         narration=[
             "A BOM declares a set of versions that work together. Import it, then omit the versions on individual artifacts. That's what prevents mixing JUnit's API from one release with its engine from another.",
             "And a reproducible build needs four things. Pinned plugin versions. No version ranges or snapshots, because then the artifact depends on when you built it. A fixed output timestamp for the JAR entries. "
             "And the wrapper, so everyone, including CI, uses the same build tool version. The Maven enforcer plugin can check the first two mechanically.",
         ]),

    dict(title="Preview: the flag goes in three places",
         kicker="Core reference",
         body=code('''
<plugin><artifactId>maven-compiler-plugin</artifactId>
  <configuration><release>25</release>
    <compilerArgs><arg>--enable-preview</arg></compilerArgs></configuration></plugin>
<plugin><artifactId>maven-surefire-plugin</artifactId>
  <configuration><argLine>--enable-preview</argLine></configuration></plugin>   <!-- forgotten -->''',
                   lang="xml", title="1 · compile   2 · tests", size=22)
              + code('java --enable-preview -jar orders.jar', lang="bash", title="3 · runtime", step=1, size=24)
              + frag('<p class="callout">Keep preview behind a <b>build profile</b>, so it can be removed in one commit.</p>', 2),
         narration=[
             "Using a preview feature needs the flag in three places. The compiler, and the test runner. Forgetting surefire is the usual mistake: compilation succeeds, and every single test fails with preview features not enabled.",
             "And third, at runtime.",
             "Put all of it behind a Maven profile. Then removing preview is one commit, and a normal build proves the code still compiles without it.",
         ]),

    dict(title="Preview class files are bound to one release",
         kicker="Internals",
         body=flow(["`javac --release 25 --enable-preview`", "major **69**, minor **65535**", "loads **only** on 25, **only** with the flag"])
              + frag(table(["Artifact", "Preview acceptable?"], [
                    ["Published library", "**Never**"],
                    ["Internal shared library", "No"],
                    ["Deployed service", "Only with a pinned runtime and an exit plan"],
                    ["Scripts, spikes, tooling", "Yes"],
                ], cls="pairs"), 1),
         narration=[
             "Here's the constraint that decides whether you can use preview at all. A preview class file carries minor version sixty-five five three five, and refuses to load on any JDK other than the exact release that produced it. Not twenty-five or later. Twenty-five. "
             "That's deliberate: it's what lets the JDK redesign a preview API between releases.",
             "So never publish a library with preview, and not an internal shared library either. A deployed service only with a pinned runtime and a plan to remove it. Scripts and spikes are fine, because rewriting them is cheap.",
         ]),

    dict(title="CI across JDK versions",
         kicker="Worked example",
         body=code('''
strategy:
  matrix:
    java: [21, 25, 26]          # LTS in production, plus the latest release
steps:
  - uses: actions/setup-java@v4
    with: { distribution: temurin, java-version: ${{ matrix.java }} }
  - run: ./mvnw --batch-mode verify''', lang="yaml", title=".github/workflows/build.yml", size=24)
              + frag('<p class="callout">The non-LTS job is the cheapest early warning there is. Let it fail <b>without blocking</b> — and read it.</p>', 1),
         narration=[
             "Build in CI across a matrix of JDKs: the LTS you run in production, plus the latest release.",
             "The latest release surfaces deprecations, removals and behaviour changes months or years before an LTS upgrade forces them. Let that job fail without blocking merges, but read it.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Toolchain for the build JDK; `--release` to target",
                         "Commit and use the wrapper",
                         "Pin every plugin; import BOMs",
                         "Fix conflicts with constraints + `because`",
                         "`-parameters`, UTF-8, in a shared parent",
                         "Preview behind a profile"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["Version ranges or `SNAPSHOT`s in releases",
                         "Publish a library built with preview",
                         "Forget surefire when enabling preview",
                         "Fix a conflict with a direct dependency",
                         "Compiler settings only the IDE knows"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Declare the build JDK with a toolchain, and target with the release flag. Commit the wrapper and use it everywhere. Pin plugins and import BOMs. Fix conflicts with constraints, saying why. Set parameters and UTF-8 in a shared parent. And keep preview behind a profile.",
             "Never use version ranges or snapshots in anything released. Never publish a library compiled with preview. Never forget the test configuration. Never fix a conflict by adding a direct dependency. And never let the IDE hold compiler settings the build doesn't.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 04 · Builds &amp; Preview",
         body=bullets(["Build JDK, target, and runtime are **three** decisions",
                       "Maven: nearest wins · Gradle: highest wins",
                       "State versions with BOMs and constraints",
                       "Preview binds a class file to **one** release",
                       "Next: **Ch 05 · Migration Strategy 8 → 25**"], cls="bullets recap"),
         narration=[
             "To recap. The build JDK, the target version and the production runtime are three separate decisions. Declare all three. Maven picks the nearest version and Gradle the highest, so state versions explicitly with BOMs and constraints. "
             "And a preview class file only loads on the one release that built it.",
             "Next is chapter five: migration strategy, from Java 8 to 25. Thanks for watching.",
         ]),
]
