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

RACINE = Path(__file__).resolve().parent.parent
CLE = re.compile(r"^%%K\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$")
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")

# Running heads do not match: the Ido edition adds some the French does
# not know, and their numbering (tit-1, tit-2...) is proper to each
# edition. Counting them as orphans would drown the useful signal in
# noise.
SANS_VIS_A_VIS = ("tit", "apar", "noto")


def lire(dossier):
    """{key: [(file, leaf, folio, continuation)]} and the list of pages."""
    cles = defaultdict(list)
    pages = []
    for f in sorted(dossier.glob("*.tex")):
        feuillet = folio = ""
        for i, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            mp = PAGE.search(l)
            if mp:
                feuillet, folio = mp.group(1) or "", mp.group(2) or ""
                pages.append((f.name, i, feuillet, folio))
                continue
            m = CLE.match(l.strip())
            if m:
                cles[m.group(1)].append(
                    (f.name, i, feuillet, folio, m.group(3) == "suite"))
    return cles, pages


def feuillets_vierges(nom):
    """Leaves with no ink block, from tools/inventory-<language>.json."""
    import json
    lg = {"ido": "io", "fra": "fr"}[nom]
    f = RACINE / "tools" / f"inv-{lg}.json"
    if not f.exists():
        return set()
    inv = json.loads(f.read_text(encoding="utf-8"))
    vierges = set()
    for k, v in inv.items():
        if v.get("vide"):
            vierges.add(int(k))
            continue
        b, px = v.get("bloc"), v.get("px")
        if b and px and (b[2] - b[0]) < 0.25 * px[0]:
            vierges.add(int(k))
    return vierges


def controle_6(faute):
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
    for nom, lg in (("ido", "io"), ("fra", "fr")):
        f = RACINE / "tools" / f"inv-{lg}.json"
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
            faute(f"{nom} 6 : le bloc d'encre couvre {100*lr:.1f} % de la "
                  f"largeur et {100*hr:.1f} % de la hauteur de l'image — "
                  f"le cadre du scan tombe dans le papier, l'echelle "
                  f"absolue tiree de l'image est fausse (les rapports "
                  f"internes, eux, restent bons)")


def controle_7():
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
    _s.path.insert(0, str(RACINE / "tools"))
    import importlib
    h = importlib.import_module("html")
    rangi = h.paro()
    ecarts = []
    total = 0
    for r in rangi:
        if r["tipo"] != "p":
            continue
        o = r["tra"].get("fr")
        if not o or not r["io"] or not o["t"]:
            continue
        total += 1
        a = r["io"].count("<b>")
        b = o["t"].count("<b>")
        if a != b:
            ecarts.append((abs(a - b), r["cle"], a, b))
    ecarts.sort(reverse=True)
    print("=" * 62)
    print("CONTRÔLE 7 — LE GRAS DES DEUX COLONNES")
    print("=" * 62)
    print(f"{len(ecarts)} alinéas sur {total} n'ont pas le même nombre de "
          f"passages gras des deux côtés "
          f"({100 * len(ecarts) / max(1, total):.1f} %)")
    par_tableau = defaultdict(int)
    for e, cle, a, b in ecarts:
        par_tableau[cle.split("-")[0]] += 1
    print("  par tableau :", dict(sorted(par_tableau.items())))
    print("  les vingt plus gros écarts :")
    for e, cle, a, b in ecarts[:20]:
        print(f"    {cle:<18} ido {a:>2}  fra {b:>2}   (écart {e})")
    return ecarts


def controle_8():
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
    _s.path.insert(0, str(RACINE / "tools"))
    import importlib
    h = importlib.import_module("html")
    rangi = h.paro()

    def nu(t):
        return re.sub(r"<[^>]+>", "", t or "")

    ecarts = []
    for r in rangi:
        if r["tipo"] != "p":
            continue
        a = len(nu(r["io"]))
        b = len(nu((r["tra"].get("fr") or {}).get("t")))
        if a < 20 or b < 20:
            continue
        ratio = max(a, b) / min(a, b)
        if ratio > 1.8:
            ecarts.append((round(ratio, 2), r["cle"], a, b))
    ecarts.sort(reverse=True)
    print("=" * 62)
    print("CONTRÔLE 8 — LES DEUX COLONNES PARLENT-ELLES DU MÊME ?")
    print("=" * 62)
    total = sum(1 for r in rangi if r["tipo"] == "p")
    print(f"{len(ecarts)} rangs sur {total} apparient des textes de "
          f"longueurs très inégales (rapport > 1,8)")
    par = defaultdict(int)
    for _, cle, _, _ in ecarts:
        par[cle.split("-")[0]] += 1
    print("  par tableau :", dict(sorted(par.items())))
    for ratio, cle, a, b in ecarts[:15]:
        print(f"    {cle:<18} ido {a:>4} car.  fra {b:>4} car.  "
              f"(×{ratio})")
    return ecarts


