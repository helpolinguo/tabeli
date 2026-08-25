#!/usr/bin/env python3
# ===================================================================
#  kolori.py — ce que le texte dit de la couleur, et ce que la planche
#  en montre.
#
#  Les planches ont ete coloriees par une machine qui n'avait pas lu
#  les Livrets. Elle a donc peint au vraisemblable, et le texte la
#  dement par endroits : « la reda lanterno (25) » du tableau 14 doit
#  etre rouge, « la blua robo (42) » du tableau 4 bleue, « nigra fumuro
#  (75) » du tableau 11 noire. Cet outil releve toutes les couleurs que
#  les deux volumes attachent a un objet numerote, va voir ce que la
#  couche de couleur porte a cet endroit, et dit ou les deux
#  s'accordent.
#
#  OU REGARDER. Le numero n'est pas SUR l'objet : il est pose a cote,
#  dans une reserve de blanc. Prendre la couleur au numero, ce serait
#  prendre celle de la reserve. On lit donc une COURONNE autour du
#  numero — d'un a trois corps de chiffre — et l'on y ecarte ce qui est
#  presque blanc (la reserve, le papier) et presque noir (le trait
#  grave, qui n'est pas de la couleur mais de l'encre).
#
#  CE QUE L'OUTIL NE DIT PAS. Il ne sait pas si la couleur trouvee
#  appartient a l'objet nomme ou a son voisin : une couronne de trois
#  corps de chiffre couvre plusieurs choses. Il ne sait pas davantage
#  que le « (65) » du tableau 13 est pose sur la marquise d'un hotel et
#  nomme un paquebot au large. Il signale donc, il ne corrige pas.
#
#  CE QUE L'ŒIL A TRANCHE se tient dans plates/colours.json, sous
#  « vidita », et l'outil le redit sous chaque ligne : « planche »
#  quand la peinture dement le livret et qu'il faudra la reprendre,
#  « mesure » quand la couronne s'est trompee, « akordo » quand les
#  deux disent la meme chose. Sur les vingt-cinq couleurs que les
#  livrets attachent a un objet numerote, onze demandent la reprise.
#
#  USAGE
#      python3 tools/kolori.py            # le releve et la comparaison
#      python3 tools/kolori.py --tabelo 14
# ===================================================================

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RACINE = Path(__file__).resolve().parent.parent

# LES COULEURS NOMMEES, et le ton qu'on leur demande. Le ton est donne
# en degres sur la roue des teintes, avec la saturation et la clarte
# attendues ; « blanka » et « nigra » n'ont pas de teinte et se jugent
# a la seule clarte.
TONS = {
    "reda":     (0, 0.30, None),
    "oranjea":  (25, 0.30, None),
    "flava":    (50, 0.30, None),
    "verda":    (110, 0.20, None),
    "blua":     (215, 0.18, None),
    "violea":   (275, 0.18, None),
    "purpurea": (315, 0.20, None),
    "rozea":    (345, 0.12, None),
    "bruna":    (25, 0.20, None),
    "griza":    (None, None, None),
    "nigra":    (None, None, 0.30),
    "blanka":   (None, None, 0.80),
}
FRANCAIS = {
    "reda": "rouge", "oranjea": "orange", "flava": "jaune",
    "verda": "vert", "blua": "bleu", "violea": "violet",
    "purpurea": "pourpre", "rozea": "rose", "bruna": "brun",
    "griza": "gris", "nigra": "noir", "blanka": "blanc",
}

# L'ADJECTIF SE DECLINE — « reda », « rede », « redi » — et il faut le
# prendre en MINUSCULE : « Blanko » est un nom de personne (le pere de
# Jacques, au tableau 5), « Blank Urso » l'enseigne d'une auberge.
ADJ = re.compile(
    r'(?<![A-Za-z])(' + '|'.join(sorted(TONS, key=len, reverse=True))
    .replace('a|', '|') + r')(?=\b)')
MOTS = re.compile(r'(?<![\w-])(' +
                  '|'.join(k[:-1] for k in sorted(TONS, key=len, reverse=True)) +
                  r')(?:a|e|i)(?![\w-])')
NUM = re.compile(r'\((\d+)\)')
BALISE = re.compile(r'\\[A-Za-z]+\*?(?:\{[^{}]*\})?|[{}]|%.*')


