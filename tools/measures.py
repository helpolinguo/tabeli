#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measures.py — draws from tools/inventory-<language>.json the CONSTANTS of
the LaTeX preamble: measure, line pitch, scale of the scan.

    python3 tools/measures.py io
    python3 tools/measures.py fr

Nothing here is invented: every constant is a median, together with its
standard deviation and the number of pages it is taken over. Short pages
(fewer than `MIN_LINES` lines) are set aside: a title page or the end of a
section measures neither the text width nor the pitch.
"""
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
MINLIGNES = 25


def charger(langue):
    p = RACINE / "tools" / f"inv-{langue}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def med(v):
    v = np.asarray([x for x in v if x is not None], float)
    return float(np.median(v)), float(np.std(v)), len(v)


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    inv = charger(langue)
    pleines = {int(k): v for k, v in inv.items()
               if not v.get("vide") and v.get("lignes", 0) >= MINLIGNES}
    largeurs = [v["largeur"] for v in pleines.values()]
    pas = [v["pas"] for v in pleines.values() if v.get("pas")]

    lm, ls, ln = med(largeurs)
    pm, ps, pn = med(pas)

    print(f"langue          : {langue}")
    print(f"pages retenues  : {ln} (>= {MINLIGNES} lignes)")
    print(f"justification   : {lm:.1f} px   (ecart-type {ls:.1f})")
    print(f"pas des lignes  : {pm:.2f} px   (ecart-type {ps:.2f})")
    print(f"lignes par page : {int(np.median([v['lignes'] for v in pleines.values()]))}")
    print()
    print("L'ECHELLE DU SCAN N'EST PAS DONNEE PAR LE FICHIER.")
    print("Les deux fac-similes sont des prises de vue : le nombre de")
    print("pixels par millimetre n'y est pas celui que declare le PDF.")
    print("On l'obtient en posant UNE mesure physique — la justification")
    print("du livre imprime, relevee a la regle sur l'exemplaire — puis")
    print("en divisant. Tant que cette mesure manque, le tableau ci-")
    print("dessous donne l'echelle qui decoulerait de quelques largeurs")
    print("de justification usuelles pour un in-16 de cette epoque.")
    print()
    print("  justification    px/mm    corps deduit (pas = 1,20 x corps)")
    for mm in (68, 70, 72, 74, 76, 78, 80):
        pxmm = lm / mm
        corps_pt = (pm / pxmm) / 25.4 * 72 / 1.20
        print(f"      {mm} mm       {pxmm:6.2f}      {corps_pt:5.2f} pt")


if __name__ == "__main__":
    main()
