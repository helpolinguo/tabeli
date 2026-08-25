# Working notes

This file says how we work on this repository. The *what* is in
`README.md`, which is the project's documentation; we do not repeat it
here, we point at it.

## Branches and pull requests

**The project lives on `main`**, which is the default branch.

We never write to `main` directly. We work on a branch, and bring it in
through a **pull request whose base is `main`**, opened as a draft. A
branch always starts again from the current `main`:

    git fetch origin main
    git checkout -B <branch> origin/main

**A branch is named after its subject**, in English, in lower case, the
words joined by hyphens: `claude/branches-by-subject`,
`claude/columns-pl-af`, `claude/footnote`. No session identifier, no
random suffix — a name like that says nothing six months later, and it
lies the moment the branch serves something other than what it was
opened for. The `claude/` prefix stays: it says who held the pen.

A merged pull request is finished: it cannot carry a sequel. The next
piece of work starts again from `main`, and it is a new pull request.

## What we check before pushing

The whole chain, in this order. Each tool says what it expects; a figure
that moves without a reason is a defect, not a detail.

    python3 tools/cross_refs.py  # 683 blocks, 0 divergence, 3 declared exceptions
    python3 tools/columns.py     # 16 files, 0 reports, per column
    python3 tools/objects.py     # 1708/1694 = 100 %
    python3 tools/html.py        # 683 bloki, 524 alinei
    python3 tools/checks.py      # 1 report (the frame of the « fra 6 » scan)
    python3 tools/notes.py       # 0 and 0

And the whole thing compiles, always:

    make -f build.mk             # tabeli.pdf, tableaux.pdf, index.html

## Three rules that are not negotiable

**THE SOURCE DOES NOT MOVE.** `text/io/` and `text/fr/` reproduce the
facsimile as it is, the compositor's typos included. What has to be
corrected for the reading page is declared in `plates/corrections.json`
and acts there alone. See § 5 of `README.md`.

**A TRANSLATION IS NOT A TRANSCRIPTION.** Each `text/<language>/` carries
the same `%%K` keys, the same apparatus macro for macro and the same
`\textsuperscript{(n)}` in the same order — but no `\nl`, no `\cc`, no
`\begin{VUpage}`: those are accidents of the facsimile's page, not of the
text. The bold falls on the term alone, the punctuation outside it.

**A PRODUCED FILE IS NOT A PLACE WHERE ONE WRITES.** `index.html`,
`tabeli.md`, `tabeli.json`, `lingui/*.json`, `calibrate-*.tex` and
`body-*.tex` are regenerated; an edit made in them by hand disappears at
the first `make`. What must change is changed in `tools/template.html`,
in `tools/*.py` or in `text/`.

This one has been paid for four times, and the fourth was a measurement
rather than a piece of markup: `calibrate.py` did not write `\VUlangue`,
which `preamble.tex` reads, and computed the type size from a ratio the
journal refutes. `tools/html.py` therefore reports, at every build, the
lines about to disappear from `index.html` that are not in the template.
Read what it says.

## Writing

Commit messages and code comments **in English**, in the house style: the
finding at the head and in capitals, measurements rather than
suppositions, the approaches tried and then abandoned recorded, and an
earlier assertion that has become false corrected **where it is
written**.

The interface stays in Ido, and the `\VU…` macro names stay as they are:
they are the vocabulary in which the facsimile was recorded. See the note
on language at the end of `README.md`.