def texte(t):
    t = re.sub(r'%.*', '', t)
    # \textsuperscript{(12)} doit garder son numero.
    t = re.sub(r'\\textsuperscript\{(\([0-9]+\))\}', r'\1', t)
    t = re.sub(r'\\VUgras\{([^{}]*)\}', r'\1', t)
    # \cc RECOLLE, \nl SEPARE. Les deux marquent une fin de ligne du
    # fac-simile, mais \cc coupe un MOT et \nl coupe une locution.
    # Traites tous deux en blanc, « recou\cc verte » donnait « recou
    # verte » et le releve y voyait un vert -- la table du dessert au
    # tableau 4, les couverts au tableau 6 : deux couleurs qui
    # n'existent pas.
    # \ccplein est un \cc qui tombe en fin de PAGE : il faut le
    # prendre AVANT \cc, sinon on lui arrache sa tete et il reste
    # « plein » au milieu de la phrase.
    t = t.replace("\\ccplein\n", "").replace("\\ccplein", "")
    t = t.replace("\\cc\n", "").replace("\\cc", "")
    t = re.sub(r'\\nl\b', ' ', t)
    t = BALISE.sub(' ', t)
    return re.sub(r'\s+', ' ', t)


# LES TROIS FACONS DE DIRE LA COULEUR, et il faut les trois.
#
#  * L'EPITHETE ANTEPOSEE, celle de l'ido : « blua cielo (1) », « nigra
#    redingoto (57) ». Au plus deux mots entre l'adjectif et le numero
#    -- une fenetre plus large prenait le premier numero venu, et
#    donnait le noir aux nuages dans « la nigra silueto salias sur la
#    blanka nubi (67) », ou le noir est a la silhouette.
#
#  * L'EPITHETE POSTPOSEE, celle du francais : « le ciel (1) bleu »,
#    « la lanterne (25) rouge », « les fromages de Hollande (9) a la
#    croute rouge ». Le numero PRECEDE alors l'adjectif. Trois mots au
#    plus, et l'on remonte la coordination : « la robe (42) et a la
#    pelerine (41) bleues » donne le bleu aux deux.
#
#  * L'ATTRIBUT, dans les deux langues : « Tote rozea e blanka esas ta
#    persikieri (18) ed abrikotieri (19) », « Ils sont tout roses et
#    tout blancs ces pechers (18) et ces abricotiers (19) ». La couleur
#    porte alors sur TOUT ce que la phrase enumere, et l'on lit jusqu'au
#    point.
#
# Le francais n'est pas un doublon de l'ido : il nomme des couleurs que
# l'ido tait -- « De gros nuages (56) noirs » au tableau 8, « une teinte
# verte » a la futaie (25) du tableau 9 -- et l'ido en nomme que le
# francais tait. On releve donc les deux, et l'on dit lequel parle.
ANTE = re.compile(r"^\s*(?:[\w'\u2019-]+\s+){0,2}[\w'\u2019-]*\s*\((\d+)\)")
POST = re.compile(r"\((\d+)\)(?:[\s,]*(?:[\w'\u2019-]+[\s,]+){0,3})$")
COORD = re.compile(r"\((\d+)\)(?:[^.()]{0,40}?\b(?:et|ed?)\b[^.()]{0,40}?)$")
ETRE = re.compile(r"\b(?:esas|sont|est|semblas|semble)\b")
# LE PRONOM RELATIF COUPE LA COORDINATION. « seglo-navi (64) ed enorma
# paketboto (65) DI QUA la nigra silueto » : le noir est a la silhouette
# du paquebot, et la coordination qui le precede ne le reclame pas. Sans
# cette barriere, le releve donnait aussi le noir aux voiliers.
RELATIF = re.compile(r"\b(?:qua|qui|que|quan|dont|donta|kies)\b")

# LE FRANCAIS ANTEPOSE AUSSI, ET SON DETERMINANT LE DIT. « emportait en
# NOIRS tourbillons la fumee (1) » : l'adjectif regarde devant lui, et
# la tournure postposee lui donnait l'enseigne (3) qui precede. Un
# article ou une preposition juste avant la couleur signe l'anteposee ;
# un substantif -- « a la croute rouge », « nuages (56) noirs » --
# signe la postposee. « tout » n'est pas de la liste : « deux ramoneurs
# (91) TOUT noirs de suie » est bien une postposee.
DEVANT = re.compile(
    r"\b(?:de|du|des|en|par|avec|sans|au|aux|le|la|les|l|d|un|une|ce|ces"
    r"|cet|cette|son|sa|ses|leur|leurs|mon|ma|mes|nos|vos|deux|trois"
    r"|quelques|plusieurs|gros|grosse|petits?|petites?)['\u2019\s]+$",
    re.I)

