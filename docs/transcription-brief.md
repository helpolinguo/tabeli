# Transcription brief — the diplomatic transcription

To be read through before a single leaf is transcribed.

## 0. What we are doing

We transcribe, **line by line**, a booklet printed in 1926, from its
facsimile. The one rule:

> **ONE LINE OF THE FACSIMILE = ONE LINE OF THE PDF.**

The text is not reset, not modernised, not corrected. The printer's
typos are kept. We do not "understand" the text in order to rewrite it:
we **record** it.

## 1. Preparing the images

    python3 tools/reading.py io 13 18 --half
    python3 tools/reading.py fr 14 18 --half

produces `tools/.reading/io-013a.png` (top of the page) and
`io-013b.png` (foot of the page), with two lines of overlap between the
two. Read them with the `Read` tool, one image at a time, and transcribe
as you go. **Never transcribe from memory or by inference: every line
must have been seen.**

If an image is illegible, regenerate it larger:

    python3 -c "import sys; sys.path.insert(0,'tools'); \
      from reading import prepared; print(prepared('io', 13, True, 2200))"

## 2. The two break marks

At the end of every line of the facsimile, except the last of a
paragraph:

| mark | when | renders |
|---|---|---|
| `\nl` | the line ends on a whole word | nothing visible |
| `\cc` | the line ends on a **broken** word | the hyphen |

The hyphen of a break **is not written**: `\cc` sets it. Write
`ler\cc nanti` and not `ler-\cc nanti`.

We **never** use `\\`.

The last line of a paragraph carries no mark — unless the paragraph runs
on to the next page: it then carries `\parplein` on a line of its own,
and the resumption begins with `\VUcontinue`.

## 3. The enrichments

| facsimile | source |
|---|---|
| bold (narrow semibold) | `\VUgras{...}` |
| italic | `\textit{...}` |
| a superscript reference in brackets, e.g. `⁽¹⁸⁾` | `\textsuperscript{(18)}` |
| small capitals of a subheading | see § 4 |

**A word broken in the middle of a bold passage carries two `\VUgras`**,
one per line:

    ar\cc
    moro

becomes

    \VUgras{ar}\cc
    \VUgras{moro}

Respect the extent of the bold **exactly**: in « la **nigra tabelo**
(1) » the reference is not bold; in « **liceo.** » the full stop is.
Look, do not suppose.

Mind the space **before** the reference: the Ido booklet most often puts
one (`\VUgras{tabli} \textsuperscript{(18)}`), the French booklet most
often does not (`\VUgras{tables}\textsuperscript{(18)}`). Follow the
facsimile page by page.

## 4. The ranks of title

    \VUpk{10.2pt}{40}{Deskripto generala.}      subheading in small
                                                capitals, centred
    \VUtitre{15.0pt}{60}{TABELO N\textsuperscript{o} 2}   table title
    \VUcentre{13.2pt}{90}{DUESMA SERIO}         a line of apparatus
    \VUfilet{20mm}                              centred rule
    \VUornamento{9pt}                           fleuron
    \VUsaut{3.0mm}                              vertical white

The sizes and letterspacing passed as arguments are **provisional**:
take those of table 1 (`text/io/10-tabelo-01.tex`) rather than inventing
any. They will be surveyed later by `tools/measures.py`.

## 5. The structure of a page

    \begin{VUpage}[13]{11}
    ...
    \end{VUpage}

`[13]` = the **leaf** number in the scan; `{11}` = the **printed
folio**, left empty `{}` if the page carries none (the opening of a
table).

Remember: **printed folio = leaf number − 2**, in both booklets.

Between two paragraphs, write `\VUblancAlinea` before the first word.

### Footnotes

    \VUnotes{143.2mm}{%
    (*) Por la \textit{baptonomi} on konsilas anke transskribar li\nl
    segun la formo Latina.%
    }

They are declared **at the head of the page**, just after
`\begin{VUpage}`, whatever their real place: they are laid at an
absolute ordinate, at zero height. The ordinate is provisional — put
`143.2mm` if the note is at the foot of a full page.

## 6. The pairing keys `%%K`

**This is the most important part, and the easiest to get wrong.**

Before each block of text, one line:

    %%K t02-09-3 p

* `t02` — the table's number, on two digits.
* `09` — **the paragraph number printed by the author** (`9. —`), on
  two digits. Blocks that carry no number (the paragraphs that follow,
  with no figure) keep the number of the numbered paragraph before them.
* `3` — the block's rank **inside** that numbered paragraph: `1` for the
  one that carries the figure, `2` for the next, and so on.
* `p` — the type: `p` a running paragraph, `sub` a subheading, `apar` a
  page of apparatus (the opening of a table), `noto` a note.

Subheadings and pages of apparatus are numbered apart: `t02-tit-1`,
`t02-tit-2`, … in order, and `t02-apar-1`.

### The scenes: leave them alone

Several tables are cut into scenes (« Unesma ceno », « Duesma ceno »),
and **the author resets the paragraph numbering to 1 at each scene**.
The same key `t04-01-1` then names two different paragraphs.

**That is not your problem.** Note what you see: the print carries
« 1. — », you write `01`. A deterministic pass (`tools/scenes.py`),
applied afterwards and identically to both languages, inserts the scene
index (`t04-c2-01-1`) by detecting the fall in the number. If you do it
yourself, your scene numbering and the other language's risk diverging,
and the pairing will be wrong.

A paragraph cut by a change of page carries **the same key twice**, the
second followed by `suite`:

    %%K t01-13-1 p suite

**Why this matters.** These keys pair the Ido column and the French
column on the reading page. The two editions have neither the same
pagination, nor the same number of lines, nor the same division into
sections — but they number the same paragraphs, and that is the only
anchor they share. A wrong key makes the side-by-side lie.

If a block exists in one edition only (the Ido adds subheadings the
French does not know), it keeps its key and simply has no counterpart.
**Never force a correspondence that does not exist, never merge two
paragraphs so that they "fall opposite".**

## 7. Spelling and punctuation

* Write the accents in direct UTF-8 (`é`, `à`, `ô`), not as macros.
* Apostrophe: type it straight (`'`); the conversion curves it.
* The print's em dash: `---`. En dash: `--`.
* A space before `;` `:` `?` `!`: type it normally, one space.
* The facsimile's French quotation marks `«~...~»`: simply write
  `« ... »`.
* **Do not correct the text.** If the print carries `et` where Ido
  expects `e`, write `et`. If a full stop is missing, do not add it.

## 8. Check before handing in

1. Count the lines: the number of `\nl` + `\cc` + paragraph endings on a
   page must equal the number of printed lines on that page.
2. Compile:

       pdflatex -interaction=nonstopmode -jobname=trial main-io.tex

   **No « Overfull \hbox » may appear.** If there is one, the line
   recorded is too long: it is almost always a break left out.
3. Reread the `%%K` keys: a run of paragraph numbers with no gap.

## 9. Where to write

    text/io/<NN>-tabelo-<NN>.tex        e.g. text/io/11-tabelo-02.tex
    text/fr/<NN>-tableau-<NN>.tex       e.g. text/fr/11-tableau-02.tex

The numeric prefix gives the order of inclusion: `10` for table 1, `11`
for table 2, … `25` for table 16.

The model to imitate in detail: `text/io/10-tabelo-01.tex` and
`text/fr/10-tableau-01.tex`.
