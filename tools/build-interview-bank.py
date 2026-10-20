#!/usr/bin/env python3
"""Harvest the banded interview questions (section 9) from chapters and render
them as a self-test bank with collapsible answers.

Usage: build-interview-bank.py OUTPUT TITLE CHAPTER_GLOB... [--preamble FILE]
"""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
BANDS = [("L1", "Foundations"), ("L2", "Professional"), ("L3", "Enterprise"), ("L4", "Architect")]

def harvest(path):
    lines = path.read_text().splitlines()
    title = next(l[2:].strip() for l in lines if l.startswith("# "))
    start = next(i for i, l in enumerate(lines) if l.startswith("## 9. Interview Questions"))
    band, qs, i = None, [], start + 1
    while i < len(lines):
        l = lines[i]
        if l.startswith("## ") or l.startswith("!!! abstract"):
            break
        m = re.match(r"### (L[1-4])", l)
        if m:
            band = m.group(1)
        q = re.match(r"\*\*Q\d+\. (.+?)\*\*(.*)", l)
        if q and band:
            star = "⭐" in q.group(2)
            ans, i = [], i + 1
            while i < len(lines) and lines[i].strip():
                ans.append(lines[i].strip()); i += 1
            qs.append(dict(band=band, q=q.group(1), a=" ".join(ans), star=star))
            continue
        i += 1
    return title, qs

def rel(path):
    return f"../{path.parent.name}/{path.name}"

def main():
    args = sys.argv[1:]
    preamble = None
    if "--preamble" in args:
        k = args.index("--preamble"); preamble = args[k+1]; del args[k:k+2]
    out_path, title, globs = args[0], args[1], args[2:]
    chapters = []
    for g in globs:
        chapters += sorted(root.glob(g))
    data = [(p, *harvest(p)) for p in chapters]
    total = sum(len(q) for _, _, q in data)

    out = []
    if preamble:
        out.append((root / preamble).read_text().rstrip() + "\n")
    else:
        out += ["---", f"title: {title}", "status: review", "---", "", f"# {title}", ""]
    out += [f"!!! note \"Generated\"",
            f"    {total} questions harvested from {len(data)} chapters by "
            f"`tools/build-interview-bank.py`. Edit the chapters, not this page.", "",
            "!!! tip \"Use it as a self-test\"",
            "    Answer each question aloud before expanding the answer. If your answer is "
            "missing the mechanism — *why*, not just *what* — reread the chapter's Internals section.", ""]

    def render(ch_path, ch_title, q):
        return [f"**{q['q']}** {'⭐' if q['star'] else ''}  ",
                f"<small>[{ch_title}]({rel(ch_path)})</small>", "",
                "??? success \"Answer\"", f"    {q['a']}", ""]

    stars = [(p, t, q) for p, t, qs in data for q in qs if q["star"]]
    out += ["## Most frequently asked", "",
            f"The {len(stars)} questions marked high-frequency across these chapters. Start here.", ""]
    for p, t, q in stars:
        out += render(p, t, q)

    for code, name in BANDS:
        band_qs = [(p, t, q) for p, t, qs in data for q in qs if q["band"] == code]
        out += ["---", "", f"## {code} — {name}", "", f"{len(band_qs)} questions.", ""]
        for p, t, qs in data:
            chosen = [q for q in qs if q["band"] == code]
            if not chosen: continue
            out += [f"### {t}", ""]
            for q in chosen:
                out += render(p, t, q)
    (root / out_path).write_text("\n".join(out) + "\n")
    print(f"{out_path}: {total} questions from {len(data)} chapters, {len(stars)} starred")

main()
