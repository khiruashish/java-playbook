#!/usr/bin/env bash
#
# scaffold-handbook.sh
# Creates the full directory tree and stub files for the
# Modern Java Enterprise Handbook (Java 8 -> 26).
#
# Usage:
#   ./scaffold-handbook.sh [target-dir]
#
# Idempotent: existing files are never overwritten.

set -euo pipefail

ROOT="${1:-.}"
DOCS="$ROOT/docs"

# chapter spec: path|title|band|sources
CHAPTERS=(
"01-platform/01-jdk-landscape|The JDK Landscape (8 → 26)|L1|new"
"01-platform/02-jvm-runtime-model|JVM Runtime Model|L2|new"
"01-platform/03-toolchain|The Toolchain|L2|new"
"01-platform/04-builds-and-preview-features|Builds, Release Flags & Preview Features|L2|new"
"01-platform/05-migration-strategy|Migration Strategy 8 → 25|L4|new"

"02-language/06-lambdas-functional-interfaces|Lambdas & Functional Interfaces|L1|Java8-Guide §2-4; Java8-Interview §1-4"
"02-language/07-stream-api|The Stream API|L2|Java8-Guide §5; Java8-Interview §5-6"
"02-language/08-collectors|Collectors & Stream Composition|L2|Java8-Guide §5.6; Java8-Interview §7,§14"
"02-language/09-optional|Optional & Null Strategy|L2|Java8-Guide §6; Java8-Interview §8"
"02-language/10-java-time|java.time|L1|Java8-Guide §7; Java8-Interview §10"
"02-language/11-java-9-to-11|Java 9–11: Modules, var, HttpClient|L3|new"
"02-language/12-java-14-to-17|Java 14–17: Records, Sealed Types, Text Blocks|L2|new"
"02-language/13-pattern-matching|Pattern Matching|L2|Java21-Features §7-9"
"02-language/14-java-21-to-26|Java 21–26 Language Features|L3|Java21-Features §9"
"02-language/15-string-templates-postmortem|String Templates: A Post-Mortem|L4|Java21-Features §10"
"02-language/16-generics|Generics in Depth|L3|new"

"03-collections/17-choosing-a-collection|Choosing the Right Collection|L1|List-Guide §2"
"03-collections/18-list-internals|List Internals & CustomArrayList|L2|List-Guide §3-9; CustomArrayList-Guide"
"03-collections/19-hashmap-internals|HashMap Internals|L2|HashMap-Guide"
"03-collections/20-set-queue-deque|Set, Queue & Deque|L2|new"
"03-collections/21-sequenced-collections|Sequenced Collections|L2|List-Guide §5.6; HashMap-Guide §6.5"
"03-collections/22-immutability|Immutability & Defensive Copying|L3|new"
"03-collections/23-equality-and-ordering|equals, hashCode & Comparators|L2|new"

"04-concurrency/24-threading-fundamentals|Threading Fundamentals|L1|Threading-Basic §2-4"
"04-concurrency/25-shared-state|Shared State & Synchronization|L2|Threading-Basic §5-6"
"04-concurrency/26-java-memory-model|The Java Memory Model|L4|new"
"04-concurrency/27-locks-and-atomics|Locks, Atomics & java.util.concurrent|L3|Threading-Enterprise §3"
"04-concurrency/28-executors|Executors & Thread Pool Design|L3|Threading-Enterprise §3.1; Threading-Basic §7"
"04-concurrency/29-completable-future|CompletableFuture|L3|Threading-Enterprise §3.3; Java8-Interview §11"
"04-concurrency/30-concurrent-collections|ConcurrentHashMap & Concurrent Collections|L3|ConcurrentHashMap-Guide"
"04-concurrency/31-virtual-threads|Virtual Threads|L3|Java21-Concurrency §3-5; Java21-Features §3"
"04-concurrency/32-structured-concurrency|Structured Concurrency|L4|Java21-Concurrency §6,§8"
"04-concurrency/33-scoped-values|ThreadLocal → ScopedValue|L3|Threading-Enterprise §6; Java21-Features §5"

"05-runtime/34-garbage-collection|Garbage Collection|L4|new"
"05-runtime/35-memory-footprint|Memory Footprint & Object Layout|L4|new"
"05-runtime/36-startup-and-leyden|Startup, Warmup & Project Leyden|L4|new"
"05-runtime/37-profiling-jfr|Profiling with JFR|L3|new"
"05-runtime/38-stream-gatherers|Stream Gatherers|L3|new"
"05-runtime/39-ffm-and-vector-api|FFM API & Vector API|L4|Java21-Features §11"
"05-runtime/40-http-client|The HTTP Client (HTTP/3)|L3|new"

"06-testing/41-junit5|JUnit 5|L1|Unit-Testing-Guide §2-6"
"06-testing/42-mockito|Mockito & Test Doubles|L2|Unit-Testing-Guide §7-9"
"06-testing/43-integration-testing|Integration Testing & Testcontainers|L3|Integration-Testing-Guide"
"06-testing/44-testing-concurrency|Testing Concurrent Code|L4|new"

"appendix/a-jep-matrix|JEP Matrix (Java 8 → 26)|—|new"
"appendix/b-java8-interview-workbook|Java 8 Interview Workbook|—|Java8-Interview-Guide §14-16"
"appendix/c-concurrency-interview-bank|Concurrency Interview Bank|—|Java21-Concurrency §11"
"appendix/d-migration-checklists|Migration Checklists|—|new"
"appendix/e-cheat-sheets|Cheat Sheet Index|—|harvested"
"appendix/f-glossary|Glossary & JEP Index|—|new"
)