RAD = {
    "io": ["red", "oranje", "flav", "verd", "blu", "viole", "purpure",
           "roze", "brun", "griz", "nigr", "blank"],
    "fr": ["rouge", "orang", "jaune", "vert", "bleu", "violet", "pourpre",
           "ros", "brun", "gris", "noir", "blanc", "blanch"],
}
FIN = {"io": r"(?:a|e|i)", "fr": r"(?:e?s?)"}
VERS_IO = {"rouge": "reda", "orang": "oranjea", "jaune": "flava",
           "vert": "verda", "bleu": "blua", "violet": "violea",
           "pourpre": "purpurea", "ros": "rozea", "brun": "bruna",
           "gris": "griza", "noir": "nigra", "blanc": "blanka",
           "blanch": "blanka"}
MOTS = {lg: re.compile(r"(?<![\w-])(" +
                       "|".join(sorted(r, key=len, reverse=True)) +
                       r")" + FIN[lg] + r"(?![\w-])",
                       0 if lg == "io" else re.I)
        for lg, r in RAD.items()}

SOURCES = [("io", "*-tabelo-*.tex"), ("fr", "*-tableau-*.tex")]


# LE RENVOI QUE LA PLANCHE NE PORTE PAS. « les plates-bandes (150) »,
# au tableau 5, sont gravees « 50 » : la couleur doit aller chercher le
# numero qu'on montrera, non celui qu'on lit. plates/corrections.json tient
# la table, et numeri.py la lit de meme.
def korekti():
    f = RACINE / "plates" / "corrections.json"
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding="utf-8")).items() if not k.startswith("_")}


KOREKTI = korekti()


