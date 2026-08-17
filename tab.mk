# Compilation des deux volumes : « make -f tab.mk ».
# Le PDF porte le nom sous lequel il est publie, et non celui de sa
# source : « -jobname » suffit. Le nom compte : la page de lecture et
# tous ses renvois de folio pointent tabeli.pdf et tableaux.pdf.
# Le fichier s'appelle tab.mk et non Makefile : le pont vers le disque
# de l'utilisateur refuse d'ecrire un fichier portant ce dernier nom.

all: tabeli.pdf tableaux.pdf index.html

tabeli.pdf: main-io.tex preambule.tex kalibro-io.tex texto/io/*.tex
	pdflatex -interaction=nonstopmode -jobname=tabeli main-io.tex

tableaux.pdf: main-fr.tex preambule.tex kalibro-fr.tex texto/fr/*.tex
	pdflatex -interaction=nonstopmode -jobname=tableaux main-fr.tex

index.html: outils/html.py texto/io/*.tex texto/fr/*.tex
	python3 outils/html.py

kalibro: outils/kalibro.py outils/inv-io.json outils/inv-fr.json
	python3 outils/kalibro.py io 110
	python3 outils/kalibro.py fr 110

inventaire:
	python3 outils/inventaire.py io
	python3 outils/inventaire.py fr

controles: tabeli.pdf tableaux.pdf
	python3 outils/controles.py

.PHONY: all kalibro inventaire controles
