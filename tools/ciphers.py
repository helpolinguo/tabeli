#!/usr/bin/env python3
# ===================================================================
#  ciphers.py — learn the facsimile's figures, and use them to PROPOSE
#               to the eye what is still missing.
#
#  THE PROBLEM. tools/ciphers.npz holds ten models of figures drawn from
#  the line layer of the colourised PDF: a stencil, two tones, clean
#  outlines. The sixteen plates having been redone from their facsimiles,
#  that layer is no longer what one looks at; the ink there is grey, the
#  stems bleed, the hairlines fade, and the reader in numbering.py, which
#  compares shapes, recognises nothing any more: on table 14 it read
#  seventy-six numbers on the stencil, it reads ten on the grey.
#
#  WHAT CAN BE LEARNT WITHOUT DRAWING ANYTHING. Fifteen hundred numbers
#  are already placed, verified one by one, on the grey plates
#  themselves. Each is a LABELLED specimen of the fount to be
#  recognised, in the very medium in which it must be recognised. We cut
#  them out — seven hundred and sixty-one separate cleanly into figures,
#  which makes fourteen hundred specimens, at least eighty-four per class
#  — we group them by shape, and the centres of the groups are the
#  models.
#
#  AND WHAT THAT IS WORTH, MEASURED. With these models, the reader
#  re-reads the sixteen plates: 442 numbers found in their place, 132
#  laid ELSEWHERE, 45 new numbers. One in four is wrong. That is too many
#  to enter numbers.json on its own — the rule of the house is that a
#  number without a close-up is better than a close-up on something else
#  — and that is why this reader DOES NOT RUN in the chain. Raising the
#  threshold does nothing: at 0.86 the reading falls to 246 right for 173
#  wrong; the measurement has been made.
#
#  HENCE ITS USE: it does not decide, it PROPOSES. We ask it only for the
#  numbers STILL MISSING — the rest are already judged — we cut out what
#  it shows, and the eye keeps or throws away. First batch: forty-five
#  proposals, twenty-six good. The other nineteen were either drawing
#  taken for a figure, or a piece of a neighbouring number: "6" read in
#  36, "5" in 56, "3" in 31 and in 13. What is kept enters
#  plates/manual.json, by the same door as what the eye finds on its own.
#
#  USAGE
#      python3 tools/ciphers.py aprendar     # rebuilds ciphers-grey.npz
#      python3 tools/ciphers.py proponar     # proposes, and cuts out
#      python3 tools/ciphers.py proponar t14-apar-1
#
#  The proofing sheet comes out in plates/proposals.png, and the proposed
#  places in plates/proposals.json — to be copied by hand into manual.json,
#  those that are kept.
# ===================================================================

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbering as N                                          # noqa: E402

ROOT = N.ROOT
MODELS = ROOT / "tools" / "ciphers-grey.npz"
PROPOSALS = ROOT / "plates" / "proposals.png"
PLACES = ROOT / "plates" / "proposals.json"
GROUPS = 8            # groups by class
RARE = 0.05            # a group below this weight does not make a model