def korekti_renvojo(tab, cle=""):
    """{lu: a lire} pour UN BLOC : les corrections qui valent pour tout
    le tableau, plus celles que ce bloc-ci porte seul.
    """
    t = KOREKTI.get(f"t{tab:02d}", {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out


# LES PLANCHES A PLUSIEURS SCENES. Six tableaux montrent deux vignettes
# ou davantage, et chacune recommence sa numerotation a 1 : le « (18) »
# de la premiere scene et celui de la troisieme ne montrent pas le meme
# objet. Sans la scene, les vingt-huit couleurs des tableaux 3, 4, 6, 7,
# 8 et 9 ne trouvaient aucune boite sur la planche, numbers.json les
# rangeant sous « c1:18 ». plates/scenes.json dit quels tableaux sont
# dans ce cas.
def a_ceni():
    f = RACINE / "plates" / "scenes.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


CENI = a_ceni()

# LA PAGE QUI COUPE UN MOT. \ccplein ferme la page sur un mot coupe, et
# quatre lignes de service s'intercalent avant la suite. On les efface
# d'abord, sinon le mot reste en deux morceaux -- et un bloc « suite »
# viendrait couper une phrase que rien ne coupe.
SAUT = re.compile(
    r'\\ccplein\s*\n\\end\{VUpage\}.*?'
    r'^%%K\s+\S+\s+\S+\s+suite\s*\n\\VUcontinue\s*\n',
    re.S | re.M)


def koloroj():
    f = RACINE / "plates" / "colours.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def ecartes():
    """{tableau: [(mot, fragment)]} — voir plates/colours.json."""
    return koloroj().get("ecarte", {})


# CE QUE L'ŒIL A VU PREVAUT SUR CE QUE LA COURONNE MESURE. La mesure ne
# sait pas que le (65) du tableau 13 est pose sur la marquise d'un hotel
# et nomme un paquebot au large ; elle dit « NON » et n'a rien vu. Le
# verdict tenu a la main dans colours.json tranche : « planche » quand
# c'est a la planche d'etre reprise, « mesure » quand la planche dit
# deja ce que le livret dit.
VERDIKTO = {"planche": "A REPEINDRE",
            "mesure": "la mesure a tort",
            "akordo": "vu, et la planche dit vrai"}


def vidita():
    """{« t13/65 »: (verdict, ce qu'on a vu)}."""
    return {k: tuple(v) for k, v in koloroj().get("vidita", {}).items()}


def anteposee(apres):
    """Le numero que l'epithete anteposee regarde devant elle."""
    m = ANTE.match(apres)
    return [int(m.group(1))] if m else []


def postposee(avant, lg="io", mot=""):
    """Les numeros que l'epithete postposee reclame derriere elle."""
    m = POST.search(avant)
    if not m:
        return []
    if lg == "fr" and DEVANT.search(avant):
        return []
    ns = [int(m.group(1))]
    # LA COORDINATION REMONTE : « la robe (42) et a la pelerine (41)
    # bleues » -- l'adjectif s'accorde aux deux, et les deux le veulent.
    # On regarde apres le NUMERO, non apres la fenetre : POST etant
    # ancree sur la fin du texte qui precede, m.end() en designait le
    # bout et la tranche etait toujours vide -- la barriere du relatif
    # ne se levait jamais, et les voiliers (64) restaient noirs.
    if RELATIF.search(avant[m.end(1):]):
        return ns
    # EN IDO, LA POSTPOSEE N'EXISTE QUE DERRIERE UN RELATIF. La langue
    # antepose son epithete : quand l'adjectif suit un numero sans
    # relatif entre les deux, c'est qu'il en qualifie un autre, et cet
    # autre n'est pas toujours numerote. « nigra redingoto (57) e
    # blanka jileto » -- le gilet n'a pas de renvoi, et le blanc allait
    # a la redingote ; « brancho de filiko (55) e bela rozea brancheto
    # di eriko (57) » -- le rose est a la bruyere, et il allait a la
    # fougere. On ne garde donc, en ido, que la tournure de la
    # subordonnee : « paketboto (65) di qua la nigra silueto ».
    if lg == "io":
        return []
    # LA COORDINATION SE LIT AU PLURIEL DE L'ADJECTIF. « la robe (42)
    # et a la pelerine (41) BLEUES » les prend toutes deux ; « un brin
    # de fougere (55) tres curieuse et un brin de bruyere (57) ROSE »
    # n'en prend qu'un, et le rose n'est pas a la fougere. L'accord dit
    # a lui seul jusqu'ou l'epithete porte -- « gris », invariable, est
    # le seul mot qui mente, et il ne parait nulle part.
    if not mot.lower().endswith("s"):
        return ns
    reste = avant[:m.start()]
    while True:
        c = COORD.search(reste)
        if not c:
            break
        ns.append(int(c.group(1)))
        reste = reste[:c.start()]
    return ns


def numeros(t, i, j, lg="io"):
    """Les numeros qu'une couleur atteint depuis la position (i, j)."""
    avant, apres = t[max(0, i - 90):i], t[j:j + 90]
    # L'ATTRIBUT D'ABORD : s'il y a un verbe d'etat tout pres, la
    # couleur porte sur l'enumeration entiere, et non sur le premier
    # substantif venu.
    #
    # ENCORE FAUT-IL QUE LE VERBE SOIT LE SIEN. « l'etalage EST garni de
    # fromages de Hollande (9) a la croute rouge » a bien un « est »
    # dans la fenetre, mais il est a l'etalage, non a la croute : un
    # numero le separe de l'adjectif. Une ponctuation forte les separe
    # de meme : « De gros nuages (56) NOIRS montent dans le ciel ; ils
    # SONT sillonnes par les zigzags de l'eclair (55) » -- le verbe est
    # a la proposition suivante, et le noir allait a l'eclair. On exige
    # donc que rien ne tombe entre l'adjectif et son verbe, ni renvoi ni
    # point-virgule -- et « la reda lanterno (25) e la grosa pipo qua
    # ESAS uzata kom insigno (26) » cesse de peindre l'enseigne.
    for m in ETRE.finditer(t[max(0, i - 40):j + 40]):
        d, g = max(0, i - 40) + m.start(), max(0, i - 40) + m.end()
        entre = t[min(g, i):max(d, j)]
        if any(c in entre for c in "(;:."):
            continue
        phrase = apres.split(".")[0]
        ns = [int(x) for x in re.findall(r"\((\d+)\)", phrase)]
        if ns:
            return ns
        break
    # L'ORDRE DES DEUX TOURNURES SUIT LA LANGUE. L'ido antepose son
    # epithete, le francais la postpose ; essayer l'anteposee d'abord
    # des deux cotes donnait la croute rouge aux camemberts, « a la
    # croute rouge, de camemberts (10) » -- l'adjectif regardait devant
    # lui alors qu'il appartient a ce qui le precede. Chaque langue
    # commence donc par sa tournure propre, et se rabat sur l'autre :
    # le francais dit aussi « en noirs tourbillons la fumee (1) ».
    tour = [lambda: anteposee(apres), lambda: postposee(avant, lg, t[i:j])]
    if lg == "fr":
        tour.reverse()
    for f in tour:
        ns = f()
        if ns:
            return ns
    return []


def relever():
    """Les couples (tableau, numero, couleur) que les livrets enoncent.

    ON LIT BLOC PAR BLOC, et non le fichier d'un trait : c'est la cle du
    bloc qui dit la scene, et sans la scene un numero de tableau 3 ne
    designe rien. La coupure a un autre merite : une couleur ne
    reclamera pas un numero de l'alinea voisin.
    """
    hors = ecartes()
    par = {}
    for lg, motif in SOURCES:
        for f in sorted((RACINE / "text" / lg).glob(motif)):
            tab = int(re.search(r"-(\d+)\.tex$", f.name).group(1))
            cle = f"t{tab:02d}"
            brut = SAUT.sub("\\\\cc\\n", f.read_text(encoding="utf-8"))
            sceno = ""
            parts = re.split(r"^%%K (\S+)", brut, flags=re.M)
            for i in range(1, len(parts), 2):
                mk = re.match(r"t\d\d-(c\d+)-", parts[i])
                if mk:
                    sceno = mk.group(1)
                kor = korekti_renvojo(tab, parts[i])
                t = texte(parts[i + 1])
                for m in MOTS[lg].finditer(t):
                    mot = m.group(0)
                    kunteksto = re.sub(
                        r"\s+", " ",
                        t[max(0, m.start() - 45):m.end() + 55]).strip()
                    if any(a.lower() == mot.lower() and b in kunteksto
                           for a, b in hors.get(cle, [])):
                        continue
                    coul = (m.group(1) + "a") if lg == "io" \
                        else VERS_IO[m.group(1).lower()]
                    for n in numeros(t, m.start(), m.end(), lg):
                        n = kor.get(str(n), str(n))
                        k = f"{sceno}:{n}" if cle in CENI and sceno else n
                        d = par.setdefault((tab, k, coul),
                                           {"tabelo": tab, "numero": k,
                                            "koloro": coul, "dit": [],
                                            "kunteksto": kunteksto})
                        if lg not in d["dit"]:
                            d["dit"].append(lg)
    return sorted(par.values(),
                  key=lambda r: (r["tabelo"], str(r["numero"])))


def teinte(rgb):
    """(teinte en degres, saturation, clarte) d'un tableau RGB 0-255."""
    a = rgb.astype(np.float32) / 255.0
    mx = a.max(1)
    mn = a.min(1)
    d = mx - mn
    h = np.zeros(len(a), np.float32)
    r, g, b = a[:, 0], a[:, 1], a[:, 2]
    nz = d > 1e-6
    i = nz & (mx == r)
    h[i] = (60 * ((g[i] - b[i]) / d[i])) % 360
    i = nz & (mx == g)
    h[i] = 60 * ((b[i] - r[i]) / d[i]) + 120
    i = nz & (mx == b)
    h[i] = 60 * ((r[i] - g[i]) / d[i]) + 240
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def lire_couronne(couleur, x, y, w, h, corps, dedans=1.0, dehors=3.0):
    """La couleur dominante autour d'un numero, reserve exclue."""
    cx, cy = x + w / 2, y + h / 2
    R = round(dehors * corps)
    x0, y0 = max(0, round(cx) - R), max(0, round(cy) - R)
    x1 = min(couleur.shape[1], round(cx) + R)
    y1 = min(couleur.shape[0], round(cy) + R)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return None
    f = couleur[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.hypot(xx - cx, yy - cy)
    m = (d >= dedans * corps) & (d <= dehors * corps)
    pix = f[m]
    if len(pix) < 40:
        return None
    hh, ss, vv = teinte(pix)
    # LE TRAIT N'EST PAS DE LA COULEUR, ni le papier de la reserve.
    bon = (vv > 0.14) & (vv < 0.97)
    if bon.sum() < 30:
        return None
    hh, ss, vv = hh[bon], ss[bon], vv[bon]
    # La teinte se moyenne en rond, sinon le rouge s'annule avec
    # lui-meme de part et d'autre de zero.
    a = np.deg2rad(hh)
    poids = ss
    if poids.sum() < 1e-6:
        poids = np.ones_like(ss)
    hm = np.rad2deg(np.arctan2((np.sin(a) * poids).sum(),
                               (np.cos(a) * poids).sum())) % 360
    return float(hm), float(np.median(ss)), float(np.median(vv))


def accord(coul, mesure, tol=45):
    """Le ton mesure repond-il au ton nomme ?"""
    h, s, v = mesure
    t, smin, vmax = TONS[coul]
    if coul == "nigra":
        return v <= 0.34, f"clarte {v:.2f}"
    if coul == "blanka":
        return v >= 0.72, f"clarte {v:.2f}"
    if coul == "griza":
        return s <= 0.16, f"saturation {s:.2f}"
    if s < smin:
        return False, f"trop pale (saturation {s:.2f}, teinte {h:.0f}°)"
    ecart = min(abs(h - t), 360 - abs(h - t))
    return ecart <= tol, f"teinte {h:.0f}° au lieu de {t}° (ecart {ecart:.0f}°)"


def main(args):
    releve = relever()
    if "--tabelo" in args:
        n = int(args[args.index("--tabelo") + 1])
        releve = [r for r in releve if r["tabelo"] == n]
    num = json.loads((RACINE / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    obj = json.loads((RACINE / "plates" / "objects.json")
                     .read_text(encoding="utf-8"))
    par_tab = {}
    for cle, v in num.items():
        par_tab.setdefault(cle[:3], []).append((cle, v))
    vu = vidita()
    caches = {}
    accords = desaccords = sans = 0
    lignes = []
    for r in releve:
        tab = f"t{r['tabelo']:02d}"
        trouve = None
        for cle, v in par_tab.get(tab, []):
            b = v["numeri"].get(r["numero"])
            if b:
                trouve = (cle, v, b)
                break
        if not trouve:
            sans += 1
            continue
        cle, v, b = trouve
        if cle not in caches:
            im = Image.open(RACINE / "plates" / "kovri" /
                            f"{cle}-koloro.png").convert("RGB")
            caches[cle] = np.asarray(
                im.resize((v["largeur"], v["alteso"]), Image.LANCZOS))
        C = caches[cle]
        m = lire_couronne(C, b[0] * v["largeur"], b[1] * v["alteso"],
                          b[2] * v["largeur"], b[3] * v["alteso"], v["corpo"])
        if m is None:
            sans += 1
            continue
        ok, dit = accord(r["koloro"], m)
        accords += ok
        desaccords += not ok
        # UN NUMERO PORTE PARFOIS DEUX NOMS. Le « (19) » du tableau 3
        # est le presbytere pour un alinea et les abricotiers pour un
        # autre ; n'en montrer qu'un donnait a lire « rose presbytere ».
        n_obj = obj.get(tab, {}).get(r["numero"], {})
        nom = n_obj.get("fr") or n_obj.get("io") or ["—"]
        v = vu.get(f"{tab}/{r['numero']}")
        lignes.append((ok, tab, r["numero"], r["koloro"],
                       " / ".join(nom), dit, v))
    for ok, tab, n, c, nom, dit, v in sorted(lignes,
                                             key=lambda x: (x[0], x[1])):
        print(f"  {'  ' if ok else 'NON'}  {tab} ({str(n):>5})  "
              f"{FRANCAIS[c]:<8} {nom:<34} {dit}")
        if v:
            print(f"        {VERDIKTO[v[0]]} : {v[1]}")
    a_reprendre = sum(1 for l in lignes if l[6] and l[6][0] == "planche")
    print(f"\n  {accords} accords, {desaccords} desaccords, "
          f"{sans} sans position sur la planche "
          f"(sur {len(releve)} couleurs enoncees)")
    print(f"  {a_reprendre} endroits ou la planche dement le livret, "
          f"{len(lignes) - sum(1 for l in lignes if l[6])} pas encore regardes")



if __name__ == "__main__":
    main(sys.argv[1:])