def controle_1_2(nom, pages, faute):
    vus = defaultdict(list)
    for f, i, feuillet, folio in pages:
        if not feuillet:
            faute(f"{nom} 1 : {f}:{i} — page sans numéro de feuillet")
            continue
        vus[int(feuillet)].append(f"{f}:{i}")
        if folio and int(folio) != int(feuillet) - 2:
            faute(f"{nom} 1 : {f}:{i} — feuillet {feuillet} porte le "
                  f"folio {folio}, attendu {int(feuillet) - 2}")
    for n, ou in sorted(vus.items()):
        if len(ou) > 1:
            faute(f"{nom} 2 : feuillet {n} relevé {len(ou)} fois "
                  f"({', '.join(ou)})")
    if vus:
        # A BLANK PAGE IS NOT A FORGOTTEN PAGE. The Ido booklet has two
        # blank versos (leaves 48 and 76); reporting them as missing would
        # make the check cry out at every run, and a check that cries for
        # nothing ends up unread. We consult the geometry survey: a page
        # whose ink box is degenerate is blank, and its absence is normal.
        vierges = feuillets_vierges(nom)
        manquants = [n for n in range(min(vus), max(vus) + 1)
                     if n not in vus and n not in vierges]
        if manquants:
            faute(f"{nom} 2 : feuillets non relevés dans l'intervalle "
                  f"{min(vus)}–{max(vus)} : "
                  f"{', '.join(map(str, manquants))}")


def controle_4_5(nom, cles, dossier, faute):
    for cle, occ in cles.items():
        principaux = [o for o in occ if not o[4]]
        if len(principaux) > 1:
            ou = ", ".join(f"{o[0]}:{o[1]}" for o in principaux)
            faute(f"{nom} 4 : clé « {cle} » posée {len(principaux)} fois "
                  f"sans « suite » ({ou})")
    for f in sorted(dossier.glob("*.tex")):
        t = f.read_text(encoding="utf-8")
        p = t.count("\\parplein") + t.count("\\ccplein")
        c = t.count("\\VUcontinue")
        if p != c:
            faute(f"{nom} 5 : {f.name} — {p} \\parplein pour "
                  f"{c} \\VUcontinue")


def main():
    io, pio = lire(RACINE / "text" / "io")
    fr, pfr = lire(RACINE / "text" / "fr")
    fautes = []

    def faute(m):
        fautes.append(m)

    controle_1_2("ido", pio, faute)
    controle_1_2("fra", pfr, faute)
    controle_4_5("ido", io, RACINE / "text" / "io", faute)
    controle_4_5("fra", fr, RACINE / "text" / "fr", faute)
    controle_6(faute)
    controle_7()
    controle_8()

    # Check 3, by table: we want to see WHERE the orphans concentrate.
    # Spread one per table, they are differences of edition; grouped on a
    # single one, they are a fault of survey.
    def tableau(cle):
        return cle.split("-")[0]

    def apparieble(cle):
        return not any(f"-{s}-" in cle for s in SANS_VIS_A_VIS)

    orph_io = defaultdict(list)
    orph_fr = defaultdict(list)
    apparies = defaultdict(int)
    for cle in io:
        if not apparieble(cle):
            continue
        (apparies if cle in fr else orph_io)[tableau(cle)] = (
            apparies[tableau(cle)] + 1 if cle in fr
            else orph_io[tableau(cle)] + [cle])
    for cle in fr:
        if apparieble(cle) and cle not in io:
            orph_fr[tableau(cle)].append(cle)

    print("=" * 62)
    print("CONTRÔLE 3 — APPARIEMENT DES DEUX COLONNES")
    print("=" * 62)
    print(f"{'tabl.':>6} {'appariés':>9} {'ido seul':>9} {'fra seul':>9}")
    total = [0, 0, 0]
    for t in sorted(set(list(apparies) + list(orph_io) + list(orph_fr))):
        a, i, f = (apparies.get(t, 0), len(orph_io.get(t, [])),
                   len(orph_fr.get(t, [])))
        total = [total[0] + a, total[1] + i, total[2] + f]
        drapeau = "  <<<" if (i + f) > max(3, a * 0.25) else ""
        print(f"{t:>6} {a:>9} {i:>9} {f:>9}{drapeau}")
    print(f"{'TOTAL':>6} {total[0]:>9} {total[1]:>9} {total[2]:>9}")
    print()
    for t in sorted(set(list(orph_io) + list(orph_fr))):
        if orph_io.get(t):
            print(f"  {t} ido seul : {' '.join(sorted(orph_io[t]))}")
        if orph_fr.get(t):
            print(f"  {t} fra seul : {' '.join(sorted(orph_fr[t]))}")

    print()
    print("=" * 62)
    if fautes:
        print(f"CONTRÔLES 1, 2, 4, 5 — {len(fautes)} SIGNALEMENTS")
        print("=" * 62)
        for m in fautes:
            print(" ", m)
    else:
        print("CONTRÔLES 1, 2, 4, 5 — rien à signaler")
    return 1 if fautes else 0


if __name__ == "__main__":
    sys.exit(main())
