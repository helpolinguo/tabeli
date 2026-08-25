#!/usr/bin/env python3
# ===================================================================
#  manual.py — the numbers picked up by eye, placed to the pixel.
#
#  The automatic reader has a ceiling: the reserve of white that carries
#  the figure closes up as soon as the engraving is dense, and the figure
#  is then lost in the hatching. The rest is therefore picked up by hand
#  — but by hand ONLY FOR WHAT THE MACHINE CANNOT DO.
#
#  THE DIVISION OF LABOUR. The eye reads the plate in tiles, on a grid
#  whose lines carry the coordinate, and dictates « 74 at 2286,1326 »:
#  the number, and its place. What has already been found is circled on
#  the tile, so that nothing is ever read twice.
#
#  WE FIRST TRIED DICTATING ONLY HALF OF IT — the cell, the tool looking
#  for the number inside it by matched filter. That does not work:
#  « 72 » landed on the 71 next door, « 77 » on the 75, and narrowing
#  the window to half a cell changed nothing. On table 1, the « 7 » of 72
#  is half hidden behind a hat, and the filter does not recognise an
#  amputated figure even when told which one to look for and where. The
#  eye, for its part, reads the number AND its place: it may as well
#  dictate both.
#
#  plates/manual.json is kept by hand, like verdicts.json; numbering.py
#  reads it and adds what it names.
#
#  USAGE
#      python3 tools/manual.py tile   t01-apar-1   # make the tiles
#      python3 tools/manual.py zone   t01-apar-1   # what is missing, close up
#      python3 tools/manual.py place  t01-apar-1 10=615,868 74=2286,1326
#      python3 tools/manual.py sheet  t01-apar-1   # the check
# ===================================================================

import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbering as N                                          # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = N.ROOT
TILES = ROOT / "plates" / "tuili"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PAS = 290
NX = NY = 2
MARGIN = 0.02


def font_(size_):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size_)
    except Exception:
        return ImageFont.load_default()


def frames(key, n=NX, scene=""):
    """The division into n x n: (x0, y0, x1, y1) for each tile.

    With a scene, only its vignette is cut up: on a plate carrying five
    of them, tiling the whole plate gives tiles straddling two
    numberings, and the eye no longer knows which of the two
    « 12 » it is looking at.
    """
    im = N.plate(key)
    W, H = im.size
    bx0, by0, bx1, by1 = 0.0, 0.0, 1.0, 1.0
    if scene:
        shape_ = dict(N.scenes_(key))[scene]
        bx0, by0, bx1, by1 = N.box(shape_)
    X0, Y0 = bx0 * W, by0 * H
    LG, HT = (bx1 - bx0) * W, (by1 - by0) * H
    out = []
    for iy in range(n):
        for ix in range(n):
            x0 = max(0, round(X0 + LG * ix / n - LG * MARGIN))
            y0 = max(0, round(Y0 + HT * iy / n - HT * MARGIN))
            x1 = min(W, round(X0 + LG * (ix + 1) / n + LG * MARGIN))
            y1 = min(H, round(Y0 + HT * (iy + 1) / n + HT * MARGIN))
            out.append((x0, y0, x1, y1))
    return im, out


def remaining(key, known):
    """What the text calls for and nobody has found yet."""
    att = {N.kl(sc, n) for sc, ns in N.expected(key).items() for n in ns}
    return sorted(att - set(known), key=N.unkey)


