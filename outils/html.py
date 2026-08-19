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


# LE TABLEAU MURAL AU-DESSUS DE SON TEXTE. Le livret explique une
# gravure que le lecteur n'a pas sous les yeux ; la page la lui donne.
# Le catalogue est ecrit par outils/gravuri.py, qui prepare les images :
# il porte les dimensions, et c'est par elles que la page reserve la
# place avant meme le chargement -- sans quoi le texte sursaute quand
# l'image arrive.
def gravuri():
    cat = RACINE / "gravuri" / "gravuri.json"
    return json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}


# LE RENVOI QUE LA PLANCHE NE PORTE PAS. gravuri/korekti.json dit,
# tableau par tableau, quel renvoi lire a la place de quel autre : au
# tableau 5, « les plates-bandes (150) » sont gravees « 50 ». La source
# ne bouge pas ; c'est la page de lecture qui montre le bon numero.
_KOREKTI = None


def korekti(tab):
    """Les renvois a corriger pour ce tableau : {lu: a lire}."""
    global _KOREKTI
    if _KOREKTI is None:
        f = RACINE / "gravuri" / "korekti.json"
        _KOREKTI = (json.loads(f.read_text(encoding="utf-8"))
                    if f.exists() else {})
    return _KOREKTI.get(tab, {})


def nomo(nm, langue):
    """Le nom de l'objet DANS LA LANGUE DE LA COLONNE.

    Le gros plan porte le nom de ce qu'il montre, et ce nom se lit dans
    la langue du texte qui l'a appele : « fumeyo » a gauche, « fumoir »
    au milieu, « smoking room » a droite. Les 1693 objets ne sont pas
    tous nommes dans les trois -- il faut que le substantif soit en
    gras devant le renvoi, et une edition l'oublie parfois -- d'ou le
    repli, dans l'ordre : sa langue, l'ido, le francais.
    """
    for k in (langue, "io", "fr", "en"):
        v = nm.get(k)
        if v:
            return v[0]
    return ""


def numeri():
    """{tabelo: {numero: (cle de gravure, x, y, l, h, noms)}}.

    Les positions sont en FRACTION de la planche : la page sert la meme
    gravure a trois definitions, et le gros plan doit tomber juste sur
    chacune. Le nom vient du releve des substantifs en gras.
    """
    f = RACINE / "gravuri" / "numeri.json"
    if not f.exists():
        return {}
    o = RACINE / "gravuri" / "objekti.json"
    noms = json.loads(o.read_text(encoding="utf-8")) if o.exists() else {}
    out, force = {}, {}
    for cle, v in json.loads(f.read_text(encoding="utf-8")).items():
        tab = cle[:3]
        for n, b in v["numeri"].items():
            # UN TABLEAU PEUT AVOIR DEUX PLANCHES — le 5 en a deux, le
            # 12 aussi — et le meme numero peut alors etre lu sur les
            # deux. On garde la lecture la mieux etayee, non la
            # derniere venue.
            if force.get((tab, n), -1) >= b[4]:
                continue
            force[(tab, n)] = b[4]
            out.setdefault(tab, {})[n] = (
                cle, b[0], b[1], b[2], b[3],
                noms.get(tab, {}).get(n, {}))
    return out


# LE RENVOI QUI SAIT OU IL POINTE DEVIENT UN BOUTON. Les autres restent
# du texte : on ne promet pas un gros plan qu'on ne saurait pas montrer.
# « 94 bis » N'EST PAS 94. Le graveur du tableau 5 a ajoute deux outils
# apres coup et les a glisses entre les autres plutot que de renumeroter
# la planche : le ciseau porte « 94bis », le maillet « 95bis ». Le
# renvoi garde le mot -- en italique du cote francais, nu du cote ido --
# et le bouton vise l'objet a part, non son voisin.
RENVOI_REND = re.compile(
    r'<sup>(\(?)\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)'
    r'(\s*(?:<i>)?bis(?:</i>)?)?\s*(\)?)</sup>')

