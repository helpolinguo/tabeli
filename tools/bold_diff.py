#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bold_diff.py — shows, paragraph by paragraph, where the bold of the two
columns does not answer.

    python3 tools/bold_diff.py t16
    python3 tools/bold_diff.py t05 --tout

The two booklets set the same thing in bold: the vocabulary word the wall
table illustrates. When the counts differ, one of the two columns is wrong
-- and the tool does not know which. It lays the two texts one under the
other, with their bold passages in brackets, so that one can go and look at
the facsimile in the right place.
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
