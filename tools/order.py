#!/usr/bin/env python3
# ===================================================================
#  order.py — the order of the references, block by block, as Ido gives
#  it
#
#  THE THIRD TOOL OF THE SAME FAMILY, AND IT FILLS A GAP WE PAID DEARLY
#  FOR. pair_up.py says BEFORE writing which PAIRS a head-final language
#  will bring out reversed; cross_refs.py says AFTER THE FACT whether the
#  order is right. Between the two the simplest thing was missing: the
#  COMPLETE RUN of a block's references, to follow while writing.
#
#  WHY IT REALLY WAS MISSING. Table 9 in Tamil cost nine discrepancies on
#  the first pass, and SEVEN of them bore on couples pair_up.py does not
#  contain: the saw and the woodcutter, the horn and the huntsmen, the
#  crow and its branch. These are not modifier-head relations -- pair_up.py
#  has no business seeing them -- they are sentence-internal orders. Table
#  10, written with the run under the eye, cost three. Nine against three,
#  the same column, two tables running: that is the measurement that
#  justifies this file.
#
#  WHAT IT DOES. It reads text/io, finds the table asked for, and prints
#  for each %%K key the run of references in the order in which they fall
#  -- figures, letters, "94 bis", and the bare parentheses the facsimile
#  sets without their \textsuperscript. "Continuation" blocks are rejoined
#  to the block they continue, as html.py rejoins them.
#
#  AND ONE COLUMN MORE, ADDED AFTER TWO IDENTICAL MISTAKES. Five blocks of
#  the volume hold TWO paragraphs under a single key: t01-09-2, t07-c1-07-1,
#  t09-c1-05-1, t11-c1-12-1, t11-c2-03-1. Ido puts a \VUblancAlinea in the
#  middle of the block there, often because a page break falls at that
#  point. In translating one sees two paragraphs and invents a second key
#  -- "t09-c1-05-2", "t11-c1-12-2" -- cross_refs.py answers "unknown key"
#  and columns.py reports a truncated block. This happened twice in the
#  same column. order.py now prints "¶2" before those blocks: the key holds
#  two paragraphs, both must be written UNDER IT, separated by a blank
#  line, and no new key opened.
#
#  WHAT IT DOES NOT DO: any judging. It does not say what to reverse or
#  why. It is a copy of the order received, and that is all that is asked
#  of it.
#
#  USAGE
#      python3 tools/order.py t10      # the blocks of table 10
#      python3 tools/order.py t03      # both scenes, c1 and c2
# ===================================================================

import glob
import re
import sys

#  THE FACSIMILE'S TWO FORMS OF REFERENCE. The first is the normal form;
#  the second is the bare parenthesis, which the printer sometimes leaves
#  without a superscript -- "(58)", "13)" -- and which html.py also renders
#  as a reference. Both count for the order.
XREF_ = re.compile(r"\\textsuperscript\{\(([^)]*)\)\}"
                     r"|(?<!\w)\((\d{1,3}(?: bis)?|[a-z]{1,2})\)")

KEY = re.compile(r"%%K (\S+) (\S+)(.*)")


def blocks(tabelo):
    """The blocks of this table, with their run of references."""
    source_ = ""
    for path in sorted(glob.glob("text/io/*.tex")):
        text_ = open(path, encoding="utf-8").read()
        if "%%K " + tabelo + "-" in text_:
            source_ = text_
            break
    if not source_:
        return []

    list_, current_ = [], None
    for ligno in source_.split("\n"):
        m = KEY.match(ligno)
        if m:
            current_ = m.group(1)
            #  "p suite" does not open a block: it continues the previous
            #  one, cut by a page break.
            if not (list_ and list_[-1][0] == current_
                    and "suite" in m.group(3)):
                list_.append([current_, [], 0])
            continue
        if current_ is None or ligno.startswith("%"):
            continue
        list_[-1][2] += ligno.count("\\VUblancAlinea")
        for a, b in XREF_.findall(ligno):
            value = (a or b).strip()
            #  The asterisk of note calls is not a reference.
            if value and value != "*":
                list_[-1][1].append(value)
    return [(c, r, n) for c, r, n in list_
            if c.startswith(tabelo + "-")]


def hand():
    if len(sys.argv) != 2:
        print("usage : python3 tools/ordo.py t10")
        return
    tabelo = sys.argv[1]
    if not tabelo.startswith("t"):
        tabelo = "t%02d" % int(tabelo)
    trovita = blocks(tabelo)
    if not trovita:
        print("  %s : no block in text/io" % tabelo)
        return
    for key, xrefs_, paras in trovita:
        mark_ = "¶%d " % paras if paras > 1 else "   "
        print("  %s%-22s %s" % (mark_, key, " ".join(xrefs_)))
    doubles = sum(1 for _, _, a in trovita if a > 1)
    print("\n  %d blocks, %d cross-references."
          % (len(trovita), sum(len(r) for _, r, _ in trovita)))
    if doubles:
        print("  %d block(s) marked ¶ : one key, several "
              "paragraphs — do not open a second one." % doubles)


if __name__ == "__main__":
    hand()