def tile(key, n=NX, z=1.0, scene=""):
    """Writes the tiles, the already known numbers circled."""
    TILES.mkdir(parents=True, exist_ok=True)
    im, cads = frames(key, n, scene)
    W, H = im.size
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    known = {n: (v[0] * W + v[2] * W / 2, v[1] * H + v[3] * H / 2)
              for n, v in d["numeri"].items()}
    # What has just been placed by hand counts too, failing which the whole
    # reader would have to be run again between two tiles to stop re-reading
    # what has already been picked up.
    fm = ROOT / "plates" / "manual.json"
    if fm.exists():
        for n, v in json.loads(fm.read_text(encoding="utf-8")) \
                .get(key, {}).items():
            known[n] = (v[0] * W + v[2] * W / 2, v[1] * H + v[3] * H / 2)
    F = font_(34)
    for k, (x0, y0, x1, y1) in enumerate(cads):
        # THE LINE WORK REVERSED. The layer carries the ink white on black;
        # the eye loses half of what it could read there. We put it back the
        # right way round, and the tile becomes an engraving again.
        t = im.crop((x0, y0, x1, y1)).convert("RGB")
        if z != 1.0:
            t = t.resize((round(t.width * z), round(t.height * z)),
                         Image.LANCZOS)
        g = ImageDraw.Draw(t)
        # WHAT HAS ALREADY BEEN FOUND IS CIRCLED: the eye has only to read
        # what is not, and does not read the same thing twice.
        for bare_, (cx, cy) in known.items():
            if x0 <= cx < x1 and y0 <= cy < y1:
                a, b = (cx - x0) * z, (cy - y0) * z
                g.ellipse([a - 34 * z, b - 34 * z, a + 34 * z, b + 34 * z],
                          outline=(255, 60, 0), width=6)
        for gx in range(0, x1 - x0, PAS):
            g.line([gx * z, 0, gx * z, t.height], fill=(0, 130, 255), width=2)
        for gy in range(0, y1 - y0, PAS):
            g.line([0, gy * z, t.width, gy * z], fill=(0, 130, 255), width=2)
        # THE LINES CARRY THE PLATE'S COORDINATE, not a cell name. We first
        # dictated « 74 at H4 » and let the machine search within the cell:
        # it cannot manage it. On this plate, the « 7 » of 72 is half hidden
        # by a hat, that of 77 abuts a 75 — and the matched filter, already
        # unable to choose between two numbers of the same length, goes wrong
        # even within half a cell. The eye, for its part, reads the number AND
        # its place; it may as well dictate both.
        for gx in range(0, x1 - x0, PAS):
            e = f"{x0 + gx}"
            g.rectangle([gx * z + 3, 3, gx * z + 26 + 17 * len(e), 46],
                        fill=(0, 0, 0))
            g.text((gx * z + 8, 2), e, fill=(0, 190, 255), font=F)
        for gy in range(PAS, y1 - y0, PAS):
            e = f"{y0 + gy}"
            g.rectangle([3, gy * z + 3, 26 + 17 * len(e), gy * z + 46],
                        fill=(0, 0, 0))
            g.text((8, gy * z + 2), e, fill=(0, 190, 255), font=F)
        t.save(TILES / f"{key}{'-' + scene if scene else ''}-{k}.png")
    missing = remaining(key, known)
    if scene:
        missing = [q for q in missing if N.unkey(q)[0] == scene]
    print(f"  {key} : {len(cads)} tuiles, {len(missing)} numeros manquants")
    print(f"  {missing}")


# THE ZONES. The last numbers of a dense plate are the ones the eye
# could not see on a half-plate tile: at that reduction the figure is no
# more than twenty-seven points. We therefore look closer, but only
# WHERE IT IS NEEDED. Number n lies, nine times out of ten, less than
# three hundred and fifty points from the midpoint of the segment
# joining n-1 to n+1 — measured on the thirty-eight numbers of table 14
# whose two neighbours are known. We therefore cut around that midpoint,
# and windows that overlap are merged into one, so that a single image
# often serves several.
ZONE_W, ZONE_H = 950, 680
ZONE_Z = 2.1                     # the figure is eighty points there


