#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plates.py — prepares the wall tables for the reading page.

    python3 tools/plates.py t01-apar-1 plates/font/page1.pdf
    python3 tools/plates.py t02-tit-0  plates/font/page2.pdf
    python3 tools/plates.py --tuto          # what the tool does, in detail

A PLATE IS FILED UNDER A BLOCK KEY, not under a table number. Most
illustrate the opening -- "t01-apar-1" -- but not all: the figure of the
human body goes under "La Korpo homala.", hence under t02-tit-0, and the
plan of the house under the "(Videz la plano.)" of table 5, hence under
t05-apar-2. It is the key that says where the engraving is laid, and a
table may carry several.

TWO SPECIES OF PLATE. The wall tables are in two layers (see below); the
plan of the house and the figure of the human body are pure vector
drawings, with neither colour nor image. We rasterise those, at 300 dots
per inch, and the rest does not change.

WHAT IS IN A TABLE'S PDF. The wall table is not a flat image: it is a
stack of TWO LAYERS, and therein lies the whole interest.

    below     the colour, in JPEG ~2270x1520
    above     the engraved line, whose ink is PURE BLACK and whose whole
              drawing lies in an alpha channel of ~5460x3660

The engraving is therefore intact and separate from the colour: one can
redo either without ever touching the other. That is what makes colour
corrections possible -- and that is why this tool keeps the two layers
apart in plates/kovri/ before composing them.

TWO OUTPUTS, BECAUSE THERE ARE TWO USES.

    <key>-vido.webp     ~1000px   the overall view laid above the table's
                                  title. It loads when the table comes
                                  into view.
    <key>-detalo.webp   ~2600px   the image from which the close-ups are
                                  cut. It is fetched only at the FIRST
                                  click on a number of the table, and then
                                  serves all the others: a close-up is
                                  only a re-crop of it, never a new load.

WHY COMPOSE HERE, AND NOT IN THE BROWSER. One could send both layers and
superimpose them on screen; that would even be convenient for redoing the
colour. But the measurement decides: at 2600px, the line alone weighs
1229 kB and the colour 142, when their composite weighs 868. The line is a
woodcut, all in hatching, and it compresses far better once the colour is
underneath. So we compose here.

    plates/font/     the original PDFs (not versioned: ~100 MB)
    plates/kovri/    the two layers extracted (not versioned)
    plates/          the two WebP per table (VERSIONED, ~1 MB)
"""
import io
import json
import sys
from pathlib import Path

import pikepdf
from PIL import Image
from pikepdf import PdfImage

Image.MAX_IMAGE_PIXELS = None
RACINE = Path(__file__).resolve().parent.parent
GRAVURI = RACINE / "plates"

# The overall view does not need to be large: it fits the width of a
# column. The detail image carries the close-ups, and it is that which
# decides their sharpness. 2600px gives a close-up of 400px of source in a
# box of 700: a little soft, but legible, and it weighs only 868 kB where
# 3200px weighs 1165.
# 1200 and not 1000: an ordinary desktop screen shows the engraving over
# about 1090 points, and an overall view of 1000 therefore fell just
# below -- the browser then went for the detail image, eight times
# heavier, for a screen that did not need it. At 1200 it also covers
# phones, whose triple-density screen calls for a thousand points; only a
# large Retina screen goes up to the detail.
LARGE_VIDO = 1200
LARGE_DETALO = 2600
QUAL_VIDO = 72
QUAL_DETALO = 72


def kovri(pdf):
    """The images of a table PDF, including those in Form XObjects.

    The document must stay OPEN as long as the rendered objects are in use:
    pikepdf destroys them with it, and one then reaps an "object of type
    destroyed" at the first read.
    """
    # The line is enclosed in a Form; a reading that does not descend into
    # it finds only the colour, and one believes the file is flat.
    trouve = []
    vus = set()

    def descendre(res):
        for nom, obj in dict(res.get("/XObject", {})).items():
            if obj.objgen in vus:
                continue
            vus.add(obj.objgen)
            if obj.get("/Subtype") == "/Image":
                trouve.append(obj)
            elif obj.get("/Subtype") == "/Form":
                descendre(obj.get("/Resources", {}))

    for page in pdf.pages:
        descendre(page.get("/Resources", {}))
    return trouve


def rasterer(chemin, dpi=300):
    """A vector plate, rendered as a line mask."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile",
                        str(chemin), str(base)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(str(base) + ".png").convert("L")
        im.load()
    # The rendering is black on white; the rest of the tool expects an
    # ALPHA, where white is the ink. We therefore invert, and the two
    # species of plate compose the same way afterwards.
    return Image.eval(im, lambda v: 255 - v)


