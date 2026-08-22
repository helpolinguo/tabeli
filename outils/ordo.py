#!/usr/bin/env python3
# ===================================================================
#  ordo.py — l'ordre des renvois, bloc par bloc, tel que l'ido le
#  donne
#
#  LE TROISIEME OUTIL DE LA MEME FAMILLE, ET IL COMBLE UN TROU QU'ON
#  A PAYE CHER. parigi.py dit AVANT d'ecrire quelles PAIRES une
#  langue a tete finale sortira a l'envers ; renvoji.py dit APRES
#  COUP si l'ordre est bon. Entre les deux il manquait la chose la
#  plus simple : la SUITE COMPLETE des renvois d'un bloc, a suivre en
#  ecrivant.
#
#  POURQUOI ELLE MANQUAIT VRAIMENT. Le tableau 9 tamoul a coute neuf
#  ecarts au premier passage, et SEPT portaient sur des couples que
#  parigi.py ne contient pas : la scie et le bucheron, le cor et les
#  veneurs, la corneille et sa branche. Ce ne sont pas des rapports
#  modificateur-tete — parigi.py n'a pas a les voir —, ce sont des
#  ordres internes de phrase. Le tableau 10, ecrit avec la suite sous
#  les yeux, en a coute trois. Neuf contre trois, meme colonne, deux
#  tableaux de suite : c'est la mesure qui justifie ce fichier.
#
#  CE QU'IL FAIT. Il lit texto/io, retrouve le tableau demande, et
#  imprime pour chaque cle %%K la suite des renvois dans l'ordre ou
#  ils tombent — chiffres, lettres, « 94 bis », et les parentheses
#  nues que le fac-simile compose sans leur \textsuperscript. Les
#  blocs « suite » sont recolles au bloc qu'ils continuent, comme
#  html.py les recolle.
#
#  CE QU'IL NE FAIT PAS : aucun jugement. Il ne dit pas ce qu'il faut
#  retourner ni pourquoi. C'est une copie de l'ordre recu, et c'est
#  tout ce qu'on lui demande.
#
#  USAGE
#      python3 outils/ordo.py t10      # les blocs du tableau 10
#      python3 outils/ordo.py t03      # les deux scenes, c1 et c2
# ===================================================================

import glob
import re
import sys

#  LES DEUX FORMES DE RENVOI DU FAC-SIMILE. La premiere est la forme
#  normale ; la seconde est la parenthese nue, que l'imprimeur laisse
#  parfois sans exposant — « (58) », « 13) » — et que html.py rend
#  elle aussi a un renvoi. Les deux comptent pour l'ordre.
RENVOJO = re.compile(r"\\textsuperscript\{\(([^)]*)\)\}"
                     r"|(?<!\w)\((\d{1,3}(?: bis)?|[a-z]{1,2})\)")

CLE = re.compile(r"%%K (\S+) (\S+)(.*)")


def blocs(tabelo):
    """Les blocs de ce tableau, avec leur suite de renvois."""
    fonto = ""
    for chemin in sorted(glob.glob("texto/io/*.tex")):
        texto = open(chemin, encoding="utf-8").read()
        if "%%K " + tabelo + "-" in texto:
            fonto = texto
            break
    if not fonto:
        return []

    listo, kuranta = [], None
    for ligno in fonto.split("\n"):
        m = CLE.match(ligno)
        if m:
            kuranta = m.group(1)
            #  « p suite » ne rouvre pas un bloc : il continue le
            #  precedent, coupe par une fin de page.
            if not (listo and listo[-1][0] == kuranta
                    and "suite" in m.group(3)):
                listo.append([kuranta, []])
            continue
        if kuranta is None or ligno.startswith("%"):
            continue
        for a, b in RENVOJO.findall(ligno):
            valoro = (a or b).strip()
            #  L'asterisque des appels de note n'est pas un renvoi.
            if valoro and valoro != "*":
                listo[-1][1].append(valoro)
    return [(c, r) for c, r in listo if c.startswith(tabelo + "-")]


def main():
    if len(sys.argv) != 2:
        print("usage : python3 outils/ordo.py t10")
        return
    tabelo = sys.argv[1]
    if not tabelo.startswith("t"):
        tabelo = "t%02d" % int(tabelo)
    trovita = blocs(tabelo)
    if not trovita:
        print("  %s : aucun bloc dans texto/io" % tabelo)
        return
    for cle, renvoji in trovita:
        print("  %-22s %s" % (cle, " ".join(renvoji)))
    print("\n  %d blocs, %d renvois."
          % (len(trovita), sum(len(r) for _, r in trovita)))


if __name__ == "__main__":
    main()
