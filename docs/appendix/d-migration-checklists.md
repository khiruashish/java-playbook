---
title: Migration Checklists
status: review
---

# Appendix D — Migration Checklists

Tickable checklists for each JDK upgrade step, distilled from [Chapter 05](../01-platform/05-migration-strategy.md). Copy the relevant section into your upgrade ticket.

!!! tip "The three rules"
    1. **Step, never jump.** 8 → 17 → 21 → 25. Ship each step to production before starting the next.
    2. **Change one thing.** The upgrade PR changes the JDK. Adopting new language features is a separate PR afterwards.
    3. **Move the runtime before raising `--release`.** Rollback then stays a runtime change, not a rebuild.

---

## 0. Assessment — one day, before estimating anything

The output of this section *is* the estimate. Roughly 90% of migration effort is in dependencies, not your code.

- [ ] Run `jdeps -jdkinternals --multi-release <target> -cp "lib/*" app.jar` and save the output
- [ ] Run `jdeprscan --release <target> --class-path "lib/*" app.jar` and save the output
- [ ] Run `mvn versions:display-dependency-updates` (or `gradlew dependencyUpdates`)
- [ ] Split the `jdeps` findings into **your code** and **dependencies**
- [ ] For each dependency finding, check whether a newer version removes it
- [ ] List dependencies with **no** supported version — these are the real blockers
- [ ] Try starting the unchanged application on the target JDK and record what fails
- [ ] Inventory every JVM flag in start scripts, Dockerfiles, and `JAVA_TOOL_OPTIONS`
- [ ] Check for `_JAVA_OPTIONS` anywhere in the environment — it overrides the command line

See [Ch 03](../01-platform/03-toolchain.md) for the tools and [Ch 05 §5.1](../01-platform/05-migration-strategy.md) for reading the output.

---

## 1. Java 8 → 17 — the hard step

### 1a. Dependencies first, still on Java 8

- [ ] Upgrade every dependency that has a version supporting both 8 and 17
- [ ] Ship that to production **on Java 8** before touching the JDK
- [ ] Replace or isolate dependencies that are abandoned

### 1b. Removed Java EE modules (removed in 11)

- [ ] Add `jakarta.xml.bind-api` + `jaxb-runtime` if JAXB is used
- [ ] Add JAX-WS, JAF, Common Annotations, or JTA artifacts if used
- [ ] Remove any CORBA usage — there is no drop-in replacement
- [ ] Search for `javax.xml.bind`, `javax.xml.ws`, `javax.annotation`, `javax.activation`

### 1c. Build

- [ ] Replace `-source`/`-target` with `--release 17`
- [ ] Declare a toolchain (Maven toolchains or Gradle `java.toolchain`)
- [ ] Add `-parameters` if not already present
- [ ] Declare annotation processor paths explicitly
- [ ] Set `-encoding UTF-8` explicitly
- [ ] Remove `mockito-inline` if moving to Mockito 5 — see [Ch 42](../06-testing/42-mockito.md)
- [ ] Add the target JDK to the CI matrix alongside the current one

### 1d. Strong encapsulation (enforced in 16, `--illegal-access` removed in 17)

- [ ] Start the application and collect every `InaccessibleObjectException`
- [ ] For each, identify the library and check for a version that no longer needs it
- [ ] Where none exists, add `--add-opens` to an **argument file** with a comment naming the library and the version that removes it
- [ ] Replace any `sun.misc.Unsafe` use in your own code with `VarHandle` or FFM
- [ ] Remove `--illegal-access` from every start script — it no longer exists

### 1e. Removed flags and features

- [ ] Remove `-XX:+UseConcMarkSweepGC` — **CMS was removed in 14 and the JVM will not start**
- [ ] Remove `-XX:PermSize` / `-XX:MaxPermSize`
- [ ] Remove Java 8-era GC tuning flags and re-derive from measurement
- [ ] Replace Nashorn (removed in 15) if any scripting depends on it
- [ ] Replace `-Xmx` fixed to container size with `-XX:MaxRAMPercentage`

### 1f. Silent behaviour changes — these do not fail, they differ

- [ ] **Locale data (CLDR, Java 9):** test every date, number, and currency formatted as a string that crosses a system boundary
- [ ] **Default GC (Parallel → G1, Java 9):** measure throughput and p99 on production-like load; set `-XX:+UseParallelGC` explicitly if throughput-bound
- [ ] **Default charset (UTF-8, Java 18):** relevant when going beyond 17 — test file and stream I/O without explicit charsets
- [ ] **TLS defaults:** verify every external integration still negotiates a connection
- [ ] **Container memory:** re-check heap sizing now that the JVM reads cgroup limits

### 1g. Ship

- [ ] Keep `--release 11` or `--release 8` for one release cycle if you need a fast rollback path
- [ ] Deploy to staging and run the full suite
- [ ] Canary one instance; watch GC pauses, non-heap footprint, and p99 — not just error rate
- [ ] Partial rollout, then full
- [ ] **Run Java 17 in production before starting the next step**

---

## 2. Java 11 → 17

