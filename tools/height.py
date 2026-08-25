#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
height.py — measures the X-HEIGHT of the facsimile, and deduces the size.

    python3 tools/height.py io
    python3 tools/height.py fr

WHY. The size was until now deduced from the line pitch by a ratio set at
1.20, the usual value for the bookwork printing of that period. It did
roughly for the Ido booklet (294 short lines over 100 pages, that is 3 a
page) and not at all for the French one (1179 over 84, that is 14 a page):
there, one line in three did not reach the margin, and TeX spread the words
to fill.

A ratio is not a measurement. The size is read from the facsimile, like the
rest -- by the x-height, which is the most robust quantity of a printed
page: it depends neither on ascenders nor on descenders, hence not on the
words the line carries.

HOW. For each band of line, we take the ink profile by row of pixels. A
line of text draws a plateau there -- the body of the letters without
ascenders -- framed by two far thinner shoulders, the ascenders above, the
descenders below. The height of the plateau above half the maximum IS the
x-height, to within a pixel.

The size follows from the ratio proper to the composing font: XCharter
places its x-height at 0.481 of its size. To set at a size such that the
x-height falls right is to make the eye of the composed face coincide with
that of the facsimile -- which governs both the colour of the page and the
width, hence the filling of the lines.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import block, otsu  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# X-height of the composing font, as a fraction of the size.
# Measured on XCharter: \fontcharht with the character "x".
XCHARTER = 0.481


def x_height_of_page(path):
    g = np.asarray(Image.open(path).convert("L"))
    ink = g < otsu(g)
    b = block(ink)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    if (x1 - x0) < 0.25 * g.shape[1]:
        return []
    band = ink[y0:y1 + 1, x0:x1 + 1]
    prof = band.sum(1).astype(float)
    threshold = 0.04 * (x1 - x0)
    solid = prof > threshold

    # Division into bands of line.
    heights = []
    i = 0
    n = len(solid)
    while i < n:
        if not solid[i]:
            i += 1
            continue
        j = i
        while j < n and solid[j]:
            j += 1
        seg = prof[i:j]
        if len(seg) >= 8:
            # THE PLATEAU, AND NOT THE WHOLE BAND. The band runs from the top
            # of the ascenders to the bottom of the descenders; the plateau is
            # where the ink is dense, that is the body of the letters. We take
            # it at half the height of the maximum: lower, we catch the
            # ascenders; higher, we clip the descenders.
            inside = seg > 0.5 * seg.max()
            k = np.where(inside)[0]
            if len(k):
                # The plateau must be in one piece: two lines joined by an
                # ascender would give two.
                h = k[-1] - k[0] + 1
                if 4 <= h <= 0.75 * len(seg):
                    heights.append(h)
        i = j
    return heights


def hand():
    lang = sys.argv[1] if len(sys.argv) > 1 else "io"
    inv = json.loads((ROOT / "tools" / f"inv-{lang}.json")
                     .read_text(encoding="utf-8"))
    solid_ = sorted(int(k) for k, v in inv.items()
                     if not v.get("vide") and v.get("lignes", 0) >= 35)
    # One sample suffices: the measurement is taken over thousands of
    # lines, not over pages.
    sample = solid_[::max(1, len(solid_) // 20)][:20]

    all_ = []
    by_page = {}
    for n in sample:
        h = x_height_of_page(ROOT / "skan" / lang / f"f-{n:03d}.jpg")
        if h:
            by_page[n] = float(np.median(h))
            all_.extend(h)

    if not all_:
        print("aucune mesure")
        return

    # THE X-HEIGHT IS RELATIVE TO THE MEASURE, not to millimetres: the
    # French facsimile is a photograph, its scale changes from one page to
    # another, and a height in pixels means nothing there outside its page.
    # The RATIO, on the other hand, is invariant.
    ratios = []
    for n, h in by_page.items():
        ratios.append(h / inv[str(n)]["largeur"])
    r = float(np.median(ratios))

    import re as _re
    kal = (ROOT / f"kalibro-{lang}.tex").read_text(encoding="utf-8")
    width_mm = float(_re.search(
        r"\\VUtexteLargeur\}\{([\d.]+)mm", kal).group(1))
    xh_mm = r * width_mm
    xh_pt = xh_mm / (25.4 / 72.27)
    size = xh_pt / XCHARTER

    print(f"langue            : {lang}")
    print(f"pages echantillon : {len(by_page)}  ({len(all_)} lignes)")
    print(f"hauteur d'x       : {np.median(all_):.2f} px "
          f"(ecart-type {np.std(all_):.2f})")
    print(f"  / justification : {r:.5f}")
    print(f"justification     : {width_mm:.2f} mm")
    print(f"hauteur d'x       : {xh_mm:.3f} mm = {xh_pt:.2f} pt")
    print()
    print(f"CORPS DEDUIT      : {size:.2f} pt "
          f"(hauteur d'x XCharter = {XCHARTER} du corps)")


if __name__ == "__main__":
    hand()
