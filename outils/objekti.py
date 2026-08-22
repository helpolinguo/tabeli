#!/usr/bin/env python3
# ===================================================================
#  objekti.py — le nom de chaque objet numerote, dans les deux langues.
#
#  « Nous avons imprime en caracteres gras les substantifs qui se
#  trouvent dans le vocabulaire des Tableaux EN LES FAISANT SUIVRE DE
#  LEUR NUMERO » : le liminaire francais donne lui-meme la regle, et
#  c'est elle qu'on lit ici. Chaque « (N) » du texte est precede du
#  substantif en gras qu'il numerote ; on releve donc le couple.
#
#  A QUOI CELA SERT. D'abord a savoir CE QUE montre un gros plan : un
#  clic sur « (15) » du tableau 13 ouvre la caisse, et la page peut le
#  dire. Ensuite, et surtout, a verifier les lectures douteuses du
#  lecteur de numeros : quand la machine hesite, on regarde la decoupe
#  et l'on demande si l'objet nomme s'y trouve. Un « (65) » lu sur une
#  hachure ne montre pas de bureau de tabac ; le nom tranche la ou la
#  forme du chiffre ne suffit plus.
#
#  UN NUMERO EST APPELE PLUSIEURS FOIS. Le texte y revient — « la
#  chambre (2) », puis « cette chambre (2) » — et pas toujours avec le
#  meme mot. On garde toutes les formes rencontrees, la premiere en
#  tete : c'est celle du releve initial, la plus descriptive.
#
#  USAGE
#      python3 outils/objekti.py            # ecrit gravuri/objekti.json
#      python3 outils/objekti.py 13         # montre le tableau 13
# ===================================================================

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Le substantif en gras, puis son numero — avec ou sans exposant, avec
# ou sans blanc entre les deux, le fac-simile hesitant sur les trois.
# TROIS FORMES DE RENVOI, et il a fallu les trois : « (18) », le groupe
# « (9, 11, 12) » qui vaut pour trois objets a la fois, et « 41) » ou la
# parenthese ouvrante manque. Le substantif se range sous chacun des
# numeros du groupe : « les tableaux muraux (9, 11, 12) » nomme les
# trois.
GRAS = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'      # \VUgras{...}
    r'(?:\s|\\nl|\\cc|%|\n)*'                   # coupures de ligne
    r'(?:\\textsuperscript\{'
    r'(\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*,?'
    r'(?:\s*(?:\\textit\{)?bis\}?)?\s*\)?)\}'
    r'|\((\d{1,3}(?:\s*,\s*\d{1,3})*)\))')
CHIFRO = re.compile(r'\d{1,3}')
BIS = re.compile(r'\bbis\b')

# LES RENVOIS A LETTRE. « rondo (a), quadrato (b) » : la lettre est
# gravee sur l'objet qui la porte -- le tableau noir, la carte -- et
# n'a de sens que rapportee a lui. gravuri/literi.json dit, bloc par
# bloc, sous quel prefixe la ranger : le « a » du tableau noir est
# « 1a », celui de la carte « 10a ».
# LA LETTRE SE PRESENTE DE TROIS FACONS. Le francais la met en
# italique — « \textsuperscript{\textit{(a)}} » — l'ido la laisse nue,
# et six fois dans les deux livrets une des deux parentheses manque :
# « mi-sferi d) ». On accepte les trois, mais on exige AU MOINS UNE
# PARENTHESE : sans elle on rangerait sous « o » les « n° » du texte.
GRAS_LIT = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'
    r'(?:\s|\\nl|\\cc|%|\n)*'
    r'(?:\\textsuperscript\{(?:\\textit\{)?'
    r'(?:\(([a-z]{1,2})\)?|([a-z]{1,2})\))\}?\}'
    r'|\(([a-z]{1,2})\))')


def literi(champo):
    f = RACINE / 'gravuri' / 'literi.json'
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding='utf-8')).get(champo, {})


