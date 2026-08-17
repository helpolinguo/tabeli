#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inventaire.py — releve, feuillet par feuillet, la GEOMETRIE de chaque
page des deux fac-similes : boite d'encre, folio, premiere et derniere
ligne de base, pas des lignes.

Le principe est celui du projet « Kompleta Gramatiko » : aucune valeur
du preambule LaTeX ne s'invente, chacune sort d'une mediane prise sur
l'ensemble des pages pleines.

    python3 outils/inventaire.py io          # les 116 feuillets ido
    python3 outils/inventaire.py fr 1 20     # une tranche

Sortie : outils/inv-<langue>.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
SKAN = RACINE / "skan"

# Seuil de binarisation. Les deux scans sont en niveaux de gris ; le
# papier du livret ido est piquete, celui du livret francais est sale et
# gondole. Un seuil fixe sur 255 mordrait sur le grain : on prend le
# seuil d'Otsu, calcule page par page.
def otsu(g):
    hist = np.bincount(g.ravel(), minlength=256).astype(float)
    tot = hist.sum()
    som = np.dot(np.arange(256), hist)
    somB = 0.0
    wB = 0.0
    mx = -1.0
    seuil = 128
    for t in range(256):
        wB += hist[t]
        if wB == 0:
            continue
        wF = tot - wB
        if wF == 0:
            break
        somB += t * hist[t]
        mB = somB / wB
        mF = (som - somB) / wF
        v = wB * wF * (mB - mF) ** 2
        if v > mx:
            mx = v
            seuil = t
    return seuil


def profils(chemin, dpi):
    """Renvoie (encre, hauteur, largeur, dpi) — encre = tableau booleen."""
    im = Image.open(chemin).convert("L")
    g = np.asarray(im)
    s = otsu(g)
    encre = g < s
    return encre


def _plage_centrale(profil, seuil, ecart):
    """Plus longue plage continue au-dessus du seuil, trous de moins de
    `ecart` pixels ignores, et qui contienne le milieu du profil.

    LE BORD DU SCAN N'EST PAS DE L'ENCRE. Les deux fac-similes portent,
    sur un bord ou sur l'autre, une bande noire — l'ombre de la reliure
    pour le livret ido, le fond du plateau pour le livret francais. Prise
    telle quelle, la boite d'encre allait donc d'un bord a l'autre de
    l'image et TOUTES les mesures de justification etaient fausses. On ne
    retient que la plage qui contient le milieu de la page : la bande de
    bord en est separee par la marge blanche, large de plus de `ecart`.
    """
    plein = profil > seuil
    n = len(plein)
    plages = []
    i = 0
    while i < n:
        if plein[i]:
            j = i
            k = i
            while j < n:
                if plein[j]:
                    k = j
                    j += 1
                elif j - k <= ecart:
                    j += 1
                else:
                    break
            plages.append((i, k))
            i = j
        else:
            i += 1
    if not plages:
        return None
    mil = n // 2
    dedans = [p for p in plages if p[0] <= mil <= p[1]]
    if dedans:
        return max(dedans, key=lambda p: p[1] - p[0])
    return max(plages, key=lambda p: p[1] - p[0])


def bloc(encre, marge_bruit=0.010, ecart=60):
    """Boite du bloc d'encre, bord du scan ecarte.

    En DEUX temps, et l'ordre compte. Les colonnes d'abord : c'est la
    largeur qui porte la justification, et c'est sur les bords lateraux
    que se trouvent les bandes noires. Les lignes ENSUITE, mesurees sur
    les seules colonnes retenues — sans quoi le bord noir, qui court sur
    toute la hauteur, remplit le profil vertical et la boite prend la
    page entiere. La plage centrale ne sert qu'aux colonnes : appliquee
    aux lignes, elle coupait la page a la premiere fenetre blanche un peu
    large (blanc de titre, fin de section) et la boite commencait au
    milieu du texte.
    """
    h, w = encre.shape
    colonne = encre.sum(0) / h
    px = _plage_centrale(colonne, marge_bruit, ecart)
    if px is None:
        return None
    x0, x1 = px
    bande = encre[:, x0:x1 + 1]
    ligne = bande.sum(1) / max(1, x1 - x0 + 1)
    ys = np.where(ligne > marge_bruit)[0]
    if len(ys) == 0:
        return None
    return int(x0), int(ys[0]), int(x1), int(ys[-1])


def lignes_de_base(encre, x0, x1, y0, y1, seuil=0.02):
    """Ordonnees des lignes de base.

    La ligne de base n'est pas le haut d'une ligne : celui-ci depend des
    ascendantes que la ligne porte, donc du texte. Le BAS de la masse
    d'encre d'une ligne, lui, ne bouge pas — sauf descendantes, qui sont
    minoritaires. On prend donc, pour chaque bande d'encre, l'ordonnee
    ou le profil retombe sous le seuil.
    """
    bande = encre[y0:y1 + 1, x0:x1 + 1]
    prof = bande.sum(1) / max(1, x1 - x0)
    plein = prof > seuil
    bases = []
    dans = False
    for i, p in enumerate(plein):
        if p and not dans:
            dans = True
        elif not p and dans:
            dans = False
            bases.append(y0 + i)
    if dans:
        bases.append(y1)
    return bases


def pas(bases):
    if len(bases) < 4:
        return None
    d = np.diff(bases)
    d = d[(d > 0.6 * np.median(d)) & (d < 1.6 * np.median(d))]
    return float(np.median(d)) if len(d) else None


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    debut = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    fin = int(sys.argv[3]) if len(sys.argv) > 3 else 999
    dossier = SKAN / langue
    fichiers = sorted(dossier.glob("f-*.jpg"))
    out = {}
    for f in fichiers:
        n = int(f.stem.split("-")[1])
        if not (debut <= n <= fin):
            continue
        encre = profils(f, None)
        h, w = encre.shape
        b = bloc(encre)
        if b is None:
            out[n] = {"vide": True, "px": [w, h]}
            continue
        x0, y0, x1, y1 = b
        bases = lignes_de_base(encre, x0, x1, y0, y1)
        out[n] = {
            "px": [w, h],
            "bloc": [x0, y0, x1, y1],
            "largeur": x1 - x0 + 1,
            "hauteur": y1 - y0 + 1,
            "lignes": len(bases),
            "bases": bases,
            "pas": pas(bases),
        }
        print(f"{n:3d}  bloc {x0:5d},{y0:5d} → {x1:5d},{y1:5d}"
              f"  l={x1-x0+1:5d}  lignes={len(bases):3d}"
              f"  pas={out[n]['pas']}")
    (RACINE / "outils" / f"inv-{langue}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
