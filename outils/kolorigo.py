#!/usr/bin/env python3
# ===================================================================
#  kolorigo.py — servir l'original en couleur a la place du fac-simile,
#  cadre sur le meme cadre, pour que les numeros tombent toujours juste.
#
#  Deux tirages de la meme pierre nous sont parvenus. Le fac-simile de
#  la Bibliotheque nationale est LA PIERRE NOIRE SEULE, tiree sans les
#  couleurs : quatre mille cinq cents points de large, chaque hachure
#  nette. L'original est la meme planche AVEC ses couleurs, mais
#  photographie a moitie moins fin.
#
#  POUR CES DEUX TABLEAUX, C'EST L'ORIGINAL QU'ON SERT. On y perd de la
#  finesse — le gros plan sur un numero est plus doux qu'ailleurs — et
#  l'on y gagne la planche telle qu'elle etait au mur de la classe.
#  C'est un choix d'edition, pas une mesure.
#
#  LE FAC-SIMILE NE DISPARAIT PAS POUR AUTANT : il reste la planche de
#  travail, celle ou les numeros se lisent et se posent, et il sert ici
#  de MIRE. Mille six cents numeros sont ranges en fractions de son
#  cadre ; si l'original se pose de travers, chaque gros plan tombe a
#  cote. On le recale donc sur lui, et l'on ne garde de lui que cela.
#
#  LE RECALAGE VA EN QUATRE TEMPS, du grossier au fin :
#
#   1. LE CADRE. Le filet de la gravure court d'un bord a l'autre ;
#      c'est la premiere rangee, en venant du dehors, ou plus de la
#      moitie des points sont sombres. Deux rectangles, une similitude.
#
#   2. ECC, sur les deux images floutees. Il descend a quelques points.
#
#   3. LA SIMILITUDE AJUSTEE TUILE PAR TUILE. ECC travaille sur une
#      reduction a douze cents points : dix points d'ecart sur la
#      planche n'en font que deux et demi chez lui, et il les laisse
#      passer. On mesure donc, sur une grille, ou chaque morceau veut
#      aller, et l'on ajuste la similitude qui les mene tous.
#
#   4. L'HOMOGRAPHIE. Il reste des ecarts, et au tableau 16 ils
#      atteignent soixante-dix points aux angles : l'objectif n'etait
#      pas d'aplomb sur la feuille. C'est de la perspective, et la
#      perspective s'ecrit en huit coefficients — une homographie, qui
#      mene toute droite sur une droite.
#
#      ON A ESSAYE UN CHAMP DE GLISSEMENT, et il faut dire pourquoi on
#      l'a retire : glissements mesures sur une grille au pas de
#      quarante, trous combles par diffusion, remappage. Le recalage
#      tombait a moins de dix points — et les facades du tableau 14
#      sortaient de travers. Un champ n'a aucune raison de respecter
#      un alignement : il suit ce qu'il mesure, tuile par tuile, et une
#      tuile qui se trompe de trois points tord tout son voisinage. Une
#      planche gauchie se voit ; dix points d'ecart sur un gros plan,
#      non. On garde donc les droites, et l'on rend les ecarts.
#
#  LE FLOU DE DOUZE POINTS, aux temps 2 a 4, n'est pas une negligence :
#  c'est la seule echelle a laquelle les deux tirages se ressemblent.
#  Plus fin, l'un n'a que le trait et l'autre que le lavis, et la
#  correlation tombe a rien — mesure faite, 0.04.
#
#  LA RESTAURATION est legere, et elle se compte :
#   — le papier a jauni : on lui retire deux cinquiemes de son jaune,
#     pas davantage. Il etait ivoire, non blanc ;
#   — la couleur a passe : on la ranime d'un sixieme. Au-dela, la
#     planche prend un air de chromo moderne qu'elle n'a jamais eu ;
#   — la prise de vue est molle : un leger masque flou lui rend son
#     mordant, sans halo visible.
#
#  ON REND A LA DEFINITION DE L'ORIGINAL, ni plus ni moins. Le porter a
#  celle du fac-simile ne fabriquerait pas un point de detail et
#  doublerait le poids du fichier.
#
#  USAGE
#      python3 outils/kolorigo.py t14-apar-1 originali/t14col.pdf
#      python3 outils/kolorigo.py t14-apar-1 originali/t14col.pdf --essai
#
#  « --essai » ne sert rien : il ecrit dans gravuri/kontrolo/ une bande
#  de comparaison — l'original brut, le rendu, le fac-simile — pour
#  juger le reglage et le recalage a l'oeil.
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

BLANKESO = 0.40   # part du jaune du papier qu'on retire
VIVECO = 1.15     # ranimation de la teinte
NETESO = 0.65     # force du masque flou
MARGE = O.MARGE_FILET
FLOU = 12.0       # l'echelle a laquelle les deux tirages se ressemblent
QUAL_KOLORO = 92  # qualite WebP du detail, plus haute qu'ailleurs


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
    """Ou chaque morceau de l'original veut aller, tuile par tuile."""
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
    """Un tour de recalage : la similitude qui suit le mieux les tuiles."""
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


# ON AJUSTE DEUX FOIS, DU LARGE AU SERRE. Le premier tour se mesure
# sur de grandes tuiles floutees a douze points : c'est robuste, et
# cela rattrape la perspective. Le second, sur des tuiles trois fois
# plus petites et un flou de cinq points, resserre.
#
# On ne va pas plus fin. Sous cinq points de flou les deux tirages ne
# se ressemblent plus assez pour se reconnaitre — l'un n'a que le
# trait, l'autre que le lavis — et la mesure se met a suivre le bruit.
PLIADI = ((FLOU, 70, (7, 10), 190, 0.35),
          (5.0, 40, (12, 16), 110, 0.30))


