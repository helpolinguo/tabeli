#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scenes.py — adds the SCENE index to the matching keys.

    python3 tools/scenes.py                 # every file in text/
    python3 tools/scenes.py text/io/13-tabelo-04.tex

WHY. Several tables are divided into scenes -- "Unesma ceno", "Duesma
ceno"; "Première scène", "Deuxième scène" -- and **the author resets the
paragraph numbering to 1 at each scene**. In table 4, the paragraphs run
from 1 to 19 and then start again from 1 to 13.

The key `t04-01-1` therefore designates TWO different paragraphs. As it
stands, it makes the reading page lie in two ways: the dictionary indexing
the French column keeps only one of them -- the last -- and the Ido column
finds itself matched with the wrong text; and the first paragraph of scene
2 inherits the counterpart of the first paragraph of scene 1.

It is not for the transcription to deal with this. The surveyor notes what
he sees: the print carries "1. —", he writes `01`. It is here, in one
deterministic pass applied TO BOTH LANGUAGES IN THE SAME WAY, that the
scene enters the key:

    t04-01-1   ->   t04-c1-01-1      (before the reset)
    t04-01-1   ->   t04-c2-01-1      (after the reset)

The reset is detected without knowing anything of the text: the paragraph
number DECREASES. That is the only reliable signal -- the scene title is
not worded the same way in the two editions, and some tables have one
without resetting the numbering.

Tables of a single scene are not touched: their keys stay `t01-09-3`,
without an index. An index everywhere would have been more regular, but
would have broken table 1, already surveyed and already matched.

The tool is IDEMPOTENT: a key that already carries its index is left as it
is. It can therefore be re-run after every survey.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# t<NN>-<NN>-<R>, with no scene index already set.
KEY = re.compile(r"^(%%K\s+t(\d\d)-)(\d\d)(-\d+[a-z]?)(\s+\S+.*)$")


def process(path, write_=True):
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    # First pass: is there a reset? If not, we touch nothing.
    previous = None
    last_ = None
    resumption = False
    for l in lines:
        m = KEY.match(l.rstrip("\n"))
        if not m:
            continue
        key = m.group(1) + m.group(3) + m.group(4)
        if key == last_:      # a "continuation" block: same key, not a new paragraph
            continue
        last_ = key
        n = int(m.group(3))
        if previous is not None and n < previous:
            resumption = True
        previous = n
    if not resumption:
        return 0

    # Second pass: we set the index.
    scene = 1
    previous = None
    last_ = None
    out = []
    n_touching = 0
    for l in lines:
        m = KEY.match(l.rstrip("\n"))
        if not m:
            out.append(l)
            continue
        key = m.group(1) + m.group(3) + m.group(4)
        n = int(m.group(3))
        if key != last_:
            if previous is not None and n < previous:
                scene += 1
            previous = n
            last_ = key
        end_ = "\n" if l.endswith("\n") else ""
        out.append(f"{m.group(1)}c{scene}-{m.group(3)}{m.group(4)}"
                   f"{m.group(5)}{end_}")
        n_touching += 1
    if write_:
        path.write_text("".join(out), encoding="utf-8")
    return n_touching


def hand():
    targets = [Path(a) for a in sys.argv[1:]]
    if not targets:
        targets = sorted((ROOT / "text").glob("*/*.tex"))
    for c in targets:
        n = process(c if c.is_absolute() else ROOT / c)
        if n:
            print(f"{c} : {n} clés indicées par scène")


if __name__ == "__main__":
    hand()
