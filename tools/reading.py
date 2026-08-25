#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reading.py — prepares a leaf for READING (surveying by eye).

The raw facsimile does not read comfortably: black bands at the edge, wide
margins, low contrast on the French booklet, which is a photograph and not
a pass through a scanner. This tool crops to the ink box, restores the
contrast and outputs an image at the width asked for.

    python3 tools/reading.py io 7            # one leaf
    python3 tools/reading.py fr 9 13         # a slice
    python3 tools/reading.py io 7 --moitie   # cut in two across the height

Output: tools/.reading/<language>-<n>[a|b].png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import bloc, otsu  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "tools" / ".lekto"
LARGEUR = 1500
AIR = 0.035          # air left around the block, as a fraction of its width


def prepare(langue, n, moitie=False, largeur=LARGEUR):
    src = RACINE / "skan" / langue / f"f-{n:03d}.jpg"
    im = Image.open(src).convert("L")
    g = np.asarray(im)
    encre = g < otsu(g)
    b = bloc(encre)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    # A BLANK PAGE HAS NO BLOCK. Leaves 48 and 76 of the Ido booklet are
    # blank versos: 0.1 % of ink, the grain of the paper. Detection returns
    # a degenerate box there -- a few pixels wide over the whole height --
    # and scaling that to 1500 px of width made an image of a billion
    # pixels, which PIL refused to open. We say so rather than suffer it.
    if (x1 - x0) < 0.25 * g.shape[1] or (y1 - y0) < 0.10 * g.shape[0]:
        print(f"  {langue} {n} : feuillet vierge (aucun bloc d'encre)")
        return []
    air = int(AIR * (x1 - x0))
    x0 = max(0, x0 - air)
    y0 = max(0, y0 - air)
    x1 = min(g.shape[1] - 1, x1 + air)
    y1 = min(g.shape[0] - 1, y1 + air)
    im = im.crop((x0, y0, x1 + 1, y1 + 1))
    # The contrast is taken from the PERCENTILES and not from the extremes:
    # a speck of black and a fleck of white would suffice to cancel the
    # stretch if it were set on the minimum and the maximum.
    a = np.asarray(im, float)
    lo, hi = np.percentile(a, [2, 98])
    if hi - lo < 1:
        hi = lo + 1
    a = np.clip((a - lo) * 255.0 / (hi - lo), 0, 255)
    im = Image.fromarray(a.astype("uint8"))
    im = ImageOps.autocontrast(im, cutoff=0)
    SORTIE.mkdir(exist_ok=True)
    morceaux = [(im, "")]
    if moitie:
        h = im.size[1]
        rec = int(h * 0.54)          # overlap: two lines in common
        morceaux = [(im.crop((0, 0, im.size[0], rec)), "a"),
                    (im.crop((0, h - rec, im.size[0], h)), "b")]
    chemins = []
    for morceau, suf in morceaux:
        w, h = morceau.size
        morceau = morceau.resize((largeur, int(h * largeur / w)),
                                 Image.LANCZOS)
        p = SORTIE / f"{langue}-{n:03d}{suf}.png"
        morceau.save(p)
        chemins.append(p)
    return chemins


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    moitie = "--moitie" in sys.argv
    langue = args[0]
    debut = int(args[1])
    fin = int(args[2]) if len(args) > 2 else debut
    for n in range(debut, fin + 1):
        for p in prepare(langue, n, moitie):
            print(p)


if __name__ == "__main__":
    main()
