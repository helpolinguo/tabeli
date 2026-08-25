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
from inventory import bloc, otsu  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
# X-height of the composing font, as a fraction of the size.
# Measured on XCharter: \fontcharht with the character "x".
XCHARTER = 0.481


def hauteur_x_page(chemin):
    g = np.asarray(Image.open(chemin).convert("L"))
    encre = g < otsu(g)
    b = bloc(encre)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    if (x1 - x0) < 0.25 * g.shape[1]:
        return []
    bande = encre[y0:y1 + 1, x0:x1 + 1]
    prof = bande.sum(1).astype(float)
    seuil = 0.04 * (x1 - x0)
    plein = prof > seuil

    # Division into bands of line.
    hauteurs = []
    i = 0
    n = len(plein)
    while i < n:
        if not plein[i]:
            i += 1
            continue
        j = i
        while j < n and plein[j]:
            j += 1
        seg = prof[i:j]
        if len(seg) >= 8:
            # THE PLATEAU, AND NOT THE WHOLE BAND. The band runs from the top
            # of the ascenders to the bottom of the descenders; the plateau is
            # where the ink is dense, that is the body of the letters. We take
            # it at half the height of the maximum: lower, we catch the
            # ascenders; higher, we clip the descenders.
            dedans = seg > 0.5 * seg.max()
            k = np.where(dedans)[0]
            if len(k):
                # The plateau must be in one piece: two lines joined by an
                # ascender would give two.
                h = k[-1] - k[0] + 1
                if 4 <= h <= 0.75 * len(seg):
                    hauteurs.append(h)
        i = j
    return hauteurs


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    inv = json.loads((RACINE / "tools" / f"inv-{langue}.json")
                     .read_text(encoding="utf-8"))
    pleines = sorted(int(k) for k, v in inv.items()
                     if not v.get("vide") and v.get("lignes", 0) >= 35)
    # One sample suffices: the measurement is taken over thousands of
    # lines, not over pages.
    echantillon = pleines[::max(1, len(pleines) // 20)][:20]

    toutes = []
    par_page = {}
    for n in echantillon:
        h = hauteur_x_page(RACINE / "skan" / langue / f"f-{n:03d}.jpg")
        if h:
            par_page[n] = float(np.median(h))
            toutes.extend(h)

    if not toutes:
        print("aucune mesure")
        return

    # THE X-HEIGHT IS RELATIVE TO THE MEASURE, not to millimetres: the
    # French facsimile is a photograph, its scale changes from one page to
    # another, and a height in pixels means nothing there outside its page.
    # The RATIO, on the other hand, is invariant.
    rapports = []
    for n, h in par_page.items():
        rapports.append(h / inv[str(n)]["largeur"])
    r = float(np.median(rapports))

    import re as _re
    kal = (RACINE / f"kalibro-{langue}.tex").read_text(encoding="utf-8")
    largeur_mm = float(_re.search(
        r"\\VUtexteLargeur\}\{([\d.]+)mm", kal).group(1))
    hx_mm = r * largeur_mm
    hx_pt = hx_mm / (25.4 / 72.27)
    corps = hx_pt / XCHARTER

    print(f"langue            : {langue}")
    print(f"pages echantillon : {len(par_page)}  ({len(toutes)} lignes)")
    print(f"hauteur d'x       : {np.median(toutes):.2f} px "
          f"(ecart-type {np.std(toutes):.2f})")
    print(f"  / justification : {r:.5f}")
    print(f"justification     : {largeur_mm:.2f} mm")
    print(f"hauteur d'x       : {hx_mm:.3f} mm = {hx_pt:.2f} pt")
    print()
    print(f"CORPS DEDUIT      : {corps:.2f} pt "
          f"(hauteur d'x XCharter = {XCHARTER} du corps)")


if __name__ == "__main__":
    main()
