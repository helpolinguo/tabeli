#!/usr/bin/env python3
# ===================================================================
#  numbering.py — finding the object numbers on a wall plate.
#
#  Each plate carries, set against the object it designates, a small
#  composed number: it is what the « (N) » of the text refer to. For a
#  click on « (12) » to be able to show object 12, one must know WHERE
#  the 12 is on the plate. That is what this tool does, and it returns a
#  report of what it has read, plate by plate.
#
#  WHAT THE TOOL DOES NOT DO. It does not read every number — far from
#  it. On the airy plates it finds eight in ten, on the busiest two or
#  three. The reason lies in the drawing itself: the number is set in a
#  small reserve of white, and when the engraving is dense that reserve
#  closes up, the figure touches a hatching, and nothing distinguishes
#  it any longer from a fragment of drawing. We therefore return the
#  list of WHAT HAS BEEN READ, with its check sheet; what is missing
#  stays without a close-up rather than receive a false one.
#
#  THE METHOD, in three stages:
#
#  1. THE ISLANDS. The line work is binary (the tool works on the line
#     layer produced by plates.py, where the ink is 255). We take the
#     connected components the size of a figure, and keep those a ring
#     of white separates from the rest: it is the printer's reserve
#     that serves as a signature.
#
#  2. THE SHAPE. Each island is reduced to a 40x32 thumbnail and
#     compared with the ten models in tools/ciphers.npz. Those models
#     are not drawn by hand: they come out of a clustering of 1429
#     islands taken from the fifteen plates, the font being the same
#     throughout. A « 1 » is only a bar, and vertical hatchings look
#     like it: it therefore carries a threshold of its own.
#
#  3. THE NEIGHBOURHOOD. The figures of one number follow each other on
#     the same baseline, less than half a body apart. We glue them back
#     together, then keep ONLY the expected numbers — those the table's
#     text calls for — and read once only. A number read twice is a
#     number about which nothing is known.
#
#  USAGE
#      python3 tools/numbering.py                 # every plate
#      python3 tools/numbering.py t05-apar-1      # just one
#
#  Writes plates/numbers.json (the positions, as a fraction of the
#  plate's width and height, hence valid at any scale) and, in
#  plates/review/, one check sheet per engraving: each number read is
#  shown there in its cut-out, with what the machine thought it read.
#  That is where one checks.
# ===================================================================

import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
WORKING = ROOT / "plates" / "kovri"
REVIEW = ROOT / "plates" / "review"

H, W = 40, 32
# A « 1 » without a serif is a bar, and an engraved plate is full of
# them. We therefore ask more of it than of the others.
THRESHOLD = 0.80
THRESHOLD_ONE = 0.86



# THE WORKING PLATE. As long as a table has not been redone from the
# original scan, we work on the line layer drawn from the colourised
# PDF, where the ink is 255. As soon as it has been, it is the facsimile
# itself we look at, and the ink there is DARK. The two tools that show
# cut-outs to the eye therefore pass through here, and no longer have to
# know where the image comes from.
def clean_(key):
    return ROOT / "originals" / "kovri" / f"{key}-neta.png"


def redone(key):
    """Has this table been redone from its original scan?"""
    return clean_(key).exists()


def plate(key):
    """The image as the eye must see it: the ink DARK."""
    if redone(key):
        return Image.open(clean_(key)).convert("L")
    return ImageOps.invert(Image.open(WORKING / f"{key}-trako.png").convert("L"))


def enko(key):
    """The ink density as a float: high = ink."""
    return 255.0 - np.asarray(plate(key)).astype(np.float32)


def models():
    d = np.load(ROOT / "tools" / "ciphers.npz")
    names = [c for c in d.files for _ in range(len(d[c]))]
    stack_ = np.stack([m for c in d.files for m in d[c]]).reshape(len(names), -1)
    return names, stack_ / np.linalg.norm(stack_, axis=1, keepdims=True)


NAMES, STACK = models()


def vignette(v):
    """Reduces an island to the reference thumbnail, height imposed."""
    h, w = v.shape
    nw = max(1, min(W, round(w * H / h)))
    r = cv2.resize(v.astype(np.float32), (nw, H), interpolation=cv2.INTER_AREA)
    c = np.zeros((H, W), np.float32)
    o = (W - nw) // 2
    c[:, o:o + nw] = r
    return c.ravel() / 255.0


def classify(v):
    x = vignette(v)
    n = np.linalg.norm(x)
    if n == 0:
        return None, 0.0
    s = STACK @ (x / n)
    i = int(s.argmax())
    return NAMES[i], float(s[i])


