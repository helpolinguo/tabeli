#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grasdiff.py — montre, alinéa par alinéa, où le gras des deux colonnes
ne se répond pas.

    python3 tools/grasdiff.py t16
    python3 tools/grasdiff.py t05 --tout

Les deux livrets mettent en gras la même chose : le mot de vocabulaire
que le tableau mural illustre. Quand les comptes diffèrent, l'une des
deux colonnes a tort — et l'outil ne sait pas laquelle. Il pose les
deux textes l'un sous l'autre, avec leurs passages gras entre
crochets, pour qu'on aille voir le fac-similé au bon endroit.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import html as h  # noqa: E402


def crochets(t):
    t = re.sub(r"<b>(.*?)</b>", r"[\1]", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    tableau = sys.argv[1] if len(sys.argv) > 1 else "t01"
    tout = "--tout" in sys.argv
    rangi = h.paro()
    n = 0
    for r in rangi:
        if r["tipo"] != "p" or not r["cle"].startswith(tableau):
            continue
        o = r["tra"].get("fr")
        if not o or not r["io"] or not o["t"]:
            continue
        a, b = r["io"].count("<b>"), o["t"].count("<b>")
        if a == b and not tout:
            continue
        n += 1
        print(f"\n--- {r['cle']}   ido {a} gras / français {b} gras "
              f"  (feuillets io {r['feuillet']}, fr {o['fe']})")
        print(f"  IDO : {crochets(r['io'])}")
        print(f"  FRA : {crochets(o['t'])}")
    print(f"\n{n} alinéas à revoir dans {tableau}.")


if __name__ == "__main__":
    main()