# part landing pages: dir|title|blurb
PARTS=(
"01-platform|Platform|The JDK itself: release cadence, runtime model, toolchain, and how to move between versions."
"02-language|Language|Every significant language feature from Java 8 to Java 26, organised by concept rather than by release."
"03-collections|Collections|The collections framework, its internals, and how to choose correctly under load."
"04-concurrency|Concurrency|From threads and the memory model through virtual threads and structured concurrency."
"05-runtime|Runtime|Garbage collection, memory layout, startup, profiling, and the APIs that reach outside the JVM."
"06-testing|Testing|Unit, integration, and concurrency testing discipline for modern Java."
"appendix|Reference|Matrices, checklists, interview banks, and cheat sheets."
)

echo "Scaffolding into: $ROOT"

mkdir -p "$ROOT/_source" "$ROOT/docs/assets/stylesheets" \
         "$ROOT/code/src/main/java/com/handbook/grocery"

# ---- part landing pages -----------------------------------------------------
for spec in "${PARTS[@]}"; do
  IFS='|' read -r dir title blurb <<< "$spec"
  mkdir -p "$DOCS/$dir"
  f="$DOCS/$dir/index.md"
  [ -f "$f" ] && continue
  cat > "$f" <<EOF
---
title: $title
status: draft
---

# $title

$blurb

!!! info "Status"
    This part is under construction. See the master plan for the chapter list
    and production order.
EOF
  echo "  + $dir/index.md"
done

# ---- chapter stubs ----------------------------------------------------------
for spec in "${CHAPTERS[@]}"; do
  IFS='|' read -r path title band sources <<< "$spec"
  f="$DOCS/$path.md"
  mkdir -p "$(dirname "$f")"
  [ -f "$f" ] && { echo "  = $path.md (exists, skipped)"; continue; }

  tag_dir="${path%%/*}"
  cat > "$f" <<EOF
---
title: $title
band: $band
status: draft
tags: [${tag_dir#0?-}]
---

# $title

!!! warning "Draft"
    **Band:** $band · **Source material:** $sources

    Not yet written. Generate with \`chapter-prompt.md\`.

## 1. Purpose & Audience

## 2. The Problem

## 3. Mental Model

## 4. Core API & Syntax

## 5. Worked Examples

## 6. Internals

## 7. Production Patterns & Anti-Patterns

## 8. Version Evolution (Java 8 → 26)

## 9. Interview Questions

!!! abstract "Cheat Sheet"
    _To be written._
EOF
  echo "  + $path.md"
done

# ---- home page --------------------------------------------------------------
if [ ! -f "$DOCS/index.md" ]; then
cat > "$DOCS/index.md" <<'EOF'
---
title: Home
---

# Modern Java Enterprise Handbook

A complete reference to the Java language and platform, **Java 8 through Java 26**,
organised by concept rather than by release. Every chapter traces its topic from
the Java 8 baseline to the current state on Java 25 LTS.

## How to read this

=== "New to modern Java"
    Start with [The JDK Landscape](01-platform/01-jdk-landscape.md), then work
    through **Language** in order. Skip **Runtime** until you have shipped
    something.

=== "Upgrading a legacy codebase"
    Start with [Migration Strategy](01-platform/05-migration-strategy.md) and
    [Appendix D](appendix/d-migration-checklists.md), then read the Part 8
    "Version Evolution" section of each chapter that touches your code.

=== "Preparing for interviews"
    Read Part 9 of every chapter, then
    [Appendix B](appendix/b-java8-interview-workbook.md) and
    [Appendix C](appendix/c-concurrency-interview-bank.md).

=== "Tuning production"
    Go straight to **Concurrency** and **Runtime**.

## Baseline

| Item | Status |
|---|---|
| Java 25 | Current LTS (September 2025) |
| Java 21 | Previous LTS (September 2023) |
| Java 26 | Current non-LTS (March 2026) |
| Spring references | Spring Boot 4 / Framework 7 |

## Conventions

- Code targets `--release 25` unless a block is explicitly labelled with an older baseline.
- Preview features carry a warning admonition naming the JDK version.
- All examples use one running domain: a grocery-marketplace **order & inventory engine**.
EOF
echo "  + index.md"
fi

# ---- extra css --------------------------------------------------------------
css="$DOCS/assets/stylesheets/extra.css"
if [ ! -f "$css" ]; then
cat > "$css" <<'EOF'
:root {
  --md-code-font: "JetBrains Mono", monospace;
}

/* Band badges: use with {.band-l1} etc. */
.band-l1, .band-l2, .band-l3, .band-l4 {
  border-radius: 0.25rem;
  padding: 0.1rem 0.4rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
}
.band-l1 { background: #2e7d32; }
.band-l2 { background: #1565c0; }
.band-l3 { background: #6a1b9a; }
.band-l4 { background: #c62828; }

/* Wider content column for API tables */
.md-grid { max-width: 68rem; }
EOF
echo "  + assets/stylesheets/extra.css"
fi

echo
echo "Done. Next:"
echo "  pip install -r requirements.txt"
echo "  cp /path/to/your/12/guides/*.md $ROOT/_source/"
echo "  mkdocs serve"
