#!/usr/bin/env python3
# ===================================================================
#  originals.py — laying an original scan over our plates.
#
#  WHY. The engravings the page serves come from a colourised PDF: the
#  line layer there is a STENCIL — 87 per cent of its points are pure
#  black or pure white — because it served as a mask for laying the ink.
#  The half-tone of the wood engraving, which makes all the softness of
#  the plate, is gone from it, and no resolution will bring it back. We
#  must therefore start again from the original scans (Gallica, BnF).
#
#  WHAT WOULD BE LOST WITHOUT THIS TOOL. Fifteen hundred numbers have
#  been picked up by hand on the present plates. They are recorded AS A
#  FRACTION of the plate, not in points: to carry them onto another
#  scan, it is enough to know which similarity — rotation, scale,
#  translation — leads from one to the other. That is what this tool
#  measures, and it measures it without being told anything: the
#  correlation between two very different renderings of the same drawing
#  is enough.
#
#  WE HAVE CHECKED THAT IT WORKS EVEN FROM VERY FAR AWAY. Gallica's
#  service copy gives the engraving of table 1 only 1250 points across,
#  against 5463 for our line layer — four times fewer — and the
#  registration still falls right.
#
#  USAGE
#      python3 tools/originals.py register t01-apar-1 original.jpg
#      python3 tools/originals.py compare  t01-apar-1 original.jpg 0.79 0.20
#      python3 tools/originals.py clean    t01-apar-1 originals/t01.jpg
#      python3 tools/originals.py redo     t02-apar-1 originals/t02.jpg
# ===================================================================

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbering as N                                          # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
CATALOGO = RACINE / "plates" / "originals.json"


def gris(chemin):
    """The image in grey, the ink in black, as a normalised float."""
    im = Image.open(chemin)
    if im.mode not in ("L", "I;16"):
        im = im.convert("L")
    a = np.asarray(im).astype(np.float32)
    if a.max() > 255:
        a = a / 257.0
    return a


def notre_trait(cle):
    """Our line layer, put back the right way round: the ink in black."""
    a = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")).astype(np.float32)
    return 255.0 - a


