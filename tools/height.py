#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
altox.py — mesure la HAUTEUR D'X du fac-similé, et en déduit le corps.

    python3 tools/altox.py io
    python3 tools/altox.py fr

POURQUOI. Le corps était jusqu'ici déduit du pas des lignes par un
rapport posé à 1,20, valeur d'usage pour l'impression de labeur de ce
temps. Elle allait à peu près pour le livret ido (294 lignes trop
courtes sur 100 pages, soit 3 par page) et pas du tout pour le livret
français (1179 sur 84, soit 14 par page) : là, une ligne sur trois
n'atteignait pas la marge, et TeX écartait les mots pour combler.

Un rapport n'est pas une mesure. Le corps se lit sur le fac-similé,
comme le reste — par la hauteur d'x, qui est la grandeur la plus
robuste d'une page imprimée : elle ne dépend ni des ascendantes ni des
descendantes, donc ni des mots que la ligne porte.

COMMENT. Pour chaque bande de ligne, on prend le profil d'encre par
rangée de pixels. Une ligne de texte y dessine un plateau — le corps
des lettres sans ascendante — encadré de deux épaules bien plus
maigres, les ascendantes en haut, les descendantes en bas. La hauteur
du plateau au-dessus de la moitié du maximum EST la hauteur d'x, à un
pixel près.

Le corps s'en déduit par le rapport propre à la fonte de composition :
XCharter place sa hauteur d'x à 0,481 de son corps. Composer à un corps
tel que la hauteur d'x tombe juste, c'est faire coïncider l'œil du
caractère composé et celui du fac-similé — ce qui gouverne à la fois la
couleur de la page et la chasse, donc le remplissage des lignes.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import bloc, otsu  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
# Hauteur d'x de la fonte de composition, en fraction du corps.
# Mesuree sur XCharter : \fontcharht avec le caractere « x ».
XCHARTER = 0.481


def hauteur_x_page(chemin):
    g = np.asarray(Image.open(chemin).convert("L"))
    encre = g < otsu(g)
    b = bloc(encre)
    if b is None:
        return []
    x0, y0, x1, y1 = b
    if (x1 - x0) < 0.25 * g.shape[1]:
        return []
    bande = encre[y0:y1 + 1, x0:x1 + 1]
    prof = bande.sum(1).astype(float)
    seuil = 0.04 * (x1 - x0)
    plein = prof > seuil

    # Decoupage en bandes de ligne.
    hauteurs = []
    i = 0
    n = len(plein)
    while i < n:
        if not plein[i]:
            i += 1
            continue
        j = i
        while j < n and plein[j]:
            j += 1
        seg = prof[i:j]
        if len(seg) >= 8:
            # LE PLATEAU, ET NON LA BANDE ENTIERE. La bande va du haut
            # des ascendantes au bas des descendantes ; le plateau, lui,
            # est la ou l'encre est dense, c'est-a-dire le corps des
            # lettres. On le prend a mi-hauteur du maximum : plus bas,
            # on happe les ascendantes ; plus haut, on rogne les
            # jambages.
            dedans = seg > 0.5 * seg.max()
            k = np.where(dedans)[0]
            if len(k):
                # Le plateau doit etre d'un seul tenant : deux lignes
                # collees par une ascendante en donneraient deux.
                h = k[-1] - k[0] + 1
                if 4 <= h <= 0.75 * len(seg):
                    hauteurs.append(h)
        i = j
    return hauteurs


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    inv = json.loads((RACINE / "tools" / f"inv-{langue}.json")
                     .read_text(encoding="utf-8"))
    pleines = sorted(int(k) for k, v in inv.items()
                     if not v.get("vide") and v.get("lignes", 0) >= 35)
    # Un echantillon suffit : la mesure est prise sur des milliers de
    # lignes, pas sur des pages.
    echantillon = pleines[::max(1, len(pleines) // 20)][:20]

    toutes = []
    par_page = {}
    for n in echantillon:
        h = hauteur_x_page(RACINE / "skan" / langue / f"f-{n:03d}.jpg")
        if h:
            par_page[n] = float(np.median(h))
            toutes.extend(h)

    if not toutes:
        print("aucune mesure")
        return

    # LA HAUTEUR D'X SE RAPPORTE A LA JUSTIFICATION, pas aux
    # millimetres : le fac-simile francais est une prise de vue, son
    # echelle change d'une page a l'autre, et une hauteur en pixels n'y
    # veut rien dire hors de sa page. Le RAPPORT, lui, est invariant.
    rapports = []
    for n, h in par_page.items():
        rapports.append(h / inv[str(n)]["largeur"])
    r = float(np.median(rapports))

    import re as _re
    kal = (RACINE / f"kalibro-{langue}.tex").read_text(encoding="utf-8")
    largeur_mm = float(_re.search(
        r"\\VUtexteLargeur\}\{([\d.]+)mm", kal).group(1))
    hx_mm = r * largeur_mm
    hx_pt = hx_mm / (25.4 / 72.27)
    corps = hx_pt / XCHARTER

    print(f"langue            : {langue}")
    print(f"pages echantillon : {len(par_page)}  ({len(toutes)} lignes)")
    print(f"hauteur d'x       : {np.median(toutes):.2f} px "
          f"(ecart-type {np.std(toutes):.2f})")
    print(f"  / justification : {r:.5f}")
    print(f"justification     : {largeur_mm:.2f} mm")
    print(f"hauteur d'x       : {hx_mm:.3f} mm = {hx_pt:.2f} pt")
    print()
    print(f"CORPS DEDUIT      : {corps:.2f} pt "
          f"(hauteur d'x XCharter = {XCHARTER} du corps)")


if __name__ == "__main__":
    main()
