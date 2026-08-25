#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
images.py — extracts from the facsimile the parts that are NOT composition:
the woodcut of wall table no. 12, the ornamental frame on the back cover of
the French booklet.

    python3 tools/images.py io 111 --haut 0.06 --bas 0.50 --nom tabelo-12
    python3 tools/images.py fr 96  --nom kadro-fr

WHAT IS EXTRACTED, AND WHY NOT OTHERWISE. All the rest of the volume is
SET: one line of the facsimile becomes one line of source, and the font
renders it. A woodcut and an Art Nouveau border are not. To reproduce them
in type would be to invent them; to omit them, as was first done -- a
`\\VUsaut` and a comment -- is to publish a page that lies about what it
showed.

We therefore take them from the scan, at their measured place, and lay them
in the page at their surveyed size. It is the only place in the project
where the image of the facsimile enters the PDF, and it is justified by the
nature of the object: it is not text.

THE CLEANING IS MINIMAL, and that is intended. We restore the contrast on
the percentiles -- as reading.py does -- and do nothing else: no denoising,
no thresholding. A woodcut passed through black and white loses its greys,
and the grain of 1926 paper is part of what is being reproduced.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import block, otsu  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "ornaments"


def extract_(lang, n, top, bottom, name_, width_=1600):
    src = ROOT / "skan" / lang / f"f-{n:03d}.jpg"
    im = Image.open(src).convert("L")
    g = np.asarray(im)

    # The crop is taken from the INK BOX and not from the image: the edge of
    # the scan varies from one leaf to another, and a fraction of the whole
    # image would not designate the same thing on two pages.
    b = block(g < otsu(g))
    if b is None:
        print("aucun bloc d'encre")
        return None
    x0, y0, x1, y1 = b
    h = y1 - y0
    y_a = int(y0 + top * h)
    y_b = int(y0 + bottom * h)
    area = int(0.02 * (x1 - x0))
    cut = im.crop((max(0, x0 - area), y_a,
                     min(g.shape[1], x1 + area), y_b))

    a = np.asarray(cut, float)
    lo, hi = np.percentile(a, [1, 99])
    if hi - lo < 1:
        hi = lo + 1
    a = np.clip((a - lo) * 255.0 / (hi - lo), 0, 255)
    cut = Image.fromarray(a.astype("uint8"))

    w, hh = cut.size
    if w > width_:
        cut = cut.resize((width_, int(hh * width_ / w)), Image.LANCZOS)

    OUT_PATH.mkdir(exist_ok=True)
    p = OUT_PATH / f"{name_}.png"
    cut.save(p, optimize=True)
    w2, h2 = cut.size
    # The width/height ratio OF THE AREA TAKEN, relative to the measure: that
    # is what allows it to be laid in the page at the size it occupies on the
    # paper.
    part = (x1 - x0 + 2 * area) / (x1 - x0)
    print(f"{p}  ({w2}x{h2} px)")
    print(f"  largeur = {part:.3f} x la justification")
    print(f"  hauteur = {(y_b - y_a) / (x1 - x0 + 2 * area):.4f} "
          f"x sa propre largeur")
    return p


def hand():
    ap = argparse.ArgumentParser()
    ap.add_argument("langue")
    ap.add_argument("feuillet", type=int)
    ap.add_argument("--haut", type=float, default=0.0)
    ap.add_argument("--bas", type=float, default=1.0)
    ap.add_argument("--nom", default="ornamento")
    ap.add_argument("--largeur", type=int, default=1600)
    a = ap.parse_args()
    extract_(a.lang, a.leaf, a.top, a.bottom, a.name_, a.width_)


if __name__ == "__main__":
    hand()
