#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lekto.py — prepare un feuillet pour la LECTURE (releve a l'oeil).

Le fac-simile brut ne se lit pas commodement : bandes noires du bord,
marges larges, contraste faible sur le livret francais, qui est une
prise de vue et non un passage au scanner. Cet outil recadre sur la
boite d'encre, redresse le contraste et sort une image a la largeur
demandee.

    python3 outils/lekto.py io 7            # un feuillet
    python3 outils/lekto.py fr 9 13         # une tranche
    python3 outils/lekto.py io 7 --moitie   # coupe en deux dans la hauteur

Sortie : outils/.lekto/<langue>-<n>[a|b].png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventaire import bloc, otsu  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "outils" / ".lekto"
LARGEUR = 1500
AIR = 0.035          # air laisse autour du bloc, en fraction de sa largeur


def prepare(langue, n, moitie=False, largeur=LARGEUR):
    src = RACINE / "skan" / langue / f"f-{n:03d}.jpg"
    im = Image.open(src).convert("L")
    g = np.asarray(im)
    encre = g < otsu(g)
    b = bloc(encre)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    # UNE PAGE BLANCHE N'A PAS DE BLOC. Les feuillets 48 et 76 du
    # livret ido sont des versos vierges : 0,1 % d'encre, du grain de
    # papier. La detection y rend une boite degeneree — quelques
    # pixels de large sur toute la hauteur — et la mise a l'echelle sur
    # 1500 px de large fabriquait alors une image d'un milliard de
    # pixels, que PIL refusait d'ouvrir. On le dit plutot que de le
    # subir.
    if (x1 - x0) < 0.25 * g.shape[1] or (y1 - y0) < 0.10 * g.shape[0]:
        print(f"  {langue} {n} : feuillet vierge (aucun bloc d'encre)")
        return []
    air = int(AIR * (x1 - x0))
    x0 = max(0, x0 - air)
    y0 = max(0, y0 - air)
    x1 = min(g.shape[1] - 1, x1 + air)
    y1 = min(g.shape[0] - 1, y1 + air)
    im = im.crop((x0, y0, x1 + 1, y1 + 1))
    # Le contraste se reprend sur les CENTILES et non sur les extremes :
    # une poussiere noire et un eclat blanc suffiraient a annuler
    # l'etirement s'il se calait sur le minimum et le maximum.
    a = np.asarray(im, float)
    lo, hi = np.percentile(a, [2, 98])
    if hi - lo < 1:
        hi = lo + 1
    a = np.clip((a - lo) * 255.0 / (hi - lo), 0, 255)
    im = Image.fromarray(a.astype("uint8"))
    im = ImageOps.autocontrast(im, cutoff=0)
    SORTIE.mkdir(exist_ok=True)
    morceaux = [(im, "")]
    if moitie:
        h = im.size[1]
        rec = int(h * 0.54)          # recouvrement : deux lignes communes
        morceaux = [(im.crop((0, 0, im.size[0], rec)), "a"),
                    (im.crop((0, h - rec, im.size[0], h)), "b")]
    chemins = []
    for morceau, suf in morceaux:
        w, h = morceau.size
        morceau = morceau.resize((largeur, int(h * largeur / w)),
                                 Image.LANCZOS)
        p = SORTIE / f"{langue}-{n:03d}{suf}.png"
        morceau.save(p)
        chemins.append(p)
    return chemins


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    moitie = "--moitie" in sys.argv
    langue = args[0]
    debut = int(args[1])
    fin = int(args[2]) if len(args) > 2 else debut
    for n in range(debut, fin + 1):
        for p in prepare(langue, n, moitie):
            print(p)


if __name__ == "__main__":
    main()
