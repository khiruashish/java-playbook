#!/usr/bin/env python3
"""Usage: check-code-blocks.py [--all] [--cp CLASSPATH]
  --all  run on JDK 25+ to include newer-feature blocks
  --cp   extra classpath, e.g. the test JARs from `mvn -f code/pom.xml dependency:build-classpath`\n\nExtract every ```java block from the handbook, wrap fragments so they can be
compiled, compile them in one javac run, and classify every result.

Buckets:
  PASS          compiled cleanly
  CONTEXT       only unresolved domain/third-party symbols — needs surrounding code
  NEWER_JDK     uses a feature final after the JDK doing the checking
  EXPECTED      the block is a deliberate compile-error example
  ILLUSTRATIVE  paraphrased JDK source or a conceptual sketch — not meant to compile
  FRAGMENT      a partial expression (e.g. a chain continuation) — cannot compile alone
  ARTEFACT      alternatives shown side by side in one block (duplicate names)
  DEFECT        anything else — needs a human to look
"""
import pathlib, re, subprocess, shutil, json, sys, textwrap, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNTIME = int(re.search(r'version "(\d+)', subprocess.run(["java", "-version"], capture_output=True, text=True).stderr).group(1))
WORK = pathlib.Path("/tmp/codecheck")
IMPORTS = """import java.util.*; import java.util.function.*; import java.util.stream.*;
import java.util.concurrent.*; import java.util.concurrent.atomic.*; import java.util.concurrent.locks.*;
import java.time.*; import java.time.format.*; import java.time.temporal.*; import java.math.*;
import java.io.*; import java.nio.*; import java.nio.file.*; import java.nio.charset.*; import java.net.*;
import java.net.http.*; import java.lang.invoke.*; import java.lang.management.*; import java.lang.reflect.*;
import java.text.*; import java.util.regex.*; import java.sql.Connection; import java.sql.PreparedStatement;
import java.sql.ResultSet; import java.sql.SQLException; import java.sql.Statement; import javax.sql.DataSource;
import static java.util.stream.Collectors.*; import static java.util.Comparator.*;
import static java.util.concurrent.CompletableFuture.*; import static java.util.concurrent.TimeUnit.*;
import com.handbook.grocery.*; import jdk.jfr.Event; import jdk.jfr.Name; import jdk.jfr.Label;
import jdk.jfr.Category; import jdk.jfr.Description; import java.net.http.HttpResponse.BodyHandlers; import java.net.http.HttpRequest.BodyPublishers;
import static java.nio.charset.StandardCharsets.UTF_8;
"""
DOMAIN_SRC = ROOT / "code/src/main/java/com/handbook/grocery"
DOMAIN_TYPES = {f.stem for f in DOMAIN_SRC.glob("*.java")} if DOMAIN_SRC.exists() else set()

NEWER = [r"Gatherers?\b", r"\.gather\(", r"\bScopedValue\b", r"StructuredTaskScope", r"\bJoiner\b",
         r"\bIO\.(println|readln)", r"^import module", r"\bArena\b", r"MemorySegment", r"MemoryLayout",
         r"ValueLayout", r"\bLinker\b", r"jdk\.incubator", r"IntVector", r"^void main\(",
         r"\bvar _\b", r"\(_,", r", _\)", r"\b_ ->", r"catch \(\w+ _\)", r"case \w+ _", r"\(_\s*\)",
         r"FunctionDescriptor", r"SymbolLookup", r"StableValue|LazyConstant"]
EXPECTED = re.compile(r"COMPILE ERROR|does not compile|won't compile|NOT VALID|compile error|// ERROR|ERROR:|if this compiled", re.I)
ILLUSTRATIVE_TITLE = re.compile(r"JDK source|paraphrased|simplified|Conceptual|Structure", re.I)
TYPE_DECL = re.compile(r"^(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|private|protected|static|final|abstract|sealed|non-sealed)\s+)*(class|record|interface|enum)\s+(\w+)", re.M)
METHOD_DECL = re.compile(r"^(?!\s)(?:@\w+(?:\([^)]*\))?\s*\n?)*(?:(?:public|private|protected|static|final|synchronized|default|abstract)\s+)*(?:<[^>]+>\s+)?[\w<>\[\],.? ]+\s+\w+\([^;]*\)\s*(?:throws [\w., ]+)?\s*\{", re.M)