def islands(ink_, hlo, hhi, radius=5, tolerance=0.10):
    """Components the size of a figure that a white ring isolates."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink_, 8)
    cand = [i for i in range(1, n)
            if hlo <= st[i, 3] <= hhi
            and 0.14 * hlo <= st[i, 2] <= 1.3 * hhi
            and st[i, 4] >= 0.18 * st[i, 2] * st[i, 3]]
    # The ring must contain no FOREIGN ink: the neighbouring figure,
    # for its part, has the right to be there, failing which « 18 »
    # would never be seen — its two figures stand five points apart.
    mc = np.isin(lab, cand)
    out = []
    for i in cand:
        x, y, w, h, _ = st[i]
        y0, y1 = max(0, y - radius), min(ink_.shape[0], y + h + radius)
        x0, x1 = max(0, x - radius), min(ink_.shape[1], x + w + radius)
        at_ = ink_[y0:y1, x0:x1].astype(bool) & ~mc[y0:y1, x0:x1]
        at_[y - y0:y - y0 + h, x - x0:x - x0 + w] = False
        if at_.sum() / max(1, at_.size - w * h) < tolerance:
            out.append((x, y, w, h,
                        (lab[y:y + h, x:x + w] == i).astype(np.uint8) * 255))
    return out


def height_(ink_, split_=38):
    """The height of the figures, measured on the plate itself.

    It is not the same everywhere: 29 points on the middle ground of
    table 5, 46 on table 6. Looking for it avoids missing the one and
    cutting out the other badly. We start from the current value and
    converge in three rounds; the « 1 » is excluded from the
    measurement, its height being the least reliable.
    """
    h = float(split_)
    for _ in range(3):
        goods = [(y2, cl) for _, _, _, y2, v in
                islands(ink_, round(0.62 * h), round(1.55 * h), 5, 0.09)
                for cl, s in [classify(v)] if s >= 0.88 and cl != '1']
        if len(goods) < 8:
            return round(h)
        fresh = float(np.median([b[0] for b in goods]))
        if abs(fresh - h) < 0.6:
            h = fresh
            break
        h = fresh
    return round(h)


def group_up(gl):
    """Glues neighbouring figures back into numbers."""
    rest = sorted(gl, key=lambda g: (g[1], g[0]))
    nums = []
    while rest:
        grp = [rest.pop(0)]
        moves = True
        while moves:
            moves = False
            for b in list(rest):
                for c in grp:
                    x1, y1, w1, h1 = c[:4]
                    x2, y2, w2, h2 = b[:4]
                    hh = min(h1, h2)
                    overlap = min(y1 + h1, y2 + h2) - max(y1, y2)
                    gap = max(x1, x2) - min(x1 + w1, x2 + w2)
                    if (overlap > 0.55 * hh and -0.3 * hh <= gap < 0.55 * hh
                            and abs(h1 - h2) < 0.45 * hh):
                        grp.append(b)
                        rest.remove(b)
                        moves = True
                        break
                else:
                    continue
                break
        grp.sort(key=lambda g: g[0])
        nums.append(grp)
    return nums


# THE TRUNCATED NUMBER IS THE MOST DANGEROUS FAULT, because it is
# silent: on table 14 we read « 2 » where the plate carries « 12 », and
# « 6 » where it carries « 60 ». The neighbouring figure, stuck to a
# hatching, had not been seen, and the truncated number happened to be
# in the expected list as well. Nothing signalled it.
#
# We therefore look at the adjacent cell, left and right. Not « is there
# ink? » — an engraving is full of it, and the question makes good
# readings be rejected as much as bad ones — but « is there a FIGURE? »,
# by the same matched filter as everywhere else. If so, the number goes
# on: we try to read it whole, and keep it only if the lengthened number
# is itself expected. Otherwise we throw the reading away rather than
# keep half of one.
NEIGHBOUR_THRESHOLD = 0.42
# The minimum lead of the chosen figure over the next, to lengthen.
NEIGHBOUR_MARGIN = 0.05
# The lead a reading needs over its rival to carry the day.
EVIDENCE_GAP = 0.05
BASE = None


# TWO SETS OF MODELS, because there are two inks. The stencil drawn from
# the colourised PDF has clean outlines; the facsimile has grey ink,
# fulls that bleed and thins that fade away. A template cut in the one
# does not fit the other: on the grey, the stencil's matched filter
# scores 0.24 where it should score close to 1. We therefore keep both,
# and GREY says which is in use -- it is the caller that knows, since it
# is the caller that knows which plate it is looking at.
GREY = False


def _base():
    global BASE
    if BASE is None:
        BASE = {}
    fh_ = "ciphers-grey.npz" if GREY else "ciphers.npz"
    if fh_ not in BASE:
        d = np.load(ROOT / "tools" / fh_)
        b = {}
        for c in d.files:
            # WE BRING THE MODEL BACK TO A FULL OF 1. The stencil's
            # models are means of cut-outs, the grey ones centres of
            # clusters ALREADY NORMALISED: their full is five
            # hundredths, and the template, which takes the stroke at
            # half the full, found nothing at all there any more.
            m = d[c].mean(0)
            m = m / max(1e-6, float(m.max()))
            col = m.max(0) > 0.15
            b[c] = m[:, col.argmax(): len(col) - col[::-1].argmax()]
        BASE[fh_] = b
    return BASE[fh_]


def template_(c, size, margin=10):
    """A figure, and around it the reserve of white that carries it.

    The model is +1 on the stroke and -1 all around, each part brought
    back to its area: a perfectly set figure scores 1, a cell full of
    ink 0. That is what makes the filter insensitive to hatchings,
    which fill the reserve as much as the stroke.
    """
    m = _base()[c]
    g = cv2.resize(m, (max(1, round(m.shape[1] * size / H)), size),
                   interpolation=cv2.INTER_AREA)
    q = np.zeros((size + 2 * margin, g.shape[1] + 2 * margin), np.float32)
    q[margin:margin + size, margin:margin + g.shape[1]] = g
    p = (q >= 0.5).astype(np.float32)
    n = 1.0 - p
    return p / p.sum() - n / n.sum(), margin, g.shape[1]


def neighbour(ink_, cx, cy, size, rad=6):
    """The best figure in the adjacent cell.

    Returns (score, figure, box, lead) — the lead being that of the
    chosen figure over the next. It alone decides the lengthenings: on
    table 14 we read « 69 » where the plate carries « 60 », because the
    0 and the 9 were nearly equal. When two figures contend for the
    cell, we do not lengthen.
    """
    scores = []
    best, who, pos = -9.0, None, None
    for c in _base():
        T, M, L = template_(c, size)
        x0, y0 = int(cx) - M - rad, int(cy) - M - rad
        h, w = T.shape
        if (x0 < 0 or y0 < 0 or x0 + w + 2 * rad > ink_.shape[1]
                or y0 + h + 2 * rad > ink_.shape[0]):
            continue
        r = cv2.matchTemplate(ink_[y0:y0 + h + 2 * rad, x0:x0 + w + 2 * rad],
                              T, cv2.TM_CCORR)
        _, mx, _, loc = cv2.minMaxLoc(r)
        scores.append(float(mx))
        if mx > best:
            best, who, pos = float(mx), c, (x0 + loc[0] + M, y0 + loc[1] + M, L)
    scores.sort(reverse=True)
    margin = (scores[0] - scores[1]) if len(scores) > 1 else 0.0
    return best, who, pos, margin



# HOW THE FACSIMILE CALLS A NUMBER. Three forms, and all three were
# needed:
#
#   (18)              the ordinary form;
#   (9, 11, 12)       A GROUP — « les tableaux muraux (9, 11, 12) » —
#                     standing for three objects at once. We read none
#                     of them, and the 9 of table 1 was called nowhere
#                     else: it was missing entirely;
#   41)               a missing opening parenthesis. Three places in the
#                     two booklets. A slip in the transcription or a
#                     broken sort at the printer's, one cannot say
#                     without the facsimile before one's eyes — so we do
#                     not touch the source, and content ourselves with
#                     recognising the cross-reference;
#   94 bis            A NUMBER THAT IS NOT A NUMBER. The engraver added
#                     two tools after the fact, and rather than renumber
#                     the whole plate he slipped them in among the
#                     others: « 94bis » is engraved on the chisel,
#                     between the 94 and the 95, and « 95bis » on the
#                     mallet. There are two of them in the whole work,
#                     both on table 5. Their key is « 94bis », and the
#                     automatic reader will never read them -- it knows
#                     only figures.
#
# A group broken by the end of a line is set as TWO superscripts,
# « (9, 11, » then « 12) ». We glue them back before reading.
REGLUE_SUP = re.compile(
    r'\\textsuperscript\{([^{}]*,)\}\s*(?:\\nl|\\cc)?\s*\n?\s*'
    r'\\textsuperscript\{([^{}]*)\}')
SUP = re.compile(r'\\textsuperscript\{([^{}]*)\}')
CONT = re.compile(r'\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*,?'
                   r'(?:\s*(?:\\textit\{)?bis\}?)?\s*\)?\s*$')
FIGURE = re.compile(r'\d{1,3}')
BIS = re.compile(r'\bbis\b')


def xrefs_(text_):
    """Every number a text calls, in whatever form. Returns the list in
    the order of the text, duplicates included."""
    t = text_
    for _ in range(3):
        t = REGLUE_SUP.sub(r'\\textsuperscript{\1 \2}', t)
    out = []
    for c in SUP.findall(t):
        if CONT.fullmatch(c.strip()):
            ns = [int(x) for x in FIGURE.findall(c)]
            # « 94 bis » is not 94: it is a separate object, slipped in
            # between the 94 and the 95. The « bis » attaches to the last
            # number of the cross-reference.
            if ns and BIS.search(c):
                ns[-1] = f"{ns[-1]}bis"
            out += ns
    # The cross-references the facsimile did not set as superscripts --
    # there are seven, all on the Ido side.
    for c in re.findall(r'\((\d{1,3}(?:\s*,\s*\d{1,3})*)\)', SUP.sub('', t)):
        out += [int(x) for x in FIGURE.findall(c)]
    return out


# A PLATE MAY CARRY SEVERAL SCENES, and each starts its numbering again
# at 1: table 6 has five vignettes, tables 3, 4, 7, 8 and 9 have two.
# The same « 39 » is therefore read twice there, and the reader, which
# believed each number unique, threw away one of the two or returned the
# other at random. plates/scenes.json gives the place of each scene; we
# then read vignette by vignette, each with only the numbers ITS text
# calls for.
def scenes_(key):
    """A plate's scenes: [(name, shape)], in the order to be tried."""
    f = ROOT / "plates" / "scenes.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8")).get(key)
    return list(d.items()) if d else []


