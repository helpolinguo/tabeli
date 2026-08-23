# Notes de travail

Ce fichier dit comment on travaille sur ce dépôt. Le *quoi* est dans
`LISEZ-MOI.md`, qui reste la documentation du projet ; on ne le double pas
ici, on y renvoie.

## Branches et pull requests

**Le projet vit sur `main`**, qui est la branche par défaut.

On n'écrit jamais directement sur `main`. On travaille sur une branche, et
on la fait entrer par une **pull request dont la base est `main`**, ouverte
en brouillon. Une branche repart toujours du `main` courant :

    git fetch origin main
    git checkout -B <branche> origin/main

Une pull request fusionnée est finie : elle ne peut pas porter de suite. Le
travail d'après repart de `main`, et c'est une nouvelle pull request.

## Ce qu'on vérifie avant de pousser

La chaîne complète, dans cet ordre. Chaque outil dit ce qu'il attend ; un
chiffre qui bouge sans raison est un défaut, pas un détail.

    python3 outils/renvoji.py    # 683 blocs, 0 divergence, 3 écarts déclarés
    python3 outils/kolonoj.py    # 16 fichiers, 0 signalement, par colonne
    python3 outils/objekti.py    # 1708/1694 = 100 %
    python3 outils/html.py       # 683 bloki, 524 alinei
    python3 outils/controles.py  # 1 signalement (le cadre du scan « fra 6 »)
    python3 outils/notoj.py      # 0 et 0

Et le tout compile en permanence :

    make -f tab.mk               # tabeli.pdf, tableaux.pdf, index.html

## Trois règles qui ne se négocient pas

**LA SOURCE NE BOUGE PAS.** `texto/io/` et `texto/fr/` reproduisent le
fac-similé tel qu'il est, coquilles du compositeur comprises. Ce qu'il faut
corriger pour la page de lecture se déclare dans `gravuri/korekti.json` et
n'agit que là. Voir § 5 de `LISEZ-MOI.md`.

**UNE TRADUCTION N'EST PAS UNE TRANSCRIPTION.** Chaque `texto/<langue>/`
porte les mêmes clés `%%K`, le même appareil macro pour macro et les mêmes
`\textsuperscript{(n)}` dans le même ordre — mais pas de `\nl`, pas de
`\cc`, pas de `\begin{VUpage}` : ce sont des accidents de page du
fac-similé, pas du texte. Le gras porte sur le terme seul, la ponctuation
en dehors.

**UN FICHIER PRODUIT N'EST PAS UN ENDROIT OÙ L'ON ÉCRIT.** `index.html`,
`kalibro-*.tex` et `lingui/*.json` sont regénérés ; une modification qu'on y
fait à la main disparaît au premier `make`. Ce qui doit changer se change
dans `outils/gabarito.html`, dans `outils/*.py` ou dans `texto/`.

## Écriture

Messages de commit et commentaires de code **en français**, dans le style de
la maison : la trouvaille en tête et en capitales, des mesures plutôt que des
suppositions, les approches essayées puis abandonnées consignées, et une
affirmation antérieure devenue fausse corrigée **là où elle est écrite**.