# Les langues de la colonne de droite. « fr » est le texte source
# (releve sur le fac-simile) ; les autres sont des traductions, et
# portent la mention qui convient.
#
# « differita » : LA TRADUCTION NE VOYAGE PAS AVEC LA PAGE. Le francais
# est un fac-simile transcrit, il fait partie de l'objet ; l'anglais
# n'est qu'une commodite de lecture. index.html pese deja 1,4 Mo pour
# ses deux colonnes, et coudre une troisieme langue dedans le ferait
# grossir d'autant pour un lecteur qui, neuf fois sur dix, ne la
# demandera pas. Les langues marquees ici sortent donc dans un fichier
# a part, lingui/<kodo>.json, et le navigateur ne va le chercher qu'au
# moment ou l'on choisit la langue dans le menu. La page, elle, garde
# les cases vides a leur place -- ce qui arrive n'a plus qu'a s'y
# verser.
LANGUES = [
    {"kodo": "fr", "nomo": "Français", "dir": "ltr", "fonto": "fac-similé"},
    {"kodo": "en", "nomo": "English", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
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

    # LE TRAIT D'UNION N'A PAS D'ESPACES. Les titres du livret ido sont
    # composes en interlettrage, et l'imprimeur y a fait respirer le
    # trait d'union comme le reste : « EXPLIKO - LIBRETO »,
    # « Matur - evo ed oldeso. », « la Delmas - tabeli », « la 3 - ma ».
    # Ces espaces tiennent a la composition, non au mot ; a l'ecran, ou
    # rien n'est interlettre, ils coupent le mot en deux. Le fac-simile
    # francais n'en porte aucun. Le tiret cadratin, qui separe vraiment,
    # s'ecrit « --- » dans le releve et sort deja en « — » : ni lui ni
    # le tiret court d'un intervalle ne sont touches.
    t = re.sub(r"(?<=[^\s\u2013\u2014-]) - (?=[^\s\u2013\u2014-])", "-", t)

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
DOSSIER = {"fr": "fr", "en": "en"}   # langue -> sous-dossier de texto/


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
    #
    # UN INTERTITRE APPARIE PAR SA PLACE N'EST PAS ORPHELIN. Ce
    # recollage juge sur la CLE, et les intertitres, eux, s'apparient sur
    # leur place : un intertitre de traduction dont la cle ne figure pas
    # cote ido tient pourtant deja sa case, en face de celui qu'il
    # traduit. Compte pour orphelin, il paraissait DEUX fois -- « Deuxième
    # scène. » a son rang, et recolle a la fin de l'alinea precedent.
    par_cle = {r["cle"]: i for i, r in enumerate(rangi)}
    for lg in LANGUES:
        k = lg["kodo"]
        pris = {tra: io for io, tra in liens[k].items()}
        precedent = None
        for cle, o in autres[k].items():
            if cle in par_cle:
                precedent = par_cle[cle]
                continue
            if cle in pris:
                # Il a sa case : c'est desormais lui, le precedent.
                precedent = par_cle.get(pris[cle], precedent)
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


# CE QUI PRECEDE UN CHIFFRE ENTRE PARENTHESES EN DIT LA NATURE. Le
# liminaire francais pose lui-meme la regle : « Nous avons imprime en
# caracteres gras les substantifs qui se trouvent dans le vocabulaire
# des Tableaux EN LES FAISANT SUIVRE DE LEUR NUMERO. » Un numero
# d'objet suit donc toujours un substantif en gras -- « la
# \VUgras{fumee}\textsuperscript{(1)} » -- tandis que l'appel de note
# suit du texte ordinaire : « qui nous fut servi \textsuperscript{(1)} ».
# L'exposant, lui, ne tranche rien : les deux volumes composent tantot
# l'un tantot l'autre en exposant.
AVANT_OBJET = re.compile(r'</b>\s*(?:<sup>\s*)?$')


def appels_note(texte, marque):
    """Positions des appels de note « (marque) » dans un bloc.

    Ecarte les renvois au tableau mural, reconnus a leur substantif en
    gras. Rend des couples (debut, fin) sur le texte donne.
    """
    if not texte:
        return []
    # UNE ASTERISQUE N'EST JAMAIS UN NUMERO D'OBJET : quand la note est
    # marquee « (*) », rien n'est a departager, et le gras ne prouve
    # rien. Le tableau 1 ido pose justement son appel apres un
    # substantif en gras — « esas \VUgras{Henrikus} (*) » — parce que la
    # note porte sur ce mot-la. La regle du gras ne vaut que pour les
    # marques chiffrees, les seules que les deux emplois partagent.
    chiffree = marque.isdigit()
    out = []
    for m in re.finditer(re.escape(f"({marque})"), texte):
        if chiffree and AVANT_OBJET.search(texte[:m.start()]):
            continue
        out.append((m.start(), m.end()))
    return out


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
        # UNE TRADUCTION N'A PAS DE PAGES. Le francais et l'ido sont des
        # fac-similes transcrits : chaque bloc sait de quel feuillet il
        # vient, et c'est le feuillet qui rapproche une note de son
        # appel. L'anglais, lui, ne transcrit rien -- il n'a ni page ni
        # feuillet, et tous ses blocs portaient donc la meme page vide :
        # les onze notes se cherchaient un appel dans le livre entier,
        # et se le disputaient. LE TABLEAU REMPLACE ALORS LA PAGE. Il
        # est plus large qu'un feuillet, mais il suffit : aucun tableau
        # ne porte plus de deux notes, et le comptage des rangs, qui
        # departageait deja deux notes d'une meme page, les departage
        # de meme.
        def zono(n):
            return (n.get("feuillet") or "").strip() or n["cle"][:3]

        rang = {}
        for n in notes:
            cle_page = (zono(n), n.get("apelo"))
            rang[id(n)] = rang.get(cle_page, 0)
            rang[cle_page] = rang.get(cle_page, 0) + 1
        for n in notes:
            marque = (n.get("apelo") or "").strip()
            if not marque:
                rapport["echecs"].append(
                    (langue, n["cle"], "?", "marqueur illisible en tete"))
                continue
            # UN « (1) » DE NOTE ET UN « (1) » D'OBJET S'ECRIVENT
            # PAREIL. Rochelle marque ses notes du meme signe que ses
            # numeros d'objets, qui vont jusqu'a 150 par planche. Au
            # tableau 13, l'alinea « au deuxieme etage (1), ou j'ai tres
            # bien dormi (1) » porte les deux, et on liait le premier :
            # le bouton s'ouvrait sur l'etage. C'est le gras qui les
            # separe (voir appels_note).
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
            reperer = page_de
            try:
                f = int(n["feuillet"])
                essais = [{str(f)}, {str(f - 1)}]
            except (TypeError, ValueError):
                essais = [{zono(n)}]
                reperer = lambda r: r["cle"][:3]
            cands, total = [], 0
            for pages in essais:
                cands = [r for r in rangi
                         # « apar » aussi : au tableau 8, l'appel est
                         # dans le titre meme de la scene, « La Rekolto
                         # (*) », qui tient sur la page d'ouverture.
                         if r["tipo"] in ("p", "sub", "apar")
                         and reperer(r) in pages
                         and lire_texte(r) is not None]
                total = sum(len(appels_note(lire_texte(r), marque))
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
                places = appels_note(t, marque)
                if vu + len(places) <= vise:
                    vu += len(places)
                    continue
                # L'appel cherche est le (vise - vu)-ieme de ce bloc.
                a, b = places[vise - vu]
                # UN SEUL SIGNE POUR TOUTES LES NOTES. Guignon marque
                # les siennes « (*) », Rochelle « (1) ». Garder a chacun
                # sa marque, c'etait donner deux signes differents a la
                # meme note en regard, et surtout reprendre en francais
                # le signe des renvois au tableau mural. La page de
                # lecture marque donc toutes les notes « (*) », le signe
                # que l'ido employait deja partout ; les PDF, eux,
                # gardent ce que chaque atelier a compose.
                bouton = (f'<button class="apel" '
                          f'data-noto="{langue}-{n["cle"]}" '
                          f'aria-expanded="false">(*)</button>')
                ecrire_texte(r, t[:a] + bouton + t[b:])
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

    uniformiser_notes(rangi)
    uniformiser_renvois(rangi)
    rapport["fermes"] = fermer_renvois(rangi)
    rapport["korektiti"] = korekti_teksto(rangi)
    boutons_renvois(rangi)
    boutons_literi(rangi)
    return rapport


# LE RENVOI AU TABLEAU MURAL, TOUJOURS COMPOSE DE LA MEME FACON.
# On prend le numero avec ce qui le porte -- l'exposant s'il en a un --
# et le blanc qui le precede s'il y en a un.
# TROIS FORMES DE RENVOI, et il a fallu les trois : la forme
# ordinaire, le GROUPE — « les tableaux muraux (9, 11, 12) », qui
# vaut pour trois objets a la fois et dont on ne lisait aucun — et
# « 41) », ou la parenthese ouvrante manque, en trois endroits des
# deux livrets. On garde les parentheses TELLES QU'ON LES A
# RELEVEES : dire si ce 41) vient d'une coquille du releve ou d'une
# sorte cassee de l'imprimeur demanderait le fac-simile sous les
# yeux. On uniformise l'exposant et le blanc, rien d'autre.
RENVOI = re.compile(
    r'(\s*)'
    r'(?:<sup>\s*(\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*\)?)\s*</sup>'
    r'|\((\d{1,3}(?:\s*,\s*\d{1,3})*)\))')


def boutons_renvois(rangi):
    """Le renvoi devient un bouton quand on sait ou il pointe.

    UN GROS PLAN QU'ON NE SAURAIT PAS MONTRER NE SE PROMET PAS. La
    lecture des numeros sur les planches est partielle -- la reserve de
    blanc qui porte le chiffre se referme des que la gravure est dense,
    et le chiffre se perd dans les hachures. Les renvois dont la
    position est connue prennent donc un bouton ; les autres restent du
    texte ordinaire, exactement comme ils etaient. Rien ne bouge dans la
    ligne : le bouton garde le corps et l'exposant du renvoi.

    Le bouton porte la CLE DE LA GRAVURE et le cadre en fractions de
    celle-ci. La page n'a plus qu'a recadrer l'image qu'elle a deja.
    """
    num = numeri()
    if not num:
        return 0
    pose = 0
    for r in rangi:
        tab = r["cle"][:3]
        par = num.get(tab)
        if not par:
            continue
        # LA SCENE DU BLOC DECIDE DE QUEL NUMERO IL S'AGIT. Six planches
        # portent plusieurs vignettes, et chacune recommence a 1 : le
        # « (39) » d'un bloc t06-c3 ne montre pas le meme objet que
        # celui d'un bloc t06-c1. La cle du bloc le dit.
        ms = re.match(r't\d\d-(c\d)-', r["cle"])
        scene = ms.group(1) if ms else ""
        # Le renvoi que la planche ne porte pas : au tableau 5 le
        # « (150) » des plates-bandes, gravees « 50 ». On lit la
        # correction, on la montre, et la source ne bouge pas.
        kor = korekti(tab)

        def ouvrir(n, langue, nu):
            """Le debut du bouton d'un numero, ou None si l'on ignore
            ou il se trouve : on ne promet pas un gros plan qu'on ne
            saurait pas montrer."""
            v = par.get(f"{scene}:{n}" if scene else str(n))
            if not v:
                return None
            cle, x, y, w, h, nm = v
            # LE NOM SUIT SA COLONNE (voir nomo, plus haut).
            titre = nomo(nm, langue).replace('"', "&quot;")
            return (f'<button class="lupo{chr(32) + "nuda" if nu else ""}" '
                    f'data-g="{cle}" data-c="{x},{y},{w},{h}" data-n="{n}" '
                    f'title="{titre}" aria-expanded="false">')

        def bouton(m, par=par, langue="io", scene=scene):
            nonlocal pose
            ouv, corps, bis, fer = (m.group(1), m.group(2),
                                    m.group(3) or "", m.group(4))
            ns = [int(kor.get(x, x)) for x in re.findall(r"\d+", corps)]
            # UN GROUPE VAUT POUR PLUSIEURS OBJETS A LA FOIS. Chaque
            # numero y devient cliquable separement ; les parentheses et
            # les virgules restent du texte, et rien ne bouge dans la
            # ligne.
            if len(ns) > 1:
                bouts, fait = [], 0
                for n in ns:
                    d = ouvrir(n, langue, True)
                    bouts.append(f"{d}{n}</button>" if d else str(n))
                    fait += 1 if d else 0
                if not fait:
                    return m.group(0)
                pose += fait
                return f"<sup>{ouv}" + ", ".join(bouts) + f"{bis}{fer}</sup>"
            d = ouvrir(f"{ns[0]}bis" if bis else ns[0], langue, False)
            if not d:
                return m.group(0)
            pose += 1
            return f"{d}<sup>{ouv}{ns[0]}{bis}{fer}</sup></button>"

        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            texte = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not texte:
                continue
            neuf = RENVOI_REND.sub(
                lambda m, k=k: bouton(m, langue=k), texte)
            if neuf == texte:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return pose


# -------------------------------------------------------------------
#  LES RENVOIS A LETTRE
# -------------------------------------------------------------------
#  Trois tableaux ne se contentent pas de numeros. « Ni vidas sur la
#  tabelo la precipua figuri geometriala : rondo (a), quadrato (b) » —
#  ces lettres sont gravees SUR le tableau noir, qui porte lui-meme le
#  numero 1, et n'ont de sens que rapportees a lui : le « a » du tableau
#  noir est un cercle, celui de la carte l'Amerique, celui du tableau de
#  sciences naturelles un cheval.
#
#  gravuri/literi.json dit, bloc par bloc, de quel objet les lettres
#  dependent — cela ne se devine pas, le texte ne le disant pas toujours
#  — et ou chacune se trouve sur la planche.
# LE RENVOI A LETTRE SE COMPOSE EN ITALIQUE DU COTE FRANCAIS, et nu du
# cote ido. Sans cette italique dans le motif, les six lettres du
# tableau d'astronomie n'etaient cliquables qu'en ido : le lecteur du
# francais lisait « les hemispheres (d) » sans rien pouvoir en voir.
RENVOI_LIT = re.compile(r'<sup>(<i>)?\(([a-z]{1,2})\)(</i>)?</sup>')


def literi():
    """{planche: {cle: place}} et la table des blocs."""
    f = RACINE / "gravuri" / "literi.json"
    if not f.exists():
        return {}, {}
    d = json.loads(f.read_text(encoding="utf-8"))
    return d, d.get("patri", {})


# UN SEUL SORT POUR DEUX SIGNES. Au tableau 5, la salle de bains porte
# un renvoi compose « (1) » — dans les deux livrets. Ce n'est pas le
# numero 1, qui est la facade de la maison : c'est la LETTRE l, et le
# plan le dit lui-meme, sa legende portant « l. Balneyo » entre le k des
# enfants et le m du palier. Dans cette fonte le l bas de casse et le
# chiffre 1 ont le meme dessin, et la casse du compositeur n'avait
# peut-etre que l'un des deux : rien sur la page ne les separe.
#
# LA SOURCE NE BOUGE PAS — les deux PDF restent le fac-simile — mais la
# page de lecture, elle, n'a pas a repeter une ambiguite que le plan
# leve. On y lit donc « (l) », et le gros plan montre la salle de
# bains. C'est le seul endroit du livre ou la page de lecture corrige
# ce que la transcription conserve, et c'est pourquoi il se declare
# dans literi.json plutot que de se deviner.
BOUTON_UN = re.compile(
    r'<button class="lupo" data-g="[^"]*" data-c="[^"]*" data-n="1" '
    r'title="[^"]*" aria-expanded="false"><sup>\(1\)</sup></button>')


def sorto_unika(t, regles, planche, places, noms, langue):
    """Redirige vers sa lettre le « (1) » qui n'est pas un numero."""
    for mot, L in regles:
        i = t.find(f"{mot}</b>")
        v = places.get(L)
        if i < 0 or not v:
            continue
        m = BOUTON_UN.search(t, i, i + 400)
        if not m:
            continue
        nm = noms.get(planche[:3], {}).get(L, {})
        io = (nm.get("io") or nm.get("fr") or [""])[0]
        fr = (nm.get("fr") or nm.get("io") or [""])[0]
        titre = ((io if langue == "io" else fr) or io or fr)
        t = t[:m.start()] + (
            f'<button class="lupo" data-g="{planche}" '
            f'data-c="{v[0]},{v[1]},{v[2]},{v[3]}" data-n="{L}" '
            f'title="{titre.replace(chr(34), "&quot;")}" '
            f'aria-expanded="false"><sup>({L})</sup></button>'
        ) + t[m.end():]
    return t


def boutons_literi(rangi):
    """Le renvoi a lettre devient un bouton, comme le renvoi a numero."""
    tout, patri = literi()
    if not patri:
        return 0
    uniq = tout.get("unu-sorto", {})
    o = RACINE / "gravuri" / "objekti.json"
    noms = json.loads(o.read_text(encoding="utf-8")) if o.exists() else {}
    pose = 0
    for r in rangi:
        pa = patri.get(r["cle"])
        if not pa:
            continue
        planche, prefixo = pa
        places = tout.get(planche, {})

        def bouton(m, langue="io"):
            nonlocal pose
            bouts, fait = [], 0
            ita = "<i>" if m.group(1) else ""
            for L in m.group(2):
                v = places.get(prefixo + L)
                if not v:
                    bouts.append(L)
                    continue
                nm = noms.get(planche[:3], {}).get(prefixo + L, {})
                titre = nomo(nm, langue).replace('"', "&quot;")
                bouts.append(
                    f'<button class="lupo nuda" data-g="{planche}" '
                    f'data-c="{v[0]},{v[1]},{v[2]},{v[3]}" data-n="{L}" '
                    f'title="{titre}" aria-expanded="false">{L}</button>')
                fait += 1
            if not fait:
                return m.group(0)
            pose += fait
            return (f"<sup>{ita}(" + "".join(bouts)
                    + ")" + ("</i>" if ita else "") + "</sup>")

        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = RENVOI_LIT.sub(lambda m, k=k: bouton(m, k), t)
            if uniq.get(r["cle"]):
                neuf = sorto_unika(neuf, uniq[r["cle"]], planche,
                                   places, noms, k)
            if neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return pose


def uniformiser_renvois(rangi):
    """Une seule facon d'ecrire « mot (N) », sur toute la page.

    Les deux ateliers hesitent : 2884 renvois sont separes du substantif
    par un blanc, 478 lui sont colles, et sept — tous ido — ne sont meme
    pas en exposant. Rien ne distingue ces cas : c'est du flottement de
    composition. La page de lecture les ecrit donc tous pareil, exposant
    et blanc.

    LE BLANC EST INSECABLE. Un renvoi rejeté seul en tete de ligne ne
    veut plus rien dire ; en colonne etroite, sur telephone, cela
    arrivait. Le numero reste desormais accroche a son substantif.

    Tous les nombres entre parentheses du texte suivi sont des renvois :
    ils vont de 1 a 150, et les appels de note portent « (*) ».
    """
    n = 0

    def poser(m):
        # Un renvoi qui ouvre un bloc — alinea coupe par un changement
        # de page — n'a pas de mot devant lui a qui s'accrocher.
        # « \u00a0 » et non un blanc ordinaire : ecrit en clair,
        # parce qu'a l'oeil rien ne l'aurait distingue.
        blanc = "\u00a0" if m.start() else ""
        corps = m.group(2)
        if corps is None:                    # releve sans exposant
            corps = f"({m.group(3)})"
        return f'{blanc}<sup>{corps.strip()}</sup>'

    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf, combien = RENVOI.subn(poser, t)
            if not combien or neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            n += combien
    return n


# UN RENVOI ENTRE PARENTHESES SE FERME. Six fois dans les deux
# livrets, une parenthese manque : « buvard 41) » et « ballots 61) » du
# cote francais, « gobleto 13) » et « mi-sferi d) » du cote ido, un
# « singe (10 » a qui l'on n'a pas ferme, et le renvoi au tableau de
# l'Hotel, « n° 13) », dont le francais montre bien qu'il devait
# s'ouvrir. Sorte cassee de l'imprimeur ou distraction du releveur, on
# ne peut pas le dire — et cela n'a pas d'importance : la source garde
# ce qu'elle lit, les deux PDF avec elle, et c'est la page de lecture
# qui compose proprement.
#
# LE CONTROLE QUI LES A TOUS TROUVES tient en une ligne : compter les
# parentheses de chaque alinea et signaler celles qui ne se repondent
# pas. Six alineas sur six cent quatre-vingt-trois, et pas un de plus ;
# aucune de ces six n'etait une vraie parenthese depareillee du texte.
#
# On ne touche qu'a CE QUI EST DEJA UN RENVOI : un exposant qui ne
# porte que des chiffres, ou une lettre avec au moins une parenthese.
# Sans cette derniere condition on ecrirait « (o) » sur les « n° » du
# texte, qui sont aussi des exposants.
FERME_NUM = re.compile(
    r'<sup>\(?\s*(\d{1,3}(?:\s*,\s*\d{1,3})*(?:\s*(?:<i>)?bis(?:</i>)?)?)'
    r'\s*\)?</sup>')
FERME_LIT = re.compile(
    r'<sup>(<i>)?(?:\(([a-z]{1,2})\)?|([a-z]{1,2})\))(</i>)?</sup>')


def fermer_renvois(rangi):
    """Rend a chaque renvoi ses deux parentheses."""
    n = 0

    def num(m):
        nonlocal n
        neuf = f"<sup>({m.group(1)})</sup>"
        n += neuf != m.group(0)
        return neuf

    def lit(m):
        nonlocal n
        ita = "<i>" if m.group(1) or m.group(4) else ""
        neuf = (f"<sup>{ita}({m.group(2) or m.group(3)})"
                + ("</i>" if ita else "") + "</sup>")
        n += neuf != m.group(0)
        return neuf

    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = FERME_LIT.sub(lit, FERME_NUM.sub(num, t))
            if neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# ET CE QUI N'EST PAS UN RENVOI SE CORRIGE A LA MAIN. « La listo esos
# kompletigata sur la du tabeli « La Hotelo » n° 13) e « La Merkato »
# (n° 15) » : la seconde parenthese s'ouvre, la premiere non, et le
# francais de la meme note les ouvre toutes deux. Ce n'est pas un renvoi
# a un objet de la planche mais a un autre tableau ; aucune regle
# generale ne l'attrape, et l'on ne va pas en inventer une pour un cas.
# gravuri/korekti.json le dit en toutes lettres, bloc par bloc.
def korekti_teksto(rangi):
    """Les corrections declarees a la main, bloc par bloc."""
    tab = korekti("teksto")
    if not tab:
        return 0
    n = 0
    for r in rangi:
        regles = tab.get(r["cle"])
        if not regles:
            continue
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = t
            for lg, avant, apres in regles:
                if lg == k:
                    neuf = neuf.replace(avant, apres)
            if neuf == t:
                continue
            n += 1
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# LE CONTROLE QUI A TROUVE LES SIX. Compter les parentheses de chaque
# alinea et signaler celles qui ne se repondent pas : six alineas sur
# six cent quatre-vingt-trois, et pas un de plus — aucune n'etait une
# vraie parenthese depareillee du texte, toutes etaient des renvois
# estropies. On le laisse tourner a chaque fabrication : le jour ou un
# relevé en laissera passer une, elle se dira ici.
def depareillees(rangi):
    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            nu = re.sub(r'<[^>]+>', '', t)
            if nu.count("(") != nu.count(")"):
                yield r["cle"], k, re.sub(r'\s+', ' ', nu)[:110]


TETE_NOTE = re.compile(r'^((?:<[^>]+>)*)\((?:\*+|\d+)\)')


def uniformiser_notes(rangi):
    """Marque « (*) » la note elle-meme, comme son appel.

    L'appel est deja rendu « (*) » pour tout le monde ; il fallait que
    la note ouvre sur le meme signe, sans quoi le bouton « (*) » du
    tableau 13 depliait une note commencant par « (1) ». On ne touche
    qu'a la marque de tete, jamais au corps de la note -- celle du
    tableau 6 cite « la E. baby, F. bebe », et ces parentheses-la
    doivent rester.
    """
    n = 0
    for r in rangi:
        if r["tipo"] != "noto":
            continue
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf, combien = TETE_NOTE.subn(r"\1(*)", t, count=1)
            if not combien or neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            n += 1
    return n


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
SERIO = re.compile(
    r"\b(?:unesma|duesma|triesma|quaresma"
    r"|premi[eè]re|deuxi[eè]me|troisi[eè]me|quatri[eè]me)\s+"
    r"(?:serio|s[eé]rie)\b", re.I)

# LA SCENE, DANS LES DEUX LANGUES. On la reconnaissait a l'italique du
# fac-simile ; mais l'italique est justement ce qui differe -- Guignon
# compose « Unesma ceno. » en italique la ou Rochelle laisse « Première
# scène. » en romain. Le mot, lui, est sur. C'est le meme parti que pour
# la serie, juste au-dessus.
CENO = re.compile(
    r"\b(?:unesma|duesma|triesma|quaresma"
    r"|premi[eè]re|deuxi[eè]me|troisi[eè]me|quatri[eè]me)\s+"
    r"(?:ceno|sc[eè]ne)\b", re.I)

# LE SOUS-TITRE ENTRE PARENTHESES. Le point n'est pas du meme cote d'un
# volume a l'autre -- « (Simpla leciono pri naturcienco.) » chez Guignon,
# « (Simple leçon d'histoire naturelle). » chez Rochelle -- et un test
# sur la derniere lettre laissait donc le francais de cote.
SUBT = re.compile(r"\(.*\)\s*[.,;:!?]?")


def korpo_de(attrs):
    """Le corps de caractere d'une ligne d'apparat, ou rien."""
    m = KORPO.search(attrs)
    return m.group(1) if m else ""


# LE ROLE PREVAUT SUR LA MACRO. Les deux volumes ne composent pas de la
# meme facon ce qui joue le meme role : le titre du tableau 8 passe par
# \VUpk cote ido et par \VUtitre cote francais, de sorte que la page
# donnait « La Rekolto. » en corps de texte en face d'un « La Moisson.
# --- Les aspects de la campagne. » en gros et gras. De meme la scene :
# italique d'un cote, romain de l'autre. Le PDF doit garder chaque
# fac-simile tel qu'il est ; la page de lecture, elle, sert a COMPARER,
# et deux choses qui se repondent doivent se ressembler.
#
# On marque donc chaque ligne d'apparat de son ROLE -- numero, titre,
# serie, scene, section, sous-titre -- et c'est le role, non la macro,
# que la feuille de style habille. Le role se lit sur la place et sur le
# mot, les deux seules choses que les deux editions partagent.
def roles_ap(html, porte_titre=False, apres_ceno=False):
    """Marque chaque ligne d'apparat d'un data-rolo.

    « porte_titre » : ce bloc n'est pas une ouverture, mais il porte le
    titre du tableau -- aux tableaux 14 et 15 le fac-simile ne met rien
    sous le numero et le titre ouvre le premier intertitre. Sans cela il
    se composait en petites capitales de SECTION, si bien que le titre du
    tableau 14 ne ressemblait pas a celui du tableau 2.

    « apres_ceno » : le bloc precedent n'etait qu'un marqueur de scene,
    et celui-ci porte donc le titre de cette scene. Aux tableaux 3, 7 et
    9 la scene et son titre sont deux blocs ; au 4 et au 8, un seul.
    """
    trouves = list(LIGNE_AP.finditer(html))
    lignes = [(m.group(1), m.group(2)) for m in trouves]
    # UN ORNEMENT OU UN FILET SEPARE. Deux lignes de meme corps sont la
    # suite d'un meme titre -- sauf si l'imprimeur a mis une vignette ou
    # un filet entre elles, ce qui les donne pour deux choses. Les six
    # cas de l'edition sont les ouvertures de serie : « la Delmas-tabeli
    # helpanta » puis un fleuron puis « UNESMA SERIO », et de meme aux
    # deuxieme et troisieme series, ou la mention de serie precede le
    # numero du tableau. Sans cette regle on recollerait le titre du
    # volume et le nom de la serie en une seule ligne.
    coupe = [False] * len(trouves)
    for k in range(1, len(trouves)):
        entre = html[trouves[k - 1].end():trouves[k].start()]
        coupe[k] = 'class="orn"' in entre or 'class="fil"' in entre
    if not lignes:
        # Quelques titres sont composes a la main, sans macro \VU, et
        # n'ont donc aucune ligne a marquer : on prend le bloc entier.
        nu = net_tdm(html)
        if not nu:
            return html
        return f'<span class="pk" data-rolo="sekc">{html}</span>'

    role = [None] * len(lignes)
    numero = next((k for k, (_, t) in enumerate(lignes)
                   if "TABELO" in t or "TABLEAU" in t), None)
    for k, (_, t) in enumerate(lignes):
        nu = net_tdm(t)
        if k == numero:
            role[k] = "nom"
        elif SERIO.search(nu):
            role[k] = "serio"
        elif CENO.search(nu):
            role[k] = "ceno"
        elif SUBT.fullmatch(nu):
            role[k] = "subt"

    # OU COMMENCE LE TITRE, ET LEQUEL. Sous le numero vient le titre du
    # tableau ; mais si une scene s'intercale -- « Unesma ceno. » au
    # tableau 8 -- ce qui suit titre la SCENE, non le tableau. Un titre
    # de scene doit se composer partout de la meme facon, que le tableau
    # en compte une ou plusieurs, et plus grand qu'un simple intertitre.
    depart, ceno_avant = None, apres_ceno
    if numero is not None:
        depart = numero + 1
        ceno_avant = False
    elif any(r == "ceno" for r in role):
        depart = max(k for k, r in enumerate(role) if r == "ceno") + 1
        ceno_avant = True
    elif porte_titre or apres_ceno:
        depart = 0
    if depart is not None:
        ti = next((k for k in range(depart, len(lignes))
                   if role[k] is None and net_tdm(lignes[k][1])), None)
        if ti is not None and (numero is not None or porte_titre or ceno_avant):
            if numero is not None:
                ceno_avant = any(role[k] == "ceno"
                                 for k in range(numero + 1, ti))
            quel = "titceno" if ceno_avant else "tit"
            role[ti] = quel
            # Les lignes de MEME CORPS qui suivent sont la suite du meme
            # titre (voir la table des matieres, qui les recolle ainsi).
            for k in range(ti + 1, len(lignes)):
                if not net_tdm(lignes[k][1]):
                    continue
                # L'ornement ne change pas la NATURE de la ligne : « Les
                # Bateaux. » reste un morceau du titre du tableau 12,
                # comme « La Navi. » cote ido. Il empeche seulement de
                # les recoller sur une meme ligne, plus bas.
                if role[k] is not None or \
                        korpo_de(lignes[k][0]) != korpo_de(lignes[ti][0]):
                    break
                role[k] = quel

    for k in range(len(lignes)):
        if role[k] is None:
            # Au-dessus du numero c'est l'apparat du volume lui-meme --
            # « EXPLIKO - LIBRETO », « DI » ; au-dessous, une section.
            role[k] = "avan" if (numero is not None and k < numero) else "sekc"

    # UN TITRE COUPE PAR LA COMPOSITION SE RELIT D'UN TRAIT. Le
    # fac-simile ido casse « La Homala Korpo. --- La Amuztempo. » et
    # « La Ludi. » sur deux lignes la ou le francais les unit d'un tiret.
    # On les remet donc sur une ligne, avec le tiret quand la premiere
    # s'acheve sur un point -- et sans lui quand elle s'acheve sur une
    # virgule, ou la phrase se poursuit d'elle-meme (tableau 6).
    joint = [False] * len(lignes)
    k = 0
    while k < len(lignes):
        if role[k] in ("tit", "titceno"):
            fin = k
            while fin + 1 < len(lignes) and role[fin + 1] == role[k] \
                    and not coupe[fin + 1]:
                fin += 1
            if fin > k:
                for j in range(k, fin + 1):
                    joint[j] = True
            k = fin + 1
        else:
            k += 1

    n = [0]

    def poser(m):
        k = n[0]
        n[0] += 1
        att = f' data-rolo="{role[k]}"'
        if joint[k]:
            att += ' data-kunligita="1"'
        return f'{m.group(0)[:-1]}{att}>'
    html = OUVRE_AP.sub(poser, html)

    # Le liant se pose DANS la ligne suivante, pour que la ligne garde sa
    # propre ancre : la table des matieres compte les memes lignes.
    n = [0]

    def lier(m):
        k = n[0]
        n[0] += 1
        if k == 0 or not (joint[k] and joint[k - 1]):
            return m.group(0)
        avant = net_tdm(lignes[k - 1][1])
        liant = " — " if avant.endswith((".", ")", "!", "?")) else " "
        return f'{m.group(0)}{liant}'
    return OUVRE_AP.sub(lier, html)


def joindre(morceaux):
    """Recolle les lignes d'un meme titre, comme le fait la page."""
    # Le meme liant qu'a l'ecran : un tiret quand la ligne precedente
    # s'acheve sur un point, rien quand elle s'acheve sur une virgule et
    # que la phrase se poursuit d'elle-meme.
    out = ""
    for m in morceaux:
        if not out:
            out = m
        elif out.endswith((".", ")", "!", "?")):
            out = f"{out} — {m}"
        else:
            out = f"{out} {m}"
    return out


def libelle_bloc(brut):
    """Le texte d'un bloc pour le volet, recolle comme il l'est a l'ecran."""
    # Deux lignes de MEME CORPS sont un seul titre coupe par la
    # composition, et se rejoignent avec le liant -- comme dans la page.
    # Un changement de corps, ou un marqueur de scene, separe deux choses
    # distinctes : « Unesma ceno. » et son titre gardent leur espace.
    paires = [(korpo_de(m.group(1)), net_tdm(m.group(2)))
              for m in LIGNE_AP.finditer(brut)]
    paires = [(c, t) for c, t in paires if t]
    if not paires:
        return net_tdm(brut)
    out = paires[0][1]
    for (corps, texte), (corps_av, texte_av) in zip(paires[1:], paires):
        # UN SOUS-TITRE ENTRE PARENTHESES N'EST PAS LA SUITE DU TITRE,
        # meme compose au meme corps. « Gimnastiko. » et « (Naraco da un
        # de la lernanti.) » le sont tous deux en 10.2pt : le volet les
        # joignait donc d'un tiret, puis otait la parenthese -- et le
        # tiret restait tout seul, « Gimnastiko. — ».
        if corps == corps_av and not CENO.search(texte_av) \
                and not CENO.search(texte) and not SUBT.fullmatch(texte):
            out = joindre([out, texte])
        else:
            out = f"{out} {texte}"
    return out


def sen_subtitro(t):
    """Le sous-titre entre parentheses ne va pas dans le volet."""
    # Le fac-simile precise certains titres par une parenthese --
    # « (Naraco da un de la lernanti.) » sous « Gimnastiko. »,
    # « (Simpla leciono pri naturcienco.) » sous « La Korpo homala. »,
    # « (Balno-chambro.) » sous « La Balneyo. ». Cela a sa place dans la
    # page, qui reproduit la mise en page ; dans le volet, ou l'on
    # cherche un titre du coin de l'oeil, cela double la longueur de
    # l'entree sans rien apprendre. On ne l'ote que si elle SUIT un
    # titre : une entree qui ne serait que parenthese se garde entiere,
    # faute de mieux que rien.
    court = re.sub(r"\s*\([^()]*\)\s*$", "", t).strip()
    # Et le liant qui la precedait s'en va avec elle : rien ne doit rester
    # pendu au bout de l'entree.
    court = re.sub(r"\s*[—–-]\s*$", "", court).strip()
    return court or t


FILET = '<span class="fil"></span>'


def uniformiser_filets(rangi):
    """Met le meme filet dans les deux colonnes.

    Le filet est une fantaisie d'imprimeur, et les deux ateliers ne
    l'ont pas posee aux memes endroits : le francais ferme le tableau 2
    par un filet que l'ido n'a pas, ouvre le tableau 13 par un filet que
    l'ido n'a pas non plus, tandis que seuls les tableaux 1, 7 et 11
    portent un filet sous leur titre dans les DEUX volumes. En regard,
    cela donnait un trait dans une colonne et rien en face, a la meme
    hauteur -- et un tableau qui s'ouvre autrement que le precedent.

    La page de lecture n'est pas le fac-simile : les PDF gardent ce que
    l'imprimeur a compose, la page harmonise. Deux regles suffisent :
    tout tableau s'ouvre sur un filet sous son titre, et tout filet
    presente dans une colonne se retrouve dans l'autre. On ne touche
    qu'a la FIN des blocs, la ou tous ces filets se trouvent deja.
    """
    pose = 0
    for r in rangi:
        if r["tipo"] == "noto":
            continue
        cels = [("io", r)] + [(lg["kodo"], r["tra"].get(lg["kodo"]))
                              for lg in LANGUES]
        textes = {k: (o["io"] if k == "io" else o["t"])
                  for k, o in cels if o}
        pleins = {k: t for k, t in textes.items() if t and t.strip()}
        if not pleins:
            continue
        ouverture = r["tipo"] == "apar" and any(
            "TABELO" in t or "TABLEAU" in t for t in pleins.values())
        veut = ouverture or any(t.rstrip().endswith(FILET)
                                for t in pleins.values())
        if not veut:
            continue
        for k, t in pleins.items():
            if t.rstrip().endswith(FILET):
                continue
            neuf = t.rstrip() + FILET
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            pose += 1
    return pose


def rendre(rangi):
    # LES LANGUES DIFFEREES SE RANGENT ICI PLUTOT QUE DANS LA PAGE.
    # Tout est calcule comme pour les autres -- roles d'apparat, appels
    # de note, boutons de renvoi -- et seul le dernier geste change :
    # au lieu d'ecrire le texte dans la case, on le pose dans ce sac,
    # qui partira dans lingui/<kodo>.json, et la case reste vide.
    differe = {lg["kodo"]: {"k": {}, "noto": {}}
               for lg in LANGUES if lg.get("differita")}

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
    # Un titre de scene annonce avec sa scene ne s'annonce pas deux fois.
    fusionnes = set()
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
            # UNE SCENE AVANT LE TITRE, ET LE TABLEAU N'EN A PAS. Aux
            # tableaux 7, 8 et 9 le numero est suivi d'un « Unesma
            # ceno. » : ce qui vient ensuite titre la SCENE, non le
            # tableau, et les deux volumes le disent de meme -- le
            # francais du tableau 8 porte « Première scène. » puis « La
            # Moisson. --- Les aspects de la campagne. ». La table
            # annoncait pourtant ce titre de scene comme celui du
            # tableau, qui n'en a pas.
            premiere = next((k for k in range(i + 1, len(lignes_ap))
                             if net(lignes_ap[k])), None)
            ceno_dabord = premiere is not None and \
                bool(CENO.search(net(lignes_ap[premiere])))
            ti = None if ceno_dabord else premiere
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
            titre = joindre([net(lignes_ap[ti])] +
                            [net(lignes_ap[k]) for k in suites]) \
                if ti is not None else ""
            if not titre and not ceno_dabord:
                # LE TITRE EST PARFOIS HORS DU BLOC D'OUVERTURE. Aux
                # tableaux 14 et 15, le fac-simile ido ne met
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
                    if est_ceno(suite) or CENO.search(net(suite)):
                        # Une scene ouvre le tableau : ce qui suit la
                        # titre, elle, et le tableau reste sans titre.
                        # C'est le cas des tableaux 7 et 9.
                        break
                    titre = net(suite)
                    # ET IL NE S'ANNONCE PAS DEUX FOIS. Emprunte au
                    # premier intertitre, le titre reparaissait juste
                    # au-dessous en sous-entree : le volet lisait
                    # « TABELO No 10 La Maro. --- La Portuo. » puis
                    # « La Maro. --- La Portuo. ».
                    empruntes.add(q["cle"])
                    break
            # LA SERIE S'ANNONCE AVANT LE TABLEAU QUI L'OUVRE, et parfois
            # dans le bloc d'AVANT : l'ouverture du tableau 1 est coupee
            # en deux pour loger la gravure, et « UNESMA SERIO » est
            # reste avec l'apparat du volume. On regarde donc aussi la ou
            # elle a pu tomber.
            avant = lignes_ap[:i]
            if idx and rangi[idx - 1]["tipo"] == "apar":
                avant = [m.group(2) for m in
                         LIGNE_AP.finditer(texte_de(rangi[idx - 1]))] + avant
            serie = next((SERIO.search(net(l)) for l in avant
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
            absorbe = set()
            for j in range(i + 1, len(lignes_ap)):
                if j == ti or j in suites or j in absorbe \
                        or not net(lignes_ap[j]):
                    continue
                lib = net(lignes_ap[j])
                # LA SCENE DE L'OUVERTURE EMPORTE SON TITRE, comme celles
                # qui ont leur bloc a elles : au tableau 8 la scene et son
                # titre sont tous deux dans l'ouverture, et le volet
                # annoncait « Unesma ceno. », « La Rekolto. » et « La
                # Aspekti di la Ruro. » en trois entrees.
                if CENO.search(lib):
                    parts, k, base = [], j + 1, None
                    while k < len(lignes_ap):
                        if not net(lignes_ap[k]):
                            k += 1
                            continue
                        if k in (ti,) or k in suites \
                                or CENO.search(net(lignes_ap[k])):
                            break
                        if base is None:
                            base = corps[k]
                        elif corps[k] != base:
                            break
                        parts.append(net(lignes_ap[k]))
                        absorbe.add(k)
                        k += 1
                    if parts:
                        # Une espace, non le liant : le tiret ne vaut
                        # qu'entre les lignes d'un MEME titre, et la
                        # scene n'en est pas une.
                        lib = f"{lib} {joindre(parts)}"
                tdm.append((f'{r["cle"]}-l{j}', lib, "sc"))
            continue

        # Un intertitre : scene, ou section.
        if r["cle"] in fusionnes:
            continue
        nues = [net(t) for t in lignes_ap if net(t)] or [net(brut)]
        if est_ceno(brut):
            # LE TITRE DE LA SCENE S'ANNONCE AVEC ELLE. Aux tableaux 3, 7,
            # 8 et 9 la scene et son titre sont deux blocs ; au 4, un
            # seul. Le volet donnait donc « Unesma ceno. » toute seule
            # ici et « Unesma ceno. La Mariaj-festino. » la, pour la meme
            # chose. Quand le marqueur est seul dans son bloc, on lui
            # rattache le bloc suivant, qui porte son titre.
            libelle = libelle_bloc(brut)
            if all(CENO.search(x) for x in nues):
                for q in rangi[idx + 1:]:
                    if q["tipo"] == "p":
                        break
                    if q["tipo"] != "sub":
                        continue
                    suite = texte_de(q)
                    if not est_ceno(suite):
                        libelle = f"{libelle} {libelle_bloc(suite)}"
                        fusionnes.add(q["cle"])
                    break
            tdm.append((r["cle"], libelle, "sc"))
            continue
        if r["cle"] in empruntes:
            continue
        tdm.append((r["cle"], libelle_bloc(brut), "st"))

    lignes = []
    apres_ceno = False
    gravo = gravuri()
    for r in rangi:
        cl = ["r", r["tipo"]]
        io = r["io"]
        # LA GRAVURE PRECEDE LE BLOC QU'ELLE ILLUSTRE, et c'est la CLE
        # qui le dit -- non le numero du tableau. La plupart des planches
        # ouvrent leur tableau, mais pas toutes : la figure du corps
        # humain se pose sous « La Korpo homala. », le plan de la maison
        # sous le « (Videz la plano.) » du tableau 5, et le tableau 1
        # entre l'apparat du volume et son propre titre -- ce pourquoi
        # son ouverture est coupee en deux dans le releve.
        g = gravo.get(r["cle"])
        if g:
            v, d = g["vido"], g["detalo"]
            # LE NOM DE FICHIER NE CHANGE PAS QUAND LA PLANCHE CHANGE.
            # On reprend les seize gravures une a une sur leur
            # fac-simile ; le fichier garde son nom, et le navigateur qui
            # l'a deja vu ressert l'ancienne — celle en couleur — sans
            # rien demander. Le lecteur croit alors que rien n'a bouge.
            # On accroche donc a l'adresse le POIDS du fichier, que
            # gravuri.json note deja : il change des que l'image change,
            # et ne bouge pas tant qu'elle ne bouge pas.
            qv, qd = f"?v={v['okteti']}", f"?v={d['okteti']}"
            lignes.append(
                f'<figure class="gravuro" data-cle="{r["cle"]}" '
                f'data-detalo="gravuri/{r["cle"]}-detalo.webp{qd}" '
                f'data-dl="{d["largeur"]}" data-dh="{d["alteso"]}">'
                # DEUX DEFINITIONS, ET LE NAVIGATEUR CHOISIT. Sur un
                # ecran ordinaire la vue d'ensemble suffit ; sur un
                # Retina, ou chaque point de la page vaut deux points de
                # l'ecran, elle paraissait floue. « sizes » dit la
                # largeur reelle d'affichage : un telephone prend donc la
                # petite, et seul un grand ecran dense va chercher
                # l'image de detail -- celle-la meme qui servira au plein
                # ecran et aux gros plans, donc jamais chargee deux fois.
                f'<img src="gravuri/{r["cle"]}-vido.webp{qv}" alt="" '
                f'srcset="gravuri/{r["cle"]}-vido.webp{qv} {v["largeur"]}w, '
                f'gravuri/{r["cle"]}-detalo.webp{qd} {d["largeur"]}w" '
                f'sizes="(max-width:900px) calc(100vw - 64px), '
                f'min(calc(100vw - 314px), 1246px)" '
                f'loading="lazy" decoding="async" '
                f'width="{v["largeur"]}" height="{v["alteso"]}">'
                f'</figure>')
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
        # LE ROLE SE MARQUE AVANT L'ANCRAGE, et sur les deux colonnes :
        # c'est lui qui les fait se ressembler. Les ouvertures et les
        # intertitres seuls en portent ; le texte suivi n'a pas d'apparat.
        if r["tipo"] in ("apar", "sub"):
            porte = r["cle"] in empruntes
            io = roles_ap(io, porte, apres_ceno)
            for lg in LANGUES:
                o = r["tra"].get(lg["kodo"])
                if o and o["t"]:
                    o["t"] = roles_ap(o["t"], porte, apres_ceno)
            # Le bloc suivant porte-t-il le titre de cette scene ? Oui si
            # celui-ci s'acheve sur un marqueur de scene. C'est l'ido qui
            # en decide : la colonne de droite le suit.
            derniers = re.findall(r'data-rolo="([^"]*)"', io)
            apres_ceno = bool(derniers) and derniers[-1] == "ceno"
        elif r["tipo"] == "p":
            apres_ceno = False
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
        cel_io = f'<div class="k io" lang="io">{fol}{io}</div>' if io else \
                 '<div class="k io vaka" lang="io"></div>'
        cel = [cel_io]
        for lg in LANGUES:
            k = lg["kodo"]
            o = r["tra"].get(k)
            if o:
                f2 = ""
                if o["f"]:
                    pg2 = rang_pdf(k, o["fe"])
                    f2 = (f'<a class="fol fd" href="tableaux.pdf#page={pg2}" '
                          f'title="Folio {o["f"]} dans le PDF">{o["f"]}</a>')
                if k in differe:
                    # La case est vide dans le fichier ET marquee « dif » :
                    # c'est a cette marque que le CSS sait ne pas y mettre
                    # le tiret des vraies lacunes, et que le script sait
                    # qu'il a quelque chose a y verser.
                    differe[k]["k"][r["cle"]] = f2 + o["t"]
                    cel.append(f'<div class="k tra vaka dif" '
                               f'data-lg="{k}" lang="{k}"></div>')
                else:
                    cel.append(f'<div class="k tra" data-lg="{k}" '
                               f'lang="{k}">{f2}{o["t"]}</div>')
            else:
                cel.append(f'<div class="k tra vaka" data-lg="{k}" '
                           f'lang="{k}"></div>')
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
                # La case de rang a ete construite plus haut, avant qu'on
                # sache que ce bloc etait une note : elle ne sera pas
                # rendue, et ce qu'on avait mis de cote pour elle ferait
                # double emploi avec la note elle-meme.
                if k in differe:
                    differe[k]["k"].pop(r["cle"], None)
                if txt:
                    if k in differe:
                        differe[k]["noto"][r["cle"]] = txt
                        txt = ""
                    lignes.append(
                        f'<div class="noto" id="noto-{k}-{r["cle"]}" '
                        f'data-lg="{k}" lang="{k}" hidden>{txt}</div>')
            continue
        lignes.append(f'<div class="{" ".join(cl)}"{att}>' +
                      "".join(cel) + "</div>")

    nav = "".join(
        f'<div class="parto">{t}</div>' if k == "parto"
        else f'<a href="#{c}" data-ch="{c}" class="{k}">{sen_subtitro(t)}</a>'
        for c, t, k in tdm)
    opcioni = "".join(
        f'<option value="{lg["kodo"]}">{lg["nomo"]}</option>'
        for lg in LANGUES)

    # L'ADRESSE PORTE LE POIDS DU FICHIER, comme celle des gravures :
    # le navigateur qui a deja lu une version de la traduction ne doit
    # pas la resservir quand elle a change.
    dos = RACINE / "lingui"
    dos.mkdir(exist_ok=True)
    for lg in LANGUES:
        d = differe.get(lg["kodo"])
        if d is None:
            continue
        f = dos / f'{lg["kodo"]}.json'
        f.write_text(json.dumps(d, ensure_ascii=False,
                                separators=(",", ":")) + "\n",
                     encoding="utf-8")
        lg["adreso"] = f'lingui/{lg["kodo"]}.json?v={f.stat().st_size}'
        print(f'  {f.relative_to(RACINE)} : {len(d["k"])} bloki, '
              f'{f.stat().st_size // 1024} Ko')

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
    print(f"  filets ajoutes pour egaliser les colonnes : "
          f"{uniformiser_filets(r)}")
    rendre(r)
    print(f"  notes reliees a leur appel : {rap['lies']}")
    if rap.get("fermes") or rap.get("korektiti"):
        print(f"  parentheses rendues a des renvois : {rap['fermes']}"
              f", corrections declarees : {rap['korektiti']}")
    for cle, lg, t in depareillees(r):
        print(f"  PARENTHESE DEPAREILLEE [{lg}] {cle} : {t}")
    for langue, cle, marque, pourquoi in rap["echecs"]:
        print(f"  NON RELIEE [{langue}] {cle} « ({marque}) » : {pourquoi}")
