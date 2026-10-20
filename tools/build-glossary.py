#!/usr/bin/env python3
"""Build Appendix F: the hand-written glossary plus a JEP index generated
from the tables in Appendix A, so the two cannot drift apart."""
import pathlib, re
root = pathlib.Path(__file__).resolve().parent.parent
glossary = (root/"tools/templates/f-glossary.md").read_text().rstrip()
matrix = (root/"docs/appendix/a-jep-matrix.md").read_text().splitlines()

rows, release = {}, None
for line in matrix:
    m = re.match(r"### Java (\d+)(?:–(\d+))?", line)
    if m:
        release = m.group(1) if not m.group(2) else f"{m.group(1)}–{m.group(2)}"
        continue
    m = re.match(r"\| ([\d, ]+) \| (.+?) \| (.+?) \|(?: (\d+) \|)? (.+?) \|$", line)
    if not m or release is None:
        continue
    nums, feature, status, rel, chapter = m.groups()
    feature = feature.replace("**", "")
    status = status.replace("**", "")
    rel = rel or release
    for n in re.findall(r"\d+", nums):
        rows.setdefault(int(n), (feature, rel, status, chapter))

out = [glossary, "", "---", "", "## JEP index", "",
       "Every JEP in [Appendix A](a-jep-matrix.md), by number. Generated from Appendix A "
       "by `tools/build-glossary.py` — edit A, not this table.", "",
       "| JEP | Feature | Release | Status | Chapter |", "|---|---|---|---|---|"]
for n in sorted(rows):
    f, r, s, c = rows[n]
    out.append(f"| {n} | {f} | {r} | {s} | {c} |")
(root/"docs/appendix/f-glossary.md").write_text("\n".join(out) + "\n")
print(f"glossary + {len(rows)} JEPs indexed")
