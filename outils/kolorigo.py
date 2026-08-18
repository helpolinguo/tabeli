#!/usr/bin/env python3
# ===================================================================
#  kolorigo.py — rendre a une planche la couleur de son original.
#
#  Deux tirages de la meme pierre nous sont parvenus, et ils ne
#  portent pas la meme chose. Le fac-simile de la Bibliotheque
#  nationale est LA PIERRE NOIRE SEULE, tiree sans les couleurs :
#  quatre mille cinq cents points de large, chaque hachure nette,
#  chaque numero lisible. L'original en couleur est la meme pierre
#  AVEC ses pierres de teinte, mais photographie a moitie moins fin —
#  deux mille trois cents points — et le trait y est mou.
#
#  L'UN A LE TRAIT, L'AUTRE A LE LAVIS. C'est tout le probleme, et
#  c'en est aussi la solution.
#
#  CE QUI NE MARCHE PAS. On prend d'abord la clarte du fac-simile et
#  la couleur de l'original — c'est la recette ordinaire, celle qui
#  sert a coloriser une photographie noir et blanc. Ici elle rate, et
#  pour une raison qui se voit des le premier toit : dans l'original
#  ce toit est un lavis d'ardoise, plein et sombre ; dans le
#  fac-simile c'est du papier blanc sous une hachure. La clarte du
#  fac-simile efface donc le lavis, et l'on obtient une gravure
#  teintee, pale, ou les aplats ont disparu.
#
#  ON RECOMMENCE DONC COMME L'IMPRIMEUR : le lavis dessous, le trait
#  dessus. C'est une multiplication — la ou la pierre noire a pose son
#  encre, la couleur s'assombrit ; la ou elle a laisse le papier, la
#  couleur passe entiere. Le toit redevient ardoise, et la hachure
#  reste nette.
#
#  LE LAVIS SEUL. L'original porte, lui aussi, le trait de la pierre
#  noire ; le multiplier tel quel doublerait chaque ligne. On l'en
#  debarrasse par une FERMETURE morphologique : le trait est fin et
#  sombre, elle l'efface ; un chapeau noir est large, elle le garde.
#
#  LE PAPIER A JAUNI, LA COULEUR A PASSE. On ramene le papier vers le
#  neutre — pas entierement : il etait ivoire, non blanc — et l'on
#  ranime la teinte d'un sixieme. Au-dela, la planche prend un air de
#  chromo moderne qu'elle n'a jamais eu.
#
#  USAGE
#      python3 outils/kolorigo.py t14-apar-1 originali/t14col.pdf
#      python3 outils/kolorigo.py t14-apar-1 originali/t14col.pdf --essai
#
#  « --essai » ne sert rien : il ecrit une bande de comparaison dans
#  gravuri/kontrolo/ pour juger le reglage a l'oeil.
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
import numeri as N                                          # noqa: E402
import originali as O                                       # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
KOVRI = RACINE / "originali" / "kovri"

FERMO = 25        # le disque qui efface le trait de l'original
BLANKESO = 0.40   # part du jaune du papier qu'on retire
VIVECO = 1.15     # ranimation de la teinte
MARGE = O.MARGE_FILET


def tirar(pdf):
    """L'image telle qu'elle est DANS le PDF, sans la reechantillonner.

    pdftoppm rendrait la page a une definition qu'on choisirait, et
    l'on ajouterait un rechantillonnage a celui de la prise de vue.
    pdfimages rend le JPEG que le fichier contient, point pour point.
    """
    d = Path(tempfile.mkdtemp())
    subprocess.run(["pdfimages", "-all", str(pdf), str(d / "p")], check=True)
    fs = sorted(d.glob("p-*"))
    if not fs:
        raise SystemExit(f"  aucune image dans {pdf}")
    f = max(fs, key=lambda p: p.stat().st_size)
    return np.asarray(Image.open(f).convert("RGB"))


# LE CADRE DE L'ORIGINAL, pour le poser sur celui de la planche. Le
# filet de la gravure court d'un bord a l'autre : c'est la premiere
# rangee, en venant du dehors, ou plus de la moitie des points sont
# sombres. Le titre imprime au-dessus n'en couvre pas la moitie ; le
# filet, si.
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
    """La matrice qui pose l'original en couleur sur la planche."""
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
    # L'AFFINAGE. Le cadre pose l'original a quelques points pres ; on
    # finit par ECC, sur les deux images floutees a l'echelle ou toutes
    # deux ont encore du signal. Plus fin, l'original n'a plus rien a
    # dire : sa prise de vue s'arrete la ou le fac-simile commence.
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
    # ET L'ON FINIT PAR UNE TRANSLATION, MESUREE EN GRAND. ECC travaille
    # sur une reduction a douze cents points ; dix points de decalage
    # sur la planche n'en font que deux et demi chez lui, et il les
    # laisse passer. On les voit pourtant : le lavis se pose a cote de
    # la figure. On mesure donc le glissement qui reste sur les images
    # entieres, floutees a l'echelle du lavis -- la seule ou les deux
    # tirages se ressemblent -- et on l'ajoute.
    for _ in range(3):
        T, n, co = afini(T, col, gp)
    if verbeux:
        print(f"  recalage : correlation {cc:.4f} puis {co:.3f} "
              f"sur {n} tuiles")
    return T, gp