def inside(shape_, x, y):
    """Is the point (x, y), as a fraction, inside the shape?"""
    if shape_[0] == "elipso":
        _, cx, cy, rx, ry = shape_
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
    _, x0, y0, x1, y1 = shape_
    return x0 <= x <= x1 and y0 <= y <= y1


def box(shape_):
    """The bounding frame of a shape, as a fraction."""
    if shape_[0] == "elipso":
        _, cx, cy, rx, ry = shape_
        return (max(0.0, cx - rx), max(0.0, cy - ry),
                min(1.0, cx + rx), min(1.0, cy + ry))
    return tuple(shape_[1:])


def blocks(tab):
    """The table's text, cut by key: [(key, scene, body)]."""
    f = list((ROOT / "text" / "io").glob(f"*-tabelo-{tab}.tex"))
    if not f:
        return []
    parts = re.split(r'^%%K (\S+)', f[0].read_text(encoding="utf-8"),
                     flags=re.M)
    out, sc = [], ""
    for i in range(1, len(parts), 2):
        m = re.match(r't\d\d-(c\d)-', parts[i])
        if m:
            sc = m.group(1)
        # A note or a title follows the scene it is in.
        out.append((parts[i], sc, parts[i + 1]))
    return out


# THE CROSS-REFERENCE THAT SHOWS NOTHING. The booklet sometimes calls a
# number the plate does not carry: on table 5, « les plates-bandes
# (150) », when the numbering stops at 146 and the object is engraved
# « 50 ». plates/corrections.json says, table by table, which
# cross-reference to read in place of which other. The source does not
# move; it is the reading that is corrected.
_CORRECTIONS = None


