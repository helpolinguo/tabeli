#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controles.py — vérifie ce que ni le compilateur ni l'œil ne voient.

    python3 outils/controles.py

Un relevé peut compiler parfaitement et être faux. Ces contrôles
cherchent les fautes qui ne se signalent pas d'elles-mêmes.

  1. PAGINATION      folio imprimé = feuillet − 2, sur toutes les pages.
  2. FEUILLETS       aucun feuillet du fac-similé oublié, aucun relevé
                     deux fois, dans l'intervalle couvert.
  3. APPARIEMENT     chaque clé %%K de l'ido a-t-elle un vis-à-vis
                     français, et réciproquement ? C'est LE contrôle du
                     projet : une clé orpheline est soit un écart réel
                     entre les deux éditions, soit une faute de relevé,
                     et il faut regarder chacune pour trancher.
  4. UNICITÉ         aucune clé ne paraît deux fois dans une même
                     langue, sauf le second membre d'un alinéa coupé
                     par un changement de page, qui porte « suite ».
  5. COUPURES        chaque fin d'alinea a cheval (\\parplein ou
                     \\ccplein) a sa reprise \\VUcontinue.
  6. GEOMETRIE       la boite d'encre occupe-t-elle une part
                     vraisemblable de la page ? Sinon, le cadre du scan
                     tombe dans le papier et l'echelle est fausse.
  7. GRAS            les deux colonnes mettent-elles en gras le meme
                     nombre de passages ? L'une temoigne pour l'autre.
  8. SYNCHRONIE      les deux colonnes d'un rang portent-elles le meme
                     alinea ? Une difference de longueur enorme dit que
                     le compteur de cles a derive.

Le contrôle 3 ne peut pas être automatisé jusqu'au verdict : il compte
et il montre. C'est au releveur de dire, pour chaque orphelin, s'il est
légitime.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CLE = re.compile(r"^%%K\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$")
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")

# Les intertitres ne s'apparient pas : l'edition ido en ajoute que le
# francais ne connait pas, et leur numerotation (tit-1, tit-2...) est
# propre a chaque edition. Les compter comme orphelins noierait le
# signal utile sous le bruit.
SANS_VIS_A_VIS = ("tit", "apar", "noto")


def lire(dossier):
    """{cle: [(fichier, feuillet, folio, suite)]} et la liste des pages."""
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
    """Feuillets sans bloc d'encre, d'apres outils/inv-<langue>.json."""
    import json
    lg = {"ido": "io", "fra": "fr"}[nom]
    f = RACINE / "outils" / f"inv-{lg}.json"
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
    """La boite d'encre occupe-t-elle une part vraisemblable de la page ?

    Un livre imprime laisse des marges. Quand la boite d'encre couvre
    presque toute la hauteur de l'image, ce n'est pas que le livre n'a
    pas de marges : c'est que le CADRE DE LA PRISE DE VUE tombe a
    l'interieur du papier. La hauteur d'image ne vaut alors plus la
    hauteur du papier, et l'echelle qu'on en tire est fausse.

    C'est le cas du fac-simile francais : 96,5 % de la hauteur, contre
    83,7 % pour l'ido. Les rapports internes -- pas sur justification,
    hauteur d'x sur justification -- restent bons, et la composition
    est donc juste ; seule l'echelle d'ensemble est incertaine. Une
    regle posee sur l'exemplaire la corrige d'un coup.
    """
    import json
    import statistics
    for nom, lg in (("ido", "io"), ("fra", "fr")):
        f = RACINE / "outils" / f"inv-{lg}.json"
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
    """Le gras des deux colonnes se repond-il ?

    Les deux livrets mettent en gras LES MEMES CHOSES : le mot de
    vocabulaire que le tableau mural illustre. « ok \VUgras{tabli} » a
    pour vis-a-vis « huit \VUgras{tables} ». Le nombre de passages gras
    d'un alinea doit donc etre le meme des deux cotes -- non pas par
    principe, mais parce que c'est ainsi que les deux editions sont
    faites.

    Quand il differe, c'est presque toujours une faute de releve : le
    releveur a mis en gras un mot qui ne l'etait pas, ou l'inverse.
    L'autre colonne sert alors de temoin. Ce controle ne tranche pas --
    il ne sait pas laquelle des deux a tort -- il DESIGNE les alineas a
    revoir au fac-simile, et il les classe par ecart decroissant pour
    qu'on commence par les plus douteux.
    """
    import subprocess
    import sys as _s
    _s.path.insert(0, str(RACINE / "outils"))
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
    """Les deux colonnes d'un rang portent-elles le MEME alinea ?

    Le controle 3 voit les cles orphelines — celles qui n'existent que
    d'un cote. Il ne voit pas la faute plus grave : deux cles qui se
    correspondent alors que leurs textes n'ont rien a voir. Cela
    arrive des que la numerotation d'alineas de l'auteur manque et que
    le releve doit compter lui-meme : au tableau 5, un dialogue sans
    numeros imprimes, les deux releveurs n'ont pas coupe aux memes
    endroits, et le compteur a derive. La page mettait alors en regard
    une replique et la reponse a la precedente.

    Un signal simple le trahit : LA LONGUEUR. Une traduction fait
    rarement moins de la moitie ou plus du double de son original ; un
    rapport de sept pour un ne se traduit pas, il se decale. On
    signale, et l'oeil verifie.
    """
    import sys as _s
    _s.path.insert(0, str(RACINE / "outils"))
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
        # UNE PAGE VIERGE N'EST PAS UNE PAGE OUBLIEE. Le livret ido a
        # deux versos blancs (feuillets 48 et 76) ; les signaler comme
        # manquants ferait crier le controle a chaque execution, et un
        # controle qui crie pour rien finit par ne plus etre lu. On
        # interroge le releve de geometrie : une page dont la boite
        # d'encre est degeneree est vierge, et son absence est normale.
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
    io, pio = lire(RACINE / "texto" / "io")
    fr, pfr = lire(RACINE / "texto" / "fr")
    fautes = []

    def faute(m):
        fautes.append(m)

    controle_1_2("ido", pio, faute)
    controle_1_2("fra", pfr, faute)
    controle_4_5("ido", io, RACINE / "texto" / "io", faute)
    controle_4_5("fra", fr, RACINE / "texto" / "fr", faute)
    controle_6(faute)
    controle_7()
    controle_8()

    # Controle 3, par tableau : on veut voir OU se concentrent les
    # orphelins. Repartis un par tableau, ce sont des ecarts d'edition ;
    # groupes sur un seul, c'est une faute de releve.
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