# CE QUE LA SIMILITUDE NE RATTRAPE PAS. Au tableau 16 l'original a ete
# photographie de biais, ou la feuille bombait : le lavis se pose bien
# au milieu et glisse de vingt points aux angles. Une similitude ne sait
# pas cela — il lui faudrait plier.
#
# On mesure donc le glissement sur une grille serree, et on l'ajuste par
# un POLYNOME DU SECOND DEGRE en x et y : six coefficients par axe, de
# quoi suivre une perspective ou un gonflement, pas assez pour suivre le
# bruit. Puis on remappe. C'est une deformation douce, et elle ne porte
# que sur le lavis : le trait, lui, vient du fac-simile et ne bouge pas.
def plier(T, col, gp, sigma=12.0, marge=70, cases=(7, 10), R=190,
          seuil=0.35, verbeux=True):
    """Le champ de glissement, ajuste par un polynome, puis applique."""
    HN, LN = gp.shape
    pose = cv2.warpAffine(col, T, (LN, HN), flags=cv2.INTER_CUBIC,
                          borderValue=(255, 255, 255))
    a = cv2.GaussianBlur(cv2.cvtColor(pose, cv2.COLOR_RGB2GRAY)
                         .astype(np.float32), (0, 0), sigma)
    b = cv2.GaussianBlur(gp, (0, 0), sigma)
    P, D = [], []
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
            if mx < seuil:
                continue
            P.append((x, y))
            D.append((loc[0] - marge, loc[1] - marge))
    if len(P) < 12:
        if verbeux:
            print(f"  pas de quoi plier ({len(P)} tuiles) : on laisse droit")
        return pose
    # LE CHAMP SE FAIT PAR DIFFUSION, non par formule. Un polynome du
    # second degre laissait vingt points d'ecart au tableau 16 : la
    # deformation n'est pas une perspective, c'est une feuille qui a
    # gondole, et cela ne s'ecrit pas. On pose donc les glissements
    # mesures sur une grille grossiere, on comble les trous par
    # diffusion — chaque tour remplace un point vide par la moyenne de
    # ses voisins — et l'on floute largement. Ce qui reste est doux par
    # construction : le champ ne peut pas inventer un pli plus fin que
    # la maille.
    P = np.float64(P); D = np.float64(D)
    pas = 64
    gh, gw = HN // pas + 2, LN // pas + 2
    fx = np.zeros((gh, gw), np.float32); fy = np.zeros_like(fx)
    pn = np.zeros_like(fx)
    for (x, y), (dx, dy) in zip(P, D):
        j, i = int(y / pas), int(x / pas)
        fx[j, i] += dx; fy[j, i] += dy; pn[j, i] += 1
    plein = pn > 0
    fx[plein] /= pn[plein]; fy[plein] /= pn[plein]
    for _ in range(600):
        for f in (fx, fy):
            m = cv2.blur(f, (3, 3))
            f[~plein] = m[~plein]
    fx = cv2.GaussianBlur(fx, (0, 0), 2.0)
    fy = cv2.GaussianBlur(fy, (0, 0), 2.0)
    ys, xs = np.mgrid[0:HN, 0:LN].astype(np.float32)
    gx = cv2.resize(fx, (LN, HN), interpolation=cv2.INTER_CUBIC)
    gy = cv2.resize(fy, (LN, HN), interpolation=cv2.INTER_CUBIC)
    out = cv2.remap(pose, xs - gx, ys - gy, cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    if verbeux:
        print(f"  pliage sur {len(P)} tuiles : glissement de "
              f"{np.abs(D).max():.0f} points au plus")
    return out


# LE RECALAGE SE FINIT TUILE PAR TUILE. ECC travaille sur une reduction
# a douze cents points : dix points de decalage sur la planche n'en font
# que deux et demi chez lui, et il les laisse passer. On les voit
# pourtant — le lavis se pose a cote de la figure — et au tableau 16 le
# cadre de l'original ne donne meme pas le bon rapport : trois pour cent
# d'ecart en hauteur, la prise de vue n'etait pas d'aplomb.
#
# On mesure donc, sur une grille, ou chaque morceau de l'original veut
# aller ; on ne garde que les morceaux qui se reconnaissent franchement,
# et l'on ajuste sur eux la similitude qui les mene tous a la fois. Le
# flou de douze points n'est pas un defaut : c'est l'echelle a laquelle
# les DEUX tirages se ressemblent, l'un n'ayant que le trait et l'autre
# que le lavis.
def afini(T, col, gp, sigma=12.0, marge=90, cases=(5, 7), R=280, seuil=0.35):
    """Un tour de recalage : la similitude qui suit le mieux les tuiles."""
    HN, LN = gp.shape
    pose = cv2.warpAffine(col, T, (LN, HN), flags=cv2.INTER_LINEAR,
                          borderValue=(255, 255, 255))
    a = cv2.GaussianBlur(cv2.cvtColor(pose, cv2.COLOR_RGB2GRAY)
                         .astype(np.float32), (0, 0), sigma)
    b = cv2.GaussianBlur(gp, (0, 0), sigma)
    ici, la, sco = [], [], []
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
            if mx < seuil:
                continue
            ici.append((x, y))
            la.append((x + loc[0] - marge, y + loc[1] - marge))
            sco.append(float(mx))
    if len(ici) < 6:
        return T, len(ici), float(np.median(sco)) if sco else float("nan")
    M, _ = cv2.estimateAffinePartial2D(np.float32(ici), np.float32(la),
                                       method=cv2.RANSAC,
                                       ransacReprojThreshold=12.0)
    if M is None:
        return T, len(ici), float(np.median(sco))
    T2 = (np.vstack([M, [0, 0, 1]]) @ np.vstack([T, [0, 0, 1]]))[:2]
    return T2.astype(np.float32), len(ici), float(np.median(sco))


def lavis(col, fermo=FERMO, blankeso=BLANKESO, viveco=VIVECO, verbeux=True):
    """L'original debarrasse de son trait, et rendu a ses couleurs."""
    e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (fermo, fermo))
    w = cv2.morphologyEx(col, cv2.MORPH_CLOSE, e)
    lab = cv2.cvtColor(w, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    # LE TON DU PAPIER se prend sur le papier, c'est-a-dire sur ce que
    # la planche a de plus clair : le blanc de reserve entre les
    # hachures. Un cinquieme de la surface suffit a le donner.
    pap = L > np.percentile(L, 80)
    ca, cb = float(np.median(A[pap])), float(np.median(B[pap]))
    if verbeux:
        print(f"  le papier tire sur a={ca:+.1f} b={cb:+.1f} ; "
              f"on lui en retire {blankeso:.0%}")
    A = (A - blankeso * ca) * viveco
    B = (B - blankeso * cb) * viveco
    return cv2.cvtColor(np.dstack([L, np.clip(A + 128, 0, 255),
                                   np.clip(B + 128, 0, 255)]).astype(np.uint8),
                        cv2.COLOR_LAB2RGB)


def kolorigi(cle, pdf, essai=False, **kw):
    col = tirar(pdf)
    print(f"  {Path(pdf).name} : {col.shape[1]} x {col.shape[0]} points")
    T, gp = poser(cle, col)
    pose = plier(T, col, gp)
    w = lavis(pose, **kw)
    # LE TIRAGE : le lavis dessous, la pierre noire dessus.
    out = (w.astype(np.float32) * (gp[..., None] / 255.0))
    out = out.clip(0, 255).astype(np.uint8)
    KOVRI.mkdir(parents=True, exist_ok=True)
    dest = KOVRI / f"{cle}-koloro.png"
    Image.fromarray(out).save(dest)
    print(f"  ecrit dans {dest}")
    if essai:
        bande(cle, pose, out, gp)
    return dest


def bande(cle, pose, out, gp, boite=None):
    """Une bande de comparaison : l'original, le tirage, la pierre."""
    HN, LN = gp.shape
    if boite is None:
        x = round(0.72 * LN)
        y = round(0.37 * HN)
        boite = (x, y, x + 600, y + 400)
    x0, y0, x1, y1 = boite
    trio = [pose[y0:y1, x0:x1], out[y0:y1, x0:x1],
            np.dstack([gp[y0:y1, x0:x1].astype(np.uint8)] * 3)]
    sep = np.full((y1 - y0, 6, 3), 255, np.uint8)
    im = np.hstack([x for p in zip(trio, [sep] * 3) for x in p][:-1])
    d = N.KONTROLO / f"{cle}-koloro.png"
    d.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(im).save(d)
    print(f"  l'original, le tirage et la pierre dans {d}")


def main(args):
    if len(args) < 2:
        raise SystemExit(__doc__ or "kolorigo.py <cle> <original.pdf>")
    cle, pdf = args[0], args[1]
    dest = kolorigi(cle, pdf, essai="--essai" in args)
    if "--essai" in args:
        return
    O.servir(cle, dest)
    cat = RACINE / "gravuri" / "gravuri.json"
    tout = json.loads(cat.read_text(encoding="utf-8"))
    tout[cle]["koloro"] = True
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {cle} : servi en couleur.")


if __name__ == "__main__":
    main(sys.argv[1:])
