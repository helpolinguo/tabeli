#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
checks.py — verifies what neither the compiler nor the eye sees.

    python3 tools/checks.py

A survey can compile perfectly and be wrong. These checks look for the
faults that do not announce themselves.

  1. PAGINATION      printed folio = leaf − 2, on every page.
  2. LEAVES          no leaf of the facsimile forgotten, none surveyed
                     twice, within the interval covered.
  3. MATCHING        does each %%K key of the Ido have a French
                     counterpart, and the reverse? This is THE check of
                     the project: an orphaned key is either a real
                     divergence between the two editions or a fault of
                     survey, and each must be looked at to decide.
  4. UNIQUENESS      no key appears twice in the same language, save the
                     second member of a paragraph cut by a change of
                     page, which carries "suite".
  5. BREAKS          each straddling end of paragraph (\\parplein or
                     \\ccplein) has its \\VUcontinue resumption.
  6. GEOMETRY        does the ink box occupy a plausible share of the
                     page? If not, the frame of the shot falls inside
                     the paper and the scale is wrong.
  7. BOLD            do the two columns set the same number of passages
                     in bold? Each is witness for the other.
  8. SYNCHRONY       do the two columns of a row carry the same
                     paragraph? An enormous difference of length says
                     that the key counter has drifted.

Check 3 cannot be automated as far as a verdict: it counts and it shows.
It is for the surveyor to say, for each orphan, whether it is legitimate.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = re.compile(r"^%%K\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$")
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")

# Running heads do not match: the Ido edition adds some the French does
# not know, and their numbering (tit-1, tit-2...) is proper to each
# edition. Counting them as orphans would drown the useful signal in
# noise.
WITHOUT_COUNTERPART = ("tit", "apar", "noto")


def read_file(folder):
    """{key: [(file, leaf, folio, continuation)]} and the list of pages."""
    keys = defaultdict(list)
    pages = []
    for f in sorted(folder.glob("*.tex")):
        leaf = folio = ""
        for i, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            mp = PAGE.search(l)
            if mp:
                leaf, folio = mp.group(1) or "", mp.group(2) or ""
                pages.append((f.name, i, leaf, folio))
                continue
            m = KEY.match(l.strip())
            if m:
                keys[m.group(1)].append(
                    (f.name, i, leaf, folio, m.group(3) == "suite"))
    return keys, pages


def blank_leaves(name_):
    """Leaves with no ink block, from tools/inventory-<language>.json."""
    import json
    lg = {"ido": "io", "fra": "fr"}[name_]
    f = ROOT / "tools" / f"inventory-{lg}.json"
    if not f.exists():
        return set()
    inv = json.loads(f.read_text(encoding="utf-8"))
    blank = set()
    for k, v in inv.items():
        if v.get("vide"):
            blank.add(int(k))
            continue
        b, px = v.get("bloc"), v.get("px")
        if b and px and (b[2] - b[0]) < 0.25 * px[0]:
            blank.add(int(k))
    return blank


def check_6(fault):
    """Does the ink box occupy a plausible share of the page?

    A printed book leaves margins. When the ink box covers nearly the whole
    height of the image, it is not that the book has no margins: it is that
    the FRAME OF THE SHOT falls inside the paper. The image height is then
    no longer the height of the paper, and the scale drawn from it is
    wrong.

    That is the case of the French facsimile: 96.5 % of the height, against
    83.7 % for the Ido. The internal ratios -- pitch over measure, x-height
    over measure -- stay good, and the composition is therefore right; only
    the overall scale is uncertain. A rule laid on the copy corrects it at
    a stroke.
    """
    import json
    import statistics
    for name_, lg in (("ido", "io"), ("fra", "fr")):
        f = ROOT / "tools" / f"inventory-{lg}.json"
        if not f.exists():
            continue
        inv = json.loads(f.read_text(encoding="utf-8"))
        p = [v for v in inv.values()
             if not v.get("vide") and v.get("lignes", 0) >= 35]
        if not p:
            continue
        hr = statistics.median(v["hauteur"] / v["px"][1] for v in p)
        lr = statistics.median(v["largeur"] / v["px"][0] for v in p)
        if hr > 0.90 or lr > 0.90:
            fault(f"{name_} 6 : le bloc d'encre couvre {100*lr:.1f} % de la "
                  f"largeur et {100*hr:.1f} % de la hauteur de l'image — "
                  f"le cadre du scan tombe dans le papier, l'echelle "
                  f"absolue tiree de l'image est fausse (les rapports "
                  f"internes, eux, restent bons)")