def blocks():
    files = sorted((ROOT/"docs").rglob("*.md"))
    files = [f for f in files if f.parent.name != "appendix" or f.name.startswith("b-")]
    for f in files:
        lines = f.read_text().splitlines()
        i = 0
        while i < len(lines):
            m = re.match(r"^(\s*)```java(.*)$", lines[i])
            if m:
                ind, attrs = m.group(1), m.group(2)
                j = i + 1; body = []
                while j < len(lines) and lines[j].strip() != "```":
                    body.append(lines[j][len(ind):] if lines[j].startswith(ind) else lines[j]); j += 1
                title = (re.search(r'title="([^"]*)"', attrs) or [None, ""])[1]
                code = "\n".join(body)
                inc = re.fullmatch(r'\s*--8<--\s*"([^"]+)"\s*', code)
                if inc:                                          # snippet include: check the real file
                    code = (ROOT / inc.group(1)).read_text()
                    code = "\n".join(l for l in code.splitlines() if not l.startswith("// run:"))
                yield dict(file=str(f.relative_to(ROOT)), line=i+1, title=title, code=code)
                i = j
            i += 1

TOP_PUBLIC = re.compile(r"^public\s+(?=(?:(?:final|abstract|sealed|non-sealed|static)\s+)*(?:class|record|interface|enum)\b)", re.M)

def single_file(code):
    """Blocks often show several public types as if they were separate files. Java allows one
    public top-level type per file, so drop `public` on top-level declarations: same package,
    same meaning for compile-checking."""
    return TOP_PUBLIC.sub("", code)

def elide(code):
    code = re.sub(r"/\*[^*]*\.\.\.[^*]*\*/", "/* elided */", code)   # keep existing /* ... */ intact
    code = re.sub(r"=\s*\.\.\.\s*;", "= null;", code)                 # `x = ...;` placeholders
    code = re.sub(r"(?<![\w>\]])\.\.\.", "/*...*/", code)             # `{ ... }`, `(...)`, `)...`
    return code

MEMBER_LINE = re.compile(r"^(?:@\w+|(?:private|protected|public|static|final)\b)")
STMT_LINE = re.compile(r"^(?:try|for|if|while|switch|return|throw|do)\b|^\w+(?:\.\w+)*\s*\(|^\w+\.\w+.*;\s*(//.*)?$")

B_DOMAIN = """
record Product(String sku, String name, String vendor, String category, long pricePaise, boolean perishable) { }
record OrderLine(String sku, int quantity, long pricePaise) { long total() { return quantity * pricePaise; } }
record Order(String id, String customer, String city, List<OrderLine> lines, LocalDate placedOn) {
    long total() { return lines.stream().mapToLong(OrderLine::total).sum(); } }
"""
B_FIELDS = """List<Product> products; List<Order> orders; String input; List<String> skus;
Map<String, Product> bySku; Product p; Clock clock; List<Integer> nums; List<String> rawSkus;"""

def wrap(b, n, returning):
    code = single_file(elide(b["code"]))
    pkg = f"s{n:04d}"
    is_b = b["file"].startswith("docs/appendix/b-")
    extra_types = B_DOMAIN if is_b else ""
    fields = B_FIELDS if is_b else ""
    has_type = bool(TYPE_DECL.search(code))
    col0 = [l for l in code.splitlines() if l and not l[0].isspace() and not l.startswith(("//","/*","*"))]
    body_is_members = (bool(METHOD_DECL.search(code)) or any(MEMBER_LINE.match(l) for l in col0)) and not has_type
    b["unit"] = has_type and not body_is_members
    if has_type:
        # compile as a unit
        src = f"package {pkg};\n{IMPORTS}\n{code}\n{extra_types}\nclass Snippet {{ {fields} }}\n"
    elif body_is_members:
        src = f"package {pkg};\n{IMPORTS}\n{extra_types}\nclass Snippet extends SnippetContext {{\n{fields}\n{code}\n}}\n"
    else:
        ret = "Object" if returning else "void"
        src = (f"package {pkg};\n{IMPORTS}\n{extra_types}\nclass Snippet extends SnippetContext {{\n{fields}\n"
               f"@SuppressWarnings(\"all\") {ret} run() throws Throwable {{\n{code}\n}}\n}}\n")
    return pkg, src

