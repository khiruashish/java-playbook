#!/usr/bin/env python3
"""Run every example under code/examples/ with `java File.java` and save its real output
to File.out, which the Examples pages include next to the code.

A first-line comment `// run: <flags>` adds JVM flags, e.g.
    // run: --add-opens java.base/java.util=ALL-UNNAMED

Usage: python3 tools/run-examples.py [substring-filter]
"""
import pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "code/examples"


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    files = sorted(f for f in EXAMPLES.rglob("*.java") if only in str(f))
    failed = []
    for f in files:
        first = f.read_text().splitlines()[0]
        flags = first.split("run:", 1)[1].split() if first.startswith("// run:") else []
        start = time.time()
        try:
            r = subprocess.run(["java", *flags, f.name], cwd=f.parent, capture_output=True, text=True, timeout=60)
            out = (r.stdout + r.stderr).rstrip() + "\n"
            ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            out, ok = "TIMED OUT\n", False
        f.with_suffix(".out").write_text(out)
        status = "ok " if ok else "FAIL"
        print(f"  {status} {f.relative_to(EXAMPLES)}  ({time.time() - start:.1f}s)")
        if not ok:
            failed.append((f, out))
    print(f"\n{len(files)} examples · {len(files) - len(failed)} ran · {len(failed)} failed")
    for f, out in failed:
        print(f"\n--- {f.relative_to(EXAMPLES)}\n{out[:1200]}")
    sys.exit(1 if failed else 0)


main()