def check_7():
    """Does the bold of the two columns answer?

    The two booklets set THE SAME THINGS in bold: the vocabulary word the
    wall table illustrates. "ok \VUgras{tabli}" has for counterpart "huit
    \VUgras{tables}". The number of bold passages in a paragraph must
    therefore be the same on both sides -- not on principle, but because
    that is how the two editions are made.

    When it differs, it is nearly always a fault of survey: the surveyor
    set a word in bold that was not, or the reverse. The other column then
    serves as witness. This check does not decide -- it does not know which
    of the two is wrong -- it POINTS OUT the paragraphs to be looked at
    again in the facsimile, and it ranks them by decreasing discrepancy so
    that one begins with the most doubtful.
    """
    import subprocess
    import sys as _s
    _s.path.insert(0, str(ROOT / "tools"))
    import importlib
    h = importlib.import_module("html")
    rows = h.pair()
    gaps = []
    total = 0
    for r in rows:
        if r["tipo"] != "p":
            continue
        o = r["tra"].get("fr")
        if not o or not r["io"] or not o["t"]:
            continue
        total += 1
        a = r["io"].count("<b>")
        b = o["t"].count("<b>")
        if a != b:
            gaps.append((abs(a - b), r["cle"], a, b))
    gaps.sort(reverse=True)
    print("=" * 62)
    print("CHECK 7 — THE BOLD OF THE TWO COLUMNS")
    print("=" * 62)
    print(f"{len(gaps)} paragraphs out of {total} do not have the same "
          f"number of bold passages on both sides "
          f"({100 * len(gaps) / max(1, total):.1f} %)")
    by_table = defaultdict(int)
    for e, key, a, b in gaps:
        by_table[key.split("-")[0]] += 1
    print("  by table:", dict(sorted(by_table.items())))
    print("  the twenty widest gaps:")
    for e, key, a, b in gaps[:20]:
        print(f"    {key:<18} ido {a:>2}  fra {b:>2}   (gap {e})")
    return gaps


def check_8():
    """Do the two columns of a row carry the SAME paragraph?

    Check 3 sees the orphaned keys — those that exist on one side only. It
    does not see the graver fault: two keys that correspond to each other
    while their texts have nothing to do with each other. That happens as
    soon as the author's paragraph numbering is missing and the survey has
    to count for itself: at table 5, a dialogue with no printed numbers,
    the two surveyors did not cut in the same places, and the counter
    drifted. The page then set a speech opposite the answer to the one
    before it.

    A simple signal betrays it: LENGTH. A translation is rarely less than
    half or more than double its original; a ratio of seven to one is not a
    translation, it is a shift. We report, and the eye verifies.
    """
    import sys as _s
    _s.path.insert(0, str(ROOT / "tools"))
    import importlib
    h = importlib.import_module("html")
    rows = h.pair()

    def bare_(t):
        return re.sub(r"<[^>]+>", "", t or "")

    gaps = []
    for r in rows:
        if r["tipo"] != "p":
            continue
        a = len(bare_(r["io"]))
        b = len(bare_((r["tra"].get("fr") or {}).get("t")))
        if a < 20 or b < 20:
            continue
        ratio = max(a, b) / min(a, b)
        if ratio > 1.8:
            gaps.append((round(ratio, 2), r["cle"], a, b))
    gaps.sort(reverse=True)
    print("=" * 62)
    print("CHECK 8 — ARE THE TWO COLUMNS SPEAKING OF THE SAME THING?")
    print("=" * 62)
    total = sum(1 for r in rows if r["tipo"] == "p")
    print(f"{len(gaps)} rows out of {total} pair texts of very "
          f"unequal lengths (ratio > 1.8)")
    per = defaultdict(int)
    for _, key, _, _ in gaps:
        per[key.split("-")[0]] += 1
    print("  by table:", dict(sorted(per.items())))
    for ratio, key, a, b in gaps[:15]:
        print(f"    {key:<18} ido {a:>4} car.  fra {b:>4} car.  "
              f"(×{ratio})")
    return gaps


