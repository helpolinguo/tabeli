#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imaji.py — extrait du fac-similé les parties qui ne sont PAS de la
composition : la gravure du tableau mural n° 12, le cadre ornemental de
la quatrième de couverture française.

    python3 outils/imaji.py io 111 --haut 0.06 --bas 0.50 --nom tabelo-12
    python3 outils/imaji.py fr 96  --nom kadro-fr

CE QU'ON EXTRAIT, ET POURQUOI PAS AUTREMENT. Tout le reste du volume se
COMPOSE : une ligne du fac-similé devient une ligne de source, et la
fonte la rend. Une gravure sur bois et un encadrement Art nouveau, non.
Les reproduire en caractères serait les inventer ; les omettre, comme
on l'avait fait d'abord — un `\\VUsaut` et un commentaire —, c'est
publier une page qui ment sur ce qu'elle montrait.

On les prélève donc sur le scan, à leur emplacement mesuré, et on les
pose dans la page à leur taille relevée. C'est le seul endroit du
projet où l'image du fac-similé entre dans le PDF, et cela se justifie
par la nature de l'objet : ce n'est pas du texte.

LE NETTOYAGE EST MINIMAL, et c'est voulu. On redresse le contraste sur
les centiles — comme `lekto.py` — et on ne fait rien d'autre : ni
débruitage, ni seuillage. Une gravure passée au noir et blanc perd ses
gris, et le grain du papier de 1926 fait partie de ce qu'on reproduit.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventaire import bloc, otsu  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "ornamenti"


def extraire(langue, n, haut, bas, nom, largeur=1600):
    src = RACINE / "skan" / langue / f"f-{n:03d}.jpg"
    im = Image.open(src).convert("L")
    g = np.asarray(im)

    # Le cadrage se prend sur la BOITE D'ENCRE et non sur l'image : le
    # bord du scan varie d'un feuillet a l'autre, et une fraction de
    # l'image entiere ne designerait pas la meme chose sur deux pages.
    b = bloc(g < otsu(g))
    if b is None:
        print("aucun bloc d'encre")
        return None
    x0, y0, x1, y1 = b
    h = y1 - y0
    y_a = int(y0 + haut * h)
    y_b = int(y0 + bas * h)
    air = int(0.02 * (x1 - x0))
    coupe = im.crop((max(0, x0 - air), y_a,
                     min(g.shape[1], x1 + air), y_b))

    a = np.asarray(coupe, float)
    lo, hi = np.percentile(a, [1, 99])
    if hi - lo < 1:
        hi = lo + 1
    a = np.clip((a - lo) * 255.0 / (hi - lo), 0, 255)
    coupe = Image.fromarray(a.astype("uint8"))

    w, hh = coupe.size
    if w > largeur:
        coupe = coupe.resize((largeur, int(hh * largeur / w)), Image.LANCZOS)

    SORTIE.mkdir(exist_ok=True)
    p = SORTIE / f"{nom}.png"
    coupe.save(p, optimize=True)
    w2, h2 = coupe.size
    # Le rapport largeur/hauteur DE LA ZONE PRELEVEE, rapporte a la
    # justification : c'est ce qui permet de la poser dans la page a la
    # taille qu'elle occupe sur le papier.
    part = (x1 - x0 + 2 * air) / (x1 - x0)
    print(f"{p}  ({w2}x{h2} px)")
    print(f"  largeur = {part:.3f} x la justification")
    print(f"  hauteur = {(y_b - y_a) / (x1 - x0 + 2 * air):.4f} "
          f"x sa propre largeur")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("langue")
    ap.add_argument("feuillet", type=int)
    ap.add_argument("--haut", type=float, default=0.0)
    ap.add_argument("--bas", type=float, default=1.0)
    ap.add_argument("--nom", default="ornamento")
    ap.add_argument("--largeur", type=int, default=1600)
    a = ap.parse_args()
    extraire(a.langue, a.feuillet, a.haut, a.bas, a.nom, a.largeur)


if __name__ == "__main__":
    main()