For teams already on 11. A subset of section 1.

- [ ] Assessment (section 0) against 17
- [ ] Section **1d** in full — strong encapsulation is the main work
- [ ] Remove CMS flags and Nashorn usage (1e)
- [ ] Recompile and check exhaustive switches if adopting sealed types later
- [ ] Rollout (1g)

---

## 3. Java 17 → 21

Comparatively easy. Frameworks already target 17.

- [ ] Assessment (section 0) against 21
- [ ] Replace any `Thread.stop`, `suspend`, or `resume` calls — they throw `UnsupportedOperationException` since 20
- [ ] Check `-Xlint:this-escape` warnings
- [ ] If adopting virtual threads: profile for pinning with the JFR `jdk.VirtualThreadPinned` event — `synchronized` still pins on 21
- [ ] If adopting virtual threads: audit `ThreadLocal` usage for large per-thread values — see [Ch 31](../04-concurrency/31-virtual-threads.md)
- [ ] If adopting virtual threads: re-check connection pool sizing — it becomes the visible ceiling
- [ ] Rollout (1g)

---

## 4. Java 21 → 25

Mostly additive.

- [ ] Assessment (section 0) against 25
- [ ] Remove `ReentrantLock` conversions made **only** to avoid virtual-thread pinning — JEP 491 (Java 24) fixed `synchronized`
- [ ] Recheck the `--add-opens` inventory; many libraries no longer need theirs
- [ ] Confirm no Security Manager usage remains — permanently disabled in 24
- [ ] Confirm no 32-bit x86 deployments — removed in 24 (Windows) and 25 (all)
- [ ] Check for `sun.misc.Unsafe` memory-access warnings (JEP 498, Java 24)
- [ ] Rewrite any `StructuredTaskScope.ShutdownOnFailure` code — the preview API changed; see [Ch 32](../04-concurrency/32-structured-concurrency.md)
- [ ] Rewrite any String Templates (`STR."..."`) code — withdrawn, see [Ch 15](../02-language/15-string-templates-postmortem.md)
- [ ] **Re-baseline heap sizing** — compact object headers (JEP 519) shrink the live set
- [ ] Consider `-XX:+AutoCreateSharedArchive` for startup — see [Ch 36](../05-runtime/36-startup-and-leyden.md)
- [ ] Rollout (1g)

---

## 5. Java 25 → 26 — CI only, for most teams

Java 26 is a non-LTS release. Run it in CI to surface the next LTS's changes early.

- [ ] Add 26 to the CI matrix as a **non-blocking** job
- [ ] Check for final-field mutation warnings (JEP 500) — frameworks setting final fields reflectively
- [ ] Remove any Applet API references (removed, JEP 504)
- [ ] Treat failures as backlog for the next LTS, not as blockers

---

## 6. After landing — adoption, as separate PRs

Adopt these **after** the upgrade has been in production, each in its own change.

| Feature | Available | Checklist |
|---|---|---|
| `var` | 10 | Never with a bare diamond — [Ch 11](../02-language/11-java-9-to-11.md) |
| Records | 16 | `List.copyOf` every collection component — [Ch 22](../03-collections/22-immutability.md) |
| Sealed types | 17 | Only for genuinely closed domains; omit `default` in switches — [Ch 12](../02-language/12-java-14-to-17.md) |
| Pattern matching for `switch` | 21 | Seal the hierarchy first — [Ch 13](../02-language/13-pattern-matching.md) |
| Sequenced collections | 21 | `reversed()` is a view, not a copy — [Ch 21](../03-collections/21-sequenced-collections.md) |
| Virtual threads | 21 | Never pool them; bound resources with a `Semaphore` — [Ch 31](../04-concurrency/31-virtual-threads.md) |
| Stream gatherers | 24 | `mapConcurrent` for bounded I/O fan-out — [Ch 38](../05-runtime/38-stream-gatherers.md) |
| `ScopedValue` | 25 | Replace request-context `ThreadLocal`s — [Ch 33](../04-concurrency/33-scoped-values.md) |

- [ ] `collect(Collectors.toList())` → `.toList()` **only** where the result is never mutated
- [ ] `list.get(list.size() - 1)` → `list.getLast()`
- [ ] Test-and-cast → `instanceof` patterns
- [ ] `new HashMap<>(n)` → `HashMap.newHashMap(n)` (19+)
- [ ] Executor-and-futures I/O fan-out → virtual threads or `mapConcurrent`

---

## 7. Standing hygiene — every upgrade

- [ ] Every `--add-opens` has a comment naming its library and removal version
- [ ] No `SNAPSHOT` dependencies or version ranges in released artifacts
- [ ] Container images pin the JDK **patch** version
- [ ] No preview features in any published library
- [ ] GC logging and continuous JFR enabled — see [Ch 34](../05-runtime/34-garbage-collection.md), [Ch 37](../05-runtime/37-profiling-jfr.md)
- [ ] Every scheduled task catches its own exceptions — see [Ch 28](../04-concurrency/28-executors.md)
- [ ] The latest non-LTS release runs in CI