# Third-party names the handbook uses but the offline checker cannot resolve (pass --cp to check them).
LIBRARY_NAMES = {"LoggerFactory", "Logger", "ObjectMapper", "TypeReference", "Flyway", "PGSimpleDataSource",
    "Awaitility", "WireMock", "Assertions", "Mockito", "BDDMockito", "ArgumentMatchers"}

def classify_errors(errs, code):
    declared = set(re.findall(r"\b(?:class|record|interface|enum)\s+(\w+)", code))
    kinds = set()
    for e in errs:
        msg = e["msg"]
        if "missing return statement" in msg: continue
        if re.search(r"preview|underscore|unnamed class|call to super must be first|as of release", msg, re.I):
            kinds.add("NEWER_JDK"); e["class"]="NEWER"; continue
        if re.search(r"already defined|is public, should be declared in a file|duplicate class", msg):
            kinds.add("ARTEFACT"); e["class"]="ARTEFACT"; continue
        if "unexpected return value" in msg: kinds.add("RETRY"); continue
        if re.search(r"invalid method reference|<any>|is never thrown in body|of type Object", msg + e.get("location","")):
            kinds.add("CONTEXT"); e["class"]="CONTEXT"; continue
        if re.search(r"not initialized in the default constructor|does not override or implement|"
                     r"return type required|cannot be converted to Annotation|package .* does not exist|"
                     r"not abstract and does not override", msg):
            kinds.add("CONTEXT"); e["class"]="CONTEXT"; continue
        if "cannot find symbol" in msg:
            sym, loc = e.get("symbol",""), e.get("location","")
            if sym.split(" ")[-1].split("(")[0] in LIBRARY_NAMES:
                kinds.add("CONTEXT"); e["class"]="CONTEXT"; continue
            loc_type = (loc.split("of type")[-1].strip() if "of type" in loc else loc.split()[-1]) if loc else ""
            loc_type = loc_type.split("<")[0].split(".")[-1]
            if loc_type in DOMAIN_TYPES and loc_type not in declared:
                kinds.add("DOMAIN_GAP"); e["class"]="DOMAIN_GAP"; continue
            if sym.startswith("variable") and loc.startswith(("class", "interface")) and loc_type[:1].isupper() \
               and loc_type not in declared and loc_type != "Snippet" and loc_type != "SnippetContext":
                kinds.add("DEFECT?"); e["class"]="DEFECT"; continue
            if sym.startswith(("class", "variable")) or not loc:
                kinds.add("CONTEXT"); e["class"]="CONTEXT"; continue
            loc_type = loc_type.split("<")[0].split(".")[-1]
            if loc_type in declared or loc_type == "Snippet" or not loc_type[:1].isupper():
                kinds.add("CONTEXT"); e["class"]="CONTEXT"; continue
            kinds.add("DEFECT?"); e["class"]="DEFECT"; continue
        kinds.add("DEFECT?"); e["class"]="DEFECT"
    return kinds

TYPE_NAMES = re.compile(r"\b(?:class|record|interface|enum)\s+(\w+)")

def support_for(bs, n):
    """Other blocks in the same chapter that declare types block n uses but does not declare.
    Only clean, whole-type blocks qualify; names declared in more than one block are skipped
    (those are deliberate before/after pairs)."""
    me = bs[n]; own = set(TYPE_NAMES.findall(me["code"]))
    used = set(re.findall(r"\b([A-Z]\w+)\b", me["code"])) - own
    chapter = [i for i, b in enumerate(bs) if b["file"] == me["file"] and i != n]
    counts = {}
    for i in chapter:
        for name in set(TYPE_NAMES.findall(bs[i]["code"])): counts[name] = counts.get(name, 0) + 1
    picked, names = [], set()
    for i in chapter:
        b = bs[i]
        if b.get("bucket") not in ("PASS", "CONTEXT", "REVIEWED") or not b.get("unit"): continue
        declares = set(TYPE_NAMES.findall(b["code"]))
        if not (declares & used) or (declares & own) or (declares & names): continue
        if any(counts[d] > 1 for d in declares): continue
        picked.append(i); names |= declares
    return picked

