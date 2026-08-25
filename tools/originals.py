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
ROOT = N.ROOT
CATALOGUE = ROOT / "plates" / "originals.json"


def grey_(path):
    """The image in grey, the ink in black, as a normalised float."""
    im = Image.open(path)
    if im.mode not in ("L", "I;16"):
        im = im.convert("L")
    a = np.asarray(im).astype(np.float32)
    if a.max() > 255:
        a = a / 257.0
    return a


def our_line_layer(key):
    """Our line layer, put back the right way round: the ink in black."""
    a = np.asarray(Image.open(N.WORKING / f"{key}-trako.png")).astype(np.float32)
    return 255.0 - a


def centre_(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 1e-6 else a


# THE PLATE MAY BE LYING ON ITS SIDE IN THE SCAN. The leaves are bound
# the tall way and the engraving lies across them; we therefore try all
# four quarter turns, and keep the one that catches.
def orientations(a):
    for k in range(4):
        yield k, np.rot90(a, k)


def register_scan(key, path, wide=1100, verbose=True):
    """The similarity that leads from our plate to the scan.

    Returns (M, score, turn): M is the 2x3 matrix that sends a point of
    OUR plate, in points, onto the scan, in points.
    """
    src = our_line_layer(key)
    HS, LS = src.shape
    dst0 = grey_(path)
    small_src = cv2.resize(src, (wide, round(wide * HS / LS)),
                           interpolation=cv2.INTER_AREA)
    sc_src = LS / wide
    best = None
    for turn, dst in orientations(dst0):
        HD, LD = dst.shape
        if LD < 200 or HD < 200:
            continue
        f = wide / max(LD, HD)
        small_dst = cv2.resize(dst, (max(1, round(LD * f)),
                                     max(1, round(HD * f))),
                               interpolation=cv2.INTER_AREA)
        sc_dst = 1 / f
        # The engraving occupies only part of the leaf: we look for our
        # plate WITHIN the page, at several scales.
        g = centre_(small_dst)
        for r in np.arange(0.45, 1.02, 0.025):
            w = round(small_src.shape[1] * r)
            h = round(small_src.shape[0] * r)
            if w < 80 or h < 80 or w > g.shape[1] or h > g.shape[0]:
                continue
            s = centre_(cv2.resize(small_src, (w, h),
                                   interpolation=cv2.INTER_AREA))
            m = cv2.matchTemplate(g, s, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(m)
            if best is None or mx > best[0]:
                best = (mx, turn, r, loc, sc_dst, w, h)
    if best is None:
        raise SystemExit("  rien a caler")
    score, turn, r, (x0, y0), sc_dst, w, h = best
    # From our plate (points) to the TURNED scan (points).
    k = r / sc_src * sc_dst
    M = np.array([[k, 0.0, x0 * sc_dst],
                  [0.0, k, y0 * sc_dst]], np.float32)
    if verbose:
        print(f"  {key} : quart de tour {turn}, echelle {k:.4f}, "
              f"coin ({round(x0 * sc_dst)}, {round(y0 * sc_dst)}), "
              f"correlation {score:.3f}")
        print(f"  la gravure y mesure {round(LS * k)} x {round(HS * k)} "
              f"points (nous : {LS} x {HS})")
    return M, score, turn


def load_turned(path, turn):
    a = grey_(path)
    return np.rot90(a, turn)


def compare(key, path, cx=0.5, cy=0.5, w=0.115, h=0.095, out_path=None):
    """The same detail in all three states, side by side."""
    M, score, turn = register_scan(key, path)
    ori = load_turned(path, turn)
    HS, LS = np.asarray(Image.open(N.WORKING / f"{key}-trako.png")).shape
    x0f, y0f = cx - w / 2, cy - h / 2

    def cut_orig():
        p = np.array([[x0f * LS, y0f * HS, 1.0],
                      [(x0f + w) * LS, (y0f + h) * HS, 1.0]]).T
        q = M @ p
        return Image.fromarray(ori.astype(np.uint8)).crop(
            (round(q[0, 0]), round(q[1, 0]), round(q[0, 1]), round(q[1, 1])))

    views = [(cut_orig(), "la numerisation d'origine")]
    for name_, im, what in (
            ("detalo", Image.open(ROOT / "plates" / f"{key}-detalo.webp")
             .convert("L"), "ce que la page sert"),
            ("trako", ImageOps.invert(Image.open(N.WORKING / f"{key}-trako.png")
                                      .convert("L")), "notre couche de trait")):
        W_, H_ = im.size
        views.append((im.crop((round(x0f * W_), round(y0f * H_),
                              round((x0f + w) * W_), round((y0f + h) * H_))),
                     what))
    OUT = (1000, round(1000 * h / w * (HS / LS) / 1.0))
    F = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
    F2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
    pl = Image.new("RGB", (3 * (OUT[0] + 16) + 16, OUT[1] + 90),
                   (255, 255, 255))
    d = ImageDraw.Draw(pl)
    for i, (c, t) in enumerate(views):
        n = f"{c.width} x {c.height} points pour ce detail"
        c = c.resize(OUT, Image.LANCZOS).convert("RGB")
        X = 16 + i * (OUT[0] + 16)
        pl.paste(c, (X, 16))
        d.rectangle([X, 16, X + OUT[0], 16 + OUT[1]], outline=(190, 0, 0),
                    width=2)
        d.text((X, OUT[1] + 26), t, fill=(0, 0, 0), font=F)
        d.text((X, OUT[1] + 54), n, fill=(90, 90, 90), font=F2)
    out_path = Path(out_path or (ROOT / "plates" / "review" /
                             f"{key}-origino.png"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pl.save(out_path)
    print(f"  comparaison dans {out_path}")


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
RULE_MARGIN = 8


def _turn(a, th, centre):
    return cv2.getRotationMatrix2D(centre, th, 1.0)


def rule_angle(ink_, band, axe, ampl=1.2, pas=0.025):
    """The angle that makes a line of the frame sharpest."""
    best = None
    y0, y1, x0, x1 = band
    b = ink_[y0:y1, x0:x1]
    for th in np.arange(-ampl, ampl + 1e-9, pas):
        M = _turn(b, th, (b.shape[1] / 2, b.shape[0] / 2))
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
def best_rule(ink_, a0, a1, x0, x1, cand=8):
    """A band's rule: the candidate we follow best."""
    prof = ink_[a0:a1, round(0.20 * ink_.shape[1]):
               round(0.80 * ink_.shape[1])].mean(1)
    order_ = np.argsort(prof)[::-1]
    taken = []
    for i in order_:
        if all(abs(int(i) - j) > 25 for j in taken):
            taken.append(int(i))
        if len(taken) >= cand:
            break
    best = None
    for i in taken:
        y = a0 + i
        m = follow_rule(ink_, max(0, y - 22), min(ink_.shape[0], y + 23),
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
def _paper(q, margin):
    m = round(margin * len(q))
    return float(np.percentile(q[:m], 20)), float(np.median(q[m:]))


def side_rule(q, margin=0.30, wide=20):
    """The first thin peak that rises above the paper."""
    floor, solid = _paper(q, margin)
    top = max(6.0, 0.25 * (solid - floor))
    for i in range(2, len(q) - 2):
        if q[i] >= q[i - 1] and q[i] > q[i + 1] and q[i] - floor >= top:
            mi = floor + (q[i] - floor) / 2
            a, b = i, i
            while a > 0 and q[a] > mi:
                a -= 1
            while b < len(q) - 1 and q[b] > mi:
                b += 1
            if b - a <= wide:
                return i
    return None


def drawing_entry(q, margin=0.30, tenue=20):
    """The place where the ink rises to half-full and stays there."""
    floor, solid = _paper(q, margin)
    if solid - floor < 4:
        return None
    threshold = floor + 0.40 * (solid - floor)
    for i in range(len(q) - tenue):
        if (q[i:i + tenue] > threshold).all():
            return i
    return None


def side_edge(prof, way):
    """One side's edge: the outer of the two measurements."""
    q = np.asarray(prof, dtype=float)
    if way < 0:
        q = q[::-1]
    pair_ = [i for i in (side_rule(q), drawing_entry(q)) if i is not None]
    if not pair_:
        return None
    i = min(pair_)
    return i if way > 0 else len(q) - 1 - i


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
def follow_rule(ink_, y0, y1, x0, x1, pas=40, window=14):
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
        col = ink_[y0:y1, x:x + pas].mean(1)
        if col.max() < 8:
            continue
        i = int(np.argmax(col))
        a0, b0 = max(0, i - window), min(len(col), i + window + 1)
        w = col[a0:b0]
        if w.sum() <= 0:
            continue
        xs.append(x + pas / 2)
        ys.append(y0 + a0 + float((w * np.arange(len(w))).sum() / w.sum()))
        fs.append(float(w.max() - np.median(col)))
    if len(xs) < 8:
        return None
    X, Y, F = np.array(xs), np.array(ys), np.array(fs)
    keep = F >= 0.5 * float(np.median(F))
    if keep.sum() >= 8:
        X, Y = X[keep], Y[keep]
    m = c = 0.0
    for _ in range(4):
        A = np.vstack([X, np.ones_like(X)]).T
        (m, c), *_ = np.linalg.lstsq(A, Y, rcond=None)
        r = np.abs(Y - (m * X + c))
        threshold = max(2.0, 3.0 * float(np.median(r)))
        g = r <= threshold
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
def frame(ink_, yh, yb):
    """The frame of an already straightened image, horizontals known."""
    H, W = ink_.shape
    mh, mv = round(0.045 * H), round(0.035 * W)

    def register_scan(y, r=20):
        a, b = max(0, y - r), min(H, y + r + 1)
        p = ink_[a:b, mv:W - mv].mean(1)
        return a + int(np.argmax(p)), float(p.max() - np.median(p))

    top, fh = register_scan(yh) if yh is not None else (round(0.055 * H), 0.0)
    bottom, fb = register_scan(yb) if yb is not None else (round(0.905 * H), 0.0)
    pg = ink_[mh:H - mh, 0:round(0.12 * W)].mean(0)
    pd = ink_[mh:H - mh, round(0.88 * W):W].mean(0)
    g = side_edge(pg, +1)
    d = side_edge(pd, -1)
    lef = 0 if g is None else g
    rig = W - 1 if d is None else round(0.88 * W) + d
    return (lef, top, rig, bottom), (0.0, fh, 0.0, fb)


def clean_up(path, dest=None, verbose=True):
    """Straightens and trims a scan, in a single resampling."""
    im = Image.open(path)
    a = np.asarray(im.convert("L"))
    # THE SHEET IS BOUND THE TALL WAY, the engraving lies across it.
    turn = 3 if a.shape[0] > a.shape[1] else 0
    a = np.rot90(a, turn)
    H, W = a.shape
    ink_ = np.clip(200.0 - a.astype(np.float32), 0, None)
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
    rh = best_rule(ink_, round(0.045 * H), round(0.100 * H), X0, X1)
    rb = best_rule(ink_, round(0.875 * H), round(0.925 * H), X0, X1)
    mh, yh = rh if rh else (None, None)
    mb, yb = rb if rb else (None, None)
    # WHEN THE TWO RULES CONTRADICT EACH OTHER, WE BELIEVE THE BETTER
    # MEASURED. They agree to within a tenth of a degree on eleven plates;
    # on the other five one of the two was followed on half as many
    # columns, and it is that one that departs. The weight of a measurement
    # is the number of columns kept divided by its fitting residual.
    def weight(m):
        return m[2] / (m[1] + 0.5) if m else 0.0

    pair_ = [m for m in (mh, mb) if m]
    if len(pair_) == 2 and abs(mh[0] - mb[0]) > 0.35:
        th = max(pair_, key=weight)[0]
    elif pair_:
        pt = sum(weight(m) for m in pair_)
        th = sum(m[0] * weight(m) for m in pair_) / pt
    else:
        th = 0.0
    # 2. the frame, measured on a straightened copy (thrown away after)
    Mr = _turn(a, th, (W / 2, H / 2))
    right = cv2.warpAffine(ink_, Mr, (W, H), flags=cv2.INTER_LINEAR,
                           borderValue=0)
    (x0, y0, x1, y1), strengths = frame(right, yh, yb)
    x0, y0 = x0 - RULE_MARGIN, y0 - RULE_MARGIN
    x1, y1 = x1 + RULE_MARGIN, y1 + RULE_MARGIN
    # 3. rotation AND trim in a single matrix, a single pass
    M = Mr.copy()
    M[0, 2] -= x0
    M[1, 2] -= y0
    LG, HT = x1 - x0, y1 - y0
    src = np.rot90(np.asarray(im.convert("L")), turn)
    out = cv2.warpAffine(src, M, (LG, HT), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    # check: what skew is left in the verticals
    e2 = np.clip(200.0 - out.astype(np.float32), 0, None)
    vg = rule_angle(e2, (round(.05*HT), round(.95*HT), 0, 40), 0, 1.0)[1]
    vd = rule_angle(e2, (round(.05*HT), round(.95*HT), LG-40, LG), 0, 1.0)[1]
    if verbose:
        def say(m):
            return (f"{m[0]:+.3f} (ecart {m[1]:.2f} sur {m[2]} points)"
                    if m else "introuvable")
        print(f"  quart de tour {turn}, redressement {th:+.3f} deg")
        print(f"    filet du haut : {say(mh)}")
        print(f"    filet du bas  : {say(mb)}")
        print(f"  cadre en ({x0}, {y0})-({x1}, {y1}) : {LG} x {HT} points")
        print(f"  verticales laissees de biais : {vg:+.3f} et {vd:+.3f} deg")
    if dest:
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(out).save(dest)
        if verbose:
            print(f"  ecrit dans {dest}")
    return out, {"tour": turn, "angulo": round(th, 4),
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
def ink_density(a, W, sigma=1.6):
    """An ink density map, comparable from one rendering to another."""
    h = round(W * a.shape[0] / a.shape[1])
    s = cv2.resize(a.astype(np.float32), (W, h), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), sigma)
    return (s - s.mean()) / (s.std() + 1e-6)


def measure_shift(key, clean_, W=1000, verbose=True):
    """The matrix that leads from the old plate to the new one."""
    # THE REFERENCE IS THE PREVIOUS PLATE, whatever it may be. The first
    # time it is the line layer of the colourised PDF, where the ink is
    # 255; afterwards, if we clean again, it is the already cleaned
    # facsimile, where the ink is dark. Without that a second cleaning
    # would start the numbers off from the stencil, which they have left.
    old_ = ROOT / "originals" / "kovri" / f"{key}-neta-antaua.png"
    if old_.exists():
        old = 255.0 - np.asarray(Image.open(old_).convert("L")
                                   ).astype(np.float32)
    else:
        old = np.asarray(Image.open(N.WORKING / f"{key}-trako.png")
                           ).astype(np.float32)      # the ink is 255 there
    fresh = 255.0 - np.asarray(Image.open(clean_).convert("L")).astype(np.float32)
    LO, HO = old.shape[1], old.shape[0]
    LN, HN = fresh.shape[1], fresh.shape[0]
    sO, sN = W / LO, W / LN
    A, B = ink_density(old, W), ink_density(fresh, W)

    def trial(k, th, m=0.14):
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
            e = trial(k, th)
            if e and (best is None or e[0] > best[0]):
                best = e
    for k in np.arange(best[1] - 0.006, best[1] + 0.0061, 0.0005):
        for th in np.arange(best[2] - 0.12, best[2] + 0.121, 0.01):
            e = trial(k, th)
            if e and e[0] > best[0]:
                best = e
    mx, k, th, loc, (gx, gy) = best
    hA, wA = A.shape
    M3 = np.vstack([cv2.getRotationMatrix2D((wA / 2, hA / 2), th, k), [0, 0, 1]])
    D = np.array([[1, 0, loc[0] - gx], [0, 1, loc[1] - gy], [0, 0, 1]], float)
    T = np.diag([1 / sN, 1 / sN, 1.0]) @ D @ M3 @ np.diag([sO, sO, 1.0])
    if verbose:
        print(f"  {key} : correlation {mx:.4f}, echelle {T[0, 0]:.5f}, "
              f"rotation {th:+.2f} deg")
        print(f"  l'ancienne planche ({LO} x {HO}) se pose en "
              f"({T[0, 2]:.0f}, {T[1, 2]:.0f}) de la nouvelle ({LN} x {HN})")
    return T, float(mx), (LO, HO), (LN, HN)


def _pt(T, x, y):
    q = T @ np.array([x, y, 1.0])
    return float(q[0]), float(q[1])


def already_carried(key):
    """Has this table already been carried onto its original?"""
    if not CATALOGUE.exists():
        return False
    return "transporto" in json.loads(
        CATALOGUE.read_text(encoding="utf-8")).get(key, {})


# THE CARRYING OVER IS DONE ONLY ONCE. Doing it again would apply the
# similarity to positions that have already undergone it, and the
# fifteen hundred numbers would go off askew with nothing to signal it.
# The tool therefore refuses to start over, unless told to.
def carry_over(key, clean_, verbose=True, force=False):
    """Carries the numbers, the scenes and the sizes onto the new plate."""
    if already_carried(key) and not force:
        raise SystemExit(
            f"  {key} : deja porte sur son original. Recommencer "
            f"deplacerait les numeros une seconde fois.\n"
            f"  Si c'est bien ce qu'on veut : ajouter « force ».")
    T, correlation, (LO, HO), (LN, HN) = measure_shift(key, clean_, verbose=verbose)
    k = float(np.hypot(T[0, 0], T[1, 0]))

    # WHAT FALLS OUTSIDE THE PLATE IS NOT KEPT. The trim does not fall in
    # the same place from one redo to the next — it follows the rules, and
    # the rules are measured — so that a number placed right at the edge
    # may end up outside. To keep it is to promise a close-up on nothing.
    # We say so, and let it drop: it will have to be looked for again on
    # the new plate.
    losts = []

    def box(v, name_=""):
        """(x, y, w, h) as a fraction of the old -> of the new."""
        x, y = _pt(T, v[0] * LO, v[1] * HO)
        cx, cy = x + v[2] * LO * k / 2, y + v[3] * HO * k / 2
        if not (0 <= cx < LN and 0 <= cy < HN):
            losts.append(name_)
            return None
        return [round(x / LN, 6), round(y / HN, 6),
                round(v[2] * LO * k / LN, 6), round(v[3] * HO * k / HN, 6)] \
            + list(v[4:])

    n = 0
    f = ROOT / "plates" / "numbers.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    if key in d:
        e = d[key]
        e["numeri"] = {q: b for q, v in e["numeri"].items()
                       if (b := box(v, q)) is not None}
        e["largeur"], e["alteso"] = LN, HN
        e["corpo"] = max(1, round(e["corpo"] * k))
        n += len(e["numeri"])
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    m = 0
    f = ROOT / "plates" / "manual.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if key in d:
            d[key] = {q: b for q, v in d[key].items()
                      if (b := box(v, q)) is not None}
            m = len(d[key])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    c = 0
    f = ROOT / "plates" / "scenes.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if key in d:
            for sc, shape_ in d[key].items():
                if shape_[0] == "elipso":
                    x, y = _pt(T, shape_[1] * LO, shape_[2] * HO)
                    d[key][sc] = ["elipso", round(x / LN, 6), round(y / HN, 6),
                                  round(shape_[3] * LO * k / LN, 6),
                                  round(shape_[4] * HO * k / HN, 6)]
                else:
                    x0, y0 = _pt(T, shape_[1] * LO, shape_[2] * HO)
                    x1, y1 = _pt(T, shape_[3] * LO, shape_[4] * HO)
                    d[key][sc] = ["rekt", round(max(0.0, x0 / LN), 6),
                                  round(max(0.0, y0 / HN), 6),
                                  round(min(1.0, x1 / LN), 6),
                                  round(min(1.0, y1 / HN), 6)]
                c += 1
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    lt = 0
    f = ROOT / "plates" / "letters.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get(key):
            d[key] = {q: b for q, v in d[key].items()
                      if (b := box(v, q)) is not None}
            lt = len(d[key])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    cat = (json.loads(CATALOGUE.read_text(encoding="utf-8"))
           if CATALOGUE.exists() else {})
    e = cat.setdefault(key, {})
    e["transporto"] = {"matrico": [[float(v) for v in r] for r in T[:2]],
                       "korelo": round(correlation, 4),
                       "de": [LO, HO], "a": [LN, HN]}
    CATALOGUE.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    if verbose:
        print(f"  {n} numeros portes, dont {m} poses a la main"
              + (f", {c} scenes" if c else "")
              + (f", {lt} lettres" if lt else ""))
        if losts:
            print(f"  ATTENTION : {len(losts)} sortis de la planche au "
                  f"rognage, a rechercher — {', '.join(sorted(losts))}")
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
VIEW_WIDTH = 1200
VIEW_QUALITY = 74
DETAIL_QUALITY = 74


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
TONE_BLACK = 0.05
TONE_WHITE = 99.5


def stretch_tone(im):
    """Stretches the tone between two percentiles. Returns image and bounds."""
    a = np.asarray(im.convert("L")).astype(np.float32)
    black = float(np.percentile(a, TONE_BLACK))
    white = float(np.percentile(a, TONE_WHITE))
    if white - black < 1.0:
        return im, None
    b = np.clip((np.asarray(im).astype(np.float32) - black) / (white - black),
                0, 1) * 255.0
    return (Image.fromarray(np.round(b).astype(np.uint8), mode=im.mode),
            {"noir": round(black, 1), "blanc": round(white, 1),
             "faktoro": round(255.0 / (white - black), 4)})


def serve(key, clean_, verbose=True, detail_quality=None, tone=True):
    """The two WebPs, drawn from the cleaned original plate."""
    im = Image.open(clean_).convert("RGB")
    by_tone = None
    if tone:
        im, by_tone = stretch_tone(im)
        if verbose and by_tone:
            print(f"  ton : noir {by_tone['noir']:.0f}, "
                  f"blanc {by_tone['blanc']:.0f}, "
                  f"facteur x{by_tone['faktoro']:.3f}")
    PLATES = ROOT / "plates"
    size_ = {}
    for name_, width_, quality_ in (("vido", VIEW_WIDTH, VIEW_QUALITY),
                                  ("detalo", im.width,
                                   detail_quality or DETAIL_QUALITY)):
        h = round(width_ * im.height / im.width)
        small = im if width_ == im.width else im.resize((width_, h),
                                                          Image.LANCZOS)
        dest = PLATES / f"{key}-{name_}.webp"
        small.save(dest, format="WEBP", quality=quality_, method=6)
        o = dest.stat().st_size
        size_[name_] = {"largeur": small.width, "alteso": small.height,
                       "okteti": o}
        if verbose:
            print(f"  {key}-{name_}.webp  {small.width}x{small.height}  "
                  f"{o / 1024:.0f} Ko")
    cat = PLATES / "plates.json"
    everything = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    everything[key] = {"largeur": im.width, "alteso": im.height,
                 "koloro": False, "fonto": Path(clean_).name,
                 "origino": True,
                 "vido": size_["vido"], "detalo": size_["detalo"]}
    if by_tone:
        everything[key]["tono"] = by_tone
    cat.write_text(json.dumps(everything, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")


# -------------------------------------------------------------------
#  THE WHOLE REDO, IN ONE COMMAND
# -------------------------------------------------------------------
#  Clean, carry the numbers over, serve the two images: three motions
#  that always go together and in that order. Fifteen plates remain to
#  be redone; better not to type them three times each.
#
#      python3 tools/originals.py redo t02-apar-1 originals/t02.jpg
def redo(key, path, force=False):
    dest = ROOT / "originals" / "kovri" / f"{key}-neta.png"
    # We set the previous plate aside: it is on THAT one that the
    # numbers are placed, and it is from it that they will have to be
    # carried over.
    if dest.exists():
        dest.replace(dest.with_name(f"{key}-neta-antaua.png"))
    out, per = clean_up(path, dest)
    cat = (json.loads(CATALOGUE.read_text(encoding="utf-8"))
           if CATALOGUE.exists() else {})
    e = cat.setdefault(key, {})
    e["fonto"] = str(path)
    e["netigo"] = per
    CATALOGUE.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    carry_over(key, dest, force=force)
    serve(key, dest)
    print(f"  {key} : repris. Verifier la planche de controle, "
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
def tone_all():
    cat = json.loads((ROOT / "plates" / "plates.json")
                     .read_text(encoding="utf-8"))
    working = ROOT / "originals" / "kovri"
    n = 0
    for key in sorted(cat):
        if cat[key].get("koloro"):
            print(f"{key} : en couleur, laissee telle quelle")
            continue
        clean_ = working / f"{key}-neta.png"
        if not clean_.exists():
            print(f"{key} : {clean_.name} introuvable, passee")
            continue
        print(f"{key} :")
        serve(key, clean_)
        n += 1
    print(f"\n{n} planches re-servies avec leur ton redresse.")


def hand(args):
    if args and args[0] == "toni":
        return tone_all()
    if len(args) < 2:
        raise SystemExit(__doc__)
    verb, key, path = args[0], args[1], args[2]
    if verb == "reprendre":
        redo(key, path, force="force" in args)
    elif verb == "netigar":
        key_ = key
        out, per = clean_up(path, ROOT / "originals" / "kovri" /
                           f"{key_}-neta.png")
        cat = (json.loads(CATALOGUE.read_text(encoding="utf-8"))
               if CATALOGUE.exists() else {})
        e = cat.setdefault(key_, {})
        e["fonto"] = str(path)
        e["netigo"] = per
        CATALOGUE.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verb == "servir":
        serve(key, path)
    elif verb == "toni":
        tone_all()
    elif verb == "transporti":
        carry_over(key, path, force="force" in args)
    elif verb == "caler":
        M, score, turn = register_scan(key, path)
        cat = (json.loads(CATALOGUE.read_text(encoding="utf-8"))
               if CATALOGUE.exists() else {})
        cat[key] = {"fonto": str(path), "tour": turn,
                    "matrico": [[float(v) for v in r] for r in M],
                    "korelo": round(float(score), 4)}
        CATALOGUE.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verb == "compar":
        cx = float(args[3]) if len(args) > 3 else 0.5
        cy = float(args[4]) if len(args) > 4 else 0.5
        compare(key, path, cx, cy)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    hand(sys.argv[1:])