def check_1_2(name_, pages, fault):
    seen = defaultdict(list)
    for f, i, leaf, folio in pages:
        if not leaf:
            fault(f"{name_} 1 : {f}:{i} — page sans numéro de feuillet")
            continue
        seen[int(leaf)].append(f"{f}:{i}")
        if folio and int(folio) != int(leaf) - 2:
            fault(f"{name_} 1 : {f}:{i} — feuillet {leaf} porte le "
                  f"folio {folio}, attendu {int(leaf) - 2}")
    for n, ou in sorted(seen.items()):
        if len(ou) > 1:
            fault(f"{name_} 2 : feuillet {n} relevé {len(ou)} fois "
                  f"({', '.join(ou)})")
    if seen:
        # A BLANK PAGE IS NOT A FORGOTTEN PAGE. The Ido booklet has two
        # blank versos (leaves 48 and 76); reporting them as missing would
        # make the check cry out at every run, and a check that cries for
        # nothing ends up unread. We consult the geometry survey: a page
        # whose ink box is degenerate is blank, and its absence is normal.
        blank = blank_leaves(name_)
        missing_ = [n for n in range(min(seen), max(seen) + 1)
                     if n not in seen and n not in blank]
        if missing_:
            fault(f"{name_} 2 : feuillets non relevés dans l'intervalle "
                  f"{min(seen)}–{max(seen)} : "
                  f"{', '.join(map(str, missing_))}")


def check_4_5(name_, keys, folder, fault):
    for key, occ in keys.items():
        mains_ = [o for o in occ if not o[4]]
        if len(mains_) > 1:
            ou = ", ".join(f"{o[0]}:{o[1]}" for o in mains_)
            fault(f"{name_} 4 : clé « {key} » posée {len(mains_)} fois "
                  f"sans « suite » ({ou})")
    for f in sorted(folder.glob("*.tex")):
        t = f.read_text(encoding="utf-8")
        p = t.count("\\parplein") + t.count("\\ccplein")
        c = t.count("\\VUcontinue")
        if p != c:
            fault(f"{name_} 5 : {f.name} — {p} \\parplein pour "
                  f"{c} \\VUcontinue")


def hand():
    io, pio = read_file(ROOT / "text" / "io")
    fr, pfr = read_file(ROOT / "text" / "fr")
    faults = []

    def fault(m):
        faults.append(m)

    check_1_2("ido", pio, fault)
    check_1_2("fra", pfr, fault)
    check_4_5("ido", io, ROOT / "text" / "io", fault)
    check_4_5("fra", fr, ROOT / "text" / "fr", fault)
    check_6(fault)
    check_7()
    check_8()

    # Check 3, by table: we want to see WHERE the orphans concentrate.
    # Spread one per table, they are differences of edition; grouped on a
    # single one, they are a fault of survey.
    def table_(key):
        return key.split("-")[0]

    def pairable(key):
        return not any(f"-{s}-" in key for s in WITHOUT_COUNTERPART)

    orphan_io = defaultdict(list)
    orphan_fr = defaultdict(list)
    paired = defaultdict(int)
    for key in io:
        if not pairable(key):
            continue
        (paired if key in fr else orphan_io)[table_(key)] = (
            paired[table_(key)] + 1 if key in fr
            else orphan_io[table_(key)] + [key])
    for key in fr:
        if pairable(key) and key not in io:
            orphan_fr[table_(key)].append(key)

    print("=" * 62)
    print("CHECK 3 — THE PAIRING OF THE TWO COLUMNS")
    print("=" * 62)
    print(f"{'tabl.':>6} {'paired':>9} {'ido only':>9} {'fra only':>9}")
    total = [0, 0, 0]
    for t in sorted(set(list(paired) + list(orphan_io) + list(orphan_fr))):
        a, i, f = (paired.get(t, 0), len(orphan_io.get(t, [])),
                   len(orphan_fr.get(t, [])))
        total = [total[0] + a, total[1] + i, total[2] + f]
        flag = "  <<<" if (i + f) > max(3, a * 0.25) else ""
        print(f"{t:>6} {a:>9} {i:>9} {f:>9}{flag}")
    print(f"{'TOTAL':>6} {total[0]:>9} {total[1]:>9} {total[2]:>9}")
    print()
    for t in sorted(set(list(orphan_io) + list(orphan_fr))):
        if orphan_io.get(t):
            print(f"  {t} ido seul : {' '.join(sorted(orphan_io[t]))}")
        if orphan_fr.get(t):
            print(f"  {t} fra seul : {' '.join(sorted(orphan_fr[t]))}")

    print()
    print("=" * 62)
    if faults:
        print(f"CHECKS 1, 2, 4, 5 — {len(faults)} REPORTS")
        print("=" * 62)
        for m in faults:
            print(" ", m)
    else:
        print("CHECKS 1, 2, 4, 5 — nothing to report")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(hand())
