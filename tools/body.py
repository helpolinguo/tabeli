#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.py — measures the type size PAGE BY PAGE and writes body-<language>.tex.

    python3 tools/body.py io
    python3 tools/body.py fr

THE PROBLEM. `tools/chaso.py` finds the size that best fills the lines of
the WHOLE volume. That is an average: on the pages where the compositor of
1926 set a little tighter than his average, that size is too small, and TeX
spreads the words to fill -- hence gaping word spaces, visible to the eye
and tiring to read.

The cause is real and is not a fault of the survey. The compositor did not
hold a constant width from one gathering to the next -- worn sorts,
substitute founts -- and today's font does not have his in any case. A
single size therefore cannot fill every page.

THE MEASUREMENT. For each page, the right size is **the largest that makes
none of its lines overflow**. That is measurable: we sweep, we compile, and
TeX itself says, source line by source line, what overflows and by how
much.

One practical difficulty: TeX's log gives "in paragraph at lines A--B"
without saying which file. We therefore compile **one transcription file at
a time**, in a minimal wrapper: the line numbers there are unambiguous, and
we attach them to their page by the `\\begin{VUpage}[n]` of the file.

We ask TeX to say everything -- `\\hbadness=0`, `\\hfuzz=0pt` -- otherwise
it keeps quiet about overflows under 0.1 pt and about slightly loose lines.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")
BOX = re.compile(
    r"(Overfull|Underfull) \\hbox \(([\d.]+)pt too wide|"
    r"(Underfull) \\hbox \(badness (\d+)\)")
LINES = re.compile(r"in paragraph at lines (\d+)--(\d+)")

# The sweep: around the global size, upwards above all, since that is the
# average and half the pages want more.
GAP = [-0.30, -0.15, 0.0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90,
         1.05, 1.20, 1.35, 1.50]


def global_size(lang):
    kal = (ROOT / f"calibrate-{lang}.tex").read_text(encoding="utf-8")
    return float(re.search(r"\\VUcorps\}\{([\d.]+)pt", kal).group(1))


def pages_of_file(path):
    """[(leaf, first line, last line)] of the file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    bounds = []
    for i, l in enumerate(lines, 1):
        m = PAGE.search(l)
        if m and m.group(1):
            bounds.append((m.group(1), i))
    out = []
    for k, (f, beg) in enumerate(bounds):
        end_ = bounds[k + 1][1] - 1 if k + 1 < len(bounds) else len(lines)
        out.append((f, beg, end_))
    return out


def trial(lang, file_, size, tmp):
    """{leaf: (maximum overflow in pt, number of loose lines)}."""
    env = tmp / "essai.tex"
    env.write_text(
        f"\\documentclass{{article}}\n"
        f"\\input{{{ROOT}/calibrate-{lang}}}\n"
        f"\\renewcommand{{\\VUcorps}}{{{size:.2f}pt}}\n"
        f"\\input{{{ROOT}/preamble}}\n"
        f"\\hbadness=0 \\hfuzz=0pt\n"
        f"\\begin{{document}}\n"
        f"\\input{{{file_}}}\n"
        f"\\end{{document}}\n", encoding="utf-8")
    subprocess.run(["pdflatex", "-interaction=nonstopmode",
                    "-halt-on-error", "essai.tex"],
                   cwd=tmp, capture_output=True)
    log = (tmp / "essai.log")
    if not log.exists():
        return {}
    text_ = log.read_text(encoding="utf-8", errors="ignore")

    pages = pages_of_file(Path(file_))
    res = {f: [0.0, 0] for f, _, _ in pages}

    def page_of(line):
        for f, beg, end_ in pages:
            if beg <= line <= end_:
                return f
        return None

    for block in text_.split("\n\n"):
        mb = BOX.search(block)
        ml = LINES.search(block)
        if not mb or not ml:
            continue
        f = page_of(int(ml.group(1)))
        if f is None:
            continue
        if mb.group(1) == "Overfull":
            res[f][0] = max(res[f][0], float(mb.group(2)))
        else:
            res[f][1] += 1
    return res


def hand():
    lang = sys.argv[1] if len(sys.argv) > 1 else "io"
    base = global_size(lang)
    under = "io" if lang == "io" else "fr"
    files_ = sorted((ROOT / "text" / under).glob("*.tex"))

    # {leaf: {size: (overflow, loose)}}
    survey = {}
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for f in files_:
            for e in GAP:
                c = round(base + e, 2)
                for leaf, (beg, lach) in trial(lang, f, c, tmp).items():
                    survey.setdefault(leaf, {})[c] = (beg, lach)
            print(f"  {f.name}", flush=True)

    lines = []
    choisis = {}
    for leaf, by_size in survey.items():
        # The largest size WITH NO OVERFLOW. A page all of whose values
        # overflow (which happens when a single line of the survey is a little
        # too long) keeps the smallest trial: better a loose page than a line
        # that leaves the measure.
        without = [c for c, (beg, _) in by_size.items() if beg == 0.0]
        c = max(without) if without else min(by_size)
        choisis[leaf] = c
        if abs(c - base) > 0.001:
            lines.append(f"\\VUkorpoPage{{{leaf}}}{{{c:.2f}pt}}")

    header = (
        f"% body-{lang}.tex — the size proper to each page.\n"
        f"% FILE PRODUCED by tools/body.py: do not edit it by hand. For\n"
        f"% each page, the largest size that makes none of its lines\n"
        f"% overflow. Global size: {base:.2f}pt.\n"
        f"% {len(lines)} pages out of {len(choisis)} receive a value of\n"
        f"% their own; the others keep the global size.\n\n")
    (ROOT / f"body-{lang}.tex").write_text(
        header + "\n".join(lines) + "\n", encoding="utf-8")

    import statistics
    v = sorted(choisis.values())
    print(f"\nbody-{lang}.tex : {len(lines)}/{len(choisis)} pages "
          f"have a size of their own")
    print(f"  global size {base:.2f}pt ; per page: "
          f"min {v[0]:.2f}  median {statistics.median(v):.2f}  "
          f"max {v[-1]:.2f}")


if __name__ == "__main__":
    hand()
