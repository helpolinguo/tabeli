#!/usr/bin/env python3
# ===================================================================
#  colourise.py — serve the original in colour in place of the facsimile,
#  framed on the same frame, so that the numbers always fall right.
#
#  Two impressions of the same stone have come down to us. The
#  Bibliothèque nationale's facsimile is THE BLACK STONE ALONE, pulled
#  without the colours: four thousand five hundred points wide, every
#  hatching clean. The original is the same plate WITH its colours, but
#  photographed at half the fineness.
#
#  FOR THESE TWO TABLES, IT IS THE ORIGINAL THAT IS SERVED. One loses
#  fineness there — the close-up on a number is softer than elsewhere —
#  and one gains the plate as it was on the classroom wall. It is a
#  choice of edition, not a measurement.
#
#  THE FACSIMILE DOES NOT DISAPPEAR FOR ALL THAT: it remains the working
#  plate, the one on which the numbers are read and placed, and it serves
#  here as a REGISTRATION TARGET. Sixteen hundred numbers are filed as
#  fractions of its frame; if the original is laid askew, every close-up
#  falls wide. We therefore register it on the facsimile, and keep
#  nothing else of it.
#
#  THE REGISTRATION GOES IN FOUR STAGES, from coarse to fine:
#
#   1. THE FRAME. The engraving's rule runs from edge to edge; it is the
#      first row, coming from outside, in which more than half the points
#      are dark. Two rectangles, one similarity.
#
#   2. ECC, on the two blurred images. It comes down to a few points.
#
#   3. THE SIMILARITY FITTED TILE BY TILE. ECC works on a reduction to
#      twelve hundred points: ten points of discrepancy on the plate make
#      only two and a half at its scale, and it lets them pass. We
#      therefore measure, on a grid, where each piece wants to go, and fit
#      the similarity that leads them all.
#
#   4. THE HOMOGRAPHY. Discrepancies remain, and on table 16 they reach
#      seventy points at the corners: the lens was not square to the
#      sheet. That is perspective, and perspective is written in eight
#      coefficients — a homography, which carries every straight line onto
#      a straight line.
#
#      WE TRIED A DISPLACEMENT FIELD, and it must be said why it was
#      withdrawn: displacements measured on a grid of pitch forty, gaps
#      filled by diffusion, remapping. The registration fell below ten
#      points — and the façades of table 14 came out askew. A field has no
#      reason to respect an alignment: it follows what it measures, tile
#      by tile, and a tile that is wrong by three points twists its whole
#      neighbourhood. A warped plate is visible; ten points of discrepancy
#      on a close-up is not. We therefore keep the straight lines, and
#      accept the discrepancies.
#
#  THE BLUR OF TWELVE POINTS, in stages 2 to 4, is not carelessness: it is
#  the only scale at which the two impressions resemble each other. Finer,
#  one has only the line and the other only the wash, and the correlation
#  falls to nothing — measured, 0.04.
#
#  THE RESTORATION is light, and it is counted:
#   — the paper has yellowed: we take off two fifths of its yellow, no
#     more. It was ivory, not white;
#   — the colour has faded: we revive it by a sixth. Beyond that, the
#     plate takes on the air of a modern chromo it never had;
#   — the photograph is soft: a light unsharp mask gives it back its bite,
#     with no visible halo.
#
#  WE RENDER AT THE ORIGINAL'S DEFINITION, no more and no less. Bringing
#  it to the facsimile's would not manufacture one point of detail and
#  would double the weight of the file.
#
#  USAGE
#      python3 tools/colourise.py t14-apar-1 originals/t14col.pdf
#      python3 tools/colourise.py t14-apar-1 originals/t14col.pdf --essai
#
#  "--essai" serves nothing: it writes into plates/review/ a comparison
#  strip — the raw original, the rendering, the facsimile — to judge the
#  settings and the registration by eye.
# ===================================================================

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbering as N                                          # noqa: E402
import originals as O                                       # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
KOVRI = RACINE / "originals" / "kovri"

