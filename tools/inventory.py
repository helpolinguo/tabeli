#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inventory.py — surveys, leaf by leaf, the GEOMETRY of each page of the two
facsimiles: ink box, folio, first and last baseline, line pitch.

The principle is that of the "Kompleta Gramatiko" project: no value in the
LaTeX preamble is invented, each comes from a median taken over all the
full pages.

    python3 tools/inventory.py io          # the 116 Ido leaves
    python3 tools/inventory.py fr 1 20     # a slice

Output: tools/inventory-<language>.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "scan"

# Binarisation threshold. Both scans are greyscale; the paper of the Ido
# booklet is speckled, that of the French booklet dirty and cockled. A
# fixed threshold on 255 would bite into the grain: we take Otsu's
# threshold, computed page by page.
def otsu(g):
    hist = np.bincount(g.ravel(), minlength=256).astype(float)
    tot = hist.sum()
    sm = np.dot(np.arange(256), hist)
    somB = 0.0
    wB = 0.0
    mx = -1.0
    threshold = 128
    for t in range(256):
        wB += hist[t]
        if wB == 0:
            continue
        wF = tot - wB
        if wF == 0:
            break
        somB += t * hist[t]
        mB = somB / wB
        mF = (sm - somB) / wF
        v = wB * wF * (mB - mF) ** 2
        if v > mx:
            mx = v
            threshold = t
    return threshold


def profiles(path, dpi):
    """Returns (ink, height, width, dpi) — ink = boolean array."""
    im = Image.open(path).convert("L")
    g = np.asarray(im)
    s = otsu(g)
    ink = g < s
    return ink


def _central_range(profile, threshold, gap):
    """Longest continuous run above the threshold, gaps of fewer than `gap`
    pixels ignored, and which contains the middle of the profile.

    THE EDGE OF THE SCAN IS NOT INK. Both facsimiles carry, on one edge or
    the other, a black band -- the shadow of the binding for the Ido
    booklet, the ground of the platen for the French one. Taken as it is,
    the ink box therefore ran from one edge of the image to the other and
    ALL the measurements of the text width were wrong. We keep only the run
    that contains the middle of the page: the edge band is separated from
    it by the white margin, wider than `gap`.
    """
    solid = profile > threshold
    n = len(solid)
    ranges = []
    i = 0
    while i < n:
        if solid[i]:
            j = i
            k = i
            while j < n:
                if solid[j]:
                    k = j
                    j += 1
                elif j - k <= gap:
                    j += 1
                else:
                    break
            ranges.append((i, k))
            i = j
        else:
            i += 1
    if not ranges:
        return None
    mil = n // 2
    inside = [p for p in ranges if p[0] <= mil <= p[1]]
    if inside:
        return max(inside, key=lambda p: p[1] - p[0])
    return max(ranges, key=lambda p: p[1] - p[0])


def block(ink, noise_margin=0.010, gap=60):
    """Box of the ink block, the edge of the scan set aside.

    In TWO stages, and the order matters. The columns first: it is the
    width that carries the measure, and it is on the lateral edges that the
    black bands lie. The rows AFTERWARDS, measured on the retained columns
    alone -- without which the black edge, which runs the whole height,
    fills the vertical profile and the box takes the whole page. The
    central-run test serves only for the columns: applied to the rows, it
    cut the page at the first slightly wide white window (title space, end
    of section) and the box began in the middle of the text.
    """
    h, w = ink.shape
    column = ink.sum(0) / h
    px = _central_range(column, noise_margin, gap)
    if px is None:
        return None
    x0, x1 = px
    band = ink[:, x0:x1 + 1]
    line = band.sum(1) / max(1, x1 - x0 + 1)
    ys = np.where(line > noise_margin)[0]
    if len(ys) == 0:
        return None
    return int(x0), int(ys[0]), int(x1), int(ys[-1])


def baselines(ink, x0, x1, y0, y1, threshold=0.02):
    """Ordinates of the baselines.

    The baseline is not the top of a line: the top depends on the ascenders
    the line carries, hence on the text. The BOTTOM of a line's mass of
    ink, on the other hand, does not move -- save for descenders, which are
    in the minority. We therefore take, for each band of ink, the ordinate
    at which the profile falls back below the threshold.
    """
    band = ink[y0:y1 + 1, x0:x1 + 1]
    prof = band.sum(1) / max(1, x1 - x0)
    solid = prof > threshold
    bases = []
    in_ = False
    for i, p in enumerate(solid):
        if p and not in_:
            in_ = True
        elif not p and in_:
            in_ = False
            bases.append(y0 + i)
    if in_:
        bases.append(y1)
    return bases


def pas(bases):
    if len(bases) < 4:
        return None
    d = np.diff(bases)
    d = d[(d > 0.6 * np.median(d)) & (d < 1.6 * np.median(d))]
    return float(np.median(d)) if len(d) else None


def hand():
    lang = sys.argv[1] if len(sys.argv) > 1 else "io"
    start_ = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_ = int(sys.argv[3]) if len(sys.argv) > 3 else 999
    folder = SCAN / lang
    files_ = sorted(folder.glob("f-*.jpg"))
    out = {}
    for f in files_:
        n = int(f.stem.split("-")[1])
        if not (start_ <= n <= end_):
            continue
        ink = profiles(f, None)
        h, w = ink.shape
        b = block(ink)
        if b is None:
            out[n] = {"vide": True, "px": [w, h]}
            continue
        x0, y0, x1, y1 = b
        bases = baselines(ink, x0, x1, y0, y1)
        out[n] = {
            "px": [w, h],
            "bloc": [x0, y0, x1, y1],
            "largeur": x1 - x0 + 1,
            "hauteur": y1 - y0 + 1,
            "lignes": len(bases),
            "bases": bases,
            "pas": pas(bases),
        }
        print(f"{n:3d}  block {x0:5d},{y0:5d} → {x1:5d},{y1:5d}"
              f"  w={x1-x0+1:5d}  lines={len(bases):3d}"
              f"  step={out[n]['pas']}")
    (ROOT / "tools" / f"inv-{lang}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    hand()