def harvest():
    """Cuts out, on the grey plates, the figures of the sure numbers."""
    cat = json.loads((ROOT / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    rec = {str(c): [] for c in range(10)}
    tot = ok = 0
    for key in sorted(cat):
        if not N.redone(key):
            continue
        ink_ = (N.enko(key) > 128).astype(np.uint8)
        ht, la = ink_.shape
        e = cat[key]
        h = e["corpo"]
        for q, v in e["numeri"].items():
            txt = str(N.unkey(q)[1])
            cx, cy = (v[0] + v[2] / 2) * la, (v[1] + v[3] / 2) * ht
            L, m = v[2] * la, 8
            x0, x1 = max(0, int(cx - L / 2 - m)), min(la, int(cx + L / 2 + m))
            y0, y1 = max(0, int(cy - h * 0.8)), min(ht, int(cy + h * 0.8))
            tot += 1
            n, lab, st, cen = cv2.connectedComponentsWithStats(
                ink_[y0:y1, x0:x1], 8)
            # A FIGURE IS A COMPONENT THE SIZE OF A FIGURE.
            # We learn only from numbers that separate of themselves into as
            # many pieces as they have figures, all sitting on the same
            # baseline: that is the only way to be sure of what one is
            # labelling.
            comp = [i for i in range(1, n)
                    if 0.60 * h <= st[i, 3] <= 1.5 * h
                    and 0.10 * h <= st[i, 2] <= 1.15 * h
                    and st[i, 4] >= 0.15 * st[i, 2] * st[i, 3]]
            if len(comp) != len(txt):
                continue
            comp.sort(key=lambda i: st[i, 0])
            ym = float(np.median([cen[i][1] for i in comp]))
            if any(abs(cen[i][1] - ym) > 0.4 * h for i in comp):
                continue
            for c, i in zip(txt, comp):
                x, y, w, hh, _ = st[i]
                rec[c].append(N.vignette(
                    (lab[y:y + hh, x:x + w] == i).astype(np.uint8) * 255))
            ok += 1
    print(f"  {ok}/{tot} numbers came apart cleanly")
    return rec


def learn():
    """Groups the harvest: the centres of the groups are the models."""
    rec = harvest()
    out = {}
    for c in "0123456789":
        v = np.stack(rec[c]).astype(np.float32)
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        k = min(GROUPS, len(v))
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 1e-4)
        _, lab, cen = cv2.kmeans(v, k, None, crit, 8, cv2.KMEANS_PP_CENTERS)
        lab = lab.ravel()
        kept = [i for i in range(k) if (lab == i).sum() >= RARE * len(v)]
        out[c] = np.stack([cen[i].reshape(N.H, N.W) for i in kept])
        print(f"  {c} : {len(v):4d} exemplaires, {len(kept)} modeles "
              f"{[int((lab == i).sum()) for i in kept]}")
    np.savez_compressed(MODELS, **out)
    print(f"  written to {MODELS}")


def load_():
    """Puts the grey models in place of the stencil's."""
    d = np.load(MODELS)
    names = [c for c in d.files for _ in range(len(d[c]))]
    stack_ = np.stack([m for c in d.files for m in d[c]]).reshape(len(names), -1)
    N.NAMES = names
    N.STACK = stack_ / np.linalg.norm(stack_, axis=1, keepdims=True)
    N.GREY = True


def propose(keys=None):
    """Re-reads the grey plates, but returns ONLY what is missing."""
    load_()
    cat = json.loads((ROOT / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    prop = {}
    for key in sorted(cat):
        if not N.redone(key) or (keys and key not in keys):
            continue
        a = N.enko(key)
        ht, la = a.shape
        top = cat[key]["corpo"]
        att = N.expected(key)
        if not att:
            continue
        known = set(cat[key]["numeri"])
        missing = {N.kl(sc, n) for sc, ns in att.items() for n in ns} - known
        out = {}
        for sc, shape_ in (N.scenes_(key) or [("", ["rekt", 0., 0., 1., 1.])]):
            if sc not in att:
                continue
            fx0, fy0, fx1, fy1 = N.box(shape_)
            x0, y0 = int(fx0 * la), int(fy0 * ht)
            x1 = min(la, int(fx1 * la) + 1)
            y1 = min(ht, int(fy1 * ht) + 1)
            for n, (b, fo) in N.read_file(a[y0:y1, x0:x1], att[sc], top).items():
                q = N.kl(sc, n)
                if q in missing:
                    out[q] = [int(b[0] + x0), int(b[1] + y0),
                              int(b[2]), int(b[3]), round(float(fo), 3)]
        if out:
            prop[key] = out
            print(f"  {key} : {len(out)} proposals out of "
                  f"{len(missing)} missing")
    PLACES.write_text(json.dumps(prop, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    feuille(prop, cat)
    print(f"  {sum(len(v) for v in prop.values())} proposals — "
          f"to be re-read in {PROPOSALS}")


def feuille(prop, cat, cols=6, side=330, foot=66, radius=62):
    """The proofing sheet: the cut-out, the object's name, the place."""
    obj = json.loads((ROOT / "plates" / "objects.json")
                     .read_text(encoding="utf-8"))
    def font_face(f, t):
        try:
            return ImageFont.truetype(
                f"/usr/share/fonts/truetype/dejavu/DejaVuSans{f}.ttf", t)
        except Exception:
            return ImageFont.load_default()
    F, G = font_face("-Bold", 26), font_face("", 19)
    cel = []
    for key in sorted(prop):
        im = N.plate(key)
        for q, (x, y, w, h, fo) in sorted(prop[key].items()):
            cx, cy = x + w / 2, y + h / 2
            t = im.crop((int(cx - radius), int(cy - radius),
                         int(cx + radius), int(cy + radius))).convert("RGB")
            c = Image.new("RGB", (side, side + foot), (255, 255, 255))
            c.paste(t.resize((side, side), Image.LANCZOS), (0, 0))
            g = ImageDraw.Draw(c)
            Z = side / (2 * radius)
            g.rectangle([side / 2 - w * Z / 2 - 3, side / 2 - h * Z / 2 - 3,
                         side / 2 + w * Z / 2 + 3, side / 2 + h * Z / 2 + 3],
                        outline=(255, 60, 0), width=3)
            n = N.unkey(q)[1]
            name_ = (obj.get(key[:3], {}).get(str(n), {}).get("fr") or ["?"])[0]
            g.text((6, side + 3), f"{key[:3]} {q}  ({fo})",
                   fill=(0, 0, 0), font=F)
            g.text((6, side + 34), name_[:34], fill=(80, 80, 80), font=G)
            cel.append(c)
    if not cel:
        return
    lig = [cel[i:i + cols] for i in range(0, len(cel), cols)]
    out = Image.new("RGB", (cols * side, len(lig) * (side + foot)),
                    (255, 255, 255))
    for j, l in enumerate(lig):
        for i, c in enumerate(l):
            out.paste(c, (i * side, j * (side + foot)))
    out.save(PROPOSALS)


def hand(args):
    if not args or args[0] == "aprendar":
        learn()
    elif args[0] == "proponar":
        propose(args[1:] or None)
    else:
        raise SystemExit(__doc__ or "aprendar | proponar")


if __name__ == "__main__":
    hand(sys.argv[1:])