def zone(key, radius=None):
    """Cuts out, around the presumed place, what is still missing."""
    TILES.mkdir(parents=True, exist_ok=True)
    im = N.plate(key)
    W, H = im.size
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    known = {n: ((v[0] + v[2] / 2) * W, (v[1] + v[3] / 2) * H)
              for n, v in d["numeri"].items()}
    fm = ROOT / "plates" / "manual.json"
    if fm.exists():
        for n, v in json.loads(fm.read_text(encoding="utf-8")) \
                .get(key, {}).items():
            known[n] = ((v[0] + v[2] / 2) * W, (v[1] + v[3] / 2) * H)
    missing = remaining(key, known)
    if not missing:
        print(f"  {key} : rien ne manque")
        return
    # The presumed place: the midpoint of the two known neighbours nearest
    # in rank, or the single neighbour when there is only one.
    def presumed(k):
        sc, n = N.unkey(k)
        frat = {N.unkey(q)[1]: v for q, v in known.items()
                if N.unkey(q)[0] == sc}
        bottom = max((k for k in frat if k < n), default=None)
        top = min((k for k in frat if k > n), default=None)
        if bottom is not None and top is not None:
            return ((frat[bottom][0] + frat[top][0]) / 2,
                    (frat[bottom][1] + frat[top][1]) / 2)
        if bottom is not None:
            return frat[bottom]
        if top is not None:
            return frat[top]
        return (W / 2, H / 2)

    zones = []                                  # (x0, y0, [numbers])
    for n in missing:
        cx, cy = presumed(n)
        for z in zones:
            if abs(z[0] + ZONE_W / 2 - cx) < ZONE_W * 0.35 and \
               abs(z[1] + ZONE_H / 2 - cy) < ZONE_H * 0.35:
                z[2].append(n)
                break
        else:
            x0 = min(max(0, round(cx - ZONE_W / 2)), max(0, W - ZONE_W))
            y0 = min(max(0, round(cy - ZONE_H / 2)), max(0, H - ZONE_H))
            zones.append([x0, y0, [n]])
    F = font_(30)
    for k, (x0, y0, ns) in enumerate(zones):
        x1, y1 = min(W, x0 + ZONE_W), min(H, y0 + ZONE_H)
        # THE LINE WORK IN BLACK ON WHITE. The line layer carries the ink white
        # on black; to the eye that reads badly — we reverse it, and the plate
        # becomes what it is again, an engraving.
        t = im.crop((x0, y0, x1, y1)).convert("RGB")
        t = t.resize((round(t.width * ZONE_Z), round(t.height * ZONE_Z)),
                     Image.LANCZOS)
        g = ImageDraw.Draw(t)
        Z = ZONE_Z
        for n, (cx, cy) in known.items():
            if x0 <= cx < x1 and y0 <= cy < y1:
                a, b = (cx - x0) * Z, (cy - y0) * Z
                g.ellipse([a - 34 * Z, b - 34 * Z, a + 34 * Z, b + 34 * Z],
                          outline=(255, 60, 0), width=6)
        pas = 100
        dx = (-x0) % pas
        dy = (-y0) % pas
        for gx in range(dx, x1 - x0, pas):
            strong = (x0 + gx) % 500 == 0
            g.line([gx * Z, 0, gx * Z, t.height],
                   fill=(0, 130, 255) if strong else (120, 190, 235),
                   width=3 if strong else 1)
            if strong:
                e = f"{x0 + gx}"
                g.rectangle([gx * Z + 3, 3, gx * Z + 22 + 15 * len(e), 40],
                            fill=(0, 0, 0))
                g.text((gx * Z + 7, 2), e, fill=(0, 190, 255), font=F)
        for gy in range(dy, y1 - y0, pas):
            strong = (y0 + gy) % 500 == 0
            g.line([0, gy * Z, t.width, gy * Z],
                   fill=(0, 130, 255) if strong else (120, 190, 235),
                   width=3 if strong else 1)
            if strong:
                e = f"{y0 + gy}"
                g.rectangle([3, gy * Z + 3, 22 + 15 * len(e), gy * Z + 40],
                            fill=(0, 0, 0))
                g.text((7, gy * Z + 2), e, fill=(0, 190, 255), font=F)
        t.save(TILES / f"{key}-z{k}.png")
        print(f"  z{k} ({x0},{y0}) : {ns}")
    print(f"  {key} : {len(zones)} zones, {len(missing)} numeros manquants")


def cell_(key, tile_, ref):
    """« H4 » on tile k -> (x, y) at the centre of the cell, on the plate."""
    m = re.fullmatch(r'([A-Z])(\d+)', ref.upper())
    if not m:
        raise SystemExit(f"case illisible : {ref}")
    _, cads = frames(key)
    x0, y0, _, _ = cads[tile_]
    cx = x0 + LETTERS.index(m.group(1)) * PAS + PAS / 2
    cy = y0 + int(m.group(2)) * PAS + PAS / 2
    return cx, cy


# THE TEMPLATE IS CUT FROM FIGURES ALONE. « 94bis » is not one: the
# engraver slipped two tools in among the others rather than renumber
# the plate, and their number carries a word. We cut the template on the
# figures alone -- it is by them that it will be found again -- and
# lengthen the frame by what the word occupies, so that the close-up
# shows it whole.
def template_(n, size, margin=12, gap=0.13):
    t = str(n)
    cont = t[len(t.rstrip("abcdefghijklmnopqrstuvwxyz")):]
    parts = []
    for c in t[:len(t) - len(cont)]:
        m = N._base()[c]
        parts.append(cv2.resize(m, (max(1, round(m.shape[1] * size / N.H)),
                                    size), interpolation=cv2.INTER_AREA))
    e = max(1, round(gap * size))
    L = sum(p.shape[1] for p in parts) + e * (len(parts) - 1)
    g = np.zeros((size, L), np.float32)
    x = 0
    for p in parts:
        g[:, x:x + p.shape[1]] = p
        x += p.shape[1] + e
    q = np.zeros((size + 2 * margin, L + 2 * margin), np.float32)
    q[margin:margin + size, margin:margin + L] = g
    pos = (q >= 0.5).astype(np.float32)
    neg = 1.0 - pos
    return pos / pos.sum() - neg / neg.sum(), margin, \
        L + round(0.62 * size * len(cont))


