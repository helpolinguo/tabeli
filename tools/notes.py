#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notes.py — do the footnotes keep their place?

    python3 tools/notes.py

TWO POSSIBLE FAULTS, AND BOTH ARE NEEDED.

The first is COLLISION: the note prints over the text. It came from
\\VUnotes laying its note in a box of NULL HEIGHT, set on the foot of the
block: the note fell right, and it pushed nothing. On a page whose text
descends to the foot, the two therefore printed one over the other -- seven
pages of the Ido booklet and one of the French. The note is now deferred
until the page closes and enters the flow after the last paragraph; the
overlap has become impossible by construction.

The second is OVERFLOW: the note passes below the edge of the leaf. It
comes not from the macro but from the page: six leaves carry, in the
survey, more matter than the sheet holds -- the text there already fills
the block, and the note has only the bottom margin, which does not suffice.
The first fault HID it: as long as the note printed within the text, it
never left the paper. Correcting the first brought it to light.

This check does not decide those six pages: it names them. Deciding them
needs the facsimile of the booklet, which this repository does not contain
-- we have only the sixteen plates.


HOW THE NOTE IS SEPARATED FROM THE TEXT: by the SIZE, not by the position.
Measured on both booklets: the note size is 0.79 times the text size --
9.09 against 10.93 in Ido, 8.45 against 10.70 in French -- while the
superscript of a reference is 0.70. The window [0.74; 0.85] therefore
separates them cleanly, and it is the measurement that fixes it.

And the LIST OF PAGES comes from the survey, not from the PDF: we look for
a note only where \\VUnotes lays one. A heuristic on size alone took
superscripts and small capitals for notes, and returned eighty-two pages
out of ninety-six.
"""

import glob
import io as _io
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MM = 72.0 / 25.4
VOLUMES = (("io", "tabeli.pdf"), ("fr", "tableaux.pdf"))


def leaves_with_notes(lg):
    """[(leaf, PDF page)] where the survey lays a note.

    AND THE LEAF NUMBER IS NOT THE PDF PAGE NUMBER. That is what this check
    believed all this time -- "one page of the facsimile, one page of the
    PDF" -- and it is false: the Ido booklet skips TWO BLANK VERSOS, leaves
    48 and 76, which are not set. The PDF page therefore falls one leaf
    behind from 49 on, two from 77 on, and the check was looking elsewhere.
    Leaves 49, 57, 85, 87, 89 and 106 -- six of the volume's ten pages with
    notes -- were never checked: we measured pages without notes in their
    place, found "no note", and said nothing.

    The PDF page is the RANK of the page in the document, and nothing else:
    the files are read in the order main-<lg>.tex calls them, which is
    their alphabetical order.
    """
    out = []
    row = 0
    for p in sorted(glob.glob(str(ROOT / "text" / lg / "*.tex"))):
        t = _io.open(p, encoding="utf-8").read()
        for m in re.finditer(r"\\begin\{VUpage\}\[(\d+)\][^\n]*\n(.*?)\\end\{VUpage\}",
                             t, re.S):
            row += 1
            size = "\n".join(l for l in m.group(2).split("\n")
                              if not l.startswith("%"))
            if "\\VUnotes" in size:
                out.append((int(m.group(1)), row))
    return sorted(set(out))


def lines(pdf, page):
    x = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf), str(page)],
                       capture_output=True, text=True).stdout
    r = ET.fromstring(x)
    top = float(r.find("page").get("height"))
    out = []
    for ln in r.iter("line"):
        f = ln.find("font")
        if f is None:
            continue
        t = float(f.get("size"))
        if t < 1.0:            # the provenance watermark
            continue
        out.append((t, [float(v) for v in ln.get("bbox").split()]))
    return top, out


def check_(lg, pdf):
    pdf = ROOT / pdf
    if not pdf.exists():
        print(f"  {pdf.name} : absent, rien a controler")
        return 0, 0
    touches = overflows = 0
    for fe, pg in leaves_with_notes(lg):
        top, ls = lines(pdf, pg)
        if len(ls) < 4:
            continue
        size = statistics.median(t for t, _ in ls)
        note = [b for t, b in ls if 0.74 * size <= t <= 0.85 * size]
        text_ = [b for t, b in ls if t > 0.88 * size]
        if not note:
            continue
        for bn in note:
            for bc in text_:
                iy = min(bn[3], bc[3]) - max(bn[1], bc[1])
                ix = min(bn[2], bc[2]) - max(bn[0], bc[0])
                if iy > 1.0 and ix > 5.0:
                    touches += 1
                    print(f"  NOTE SUR LE TEXTE  {pdf.name} f{fe} (page {pg})")
                    break
            else:
                continue
            break
        bottom = max(b[3] for b in note)
        if bottom > top:
            overflows += 1
            print(f"  NOTE HORS DU FEUILLET  {pdf.name} f{fe} (page {pg}) : "
                  f"{(bottom - top) / MM:.1f} mm sous le bord — cette page porte "
                  f"plus de matiere que la feuille n'en tient")
    return touches, overflows


def hand():
    h = d = 0
    for lg, pdf in VOLUMES:
        a, b = check_(lg, pdf)
        h += a
        d += b
    print()
    print(f"  notes sur le texte : {h}   notes hors du feuillet : {d}")
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(hand())
