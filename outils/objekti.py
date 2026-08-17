#!/usr/bin/env python3
# ===================================================================
#  objekti.py — le nom de chaque objet numerote, dans les deux langues.
#
#  « Nous avons imprime en caracteres gras les substantifs qui se
#  trouvent dans le vocabulaire des Tableaux EN LES FAISANT SUIVRE DE
#  LEUR NUMERO » : le liminaire francais donne lui-meme la regle, et
#  c'est elle qu'on lit ici. Chaque « (N) » du texte est precede du
#  substantif en gras qu'il numerote ; on releve donc le couple.
#
#  A QUOI CELA SERT. D'abord a savoir CE QUE montre un gros plan : un
#  clic sur « (15) » du tableau 13 ouvre la caisse, et la page peut le
#  dire. Ensuite, et surtout, a verifier les lectures douteuses du
#  lecteur de numeros : quand la machine hesite, on regarde la decoupe
#  et l'on demande si l'objet nomme s'y trouve. Un « (65) » lu sur une
#  hachure ne montre pas de bureau de tabac ; le nom tranche la ou la
#  forme du chiffre ne suffit plus.
#
#  UN NUMERO EST APPELE PLUSIEURS FOIS. Le texte y revient — « la
#  chambre (2) », puis « cette chambre (2) » — et pas toujours avec le
#  meme mot. On garde toutes les formes rencontrees, la premiere en
#  tete : c'est celle du releve initial, la plus descriptive.
#
#  USAGE
#      python3 outils/objekti.py            # ecrit gravuri/objekti.json
#      python3 outils/objekti.py 13         # montre le tableau 13
# ===================================================================

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Le substantif en gras, puis son numero — avec ou sans exposant, avec
# ou sans blanc entre les deux, le fac-simile hesitant sur les trois.
GRAS = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'      # \VUgras{...}
    r'(?:\s|\\nl|\\cc|%|\n)*'                   # coupures de ligne
    r'(?:\\textsuperscript\{)?'
    r'\((\d+)\)')

# Ce qui reste de balisage dans le nom releve.
MACROS = re.compile(r'\\(?:textit|textsc|emph|VUgras|nl|cc|hbox|,)\b\{?')


def nettoyer(brut):
    t = MACROS.sub('', brut)
    t = t.replace('\\-', '').replace('~', ' ').replace('{', '').replace('}', '')
    t = re.sub(r'\s+', ' ', t).strip(' .,;:')
    # Un substantif coupe par un changement de ligne garde son trait
    # d'union du fac-simile ; il n'appartient pas au mot.
    return re.sub(r'-\s+', '', t)


# UN SUBSTANTIF COUPE PAR LA FIN DE LIGNE EST COMPOSE EN DEUX MORCEAUX,
# chacun dans son \VUgras — c'est la regle du releve, une ligne du
# fac-simile etant une ligne de la source. « \VUgras{jour}\cc /
# \VUgras{naux} » donnait donc « naux », et « \VUgras{livre}\nl /
# \VUgras{des voyageurs} » donnait « des voyageurs ». On recolle avant
# de lire : \cc a coupe un mot, \nl a coupe une locution.
RECOLLE = [
    (re.compile(r'\\VUgras\{([^{}]*)\}\\cc\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    (re.compile(r'\\VUgras\{([^{}]*)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1 \2}'),
]


def recoller(texte):
    for motif, remplacement in RECOLLE:
        avant = None
        while avant != texte:
            avant = texte
            texte = motif.sub(remplacement, texte)
    return texte


def relever(dossier, motif):
    """{numero de tableau: {numero d'objet: [noms]}} pour une langue."""
    out = {}
    for f in sorted((RACINE / "texto" / dossier).glob(motif)):
        m = re.search(r'-(?:tabelo|tableau)-(\d+)\.tex$', f.name)
        if not m:
            continue
        tab = int(m.group(1))
        par = out.setdefault(tab, {})
        for g in GRAS.finditer(recoller(f.read_text(encoding="utf-8"))):
            nom = nettoyer(g.group(1))
            if not nom:
                continue
            noms = par.setdefault(int(g.group(2)), [])
            if nom not in noms:
                noms.append(nom)
    return out


def construire():
    io = relever("io", "*-tabelo-*.tex")
    fr = relever("fr", "*-tableau-*.tex")
    tout = {}
    for tab in sorted(set(io) | set(fr)):
        par = {}
        for n in sorted(set(io.get(tab, {})) | set(fr.get(tab, {}))):
            par[str(n)] = {"io": io.get(tab, {}).get(n, []),
                           "fr": fr.get(tab, {}).get(n, [])}
        tout[f"t{tab:02d}"] = par
    return tout


def attendus(tab):
    f = list((RACINE / "texto" / "io").glob(f"*-tabelo-{tab:02d}.tex"))
    if not f:
        return set()
    return {int(x) for x in
            re.findall(r'\((\d+)\)', f[0].read_text(encoding="utf-8"))}


def main(args):
    tout = construire()
    if args:
        tab = f"t{int(args[0]):02d}"
        for n, v in sorted(tout[tab].items(), key=lambda kv: int(kv[0])):
            print(f"  {n:>4}  {' / '.join(v['io']) or '—':40s}  "
                  f"{' / '.join(v['fr']) or '—'}")
        return
    (RACINE / "gravuri" / "objekti.json").write_text(
        json.dumps(tout, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    for tab, par in sorted(tout.items()):
        att = attendus(int(tab[1:]))
        deux = sum(1 for v in par.values() if v["io"] and v["fr"])
        print(f"  {tab}  {len(par):3d}/{len(att):3d} objets nommes, "
              f"dont {deux:3d} dans les deux langues")
    n = sum(len(p) for p in tout.values())
    a = sum(len(attendus(int(t[1:]))) for t in tout)
    print(f"  TOTAL {n}/{a} = {100 * n // a} %")


if __name__ == "__main__":
    main(sys.argv[1:])