def corrections(tab):
    """The cross-references to correct for this table: {read: to be read}."""
    global _CORRECTIONS
    if _CORRECTIONS is None:
        f = ROOT / "plates" / "corrections.json"
        _CORRECTIONS = (json.loads(f.read_text(encoding="utf-8"))
                    if f.exists() else {})
    return _CORRECTIONS.get(f"t{int(tab):02d}", {})


def correct_xref(tab, key=""):
    """{read: to be read} for ONE BLOCK: the corrections that hold for the
    whole table, plus those this block alone carries.

    A CORRECTION DOES NOT ALWAYS HOLD EVERYWHERE. The « (150) » of
    table 5 is a number the plate has nowhere: correcting it everywhere
    can break nothing. The « (6) » that table 6 gives the chambermaid,
    on the other hand, is a number that exists elsewhere — it is the
    soap of paragraph 2 — and correcting it everywhere would make the
    soap point at the chambermaid. An entry whose key is that of a
    BLOCK therefore holds only within that block.
    """
    t = corrections(tab)
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if key:
        out.update(t.get(key, {}))
    return out


def _read_xrefs(size, corr):
    for x in xrefs_(size):
        v = corr.get(str(x), x)
        yield int(v) if str(v).isdigit() else v


def expected(key):
    """{scene: numbers called}. The scene is "" when there is only one."""
    tab = key[1:3]
    bl = blocks(tab)
    if not bl:
        return {}
    if not scenes_(key):
        n = {x for k, _, c in bl
             for x in _read_xrefs(c, correct_xref(tab, k))}
        return {"": n} if n else {}
    out = {}
    for k, sc, size in bl:
        for x in _read_xrefs(size, correct_xref(tab, k)):
            out.setdefault(sc, set()).add(x)
    return {k: v for k, v in out.items() if k}


def kl(scene, n):
    """A number's key: « 39 » on a one-scene plate, « c1:39 » on a plate
    that carries several."""
    return f"{scene}:{n}" if scene else str(n)


def unkey(k):
    """The inverse: « c1:39 » -> ("c1", 39), « 94bis » -> ("", "94bis")."""
    s, n = k.split(":", 1) if ":" in k else ("", str(k))
    return s, (int(n) if n.isdigit() else n)


# SORTING KEYS THAT ARE NOT ALL NUMBERS. « 94bis » is filed between 94
# and 95, neither at the end nor at the start: we sort on the number,
# then on what follows it.
ORDER = re.compile(r'(\d*)(.*)$')


def order(k):
    """A number's sort key: its scene, its number, its suffix."""
    s, n = k.split(":", 1) if ":" in str(k) else ("", str(k))
    m = ORDER.match(n)
    return s, int(m.group(1) or 0), m.group(2)


# The sweep was too timid: at 0.55 it returned only what the islands
# already saw. Coming down to 0.42 takes the reading from 60 to 70 %
# on the four trial plates. The noise it lets in is stopped further on,
# by the list of expected numbers and by the parting between rival
# readings.
SWEEP_THRESHOLD = 0.50
SWEEP_MARGIN = 0.04