def centrer(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 1e-6 else a


# THE PLATE MAY BE LYING ON ITS SIDE IN THE SCAN. The leaves are bound
# the tall way and the engraving lies across them; we therefore try all
# four quarter turns, and keep the one that catches.
def orientations(a):
    for k in range(4):
        yield k, np.rot90(a, k)


def caler(cle, chemin, large=1100, verbeux=True):
    """The similarity that leads from our plate to the scan.

    Returns (M, score, turn): M is the 2x3 matrix that sends a point of
    OUR plate, in points, onto the scan, in points.
    """
    src = notre_trait(cle)
    HS, LS = src.shape
    dst0 = gris(chemin)
    petit_src = cv2.resize(src, (large, round(large * HS / LS)),
                           interpolation=cv2.INTER_AREA)
    ech_src = LS / large
    best = None
    for tour, dst in orientations(dst0):
        HD, LD = dst.shape
        if LD < 200 or HD < 200:
            continue
        f = large / max(LD, HD)
        petit_dst = cv2.resize(dst, (max(1, round(LD * f)),
                                     max(1, round(HD * f))),
                               interpolation=cv2.INTER_AREA)
        ech_dst = 1 / f
        # The engraving occupies only part of the leaf: we look for our
        # plate WITHIN the page, at several scales.
        g = centrer(petit_dst)
        for r in np.arange(0.45, 1.02, 0.025):
            w = round(petit_src.shape[1] * r)
            h = round(petit_src.shape[0] * r)
            if w < 80 or h < 80 or w > g.shape[1] or h > g.shape[0]:
                continue
            s = centrer(cv2.resize(petit_src, (w, h),
                                   interpolation=cv2.INTER_AREA))
            m = cv2.matchTemplate(g, s, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(m)
            if best is None or mx > best[0]:
                best = (mx, tour, r, loc, ech_dst, w, h)
    if best is None:
        raise SystemExit("  rien a caler")
    score, tour, r, (x0, y0), ech_dst, w, h = best
    # From our plate (points) to the TURNED scan (points).
    k = r / ech_src * ech_dst
    M = np.array([[k, 0.0, x0 * ech_dst],
                  [0.0, k, y0 * ech_dst]], np.float32)
    if verbeux:
        print(f"  {cle} : quart de tour {tour}, echelle {k:.4f}, "
              f"coin ({round(x0 * ech_dst)}, {round(y0 * ech_dst)}), "
              f"correlation {score:.3f}")
        print(f"  la gravure y mesure {round(LS * k)} x {round(HS * k)} "
              f"points (nous : {LS} x {HS})")
    return M, score, tour


def charger_tournee(chemin, tour):
    a = gris(chemin)
    return np.rot90(a, tour)


def compar(cle, chemin, cx=0.5, cy=0.5, w=0.115, h=0.095, sortie=None):
    """The same detail in all three states, side by side."""
    M, score, tour = caler(cle, chemin)
    ori = charger_tournee(chemin, tour)
    HS, LS = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")).shape
    x0f, y0f = cx - w / 2, cy - h / 2

    def coupe_ori():
        p = np.array([[x0f * LS, y0f * HS, 1.0],
                      [(x0f + w) * LS, (y0f + h) * HS, 1.0]]).T
        q = M @ p
        return Image.fromarray(ori.astype(np.uint8)).crop(
            (round(q[0, 0]), round(q[1, 0]), round(q[0, 1]), round(q[1, 1])))

    vues = [(coupe_ori(), "la numerisation d'origine")]
    for nom, im, quoi in (
            ("detalo", Image.open(RACINE / "plates" / f"{cle}-detalo.webp")
             .convert("L"), "ce que la page sert"),
            ("trako", ImageOps.invert(Image.open(N.KOVRI / f"{cle}-trako.png")
                                      .convert("L")), "notre couche de trait")):
        W_, H_ = im.size
        vues.append((im.crop((round(x0f * W_), round(y0f * H_),
                              round((x0f + w) * W_), round((y0f + h) * H_))),
                     quoi))
    OUT = (1000, round(1000 * h / w * (HS / LS) / 1.0))
    F = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
    F2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
    pl = Image.new("RGB", (3 * (OUT[0] + 16) + 16, OUT[1] + 90),
                   (255, 255, 255))
    d = ImageDraw.Draw(pl)
    for i, (c, t) in enumerate(vues):
        n = f"{c.width} x {c.height} points pour ce detail"
        c = c.resize(OUT, Image.LANCZOS).convert("RGB")
        X = 16 + i * (OUT[0] + 16)
        pl.paste(c, (X, 16))
        d.rectangle([X, 16, X + OUT[0], 16 + OUT[1]], outline=(190, 0, 0),
                    width=2)
        d.text((X, OUT[1] + 26), t, fill=(0, 0, 0), font=F)
        d.text((X, OUT[1] + 54), n, fill=(90, 90, 90), font=F2)
    sortie = Path(sortie or (RACINE / "plates" / "review" /
                             f"{cle}-origino.png"))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    pl.save(sortie)
    print(f"  comparaison dans {sortie}")


# -------------------------------------------------------------------
#  THE CLEANING, AND WHAT IT FORBIDS ITSELF
# -------------------------------------------------------------------
#  We straighten and we trim, NOTHING MORE, and IN A SINGLE
#  RESAMPLING: the rotation and the trim are composed into one matrix,
#  applied once. Two passes in a row — turn, then cut — cost one
#  interpolation too many, and that shows on a hatching two points wide.
#
#  THE ANGLE IS MEASURED ON THE FRAME'S RULE, not on the drawing. We
#  take the two horizontal rules, which run over four thousand points
#  and give the angle to a twentieth of a degree; the vertical rules
#  serve as a check. On table 1 the two horizontals agree on 0.30
#  degrees, and once straightened they fall exactly to zero.
#
#  WE DO NOT STRAIGHTEN THE VERTICALS. After straightening they keep a
#  third of a degree: the sheet has cockled, or the plate was printed
#  askew. Correcting that would call for a shear, that is, for inventing
#  a geometry the facsimile does not have. We record it and leave it.
#
#  AND WE DO NOT TOUCH THE TONE. The paper is cream — its mode is at
#  235, the blackest ink at 66 — and that is how it must be kept: the
#  edition is diplomatic, the lightening will be done at display time if
#  wanted, and will stay reversible.
MARGE_FILET = 8


def _tourner(a, th, centre):
    return cv2.getRotationMatrix2D(centre, th, 1.0)


def angle_filet(enc, bande, axe, ampl=1.2, pas=0.025):
    """The angle that makes a line of the frame sharpest."""
    best = None
    y0, y1, x0, x1 = bande
    b = enc[y0:y1, x0:x1]
    for th in np.arange(-ampl, ampl + 1e-9, pas):
        M = _tourner(b, th, (b.shape[1] / 2, b.shape[0] / 2))
        r = cv2.warpAffine(b, M, (b.shape[1], b.shape[0]),
                           flags=cv2.INTER_LINEAR, borderValue=0)
        p = r.mean(axis=axe)
        v = float(p.max() - np.median(p))
        if best is None or v > best[0]:
            best = (v, float(th), int(np.argmax(p)))
    return best


# WE DO NOT TRY TO RECOGNISE THE RULE: WE TRY EVERY CANDIDATE LINE,
# AND KEEP THE ONE WE FOLLOW BEST.
#
# Two false trails were followed before this one. Taking the most inked
# row: it falls on the series title, which runs along the top of every
# leaf — « Tableaux Auxiliaires Delmas pour l'Enseignement pratique des
# Langues vivantes par l'Image » — and which is far blacker than the
# rule; the fitting residual then rose to ten or twelve points on nine
# plates. Taking the THINNEST peak: one then catches a hatching of the
# drawing, and loses three quarters of the columns.
#
# What distinguishes the rule is neither its blackness nor its
# thinness, it is that it RUNS FROM ONE EDGE TO THE OTHER, dead
# straight. That cannot be guessed from a profile: it is verified by
# following it. We therefore take the eight best peaks of the band,
# follow each, and keep the tightest fit among those that keep enough
# columns.
def meilleur_filet(enc, a0, a1, x0, x1, cand=8):
    """A band's rule: the candidate we follow best."""
    prof = enc[a0:a1, round(0.20 * enc.shape[1]):
               round(0.80 * enc.shape[1])].mean(1)
    ordre = np.argsort(prof)[::-1]
    pris = []
    for i in ordre:
        if all(abs(int(i) - j) > 25 for j in pris):
            pris.append(int(i))
        if len(pris) >= cand:
            break
    best = None
    for i in pris:
        y = a0 + i
        m = suivre_filet(enc, max(0, y - 22), min(enc.shape[0], y + 23),
                         x0, x1)
        if not m or m[2] < 40:
            continue
        if best is None or m[1] < best[0][1]:
            best = (m, y)
    return best


# THE SIDE EDGE IS MEASURED IN TWO WAYS, AND WE KEEP THE OUTER ONE.
#
# The vertical rules are not the horizontals. The latter run from one
# edge to the other and can be followed; the former are sometimes
# engraved with a clean stroke, sometimes barely, sometimes not at all
# — on table 8 there is nothing on the left but the hatching of the
# pond dying away at the edge. Looking for a peak in a profile whose
# median is that of the DRAWING, and not of the paper, could only give
# an accident of the drawing: the trim then fell a hundred points too
# far in and cut off numbers 16, 18, 19 of table 8, a hundred and
# thirty points too short at the right of table 12, eighty on table 11
# — the 76 ended up outside.
#
# We therefore measure two things, starting from the margin:
#
#   the RULE — the first thin peak that rises clearly above the PAPER
#   (and not above the profile's median);
#
#   the ENTRY OF THE DRAWING — the place where the ink passes halfway
#   between the paper and the full of the drawing, and does not come
#   back down.
#
# Then we keep WHICHEVER OF THE TWO IS FURTHER OUT. A little white
# margin costs nothing; a cut engraved line cannot be got back.
# Checked on all sixteen plates: the two measurements fall on each
# other twelve times, and the four times they differ it is the outer
# one that is on the rule.
def _paper(q, marge):
    m = round(marge * len(q))
    return float(np.percentile(q[:m], 20)), float(np.median(q[m:]))


def filet_lateral(q, marge=0.30, large=20):
    """The first thin peak that rises above the paper."""
    fond, plein = _paper(q, marge)
    haut = max(6.0, 0.25 * (plein - fond))
    for i in range(2, len(q) - 2):
        if q[i] >= q[i - 1] and q[i] > q[i + 1] and q[i] - fond >= haut:
            mi = fond + (q[i] - fond) / 2
            a, b = i, i
            while a > 0 and q[a] > mi:
                a -= 1
            while b < len(q) - 1 and q[b] > mi:
                b += 1
            if b - a <= large:
                return i
    return None


def entree_dessin(q, marge=0.30, tenue=20):
    """The place where the ink rises to half-full and stays there."""
    fond, plein = _paper(q, marge)
    if plein - fond < 4:
        return None
    seuil = fond + 0.40 * (plein - fond)
    for i in range(len(q) - tenue):
        if (q[i:i + tenue] > seuil).all():
            return i
    return None


def bord_lateral(prof, sens):
    """One side's edge: the outer of the two measurements."""
    q = np.asarray(prof, dtype=float)
    if sens < 0:
        q = q[::-1]
    duo = [i for i in (filet_lateral(q), entree_dessin(q)) if i is not None]
    if not duo:
        return None
    i = min(duo)
    return i if sens > 0 else len(q) - 1 - i


# MEASURING THE RULE, RATHER THAN LOOKING FOR ITS ANGLE. We used to
# turn the trial band by steps of a fortieth of a degree and keep the
# angle that made the peak sharpest. On table 1 the two horizontal rules
# agreed at +0.300; on table 2 they gave -0.275 and +0.225, half a
# degree apart -- one of the two had caught something other than the
# rule.
#
# We therefore measure the rule ITSELF: for a hundred or so columns
# spread across the width, the most inked line within a narrow window;
# then a line fitted by least squares, rejecting from one pass to the
# next whatever departs too far from the previous one. The slope gives
# the angle, and the residual says whether we have indeed followed a
# rule or run after the branch of a tree.
def suivre_filet(enc, y0, y1, x0, x1, pas=40, fenetre=14):
    """Follows a nearly horizontal line and returns (angle, residual, n).

    WE KEEP ONLY THE COLUMNS WHERE THE RULE CAN BE SEEN. On a plate
    whose sky or ground is hatched, one column in three offers no sharp
    peak, and the barycentre there settles anywhere: the fitting
    residual then rose to ten or eleven points, and the angle was worth
    nothing any more. We therefore measure the STRENGTH of each peak --
    its height above the floor of the window -- and throw away the
    columns that do not reach half the median strength. Only then do we
    fit, four times, tightening on the median absolute residual.
    """
    xs, ys, fs = [], [], []
    for x in range(x0, x1 - pas, pas):
        col = enc[y0:y1, x:x + pas].mean(1)
        if col.max() < 8:
            continue
        i = int(np.argmax(col))
        a0, b0 = max(0, i - fenetre), min(len(col), i + fenetre + 1)
        w = col[a0:b0]
        if w.sum() <= 0:
            continue
        xs.append(x + pas / 2)
        ys.append(y0 + a0 + float((w * np.arange(len(w))).sum() / w.sum()))
        fs.append(float(w.max() - np.median(col)))
    if len(xs) < 8:
        return None
    X, Y, F = np.array(xs), np.array(ys), np.array(fs)
    garde = F >= 0.5 * float(np.median(F))
    if garde.sum() >= 8:
        X, Y = X[garde], Y[garde]
    m = c = 0.0
    for _ in range(4):
        A = np.vstack([X, np.ones_like(X)]).T
        (m, c), *_ = np.linalg.lstsq(A, Y, rcond=None)
        r = np.abs(Y - (m * X + c))
        seuil = max(2.0, 3.0 * float(np.median(r)))
        g = r <= seuil
        if g.sum() < 8 or g.all():
            break
        X, Y = X[g], Y[g]
    return (float(np.degrees(np.arctan(m))),
            float(np.sqrt(((Y - (m * X + c)) ** 2).mean())), int(len(X)))


# THE FRAME: the horizontals are given, the verticals are measured.
#
# We no longer look for the top and bottom rules: they have already been
# FOLLOWED, column by column, to find the sheet's angle, and best_rule
# returned the row each passes through. Straightening does not move it —
# the point (W/2, y) turns about (W/2, H/2), hence along the very axis
# of the rotation. We take it as it stands, with one last registration
# to within twenty points.
def cadre(enc, yh, yb):
    """The frame of an already straightened image, horizontals known."""
    H, W = enc.shape
    mh, mv = round(0.045 * H), round(0.035 * W)

    def caler(y, r=20):
        a, b = max(0, y - r), min(H, y + r + 1)
        p = enc[a:b, mv:W - mv].mean(1)
        return a + int(np.argmax(p)), float(p.max() - np.median(p))

    haut, fh = caler(yh) if yh is not None else (round(0.055 * H), 0.0)
    bas, fb = caler(yb) if yb is not None else (round(0.905 * H), 0.0)
    pg = enc[mh:H - mh, 0:round(0.12 * W)].mean(0)
    pd = enc[mh:H - mh, round(0.88 * W):W].mean(0)
    g = bord_lateral(pg, +1)
    d = bord_lateral(pd, -1)
    gau = 0 if g is None else g
    dro = W - 1 if d is None else round(0.88 * W) + d
    return (gau, haut, dro, bas), (0.0, fh, 0.0, fb)


def netigar(chemin, dest=None, verbeux=True):
    """Straightens and trims a scan, in a single resampling."""
    im = Image.open(chemin)
    a = np.asarray(im.convert("L"))
    # THE SHEET IS BOUND THE TALL WAY, the engraving lies across it.
    tour = 3 if a.shape[0] > a.shape[1] else 0
    a = np.rot90(a, tour)
    H, W = a.shape
    enc = np.clip(200.0 - a.astype(np.float32), 0, None)
    # 1. the angle, on the two horizontal rules, followed point by point.
    #    WE FIRST NARROW THE BAND AROUND THE RULE. On table 2 the ground is
    #    hatched horizontally right down to the bottom of the engraving,
    #    and the follower was catching a hatching instead of the rule: the
    #    two measurements then contradicted each other by half a degree. We
    #    therefore locate the most inked line of the outer half, and follow
    #    the rule only within twenty-five points either side.
    # THE BAND WHERE THE RULE IS, and nowhere else. The sixteen leaves are
    # printed the same way: the top rule falls between the twenty-third and
    # the twenty-seventh hundredth of the leaf, the bottom one between the
    # eighty-ninth and the ninety-first. To search wider is to catch the
    # edge of the sheet — straighter than the rule, and wrong.
    X0, X1 = round(0.08 * W), round(0.92 * W)
    rh = meilleur_filet(enc, round(0.045 * H), round(0.100 * H), X0, X1)
    rb = meilleur_filet(enc, round(0.875 * H), round(0.925 * H), X0, X1)
    mh, yh = rh if rh else (None, None)
    mb, yb = rb if rb else (None, None)
    # WHEN THE TWO RULES CONTRADICT EACH OTHER, WE BELIEVE THE BETTER
    # MEASURED. They agree to within a tenth of a degree on eleven plates;
    # on the other five one of the two was followed on half as many
    # columns, and it is that one that departs. The weight of a measurement
    # is the number of columns kept divided by its fitting residual.
    def poids(m):
        return m[2] / (m[1] + 0.5) if m else 0.0

    duo = [m for m in (mh, mb) if m]
    if len(duo) == 2 and abs(mh[0] - mb[0]) > 0.35:
        th = max(duo, key=poids)[0]
    elif duo:
        pt = sum(poids(m) for m in duo)
        th = sum(m[0] * poids(m) for m in duo) / pt
    else:
        th = 0.0
    # 2. the frame, measured on a straightened copy (thrown away after)
    Mr = _tourner(a, th, (W / 2, H / 2))
    droit = cv2.warpAffine(enc, Mr, (W, H), flags=cv2.INTER_LINEAR,
                           borderValue=0)
    (x0, y0, x1, y1), forces = cadre(droit, yh, yb)
    x0, y0 = x0 - MARGE_FILET, y0 - MARGE_FILET
    x1, y1 = x1 + MARGE_FILET, y1 + MARGE_FILET
    # 3. rotation AND trim in a single matrix, a single pass
    M = Mr.copy()
    M[0, 2] -= x0
    M[1, 2] -= y0
    LG, HT = x1 - x0, y1 - y0
    src = np.rot90(np.asarray(im.convert("L")), tour)
    out = cv2.warpAffine(src, M, (LG, HT), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    # check: what skew is left in the verticals
    e2 = np.clip(200.0 - out.astype(np.float32), 0, None)
    vg = angle_filet(e2, (round(.05*HT), round(.95*HT), 0, 40), 0, 1.0)[1]
    vd = angle_filet(e2, (round(.05*HT), round(.95*HT), LG-40, LG), 0, 1.0)[1]
    if verbeux:
        def dire(m):
            return (f"{m[0]:+.3f} (ecart {m[1]:.2f} sur {m[2]} points)"
                    if m else "introuvable")
        print(f"  quart de tour {tour}, redressement {th:+.3f} deg")
        print(f"    filet du haut : {dire(mh)}")
        print(f"    filet du bas  : {dire(mb)}")
        print(f"  cadre en ({x0}, {y0})-({x1}, {y1}) : {LG} x {HT} points")
        print(f"  verticales laissees de biais : {vg:+.3f} et {vd:+.3f} deg")
    if dest:
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(out).save(dest)
        if verbeux:
            print(f"  ecrit dans {dest}")
    return out, {"tour": tour, "angulo": round(th, 4),
                 "kadro": [int(x0), int(y0), int(x1), int(y1)],
                 # THE TWO RULES SEPARATELY, with their fitting residual:
                 # it is the only way to know later whether we have indeed
                 # followed the frame, and whether the sheet was straight.
                 # On table 2 they converge by four tenths of a degree --
                 # the engraving there is a trapezium, and one does not
                 # correct that without inventing a geometry.
                 "filetoj": [[round(m[0], 3), round(m[1], 2), m[2]]
                             if m else None for m in (mh, mb)],
                 "vertikali": [round(vg, 3), round(vd, 3)]}


# -------------------------------------------------------------------
#  CARRYING THE NUMBERS OVER
# -------------------------------------------------------------------
#  Fifteen hundred numbers have been picked up by hand on the
#  colourised plates. They are recorded AS A FRACTION of the plate: to
#  carry them onto the original scan, the similarity that leads from one
#  to the other is enough.
#
#  IT IS MEASURED BY CORRELATION, on an ink density map — the two
#  images blurred, centred, reduced. The stencil and the facsimile do
#  not resemble each other stroke for stroke, but their masses of ink
#  do: on table 1 the correlation rises to 0.95.
#
#  MIND THE SENSE OF THE INK. In the line layer the ink is 255, in a
#  scan it is dark. Having taken them in the same sense made the
#  correlation drop from 0.95 to 0.10, and we were looking for the fault
#  elsewhere.
def densito(a, W, sigma=1.6):
    """An ink density map, comparable from one rendering to another."""
    h = round(W * a.shape[0] / a.shape[1])
    s = cv2.resize(a.astype(np.float32), (W, h), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), sigma)
    return (s - s.mean()) / (s.std() + 1e-6)


def mezuri(cle, neta, W=1000, verbeux=True):
    """The matrix that leads from the old plate to the new one."""
    # THE REFERENCE IS THE PREVIOUS PLATE, whatever it may be. The first
    # time it is the line layer of the colourised PDF, where the ink is
    # 255; afterwards, if we clean again, it is the already cleaned
    # facsimile, where the ink is dark. Without that a second cleaning
    # would start the numbers off from the stencil, which they have left.
    ancienne = RACINE / "originals" / "kovri" / f"{cle}-neta-antaua.png"
    if ancienne.exists():
        vieux = 255.0 - np.asarray(Image.open(ancienne).convert("L")
                                   ).astype(np.float32)
    else:
        vieux = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")
                           ).astype(np.float32)      # the ink is 255 there
    neuf = 255.0 - np.asarray(Image.open(neta).convert("L")).astype(np.float32)
    LO, HO = vieux.shape[1], vieux.shape[0]
    LN, HN = neuf.shape[1], neuf.shape[0]
    sO, sN = W / LO, W / LN
    A, B = densito(vieux, W), densito(neuf, W)

    def essai(k, th, m=0.14):
        hA, wA = A.shape
        M = cv2.getRotationMatrix2D((wA / 2, hA / 2), th, k)
        r = cv2.warpAffine(A, M, (wA, hA), flags=cv2.INTER_LINEAR,
                           borderValue=0)
        y0, y1 = round(m * hA), round((1 - m) * hA)
        x0, x1 = round(m * wA), round((1 - m) * wA)
        g = r[y0:y1, x0:x1]
        if g.shape[0] >= B.shape[0] or g.shape[1] >= B.shape[1]:
            return None
        res = cv2.matchTemplate(B, g, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(res)
        return float(mx), float(k), float(th), loc, (x0, y0)

    best = None
    for k in np.arange(0.90, 1.101, 0.005):
        for th in np.arange(-1.0, 1.01, 0.1):
            e = essai(k, th)
            if e and (best is None or e[0] > best[0]):
                best = e
    for k in np.arange(best[1] - 0.006, best[1] + 0.0061, 0.0005):
        for th in np.arange(best[2] - 0.12, best[2] + 0.121, 0.01):
            e = essai(k, th)
            if e and e[0] > best[0]:
                best = e
    mx, k, th, loc, (gx, gy) = best
    hA, wA = A.shape
    M3 = np.vstack([cv2.getRotationMatrix2D((wA / 2, hA / 2), th, k), [0, 0, 1]])
    D = np.array([[1, 0, loc[0] - gx], [0, 1, loc[1] - gy], [0, 0, 1]], float)
    T = np.diag([1 / sN, 1 / sN, 1.0]) @ D @ M3 @ np.diag([sO, sO, 1.0])
    if verbeux:
        print(f"  {cle} : correlation {mx:.4f}, echelle {T[0, 0]:.5f}, "
              f"rotation {th:+.2f} deg")
        print(f"  l'ancienne planche ({LO} x {HO}) se pose en "
              f"({T[0, 2]:.0f}, {T[1, 2]:.0f}) de la nouvelle ({LN} x {HN})")
    return T, float(mx), (LO, HO), (LN, HN)


def _pt(T, x, y):
    q = T @ np.array([x, y, 1.0])
    return float(q[0]), float(q[1])


def deja_porte(cle):
    """Has this table already been carried onto its original?"""
    if not CATALOGO.exists():
        return False
    return "transporto" in json.loads(
        CATALOGO.read_text(encoding="utf-8")).get(cle, {})


# THE CARRYING OVER IS DONE ONLY ONCE. Doing it again would apply the
# similarity to positions that have already undergone it, and the
# fifteen hundred numbers would go off askew with nothing to signal it.
# The tool therefore refuses to start over, unless told to.
def transporti(cle, neta, verbeux=True, force=False):
    """Carries the numbers, the scenes and the sizes onto the new plate."""
    if deja_porte(cle) and not force:
        raise SystemExit(
            f"  {cle} : deja porte sur son original. Recommencer "
            f"deplacerait les numeros une seconde fois.\n"
            f"  Si c'est bien ce qu'on veut : ajouter « force ».")
    T, korelo, (LO, HO), (LN, HN) = mezuri(cle, neta, verbeux=verbeux)
    k = float(np.hypot(T[0, 0], T[1, 0]))

    # WHAT FALLS OUTSIDE THE PLATE IS NOT KEPT. The trim does not fall in
    # the same place from one redo to the next — it follows the rules, and
    # the rules are measured — so that a number placed right at the edge
    # may end up outside. To keep it is to promise a close-up on nothing.
    # We say so, and let it drop: it will have to be looked for again on
    # the new plate.
    perdus = []

    def boite(v, nom=""):
        """(x, y, w, h) as a fraction of the old -> of the new."""
        x, y = _pt(T, v[0] * LO, v[1] * HO)
        cx, cy = x + v[2] * LO * k / 2, y + v[3] * HO * k / 2
        if not (0 <= cx < LN and 0 <= cy < HN):
            perdus.append(nom)
            return None
        return [round(x / LN, 6), round(y / HN, 6),
                round(v[2] * LO * k / LN, 6), round(v[3] * HO * k / HN, 6)] \
            + list(v[4:])

    n = 0
    f = RACINE / "plates" / "numbers.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    if cle in d:
        e = d[cle]
        e["numeri"] = {q: b for q, v in e["numeri"].items()
                       if (b := boite(v, q)) is not None}
        e["largeur"], e["alteso"] = LN, HN
        e["corpo"] = max(1, round(e["corpo"] * k))
        n += len(e["numeri"])
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    m = 0
    f = RACINE / "plates" / "manual.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if cle in d:
            d[cle] = {q: b for q, v in d[cle].items()
                      if (b := boite(v, q)) is not None}
            m = len(d[cle])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    c = 0
    f = RACINE / "plates" / "scenes.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if cle in d:
            for sc, forme in d[cle].items():
                if forme[0] == "elipso":
                    x, y = _pt(T, forme[1] * LO, forme[2] * HO)
                    d[cle][sc] = ["elipso", round(x / LN, 6), round(y / HN, 6),
                                  round(forme[3] * LO * k / LN, 6),
                                  round(forme[4] * HO * k / HN, 6)]
                else:
                    x0, y0 = _pt(T, forme[1] * LO, forme[2] * HO)
                    x1, y1 = _pt(T, forme[3] * LO, forme[4] * HO)
                    d[cle][sc] = ["rekt", round(max(0.0, x0 / LN), 6),
                                  round(max(0.0, y0 / HN), 6),
                                  round(min(1.0, x1 / LN), 6),
                                  round(min(1.0, y1 / HN), 6)]
                c += 1
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    lt = 0
    f = RACINE / "plates" / "letters.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get(cle):
            d[cle] = {q: b for q, v in d[cle].items()
                      if (b := boite(v, q)) is not None}
            lt = len(d[cle])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
           if CATALOGO.exists() else {})
    e = cat.setdefault(cle, {})
    e["transporto"] = {"matrico": [[float(v) for v in r] for r in T[:2]],
                       "korelo": round(korelo, 4),
                       "de": [LO, HO], "a": [LN, HN]}
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    if verbeux:
        print(f"  {n} numeros portes, dont {m} poses a la main"
              + (f", {c} scenes" if c else "")
              + (f", {lt} lettres" if lt else ""))
        if perdus:
            print(f"  ATTENTION : {len(perdus)} sortis de la planche au "
                  f"rognage, a rechercher — {', '.join(sorted(perdus))}")
    return T


# -------------------------------------------------------------------
#  SERVING THE PLATE
# -------------------------------------------------------------------
#  Two sizes, as before: the general view set above the title, and the
#  image from which the close-ups are cut. But the latter is no longer
#  planed down to 2600 points: WE SERVE THE WHOLE PLATE.
#
#  The measurement calls for it. The close-up shows nine figure heights,
#  that is two hundred and ninety points of plate, on two hundred and
#  fifty points of screen — five hundred on a double-density screen.
#  Even at full resolution we are therefore short: trimming further
#  would make no sense. At 2600 points, moreover, the fine hatching
#  moirés, which is unforgivable on a wood engraving.
#
#  The image costs only at the FIRST click on a number of the table, and
#  serves all the others afterwards.
LARGE_VIDO = 1200
QUAL_VIDO = 74
QUAL_DETALO = 74


# THE DETAIL'S QUALITY IS SET PLATE BY PLATE. The facsimile is four
# thousand five hundred points wide: at seventy-four, the WebP has room
# and loses nothing visible. The colour original has only two thousand
# two hundred, and the same quality made it lumpy — the « PIANOS » of
# building (10) on table 14 read less well there than on the original
# PDF. Fewer points, more quality: the file stays lighter than a
# facsimile's.
# -------------------------------------------------------------------
#  THE TONE: GIVING THE PLATE ITS BLACK BACK
# -------------------------------------------------------------------
#  THE FOURTEEN GREY PLATES HAD NO BLACK. Their darkest ink stopped
#  between 45 and 65 out of 255, and at most one point in ten thousand
#  went below 40 -- when the two colour plates, served beside them in
#  the same gallery, go down to 11 and 13 with three or four points in a
#  hundred truly black. It was that neighbourhood the eye read as
#  paleness.
#
#  IT WAS NOT OUR PROCESSING: clean straightens and trims, it did not
#  touch the tone. The paleness comes from the original scans.
#
#  WE THEREFORE STRETCH BETWEEN TWO PERCENTILES, plate by plate -- the
#  scans differ too much for a common setting. The black point at
#  percentile 0.05, the white point at percentile 99.5.
#
#  THE WHITE POINT WAS THE DISPUTED POINT, and measurement settled it
#  against intuition. Moving it crushes six points in a thousand to
#  white, against three before: we first thought it was the grain of the
#  paper going. The reading says otherwise. The mean gradient where we
#  crush is 16 to 18, that is, that of the rest of the plate; only two
#  points in a thousand of those have no neighbour different from
#  themselves. These are not flats of paper: they are the LIGHT edge of
#  the strokes. Whitening them removes no line, it detaches the line
#  from its paper. The count of weak gradients in light areas -- the
#  fine hatching, what we risked losing -- confirms it: it rises to
#  107-111 per cent after stretching, exactly as if we had kept the
#  white at 255.
#
#  AND KEEPING THE WHITE AT 255 COST MORE THAN IT SAVED. The median
#  paper then fell from 227 to 217, when the ground of the reading page
#  is 250: the plate settled on the page as a rectangle greyer than
#  before. At percentile 99.5 it stays at 224.
#
#  APPROACH TRIED AND ABANDONED: a soft knee instead of a clean clip,
#  so as to crush nothing at all. It is the only one of the four
#  variants that harms the drawing -- the fine hatching falls to 86-93
#  per cent, because the curve packs precisely the top of the signal,
#  where the light stroke lives. Withdrawn.
#
#  WE DO NOT GO BEYOND PERCENTILE 99.5, and that too was measured: at
#  percentile 98 the fine hatching still holds (103-108 %), at
#  percentile 96 it starts to fall (91 % on table 7), at percentile 92
#  it collapses (63 %). The gain in standard deviation between 99.5 and
#  98 is only two per cent. We stop where the gain ceases to pay.
#
#  THE TWO COLOUR PLATES DO NOT GO THROUGH THIS: colourise.py calls
#  serve() with tone=False. They already have their black.
TONO_NOIR = 0.05
TONO_BLANC = 99.5


def tonigar(im):
    """Stretches the tone between two percentiles. Returns image and bounds."""
    a = np.asarray(im.convert("L")).astype(np.float32)
    noir = float(np.percentile(a, TONO_NOIR))
    blanc = float(np.percentile(a, TONO_BLANC))
    if blanc - noir < 1.0:
        return im, None
    b = np.clip((np.asarray(im).astype(np.float32) - noir) / (blanc - noir),
                0, 1) * 255.0
    return (Image.fromarray(np.round(b).astype(np.uint8), mode=im.mode),
            {"noir": round(noir, 1), "blanc": round(blanc, 1),
             "faktoro": round(255.0 / (blanc - noir), 4)})


def servir(cle, neta, verbeux=True, qual_detalo=None, tono=True):
    """The two WebPs, drawn from the cleaned original plate."""
    im = Image.open(neta).convert("RGB")
    par_tono = None
    if tono:
        im, par_tono = tonigar(im)
        if verbeux and par_tono:
            print(f"  ton : noir {par_tono['noir']:.0f}, "
                  f"blanc {par_tono['blanc']:.0f}, "
                  f"facteur x{par_tono['faktoro']:.3f}")
    GRAVURI = RACINE / "plates"
    taille = {}
    for nom, largeur, qualite in (("vido", LARGE_VIDO, QUAL_VIDO),
                                  ("detalo", im.width,
                                   qual_detalo or QUAL_DETALO)):
        h = round(largeur * im.height / im.width)
        petite = im if largeur == im.width else im.resize((largeur, h),
                                                          Image.LANCZOS)
        dest = GRAVURI / f"{cle}-{nom}.webp"
        petite.save(dest, format="WEBP", quality=qualite, method=6)
        o = dest.stat().st_size
        taille[nom] = {"largeur": petite.width, "alteso": petite.height,
                       "okteti": o}
        if verbeux:
            print(f"  {cle}-{nom}.webp  {petite.width}x{petite.height}  "
                  f"{o / 1024:.0f} Ko")
    cat = GRAVURI / "plates.json"
    tout = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    tout[cle] = {"largeur": im.width, "alteso": im.height,
                 "koloro": False, "fonto": Path(neta).name,
                 "origino": True,
                 "vido": taille["vido"], "detalo": taille["detalo"]}
    if par_tono:
        tout[cle]["tono"] = par_tono
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")


# -------------------------------------------------------------------
#  THE WHOLE REDO, IN ONE COMMAND
# -------------------------------------------------------------------
#  Clean, carry the numbers over, serve the two images: three motions
#  that always go together and in that order. Fifteen plates remain to
#  be redone; better not to type them three times each.
#
#      python3 tools/originals.py redo t02-apar-1 originals/t02.jpg
def reprendre(cle, chemin, force=False):
    dest = RACINE / "originals" / "kovri" / f"{cle}-neta.png"
    # We set the previous plate aside: it is on THAT one that the
    # numbers are placed, and it is from it that they will have to be
    # carried over.
    if dest.exists():
        dest.replace(dest.with_name(f"{cle}-neta-antaua.png"))
    out, par = netigar(chemin, dest)
    cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
           if CATALOGO.exists() else {})
    e = cat.setdefault(cle, {})
    e["fonto"] = str(chemin)
    e["netigo"] = par
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    transporti(cle, dest, force=force)
    servir(cle, dest)
    print(f"  {cle} : repris. Verifier la planche de controle, "
          f"puis relancer numeri.py et html.py.")


