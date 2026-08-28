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

# 180 is the HEIGHT of the paper in millimetres, and it is the one
# physical constant of the whole calibration -- the HathiTrust record for
# the French booklet reads "90 p., 2 l. 18 cm.". This target passed 110
# for as long as the scale was taken from the WIDTH; the scale has been
# taken from the height since, and 110 would have rescaled both volumes.
calibrate: tools/calibrate.py tools/inventory-io.json tools/inventory-fr.json
	python3 tools/calibrate.py io 180
	python3 tools/calibrate.py fr 180

inventory:
	python3 tools/inventory.py io
	python3 tools/inventory.py fr

# The glossary is drawn from tabeli.json and teksti/, so it follows
# machine_readable.py and never precedes it.
glosaro: tools/glosaro.py tabeli.json teksti/*.json
	python3 tools/glosaro.py

checks: tabeli.pdf tableaux.pdf
	python3 tools/checks.py
	python3 tools/notes.py

.PHONY: all calibrate inventory checks glosaro