# UNE DROITE DE LA PIERRE DOIT RESTER DROITE. Premiere version, on
# posait les glissements mesures sur une grille au pas de quarante, on
# comblait les trous par diffusion et l'on remappait : le recalage
# tombait a moins de dix points, et les facades du tableau 14 sortaient
# de travers. Un champ de glissement n'a aucune raison de respecter
# l'alignement — il suit ce qu'il mesure, tuile par tuile, et une tuile
# qui se trompe de trois points tord tout son voisinage.
#
# LA PHOTOGRAPHIE D'UNE FEUILLE PLANE EST UNE HOMOGRAPHIE, et rien de
# plus : l'objectif n'etait pas d'aplomb, voila tout. Huit coefficients
# suffisent a le dire, et une homographie mene toute droite sur une
# droite. On ajuste donc les huit sur les memes tuiles, et l'on
# s'arrete la : ce qui reste apres elle n'est plus de la perspective
# mais du gondolement du papier, et le redresser couterait plus cher
# qu'il ne rapporte.
def projekti(T, col, gp, verbeux=True):
    """L'homographie qui reste, en points de la planche."""
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


# ON A ESSAYE DE PLIER SUR LES NUMEROS EUX-MEMES, et c'est pire.
# L'idee etait bonne : on sait ou sont les mille six cent soixante-seize
# numeros sur le fac-simile, au point pres, et ce sont eux que le gros
# plan doit viser — pourquoi caler sur du paysage ce qu'on peut caler
# sur eux ? Parce que le suiveur ne les retrouve pas assez surement
# dans la photographie : sur quatre-vingt-treize numeros du tableau 14
# il n'en reconnait franchement que quarante-huit, et le champ tire de
# ces quarante-huit-la fait passer l'ecart median de seize a
# vingt-quatre points. Une poignee de reperes bruyants, etires par la
# diffusion, deforme plus qu'elle ne corrige. Mesure faite deux fois,
# sur les deux planches.
#
# ET CE QUI RESTE D'ECART N'EST PAS UNE ERREUR DE MESURE : quinze a
# vingt points, quel que soit le reglage du suiveur — fenetre de
# quatre-vingts points ou de cent vingt, flou d'un point et demi ou de
# trois, seuil de confiance a trois dixiemes ou a six. Ce sont DEUX
# EXEMPLAIRES DIFFERENTS de la meme planche : tires a des dates
# differentes, sur un papier qui n'a pas retreci pareil, et dont les
# pierres n'etaient pas calees au meme point. Un demi pour cent sur
# quatre mille cinq cents points fait vingt points, et c'est exactement
# ce qu'on trouve. Aucune similitude ne rattrape cela.
#
# Seize points d'ecart sur une vue de gros plan qui en montre deux cent
# quatre-vingt-dix : le numero vise n'est pas au centre au point pres,
# il est a un vingtieme du centre. On s'en tient la.


def rendre(col, T, H, taille, echelo, interp=cv2.INTER_LANCZOS4):
    LT, HT = taille
    ys, xs = np.mgrid[0:HT, 0:LT].astype(np.float32)
    # de la sortie vers la planche, en defaisant l'ajustement projectif
    px, py = xs / echelo, ys / echelo
    w = H[2, 0] * px + H[2, 1] * py + H[2, 2]
    px, py = ((H[0, 0] * px + H[0, 1] * py + H[0, 2]) / w,
              (H[1, 0] * px + H[1, 1] * py + H[1, 2]) / w)
    # de la planche vers l'original
    Ti = cv2.invertAffineTransform(T)
    sx = Ti[0, 0] * px + Ti[0, 1] * py + Ti[0, 2]
    sy = Ti[1, 0] * px + Ti[1, 1] * py + Ti[1, 2]
    return cv2.remap(col, sx, sy, interp,
                     borderMode=cv2.BORDER_CONSTANT,
                     borderValue=(255, 255, 255))


def restaurar(im, blankeso=BLANKESO, viveco=VIVECO, neteso=NETESO,
              verbeux=True):
    """Le papier rendu au neutre, la teinte ranimee, le trait raffermi."""
    lab = cv2.cvtColor(im, cv2.COLOR_RGB2LAB).astype(np.float32)
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
    # LE MORDANT SE REND A LA CLARTE SEULE. Aiguiser les trois couleurs
    # ensemble reveille le grain colore de la photographie ; sur la
    # clarte, il ne reveille que le trait.
    # (La clarte d'un Lab TIRE D'UNE IMAGE A HUIT BITS va de 0 a 255, non
    #  de 0 a 100 : la borner a cent ecrasait tout le haut du ton, et la
    #  planche sortait en aplats.)
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
    # LA DEFINITION DE SORTIE EST CELLE DE L'ORIGINAL. L'echelle de la
    # similitude dit de combien la photographie a ete grandie pour
    # tomber sur le fac-simile ; on rend l'inverse.
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
    """L'original brut, le rendu, le fac-simile : la meme portion."""
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
    O.servir(cle, dest, qual_detalo=QUAL_KOLORO)
    cat = RACINE / "gravuri" / "gravuri.json"
    tout = json.loads(cat.read_text(encoding="utf-8"))
    tout[cle]["koloro"] = True
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {cle} : servi en couleur.")


if __name__ == "__main__":
    main(sys.argv[1:])
