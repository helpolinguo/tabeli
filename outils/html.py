#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html.py — construit index.html a partir des sources LaTeX.

    python3 outils/html.py

LE TEXTE N'EST SAISI QU'UNE FOIS. Les fichiers de texto/ sont la seule
source : le PDF et la page de lecture en sortent tous deux. Une
correction de lecture faite dans le .tex se retrouve donc a l'ecran
sans qu'on ait rien a reporter, et il est impossible que les deux
etats du texte divergent.

CE QUE LA PAGE FAIT DU RELEVE DIPLOMATIQUE. Le PDF garde les coupures
de ligne du fac-simile ; la page de lecture, elle, ne le peut pas —
sa colonne n'a pas de largeur fixe. Les deux marques du releve y sont
donc traitees ainsi :
    \\nl  (fin de ligne sans trait d'union)  ->  une espace
    \\cc  (fin de ligne AVEC trait d'union)  ->  rien : le mot se
          recolle, puisque le trait d'union n'appartenait pas au mot
          mais a la composition.
C'est la seule maniere de rendre le texte cherchable : « docochambro »
coupe en « doco-chambro » ne se trouverait pas.

L'APPARIEMENT DES DEUX COLONNES ne se fait ni par page ni par ligne —
les deux editions n'ont ni la meme pagination ni le meme nombre de
lignes — mais par les cles « %%K » du releve, qui reprennent la
NUMEROTATION D'ALINEA DE L'AUTEUR. Elle est la meme dans les deux
livrets, et c'est le seul ancrage qu'ils partagent.
"""
import html as H
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Les langues de la colonne de droite. « fr » est le texte source
# (releve sur le fac-simile) ; les autres seront des traductions, et
# porteront la mention qui convient.
LANGUES = [
    {"kodo": "fr", "nomo": "Français", "dir": "ltr", "fonto": "fac-similé"},
]

TITRO = "Expliko-Libreto di la Delmas-Tabeli helpanta"
SUBTITRO = ("J. Guignon &middot; Ido-Kontoro, Thaon-les-Vosges, 1926 "
            "&middot; E. Rochelle &middot; G. Delmas, Bordeaux")


# -------------------------------------------------------------------
#  1. LECTURE DES SOURCES LaTeX
# -------------------------------------------------------------------
CLE = re.compile(r"^%%K\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$")
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")


def accolade(s, i):
    """Contenu de l'accolade qui commence a s[i] == '{'. Renvoie
    (contenu, index apres l'accolade fermante). Les accolades
    imbriquees sont comptees : \\VUgras{Ka\\cc rolus} contient lui-meme
    des macros, et une simple recherche du prochain '}' les couperait."""
    assert s[i] == "{"
    p = 0
    j = i
    while j < len(s):
        if s[j] == "{":
            p += 1
        elif s[j] == "}":
            p -= 1
            if p == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def texte_html(t):
    """Convertit un fragment LaTeX du releve en HTML."""
    # LES COMMENTAIRES D'ABORD. Un « % » ouvre un commentaire jusqu'a la
    # fin de la ligne, et le releve en use : le contenu d'une note
    # s'ouvre par « {% » pour que LaTeX n'y prenne pas d'espace, et se
    # ferme par « .% » pour la meme raison. Sans les oter, le texte
    # rendu commencait par « % (*) Por la baptonomi... » — et le
    # marqueur d'appel, precede de ce pourcent, n'etait plus reconnu :
    # aucune note ne se reliait a son appel.
    # Le pourcent litteral s'ecrit « \% » dans le releve ; on le
    # protege avant de couper, et on le rend apres.
    t = t.replace("\\%", "\x00")
    t = re.sub(r"%.*?(?:\n|$)", "\n", t)
    t = t.replace("\x00", "%")

    # Les coupures : elles portent la logique du releve.
    t = t.replace("\\cc\n", "").replace("\\cc", "")
    t = t.replace("\\nl\n", " ").replace("\\nl", " ")
    t = t.replace("\\parplein", "").replace("\\VUcontinue", "")
    t = re.sub(r"\\VUblancAlinea\b", "", t)
    t = re.sub(r"\\VUsaut\{[^}]*\}", "", t)
    t = re.sub(r"\\VUblanc\{[^}]*\}", "", t)
    t = re.sub(r"\\VUinterlignePage\{[^}]*\}", "", t)

    out = []
    i = 0
    balises = {"\\VUgras": "b", "\\textit": "i", "\\textsuperscript": "sup",
               "\\emph": "i", "\\textbf": "b"}
    # Macros a PLUSIEURS arguments : on dit combien il en faut lire et
    # lequel porte le texte. \VUcentre{corps}{interlettrage}{texte} :
    # les deux premiers sont des mesures du fac-simile, ils n'ont rien
    # a faire dans la page de lecture, mais il faut les LIRE, sinon
    # leur contenu tombe dans le texte — c'est ce qui donnait
    # « 12.6pt{120}{EXPLIKO - LIBRETO} » au premier essai.
    # Le troisieme membre est l'habillage HTML du texte garde : les
    # lignes d'apparat d'une ouverture de tableau sont des LIGNES, et
    # doivent le rester a l'ecran — sans quoi « EXPLIKO - LIBRETO DI la
    # Delmas - tabeli helpanta UNESMA SERIO » se lit d'un trait.
    # \VUpk ne compose rien autour de son texte \u2014 le bloc qui la porte
    # le centre deja \u2014 mais c'est une LIGNE d'apparat, et la table des
    # matieres doit la compter comme telle : les titres des tableaux 8,
    # 11, 12, 13 et 16 passent par elle, et non par \VUtitre. Sans
    # marque, ils etaient invisibles a la table, qui annoncait ces
    # tableaux sous leur seul numero. On la marque donc d'une classe
    # SANS STYLE, \u00ab pk \u00bb : le rendu ne change pas d'un pixel, mais la
    # ligne se compte. Le nom de la classe doit rester accorde a
    # LIGNE_AP, qui la relit.
    # LE CORPS DE CARACTERE SE GARDE, LUI. Les autres mesures du
    # fac-simile ne servent qu'a l'imprime, mais le corps dit si deux
    # lignes d'apparat sont une seule et meme chose : le titre du tableau
    # 6 tient sur deux lignes de 11.4pt, celui du 13 sur deux lignes de
    # 10.2pt, et la table les annoncait comme un titre suivi d'une
    # section. Une ligne de corps DIFFERENT, elle, commence autre chose
    # \u2014 au tableau 2, \u00ab La Korpo homala. \u00bb est en 13.2pt sous un titre
    # en 11.4pt. On le depose donc dans data-korpo, que la table relit.
    arite = {"\\VUcentre": (3, 2, '<span class="ln" data-korpo="%(korpo)s">'
                                  '%(texto)s</span>'),
             "\\VUtitre": (3, 2, '<span class="ln lg" data-korpo="%(korpo)s">'
                                 '%(texto)s</span>'),
             "\\VUpk": (3, 2, '<span class="pk" data-korpo="%(korpo)s">'
                              '%(texto)s</span>'),
             "\\VUcentreA": (4, 3, '<span class="ln" data-korpo="%(korpo)s">'
                                   '%(texto)s</span>'),
             "\\VUfilet": (1, None, '<span class="fil"></span>'),
             "\\VUornamento": (1, None, '<span class="orn">\u2766</span>'),
             "\\VUnotes": (2, 1, "%(texto)s"),
             # \fontsize{corps}{interligne} : deux mesures du fac-simile,
             # rien a garder. Non declaree, elle passait pour une macro
             # inconnue a UN argument : le corps tombait dans le texte et
             # l'interligne restait entre accolades \u2014 le titre de la
             # Balneyo s'annoncait \u00ab 10.2pt{10.2pt}[40]{La Balneyo.} \u00bb.
             "\\fontsize": (2, None, "")}
    while i < len(t):
        if t[i] == "\\":
            m = re.match(r"\\[A-Za-z]+", t[i:])
            if m:
                nom = m.group(0)
                j = i + len(nom)
                while j < len(t) and t[j] == " ":
                    j += 1
                # L'ARGUMENT OPTIONNEL SE LIT AUSSI. \textls[40]{...}
                # porte son interlettrage entre crochets ; non lu, il
                # sortait tel quel — « [40]{La Balneyo.} ». C'est une
                # mesure du fac-simile : on la lit et on la jette.
                while j < len(t) and t[j] == "[":
                    ferme = t.find("]", j)
                    if ferme < 0:
                        break
                    j = ferme + 1
                    while j < len(t) and t[j] == " ":
                        j += 1
                if nom in arite:
                    n, garde, habit = arite[nom]
                    args = []
                    k = j
                    for _ in range(n):
                        while k < len(t) and t[k] in " \n":
                            k += 1
                        if k < len(t) and t[k] == "{":
                            a, k = accolade(t, k)
                            args.append(a)
                        else:
                            args.append("")
                    if garde is None:
                        out.append(habit)
                    elif garde < len(args):
                        out.append(habit % {
                            "texto": texte_html(args[garde]),
                            "korpo": args[0] if args else ""})
                    i = k
                    continue
                if nom in balises and j < len(t) and t[j] == "{":
                    dedans, k = accolade(t, j)
                    out.append(f"<{balises[nom]}>{texte_html(dedans)}"
                               f"</{balises[nom]}>")
                    i = k
                    continue
                if nom == "\\textasciitilde":
                    out.append("~")
                    i = j
                    continue
                # Macro inconnue : on la laisse tomber avec son argument.
                if j < len(t) and t[j] == "{":
                    dedans, k = accolade(t, j)
                    out.append(texte_html(dedans))
                    i = k
                    continue
                i = j
                continue
            # \, \; \: — espaces fines
            if t[i + 1:i + 2] in (",", ";", ":"):
                out.append("\u202f")
                i += 2
                continue
            out.append(t[i + 1:i + 2])
            i += 2
            continue
        # UN GROUPE N'EST PAS DU TEXTE. Quelques endroits du releve
        # composent a la main ce que les macros \VU font ailleurs :
        # « {\centering\textit{(Videz la plano.)}\par} ». Les accolades y
        # ouvrent une PORTEE LaTeX, elles ne s'impriment pas ; laissees
        # telles quelles, elles sortaient dans la page et dans la table
        # des matieres — « {(Videz la plano.)} ». On lit le groupe et on
        # ne garde que son contenu. L'accolade litterale, elle, s'ecrit
        # « \{ » dans le releve, et le cas est traite juste au-dessus.
        if t[i] == "{":
            dedans, k = accolade(t, i)
            out.append(texte_html(dedans))
            i = k
            continue
        out.append(t[i])
        i += 1
    t = "".join(out)

    # UN MOT COUPE PAR LA COMPOSITION RESTE UN MOT. Quand la coupure
    # tombe a l'interieur d'un passage en gras, le releve porte deux
    # \\VUgras — un par ligne — et la conversion naive en rendait deux
    # balises : « <b>ar</b><b>moro</b> », soit « armoro » aux yeux mais
    # deux mots pour la recherche du navigateur, qui ne trouvait plus
    # « armoro ». On recolle donc les balises jointives. Deux appels de
    # renvoi separes par la coupure — « (9, 11, » et « 12) » — sont le
    # meme renvoi, et se reunissent de meme, l'espace en plus.
    # La regle vaut pour les balises JOINTIVES seulement. Premiere
    # version, elle tolerait l'espace entre les deux — et « une
    # \\VUgras{armoire}\\nl \\VUgras{vitree} », deux mots gras sur deux
    # lignes du fac-simile francais, devenait « armoirevitree ».
    # L'espace distingue les deux cas : \\cc n'en laisse pas, \\nl si.
    for b in ("b", "i"):
        t = re.sub(rf"</{b}><{b}>", "", t)
    # Les renvois, eux, se reunissent MEME separes : « (9, 11, » et
    # « 12) » sont un seul appel que la ligne a coupe en deux.
    t = re.sub(r"</sup>\s*<sup>", " ", t)

    # L'apostrophe des deux fac-similes est la courbe, non la droite :
    # « l'unesma », « L'Ecole ». La droite est une commodite de clavier
    # que l'imprime ne connait pas.
    t = t.replace("'", "\u2019")

    # Ponctuation du fac-simile.
    t = t.replace("---", "\u2014").replace("--", "\u2013")
    t = re.sub(r"\s+", " ", t).strip()
    # Le tiret cadratin colle au mot qui suit quand le compositeur
    # serre sa ligne (« 3. ---Ne omna... », folio 5). C'est une
    # contrainte de justification, non une intention : la page de
    # lecture, qui rejustifie, rend l'espace. Le PDF, lui, garde le
    # fac-simile.
    t = re.sub(r"\u2014(?=[^\s\u2014])", "\u2014 ", t)
    # Espace fine insecable devant la ponctuation haute, usage francais
    # et ido de l'epoque — les deux livrets la composent.
    t = re.sub(r" ([;:?!])", "\u202f\\1", t)
    t = t.replace("<b> ", " <b>").replace(" </b>", "</b> ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def lire(chemin):
    """Renvoie la liste des blocs d'un fichier de releve.

    Un bloc = {cle, tipo, folio, feuillet, html}. Tout ce qui precede
    la premiere cle d'une page (les lignes d'apparat d'une ouverture de
    tableau, les notes) est rattache au bloc qui suit ou porte sa
    propre cle.
    """
    src = chemin.read_text(encoding="utf-8")
    blocs = []
    folio = ""
    feuillet = ""
    courant = None
    notes = []
    dans_note = False
    accolades = 0
    for ligne in src.splitlines():
        mp = PAGE.search(ligne)
        if mp:
            feuillet = mp.group(1) or ""
            folio = mp.group(2) or ""
            continue
        m = CLE.match(ligne.strip())
        if m:
            if courant:
                blocs.append(courant)
            # Le troisieme membre d'une cle : « suite » pour la reprise
            # d'un alinea coupe par un changement de page, « pos=<cle> »
            # pour un bloc qui SE LIT ailleurs qu'il s'imprime.
            extra = m.group(3) or ""
            courant = {"cle": m.group(1), "tipo": m.group(2),
                       "suite": extra == "suite",
                       "apres": extra[4:] if extra.startswith("pos=") else "",
                       "folio": folio, "feuillet": feuillet, "brut": []}
            continue
        if ligne.startswith("%"):
            continue
        if "\\end{VUpage}" in ligne:
            # La fin d'environnement n'est pas du texte. Sans cette
            # ligne-ci, « VUpage » se composait a la fin du dernier
            # alinea de chaque page : la macro inconnue tombait, son
            # nom restait.
            courant = None if courant is None else courant
            if courant is not None:
                courant["brut"].append(
                    ligne.replace("\\end{VUpage}", ""))
            continue
        if courant is not None:
            courant["brut"].append(ligne)
        elif ligne.strip().startswith("\\VUnotes"):
            notes.append(ligne)
    if courant:
        blocs.append(courant)

    # Les notes : elles sont declarees en tete de page, avant toute cle.
    # On les retrouve dans le brut de la source, on les extrait et on en
    # fait des blocs a part, poses a la fin de leur page.
    entier = src
    for mo in re.finditer(r"\\VUnotes\{[^}]*\}\{", entier):
        deb = mo.end() - 1
        dedans, _ = accolade(entier, deb)
        # A quelle page appartient-elle ? La derniere \begin{VUpage}
        # avant elle.
        avant = entier[:mo.start()]
        pages = list(PAGE.finditer(avant))
        f = pages[-1].group(2) if pages else ""
        fe = pages[-1].group(1) if pages else ""
        blocs.append({"cle": f"noto-f{fe}", "tipo": "noto", "suite": False,
                      "folio": f, "feuillet": fe,
                      "brut": [dedans]})


    for b in blocs:
        b["html"] = texte_html("\n".join(b["brut"]))
        del b["brut"]
    # LE MARQUEUR SE LIT SUR LE TEXTE RENDU, non sur la source. Il y est
    # parfois enferme dans une macro — « \textit{(*) Pro ke ta vorto...} »
    # au tableau 8 — et une expression reguliere posee sur le LaTeX ne
    # le voyait pas. Le HTML, lui, a deja resolu les macros : il ne
    # reste que le texte, et le marqueur y est en tete.
    for b in blocs:
        if b["tipo"] != "noto":
            b["apelo"] = ""
            continue
        nu = re.sub(r"<[^>]+>", "", b["html"]).strip()
        m2 = re.match(r"\(([^)]{1,3})\)", nu)
        b["apelo"] = m2.group(1) if m2 else ""

    # DEUX SOURCES POUR UNE MEME NOTE. Certains releves declarent la
    # note par une cle « %%K ... noto », d'autres la laissent porter par
    # le seul \VUnotes, que la seconde passe ci-dessus ramasse. Quand
    # les deux coexistent, la note paraissait deux fois. On ecarte le
    # doublon sur les premiers caracteres du texte nu.
    vus = set()
    net = []
    for b in blocs:
        if b["tipo"] == "noto":
            empreinte = re.sub(r"<[^>]+>|\s+", "", b["html"])[:40]
            if empreinte in vus:
                continue
            vus.add(empreinte)
        net.append(b)
    return [b for b in net if b["html"]]


def fusionner(blocs):
    """Recolle les blocs « suite » a leur bloc d'origine.

    Un alinea coupe par un changement de page porte deux fois la meme
    cle, la seconde marquee « suite ». Dans le PDF ce sont deux pages ;
    dans la page de lecture c'est un seul alinea, et il doit l'etre,
    sinon la colonne d'en face — qui ne coupe pas au meme endroit —
    ne lui repondrait plus.
    """
    out = []
    par_cle = {}
    for b in blocs:
        if b["suite"] and b["cle"] in par_cle:
            a = par_cle[b["cle"]]
            a["html"] = (a["html"] + " " + b["html"]).strip()
            a["folio2"] = b["folio"]
            continue
        par_cle[b["cle"]] = b
        out.append(b)
    return out


# -------------------------------------------------------------------
#  2. ASSEMBLAGE
# -------------------------------------------------------------------
DOSSIER = {"fr": "fr"}      # code de langue -> sous-dossier de texto/


# LA PAGE DE LECTURE NE PORTE QUE LES SEIZE TABLEAUX. Couverture,
# dedicace, PREFACO, AVERTISSEMENT, tables des matieres, annonces de
# l'editeur : tout cela est dans les deux PDF, qui reproduisent les
# volumes entiers, et n'a rien a faire dans une page dont l'objet est
# de mettre DEUX TEXTES EN REGARD. Ces pieces-la ne se repondent pas
# d'une edition a l'autre -- la preface de Guignon n'est pas
# l'avertissement de Rochelle, elle en est meme le contraire par le
# ton -- et les afficher cote a cote donnait deux colonnes qui se
# regardaient sans rien avoir a se dire.
#
# Le partage se lit sur le nom du fichier : « 00- » les liminaires,
# « 90- » la fin, et entre les deux les tableaux.
# « pos= » : CE QUI S'IMPRIME ICI SE LIT LA. Le fac-simile compose
# parfois un intertitre a une place que la page de lecture ne peut pas
# garder. Au tableau 2, « LA KAPO. » est imprime AVANT l'alinea 1 -- qui
# n'est pas la tete, mais l'annonce des trois parties du corps -- et le
# volume francais met la, lui, le titre de section « I. Le Corps
# Humain. ». Les deux colonnes annoncaient donc des choses differentes.
#
# Deplacer la macro dans le releve corrigerait la page de lecture et
# FAUSSERAIT LE PDF, qui est la transcription diplomatique : la ligne
# doit rester ou l'imprimeur l'a mise. On note donc le deplacement a
# cote d'elle, et le PDF ne bouge pas d'un point.
def deplacer(blocs):
    """Repose les blocs marques « pos= » derriere le bloc qu'ils visent."""
    fixes = [b for b in blocs if not b.get("apres")]
    for b in [b for b in blocs if b.get("apres")]:
        i = next((k for k, x in enumerate(fixes) if x["cle"] == b["apres"]),
                 None)
        if i is None:
            raise SystemExit(f'%%K {b["cle"]} : pos={b["apres"]} introuvable')
        fixes.insert(i + 1, b)
    return fixes


def lire_langue(sous_dossier):
    """Les seize tableaux d'une langue, dans l'ordre."""
    d = RACINE / "texto" / sous_dossier
    blocs = []
    for f in sorted(d.glob("*.tex")):
        if f.name.startswith(("00-", "90-")):
            continue
        blocs.extend(deplacer(fusionner(lire(f))))
    return blocs


# LES INTERTITRES NE S'APPARIENT PAS PAR LEUR CLE. C'est deja la regle
# du releve, et outils/controles.py la dit : « leur numerotation (tit-1,
# tit-2...) est propre a chaque edition ». L'ido subdivise plus fin que
# le francais -- sept intertitres au tableau 2 contre trois -- de sorte
# que t02-tit-2 ne designe pas la meme chose des deux cotes. Le rendu,
# lui, appariait tout par la cle : « La Torso. » se retrouvait en face
# de « II. La Gymnastique. », et les deux colonnes annoncaient des
# sections differentes. Dix-sept intertitres etaient ainsi mal apparies,
# sur onze tableaux.
#
# CE QUI LES APPARIE, C'EST LA PLACE. Un intertitre ouvre un alinea, et
# l'alinea, lui, porte la meme cle dans les deux editions -- c'est la
# le pivot du releve. On groupe donc les intertitres par l'alinea qu'ils
# precedent, et l'on apparie DANS L'ORDRE a l'interieur du groupe : la
# ou une edition en met trois et l'autre deux, les deux premiers se
# repondent et le troisieme reste seul. Ce qu'il doit rester.
def apparier_subs(io_blocs, autre_blocs):
    """{cle d'intertitre ido: cle d'intertitre de l'autre edition}"""
    def groupes(blocs):
        g, courant = {}, []
        for b in blocs:
            if b["tipo"] == "sub":
                courant.append(b["cle"])
            elif b["tipo"] == "p" and courant:
                # Les cles d'alinea portent leur tableau : deux groupes
                # de deux tableaux ne peuvent pas se confondre.
                g[b["cle"]] = courant
                courant = []
        return g

    ici, la = groupes(io_blocs), groupes(autre_blocs)
    lien = {}
    for alinea, subs_io in ici.items():
        subs_la = la.get(alinea, [])
        for i, cle in enumerate(subs_io):
            if i < len(subs_la):
                lien[cle] = subs_la[i]
    return lien


def paro():
    io = lire_langue("io")
    autres, liens = {}, {}
    for lg in LANGUES:
        sd = DOSSIER.get(lg["kodo"])
        if sd and (RACINE / "texto" / sd).is_dir():
            bl = lire_langue(sd)
            autres[lg["kodo"]] = {b["cle"]: b for b in bl}
            liens[lg["kodo"]] = apparier_subs(io, bl)
        else:
            autres[lg["kodo"]] = {}
            liens[lg["kodo"]] = {}

    # L'ORDRE EST CELUI DE L'IDO. C'est le livret ido qui est l'objet du
    # site ; la colonne de droite le suit.
    # Cote ido, la symetrie : un bloc ido sans vis-a-vis francais est
    # recolle au precedent LORS DU RENDU (voir plus bas), et non ici,
    # parce qu'il faut d'abord savoir lesquels sont orphelins.
    rangi = []
    for b in io:
        r = {"cle": b["cle"], "tipo": b["tipo"], "io": b["html"],
             "apelo": b.get("apelo", ""),
             "folio": b["folio"], "folio2": b.get("folio2", ""),
             "feuillet": b["feuillet"], "tra": {}}
        for lg in LANGUES:
            # L'intertitre se cherche par sa place, tout le reste par sa
            # cle. Sans vis-a-vis, la case de droite reste vide : c'est
            # une subdivision que l'autre edition n'a pas.
            cible = (liens[lg["kodo"]].get(b["cle"]) if b["tipo"] == "sub"
                     else b["cle"])
            o = autres[lg["kodo"]].get(cible) if cible else None
            if o:
                r["tra"][lg["kodo"]] = {"t": o["html"], "f": o["folio"],
                                        "f2": o.get("folio2", ""),
                                        "fe": o["feuillet"],
                                        "apelo": o.get("apelo", "")}
        rangi.append(r)

    # LE DECOUPAGE EN ALINEAS N'EST PAS LE MEME DES DEUX COTES, et il
    # faut en faire quelque chose. Rochelle coupe parfois en deux un
    # alinea que Guignon laisse d'un tenant, ou l'inverse : la cle
    # « t07-c1-05-2 » existe alors d'un seul cote. Rendue telle quelle,
    # elle fabrique un rang dont une colonne est vide, et l'oeil y lit
    # un manque -- alors que le texte, lui, est bien la, deux lignes
    # plus haut.
    #
    # LE PDF GARDE LE FAC-SIMILE ; LA PAGE DE LECTURE REGROUPE. Le
    # volume est une transcription diplomatique et doit le rester : la
    # coupure d'alinea y est celle de l'imprime. La page de lecture,
    # elle, sert a COMPARER deux textes, et une comparaison veut des
    # rangs qui se repondent. On recolle donc le bloc orphelin au
    # precedent de la meme langue, avec la marque du retour a la ligne
    # qu'il portait -- rien n'est perdu, rien n'est deplace, et les
    # deux colonnes redeviennent paralleles.
    par_cle = {r["cle"]: i for i, r in enumerate(rangi)}
    for lg in LANGUES:
        k = lg["kodo"]
        precedent = None
        for cle, o in autres[k].items():
            if cle in par_cle:
                precedent = par_cle[cle]
                continue
            if precedent is None:
                continue
            cible = rangi[precedent]["tra"].get(k)
            if cible is None:
                continue
            cible["t"] = (cible["t"] + ' <span class="nal"></span> '
                          + o["html"])
    return rangi


# LE FOLIO NE DONNE PAS LE NUMERO DE PAGE DU PDF, et la difference
# n'est pas une constante. Le PDF ne compose que les feuillets releves,
# et le livret ido en saute deux, vierges (48 et 76). Une soustraction
# fixe -- ce qu'on faisait quand seul le tableau 1 existait -- envoyait
# donc le lecteur deux pages trop loin dans tout le second tiers du
# volume. On numerote les feuillets composes dans l'ordre, une fois.
_RANGS = {}


def rang_pdf(langue, feuillet):
    sd = "io" if langue == "io" else DOSSIER.get(langue, langue)
    if sd not in _RANGS:
        table = {}
        for f in sorted((RACINE / "texto" / sd).glob("*.tex")):
            for m in PAGE.finditer(f.read_text(encoding="utf-8")):
                if m.group(1):
                    table[m.group(1)] = len(table) + 1
        _RANGS[sd] = table
    return _RANGS[sd].get(str(feuillet), 1)


def ancro(cle):
    return cle


def lier_notes(rangi):
    """Relie chaque appel de note, dans le texte, a sa note.

    LA NOTE N'EST PAS UN BLOC COMME UN AUTRE. Au bas d'une page du
    fac-simile elle a sa place naturelle ; dans une colonne qui defile,
    posee entre deux alineas, elle coupe la lecture — et l'appel, lui,
    ne mene nulle part. On la replie donc : l'appel devient un bouton,
    la note s'ouvre sous l'alinea qui la porte, comme dans la page du
    « Kompleta Gramatiko ».

    CHAQUE LANGUE A SES NOTES, et ce sont rarement les memes : le
    livret ido porte une note sur la latinisation des prenoms que le
    francais ignore, et Rochelle en a que Guignon n'a pas reprises. On
    relie donc colonne par colonne.

    L'APPARIEMENT SE FAIT PAR LA PAGE ET PAR LE MARQUEUR, les deux. Un
    « (1) » de note et un « (1) » de renvoi au tableau mural s'ecrivent
    pareil ; seule la page les distingue, puisque la note est au bas de
    la page ou son appel se trouve. Quand le marqueur parait plusieurs
    fois sur la meme page, on ne lie RIEN plutot que de lier au
    hasard : la fonction le dit, et l'oeil tranche.
    """
    rapport = {"lies": 0, "echecs": []}

    def relier(notes, lire_texte, ecrire_texte, page_de, langue):
        # PLUSIEURS NOTES SUR UNE MEME PAGE, TOUTES MARQUEES « (*) ».
        # Le folio 37 du livret ido en porte deux. Le marqueur ne les
        # distingue pas — mais l'ORDRE, si : le premier appel de la page
        # renvoie a la premiere note, le second a la seconde, et c'est
        # ainsi que le lecteur de 1926 les lisait. On compte donc, pour
        # chaque note, son rang parmi celles de sa page.
        # LE RANG SE COMPTE SUR LA PAGE ET LE MARQUEUR, rien de plus.
        # « page_de » sert a lire la page d'un RANG de la table, non
        # d'une note : pour la colonne de droite il va chercher
        # r["tra"], que les notes n'ont pas. Il figurait ici en tete de
        # « cle_page », dont seuls les deux derniers membres sont lus --
        # un appel mort, mais qui levait KeyError des qu'une note de
        # traduction se presentait. Aucune ne se presentait jamais,
        # faute de cle appariee ; la premiere l'a fait tomber.
        rang = {}
        for n in notes:
            cle_page = (n.get("feuillet"), n.get("apelo"))
            rang[id(n)] = rang.get(cle_page, 0)
            rang[cle_page] = rang.get(cle_page, 0) + 1
        for n in notes:
            marque = (n.get("apelo") or "").strip()
            if not marque:
                rapport["echecs"].append(
                    (langue, n["cle"], "?", "marqueur illisible en tete"))
                continue
            cible = re.escape(f"({marque})")
            # L'APPEL PEUT ETRE SUR LA PAGE D'AVANT. Un alinea a cheval
            # commence au verso et sa note tombe au bas du recto : le
            # releve fusionne les deux moities en un seul bloc, qui
            # porte alors le feuillet de sa PREMIERE page. On accepte
            # donc la page de la note et celle qui la precede.
            # SA PAGE D'ABORD, LA PRECEDENTE ENSUITE, et jamais les
            # deux ensemble. Chaque page a sa propre note et son propre
            # « (*) » : chercher sur deux pages a la fois rendait donc
            # deux appels pour une note, et l'outil renoncait a lier ce
            # qui n'etait pas ambigu du tout.
            try:
                f = int(n["feuillet"])
                essais = [{str(f)}, {str(f - 1)}]
            except (TypeError, ValueError):
                essais = [{n["feuillet"]}]
            cands, total = [], 0
            for pages in essais:
                cands = [r for r in rangi
                         # « apar » aussi : au tableau 8, l'appel est
                         # dans le titre meme de la scene, « La Rekolto
                         # (*) », qui tient sur la page d'ouverture.
                         if r["tipo"] in ("p", "sub", "apar")
                         and page_de(r) in pages
                         and lire_texte(r) is not None]
                total = sum(len(re.findall(cible, lire_texte(r)))
                            for r in cands)
                if total:
                    break
            vise = rang.get(id(n), 0)      # le rang de cette note-ci
            if total == 0 or vise >= total:
                rapport["echecs"].append(
                    (langue, n["cle"], marque,
                     "aucun appel sur la page" if total == 0
                     else f"{total} appels pour {vise + 1} notes"))
                continue
            vu = 0
            for r in cands:
                t = lire_texte(r)
                ici = len(re.findall(cible, t))
                if vu + ici <= vise:
                    vu += ici
                    continue
                # L'appel cherche est le (vise - vu)-ieme de ce bloc.
                saut = vise - vu
                if True:
                    compteur = [0]

                    def poser(m, saut=saut):
                        compteur[0] += 1
                        if compteur[0] - 1 != saut:
                            return m.group(0)
                        return (f'<button class="apel" '
                                f'data-noto="{langue}-{n["cle"]}" '
                                f'aria-expanded="false">({marque})</button>')
                    ecrire_texte(r, re.sub(cible, poser, t))
                    n["porte"] = r["cle"]
                    n["langue"] = langue
                    rapport["lies"] += 1
                    break

    # Colonne de gauche.
    relier([r for r in rangi if r["tipo"] == "noto"],
           lambda r: r["io"],
           lambda r, v: r.__setitem__("io", v),
           lambda r: r["feuillet"], "io")

    # Colonnes de droite : leurs notes ne sont pas dans `rangi`, elles
    # sont restees dans les blocs de traduction. On les en tire.
    for lg in LANGUES:
        k = lg["kodo"]
        notes = []
        for r in rangi:
            o = r["tra"].get(k)
            if o and o.get("apelo") and r["tipo"] == "noto":
                notes.append({"cle": r["cle"], "apelo": o["apelo"],
                              "feuillet": o["fe"], "html": o["t"]})
        relier(notes,
               lambda r, k=k: (r["tra"].get(k) or {}).get("t"),
               lambda r, v, k=k: r["tra"][k].__setitem__("t", v),
               lambda r, k=k: (r["tra"].get(k) or {}).get("fe"), k)

    return rapport


# LES LIGNES D'APPARAT, ET LA MEME LISTE POUR TOUT LE MONDE.
# \VUcentre et \VUtitre portent « ln », \VUpk porte « pk » : les trois
# composent une LIGNE du fac-simile. Deux endroits les relisent -- la
# table des matieres, qui en tire ses entrees, et l'ancrage, qui pose un
# « -lN » sur chacune -- et il faut qu'ils comptent LES MEMES, sinon les
# renvois de la table tombent a cote de la ligne annoncee. D'ou une
# seule liste de classes, lue par les deux.
CLASSE_AP = r'ln[^"]*|pk'
ATTRS_AP = r'(?: [a-z-]+="[^"]*")*'
LIGNE_AP = re.compile(
    rf'<span class="(?:{CLASSE_AP})"({ATTRS_AP})>(.*?)</span>', re.S)
OUVRE_AP = re.compile(rf'<span class="({CLASSE_AP})"({ATTRS_AP})>')
KORPO = re.compile(r'data-korpo="([^"]*)"')


def net_tdm(x):
    """Le texte nu d'une ligne, pour la table des matieres."""
    # L'appel de note est un bouton dans la page ; dans la table il ne
    # mene nulle part. On l'ote, et on recoud : « La Rekolto (*). » sans
    # son marqueur laisserait « La Rekolto . ».
    x = re.sub(r'<button class="apel".*?</button>', "", x, flags=re.S)
    x = re.sub(r"<[^>]+>", "", x)
    x = re.sub(r"\s+", " ", x)
    return re.sub(r" +([.,;:])", r"\1", x).strip()


def est_ceno(x):
    """Un marqueur de scene -- « Unesma ceno. », « Duesma ceno. »."""
    # LE FAC-SIMILE LES COMPOSE EN ITALIQUE, et c'est a cela qu'on les
    # reconnait : le mot, lui, change d'une langue a l'autre. On accepte
    # la ligne nue comme la ligne encore dans son span.
    x = re.sub(rf'^\s*<span class="(?:{CLASSE_AP})"{ATTRS_AP}>', "", x)
    return bool(re.match(r"\s*<i>", x))


# LA SERIE. Le livre en a trois, et le fac-simile l'annonce en tete du
# tableau qui l'ouvre : « UNESMA SERIO » au 1, « DUESMA SERIO » au 7,
# « TRIESMA SERIO » au 11. Le volet n'en portait qu'une, ecrite en dur
# dans le gabarit, de sorte que les seize tableaux paraissaient tous
# sous la premiere serie.
SERIO = re.compile(r"\b(UNESMA|DUESMA|TRIESMA|QUARESMA)\s+SERIO\b", re.I)


def korpo_de(attrs):
    """Le corps de caractere d'une ligne d'apparat, ou rien."""
    m = KORPO.search(attrs)
    return m.group(1) if m else ""


def rendre(rangi):
    # La table des matieres se tire des blocs de titre.
    # LA TABLE DES MATIERES A TROIS RANGS, parce que le livre en a
    # trois : le tableau, la scene, l'intertitre. Les tableaux a
    # plusieurs parties -- 3, 4, 7, 8, 9... -- portent « Unesma ceno »
    # et « Duesma ceno », composes en italique et non en petites
    # capitales ; c'est ce qui les distingue, et c'est au fac-simile
    # qu'on le lit, pas a la logique.
    def texte_de(r):
        return r["io"] or next(iter(r["tra"].values()), {}).get("t", "")

    tdm = []
    # LE LIBELLE COURT DE CHAQUE OUVERTURE DE TABLEAU. La recherche
    # masque tout ce qui ne repond pas, y compris les titres ; mais un
    # resultat sans son tableau ne se situe pas, et l'ouverture entiere
    # ferait quatre lignes d'apparat au-dessus de deux alineas. On garde
    # donc ici le numero et le titre, deja calcules pour la table, et la
    # page s'en sert comme titre courant de ses resultats.
    tetes = {}
    # Un intertitre repris en titre de tableau ne s'annonce pas deux fois
    # (voir plus bas).
    empruntes = set()
    net = net_tdm
    for idx, r in enumerate(rangi):
        if r["tipo"] not in ("sub", "apar"):
            continue
        brut = texte_de(r)
        paires = [(m.group(2), korpo_de(m.group(1)))
                  for m in LIGNE_AP.finditer(brut)]
        lignes_ap = [texte for texte, _ in paires]
        corps = [c for _, c in paires]

        if r["tipo"] == "apar":
            i = next((k for k, l in enumerate(lignes_ap)
                      if "TABELO" in l or "TABLEAU" in l), None)
            if i is None:
                # PAS UNE OUVERTURE DE TABLEAU, DONC PAS UNE ENTREE.
                # Trois blocs d'apparat tombent en cours de tableau : la
                # note de l'editeur sur les tableaux 3 et 4, le
                # « (Videz la plano.) » du tableau 5, l'alinea de
                # liaison du tableau 6. Ce sont des indications de
                # lecture, non des titres, et la table les annoncait au
                # rang des tableaux -- « (La 3 - ma e 4 - ma tabeli esas
                # tale kombinita ke li prizent ». La branche d'origine
                # visait la couverture et la dedicace ; mais celles-la
                # ne parviennent jamais ici, puisque lire_langue ecarte
                # « 00- » et « 90- ». Elle ne ramassait plus que ces
                # trois-la.
                continue
            num = net(lignes_ap[i])
            # LE TITRE NE SUIT PAS TOUJOURS LE NUMERO. Les tableaux a
            # plusieurs scenes glissent « Unesma ceno. » entre les deux :
            # on passe les marqueurs de scene. Et ce n'est pas non plus
            # la DERNIERE ligne du bloc -- au tableau 2 la derniere est
            # « (Simpla leciono pri naturcienco.) », le sous-titre d'une
            # lecon, sous lequel la table annoncait tout le tableau.
            ti = next((k for k in range(i + 1, len(lignes_ap))
                       if net(lignes_ap[k]) and not est_ceno(lignes_ap[k])),
                      None)
            # UN TITRE PEUT TENIR SUR PLUSIEURS LIGNES, et c'est le CORPS
            # qui le dit : les lignes de meme corps que la premiere sont
            # la suite du meme titre, une ligne d'un autre corps commence
            # autre chose. Le titre du tableau 6 tient sur deux lignes de
            # 11.4pt, celui du 13 sur deux de 10.2pt, celui du 16 sur
            # deux de 13.2pt ; la table coupait apres la premiere et
            # annoncait « la Lumizado. », « La Kafeerio. », « La Ludili. »
            # comme des sections a part -- en italique, au rang des
            # scenes, alors qu'elles achevent le titre du tableau.
            suites = []
            if ti is not None:
                for k in range(ti + 1, len(lignes_ap)):
                    if not net(lignes_ap[k]):
                        continue
                    if corps[k] != corps[ti] or est_ceno(lignes_ap[k]):
                        break
                    suites.append(k)
            titre = " ".join([net(lignes_ap[ti])] +
                             [net(lignes_ap[k]) for k in suites]) \
                if ti is not None else ""
            if not titre:
                # LE TITRE EST PARFOIS HORS DU BLOC D'OUVERTURE. Aux
                # tableaux 7, 9, 10, 14 et 15, le fac-simile ido ne met
                # sous le numero qu'un blanc, et le titre ouvre le
                # premier intertitre qui suit -- la ou le volume
                # francais, lui, le garde dans l'ouverture. La table
                # annoncait donc ces cinq tableaux sous leur seul
                # numero, « TABELO No 10 » et rien de plus. On va le
                # chercher au premier intertitre qui n'est pas une
                # scene, sans franchir le tableau suivant.
                for q in rangi[idx + 1:]:
                    if q["tipo"] == "apar":
                        break
                    if q["tipo"] != "sub":
                        continue
                    suite = texte_de(q)
                    if est_ceno(suite):
                        continue
                    titre = net(suite)
                    # ET IL NE S'ANNONCE PAS DEUX FOIS. Emprunte au
                    # premier intertitre, le titre reparaissait juste
                    # au-dessous en sous-entree : le volet lisait
                    # « TABELO No 10 La Maro. --- La Portuo. » puis
                    # « La Maro. --- La Portuo. ».
                    empruntes.add(q["cle"])
                    break
            # La serie s'annonce avant le tableau qui l'ouvre.
            serie = next((SERIO.search(net(l)) for l in lignes_ap[:i]
                          if SERIO.search(net(l))), None)
            if serie:
                tdm.append((None, serie.group(0).capitalize(), "parto"))
            tdm.append((r["cle"], f"<b>{num}</b> {titre}".strip(), "tt"))
            # Le point median, comme dans la ligne d'auteur de la page :
            # les titres portent deja des tirets cadratins, et un tiret
            # de plus ne se distinguerait pas d'eux.
            tetes[r["cle"]] = f"{num} · {titre}" if titre else num
            # Ce qui reste du bloc -- scene, intertitre -- vaut une
            # entree a soi. Le titre en est ote : il est deja annonce
            # au-dessus. Ce qui PRECEDE le numero ne compte pas : c'est
            # l'apparat de serie, « EXPLIKO - LIBRETO », « UNESMA SERIO ».
            for j in range(i + 1, len(lignes_ap)):
                if j != ti and j not in suites and net(lignes_ap[j]):
                    tdm.append((f'{r["cle"]}-l{j}', net(lignes_ap[j]), "sc"))
            continue

        # Un intertitre : scene si sa premiere ligne est en italique.
        if r["cle"] in empruntes:
            continue
        tdm.append((r["cle"], net(brut), "sc" if est_ceno(brut) else "st"))

    lignes = []
    for r in rangi:
        cl = ["r", r["tipo"]]
        io = r["io"]
        att = f' id="{ancro(r["cle"])}" data-cle="{r["cle"]}"'
        if r["cle"] in tetes:
            tete = (tetes[r["cle"]].replace("&", "&amp;")
                    .replace('"', "&quot;").replace("<", "&lt;"))
            att += f' data-tete="{tete}"'
        fol = ""
        if r["folio"]:
            pg = rang_pdf("io", r["feuillet"])
            fol = (f'<a class="fol" href="tabeli.pdf#page={pg}" '
                   f'title="Folio {r["folio"]} en la PDF">{r["folio"]}</a>')
        # Les lignes d'apparat recoivent une ancre chacune : la table
        # des matieres renvoie a la scene, pas seulement au tableau.
        if r["tipo"] == "apar":
            n = [0]

            def ancrer(m):
                n[0] += 1
                # Les attributs de la ligne sont recopies : data-korpo
                # doit survivre a l'ancrage.
                return (f'<span id="{r["cle"]}-l{n[0]-1}" '
                        f'class="{m.group(1)}"{m.group(2)}>')
            # OUVRE_AP, et non « ln » seul : la table compte aussi les
            # lignes « pk », et les deux numerotations doivent coincider.
            io = OUVRE_AP.sub(ancrer, io)
        cel_io = f'<div class="k io">{fol}{io}</div>' if io else \
                 '<div class="k io vaka"></div>'
        cel = [cel_io]
        for lg in LANGUES:
            o = r["tra"].get(lg["kodo"])
            if o:
                f2 = ""
                if o["f"]:
                    pg2 = rang_pdf(lg["kodo"], o["fe"])
                    f2 = (f'<a class="fol fd" href="tableaux.pdf#page={pg2}" '
                          f'title="Folio {o["f"]} dans le PDF">{o["f"]}</a>')
                cel.append(f'<div class="k tra" data-lg="{lg["kodo"]}">'
                           f'{f2}{o["t"]}</div>')
            else:
                cel.append(f'<div class="k tra vaka" data-lg="{lg["kodo"]}">'
                           f'</div>')
        if r["tipo"] == "noto":
            # La note se rend a part : elle n'est pas un rang a deux
            # colonnes mais un depli attache a l'alinea qui l'appelle.
            # UNE NOTE PAR LANGUE, et l'identifiant porte la langue :
            # le bouton d'appel est pose dans une colonne, il doit
            # ouvrir la note de CETTE colonne. Sans la langue dans
            # l'identifiant, le bouton francais ouvrait la note ido —
            # ou, plus souvent, n'ouvrait rien du tout.
            for k, txt in [("io", r["io"])] + [
                    (lg["kodo"], (r["tra"].get(lg["kodo"]) or {}).get("t"))
                    for lg in LANGUES]:
                if txt:
                    lignes.append(
                        f'<div class="noto" id="noto-{k}-{r["cle"]}" '
                        f'data-lg="{k}" hidden>{txt}</div>')
            continue
        lignes.append(f'<div class="{" ".join(cl)}"{att}>' +
                      "".join(cel) + "</div>")

    nav = "".join(
        f'<div class="parto">{t}</div>' if k == "parto"
        else f'<a href="#{c}" data-ch="{c}" class="{k}">{t}</a>'
        for c, t, k in tdm)
    opcioni = "".join(
        f'<option value="{lg["kodo"]}">{lg["nomo"]}</option>'
        for lg in LANGUES)

    gabarito = (RACINE / "outils" / "gabarito.html").read_text(encoding="utf-8")
    page = (gabarito
            .replace("{{TITRO}}", TITRO)
            .replace("{{SUBTITRO}}", SUBTITRO)
            .replace("{{NAV}}", nav)
            .replace("{{LINGUI}}", opcioni)
            .replace("{{KONTENO}}", "\n".join(lignes))
            .replace("{{LINGUIJSON}}", json.dumps(LANGUES, ensure_ascii=False)))
    (RACINE / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html ecrit : {len(rangi)} bloki, "
          f"{sum(1 for r in rangi if r['tipo'] == 'p')} alinei")


if __name__ == "__main__":
    r = paro()
    rap = lier_notes(r)
    rendre(r)
    print(f"  notes reliees a leur appel : {rap['lies']}")
    for langue, cle, marque, pourquoi in rap["echecs"]:
        print(f"  NON RELIEE [{langue}] {cle} « ({marque}) » : {pourquoi}")
