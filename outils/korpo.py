#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
korpo.py — mesure le corps PAGE PAR PAGE et écrit korpi-<langue>.tex.

    python3 outils/korpo.py io
    python3 outils/korpo.py fr

LE PROBLÈME. `outils/chaso.py` trouve le corps qui remplit le mieux les
lignes du volume ENTIER. C'est une moyenne : sur les pages où le
compositeur de 1926 serrait un peu plus que sa moyenne, ce corps est
trop petit, et TeX écarte les mots pour combler — d'où des blancs
inter-mots béants, visibles à l'œil et pénibles à lire.

La cause est réelle et n'est pas un défaut de relevé. Le compositeur ne
tenait pas une chasse constante d'un cahier à l'autre — casses usées,
fontes de remplacement — et la fonte d'aujourd'hui n'a de toute façon
pas exactement la sienne. Un seul corps ne peut donc pas remplir toutes
les pages.

LA MESURE. Pour chaque page, le bon corps est **le plus grand qui ne
fasse déborder aucune de ses lignes**. C'est mesurable : on balaie, on
compile, et TeX dit lui-même, ligne de source par ligne de source, ce
qui déborde et de combien.

Une difficulté pratique : le journal de TeX donne « in paragraph at
lines A--B » sans dire de quel fichier. On compile donc **un fichier de
relevé à la fois**, dans une enveloppe minimale : les numéros de ligne
y sont sans ambiguïté, et on les rattache à leur page par les
`\\begin{VUpage}[n]` du fichier.

On demande à TeX de tout dire — `\\hbadness=0`, `\\hfuzz=0pt` — sinon il
tait les débordements inférieurs à 0,1 pt et les lignes un peu lâches.
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

# Le balayage : autour du corps global, vers le haut surtout, puisque
# c'est la moyenne et que la moitie des pages en veut davantage.
ECART = [-0.30, -0.15, 0.0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90,
         1.05, 1.20, 1.35, 1.50]


def corps_global(langue):
    kal = (RACINE / f"kalibro-{langue}.tex").read_text(encoding="utf-8")
    return float(re.search(r"\\VUcorps\}\{([\d.]+)pt", kal).group(1))


def pages_du_fichier(chemin):
    """[(feuillet, premiere ligne, derniere ligne)] du fichier."""
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
    """{feuillet: (debordement max en pt, nombre de lignes laches)}."""
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
    fichiers = sorted((RACINE / "texto" / sous).glob("*.tex"))

    # {feuillet: {corps: (debordement, laches)}}
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
        # Le plus grand corps SANS DEBORDEMENT. Une page dont toutes les
        # valeurs debordent (cela arrive quand une seule ligne du releve
        # est un peu trop longue) garde le plus petit essai : mieux vaut
        # une page lache qu'une ligne qui sort de la justification.
        sans = [c for c, (deb, _) in par_corps.items() if deb == 0.0]
        c = max(sans) if sans else min(par_corps)
        choisis[feuillet] = c
        if abs(c - base) > 0.001:
            lignes.append(f"\\VUkorpoPage{{{feuillet}}}{{{c:.2f}pt}}")

    entete = (
        f"% korpi-{langue}.tex — corps propre a chaque page.\n"
        f"% Fichier PRODUIT par outils/korpo.py : ne pas le modifier a la\n"
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
