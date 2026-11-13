"""Chapter 05 — Migration Strategy 8 → 25. Source: docs/01-platform/05-migration-strategy.md"""
from kit import code, frag, bullets, table, card, flow

CHAPTER = "Ch 05 · Migration Strategy 8 → 25"
SECTION = "Platform"

SLIDES = [
    dict(kind="title",
         title="Migration Strategy 8 → 25",
         kicker="Platform · Chapter 05",
         body='<p class="sub">Assess first, upgrade dependencies first, step through 17, and keep rollback a runtime change.</p>',
         narration=[
             "Welcome to the Modern Java Enterprise Handbook. This is chapter five: migration strategy, from Java 8 to 25.",
             "Upgrading the JDK is rarely hard because of any one change. It's hard because teams treat it as one change, when it's several different kinds of breakage stacked on top of each other.",
         ]),

    dict(title="The stall and the big bang",
         kicker="The problem",
         body='<div class="grid2">'
              + card("The stall", "On Java 8 since 2016. The estimate is \"a quarter, maybe\" and it loses to features **every year**. Dependencies freeze; CVEs pile up.", "amber", 0)
              + card("The big bang", "8 → 21 in one branch. Three weeks, **400 files**, and failures nobody can attribute to the JDK, a framework, or a removed API.", "fuchsia", 1)
              + "</div>"
              + frag('<p class="callout">Same mistake both ways: treating the upgrade as <b>one</b> change.</p>', 2),
         narration=[
             "Two failure patterns. The stall: a team has been on Java 8 since 2016. Every year someone proposes upgrading, the estimate is a quarter, maybe, and it loses to feature work. Meanwhile libraries raise their baselines, nothing can be updated, and vulnerabilities accumulate.",
             "And the big bang: a team goes from 8 to 21 in one branch. Three weeks in, there are four hundred changed files and failing tests nobody can attribute. Was it the JDK, a framework upgrade, a removed API, or a changed default?",
             "Both come from the same mistake: treating the upgrade as one change.",
         ]),

    dict(title="Three kinds of breakage",
         kicker="Mental model",
         body=table(["Kind", "Example", "When you find out"], [
                    ["**Removed**", "`javax.xml.bind` gone in 11", "Compile or startup — loud"],
                    ["**Encapsulated**", "`Unsafe` reflection blocked in 17", "Runtime, on that code path"],
                    ["**Changed default**", "CLDR locale data; G1 GC", "**When a customer notices**"],
                ], step_per_row=0, cls="sm")
              + frag('<p class="callout">The work is <b>~90% dependencies</b>. The estimate depends on how many major versions behind you are, not on codebase size.</p>', 3),
         narration=[
             "There are three kinds of breakage. Removed APIs, like JAXB in Java 11. Those fail at compile time or startup, so they're loud.",
             "Encapsulated internals, like reflection into Unsafe, blocked in 17. Those fail at runtime, but only on the code path that uses them.",
             "And changed defaults: locale data, the default garbage collector. Those are silent. You find out when a customer notices. That's why a migration needs testing, not just compiling.",
             "And most of the work is in dependencies, not your code. Your code rarely touches internals. Your old bytecode library, XML stack and mocking framework do. So the estimate depends on how far behind your dependencies are, not on how big the codebase is.",
         ]),

    dict(title="Assess before you estimate",
         kicker="One day, before committing",
         body=code('''
jdeps -jdkinternals --multi-release 17 -cp "lib/*" app.jar   > internals.txt
jdeprscan --release 17 --class-path "lib/*" app.jar          > deprecated.txt
mvn versions:display-dependency-updates                       > updates.txt
java -jar app.jar                                             # on JDK 17, unchanged''',
                   lang="bash", title="The assessment pass", size=23)
              + frag(code('''
app.jar -> JDK removed internal API
   com.grocery.FastCache -> sun.misc.Unsafe       ← your code: a handful
lib/asm-5.0.3.jar -> JDK internal API              ← dependencies: most of it
   sun.misc.Unsafe -> java.lang.invoke.VarHandle @since 9''', lang="text", title="internals.txt", size=23), 1),
         narration=[
             "Before estimating anything, spend a day on an assessment. jdeps lists internal API use across the whole dependency set. jdeprscan lists deprecated API use. The versions plugin shows how far behind each dependency is. And try starting the app on JDK 17 without changing anything.",
             "The output splits cleanly into your code, usually a handful of places, and dependencies, usually most of it, fixed by upgrading. That split is the estimate.",
         ]),

    dict(title="Step one: 8 → 17",
         kicker="Each as its own PR",
         body=table(["", "Step"], [
                    ["1", "**Upgrade dependencies while still on 8**"],
                    ["2", "Add back removed Java EE modules — `jakarta.xml.bind`, `jaxb-runtime`"],
                    ["3", "Switch the build to `--release 17`; fix compile errors"],
                    ["4", "Start it; triage every `InaccessibleObjectException`"],
                    ["5", "**Verify behaviour changes** — the step teams skip"],
                    ["6", "Ship 17 to production"],
                ], step_per_row=0, cls="pairs"),
         narration=[
             "The first step, from 8 to 17, in order, each as its own PR. First, upgrade dependencies while you're still on Java 8. Most libraries that support 17 still support 8, so this removes most of the risk without touching the JDK.",
             "Second, add the removed Java EE modules back as ordinary dependencies. That's the fix for NoClassDefFoundError on javax dot xml dot bind.",
             "Third, switch the build to release 17 and fix the compile errors. There are usually few.",
             "Fourth, start the application and collect the reflection failures. For each one, find the library, and look for a version that doesn't need it.",
             "Fifth, verify the behaviour changes. This is the step teams skip.",
             "And sixth, ship Java 17 to production before starting the next step.",
         ]),

    dict(title="Escape hatches are tickets, not config",
         kicker="--add-opens",
         body=code('''
InaccessibleObjectException: Unable to make field private final java.util.ArrayList.elementData
accessible: module java.base does not "opens java.util" to unnamed module''', lang="text", size=22)
              + code('''
# hibernate 5.4 reflects into java.util — remove after upgrading to 6.x
--add-opens java.base/java.util=ALL-UNNAMED''', lang="text", title="jvm.args", step=1, size=24)
              + frag('<p class="callout">Opens the <b>whole package</b> to all classpath code. Each flag is a dependency that needs upgrading — '
                     'give it an owner and a target version.</p>', 2),
         narration=[
             "Here's the typical reflection failure. A library is reaching into a private field of ArrayList, and java dot base won't open java dot util to it.",
             "When no fixed version exists yet, add the flag. But put it in an argument file, with a comment naming the library and the version that removes it.",
             "Add opens works per package, not per class, so it opens all of java dot util to all classpath code. Treat each one as a ticket with an owner and an upgrade target, not as configuration.",
         ]),

    dict(title="The silent changes",
         kicker="Verify, don't assume",
         body=code('''
DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM).withLocale(Locale.UK)
                 .format(LocalDate.of(2026, 9, 20));
// Java 8:  20-Sep-2026
// Java 9+: 20 Sep 2026          ← nothing fails; a downstream parser breaks weeks later''',
                   title="LocaleChange.java", size=23)
              + frag(table(["Change", "Check"], [
                    ["Default GC Parallel → **G1** (9)", "Batch throughput may drop — nobody changed a flag"],
                    ["CMS removed (14)", "`-XX:+UseConcMarkSweepGC` won't start"],
                    ["Nashorn removed (15)", "Any scripted rules engine"],
                    ["TLS defaults", "Old protocols off — check integrations"],
                ], cls="sm"), 1),
         narration=[
             "Java 9 switched the default locale data to CLDR. The same UK medium date that printed twenty dash Sep dash 2026 now prints twenty Sep 2026. Nothing fails. A downstream parser breaks weeks later. If a JDK-formatted date crosses a system boundary, assert on it in a test.",
             "Others: the default collector moved from Parallel to G1, which is better for latency but can cost a batch job throughput, without anyone changing a flag. CMS was removed, so old flags stop startup. Nashorn is gone. And old TLS versions are disabled.",
         ]),

    dict(title="17 → 21 → 25: the easy steps",
         kicker="Mostly additive",
         body='<div class="grid2 start">'
              + table(["17 → 21", ""], [
                    ["`jdeprscan --release 21`", "Deprecations"],
                    ["`Thread.stop`", "Now throws"],
                    ["Virtual threads", "`synchronized` still pins on 21"],
                ], cls="sm")
              + frag(table(["21 → 25", ""], [
                    ["Compact object headers", "Re-baseline heap sizing"],
                    ["`--add-opens` inventory", "Many no longer needed"],
                    ["Pinning workarounds", "Remove — fixed in 24"],
                ], cls="sm"), 1)
              + "</div>"
              + frag('<p class="callout">A JDK upgrade PR changes the JDK and <b>nothing else</b>. Adopt records and virtual threads afterwards.</p>', 2),
         narration=[
             "After 17, the steps are easy. For 21: check deprecations, Thread dot stop now throws, and remember that synchronized still pins virtual threads on 21.",
             "For 25: compact object headers make objects smaller, so re-baseline heap sizing. Recheck your add-opens list, because many libraries no longer need theirs. And remove any workarounds for pinning, which Java 24 fixed.",
             "And resist adopting new features in the upgrade PR. A JDK upgrade should change the JDK and nothing else, or you lose the ability to attribute a regression.",
         ]),

    dict(title="Keep rollback a runtime change",
         kicker="Rollout",
         body=flow(["CI matrix", "Staging", "Canary · hours", "25% · a day", "Full"])
              + frag(code('''
1. Move the runtime to 21, keep --release 17     ← rollback = swap the JDK
2. Run in production for a release cycle
3. Raise --release to 21                          ← now committed''', lang="text", size=24), 1)
              + frag('<p class="callout">On canary watch <b>GC pauses, off-heap footprint, p99</b>, and anything that formats dates or money.</p>', 2),
         narration=[
             "Roll out in stages: a CI matrix on both JDKs, staging, a canary for a few hours, a quarter of traffic for a day, then everything.",
             "Here's the property that makes it safe. Compiled with release 17, the same artifact runs on 17 and on 21, so rollback is just swapping the runtime. Raising the release flag is the one-way door. "
             "So move the runtime first, run it for a release cycle, and only then raise the target. Teams that do both together lose their cheapest rollback exactly when they need it.",
             "On the canary, watch GC pause distribution, memory outside the heap, p99 latency, and errors on anything that formats dates, numbers or currency.",
         ]),

    dict(title="Production rules",
         kicker="Do this · Never do this",
         body='<div class="grid2 start">'
              + '<div><div class="col-h ok">Do</div>'
              + bullets(["Assess before estimating",
                         "Upgrade dependencies on the old JDK first",
                         "**8 → 17 → 21 → 25**, shipping each",
                         "Runtime first, `--release` later",
                         "Every `--add-opens` commented, with an owner",
                         "Test locale, GC, TLS, charset"], cls="bullets sm") + "</div>"
              + '<div class="frag" data-step="1"><div class="col-h bad">Never</div>'
              + bullets(["8 → 25 in one step",
                         "New language features in the upgrade PR",
                         "Treat `--add-opens` as configuration",
                         "Trust a clean compile",
                         "Skip the canary because staging passed"], cls="bullets sm bad") + "</div>"
              + "</div>",
         narration=[
             "Production rules. Assess before estimating. Upgrade dependencies on the old JDK first. Step from 8 to 17 to 21 to 25, shipping each one. Move the runtime before raising the release flag. Comment every add-opens with an owner. And test the silent changes: locale, GC, TLS and charset.",
             "Never jump from 8 to 25 in one step. Never adopt new language features in the upgrade PR. Never treat add-opens as configuration. Never trust a clean compile. And never skip the canary because staging passed.",
         ]),

    dict(kind="title",
         title="Recap",
         kicker="Ch 05 · Migration Strategy",
         body=bullets(["Removed · encapsulated · **silently changed**",
                       "The work is mostly **dependencies**",
                       "17 is the landing point; then 21 and 25 are easy",
                       "Move the runtime first; `--release` later",
                       "Next: **Ch 06 · Lambdas &amp; Functional Interfaces**"], cls="bullets recap"),
         narration=[
             "To recap. Breakage comes in three kinds, and the silent behaviour changes are the dangerous ones. The work is mostly dependency upgrades. Java 17 is the landing point, and after it, 21 and 25 are easy. "
             "And move the runtime before raising the release flag, so rollback stays cheap.",
             "That completes the platform section. Next is chapter six: lambdas and functional interfaces. Thanks for watching.",
         ]),
]