def compile_all(entries):
    if WORK.exists(): shutil.rmtree(WORK)
    (WORK/"src").mkdir(parents=True); (WORK/"out").mkdir()
    paths = []
    for entry in entries:
        pkg, src = entry[0], entry[1]
        d = WORK/"src"/pkg; d.mkdir()
        for k, extra in enumerate(entry[2] if len(entry) > 2 else []):
            pub = re.search(r"^public\s+(?:(?:final|abstract|sealed|non-sealed|static)\s+)*(?:class|record|interface|enum)\s+(\w+)", extra, re.M)
            f = d/((pub.group(1) if pub else f"Support{k}") + ".java"); f.write_text(f"package {pkg};\n{IMPORTS}\n{extra}\n"); paths.append(str(f))
        pub = re.search(r"^public\s+(?:(?:final|abstract|sealed|non-sealed|static)\s+)*(?:class|record|interface|enum)\s+(\w+)", src, re.M)
        p = d/((pub.group(1) if pub else "Snippet") + ".java"); p.write_text(src); paths.append(str(p))
    argfile = WORK/"files.txt"; argfile.write_text("\n".join(paths))
    (WORK/"domain").mkdir(exist_ok=True)
    subprocess.run(["java", "-m", "jdk.compiler/com.sun.tools.javac.Main", "-d", str(WORK/"domain"),
                    *map(str, DOMAIN_SRC.glob("*.java")),
                    *map(str, (ROOT/"code/src/test/java/com/handbook/grocery").glob("*.java"))], check=True)
    r = subprocess.run(["java", "-m", "jdk.compiler/com.sun.tools.javac.Main", "-d", str(WORK/"out"), "-cp", str(WORK/"domain") + (os.pathsep + EXTRA_CP if EXTRA_CP else ""),
                        "-proc:none", "-nowarn", "-Xmaxerrs", "100000", "-XDshould-stop.ifError=FLOW",
                        *(["--enable-preview", "--release", str(RUNTIME)] if ALL else []),
                        f"@{argfile}"], capture_output=True, text=True)
    errs, cur = {}, None
    for line in (r.stdout + r.stderr).splitlines():
        m = re.match(r"(/tmp/codecheck/src/(s\d{4})/\w+\.java):(\d+): error: (.*)", line)
        if m:
            src_lines = pathlib.Path(m.group(1)).read_text().splitlines()
            cur = dict(pkg=m.group(2), line=int(m.group(3)), msg=m.group(4),
                       src=src_lines[int(m.group(3))-1].strip() if int(m.group(3)) <= len(src_lines) else "")
            errs.setdefault(cur["pkg"], []).append(cur)
            continue
        if cur is not None:
            s = line.strip()
            if s.startswith("symbol:"):   cur["symbol"] = s.split(":", 1)[1].strip()
            if s.startswith("location:"): cur["location"] = s.split(":", 1)[1].strip()
    return errs

ALL = "--all" in sys.argv          # on a JDK 25+ machine: compile newer-feature blocks too
EXTRA_CP = sys.argv[sys.argv.index("--cp") + 1] if "--cp" in sys.argv else ""   # e.g. test-library JARs

