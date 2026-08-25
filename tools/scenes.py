#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ceni.py — ajoute l'indice de SCÈNE aux clés d'appariement.

    python3 tools/ceni.py                 # tous les fichiers de text/
    python3 tools/ceni.py text/io/13-tabelo-04.tex

POURQUOI. Plusieurs tableaux sont découpés en scènes — « Unesma ceno »,
« Duesma ceno » ; « Première scène », « Deuxième scène » — et
**l'auteur remet à 1 la numérotation des alinéas à chaque scène**. Au
tableau 4, les alinéas vont de 1 à 19 puis reprennent de 1 à 13.

La clé `t04-01-1` désigne donc DEUX alinéas différents. Telle quelle,
elle fait mentir la page de lecture de deux façons : le dictionnaire
qui indexe la colonne française n'en garde qu'un — le dernier — et la
colonne ido se voit apparier le mauvais texte ; et le premier alinéa de
la scène 2 hérite du vis-à-vis du premier alinéa de la scène 1.

Ce n'est pas au relevé de gérer cela. Le releveur note ce qu'il voit :
l'imprimé porte « 1. — », il écrit `01`. C'est ici, en une passe
déterministe appliquée AUX DEUX LANGUES DE LA MÊME MANIÈRE, que la
scène entre dans la clé :

    t04-01-1   ->   t04-c1-01-1      (avant la reprise)
    t04-01-1   ->   t04-c2-01-1      (après la reprise)

La reprise se détecte sans rien connaître du texte : le numéro d'alinéa
DÉCROÎT. C'est le seul signal fiable — le titre de scène, lui, n'est
pas libellé pareil dans les deux éditions, et certains tableaux en ont
un sans remettre la numérotation à zéro.

Les tableaux d'une seule scène ne sont pas touchés : leurs clés restent
`t01-09-3`, sans indice. Un indice partout aurait été plus régulier,
mais aurait cassé le tableau 1, déjà relevé et déjà apparié.

L'outil est IDEMPOTENT : une clé qui porte déjà son indice est laissée
telle quelle. On peut donc le relancer après chaque relevé.
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# t<NN>-<NN>-<R>, sans indice de scene deja pose.
CLE = re.compile(r"^(%%K\s+t(\d\d)-)(\d\d)(-\d+[a-z]?)(\s+\S+.*)$")


def traiter(chemin, ecrire=True):
    lignes = chemin.read_text(encoding="utf-8").splitlines(keepends=True)

    # Premiere passe : y a-t-il une reprise ? Si non, on ne touche a rien.
    precedent = None
    derniere = None
    reprise = False
    for l in lignes:
        m = CLE.match(l.rstrip("\n"))
        if not m:
            continue
        cle = m.group(1) + m.group(3) + m.group(4)
        if cle == derniere:      # bloc « suite » : meme clé, pas un alinea neuf
            continue
        derniere = cle
        n = int(m.group(3))
        if precedent is not None and n < precedent:
            reprise = True
        precedent = n
    if not reprise:
        return 0

    # Seconde passe : on pose l'indice.
    scene = 1
    precedent = None
    derniere = None
    out = []
    n_touches = 0
    for l in lignes:
        m = CLE.match(l.rstrip("\n"))
        if not m:
            out.append(l)
            continue
        cle = m.group(1) + m.group(3) + m.group(4)
        n = int(m.group(3))
        if cle != derniere:
            if precedent is not None and n < precedent:
                scene += 1
            precedent = n
            derniere = cle
        fin = "\n" if l.endswith("\n") else ""
        out.append(f"{m.group(1)}c{scene}-{m.group(3)}{m.group(4)}"
                   f"{m.group(5)}{fin}")
        n_touches += 1
    if ecrire:
        chemin.write_text("".join(out), encoding="utf-8")
    return n_touches


def main():
    cibles = [Path(a) for a in sys.argv[1:]]
    if not cibles:
        cibles = sorted((RACINE / "text").glob("*/*.tex"))
    for c in cibles:
        n = traiter(c if c.is_absolute() else RACINE / c)
        if n:
            print(f"{c} : {n} clés indicées par scène")


if __name__ == "__main__":
    main()
