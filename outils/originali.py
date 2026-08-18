#!/usr/bin/env python3
# ===================================================================
#  originali.py — poser une numerisation d'origine sur nos planches.
#
#  POURQUOI. Les gravures que sert la page viennent d'un PDF colorise :
#  la couche de trait y est un POCHOIR — 87 pour cent de ses points sont
#  du noir pur ou du blanc pur — parce qu'elle y servait de masque pour
#  poser l'encre. Le demi-ton du bois grave, qui fait toute la douceur
#  de la planche, n'y est plus, et aucune definition ne le rendra. Il
#  faut donc repartir des numerisations d'origine (Gallica, BnF).
#
#  CE QUI SERAIT PERDU SANS CET OUTIL. Mille cinq cents numeros ont ete
#  releves a la main sur les planches actuelles. Ils sont enregistres EN
#  FRACTION de la planche, non en points : pour les transporter sur une
#  autre numerisation, il suffit de savoir quelle similitude — rotation,
#  echelle, translation — mene de l'une a l'autre. C'est ce que cet
#  outil mesure, et il le mesure sans qu'on lui dise rien : la
#  correlation entre deux rendus tres differents du meme dessin suffit.
#
#  ON A VERIFIE QUE CELA MARCHE MEME DE TRES LOIN. La copie de service
#  de Gallica ne donne a la gravure du tableau 1 que 1250 points de
#  large, contre 5463 a notre couche de trait — quatre fois moins — et
#  le calage tombe juste malgre tout.
#
#  USAGE
#      python3 outils/originali.py caler  t01-apar-1 origine.jpg
#      python3 outils/originali.py compar t01-apar-1 origine.jpg 0.79 0.20
# ===================================================================

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numeri as N                                          # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
CATALOGO = RACINE / "gravuri" / "originali.json"


def gris(chemin):
    """L'image en gris, l'encre en noir, en flottant normalise."""
    im = Image.open(chemin)
    if im.mode not in ("L", "I;16"):
        im = im.convert("L")
    a = np.asarray(im).astype(np.float32)
    if a.max() > 255:
        a = a / 257.0
    return a


def notre_trait(cle):
    """Notre couche de trait, remise a l'endroit : l'encre en noir."""
    a = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")).astype(np.float32)
    return 255.0 - a


def centrer(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 1e-6 else a


# LA PLANCHE PEUT ETRE COUCHEE DANS LA NUMERISATION. Les feuillets sont
# relies dans le sens de la hauteur et la gravure y est de travers ; on
# essaie donc les quatre quarts de tour, et l'on garde celui qui accroche.
def orientations(a):
    for k in range(4):
        yield k, np.rot90(a, k)


def caler(cle, chemin, large=1100, verbeux=True):
    """La similitude qui mene de notre planche a la numerisation.

    Rend (M, score, tour) : M est la matrice 2x3 qui envoie un point de
    NOTRE planche, en points, sur la numerisation, en points.
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
        # La gravure n'occupe qu'une partie du feuillet : on cherche
        # notre planche DANS la page, a plusieurs echelles.
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
    # De notre planche (points) vers la numerisation TOURNEE (points).
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
    """Le meme detail dans les trois etats, cote a cote."""
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
            ("detalo", Image.open(RACINE / "gravuri" / f"{cle}-detalo.webp")
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
    sortie = Path(sortie or (RACINE / "gravuri" / "kontrolo" /
                             f"{cle}-origino.png"))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    pl.save(sortie)
    print(f"  comparaison dans {sortie}")


def main(args):
    if len(args) < 2:
        raise SystemExit(__doc__)
    verbe, cle, chemin = args[0], args[1], args[2]
    if verbe == "caler":
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