def main():
    bs = list(blocks())
    results = []
    todo = []
    for n, b in enumerate(bs):
        code = b["code"]
        if EXPECTED.search(code) or EXPECTED.search(b["title"]):
            b["bucket"] = "EXPECTED"
        elif ILLUSTRATIVE_TITLE.search(b["title"]) or re.search(r"CONCEPTUAL|// What the JVM sees|simplified", code):
            b["bucket"] = "ILLUSTRATIVE"
        elif not ALL and any(re.search(p, code, re.M) for p in NEWER):
            b["bucket"] = "NEWER_JDK"
        elif re.match(r"\s*\.", code) or (";" not in code and "{" not in code and len(code.strip().splitlines()) > 1):
            b["bucket"] = "FRAGMENT"
        elif all(l.startswith("import ") or l.startswith("//") or not l.strip() for l in code.splitlines()):
            b["bucket"] = "ILLUSTRATIVE"
        elif (lambda c0: any(MEMBER_LINE.match(l) or METHOD_DECL.match(l) for l in c0) and any(STMT_LINE.match(l) for l in c0))(
                [l for l in code.splitlines() if l and not l[0].isspace() and not l.startswith(("//","/*"))]) \
             and not TYPE_DECL.search(code):
            b["bucket"] = "ARTEFACT"
        else:
            todo.append(n)
    entries = [wrap(bs[n], n, False) for n in todo]
    errs = compile_all(entries)
    retry = []
    for n in todo:
        pkg = f"s{n:04d}"; e = errs.get(pkg, [])
        kinds = classify_errors(e, bs[n]["code"]) if e else set()
        if "RETRY" in kinds: retry.append(n); continue
        bs[n]["errors"] = e; bs[n]["kinds"] = kinds
    if retry:
        errs2 = compile_all([wrap(bs[n], n, True) for n in retry])
        for n in retry:
            e = errs2.get(f"s{n:04d}", []); bs[n]["errors"] = e; bs[n]["returned"] = True
            bs[n]["kinds"] = classify_errors(e, bs[n]["code"]) - {"RETRY"} if e else set()
    for n in todo:
        k = bs[n]["kinds"]
        bs[n]["bucket"] = ("PASS" if not k else "NEWER_JDK" if "NEWER_JDK" in k else
                           "DEFECT" if "DEFECT?" in k else "DOMAIN_GAP" if "DOMAIN_GAP" in k else
                           "ARTEFACT" if "ARTEFACT" in k else "CONTEXT")
    third = [(n, support_for(bs, n)) for n in todo if bs[n]["bucket"] == "CONTEXT"]
    third = [(n, s) for n, s in third if s]
    if third:
        entries3 = []
        for n, sup in third:
            pkg, src = wrap(bs[n], n, bs[n].get("returned", False))
            entries3.append((pkg, src, [single_file(elide(bs[i]["code"])) for i in sup]))
        errs3 = compile_all(entries3)
        for n, sup in third:
            e = errs3.get(f"s{n:04d}", [])
            k3 = classify_errors(e, bs[n]["code"]) - {"RETRY"} if e else set()
            bs[n]["third"] = dict(support=[bs[i]["line"] for i in sup], before=len(bs[n]["errors"]), after=len(e),
                                  kinds=sorted(k3), sample=[x["msg"][:70] + " → " + x.get("src","")[:50] for x in e[:3]])
            # Accept if it resolved more, OR if it exposed a real defect — hiding defects defeats the purpose
            if not k3 or "DEFECT?" in k3 or len(e) < len(bs[n]["errors"]):
                bs[n]["errors"], bs[n]["kinds"] = e, k3
                bs[n]["support"] = [bs[i]["line"] for i in sup]
    for n in todo:
        k = bs[n]["kinds"]
        bs[n]["bucket"] = ("PASS" if not k else "NEWER_JDK" if "NEWER_JDK" in k else
                           "DEFECT" if "DEFECT?" in k else "DOMAIN_GAP" if "DOMAIN_GAP" in k else
                           "ARTEFACT" if "ARTEFACT" in k else "CONTEXT")
    import hashlib
    baseline_file = ROOT / "tools/code-check-baseline.json"
    baseline = json.loads(baseline_file.read_text()) if baseline_file.exists() else {}
    for b in bs:
        b["hash"] = hashlib.sha1(b["code"].encode()).hexdigest()[:12]
        if b["bucket"] in ("DEFECT", "DOMAIN_GAP") and b["hash"] in baseline:
            b["bucket"] = "REVIEWED"; b["reason"] = baseline[b["hash"]]["reason"]
    json.dump(bs, open("/tmp/codecheck-results.json", "w"), indent=1, default=list)
    from collections import Counter
    c = Counter(b["bucket"] for b in bs)
    print(f"java blocks: {len(bs)}")
    for k in ["PASS","CONTEXT","DOMAIN_GAP","NEWER_JDK","EXPECTED","ILLUSTRATIVE","FRAGMENT","ARTEFACT","REVIEWED","DEFECT"]:
        print(f"  {k:13} {c.get(k,0)}")

main()