PATRI = literi('patri')

# LE « (1) » QUI EST UN l. Au tableau 5, la salle de bains porte un
# renvoi compose « (1) » : dans cette fonte le l bas de casse et le
# chiffre 1 ont le meme dessin, et le plan de la maison tranche — sa
# legende porte « l. Balneyo ». Le nom irait donc se ranger sous le
# numero 1, qui est la facade ; on le range sous la lettre.
UNU_SORTO = literi('unu-sorto')


# LE RENVOI QUE LA PLANCHE NE PORTE PAS. « les plates-bandes (150) »,
# au tableau 5, sont gravees « 50 » : le nom doit se ranger sous le
# numero qu'on montrera, non sous celui qu'on lit. gravuri/korekti.json
# tient la table, et numeri.py la lit de meme.
def korekti():
    f = RACINE / 'gravuri' / 'korekti.json'
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding='utf-8')).items() if not k.startswith('_')}


KOREKTI = korekti()


def korekti_renvojo(tab, cle=""):
    """{lu: a lire} pour UN BLOC : les corrections qui valent pour tout
    le tableau, plus celles que ce bloc-ci porte seul.

    UNE CORRECTION NE VAUT PAS TOUJOURS PARTOUT. Le « (150) » du
    tableau 5 est un numero que la planche n'a nulle part : le corriger
    partout ne peut rien casser. Le « (6) » que le tableau 6 donne a la
    femme de chambre, lui, est un numero qui existe par ailleurs — c'est
    le savon de l'alinea 2 — et le corriger partout ferait pointer
    le savon sur la femme de chambre. Une entree dont la cle est celle
    d'un BLOC ne vaut donc que dans ce bloc.
    """
    t = KOREKTI.get(f"t{tab:02d}", {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out

# LE SUBSTANTIF N'EST PAS TOUJOURS EN GRAS DEVANT UNE LETTRE. « la
# zoologio (a), botaniko (b), geologio (c) » : trois mots nus, alors
# que la regle du liminaire veut le gras. Les deux ateliers s'y
# tiennent pour les numeros et l'oublient pour les lettres. On
# reprend donc le mot qui precede, faute de mieux : sans lui le gros
# plan s'ouvrirait sans rien dire de ce qu'il montre.
NUD_LIT = re.compile(
    r"([\w'\u2019-]+)\s*(?:\\nl|\\cc)?\s*"
    r'\\textsuperscript\{\(([a-z]{1,2})\)\}')

# Ce qui reste de balisage dans le nom releve.
MACROS = re.compile(r'\\(?:textit|textsc|emph|VUgras|nl|cc|hbox|,)\b\{?')


def nettoyer(brut):
    t = MACROS.sub('', brut)
    t = t.replace('\\-', '').replace('~', ' ').replace('{', '').replace('}', '')
    t = re.sub(r'\s+', ' ', t).strip(' .,;:')
    # Un substantif coupe par un changement de ligne garde son trait
    # d'union du fac-simile ; il n'appartient pas au mot.
    return re.sub(r'-\s+', '', t)


# UN SUBSTANTIF COUPE PAR LA FIN DE LIGNE EST COMPOSE EN DEUX MORCEAUX,
# chacun dans son \VUgras — c'est la regle du releve, une ligne du
# fac-simile etant une ligne de la source. « \VUgras{jour}\cc /
# \VUgras{naux} » donnait donc « naux », et « \VUgras{livre}\nl /
# \VUgras{des voyageurs} » donnait « des voyageurs ». On recolle avant
# de lire : \cc a coupe un mot, \nl a coupe une locution.
RECOLLE = [
    (re.compile(r'\\VUgras\{([^{}]*)\}\\cc\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    # UN TRAIT D'UNION EN FIN DE LIGNE NE PREND PAS DE BLANC : le mot
    # continue. « \VUgras{lad-(if-)}\nl \VUgras{isto} » est le nom du
    # ferblantier-lampiste, et le gros plan l'intitulait
    # « lad-(if-) isto ».
    (re.compile(r'\\VUgras\{([^{}]*-\)?)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    (re.compile(r'\\VUgras\{([^{}]*)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1 \2}'),
    # UN COMPOSE DONT LA LIGNE COUPE LE TRAIT N'A QUE SA SECONDE MOITIE
    # EN GRAS. Le compositeur ouvre le gras au debut de la ligne
    # suivante : « mason-\nl \VUgras{servisto} », « pluv-\nl
    # \VUgras{kanali} », « vitro-\nl \VUgras{kareli} ». Le mot est un
    # pourtant, et le fac-simile le prouve lui-meme deux lignes plus
    # bas, ou « \VUgras{tekto-kanali} » tient sur une ligne et prend
    # tout le gras. Le gros plan disait « servisto » la ou le francais
    # dit « aide-macon ».
    (re.compile(r'(?<![\\{])\b((?:[\w\'\u2019]+-)+)\\nl\s*\n\s*\\VUgras\{'),
     r'\\VUgras{\1'),
    # ET SUR UNE SEULE LIGNE AUSSI, quand le fac-simile ouvre le gras
    # au second membre : « pesko-\VUgras{barketi} », « (muton)-\VUgras
    # {trupo} », « (pastor)-\VUgras{bastono} ». Le premier membre porte
    # le sens — le troupeau est de moutons, la houlette est de berger —
    # et le nom sans lui ne dit plus rien : « po », « bastono ».
    (re.compile(r'(?<![\\{])((?:\(?[\w\'\u2019]+\)?-)+)\\VUgras\{'),
     r'\\VUgras{\1'),
    # UN GROUPE COUPE PAR UNE FIN DE LIGNE est compose en deux exposants,
    # « (9, 11, » puis « 12) ». Sans ce recollage, le douze restait
    # orphelin et les tableaux muraux n'avaient que deux noms sur trois.
    (re.compile(r'\\textsuperscript\{([^{}]*,)\}\s*(?:\\nl|\\cc)?\s*\n?\s*'
                r'\\textsuperscript\{([^{}]*)\}'),
     r'\\textsuperscript{\1 \2}'),
]


# UN MOT COUPE PAR LA FIN DE PAGE, lui, a tout l'appareil du feuillet
# entre ses deux moities : \ccplein, la fermeture de la page, le
# commentaire du feuillet, l'ouverture de la suivante, la cle « suite »
# et \VUcontinue. On ramene ce cas au precedent — un simple \cc — et
# la regle ci-dessus fait le reste : « \VUgras{dro}\ccplein ... \VUgras
# {medaro} » donne « dromedaro », et non « medaro ».
# DEUX ECRITURES POUR LA MEME FIN DE PAGE. \ccplein la dit d'un mot ;
# le tableau 7 l'ecrit \cc puis \parplein sur deux lignes, et la
# coupure du feuillet 54 echappait au recollage : le troupeau du
# berger, « (muton)-\VUgras{tru}\cc ... \VUgras{po} », s'appelait
# « po » dans le gros plan.
# LE SAUT SE MESURE, IL NE SE DEVINE PAS. « .*? » entre la fin de page
# et le bloc « suite » etait sans borne : la ou la page suivante ne
# continuait pas l'alinea, le motif courait jusqu'au prochain « suite »
# et emportait deux feuillets entiers du tableau 2 -- le jeu de
# tonneau y perdait un de ses deux noms. On nomme donc ce qui separe
# les deux moities : la fermeture de page, un commentaire de feuillet,
# l'ouverture de la page suivante, et rien d'autre.
SAUT = re.compile(
    r'(?:\\ccplein|\\cc\s*\n\\parplein)\s*\n\\end\{VUpage\}[ \t]*\n'
    r'(?:%[^\n]*\n|[ \t]*\n)*'
    r'\\begin\{VUpage\}[^\n]*\n'
    r'%%K\s+\S+\s+\S+\s+suite[ \t]*\n\\VUcontinue[ \t]*\n')


def recoller(texte):
    texte = SAUT.sub('\\\\cc\n', texte)
    for motif, remplacement in RECOLLE:
        avant = None
        while avant != texte:
            avant = texte
            texte = motif.sub(remplacement, texte)
    return texte


# LES PLANCHES A PLUSIEURS SCENES. Six tableaux montrent deux vignettes
# ou davantage, et chacune recommence sa numerotation a 1 : le « (39) »
# de la premiere scene et celui de la quatrieme ne nomment pas le meme
# objet. Le nom se range donc sous une cle qui porte la scene —
# « c1:39 » —, comme dans numeri.json. gravuri/ceni.json dit quels
# tableaux sont dans ce cas.
def a_ceni():
    f = RACINE / "gravuri" / "ceni.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


CENI = a_ceni()


def relever(dossier, motif):
    """{numero de tableau: {cle d'objet: [noms]}} pour une langue."""
    out = {}
    for f in sorted((RACINE / "texto" / dossier).glob(motif)):
        m = re.search(r'-(?:tabelo|tableau|table|cuadro|tablica|tubiao|lawha|talika|quadro|sarani|zuhyo|naqsha|sarni|tablo|tabella|tabel|tabell|taulukko|taula|tablycia|tabelul|tabla|cadro|tabulka|lentele)-(\d+)\.tex$', f.name)
        if not m:
            continue
        tab = int(m.group(1))
        par = out.setdefault(tab, {})
        scenes = f"t{tab:02d}" in CENI
        texte = recoller(f.read_text(encoding="utf-8"))
        # On coupe par cle de bloc, pour savoir de quelle scene on parle.
        parts = re.split(r'^%%K (\S+)', texte, flags=re.M)
        for i in range(1, len(parts), 2):
            mk = re.match(r't\d\d-(c\d)-', parts[i])
            if mk:
                relever.scene = mk.group(1)
            sc = getattr(relever, "scene", "") if scenes else ""
            # Les lettres du bloc, s'il en porte.
            pa = PATRI.get(parts[i])
            if pa:
                # UNE LETTRE FAUSSE SE CORRIGE COMME UN NUMERO FAUX. Au
                # tableau 1 les deux livrets echangent l'Europe et
                # l'Asie ; sans cette lecture, le nom se rangeait sous
                # la lettre du livret et le gros plan de l'Europe
                # s'intitulait « Azia ».
                kl = korekti_renvojo(tab, parts[i])
                for g in GRAS_LIT.finditer(parts[i + 1]):
                    nom = nettoyer(g.group(1))
                    if not nom:
                        continue
                    for L in (g.group(2) or g.group(3)
                              or g.group(4) or ""):
                        k = pa[1] + kl.get(L, L)
                        noms = par.setdefault(k, [])
                        if nom not in noms:
                            noms.append(nom)
                for g in NUD_LIT.finditer(parts[i + 1]):
                    for L in g.group(2):
                        k = pa[1] + kl.get(L, L)
                        if par.get(k):
                            continue
                        nom = nettoyer(g.group(1))
                        if nom:
                            par.setdefault(k, []).append(nom)
            uniq = UNU_SORTO.get(parts[i], [])
            for g in GRAS.finditer(parts[i + 1]):
                nom = nettoyer(g.group(1))
                if not nom:
                    continue
                brut = g.group(2) or g.group(3) or ""
                # Le mot gras est parfois coupe en deux par la fin de
                # ligne — « salle » puis « de bains » — et la regle ne
                # nomme que le dernier morceau : on l'accepte en fin de
                # nom comme en nom entier.
                L = next((L for m, L in uniq
                          if nom == m or nom.endswith(" " + m)), None)
                if L:
                    k = pa[1] + L if pa else L
                    noms = par.setdefault(k, [])
                    if nom not in noms:
                        noms.append(nom)
                    continue
                ns = CHIFRO.findall(brut)
                # « 94 bis » ne nomme pas le 94 : c'est un objet a part.
                if ns and BIS.search(brut):
                    ns[-1] = f"{ns[-1]}bis"
                kor = korekti_renvojo(tab, parts[i])
                for n in ns:
                    n = kor.get(str(n), n)
                    k = f"{sc}:{n}" if sc else n
                    noms = par.setdefault(k, [])
                    if nom not in noms:
                        noms.append(nom)
        relever.scene = ""
    return out


def rang(k):
    s, n = k.split(":", 1) if ":" in k else ("", k)
    m = re.match(r'(\d*)([a-z]*)$', n)
    return (s, int(m.group(1) or 0), m.group(2))


# LE NOM DE L'OBJET SUIT LA COLONNE QUI L'APPELLE. Le gros plan porte
# le nom de ce qu'il montre, et ce nom se lit dans la langue de la
# colonne : « fumeyo » a gauche, « fumoir » au milieu, « smoking room »
# a droite. On releve donc les trois de la meme facon -- le substantif
# en gras qui precede le renvoi -- et la traduction anglaise, qui garde
# exactement les memes renvois que les deux autres, se laisse relever
# par le meme code, au nom de fichier pres.
SOURCES = [("io", "*-tabelo-*.tex"), ("fr", "*-tableau-*.tex"),
           # Meme jeton que le francais, autre dossier : voir renvoji.py.
           ("fr-CA", "*-tableau-*.tex"),
           ("en", "*-table-*.tex"), ("es", "*-cuadro-*.tex"),
           ("ru", "*-tablica-*.tex"), ("zh", "*-tubiao-*.tex"),
           ("ar", "*-lawha-*.tex"),
           # Meme jeton que l'arabe standard, autre dossier : voir
           # renvoji.py.
           ("arz", "*-lawha-*.tex"), ("hi", "*-talika-*.tex"),
           ("mr", "*-takta-*.tex"),
           ("te", "*-pattika-*.tex"),
           ("ko", "*-dopyo-*.tex"),
           ("ta", "*-attavanai-*.tex"),
           ("ur", "*-jadval-*.tex"),
           ("id", "*-bagan-*.tex"),
           ("pt", "*-quadro-*.tex"), ("bn", "*-sarani-*.tex"),
           ("ja", "*-zuhyo-*.tex"), ("pnb", "*-naqsha-*.tex"),
           ("pa", "*-sarni-*.tex"),
           ("tr", "*-tablo-*.tex"),
           ("eo", "*-tabelo-*.tex"),
           ("ia", "*-tabella-*.tex"),
           ("nl", "*-tabel-*.tex"),
           ("sv", "*-tabell-*.tex"),
           ("fi", "*-taulukko-*.tex"),
           ("ca", "*-taula-*.tex"),
           ("oc", "*-taula-*.tex"),
    ("uk", "*-tablycia-*.tex"),
    ("eu", "*-taula-*.tex"),
    ("ro", "*-tabelul-*.tex"),
    ("ga", "*-tabla-*.tex"),
    ("gl", "*-cadro-*.tex"),
    ("cs", "*-tabulka-*.tex"),
    ("lt", "*-lentele-*.tex"),
    # LE LUXEMBOURGEOIS REPREND LE JETON DU SUEDOIS, « tabell », parce
    # qu'il ecrit le mot de la meme facon. Le motif de nom de fichier
    # le connait donc deja ; seul ce couple manquait. Trois langues
    # partagent deja « taula » — le catalan, l'occitan et le basque —
    # et le glob est enracine dans texto/<langue>/ : deux dossiers
    # differents ne se melangent pas.
    ("lb", "*-tabell-*.tex"),
    # LE ROMANCHE REPREND LE JETON DE L'INTERLINGUA, « tabella ». Le
    # motif de nom de fichier le connait donc deja, comme il
    # connaissait « tabell » quand le luxembourgeois est arrive.
    # Quatrieme jeton partage de la serie ; le glob restant enracine
    # dans texto/<langue>/, deux dossiers ne se melangent pas.
    ("rm", "*-tabella-*.tex"),
    # L'ESTONIEN REPREND LE JETON DU NEERLANDAIS, « tabel ». Cinquieme
    # et dernier jeton partage de la serie des dix-sept ; le glob
    # restant enracine dans texto/<langue>/, texto/nl et texto/et ne
    # se melangent pas.
    ("et", "*-tabel-*.tex"),
    # LE VIETNAMIEN OUVRE LE RESTE DU PROGRAMME D'ETHNOLOGUE. Son
    # jeton, « bang », est le mot « bảng » depouille de ses signes,
    # comme « talika » l'est de « तालिका » et « naqsha » de « نقشہ » :
    # les noms de fichiers restent en ASCII, et c'est le dossier —
    # texto/vi — qui porte la langue. Le jeton est neuf ; aucun des
    # dix-sept precedents ne s'en approche.
    ("vi", "*-bang-*.tex"),
    # LE CANTONAIS prend « toubiu », le jyutping de « 圖表 » sans
    # ses tons. Le mandarin a « tubiao » : meme mot, deux lectures,
    # deux colonnes.
    ("yue", "*-toubiu-*.tex"),
    # L'ALLEMAND prend « tafel », qui n'est le jeton de personne : il
    # ressemble au « tabel » neerlandais et au « tabell » suedois sans
    # les egaler — un F la ou ils ont un B.
    ("de", "*-tafel-*.tex"),
    # L'ITALIEN prend « tavola », qui n'est le jeton de personne. Il
    # ressemble au « taula » que se partagent le catalan, l'occitan et
    # le basque — un V de plus — et au « tabella » de l'interlingua et
    # du romanche — un V au lieu d'un B.
    ("it", "*-tavola-*.tex")]


def construire():
    par_langue = {k: (relever(k, m) if (RACINE / "texto" / k).is_dir() else {})
                  for k, m in SOURCES}
    tabs = sorted({t for d in par_langue.values() for t in d})
    tout = {}
    for tab in tabs:
        cles = sorted({k for d in par_langue.values()
                       for k in d.get(tab, {})}, key=rang)
        tout[f"t{tab:02d}"] = {
            k: {lg: d.get(tab, {}).get(k, []) for lg, d in par_langue.items()}
            for k in cles}
    return tout


def attendus(tab):
    return set(relever("io", f"*-tabelo-{tab:02d}.tex").get(tab, {}))


def main(args):
    tout = construire()
    if args:
        tab = f"t{int(args[0]):02d}"
        for n, v in sorted(tout[tab].items(), key=lambda kv: rang(kv[0])):
            print("  " + f"{n:>6}  " + "  ".join(
                f"{' / '.join(v.get(k, [])) or '—':28s}" for k, _ in SOURCES))
        return
    (RACINE / "gravuri" / "objekti.json").write_text(
        json.dumps(tout, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    for tab, par in sorted(tout.items()):
        att = attendus(int(tab[1:]))
        tout_ = sum(1 for v in par.values() if all(v.get(k) for k, _ in SOURCES))
        print(f"  {tab}  {len(par):3d}/{len(att):3d} objets nommes, "
              f"dont {tout_:3d} dans les {len(SOURCES)} langues")
    n = sum(len(p) for p in tout.values())
    a = sum(len(attendus(int(t[1:]))) for t in tout)
    print(f"  TOTAL {n}/{a} = {100 * n // a} %")


if __name__ == "__main__":
    main(sys.argv[1:])
