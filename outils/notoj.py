#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notoj.py — les notes de bas de page tiennent-elles leur place ?

    python3 outils/notoj.py

DEUX FAUTES POSSIBLES, ET IL FAUT LES DEUX.

La premiere est la COLLISION : la note s'imprime par-dessus le texte.
Elle venait de ce que \\VUnotes posait sa note dans une boite de HAUTEUR
NULLE, calee sur le pied du bloc : la note tombait juste, et elle ne
poussait rien. Sur une page dont le texte descend jusqu'au pied, les deux
s'imprimaient donc l'un sur l'autre — sept pages du livret ido et une du
francais. La note se differe maintenant jusqu'a la fermeture de la page
et entre dans le flux apres le dernier alinea ; le chevauchement est
devenu impossible par construction.

La seconde est le DEBORDEMENT : la note passe sous le bord du feuillet.
Elle ne vient pas de la macro mais de la page : six feuillets portent,
au releve, plus de matiere que la feuille n'en tient — le texte y remplit
deja le bloc, et la note n'a plus que la marge du bas, qui ne suffit pas.
Le premier defaut la CACHAIT : tant que la note s'imprimait dans le
texte, elle ne sortait jamais du papier. La corriger l'a mise au jour.

Ce controle ne tranche pas ces six pages : il les nomme. Les trancher
demande le fac-simile du livret, que ce depot ne contient pas — on n'a
que les seize planches.


COMMENT ON SEPARE LA NOTE DU TEXTE : par le CORPS, non par la position.
Mesure sur les deux livrets : le corps de note vaut 0,79 fois le corps de
texte — 9,09 contre 10,93 en ido, 8,45 contre 10,70 en francais — tandis
que l'exposant d'un renvoi vaut 0,70. La fenetre [0,74 ; 0,85] les separe
donc proprement, et c'est la mesure qui la fixe.

Et la LISTE DES PAGES vient du releve, non du PDF : on ne cherche une
note que la ou \\VUnotes en pose une. Une heuristique de corps seule
prenait les exposants et les petites capitales pour des notes, et rendait
quatre-vingt-deux pages sur quatre-vingt-seize.
"""

import glob
import io as _io
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MM = 72.0 / 25.4
VOLUMES = (("io", "tabeli.pdf"), ("fr", "tableaux.pdf"))


def feuillets_a_note(lg):
    """Les feuillets ou le releve pose une note. Le numero de feuillet EST
    le numero de page du PDF : une page du fac-simile, une page du PDF."""
    out = []
    for p in sorted(glob.glob(str(RACINE / "texto" / lg / "*.tex"))):
        t = _io.open(p, encoding="utf-8").read()
        for m in re.finditer(r"\\begin\{VUpage\}\[(\d+)\][^\n]*\n(.*?)\\end\{VUpage\}",
                             t, re.S):
            corps = "\n".join(l for l in m.group(2).split("\n")
                              if not l.startswith("%"))
            if "\\VUnotes" in corps:
                out.append(int(m.group(1)))
    return sorted(set(out))


def lignes(pdf, page):
    x = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf), str(page)],
                       capture_output=True, text=True).stdout
    r = ET.fromstring(x)
    haut = float(r.find("page").get("height"))
    out = []
    for ln in r.iter("line"):
        f = ln.find("font")
        if f is None:
            continue
        t = float(f.get("size"))
        if t < 1.0:            # le filigrane de provenance
            continue
        out.append((t, [float(v) for v in ln.get("bbox").split()]))
    return haut, out


def controlar(lg, pdf):
    pdf = RACINE / pdf
    if not pdf.exists():
        print(f"  {pdf.name} : absent, rien a controler")
        return 0, 0
    heurte = deborde = 0
    for pg in feuillets_a_note(lg):
        haut, ls = lignes(pdf, pg)
        if len(ls) < 4:
            continue
        corps = statistics.median(t for t, _ in ls)
        note = [b for t, b in ls if 0.74 * corps <= t <= 0.85 * corps]
        texte = [b for t, b in ls if t > 0.88 * corps]
        if not note:
            continue
        for bn in note:
            for bc in texte:
                iy = min(bn[3], bc[3]) - max(bn[1], bc[1])
                ix = min(bn[2], bc[2]) - max(bn[0], bc[0])
                if iy > 1.0 and ix > 5.0:
                    heurte += 1
                    print(f"  NOTE SUR LE TEXTE  {pdf.name} f{pg}")
                    break
            else:
                continue
            break
        bas = max(b[3] for b in note)
        if bas > haut:
            deborde += 1
            print(f"  NOTE HORS DU FEUILLET  {pdf.name} f{pg} : "
                  f"{(bas - haut) / MM:.1f} mm sous le bord — cette page porte "
                  f"plus de matiere que la feuille n'en tient")
    return heurte, deborde


def main():
    h = d = 0
    for lg, pdf in VOLUMES:
        a, b = controlar(lg, pdf)
        h += a
        d += b
    print()
    print(f"  notes sur le texte : {h}   notes hors du feuillet : {d}")
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(main())
