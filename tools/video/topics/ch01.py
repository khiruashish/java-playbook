"""Chapter 01 — The JDK Landscape (8 → 26). Source: docs/01-platform/01-jdk-landscape.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 01 · The JDK Landscape"
SECTION = "Platform"

SLIDES = [
    dict(kind="title",
         title="The JDK Landscape",
         kicker="Platform · Chapter 01 · Java 8 → 26",
         body='<p class="sub">The release model, what LTS really means, which distribution to use, '
              'and how to target an older JDK without surprises.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter one: the JDK landscape, from Java 8 to Java 26.",
             "Which Java should we use has become a genuinely hard question. There are feature releases every six months, long-term-support releases every two years, "
             "a dozen vendor builds of the same source, and a licensing history confusing enough that many teams stayed on Java 8 for a decade rather than work it out.",
         ]),

    dict(title="Three symptoms of one confusion",
         kicker="The problem",
         body='<div class="grid4" style="grid-template-columns:repeat(2,1fr)">'
              + card("Version paralysis", "A team on Java 8 in 2026 is **twelve years behind**: no virtual threads, records, or pattern matching.", "fuchsia", 0)
              + card("Licence fear", "Oracle changed its terms **twice**. Teams read one announcement and concluded \"Java costs money now\".", "amber", 0)
              + "</div>"
              + code('''
java.lang.UnsupportedClassVersionError: com/grocery/OrderService
  has been compiled by a more recent version of the Java Runtime
  (class file version 65.0), this version of the Java Runtime only
  recognizes class file versions up to 61.0''', lang="text", title="Built on 21, deployed onto 17", step=1, size=23),
         narration=[
             "Three symptoms of the same confusion. Version paralysis: a team still on Java 8 in 2026 is twelve years behind, missing virtual threads, records, pattern matching and a decade of GC work. "
             "And licence fear: Oracle changed its terms twice, and teams who read one announcement but not the next concluded that Java costs money now. For most builds, that's false.",
             "The third symptom arrives in production. UnsupportedClassVersionError. The service was built on Java 21 and deployed onto Java 17. The build passed, the tests passed, and the failure showed up at startup, in the environment that mattered.",
         ]),

    dict(title="The release train",
         kicker="Mental model",
         body=flow(["Java 8 · 2014", "11 LTS · 2018", "17 LTS · 2021", "**21 LTS** · 2023", "**25 LTS** · 2025", "26 · 2026"])
              + frag('<p class="callout">A feature release every <b>March and September</b>, with whatever is ready. '
                     'LTS every <b>two years</b> since 17.</p>', 1)
              + frag('<p class="callout">LTS is a <b>vendor</b> commitment, not a JDK feature — no code path checks whether a release is LTS.</p>', 2),
         narration=[
             "Since Java 9, the JDK ships on a release train.",
             "A feature release leaves every March and September, with whatever is ready. Features that aren't ready wait for the next train. Long-term-support releases come every two years since Java 17, which is why 21 and 25 are only two years apart.",
             "And here's the subtle part. LTS is a vendor concept, not a JDK one. OpenJDK produces a release, and vendors choose which ones to support for years with backported fixes. "
             "The industry coordinates on the same ones, so LTS is real in practice. But no part of the JDK behaves differently because a release is called LTS.",
         ]),

    dict(title="One source, many builds",
         kicker="Distributions",
         body=table(["Distribution", "Licence", "Choose it when"], [
                    ["**Eclipse Temurin**", "GPLv2+CPE", "No constraints — the community default"],
                    ["Amazon Corretto", "GPLv2+CPE", "Running on AWS"],
                    ["Microsoft Build", "GPLv2+CPE", "Running on Azure"],
                    ["Azul Zulu", "GPLv2+CPE", "You need very old versions"],
                    ["GraalVM", "Mixed", "Native images"],
                    ["Oracle JDK", "NFTC", "You already pay Oracle — **read the terms**"],
                ], step_per_row=None, cls="sm")
              + frag('<p class="callout">Same OpenJDK source, same language, same library. Choose on <b>support and licence</b>, not capability. '
                     'For most teams: <b>Temurin, and stop thinking about it.</b></p>', 1),
         narration=[
             "Every mainstream JDK is built from the same OpenJDK source. Temurin, Corretto, Microsoft's build, Zulu, Red Hat's, Oracle's. "
             "They differ in support duration, licence and platform coverage, not in the language or the standard library. A correct program behaves identically on all of them.",
             "So choose on support and licensing, not on capability. Corretto if you're on AWS, Microsoft's build on Azure. And for most teams, the honest answer is Temurin, and stop thinking about it.",
         ]),

    dict(title="Is Java free?",
         kicker="The licensing summary",
         body=table(["Period", "Situation"], [
                    ["Before 2019", "Oracle JDK free for general use"],
                    ["2019 · Java 11", "Oracle JDK needs a **paid subscription** in production"],
                    ["2021 · Java 17", "Oracle JDK free again under **NFTC**, with conditions"],
                    ["Always", "**OpenJDK builds free** under GPLv2 + Classpath Exception"],
                ], step_per_row=0, cls="pairs")
              + frag('<p class="callout">The <b>Classpath Exception</b> lets proprietary code link against the JDK without becoming GPL. '
                     'Free — including in production, including commercially.</p>', 4),
         narration=[
             "Here's the licensing history. Before 2019, Oracle's JDK was free for general use.",
             "In 2019, with Java 11, Oracle's own build started to need a paid subscription for production. That's the change that caused the alarm.",
             "In 2021, with Java 17, Oracle's build became free again under its no-fee terms, with conditions. That reversal got far less attention, which is why the belief persists.",
             "And throughout, every OpenJDK build has been free under GPL version two with the Classpath Exception.",
             "The Classpath Exception is the clause that lets your proprietary code link against the JDK without becoming GPL. So it's free, including in production and commercially. "
             "Oracle's own build is the only one where you need to read the current terms.",
         ]),

    dict(title="Class file versions",
         kicker="Why UnsupportedClassVersionError happens",
         body='<div class="grid2 start">'
              + table(["Java", "Major"], [["8", "52"], ["11", "55"], ["17", "61"], ["21", "**65**"], ["25", "**69**"], ["26", "70"]], cls="sm")
              + frag(code('''
Runtime.Version v = Runtime.version();
int feature = v.feature();      // 25

// not this — breaks on the 1.8 → 9 format change
System.getProperty("java.version");''', title="RuntimeVersion.java", size=23), 1)
              + "</div>"
              + frag('<p class="callout">Major version = Java version <b>+ 44</b>. A JVM refuses any class file newer than it knows.</p>', 0),
         narration=[
             "Every class file records a major version, and the rule is simple: Java version plus forty-four. Fifty-two for Java 8, sixty-five for 21, sixty-nine for 25. "
             "A JVM refuses any class file with a higher major version than it supports. That's exactly the sixty-five versus sixty-one in our production error.",
             "To check the version at runtime, use Runtime dot version, and ask for the feature number. Don't parse the java dot version property by hand. It changed format from one point eight to nine, and old build scripts still break on it.",
         ]),

    dict(title="--release, never -source / -target",
         kicker="Targeting an older JDK",
         body=code('''
// javac -source 8 -target 8   (running on JDK 21)
List<String> list = someList.stream().toList();   // compiles!
// On a Java 8 JVM: NoSuchMethodError — Stream.toList() didn't exist''', title="WhySourceTargetIsWrong.java", size=25)
              + frag(flow(["`--release 8`", "language level 8 + bytecode 52", "**and** the Java 8 API from `lib/ct.sym`", "newer methods rejected at **compile** time"]), 1)
              + frag(code('<maven.compiler.release>25</maven.compiler.release>', lang="xml", title="pom.xml", size=25), 2),
         narration=[
             "Targeting an older JDK has a classic trap. Minus source eight, minus target eight sets the language level and the bytecode version, but still compiles against the current JDK's library. "
             "So Stream dot toList compiles happily, then fails on Java 8 with NoSuchMethodError.",
             "The release flag fixes this. The JDK ships the historical API signatures of each release in a file called ct dot sym, and the compiler checks against those. The same mistake becomes a compile error.",
             "In Maven, that's the compiler release property. There's no reason to use the older flags.",
         ]),

    dict(title="Pin the JDK in the build",
         kicker="Worked example",
         body=code('''
java {
    toolchain { languageVersion = JavaLanguageVersion.of(25) }   // Gradle downloads it
}''', lang="groovy", title="build.gradle", size=25)
              + code('''
FROM eclipse-temurin:25.0.2_9-jre-alpine      # not temurin:25-jre — that tag moves''',
                     lang="dockerfile", title="Dockerfile", step=1, size=25)
              + code('''
sdk install java 25.0.2-tem
sdk use java 21.0.5-tem        # this shell only
java -version && mvn -version  # check BEFORE debugging anything version-shaped''',
                     lang="bash", title="Two JDKs locally with SDKMAN!", step=2, size=25),
         narration=[
             "Declare the JDK instead of inheriting it from the machine. Gradle toolchains are the strongest option: Gradle downloads the specified JDK, so laptops and CI build with exactly the same one.",
             "In container images, pin the patch version. A floating tag like temurin twenty-five j-r-e resolves to whatever is current when the image is pulled, so the JDK can change between a passing CI run and a production deploy.",
             "Locally, SDKMAN installs and switches JDKs per shell. And form one habit: run java minus version and mvn minus version before debugging anything version-shaped. Maven often runs on a JDK you didn't expect.",
         ]),

    dict(title="Which version should you be on?",
         kicker="Choosing a version",
         body=table(["Today", "Go to"], [
                    ["New service", "**Java 25 LTS**"],
                    ["Java 8", "**17 first**, then 21 or 25"],
                    ["Java 11", "21 — frameworks require 17+"],
                    ["Java 17", "25 — low friction"],
                    ["Java 21", "25 when convenient"],
                ], step_per_row=None, cls="pairs")
              + frag('<p class="callout">Never <b>8 → 25</b> in one jump: module encapsulation, removed Java EE modules and a decade of library upgrades become one change nobody can bisect.</p>', 1)
              + frag('<p class="callout">Run the latest <b>non-LTS release in CI</b> — it surfaces removals a year or two early.</p>', 2),
         narration=[
             "Which version should you be on? New services start on Java 25. From 11, go to 21, and from 17, go straight to 25.",
             "Java 8 deserves two steps. Land on 17 first. Going eight to twenty-five in one jump combines the module system's encapsulation, the removed Java EE modules, and a decade of library upgrades into one change nobody can bisect.",
             "And run the latest non-LTS release in CI, even if production stays on LTS. It surfaces deprecations and removals early, so the next LTS upgrade becomes a confirmation rather than an investigation.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Java 25 LTS for new work",
                         "`--release`, always",
                         "A GPLv2+CPE build — Temurin by default",
                         "Pin the exact patch version",
                         "Toolchains declare the build JDK",
                         "Non-LTS in CI"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["`-source` / `-target`",
                         "Non-LTS in production without auto-upgrades",
                         "Floating image tags",
                         "Assume Oracle JDK = OpenJDK licence",
                         "Jump 8 → 25 in one step"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Default to Java 25 for new work. Always use the release flag. Use a GPL with Classpath Exception build, Temurin unless something points elsewhere. Pin the exact patch version. Let toolchains declare the build JDK. And run the latest non-LTS release in CI.",
             "Never use minus source and minus target. Never run a non-LTS release in production without an automated six-month upgrade path. Never use floating image tags. Never assume Oracle's JDK has the OpenJDK licence. And never jump from 8 to 25 in one step.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 01 · The JDK Landscape",
         body=bullets(["Feature release every 6 months; **LTS every 2 years**",
                       "One OpenJDK source — choose a build on **support**",
                       "GPLv2 + Classpath Exception = **free**",
                       "Class file major = Java + 44; use `--release`",
                       "Next: **Ch 02 · The JVM Runtime Model**"], cls="bullets recap"),
         narration=[
             "To recap. A feature release every six months, and an LTS every two years. Every mainstream JDK comes from the same source, so choose on support, and Temurin is the default. "
             "GPL with the Classpath Exception means free, commercially too. And class file major version is Java plus forty-four, so always compile with the release flag.",
             "Next is chapter two: the JVM runtime model. Thanks for watching.",
         ]),
]