def separer(chemin):
    """(RGB colour, line as alpha) of a table PDF."""
    couleur = trait = None
    pdf = pikepdf.open(chemin)
    images = kovri(pdf)
    if not images:
        # A PURELY VECTOR PLATE. The plan of the house and the figure of the
        # human body have neither colour nor image: everything there is drawn.
        # We rasterise them, and the line comes out black on white.
        return None, rasterer(chemin)
    for obj in images:
        if "/SMask" in obj:
            # THE INK IS PURE BLACK: it has been verified, its grey channel is 0
            # everywhere. The whole drawing is therefore in the mask, and it is
            # THAT which must be kept -- at full resolution, whereas the ink
            # itself is only a low-definition black wash.
            trait = PdfImage(obj.SMask).as_pil_image().convert("L")
        else:
            couleur = PdfImage(obj).as_pil_image().convert("RGB")
    if trait is None or couleur is None:
        raise SystemExit(f"{chemin} : couche manquante "
                         f"(trait={trait is not None}, "
                         f"couleur={couleur is not None})")
    return couleur, trait


def recaler(couleur, trait):
    """The stretch and the offset that lay the colour on the line.

    THE TWO LAYERS DO NOT SUPERIMPOSE, and the discrepancy is not a simple
    translation: they do not have the same aspect ratio -- plate 13 gives
    1.4902 for the colour and 1.4775 for the line. Bringing one to the
    other's frame therefore walks the edge: the colour falls right in the
    middle of the image and further and further out as one moves away. That
    is what the eye sees as the flat tints spilling out of the outline.

    WE MEASURE THE DISPLACEMENT, WE DO NOT GROPE FOR IT. A grid of
    stretches tried one by one did not converge: the global correlation
    score is flat, the colour having been painted by hand on the line and
    not traced. But a displacement measured ZONE BY ZONE says everything:
    if it grows steadily with x, its slope IS the missing stretch, and its
    intercept the offset.

    Each zone is registered by normalised correlation of its line with the
    outline of the colour, and we keep only the half of the zones whose
    peak clearly dominates the rest of the surface -- a flat of sky or a
    bare wall says nothing about alignment. A robust line is then fitted
    through the cloud, outliers rejected; three to five rounds suffice, and
    we keep the round in which the residual drift and the median deviation
    are lowest.

    Returns (sx, sy, dx, dy): the colour is brought to (sx * width,
    sy * height), then translated by (dx, dy).
    """
    import cv2
    import numpy as np

    W, HT = trait.width, trait.height
    T = np.asarray(trait, np.float32)
    gris = couleur.convert("L")

    def champ(sx, sy, dx, dy, nx=12, ny=8, cote=430, ray=24, garde=0.5):
        """The displacement that remains, zone by zone, with its confidence."""
        g = np.asarray(gris.resize((max(2, round(W * sx)),
                                    max(2, round(HT * sy))), Image.LANCZOS),
                       np.float32)
        a = np.zeros((HT, W), np.float32)
        hh, ww = min(HT, g.shape[0]), min(W, g.shape[1])
        a[:hh, :ww] = g[:hh, :ww]
        if hh < HT:
            a[hh:] = a[hh - 1]
        if ww < W:
            a[:, ww:] = a[:, ww - 1:ww]
        a = np.roll(a, (dy, dx), (0, 1))
        gy, gx = np.gradient(a)
        cont = np.hypot(gx, gy)
        pts = []
        for iy in range(ny):
            for ix in range(nx):
                x0 = max(ray, min(W - cote - ray,
                                  round(W * (ix + .5) / nx) - cote // 2))
                y0 = max(ray, min(HT - cote - ray,
                                  round(HT * (iy + .5) / ny) - cote // 2))
                tt = T[y0:y0 + cote, x0:x0 + cote]
                if tt.std() < 1:
                    continue
                r = cv2.matchTemplate(
                    cont[y0 - ray:y0 + cote + ray, x0 - ray:x0 + cote + ray],
                    tt - tt.mean(), cv2.TM_CCOEFF_NORMED)
                _, mx, _, loc = cv2.minMaxLoc(r)
                # The confidence is the peak's lead over the rest of the
                # surface: a wide, soft peak locates nothing.
                m = r.copy()
                cv2.circle(m, loc, 6, -1, -1)
                pts.append((x0 + cote / 2, y0 + cote / 2,
                            loc[0] - ray, loc[1] - ray, mx - m.max()))
        p = np.array(pts, float)
        if not len(p):
            return p
        return p[p[:, 4] >= np.quantile(p[:, 4], 1 - garde)]

    def droite(v, d):
        for _ in range(3):
            a, b = np.polyfit(v, d, 1)
            r = d - (a * v + b)
            bons = np.abs(r) <= max(1.2, 2.2 * r.std())
            if bons.all() or bons.sum() < 4:
                break
            v, d = v[bons], d[bons]
        return a, b

    sx = sy = 1.0
    dx = dy = 0
    meilleur = None
    for _ in range(5):
        p = champ(sx, sy, dx, dy)
        if len(p) < 6:
            break
        ax, bx = droite(p[:, 0], p[:, 2])
        ay, by = droite(p[:, 1], p[:, 3])
        cout = (abs(ax * W) + abs(ay * HT)
                + np.median(np.abs(p[:, 2])) + np.median(np.abs(p[:, 3])))
        if meilleur is None or cout < meilleur[0]:
            meilleur = (cout, sx, sy, dx, dy)
        sx, sy = sx * (1 - ax), sy * (1 - ay)
        dx, dy = round(dx * (1 - ax) - bx), round(dy * (1 - ay) - by)
    if meilleur is None:
        return 1.0, 1.0, 0, 0
    print(f"  alignement : derive residuelle et ecart median, "
          f"somme {meilleur[0]:.1f} px")
    return meilleur[1], meilleur[2], meilleur[3], meilleur[4]


def composer(couleur, trait):
    """The colour below, the black ink above according to the line's alpha.

    With no colour layer -- a vector plate -- the ground is the paper.
    """
    import numpy as np

    if couleur is None:
        fond = Image.new("RGB", trait.size, (255, 255, 255))
    else:
        sx, sy, dx, dy = recaler(couleur, trait)
        print(f"  recalage de la couleur : etirement {sx:.4f} x {sy:.4f}, "
              f"decalage {dx:+d}, {dy:+d} px")
        etire = couleur.resize((max(2, round(trait.width * sx)),
                                max(2, round(trait.height * sy))),
                               Image.LANCZOS)
        # The uncovered edge takes up the neighbouring colour rather than
        # white, which would cut sharply under the engraving.
        a = np.asarray(etire.convert("RGB"))
        g = np.zeros((trait.height, trait.width, 3), a.dtype)
        hh = min(trait.height, a.shape[0])
        ww = min(trait.width, a.shape[1])
        g[:hh, :ww] = a[:hh, :ww]
        if hh < trait.height:
            g[hh:] = g[hh - 1]
        if ww < trait.width:
            g[:, ww:] = g[:, ww - 1:ww]
        if dx or dy:
            g = np.roll(g, (dy, dx), (0, 1))
        fond = Image.fromarray(g)
    return Image.composite(Image.new("RGB", trait.size, (0, 0, 0)), fond, trait)


def poser(im, chemin, largeur, qualite):
    h = round(largeur * im.height / im.width)
    petite = im.resize((largeur, h), Image.LANCZOS)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    petite.save(chemin, format="WEBP", quality=qualite, method=6)
    return petite.size, chemin.stat().st_size


def preparer(cle, chemin):
    couleur, trait = separer(chemin)
    print(f"  couleur {couleur.size if couleur else '(aucune)'}"
          f"   trait {trait.size}")

    # The layers stay apart: it is on them that the colours will be redone,
    # the engraving having no need to suffer for it.
    kov = GRAVURI / "kovri"
    kov.mkdir(parents=True, exist_ok=True)
    if couleur is not None:
        couleur.save(kov / f"{cle}-koloro.png")
    trait.save(kov / f"{cle}-trako.png")

    plein = composer(couleur, trait)
    taille = {}
    for nom, largeur, qualite in (("vido", LARGE_VIDO, QUAL_VIDO),
                                  ("detalo", LARGE_DETALO, QUAL_DETALO)):
        dim, octets = poser(plein, GRAVURI / f"{cle}-{nom}.webp", largeur, qualite)
        taille[nom] = {"largeur": dim[0], "alteso": dim[1], "okteti": octets}
        print(f"  {cle}-{nom}.webp  {dim[0]}x{dim[1]}  {octets/1024:.0f} Ko")

    # The catalogue tells the page which tables have an engraving, and in
    # what proportions -- enough to reserve the room before the image is
    # even loaded, without which the page jumps on loading.
    cat = GRAVURI / "plates.json"
    tout = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    # The source is noted: without it, one no longer knew which plate came
    # from which file, and redoing the series meant comparing dimensions.
    tout[cle] = {"largeur": plein.width, "alteso": plein.height,
                 "koloro": couleur is not None, "fonto": Path(chemin).name,
                 "vido": taille["vido"], "detalo": taille["detalo"]}
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    return plein


if __name__ == "__main__":
    if "--tuto" in sys.argv or len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(0)
    preparer(sys.argv[1], Path(sys.argv[2]))