def sweep(ink_f, size, threshold=SWEEP_THRESHOLD, margin=SWEEP_MARGIN):
    """The matched filter passed over the whole plate, figure by figure.

    THE ISLANDS SEE ONLY WHAT WHITE ISOLATES. As soon as a figure
    touches a hatching, its component merges with the drawing and it
    disappears — that is what put a ceiling on the reading of busy
    plates. The matched filter, for its part, does not need the figure
    to be cut out: it is enough that the stroke be there and the reserve
    empty.

    Alone, it is too talkative — an engraving offers thousands of peaks.
    It therefore serves as a REINFORCEMENT to the islands, and two
    safeguards hold it: the score must be clear, and the chosen figure
    must lead the next. Whatever gets through anyway will be eliminated
    further on, for not belonging to the expected numbers.
    """
    # THE SWEEP EMITS NO « 1 ». The figure is only a bar, and the
    # filter finds it again in the stem of a 4, the flank of a 9, a
    # vertical hatching: on table 1 it made us read « 13 » for 3,
    # « 16 » for 26, « 71 » for 74. The islands, for their part,
    # recognise it honestly — they cut the shape out instead of
    # correlating it — and keep the charge of finding it.
    names = [c for c in sorted(_base()) if c != "1"]
    cartes, geo, ref = [], [], None
    for c in names:
        T, M, L = template_(c, size)
        r = cv2.matchTemplate(ink_f, T, cv2.TM_CCORR)
        if ref is None:
            ref = r.shape
        rr = np.full(ref, -9, np.float32)
        h = min(ref[0], r.shape[0])
        w = min(ref[1], r.shape[1])
        rr[:h, :w] = r[:h, :w]
        cartes.append(rr)
        geo.append((M, L))
    S = np.stack(cartes)
    order_ = np.argsort(-S, axis=0)
    best = np.take_along_axis(S, order_[:1], 0)[0]
    gap = best - np.take_along_axis(S, order_[1:2], 0)[0]
    k = max(3, (size // 2) | 1)
    peaks = ((best >= cv2.dilate(best, np.ones((k, k), np.uint8)) - 1e-6)
            & (best > threshold) & (gap > margin))
    out = []
    for y, x in zip(*np.where(peaks)):
        i = int(order_[0, y, x])
        M, L = geo[i]
        out.append((x + M, y + M, L, size, names[i],
                    float(best[y, x]), "balayage"))
    return out


def merge(a, b, size):
    """b brings only what a has not already seen."""
    out = list(a)
    for g in b:
        if any(abs(g[0] - h[0]) < 0.5 * size and abs(g[1] - h[1]) < 0.5 * size
               for h in out):
            continue
        out.append(g)
    return out


def read_file(a, att, top=None):
    """Returns {number: ((x, y, w, h), strength)} in points of the given table."""
    ink_ = (a > 128).astype(np.uint8)
    if top is None:
        top = height_(ink_)
    gl = []
    for x, y, w, h, v in islands(ink_, round(0.68 * top), round(1.35 * top),
                               4, 0.16):
        c, s = classify(v)
        if c and s >= (THRESHOLD_ONE if c == '1' else THRESHOLD):
            gl.append((x, y, w, h, c, s, "ilot"))
    gl = merge(gl, sweep(ink_.astype(np.float32), top), top)
    read_ = {}
    ef = ink_.astype(np.float32)
    gap = round(0.13 * top)
    wide = round(0.62 * top)
    for grp in group_up(gl):
        t = ''.join(g[4] for g in grp)
        if not t.lstrip('0'):
            continue
        x0 = min(g[0] for g in grp)
        y0 = min(g[1] for g in grp)
        x1 = max(g[0] + g[2] for g in grp)
        y1 = max(g[1] + g[3] for g in grp)
        sd, cd, pd, md = neighbour(ef, x1 + gap, y0, top)
        sg, cg, pg, mg = neighbour(ef, x0 - gap - wide, y0, top)
        force = (sum(g[5] for g in grp) / len(grp)
                 + (0.15 if all(g[6] == "ilot" for g in grp) else 0.0))
        if max(sd, sg) <= NEIGHBOUR_THRESHOLD:
            read_.setdefault(int(t), []).append(((x0, y0, x1 - x0, y1 - y0),
                                               force))
            continue
        if max(md if sd > NEIGHBOUR_THRESHOLD else 0,
               mg if sg > NEIGHBOUR_THRESHOLD else 0) < NEIGHBOUR_MARGIN:
            continue
        # The number goes on: we lengthen it by the neighbouring figure,
        # and keep the lengthening only if it gives an expected number —
        # and only one. Two possible lengthenings is an ambiguity: we let
        # it drop.
        prop = []
        if sd > NEIGHBOUR_THRESHOLD and int(t + cd) in att:
            prop.append((int(t + cd), (x0, y0, pd[0] + pd[2] - x0, y1 - y0)))
        if sg > NEIGHBOUR_THRESHOLD and int(cg + t) in att:
            prop.append((int(cg + t), (pg[0], y0, x1 - pg[0], y1 - y0)))
        if len(prop) == 1:
            read_.setdefault(prop[0][0], []).append((prop[0][1], force))
    # A NUMBER READ TWICE. Each number appears only once per vignette:
    # two readings mean that at least one is false. We part them by the
    # strength of their evidence: the mean resemblance of the figures,
    # and a bonus for a reading drawn entirely from the islands, where
    # the figure has been cut out and not merely correlated.
    #
    # IF THE TWO ARE EQUAL, WE DO NOT DECIDE. We tried the contrary,
    # once the vignettes were separated: since the number is unique
    # WITHIN ITS VIGNETTE, one of the two readings is certainly false,
    # and taking the better supported seemed worth more than losing
    # both. That returns sixty-one more readings -- four of them good.
    # The rest is noise: a « c. » and a « k. » from the plan's legend,
    # a fir branch, a window upright. The measure of the evidence
    # cannot part two false ones; we therefore keep to abstention.
    kept = {}
    for n, p in read_.items():
        if n not in att:
            continue
        p.sort(key=lambda q: -q[1])
        if len(p) == 1 or p[0][1] - p[1][1] >= EVIDENCE_GAP:
            kept[n] = (p[0][0], round(p[0][1], 3))
    return kept


# A NUMBER STANDS NEAR THOSE CITED WITH IT. The text describes the
# plate step by step -- « la caissiere (14) [...] la caisse (15) » --
# and the objects named in one sentence are neighbours in the drawing.
# Measurement confirms it: among the sure readings, two co-cited numbers
# are three to eight times closer than two numbers taken at random (0.12
# times the mean distance on table 13, 0.27 on 11, 0.28 on 10).
#
# It is therefore a check that owes nothing to the shape of the figures,
# and that catches what shape lets through: on table 13, « 14 » and
# « 34 » fell at eighteen and twelve times the ordinary distance from
# their sentence neighbours. We stay generous -- six times -- so as to
# reject only the absurd: correct readings rise to four or five when the
# text jumps from one end of the plate to the other.
DISTANT_THRESHOLD = 6.0


def sentences(tab, scene=""):
    """The groups of numbers cited in one sentence of the table's text."""
    bl = blocks(tab)
    if not bl:
        return []
    t = "".join(c for _, sc, c in bl if not scene or sc == scene)
    t = re.sub(r'%.*', '', t)
    t = re.sub(r'\\(?:nl|cc)\b', ' ', t)
    out = []
    for ph in re.split(r'[.;:!?]\s', t):
        ns = sorted(set(_read_xrefs(ph, correct_xref(tab))),
                    key=lambda q: order(str(q)))
        if len(ns) > 1:
            out.append(ns)
    return out


def cohere(key, found_, la, ht, scene=""):
    """Discards readings set far from their sentence neighbours."""
    from itertools import combinations
    pos = {n: (v[0][0], v[0][1]) for n, v in found_.items()}
    sure = {n: pos[n] for n, v in found_.items() if v[1] >= 0.95}
    ph = sentences(key[1:3], scene)
    ref = [np.hypot(sure[a][0] - sure[b][0], sure[a][1] - sure[b][1])
           for g in ph for a, b in combinations([x for x in g if x in sure], 2)]
    if len(ref) < 8:
        return found_, 0          # not enough to measure a scale
    sc_ = float(np.median(ref)) or 1.0
    neighbours = {}
    for g in ph:
        for a in g:
            neighbours.setdefault(a, set()).update(x for x in g if x != a)
    kept, dropped = {}, 0
    for n, v in found_.items():
        vs = [sure[w] for w in neighbours.get(n, ()) if w in sure and w != n]
        if vs:
            x, y = pos[n]
            dm = float(np.median([np.hypot(x - a, y - b) for a, b in vs]))
            if dm / sc_ > DISTANT_THRESHOLD:
                dropped += 1
                continue
        kept[n] = v
    return kept, dropped


def manual_(key, la, ht, size):
    """The numbers the eye has set itself on this plate.

    The automatic reader has a ceiling where the reserve of white closes
    up: the figure touches a hatching, or hides half behind a hat, and
    nothing distinguishes it any more. Those numbers are picked up by
    hand, with tools/manual.py, and plates/manual.json keeps them. Like
    verdicts.json, that file does not write itself.
    """
    f = ROOT / "plates" / "manual.json"
    if not f.exists():
        return {}
    d = json.loads(f.read_text(encoding="utf-8")).get(key, {})
    return {n: ((round(v[0] * la), round(v[1] * ht),
                 round(v[2] * la), round(v[3] * ht)), v[4])
            for n, v in d.items()}


def verdicts(key):
    """The readings the eye has refused, for this plate.

    THE MACHINE DOES NOT WRITE THIS FILE. plates/verdicts.json is kept
    by hand: each doubtful cut-out has been re-read with, beneath it,
    the name the facsimile gives the object, and we have entered there
    those where the announced number is not to be found. If the tool
    could rewrite it, the judgement would be lost at the first re-run --
    and it is the one piece of the apparatus that no measurement
    replaces.
    """
    f = ROOT / "plates" / "verdicts.json"
    if not f.exists():
        return set()
    d = json.loads(f.read_text(encoding="utf-8"))
    return {str(x) for x in d.get(key, [])}


def objects_(key):
    """The name of each numbered object, if it has been picked up.

    The keys follow those of numbers.json: « 39 » on a plate with a
    single scene, « c1:39 » on a plate that carries several.
    """
    f = ROOT / "plates" / "objects.json"
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding="utf-8")).get(key[:3], {})


