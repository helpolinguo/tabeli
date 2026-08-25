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
    python3 tools/reading.py io 7 --half   # cut in two across the height

Output: tools/.reading/<language>-<n>[a|b].png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import block, otsu  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "tools" / ".reading"
WIDTH = 1500
AREA = 0.035          # air left around the block, as a fraction of its width


def prepared(lang, n, half=False, width_=WIDTH):
    src = ROOT / "scan" / lang / f"f-{n:03d}.jpg"
    im = Image.open(src).convert("L")
    g = np.asarray(im)
    ink = g < otsu(g)
    b = block(ink)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    # A BLANK PAGE HAS NO BLOCK. Leaves 48 and 76 of the Ido booklet are
    # blank versos: 0.1 % of ink, the grain of the paper. Detection returns
    # a degenerate box there -- a few pixels wide over the whole height --
    # and scaling that to 1500 px of width made an image of a billion
    # pixels, which PIL refused to open. We say so rather than suffer it.
    if (x1 - x0) < 0.25 * g.shape[1] or (y1 - y0) < 0.10 * g.shape[0]:
        print(f"  {lang} {n} : blank leaf (no block of ink)")
        return []
    area = int(AREA * (x1 - x0))
    x0 = max(0, x0 - area)
    y0 = max(0, y0 - area)
    x1 = min(g.shape[1] - 1, x1 + area)
    y1 = min(g.shape[0] - 1, y1 + area)
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
    OUT_PATH.mkdir(exist_ok=True)
    pieces = [(im, "")]
    if half:
        h = im.size[1]
        rec = int(h * 0.54)          # overlap: two lines in common
        pieces = [(im.crop((0, 0, im.size[0], rec)), "a"),
                    (im.crop((0, h - rec, im.size[0], h)), "b")]
    paths = []
    for piece, suf in pieces:
        w, h = piece.size
        piece = piece.resize((width_, int(h * width_ / w)),
                                 Image.LANCZOS)
        p = OUT_PATH / f"{lang}-{n:03d}{suf}.png"
        piece.save(p)
        paths.append(p)
    return paths


def hand():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    half = "--half" in sys.argv
    lang = args[0]
    start_ = int(args[1])
    end_ = int(args[2]) if len(args) > 2 else start_
    for n in range(start_, end_ + 1):
        for p in prepared(lang, n, half):
            print(p)


if __name__ == "__main__":
    hand()
