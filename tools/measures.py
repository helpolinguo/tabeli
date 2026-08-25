#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measures.py — draws from tools/inventory-<language>.json the CONSTANTS of
the LaTeX preamble: measure, line pitch, scale of the scan.

    python3 tools/measures.py io
    python3 tools/measures.py fr

Nothing here is invented: every constant is a median, together with its
standard deviation and the number of pages it is taken over. Short pages
(fewer than `MIN_LINES` lines) are set aside: a title page or the end of a
section measures neither the text width nor the pitch.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MIN_LINES = 25


def load_(lang):
    p = ROOT / "tools" / f"inventory-{lang}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def med(v):
    v = np.asarray([x for x in v if x is not None], float)
    return float(np.median(v)), float(np.std(v)), len(v)


def hand():
    lang = sys.argv[1] if len(sys.argv) > 1 else "io"
    inv = load_(lang)
    solid_ = {int(k): v for k, v in inv.items()
               if not v.get("vide") and v.get("lignes", 0) >= MIN_LINES}
    widths = [v["largeur"] for v in solid_.values()]
    pas = [v["pas"] for v in solid_.values() if v.get("pas")]

    lm, ls, ln = med(widths)
    pm, ps, pn = med(pas)

    print(f"langue          : {lang}")
    print(f"pages kept      : {ln} (>= {MIN_LINES} lines)")
    print(f"justification   : {lm:.1f} px   (ecart-type {ls:.1f})")
    print(f"line step       : {pm:.2f} px   (standard deviation {ps:.2f})")
    print(f"lines per page  : {int(np.median([v['lignes'] for v in solid_.values()]))}")
    print()
    print("THE SCAN'S SCALE IS NOT GIVEN BY THE FILE.")
    print("Both facsimiles are photographs: the number of pixels")
    print("per millimetre in them is not the one the PDF declares.")
    print("It is got by laying down ONE physical measurement — the")
    print("justification of the printed book, taken with a rule on the")
    print("copy — and then dividing. As long as that measurement is")
    print("missing, the table below gives the scale that would follow")
    print("from a few justifications usual for a 16mo of the period.")
    print()
    print("  justification    px/mm    size deduced (step = 1.20 x size)")
    for mm in (68, 70, 72, 74, 76, 78, 80):
        pxmm = lm / mm
        size_pt = (pm / pxmm) / 25.4 * 72 / 1.20
        print(f"      {mm} mm       {pxmm:6.2f}      {size_pt:5.2f} pt")


if __name__ == "__main__":
    hand()