# THE SEARCH WINDOW STAYS NARROW. At a cell and a half, the filter went
# looking for the NEIGHBOURING number: « 72 » dictated at I5 landed on
# the 71 next door, « 73 » on the 75. Half a cell is enough once the eye
# has read the grid properly, and it forbids those slips.
def place(key, refs, radius=0.62):
    """Finds each dictated number in its cell and its neighbours.

    On a plate with several scenes the number is dictated with its own
    — « c3:12=1840,2210 » —, failing which one would not know which
    twelve it is.
    """
    # THE TEMPLATE IS CUT FROM THE INK ONE IS LOOKING AT. On a re-pulled
    # plate, the stencil models score 0.24 where the grey ones score close
    # to 1: the filter then slipped by some ten points, and the frame fell
    # beside the figure.
    N.GREY = N.redone(key)
    ink_ = (N.enko(key) > 100).astype(np.float32)
    HT, LA = ink_.shape
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    size = d["corpo"]
    f = ROOT / "plates" / "manual.json"
    everything = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    per = everything.setdefault(key, {})
    occupies = [(round(v[0] * LA), round(v[1] * HT))
              for v in d["numeri"].values()]
    occupies += [(round(v[0] * LA), round(v[1] * HT)) for v in per.values()]
    for k, tile_, ref in refs:
        n = N.unkey(k)[1]
        if ref.count(",") == 2:
            # The eye has seen the number, but pointed at it: we search
            # within the dictated radius, and the filter sets the frame to
            # the figure. Short radius -- that is what forbids the slips.
            cx, cy, rad = (int(v) for v in ref.split(","))
            T, M, L = template_(n, size)
            x0, y0 = int(cx - L / 2) - rad, int(cy - size / 2) - rad
            x1 = int(cx - L / 2) + rad + T.shape[1]
            y1 = int(cy - size / 2) + rad + T.shape[0]
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(LA, x1), min(HT, y1)
            r = cv2.matchTemplate(ink_[y0:y1, x0:x1], T, cv2.TM_CCORR)
            _, mx, _, loc = cv2.minMaxLoc(r)
            px, py = x0 + loc[0] + M, y0 + loc[1] + M
            per[k] = [round(px / LA, 6), round(py / HT, 6),
                      round(L / LA, 6), round(size / HT, 6), 1.0]
            print(f"  {k:>7} cale sur ({px}, {py})  score {mx:.3f}")
            continue
        if "," in ref:
            # The eye has read the place off the grid: we take it as it
            # stands, without searching for anything. This is the surest case.
            px, py = (int(v) for v in ref.split(","))
            T, M, L = template_(n, size)
            per[k] = [round((px - L / 2) / LA, 6),
                      round((py - size / 2) / HT, 6),
                      round(L / LA, 6), round(size / HT, 6), 1.0]
            print(f"  {k:>7} pose a l'oeil en ({px}, {py})")
            continue
        cx, cy = cell_(key, tile_, ref)
        T, M, L = template_(n, size)
        R = round(radius * PAS)
        x0, y0 = int(cx) - R, int(cy) - R
        x1, y1 = int(cx) + R + T.shape[1], int(cy) + R + T.shape[0]
        if x0 < 0 or y0 < 0 or x1 > LA or y1 > HT:
            print(f"  {n} en {ref} : hors planche")
            continue
        r = cv2.matchTemplate(ink_[y0:y1, x0:x1], T, cv2.TM_CCORR)
        # THE PLACES ALREADY TAKEN ARE FORBIDDEN. « 77 » dictated at G5
        # landed on the 75 next door — same first figure, a hundred and
        # thirty points further on — and « 72 » on the 71. But we know
        # where the numbers already found are: we erase those places from
        # the map, and the filter has to look elsewhere.
        for b2 in occupies:
            ox, oy = b2[0] - x0 - M, b2[1] - y0 - M
            if -size < ox < r.shape[1] + size and \
               -size < oy < r.shape[0] + size:
                a0 = max(0, int(oy - 0.7 * size))
                a1 = min(r.shape[0], int(oy + 0.7 * size) + 1)
                b0 = max(0, int(ox - 0.7 * size))
                b1 = min(r.shape[1], int(ox + 0.7 * size) + 1)
                if a1 > a0 and b1 > b0:
                    r[a0:a1, b0:b1] = -9
        _, mx, _, loc = cv2.minMaxLoc(r)
        px, py = x0 + loc[0] + M, y0 + loc[1] + M
        per[k] = [round(px / LA, 6), round(py / HT, 6),
                  round(L / LA, 6), round(size / HT, 6), round(mx, 3)]
        print(f"  {k:>7} en {ref} (tuile {tile_}) -> "
              f"({px}, {py})  score {mx:.3f}")
    f.write_text(json.dumps(everything, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")


def plate(key):
    """The check sheet for the numbers placed by hand."""
    f = ROOT / "plates" / "manual.json"
    if not f.exists():
        return
    per = json.loads(f.read_text(encoding="utf-8")).get(key, {})
    if not per:
        print(f"  {key} : rien de pose a la main")
        return
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    LA, HT, size = d["largeur"], d["alteso"], d["corpo"]
    found_ = {n: ((round(v[0] * LA), round(v[1] * HT),
                    round(v[2] * LA), round(v[3] * HT)), v[4])
               for n, v in per.items()}
    N.REVIEW.mkdir(parents=True, exist_ok=True)
    n = N.check(key, found_,
                   N.REVIEW / f"{key}-manuali.png", size,
                   wide=1.5, cols=10)
    print(f"  {key} : {n} decoupes dans "
          f"{N.REVIEW / (key + '-manuali.png')}")


# THE RE-READING OF THE AUTOMATIC READINGS. The score does not say
# everything: the filter looking for « 14 » finds it in the « 144 » next
# door, and nothing warns it -- the piece is perfectly formed. The
# readings must therefore be passed under the eye, one plate at a time,
# each cut wide and carrying the name the facsimile gives the object.
# What has been placed by hand does not appear there: it is already
# judged.
def review(key, page=0, per=24, cols=6, Z=3):
    """A plate's automatic readings, to be re-read one by one."""
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    LA, HT, size = d["largeur"], d["alteso"], d["corpo"]
    fm = ROOT / "plates" / "manual.json"
    hands = (json.loads(fm.read_text(encoding="utf-8")).get(key, {})
             if fm.exists() else {})
    names = N.objects_(key)
    everything = [(n, v) for n, v in d["numeri"].items() if n not in hands]
    everything.sort(key=lambda q: N.unkey(q[0]))
    lot = everything[page * per:(page + 1) * per]
    if not lot:
        print(f"  {key} : plus rien a relire")
        return 0
    im = N.plate(key)
    w, h = round(size * 4.4), round(size * 3.0)
    F = font_(20)
    F2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    lig = (len(lot) + cols - 1) // cols
    pl = Image.new("RGB", (cols * (w * Z + 10) + 10,
                           lig * (h * Z + 52) + 10), (255, 255, 255))
    g = ImageDraw.Draw(pl)
    for i, (n, v) in enumerate(lot):
        cx, cy = (v[0] + v[2] / 2) * LA, (v[1] + v[3] / 2) * HT
        c = im.crop((round(cx - w / 2), round(cy - h / 2),
                     round(cx + w / 2), round(cy + h / 2))).convert("RGB")
        c = c.resize((w * Z, h * Z), Image.LANCZOS)
        X, Y = 10 + (i % cols) * (w * Z + 10), 10 + (i // cols) * (h * Z + 52)
        pl.paste(c, (X, Y))
        g.rectangle([X, Y, X + w * Z, Y + h * Z], outline=(200, 0, 0))
        nm = names.get(str(n), {})
        name_ = (nm.get("fr") or nm.get("io") or [""])[0]
        g.text((X + 2, Y + h * Z + 3), f"{n} — {name_[:24]}",
               fill=(0, 0, 0), font=F)
        g.text((X + 2, Y + h * Z + 26),
               f"{v[4]:.2f}   {round(cx)},{round(cy)}",
               fill=(90, 90, 90), font=F2)
    N.REVIEW.mkdir(parents=True, exist_ok=True)
    dest = N.REVIEW / f"{key}-revizo{page}.png"
    pl.save(dest)
    print(f"  {key} : page {page}, {len(lot)} lectures sur {len(everything)} "
          f"-> {dest}")
    return len(everything)


# -------------------------------------------------------------------
#  THE LETTERS
# -------------------------------------------------------------------
#  Three tables carry, beside the numbers, letters engraved on an
#  object: the figures on the blackboard, the parts of the world on the
#  map, the rooms on the house plan. They are placed like the numbers --
#  the eye reads the place off the grid and dictates it -- but are filed
#  in plates/letters.json, under the prefix of the object that carries
#  them: « 1a » is the circle on the blackboard, « 10a » North America
#  on the map.
#
#  THE BOX IS SQUARE, of the figure's body: a letter has no predictable
#  width, and the close-up takes it wide in any case.
#
#      python3 tools/manual.py letter t01-apar-1 1a=91,2026 1b=239,1926
LETTERS_ = ROOT / "plates" / "letters.json"


def letter(key, refs):
    """Places letters by eye, as one places numbers."""
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    LA, HT, size = d["largeur"], d["alteso"], d["corpo"]
    everything = json.loads(LETTERS_.read_text(encoding="utf-8"))
    per = everything.setdefault(key, {})
    for k, ref in refs:
        px, py = (int(v) for v in ref.split(","))
        per[k] = [round((px - size / 2) / LA, 6),
                  round((py - size / 2) / HT, 6),
                  round(size / LA, 6), round(size / HT, 6), 1.0]
        print(f"  {k:>6} pose a l'oeil en ({px}, {py})")
    LETTERS_.write_text(json.dumps(everything, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")


def letters_sheet(key):
    """The check sheet for the letters placed."""
    everything = json.loads(LETTERS_.read_text(encoding="utf-8"))
    per = everything.get(key, {})
    if not per:
        print(f"  {key} : aucune lettre posee")
        return
    d = json.loads((ROOT / "plates" / "numbers.json")
                   .read_text(encoding="utf-8"))[key]
    LA, HT, size = d["largeur"], d["alteso"], d["corpo"]
    im = N.plate(key).convert("RGB")
    cols, Z = 8, 3
    w = h = round(size * 3.0)
    lot = sorted(per.items())
    lig = (len(lot) + cols - 1) // cols
    pl = Image.new("RGB", (cols * (w * Z + 8) + 8, lig * (h * Z + 30) + 8),
                   (255, 255, 255))
    g = ImageDraw.Draw(pl)
    F = font_(19)
    for i, (k, v) in enumerate(lot):
        cx, cy = (v[0] + v[2] / 2) * LA, (v[1] + v[3] / 2) * HT
        c = im.crop((round(cx - w / 2), round(cy - h / 2),
                     round(cx + w / 2), round(cy + h / 2))) \
            .resize((w * Z, h * Z), Image.LANCZOS)
        X, Y = 8 + (i % cols) * (w * Z + 8), 8 + (i // cols) * (h * Z + 30)
        pl.paste(c, (X, Y))
        g.rectangle([X, Y, X + w * Z, Y + h * Z], outline=(200, 0, 0))
        g.text((X + 2, Y + h * Z + 4), k, fill=(0, 0, 0), font=F)
    N.REVIEW.mkdir(parents=True, exist_ok=True)
    dest = N.REVIEW / f"{key}-literi.png"
    pl.save(dest)
    print(f"  {key} : {len(lot)} lettres dans {dest}")



def hand(args):
    if not args:
        raise SystemExit(__doc__)
    verb, key = args[0], args[1]
    if verb == "tuiler":
        tile(key, int(args[2]) if len(args) > 2 else NX,
               float(args[3]) if len(args) > 3 else 1.0,
               args[4] if len(args) > 4 else "")
    elif verb == "zono":
        zone(key)
    elif verb == "litero":
        letter(key, [tuple(a.split("=")) for a in args[2:]])
    elif verb == "literi":
        letters_sheet(key)
    elif verb == "revizo":
        review(key, int(args[2]) if len(args) > 2 else 0)
    elif verb == "planche":
        plate(key)
    elif verb == "poser":
        refs = []
        tile_ = 0
        for a in args[2:]:
            if a.startswith("t="):
                tile_ = int(a[2:])
                continue
            k, ref = a.split("=")
            refs.append((k, tile_, ref))
        place(key, refs)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    hand(sys.argv[1:])