def check(path, found_, dest, top, threshold=None, wide=1.1, cols=12):
    """A check sheet: each number read, in its cut-out.

    THE OBJECT'S NAME IS CARRIED BENEATH THE CUT-OUT. The shape of the
    figure is not enough to judge a doubtful reading -- a hatching
    resembles many things -- but the facsimile says what the number
    designates, and the eye then decides at once: if « (20) » is to show
    a bicycle and the cut-out carries none, the reading is false,
    whatever its score may have been.

    « threshold » keeps only the readings below a given confidence, and
    « wide » widens the cut-out: this is the sheet of doubtful cases,
    where one wants to see the object around the number, not the figure
    alone.
    """
    from PIL import ImageDraw
    key = key_of(dest)
    names = objects_(key)
    kept = {n: v for n, v in found_.items()
            if threshold is None or v[1] < threshold}
    if not kept:
        return 0
    # THE CUTTING OUT IS ALWAYS DONE IN THE WORKING PLATE, and that
    # one carries its ink dark: a check sheet reads like an engraving,
    # not like a negative.
    im = plate(key)
    margin = round(wide * top)
    cell = round(3.2 * top * max(1.0, wide / 1.1))
    lig = (len(kept) + cols - 1) // cols
    bottom = 34
    feuille = Image.new('L', (cols * cell, lig * (cell + bottom)), 255)
    d = ImageDraw.Draw(feuille)
    for k, n in enumerate(sorted(kept, key=lambda q: order(str(q)))):
        (x, y, w, h), f = kept[n]
        cr = im.crop((x - margin, y - margin, x + w + margin, y + h + margin))
        r, c = divmod(k, cols)
        feuille.paste(cr.resize((cell, cell)), (c * cell, r * (cell + bottom)))
        d.text((c * cell + 4, r * (cell + bottom) + cell + 3),
               f"{n}  ({f:.2f})", fill=0)
        v = names.get(str(n), {})
        name_ = (v.get("fr") or v.get("io") or ["—"])[0]
        d.text((c * cell + 4, r * (cell + bottom) + cell + 17), name_[:26], fill=0)
    feuille.save(dest)
    return len(kept)


