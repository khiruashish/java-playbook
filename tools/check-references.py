#!/usr/bin/env python3
"""Editorial audit: checks that references say what they point at.

  1. Link text vs target   — "[Ch 31](…/31-virtual-threads.md)" must point at chapter 31;
                             "[Virtual Threads](…)" must point at a page with that title.
  2. Section references    — "§5.2" must exist in the chapter it refers to.
  3. Chapter mentions      — plain-text "Chapter 47" must be a real chapter.
  4. JEP / release claims  — "JEP 491 (Java 24)" must agree with Appendix A.
  5. Typos                 — doubled words and common misspellings, outside code.

Usage: python3 tools/check-references.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MISSPELLINGS = ["occured", "seperate", "recieve", "definately", "untill", "accross", "wich ", "teh ",
                "dependancy", "existant", "consistant", "occurence", "concurent", "asynchronus", "threshhold",
                "paramter", "retreive", "sucess", "garantee", "enviroment", "adress", "begining", "calender",
                "comming", "comparision", "explicitely", "independant", "neccessary", "ocurr", "persistance",
                "preceed", "refering", "responsability", "succesful", "supress", "tommorow", "wierd"]


def pages():
    out = {}
    for f in sorted(DOCS.rglob("*.md")):
        t = f.read_text()
        title = (re.search(r"^# (.+)$", t, re.M) or [None, f.stem])[1]
        out[f] = dict(text=t, title=title, num=(re.match(r"(\d\d)-", f.name) or [None, None])[1],
                      sections=set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)[. ]", t, re.M)))
    return out


def prose_lines(text):
    """Yield (line_no, line) outside fenced code, with inline code removed."""
    fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*```", line):
            fence = not fence; continue
        if not fence:
            yield i, re.sub(r"`[^`]*`", "``", line)


def norm(s):
    s = re.sub(r"`|\*|_|¶", "", s.lower())
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def jep_matrix():
    rows, release = {}, None
    for line in (DOCS / "appendix/a-jep-matrix.md").read_text().splitlines():
        m = re.match(r"### Java (\d+)(?:–(\d+))?", line)
        if m: release = (int(m.group(1)), int(m.group(2) or m.group(1))); continue
        m = re.match(r"\| ([\d, ]+) \|.*?\|(?: (\d+) \|)? [^|]*\|$", line)
        if m and release:
            rel = int(m.group(2)) if m.group(2) else None
            for n in re.findall(r"\d+", m.group(1)):
                rows.setdefault(int(n), (rel, rel) if rel else release)
    return rows


def section_exists(ref, sections):
    """'§5.2' needs a 5.2 heading; only an undotted '§5' may match a top-level section."""
    return ref in sections if "." in ref else ref in sections


def main():
    P = pages()
    findings = []
    checked = dict(links=0, sections=0, chapters=0, jeps=0)
    jeps = jep_matrix()
    chapter_nums = {p["num"] for p in P.values() if p["num"]}

    for f, p in P.items():
        rel = str(f.relative_to(DOCS))
        is_generated = f.name.startswith(("b-", "c-", "e-", "f-"))
        for i, line in prose_lines(p["text"]):
            # 1. link text vs target
            for text, href in re.findall(r"\[([^\]]+)\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", line):
                target = (f.parent / href).resolve()
                if target not in P: continue
                tp = P[target]; checked['links'] += 1
                m = re.fullmatch(r"(?:Ch(?:apter)?\.?\s*)?(\d{1,2})(?:\s*§[\d.]+)?", text.strip())
                if m and tp["num"] and int(m.group(1)) != int(tp["num"]):
                    findings.append((rel, i, "link-number", f"'{text}' → {href} (chapter {tp['num']})"))
                sec = re.search(r"§(\d+(?:\.\d+)*)", text)
                if sec: checked['sections'] += 1
                if sec and not section_exists(sec.group(1), tp["sections"]):
                    findings.append((rel, i, "link-section", f"'{text}' → {href} has no §{sec.group(1)}"))
                if not m and not re.match(r"^(Appendix [A-F]|Ch\b|Chapter\b|Chapters\b|[A-F]|Home|this)", text) \
                   and not href.endswith("index.md") and len(norm(text)) >= 2:
                    words = set(norm(text)) - {"the", "a", "and", "of", "in", "to", "with"}
                    if words and not words & set(norm(tp["title"])):
                        findings.append((rel, i, "link-title", f"'{text}' → '{tp['title']}'"))
            # 2. bare section refs inside this chapter
            if not is_generated:
                for sec in re.findall(r"(?<!\])§(\d+(?:\.\d+)*)", re.sub(r"\[[^\]]*\]\([^)]*\)", "", line)):
                    checked['sections'] += 1
                    if not section_exists(sec, p["sections"]):
                        findings.append((rel, i, "section", f"§{sec} not found in this page"))
            # 3. plain chapter mentions
            for n in re.findall(r"\bChapter (\d{1,2})\b", re.sub(r"\[[^\]]*\]\([^)]*\)", "", line)):
                checked['chapters'] += 1
                if f"{int(n):02d}" not in chapter_nums:
                    findings.append((rel, i, "chapter", f"Chapter {n} does not exist"))
            # 4. JEP release claims
            if f.name != "a-jep-matrix.md" and f.name != "f-glossary.md":
                for jep, ver in re.findall(r"JEP (\d{3})\)?[ ,(]{1,3}(?:Java |JDK )(\d{2})\b", line):
                    jep, ver = int(jep), int(ver); checked['jeps'] += jep in jeps
                    if jep in jeps and not (jeps[jep][0] <= ver <= jeps[jep][1]):
                        findings.append((rel, i, "jep-release", f"JEP {jep} said to be Java {ver}; Appendix A says {jeps[jep][0]}"))
                for ver, jep in re.findall(r"\b(?:Java |JDK )(\d{2})\b[^|.;,(]{0,30}\(JEP (\d{3})\)", line):
                    jep, ver = int(jep), int(ver); checked['jeps'] += jep in jeps
                    if jep in jeps and not (jeps[jep][0] <= ver <= jeps[jep][1]):
                        findings.append((rel, i, "jep-release", f"Java {ver} … (JEP {jep}); Appendix A says {jeps[jep][0]}"))
            # 4b. version-table rows: "| **24** | … (JEP 491) … |" — each JEP should belong to that release
            if f.name not in ("a-jep-matrix.md", "f-glossary.md"):
                row = re.match(r"^\|\s*\*{0,2}(\d{1,2})(?:[–-](\d{1,2}))?\*{0,2}\s*\|(.*)$", line)
                if row:
                    lo, hi = int(row.group(1)), int(row.group(2) or row.group(1))
                    for jep in map(int, re.findall(r"JEP (\d{3})", row.group(3))):
                        if jep in jeps:
                            checked['jeps'] += 1
                            a_lo, a_hi = jeps[jep]
                            if not (lo <= a_hi and a_lo <= hi):
                                findings.append((rel, i, "jep-table", f"row Java {row.group(1)}{'–'+row.group(2) if row.group(2) else ''} cites JEP {jep}; Appendix A says {a_lo}"))
            # 5. typos
            low = line.lower()
            for w in re.findall(r"\b(\w+) \1\b(?!-)", low):
                if w not in ("that", "had", "is", "very", "bye", "do", "log", "ha"):
                    findings.append((rel, i, "doubled-word", f"'{w} {w}'"))
            for bad in MISSPELLINGS:
                if bad in low:
                    findings.append((rel, i, "spelling", bad.strip()))

    kinds = {}
    for rel, i, kind, msg in findings:
        kinds.setdefault(kind, []).append(f"{rel}:{i}  {msg}")
    print(f"pages audited: {len(P)} · checked: {checked['links']} links, {checked['sections']} section refs, "
          f"{checked['chapters']} chapter mentions, {checked['jeps']} JEP/release claims · findings: {len(findings)}")
    for kind, items in kinds.items():
        print(f"\n[{kind}] {len(items)}")
        for it in items[:40]: print("   " + it)
    sys.exit(1 if findings else 0)


main()