BLANKESO = 0.40   # share of the paper's yellow that is removed
VIVECO = 1.15     # revival of the hue
NETESO = 0.65     # strength of the unsharp mask
MARGE = O.MARGE_FILET
FLOU = 12.0       # the scale at which the two impressions resemble each other
QUAL_KOLORO = 92  # WebP quality of the detail, higher than elsewhere


def tirar(pdf):
    """The image as it is IN the PDF, without resampling it.

    pdftoppm would render the page at a definition of our choosing, and we
    would add a resampling to that of the photograph. pdfimages returns the
    JPEG the file contains, point for point.
    """
    d = Path(tempfile.mkdtemp())
    subprocess.run(["pdfimages", "-all", str(pdf), str(d / "p")], check=True)
    fs = sorted(d.glob("p-*"))
    if not fs:
        raise SystemExit(f"  aucune image dans {pdf}")
    f = max(fs, key=lambda p: p.stat().st_size)
    return np.asarray(Image.open(f).convert("RGB"))


# THE ORIGINAL'S FRAME, so as to lay it on the plate's. The
# engraving's rule runs from edge to edge: it is the first row, coming
# from outside, in which more than half the points are dark. The title
# printed above does not cover half of it; the rule does.
def kadro(gris, seuil=0.55, bord=0.15):
    H, W = gris.shape
    noir = gris < (np.percentile(gris, 92) - 45)
    my0, my1 = round(bord * H), round((1 - bord) * H)
    mx0, mx1 = round(bord * W), round((1 - bord) * W)
    col, lig = noir[my0:my1].mean(0), noir[:, mx0:mx1].mean(1)

    def prem(p, sens):
        q = p if sens > 0 else p[::-1]
        for i in range(len(q)):
            if q[i] >= seuil:
                return i if sens > 0 else len(q) - 1 - i
        raise SystemExit("  cadre introuvable dans l'original en couleur")

    return prem(col, 1), prem(lig, 1), prem(col, -1), prem(lig, -1)


def poser(cle, col, verbeux=True):
    """The matrix that lays the colour original on the plate."""
    gp = np.asarray(N.planche(cle)).astype(np.float32)
    HN, LN = gp.shape
    cg = cv2.cvtColor(col, cv2.COLOR_RGB2GRAY).astype(np.float32)
    x0, y0, x1, y1 = kadro(cg)
    kx = (LN - 2 * MARGE) / (x1 - x0)
    ky = (HN - 2 * MARGE) / (y1 - y0)
    T0 = np.array([[kx, 0.0, MARGE - kx * x0],
                   [0.0, ky, MARGE - ky * y0]], np.float32)
    if verbeux:
        print(f"  cadre de l'original ({x0}, {y0})-({x1}, {y1}), "
              f"echelles {kx:.4f} et {ky:.4f}")
    W2 = 1200
    s = W2 / LN

    def lisse(a):
        h = max(1, round(a.shape[0] * W2 / a.shape[1]))
        d = cv2.resize(a, (W2, h), interpolation=cv2.INTER_AREA)
        d = cv2.GaussianBlur(d, (0, 0), 1.5)
        return (d - d.mean()) / max(1e-6, d.std())

    grand = cv2.warpAffine(255.0 - cg, T0, (LN, HN),
                           flags=cv2.INTER_LINEAR, borderValue=0)
    B, A = lisse(255.0 - gp), lisse(grand)
    warp = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    try:
        cc, warp = cv2.findTransformECC(B, A, warp, cv2.MOTION_AFFINE,
                                        crit, None, 5)
    except cv2.error:
        cc = float("nan")
    Wp = (np.diag([1 / s, 1 / s, 1.0]) @ np.vstack([warp, [0, 0, 1]])
          @ np.diag([s, s, 1.0]))
    T = (Wp @ np.vstack([T0, [0, 0, 1]]))[:2].astype(np.float32)
    for _ in range(3):
        T, n, co = afini(T, col, gp)
    if verbeux:
        print(f"  recalage : correlation {cc:.4f} puis {co:.3f} "
              f"sur {n} tuiles")
    return T, gp


