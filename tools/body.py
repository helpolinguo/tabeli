#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.py — measures the type size PAGE BY PAGE and writes body-<language>.tex.

    python3 tools/body.py io
    python3 tools/body.py fr

THE PROBLEM. `tools/chaso.py` finds the size that best fills the lines of
the WHOLE volume. That is an average: on the pages where the compositor of
1926 set a little tighter than his average, that size is too small, and TeX
spreads the words to fill -- hence gaping word spaces, visible to the eye
and tiring to read.

The cause is real and is not a fault of the survey. The compositor did not
hold a constant width from one gathering to the next -- worn sorts,
substitute founts -- and today's font does not have his in any case. A
single size therefore cannot fill every page.

THE MEASUREMENT. For each page, the right size is **the largest that makes
none of its lines overflow**. That is measurable: we sweep, we compile, and
TeX itself says, source line by source line, what overflows and by how
much.

One practical difficulty: TeX's log gives "in paragraph at lines A--B"
without saying which file. We therefore compile **one transcription file at
a time**, in a minimal wrapper: the line numbers there are unambiguous, and
we attach them to their page by the `\\begin{VUpage}[n]` of the file.

We ask TeX to say everything -- `\\hbadness=0`, `\\hfuzz=0pt` -- otherwise
it keeps quiet about overflows under 0.1 pt and about slightly loose lines.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")
BOITE = re.compile(
    r"(Overfull|Underfull) \\hbox \(([\d.]+)pt too wide|"
    r"(Underfull) \\hbox \(badness (\d+)\)")
LIGNES = re.compile(r"in paragraph at lines (\d+)--(\d+)")

# The sweep: around the global size, upwards above all, since that is the
# average and half the pages want more.
ECART = [-0.30, -0.15, 0.0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90,
         1.05, 1.20, 1.35, 1.50]


def corps_global(langue):
    kal = (RACINE / f"kalibro-{langue}.tex").read_text(encoding="utf-8")
    return float(re.search(r"\\VUcorps\}\{([\d.]+)pt", kal).group(1))


def pages_du_fichier(chemin):
    """[(leaf, first line, last line)] of the file."""
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    bornes = []
    for i, l in enumerate(lignes, 1):
        m = PAGE.search(l)
        if m and m.group(1):
            bornes.append((m.group(1), i))
    out = []
    for k, (f, deb) in enumerate(bornes):
        fin = bornes[k + 1][1] - 1 if k + 1 < len(bornes) else len(lignes)
        out.append((f, deb, fin))
    return out


def essai(langue, fichier, corps, tmp):
    """{leaf: (maximum overflow in pt, number of loose lines)}."""
    env = tmp / "essai.tex"
    env.write_text(
        f"\\documentclass{{article}}\n"
        f"\\input{{{RACINE}/kalibro-{langue}}}\n"
        f"\\renewcommand{{\\VUcorps}}{{{corps:.2f}pt}}\n"
        f"\\input{{{RACINE}/preambule}}\n"
        f"\\hbadness=0 \\hfuzz=0pt\n"
        f"\\begin{{document}}\n"
        f"\\input{{{fichier}}}\n"
        f"\\end{{document}}\n", encoding="utf-8")
    subprocess.run(["pdflatex", "-interaction=nonstopmode",
                    "-halt-on-error", "essai.tex"],
                   cwd=tmp, capture_output=True)
    log = (tmp / "essai.log")
    if not log.exists():
        return {}
    texte = log.read_text(encoding="utf-8", errors="ignore")

    pages = pages_du_fichier(Path(fichier))
    res = {f: [0.0, 0] for f, _, _ in pages}

    def page_de(ligne):
        for f, deb, fin in pages:
            if deb <= ligne <= fin:
                return f
        return None

    for bloc in texte.split("\n\n"):
        mb = BOITE.search(bloc)
        ml = LIGNES.search(bloc)
        if not mb or not ml:
            continue
        f = page_de(int(ml.group(1)))
        if f is None:
            continue
        if mb.group(1) == "Overfull":
            res[f][0] = max(res[f][0], float(mb.group(2)))
        else:
            res[f][1] += 1
    return res


def main():
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    base = corps_global(langue)
    sous = "io" if langue == "io" else "fr"
    fichiers = sorted((RACINE / "text" / sous).glob("*.tex"))

    # {leaf: {size: (overflow, loose)}}
    releve = {}
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for f in fichiers:
            for e in ECART:
                c = round(base + e, 2)
                for feuillet, (deb, lach) in essai(langue, f, c, tmp).items():
                    releve.setdefault(feuillet, {})[c] = (deb, lach)
            print(f"  {f.name}", flush=True)

    lignes = []
    choisis = {}
    for feuillet, par_corps in releve.items():
        # The largest size WITH NO OVERFLOW. A page all of whose values
        # overflow (which happens when a single line of the survey is a little
        # too long) keeps the smallest trial: better a loose page than a line
        # that leaves the measure.
        sans = [c for c, (deb, _) in par_corps.items() if deb == 0.0]
        c = max(sans) if sans else min(par_corps)
        choisis[feuillet] = c
        if abs(c - base) > 0.001:
            lignes.append(f"\\VUkorpoPage{{{feuillet}}}{{{c:.2f}pt}}")

    entete = (
        f"% korpi-{langue}.tex — corps propre a chaque page.\n"
        f"% Fichier PRODUIT par tools/korpo.py : ne pas le modifier a la\n"
        f"% main. Pour chaque page, le plus grand corps qui ne fasse\n"
        f"% deborder aucune de ses lignes. Corps global : {base:.2f}pt.\n"
        f"% {len(lignes)} pages sur {len(choisis)} recoivent une valeur\n"
        f"% propre ; les autres gardent le corps global.\n\n")
    (RACINE / f"korpi-{langue}.tex").write_text(
        entete + "\n".join(lignes) + "\n", encoding="utf-8")

    import statistics
    v = sorted(choisis.values())
    print(f"\nkorpi-{langue}.tex : {len(lignes)}/{len(choisis)} pages "
          f"ont un corps propre")
    print(f"  corps global {base:.2f}pt ; par page : "
          f"min {v[0]:.2f}  mediane {statistics.median(v):.2f}  "
          f"max {v[-1]:.2f}")


if __name__ == "__main__":
    main()
