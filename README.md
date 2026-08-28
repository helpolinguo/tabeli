# Delmas-Tabeli

A diplomatic transcription of the two 1926 booklets that explain the
**Delmas auxiliary wall charts** — _**Expliko-Libreto di la
Delmas-Tabeli helpanta**_ (J. Guignon, Ido-Kontoro, Thaon-les-Vosges)
and _**Livret explicatif des Tableaux Auxiliaires Delmas**_ (E. Rochelle,
G. Delmas, Bordeaux) — typeset in LaTeX and published as a reading page
that sets the two texts **side by side**, at
[**ido.help/tabeli**](https://ido.help/tabeli/).

The rule the whole project answers to: **one line of the facsimile is one
line of the PDF** — same pagination, same folios, same line breaks. The
1926 typos are kept.

The sixteen wall plates the booklets describe are here too, and each
numbered object in the text opens a **close-up of that object on the
plate**: fifteen hundred numbers, read off the engraving.

This is one of three books gathered at [ido.help](https://ido.help/); the
other two are [gramatiko](https://github.com/helpolinguo/gramatiko) and
[dicionario](https://github.com/helpolinguo/dicionario), and the front
door is
[helpolinguo.github.io](https://github.com/helpolinguo/helpolinguo.github.io).

## Layout

```
main-io.tex          the Ido volume: one \input per leaf
main-fr.tex          the French volume
preamble.tex         every macro, each justified by measurement
calibrate-*.tex      every MEASUREMENT, one file per facsimile   } generated
body-*.tex           the type size, page by page                 } generated
text/io/, text/fr/   the two transcriptions — the source of everything
text/<language>/     the fifty-odd translated columns
text/languages.json  the register of the columns: code, name, speakers
text/variants.json   what the other edition of a language writes instead
build.mk             make -f build.mk         -> tabeli.pdf, tableaux.pdf
                     make -f build.mk checks  -> the checks
index.html           the reading page       }  generated: see below
tabeli.md, .json     the book laid flat     }
lingui/*.json        one file per deferred language  }
teksti/*.json        the same, cleaned, for machines  }
glosaro/*.md, .json  the bold terms paired, Ido to each language }
plates/              the sixteen plates, and everything read off them
plates/review/       the check sheets: every number read, in its cut-out
originals/           the original scans, straightened and trimmed
ornaments/           the cut ornaments
tools/               the measuring, generating and checking tools
docs/journal.md      why every value is what it is
```

## Building

```sh
make -f build.mk                    # tabeli.pdf and tableaux.pdf
python3 tools/html.py               # index.html, from text/*/
python3 tools/machine_readable.py   # tabeli.md, tabeli.json, lingui/*.json
python3 tools/glosaro.py            # glosaro/*.md and *.json — 56 languages
make -f build.mk checks             # the checks
```

`index.html`, `tabeli.md`, `tabeli.json`, `lingui/*.json`,
`glosaro/*`, `calibrate-*.tex` and `body-*.tex` are **generated, never
edited by hand**: anything that must change is changed in `text/`, in `tools/` or
in `tools/template.html`. The build file is named `build.mk` rather than
`Makefile` for a reason recorded in the journal.

The LaTeX build needs `pdflatex` with XCharter, newtx and TikZ. The tools
need Python 3 with `numpy`, `Pillow` and `opencv-python`; the
scan-facing ones also want `pdftotext`, `pdfinfo` and `mutool`. The
180 MB scan is not in the repository — the transcription, the two
composed volumes and the plates are.

## The fifty-five languages, twice

`lingui/` and `teksti/` are not two versions of one thing.

**`lingui/<code>.json` is what the browser eats.** The page keeps the cells
of the deferred languages empty and pours that HTML straight into them —
`k.innerHTML = t` in `tools/template.html` — magnifier buttons and all. It is
right as it is, and **it must not be cleaned**: the buttons are the plate
references, and stripping them would take them off the reading page.

**`teksti/<code>.json` is what a program reads.** The same text through the
same `text_()` that has always made `tabeli.json`, in the same Markdown,
under the same keys. `{key: text}`, one file per language.

It exists because `lingui/` was the *only* form those languages had, so
anything joining the Ido–English pair had to strip the page's furniture
itself — 6,027 tags in `en-GB`, 1,742 of them buttons. Now the join is flat:

```
tabeli.json        t01-01-1  io  1. — Ica tabelo reprezentas **docochambro** en **liceo.** …
teksti/en-GB.json  t01-01-1      1. — This chart shows a **classroom** in a **secondary school**. …
teksti/ja.json     t01-01-1      1. — この図表が描いているのは、**中学校**の**教室**である。…
```

**MEASURED: 27,322,703 bytes of payload become 9,620,260 — 35 %** — and
nothing is lost but the markup. All 55 files carry exactly the 672 keys of
`tabeli.json`, and none carries an HTML tag.

`io` and `fr` are **not** repeated there: they are `tabeli.json`, which is the
file one joins against. The directory is emptied at every run, so a language
withdrawn from `lingui/` stops being served here too.

## The bold is a glossary

Nothing else on `ido.help` answers **what is the Ido for X**. The Dicionario
defines Ido in Ido and the Gramatiko is in Ido throughout; this booklet is
the one place where Ido stands beside another language — and it stood there
as prose, so a program wanting the English for `katedro` had to fetch two
files of 137 kB and align two sentences itself.

It no longer has to. **The two columns set the same thing in bold** — the
vocabulary word the wall table illustrates, which is why `tools/bold_diff.py`
exists to check that correspondence leaf by leaf. So the n-th bold run of a
segment answers the n-th bold run of that segment in any language, and the
pairs fall out **by position**. No alignment is guessed at and no gloss is
composed: every pair is two passages of a printed parallel text.

```
glosaro/en-GB.md    katedro — desk
                    desk — katedro
glosaro/en-GB.json  "katedro":[{"t":"desk","k":["t01-01-1"]}]
```

The `.md` gives both directions flat, and is the cheapest complete form —
**82 kB against 136 kB**. The `.json` adds the segment keys, so that any
pair can be carried back to the printing and checked.

**MEASURED: 2,320 bold runs in the Ido, and 1,897 pairs won in `en-GB`** —
2,129 in `pl`, which is the best of the 56, and 1,791 in `bho`, which is the
worst. What is lost is lost to three guards, each of which drops rather than
guesses:

| | |
|---|---|
| the counts do not answer | 317 runs in `en-GB` — five bold in Ido against four in the target says one is missing, and not which |
| a run holds a comma | it is a **list**, not a term: both sides are split, and paired only if both split into the same number |
| a run holds a sentence break | `indolenti. Albertus` is two things the transcription ran together |

The second guard is not a formality: it is what wins the language names of
`t01-04-1`, where the printing sets `(Germana, Angla, Hispana, Italiana,
Rusa` and `Franca)` as two runs across a parenthesis.

**The punctuation is inside the bold, and § *A translation is not a
transcription* says it should not be.** It is not, in the source: 201 of the
2,320 runs carry a mark, and `liceo.`, `(liceestro)`, `Ludovikus,` are the
ordinary case. Those marks are trimmed from the **edges of a term** here, in
the glossary alone. The source is not touched.

## The checks

Each tool says what it expects, and a figure that moves without a reason
is a defect, not a detail:

```sh
python3 tools/cross_refs.py   # 683 blocks, 0 divergence, 3 declared exceptions
python3 tools/columns.py      # 16 files, 0 reports, per column
python3 tools/objects.py      # 1708/1694 = 100 %
python3 tools/html.py         # 683 blocks, 524 paragraphs
python3 tools/checks.py       # 1 report (the frame of the « fra 6 » scan)
python3 tools/notes.py        # 0 and 0
```

`tools/checks.py` runs the checks against the facsimile: pagination and
overflows, the pairing of the keys of the two editions, the rules
governing `\nl` and `\cc`, the bold of the two columns, and whether the
two columns are speaking of the same thing.

`tools/columns.py` is the other half, and it checks what no other tool
looks at: the MATTER of a translation file — its macros, its breaks, and,
for the columns that exist because they are not their neighbour, its
language. Cantonese against Chinese, Egyptian Arabic against Standard
Arabic, Marathi against Hindi, Afrikaans against Dutch.

## A note on language

The source is in English — comments, identifiers, filenames and commits.
Four things deliberately stay as they are:

- **The interface is in Ido**: the reading page's text, its accessible
  names and its tooltips, and the URLs of its sections.
- **The `\VU…` macros keep their names.** They are the vocabulary in
  which the facsimile was recorded, and `text/io/` and `text/fr/` are the
  diplomatic transcription — the one thing in this repository that does
  not move.
- **The generated page's own class names, ids, anchors and `data-`
  attributes keep theirs.** An anchor is an address: `#t02-apar-1` is
  cited, bookmarked and linked to, and renaming it would break every link
  ever copied.
- **The plate filenames and the keys of `plates/*.json` keep theirs**:
  they are published in `tabeli.json` and in `/llms.txt`, where other
  programs read them.

Translating the source changed nothing a reader of the site can see. The
page was rebuilt and compared byte for byte at every step, and the
finished page was exercised in a browser — search, language, notes,
close-ups, full screen, table of contents.

## Licence

The code in this repository is under the **MIT Licence** — see
[`LICENSE`](LICENSE). Copyright © 2026 Gilles-Philippe Morin.

The **works transcribed here are in the public domain in Canada**, where
this project is maintained: both booklets were published in 1926, and
their authors died more than fifty years before Canada's 2022 term
extension, which did not restore expired copyrights. Copyright terms
differ from country to country; readers elsewhere should satisfy
themselves of the position under their own law. The transcription, the
typesetting, the tools and the reading page are this project's own work,
and are covered by the licence above.