# -------------------------------------------------------------------
#  REDOING THE TONE OF THE GREY PLATES
# -------------------------------------------------------------------
#  The tone is computed at each serving, from the lossless PNG: this
#  verb therefore only re-serves. It is idempotent -- it can be run
#  again without stacking two stretches one on the other, because
#  nothing is ever written into the original PNG.
#
#      python3 tools/originals.py tone
def toni():
    cat = json.loads((RACINE / "plates" / "plates.json")
                     .read_text(encoding="utf-8"))
    kovri = RACINE / "originals" / "kovri"
    n = 0
    for cle in sorted(cat):
        if cat[cle].get("koloro"):
            print(f"{cle} : en couleur, laissee telle quelle")
            continue
        neta = kovri / f"{cle}-neta.png"
        if not neta.exists():
            print(f"{cle} : {neta.name} introuvable, passee")
            continue
        print(f"{cle} :")
        servir(cle, neta)
        n += 1
    print(f"\n{n} planches re-servies avec leur ton redresse.")


def main(args):
    if args and args[0] == "toni":
        return toni()
    if len(args) < 2:
        raise SystemExit(__doc__)
    verbe, cle, chemin = args[0], args[1], args[2]
    if verbe == "reprendre":
        reprendre(cle, chemin, force="force" in args)
    elif verbe == "netigar":
        cle_ = cle
        out, par = netigar(chemin, RACINE / "originals" / "kovri" /
                           f"{cle_}-neta.png")
        cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
               if CATALOGO.exists() else {})
        e = cat.setdefault(cle_, {})
        e["fonto"] = str(chemin)
        e["netigo"] = par
        CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verbe == "servir":
        servir(cle, chemin)
    elif verbe == "toni":
        toni()
    elif verbe == "transporti":
        transporti(cle, chemin, force="force" in args)
    elif verbe == "caler":
        M, score, tour = caler(cle, chemin)
        cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
               if CATALOGO.exists() else {})
        cat[cle] = {"fonto": str(chemin), "tour": tour,
                    "matrico": [[float(v) for v in r] for r in M],
                    "korelo": round(float(score), 4)}
        CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verbe == "compar":
        cx = float(args[3]) if len(args) > 3 else 0.5
        cy = float(args[4]) if len(args) > 4 else 0.5
        compar(cle, chemin, cx, cy)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