# THE PLATE KEY IS DRAWN FROM THE FILENAME, whatever suffix the sheet
# carries -- « -dubita », « -manuali », « -revizo2 ». We read it by
# pattern, rather than strip a list of suffixes that would have to be
# kept up to date.
def key_of(dest):
    m = re.match(r'(t\d\d-[a-z0-9]+-\d+)', Path(dest).stem)
    return m.group(1) if m else Path(dest).stem


def hand(keys=None):
    REVIEW.mkdir(parents=True, exist_ok=True)
    cat = {}
    fh_ = ROOT / "plates" / "numbers.json"
    if fh_.exists():
        cat = json.loads(fh_.read_text(encoding="utf-8"))
    # THE COUNT IS KEPT BY TABLE, not by plate: table 5 has two
    # engravings — the house and its plan — which share a single
    # numbering, and counting its hundred and twenty-three numbers twice
    # would make the total lie.
    by_table_ = {}
    for f in sorted(WORKING.glob("*-trako.png")):
        key = f.name[:-10]
        if not re.fullmatch(r't\d\d-[a-z0-9]+-\d+', key):
            continue          # the trials of old, left in working/
        if keys and key not in keys:
            continue
        att = expected(key)
        if not att:
            continue
        # A PLATE REDONE FROM ITS ORIGINAL IS NOT RE-READ. Its numbers
        # have been carried over by originals.py, checked one by one, and
        # they are recorded as a fraction of the NEW plate: re-reading
        # them on the old line layer, which has neither the same
        # dimensions nor the same framing, would destroy the work.
        # WE TRIED TEACHING IT THE GREY, and measured what that is
        # worth: fifteen hundred numbers already placed make fourteen
        # hundred labelled figures, enough to remake the models in the
        # medium itself (tools/ciphers.py). The reader so remade finds
        # 442 numbers in their place, sets 132 ELSEWHERE, and proposes
        # 45 new ones. One in four is false: too many to come in here
        # on its own. It therefore serves to PROPOSE, not to decide,
        # and what the eye keeps of its proposals comes in through
        # manual.json like the rest.
        if redone(key) and key in cat:
            # We keep the READINGS, but go on welcoming what the eye sets:
            # a number picked up by hand on the facsimile must come in,
            # failing which the redone plate would be frozen.
            e = cat[key]
            la, ht, top = e["largeur"], e["alteso"], e["corpo"]
            found_ = {n: ((round(v[0] * la), round(v[1] * ht),
                            round(v[2] * la), round(v[3] * ht)), v[4])
                       for n, v in e["numeri"].items()}
            ref = verdicts(key)
            for n in [n for n in found_
                      if n in ref or str(unkey(n)[1]) in ref]:
                del found_[n]
            # WHAT THE HAND HAS SET, THE HAND CAN TAKE BACK. The positions
            # picked up by eye come in here with a confidence of exactly
            # 1.0 -- no automatic reading reaches it -- and, once written
            # into numbers.json, they became indistinguishable from the
            # readings carried over from the old plate: removing them from
            # manual.json no longer removed them from anything. We
            # therefore throw them all away before putting back those the
            # file still holds. A number set askew is then corrected where
            # it was set.
            for n in [n for n, v in found_.items() if v[1] == 1.0]:
                del found_[n]
            possible = {kl(sc, n) for sc, ns in att.items() for n in ns}
            hands = manual_(key, la, ht, top)
            found_.update({n: v for n, v in hands.items() if n in possible})
            expected_ = sum(len(v) for v in att.values())
            e["numeri"] = {str(n): [round(x / la, 6), round(y / ht, 6),
                                    round(w / la, 6), round(h / ht, 6), f]
                           for n, ((x, y, w, h), f)
                           in sorted(found_.items(),
                                     key=lambda q: order(str(q[0])))}
            check(f, found_, REVIEW / f"{key}.png", top)
            print(f"  {key}  {len(found_):3d}/{expected_:3d} numeros — "
                  f"planche d'origine, lecture conservee"
                  + (f", {len(hands)} poses a la main" if hands else ""))
            t = by_table_.setdefault(key[:3], [set(), 0])
            t[0].update(e["numeri"])
            t[1] = max(t[1], expected_)
            continue
        a = np.asarray(Image.open(f))
        ht, la = a.shape
        top = height_((a > 128).astype(np.uint8))
        # THE READING IS DONE VIGNETTE BY VIGNETTE. On a plate with
        # several scenes, each starts again at 1: looking for « 39 » over
        # the whole plate is to find two and keep neither.
        shapes = scenes_(key) or [("", ["rekt", 0.0, 0.0, 1.0, 1.0])]
        found_, dropped = {}, 0
        for sc, shape_ in shapes:
            if sc not in att:
                continue
            fx0, fy0, fx1, fy1 = box(shape_)
            x0, y0 = int(fx0 * la), int(fy0 * ht)
            x1, y1 = min(la, int(fx1 * la) + 1), min(ht, int(fy1 * ht) + 1)
            read_ = read_file(a[y0:y1, x0:x1], att[sc], top)
            read_ = {n: ((b[0] + x0, b[1] + y0, b[2], b[3]), fo)
                   for n, (b, fo) in read_.items()}
            # The bounding frame overruns onto the neighbouring vignettes --
            # that of the oval on table 6 overlaps all four, and its « 6 »
            # of earthenware fell into the drawing room as well. The FIRST
            # shape that contains the point wins: the oval is tried before
            # the four vignettes, and nothing is read twice.
            def who(v):
                x = (v[0][0] + v[0][2] / 2) / la
                y = (v[0][1] + v[0][3] / 2) / ht
                return next((s for s, f in shapes if inside(f, x, y)), None)

            read_ = {n: v for n, v in read_.items() if who(v) == sc}
            read_, jt = cohere(key, read_, la, ht, sc)
            dropped += jt
            found_.update({kl(sc, n): v for n, v in read_.items()})
        expected_ = sum(len(v) for v in att.values())
        # A refusal written plainly (« 54 ») on a plate with scenes holds
        # for all its vignettes: the judgement dates from before we knew
        # there were several, and nothing says which one it aimed at.
        ref = verdicts(key)
        refused = {n for n in found_
                   if n in ref or str(unkey(n)[1]) in ref}
        for n in refused:
            del found_[n]
        # What the eye has set outweighs everything else.
        possible = {kl(sc, n) for sc, ns in att.items() for n in ns}
        hands = manual_(key, la, ht, top)
        found_.update({n: v for n, v in hands.items() if n in possible})
        t = by_table_.setdefault(key[:3], [set(), 0])
        t[0].update(found_)
        t[1] = max(t[1], expected_)
        check(f, found_, REVIEW / f"{key}.png", top)
        # THE SHEET OF DOUBTFUL CASES, cut wider and carrying the name of
        # the object: that is the one re-read to decide. Four columns and
        # not eight: at eight, the figure at the centre of the cut-out is
        # no more than a few points on screen, and one cannot judge. The
        # sheet is taller, and it can be read.
        n_d = check(f, found_, REVIEW / f"{key}-dubita.png", top,
                       threshold=0.95, wide=3.4, cols=4)
        # AS A FRACTION, not in points: the page serves the plate at three
        # resolutions, and the close-up must fall right on each.
        cat[key] = {"corpo": top, "largeur": la, "alteso": ht,
                    # THE CONFIDENCE IS RECORDED WITH THE POSITION. A reading
                    # entirely cut out by the islands is sure; a reading where
                    # the sweep supplied a figure is much less so, and it is on
                    # the busy plates that the difference shows. The page will
                    # therefore be able to open a close-up only on the readings
                    # that deserve it, without the tool having to be re-run.
                    "numeri": {str(n): [round(x / la, 6), round(y / ht, 6),
                                        round(w / la, 6), round(h / ht, 6), f]
                               for n, ((x, y, w, h), f)
                               in sorted(found_.items(),
                                         key=lambda q: order(str(q[0])))}}
        print(f"  {key}  {len(found_):3d}/{expected_:3d} numeros lus "
              f"(corps {top} px), dont {n_d} a verifier"
              + (f", {dropped} ecartes par le voisinage" if dropped else "")
              + (f", {len(refused)} refuses a l'oeil" if refused else "")
              + (f", {len(hands)} poses a la main" if hands else ""))
    fh_.write_text(json.dumps(cat, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    tot_l = sum(len(v[0]) for v in by_table_.values())
    tot_a = sum(v[1] for v in by_table_.values())
    if tot_a:
        print(f"  TOTAL {tot_l}/{tot_a} = {100 * tot_l // tot_a} %")
    print(f"  planches de controle dans {REVIEW}")


if __name__ == "__main__":
    hand(sys.argv[1:] or None)
