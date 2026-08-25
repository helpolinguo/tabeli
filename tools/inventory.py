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

RACINE = Path(__file__).resolve().parent.parent
SKAN = RACINE / "skan"

# Binarisation threshold. Both scans are greyscale; the paper of the Ido
# booklet is speckled, that of the French booklet dirty and cockled. A
# fixed threshold on 255 would bite into the grain: we take Otsu's
# threshold, computed page by page.
def otsu(g):
    hist = np.bincount(g.ravel(), minlength=256).astype(float)
    tot = hist.sum()
    som = np.dot(np.arange(256), hist)
    somB = 0.0
    wB = 0.0
    mx = -1.0
    seuil = 128
    for t in range(256):
        wB += hist[t]
        if wB == 0:
            continue
        wF = tot - wB
        if wF == 0:
            break
        somB += t * hist[t]
        mB = somB / wB
        mF = (som - somB) / wF
        v = wB * wF * (mB - mF) ** 2
        if v > mx:
            mx = v
            seuil = t
    return seuil


def profils(chemin, dpi):
    """Returns (ink, height, width, dpi) — ink = boolean array."""
    im = Image.open(chemin).convert("L")
    g = np.asarray(im)
    s = otsu(g)
    encre = g < s
    return encre


def _plage_centrale(profil, seuil, ecart):
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
    plein = profil > seuil
    n = len(plein)
    plages = []
    i = 0
    while i < n:
        if plein[i]:
            j = i
            k = i
            while j < n:
                if plein[j]:
                    k = j
                    j += 1
                elif j - k <= ecart:
                    j += 1
                else:
                    break
            plages.append((i, k))
            i = j
        else:
            i += 1
    if not plages:
        return None
    mil = n // 2
    dedans = [p for p in plages if p[0] <= mil <= p[1]]
    if dedans:
        return max(dedans, key=lambda p: p[1] - p[0])
    return max(plages, key=lambda p: p[1] - p[0])


def bloc(encre, marge_bruit=0.010, ecart=60):
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
    h, w = encre.shape
    colonne = encre.sum(0) / h
    px = _plage_centrale(colonne, marge_bruit, ecart)
    if px is None:
        return None
    x0, x1 = px
    bande = encre[:, x0:x1 + 1]
    ligne = bande.sum(1) / max(1, x1 - x0 + 1)
    ys = np.where(ligne > marge_bruit)[0]
    if len(ys) == 0:
        return None
    return int(x0), int(ys[0]), int(x1), int(ys[-1])


def lignes_de_base(encre, x0, x1, y0, y1, seuil=0.02):
    """Ordinates of the baselines.

    The baseline is not the top of a line: the top depends on the ascenders
    the line carries, hence on the text. The BOTTOM of a line's mass of
    ink, on the other hand, does not move -- save for descenders, which are
    in the minority. We therefore take, for each band of ink, the ordinate
    at which the profile falls back below the threshold.
    """
    bande = encre[y0:y1 + 1, x0:x1 + 1]
    prof = bande.sum(1) / max(1, x1 - x0)
    plein = prof > seuil
    bases = []
    dans = False
    for i, p in enumerate(plein):
        if p and not dans:
            dans = True
        elif not p and dans:
            dans = False
            bases.append(y0 + i)
    if dans:
        bases.append(y1)
    return bases


def pas(bases):
    if len(bases) < 4:
        return None
    d = np.diff(bases)
    d = d[(d > 0.6 * np.median(d)) & (d < 1.6 * np.median(d))]
    return float(np.median(d)) if len(d) else None


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    debut = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    fin = int(sys.argv[3]) if len(sys.argv) > 3 else 999
    dossier = SKAN / langue
    fichiers = sorted(dossier.glob("f-*.jpg"))
    out = {}
    for f in fichiers:
        n = int(f.stem.split("-")[1])
        if not (debut <= n <= fin):
            continue
        encre = profils(f, None)
        h, w = encre.shape
        b = bloc(encre)
        if b is None:
            out[n] = {"vide": True, "px": [w, h]}
            continue
        x0, y0, x1, y1 = b
        bases = lignes_de_base(encre, x0, x1, y0, y1)
        out[n] = {
            "px": [w, h],
            "bloc": [x0, y0, x1, y1],
            "largeur": x1 - x0 + 1,
            "hauteur": y1 - y0 + 1,
            "lignes": len(bases),
            "bases": bases,
            "pas": pas(bases),
        }
        print(f"{n:3d}  bloc {x0:5d},{y0:5d} → {x1:5d},{y1:5d}"
              f"  l={x1-x0+1:5d}  lignes={len(bases):3d}"
              f"  pas={out[n]['pas']}")
    (RACINE / "tools" / f"inv-{langue}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