def tuili(pose, gp, sigma, marge, cases, R, seuil):
    """Where each piece of the original wants to go, tile by tile."""
    HN, LN = gp.shape
    a = cv2.GaussianBlur(cv2.cvtColor(pose, cv2.COLOR_RGB2GRAY)
                         .astype(np.float32), (0, 0), sigma)
    b = cv2.GaussianBlur(gp, (0, 0), sigma)
    out = []
    for j in range(cases[0]):
        for i in range(cases[1]):
            y = round((j + 0.5) * HN / cases[0])
            x = round((i + 0.5) * LN / cases[1])
            if (y - R - marge < 0 or y + R + marge > HN
                    or x - R - marge < 0 or x + R + marge > LN):
                continue
            u = a[y - R:y + R, x - R:x + R]
            v = b[y - R - marge:y + R + marge, x - R - marge:x + R + marge]
            u = (u - u.mean()) / max(1e-6, u.std())
            v = (v - v.mean()) / max(1e-6, v.std())
            r = cv2.matchTemplate(v, u, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(r)
            if mx >= seuil:
                out.append((x, y, loc[0] - marge, loc[1] - marge, float(mx)))
    return out


def afini(T, col, gp, sigma=FLOU, marge=90, cases=(5, 7), R=280, seuil=0.35):
    """One round of registration: the similarity that best follows the tiles."""
    HN, LN = gp.shape
    pose = cv2.warpAffine(col, T, (LN, HN), flags=cv2.INTER_LINEAR,
                          borderValue=(255, 255, 255))
    t = tuili(pose, gp, sigma, marge, cases, R, seuil)
    if len(t) < 6:
        return T, len(t), float(np.median([q[4] for q in t])) if t else float("nan")
    ici = np.float32([(q[0], q[1]) for q in t])
    la = np.float32([(q[0] + q[2], q[1] + q[3]) for q in t])
    M, _ = cv2.estimateAffinePartial2D(ici, la, method=cv2.RANSAC,
                                       ransacReprojThreshold=12.0)
    co = float(np.median([q[4] for q in t]))
    if M is None:
        return T, len(t), co
    T2 = (np.vstack([M, [0, 0, 1]]) @ np.vstack([T, [0, 0, 1]]))[:2]
    return T2.astype(np.float32), len(t), co


# WE FIT TWICE, FROM WIDE TO TIGHT. The first round is measured on
# large tiles blurred to twelve points: that is robust, and it catches
# the perspective. The second, on tiles three times smaller and a blur
# of five points, tightens it.
#
# We go no finer. Below five points of blur the two impressions no
# longer resemble each other enough to be recognised — one has only the
# line, the other only the wash — and the measurement starts following
# the noise.
PLIADI = ((FLOU, 70, (7, 10), 190, 0.35),
          (5.0, 40, (12, 16), 110, 0.30))


# A STRAIGHT LINE OF THE STONE MUST STAY STRAIGHT. In the first
# version we laid the displacements measured on a grid of pitch forty,
# filled the gaps by diffusion and remapped: the registration fell below
# ten points, and the façades of table 14 came out askew. A displacement
# field has no reason to respect alignment — it follows what it
# measures, tile by tile, and a tile that is wrong by three points
# twists its whole neighbourhood.
#
# THE PHOTOGRAPH OF A FLAT SHEET IS A HOMOGRAPHY, and nothing more: the
# lens was not square, that is all. Eight coefficients suffice to say
# so, and a homography carries every straight line onto a straight line.
# We therefore fit the eight on the same tiles, and stop there: what
# remains after it is no longer perspective but cockling of the paper,
# and straightening that would cost more than it returns.
def projekti(T, col, gp, verbeux=True):
    """The homography that remains, in points of the plate."""
    HN, LN = gp.shape
    H = np.eye(3, dtype=np.float32)
    for sigma, marge, cases, R, seuil in PLIADI:
        pose = rendre(col, T, H, (LN, HN), 1.0, cv2.INTER_LINEAR)
        t = tuili(pose, gp, sigma, marge, cases, R, seuil)
        if len(t) < 12:
            if verbeux:
                print(f"  flou {sigma:.0f} : {len(t)} tuiles seulement, "
                      f"on passe")
            continue
        ici = np.float32([(q[0], q[1]) for q in t])
        la = np.float32([(q[0] + q[2], q[1] + q[3]) for q in t])
        M, bon = cv2.findHomography(la, ici, cv2.RANSAC, 8.0)
        if M is None:
            continue
        H = (M @ H).astype(np.float32)
        if verbeux:
            d = np.array([(q[2], q[3]) for q in t], float)
            n = int(bon.sum()) if bon is not None else len(t)
            print(f"  ajustement au flou {sigma:.0f} : {len(t)} tuiles, "
                  f"{n} retenues, reprise de {np.abs(d).max():.0f} "
                  f"points au plus")
    return H


# WE TRIED FITTING ON THE NUMBERS THEMSELVES, and it is worse. The idea
# was good: we know where the sixteen hundred and seventy-six numbers
# are on the facsimile, to the point, and it is they the close-up must
# aim at — why register on landscape what can be registered on them?
# Because the tracker does not find them surely enough in the
# photograph: of ninety-three numbers on table 14 it clearly recognises
# only forty-eight, and the field drawn from those forty-eight takes the
# median discrepancy from sixteen to twenty-four points. A handful of
# noisy landmarks, stretched by the diffusion, deforms more than it
# corrects. Measured twice, on both plates.
#
# AND WHAT DISCREPANCY REMAINS IS NOT AN ERROR OF MEASUREMENT: fifteen
# to twenty points, whatever the tracker's settings — a window of eighty
# points or of a hundred and twenty, a blur of one and a half points or
# of three, a confidence threshold of three tenths or of six. They are
# TWO DIFFERENT COPIES of the same plate: pulled at different dates, on
# paper that did not shrink alike, and whose stones were not registered
# at the same point. Half a per cent on four thousand five hundred
# points makes twenty points, and that is exactly what one finds. No
# similarity catches that up.
#
# Sixteen points of discrepancy on a close-up view that shows two
# hundred and ninety: the number aimed at is not at the centre to the
# point, it is a twentieth off centre. We stop there.


def rendre(col, T, H, taille, echelo, interp=cv2.INTER_LANCZOS4):
    LT, HT = taille
    ys, xs = np.mgrid[0:HT, 0:LT].astype(np.float32)
    # from the output to the plate, undoing the projective fit
    px, py = xs / echelo, ys / echelo
    w = H[2, 0] * px + H[2, 1] * py + H[2, 2]
    px, py = ((H[0, 0] * px + H[0, 1] * py + H[0, 2]) / w,
              (H[1, 0] * px + H[1, 1] * py + H[1, 2]) / w)
    # from the plate to the original
    Ti = cv2.invertAffineTransform(T)
    sx = Ti[0, 0] * px + Ti[0, 1] * py + Ti[0, 2]
    sy = Ti[1, 0] * px + Ti[1, 1] * py + Ti[1, 2]
    return cv2.remap(col, sx, sy, interp,
                     borderMode=cv2.BORDER_CONSTANT,
                     borderValue=(255, 255, 255))


def restaurar(im, blankeso=BLANKESO, viveco=VIVECO, neteso=NETESO,
              verbeux=True):
    """The paper brought back to neutral, the hue revived, the line firmed."""
    lab = cv2.cvtColor(im, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    # THE TONE OF THE PAPER is taken from the paper, that is from what the
    # plate has that is lightest: the reserved white between the hatchings.
    # A fifth of the surface suffices to give it.
    pap = L > np.percentile(L, 80)
    ca, cb = float(np.median(A[pap])), float(np.median(B[pap]))
    if verbeux:
        print(f"  le papier tire sur a={ca:+.1f} b={cb:+.1f} ; "
              f"on lui en retire {blankeso:.0%}")
    A = (A - blankeso * ca) * viveco
    B = (B - blankeso * cb) * viveco
    # THE BITE IS GIVEN TO THE LIGHTNESS ALONE. Sharpening the three
    # channels together wakes the coloured grain of the photograph; on the
    # lightness, it wakes only the line.
    # (The lightness of a Lab DRAWN FROM AN EIGHT-BIT IMAGE runs from 0 to
    #  255, not from 0 to 100: bounding it at a hundred crushed the whole
    #  top of the tone, and the plate came out in flat tints.)
    if neteso > 0:
        L = np.clip(L + neteso * (L - cv2.GaussianBlur(L, (0, 0), 1.1)),
                    0, 255)
    return cv2.cvtColor(np.dstack([L, np.clip(A + 128, 0, 255),
                                   np.clip(B + 128, 0, 255)]).astype(np.uint8),
                        cv2.COLOR_LAB2RGB)


def kolorigi(cle, pdf, essai=False, **kw):
    col = tirar(pdf)
    print(f"  {Path(pdf).name} : {col.shape[1]} x {col.shape[0]} points")
    T, gp = poser(cle, col)
    HN, LN = gp.shape
    H = projekti(T, col, gp)
    # THE OUTPUT DEFINITION IS THE ORIGINAL'S. The scale of the similarity
    # says by how much the photograph was enlarged to fall on the
    # facsimile; we render the inverse.
    k = float(np.hypot(T[0, 0], T[1, 0]))
    echelo = 1.0 / k
    LT, HT = round(LN * echelo), round(HN * echelo)
    out = restaurar(rendre(col, T, H, (LT, HT), echelo), **kw)
    print(f"  rendu {LT} x {HT} points, la planche en faisant {LN} x {HN}")
    KOVRI.mkdir(parents=True, exist_ok=True)
    dest = KOVRI / f"{cle}-koloro.png"
    Image.fromarray(out).save(dest)
    print(f"  ecrit dans {dest}")
    if essai:
        bande(cle, col, T, H, out, gp)
    return dest


def bande(cle, col, T, H, out, gp, boite=None):
    """The raw original, the rendering, the facsimile: the same portion."""
    HN, LN = gp.shape
    if boite is None:
        x, y = round(0.72 * LN), round(0.37 * HN)
        boite = (x, y, x + 600, y + 400)
    x0, y0, x1, y1 = boite
    brut = rendre(col, T, np.eye(3, dtype=np.float32),
                  (LN, HN), 1.0)
    o = np.asarray(Image.fromarray(out).resize((LN, HN), Image.LANCZOS))
    trio = [brut[y0:y1, x0:x1], o[y0:y1, x0:x1],
            np.dstack([gp[y0:y1, x0:x1].astype(np.uint8)] * 3)]
    sep = np.full((y1 - y0, 6, 3), 255, np.uint8)
    im = np.hstack([q for p in zip(trio, [sep] * 3) for q in p][:-1])
    d = N.KONTROLO / f"{cle}-koloro.png"
    d.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(im).save(d)
    print(f"  l'original, le rendu et le fac-simile dans {d}")


def main(args):
    if len(args) < 2:
        raise SystemExit(__doc__ or "kolorigo.py <cle> <original.pdf>")
    cle, pdf = args[0], args[1]
    dest = kolorigi(cle, pdf, essai="--essai" in args)
    if "--essai" in args:
        return
    # THE TWO COLOUR PLATES KEEP THEIR TONE. Stretching between
    # percentiles gives its black back to a grey scan that has none;
    # these have one already -- they go down to 11 and 13, with three to
    # four points in a hundred below value 40. Stretching them on top
    # would only block up the shadows.
    O.servir(cle, dest, qual_detalo=QUAL_KOLORO, tono=False)
    cat = RACINE / "plates" / "plates.json"
    tout = json.loads(cat.read_text(encoding="utf-8"))
    tout[cle]["koloro"] = True
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {cle} : servi en couleur.")


if __name__ == "__main__":
    main(sys.argv[1:])
