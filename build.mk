# Building the two volumes: `make -f build.mk`.
# Each PDF carries the name under which it is published, not that of its
# source: `-jobname` is enough. The name matters: the reading page and all
# its folio references point at tabeli.pdf and tableaux.pdf.
# The file is called build.mk and not Makefile: the bridge to the user's
# disk refuses to write a file bearing the latter name.

all: tabeli.pdf tableaux.pdf index.html

tabeli.pdf: main-io.tex preamble.tex calibrate-io.tex text/io/*.tex
	pdflatex -interaction=nonstopmode -jobname=tabeli main-io.tex

tableaux.pdf: main-fr.tex preamble.tex calibrate-fr.tex text/fr/*.tex
	pdflatex -interaction=nonstopmode -jobname=tableaux main-fr.tex

index.html: tools/html.py text/io/*.tex text/fr/*.tex
	python3 tools/html.py

calibrate: tools/calibrate.py tools/inventory-io.json tools/inventory-fr.json
	python3 tools/calibrate.py io 110
	python3 tools/calibrate.py fr 110

inventory:
	python3 tools/inventory.py io
	python3 tools/inventory.py fr

checks: tabeli.pdf tableaux.pdf
	python3 tools/checks.py
	python3 tools/notes.py

.PHONY: all calibrate inventory checks
