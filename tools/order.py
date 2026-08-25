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
#  CE QU'IL FAIT. Il lit text/io, retrouve le tableau demande, et
#  imprime pour chaque cle %%K la suite des renvois dans l'ordre ou
#  ils tombent — chiffres, lettres, « 94 bis », et les parentheses
#  nues que le fac-simile compose sans leur \textsuperscript. Les
#  blocs « suite » sont recolles au bloc qu'ils continuent, comme
#  html.py les recolle.
#
#  ET UNE COLONNE DE PLUS, AJOUTEE APRES DEUX FAUTES IDENTIQUES.
#  Cinq blocs du volume tiennent DEUX alineas sous une seule cle :
#  t01-09-2, t07-c1-07-1, t09-c1-05-1, t11-c1-12-1, t11-c2-03-1.
#  L'ido y remet un \VUblancAlinea au milieu du bloc, souvent parce
#  qu'une fin de page tombe la. En traduisant on voit deux alineas et
#  on invente une seconde cle — « t09-c1-05-2 », « t11-c1-12-2 » —,
#  renvoji.py repond « cle inconnue » et kolonoj.py signale un bloc
#  ampute. C'est arrive deux fois dans la meme colonne. ordo.py
#  imprime desormais « ¶2 » devant ces blocs-la : la cle tient deux
#  alineas, il faut les ecrire tous les deux SOUS ELLE, separes d'une
#  ligne vide, et n'ouvrir aucune cle nouvelle.
#
#  CE QU'IL NE FAIT PAS : aucun jugement. Il ne dit pas ce qu'il faut
#  retourner ni pourquoi. C'est une copie de l'ordre recu, et c'est
#  tout ce qu'on lui demande.
#
#  USAGE
#      python3 tools/ordo.py t10      # les blocs du tableau 10
#      python3 tools/ordo.py t03      # les deux scenes, c1 et c2
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
    for chemin in sorted(glob.glob("text/io/*.tex")):
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
                listo.append([kuranta, [], 0])
            continue
        if kuranta is None or ligno.startswith("%"):
            continue
        listo[-1][2] += ligno.count("\\VUblancAlinea")
        for a, b in RENVOJO.findall(ligno):
            valoro = (a or b).strip()
            #  L'asterisque des appels de note n'est pas un renvoi.
            if valoro and valoro != "*":
                listo[-1][1].append(valoro)
    return [(c, r, n) for c, r, n in listo
            if c.startswith(tabelo + "-")]


def main():
    if len(sys.argv) != 2:
        print("usage : python3 tools/ordo.py t10")
        return
    tabelo = sys.argv[1]
    if not tabelo.startswith("t"):
        tabelo = "t%02d" % int(tabelo)
    trovita = blocs(tabelo)
    if not trovita:
        print("  %s : aucun bloc dans text/io" % tabelo)
        return
    for cle, renvoji, alinei in trovita:
        marko = "¶%d " % alinei if alinei > 1 else "   "
        print("  %s%-22s %s" % (marko, cle, " ".join(renvoji)))
    duobli = sum(1 for _, _, a in trovita if a > 1)
    print("\n  %d blocs, %d renvois."
          % (len(trovita), sum(len(r) for _, r, _ in trovita)))
    if duobli:
        print("  %d bloc(s) marque(s) ¶ : une seule cle, plusieurs "
              "alineas — ne pas en ouvrir une seconde." % duobli)


if __name__ == "__main__":
    main()
