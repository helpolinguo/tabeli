#!/usr/bin/env python3
# ===================================================================
#  numeri.py — retrouver sur une planche murale les numeros d'objets.
#
#  Chaque planche porte, pose contre l'objet qu'il designe, un petit
#  numero compose : c'est a lui que renvoient les « (N) » du texte.
#  Pour qu'un clic sur « (12) » puisse montrer l'objet 12, il faut
#  savoir OU se trouve le 12 sur la planche. C'est ce que fait cet
#  outil, et il rend un rapport de ce qu'il a lu, planche par planche.
#
#  CE QUE L'OUTIL NE FAIT PAS. Il ne lit pas tous les numeros — loin
#  de la. Sur les planches aerees il en trouve huit sur dix, sur les
#  plus chargees deux ou trois. La raison tient au dessin lui-meme :
#  le numero est pose dans une petite reserve de blanc, et quand la
#  gravure est dense cette reserve se referme, le chiffre touche une
#  hachure, et rien ne le distingue plus d'un fragment de dessin.
#  On rend donc la liste de CE QU'ON A LU, avec sa planche de
#  controle ; ce qui manque reste sans gros plan plutot que d'en
#  recevoir un faux.
#
#  LA METHODE, en trois temps :
#
#  1. LES ILOTS. Le trait est binaire (l'outil travaille sur la
#     couche de trait rendue par gravuri.py, ou l'encre vaut 255).
#     On prend les composantes connexes de la taille d'un chiffre,
#     et on garde celles qu'un anneau de blanc separe du reste :
#     c'est la reserve de l'imprimeur qui sert de signature.
#
#  2. LA FORME. Chaque ilot est ramene a une vignette de 40x32 et
#     compare aux dix modeles de outils/chifri.npz. Ces modeles ne
#     sont pas dessines a la main : ils sortent d'un regroupement de
#     1429 ilots preleves sur les quinze planches, la fonte etant la
#     meme partout. Un « 1 » n'est qu'une barre, et les hachures
#     verticales lui ressemblent : il porte donc un seuil a part.
#
#  3. LE VOISINAGE. Les chiffres d'un meme nombre se suivent sur la
#     meme ligne de base, a moins d'un demi-corps l'un de l'autre.
#     On les recolle, puis on ne garde QUE les nombres attendus —
#     ceux que le texte du tabelo appelle — et lus une seule fois.
#     Un nombre lu deux fois est un nombre dont on ne sait rien.
#
#  USAGE
#      python3 outils/numeri.py                  # toutes les planches
#      python3 outils/numeri.py t05-apar-1       # une seule
#
#  Ecrit gravuri/numeri.json (les positions, en fraction de la
#  largeur et de la hauteur de la planche, donc valables a toute
#  echelle) et, dans gravuri/kontrolo/, une planche de controle par
#  gravure : chaque numero lu y est montre dans son decoupe, avec ce
#  que la machine a cru lire. C'est la qu'on verifie.
# ===================================================================

import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

RACINE = Path(__file__).resolve().parent.parent
KOVRI = RACINE / "gravuri" / "kovri"
KONTROLO = RACINE / "gravuri" / "kontrolo"

H, W = 40, 32
# Un « 1 » sans empattement est une barre, et une planche gravee en
# est pleine. On lui demande donc davantage qu'aux autres.
SEUIL = 0.80
SEUIL_UN = 0.86



# LA PLANCHE DE TRAVAIL. Tant qu'un tableau n'a pas ete repris sur la
# numerisation d'origine, on travaille sur la couche de trait tiree du
# PDF colorise, ou l'encre vaut 255. Des qu'il l'a ete, c'est le
# fac-simile lui-meme qu'on regarde, et l'encre y est SOMBRE. Les deux
# outils qui montrent des decoupes a l'oeil passent donc par ici, et
# n'ont plus a savoir d'ou vient l'image.
def neta(cle):
    return RACINE / "originali" / "kovri" / f"{cle}-neta.png"


def repris(cle):
    """Ce tableau a-t-il ete repris sur sa numerisation d'origine ?"""
    return neta(cle).exists()


def planche(cle):
    """L'image telle que l'oeil doit la voir : l'encre en SOMBRE."""
    if repris(cle):
        return Image.open(neta(cle)).convert("L")
    return ImageOps.invert(Image.open(KOVRI / f"{cle}-trako.png").convert("L"))


def enko(cle):
    """La densite d'encre en flottant : fort = encre."""
    return 255.0 - np.asarray(planche(cle)).astype(np.float32)


def modeles():
    d = np.load(RACINE / "outils" / "chifri.npz")
    noms = [c for c in d.files for _ in range(len(d[c]))]
    pile = np.stack([m for c in d.files for m in d[c]]).reshape(len(noms), -1)
    return noms, pile / np.linalg.norm(pile, axis=1, keepdims=True)


NOMS, PILE = modeles()


def vignette(v):
    """Ramene un ilot a la vignette de reference, hauteur imposee."""
    h, w = v.shape
    nw = max(1, min(W, round(w * H / h)))
    r = cv2.resize(v.astype(np.float32), (nw, H), interpolation=cv2.INTER_AREA)
    c = np.zeros((H, W), np.float32)
    o = (W - nw) // 2
    c[:, o:o + nw] = r
    return c.ravel() / 255.0


def classer(v):
    x = vignette(v)
    n = np.linalg.norm(x)
    if n == 0:
        return None, 0.0
    s = PILE @ (x / n)
    i = int(s.argmax())
    return NOMS[i], float(s[i])


def ilots(enc, hlo, hhi, rayon=5, tolerance=0.10):
    """Composantes de la taille d'un chiffre qu'un blanc isole."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(enc, 8)
    cand = [i for i in range(1, n)
            if hlo <= st[i, 3] <= hhi
            and 0.14 * hlo <= st[i, 2] <= 1.3 * hhi
            and st[i, 4] >= 0.18 * st[i, 2] * st[i, 3]]
    # L'anneau ne doit contenir aucune encre ETRANGERE : le chiffre
    # voisin, lui, a le droit d'y etre, sans quoi « 18 » ne serait
    # jamais vu — ses deux chiffres se tiennent a cinq points l'un de
    # l'autre.
    mc = np.isin(lab, cand)
    out = []
    for i in cand:
        x, y, w, h, _ = st[i]
        y0, y1 = max(0, y - rayon), min(enc.shape[0], y + h + rayon)
        x0, x1 = max(0, x - rayon), min(enc.shape[1], x + w + rayon)
        au = enc[y0:y1, x0:x1].astype(bool) & ~mc[y0:y1, x0:x1]
        au[y - y0:y - y0 + h, x - x0:x - x0 + w] = False
        if au.sum() / max(1, au.size - w * h) < tolerance:
            out.append((x, y, w, h,
                        (lab[y:y + h, x:x + w] == i).astype(np.uint8) * 255))
    return out


def hauteur(enc, depart=38):
    """La hauteur des chiffres, mesuree sur la planche elle-meme.

    Elle n'est pas la meme partout : 29 points sur le second plan du
    tableau 5, 46 sur le tableau 6. La chercher evite de rater les
    unes et de mal decouper les autres. On part de la valeur courante
    et on converge en trois tours ; le « 1 » est ecarte de la mesure,
    sa hauteur etant la moins sure.
    """
    h = float(depart)
    for _ in range(3):
        bons = [(y2, cl) for _, _, _, y2, v in
                ilots(enc, round(0.62 * h), round(1.55 * h), 5, 0.09)
                for cl, s in [classer(v)] if s >= 0.88 and cl != '1']
        if len(bons) < 8:
            return round(h)
        neuf = float(np.median([b[0] for b in bons]))
        if abs(neuf - h) < 0.6:
            h = neuf
            break
        h = neuf
    return round(h)


def grouper(gl):
    """Recolle les chiffres voisins en nombres."""
    rest = sorted(gl, key=lambda g: (g[1], g[0]))
    nums = []
    while rest:
        grp = [rest.pop(0)]
        bouge = True
        while bouge:
            bouge = False
            for b in list(rest):
                for c in grp:
                    x1, y1, w1, h1 = c[:4]
                    x2, y2, w2, h2 = b[:4]
                    hh = min(h1, h2)
                    chev = min(y1 + h1, y2 + h2) - max(y1, y2)
                    ecart = max(x1, x2) - min(x1 + w1, x2 + w2)
                    if (chev > 0.55 * hh and -0.3 * hh <= ecart < 0.55 * hh
                            and abs(h1 - h2) < 0.45 * hh):
                        grp.append(b)
                        rest.remove(b)
                        bouge = True
                        break
                else:
                    continue
                break
        grp.sort(key=lambda g: g[0])
        nums.append(grp)
    return nums


# LE NOMBRE TRONQUE EST LA FAUTE LA PLUS DANGEREUSE, parce qu'elle est
# silencieuse : sur le tableau 14 on lisait « 2 » la ou la planche porte
# « 12 », et « 6 » la ou elle porte « 60 ». Le chiffre voisin, colle a
# une hachure, n'avait pas ete vu, et le nombre tronque se trouvait etre
# lui aussi dans la liste attendue. Rien ne le signalait.
#
# On regarde donc la case adjacente, a gauche et a droite. Non pas
# « y a-t-il de l'encre ? » — une gravure en est pleine, et la question
# fait rejeter les bonnes lectures autant que les mauvaises — mais
# « y a-t-il un CHIFFRE ? », par le meme filtre adapte que partout
# ailleurs. Si oui, le nombre continue : on essaie de le lire en entier,
# et on ne le garde que si le nombre allonge est, lui, attendu. Sinon on
# jette la lecture plutot que d'en garder une moitie.
SEUIL_VOISIN = 0.42
# L'avance minimale du chiffre retenu sur son suivant, pour allonger.
MARGE_VOISIN = 0.05
# L'avance qu'il faut a une lecture sur sa rivale pour l'emporter.
ECART_PREUVE = 0.05
BASE = None


# DEUX JEUX DE MODELES, parce qu'il y a deux encres. Le pochoir tire
# du PDF colorise a des contours nets ; le fac-simile a l'encre grise,
# les pleins qui bavent et les delies qui s'effacent. Un gabarit taille
# dans l'un ne se pose pas dans l'autre : sur le gris, le filtre adapte
# du pochoir marque 0.24 la ou il devrait marquer pres de 1. On tient
# donc les deux, et GRIS dit lequel sert -- c'est l'appelant qui le
# sait, puisque c'est lui qui sait quelle planche il regarde.
GRIS = False


def _base():
    global BASE
    if BASE is None:
        BASE = {}
    fich = "chifri-gris.npz" if GRIS else "chifri.npz"
    if fich not in BASE:
        d = np.load(RACINE / "outils" / fich)
        b = {}
        for c in d.files:
            # ON RAMENE LE MODELE A UN PLEIN DE 1. Les modeles du
            # pochoir sont des moyennes de decoupes, ceux du gris des
            # centres de groupes DEJA NORMES : leur plein vaut cinq
            # centiemes, et le gabarit, qui prend le trait a la moitie
            # du plein, n'y trouvait plus rien du tout.
            m = d[c].mean(0)
            m = m / max(1e-6, float(m.max()))
            col = m.max(0) > 0.15
            b[c] = m[:, col.argmax(): len(col) - col[::-1].argmax()]
        BASE[fich] = b
    return BASE[fich]


def gabarit(c, corps, marge=10):
    """Un chiffre, et autour de lui la reserve de blanc qui le porte.

    Le modele vaut +1 sur le trait et -1 tout autour, chaque part
    ramenee a sa surface : un chiffre parfaitement pose marque 1, une
    case pleine d'encre 0. C'est ce qui rend le filtre insensible aux
    hachures, qui remplissent la reserve autant que le trait.
    """
    m = _base()[c]
    g = cv2.resize(m, (max(1, round(m.shape[1] * corps / H)), corps),
                   interpolation=cv2.INTER_AREA)
    q = np.zeros((corps + 2 * marge, g.shape[1] + 2 * marge), np.float32)
    q[marge:marge + corps, marge:marge + g.shape[1]] = g
    p = (q >= 0.5).astype(np.float32)
    n = 1.0 - p
    return p / p.sum() - n / n.sum(), marge, g.shape[1]


def voisin(enc, cx, cy, corps, ray=6):
    """Le meilleur chiffre de la case adjacente.

    Rend (score, chiffre, boite, marge) — la marge etant l'avance du
    chiffre retenu sur son suivant. Elle decide seule des allongements :
    sur le tableau 14 on a lu « 69 » la ou la planche porte « 60 »,
    parce que le 0 et le 9 se valaient presque. Quand deux chiffres se
    disputent la case, on n'allonge pas.
    """
    scores = []
    best, qui, pos = -9.0, None, None
    for c in _base():
        T, M, L = gabarit(c, corps)
        x0, y0 = int(cx) - M - ray, int(cy) - M - ray
        h, w = T.shape
        if (x0 < 0 or y0 < 0 or x0 + w + 2 * ray > enc.shape[1]
                or y0 + h + 2 * ray > enc.shape[0]):
            continue
        r = cv2.matchTemplate(enc[y0:y0 + h + 2 * ray, x0:x0 + w + 2 * ray],
                              T, cv2.TM_CCORR)
        _, mx, _, loc = cv2.minMaxLoc(r)
        scores.append(float(mx))
        if mx > best:
            best, qui, pos = float(mx), c, (x0 + loc[0] + M, y0 + loc[1] + M, L)
    scores.sort(reverse=True)
    marge = (scores[0] - scores[1]) if len(scores) > 1 else 0.0
    return best, qui, pos, marge



# COMMENT LE FAC-SIMILE APPELLE UN NUMERO. Trois formes, et il a fallu
# les trois :
#
#   (18)              la forme ordinaire ;
#   (9, 11, 12)       UN GROUPE — « les tableaux muraux (9, 11, 12) » —
#                     qui vaut pour trois objets a la fois. On n'en
#                     lisait aucun, et le 9 du tableau 1 n'etait appele
#                     nulle part ailleurs : il manquait tout entier ;
#   41)               une parenthese ouvrante qui manque. Trois endroits
#                     dans les deux livrets. Coquille du releve ou sorte
#                     cassee de l'imprimeur, on ne peut le dire sans le
#                     fac-simile sous les yeux — alors on ne touche pas
#                     a la source, et l'on se contente de reconnaitre le
#                     renvoi ;
#   94 bis            UN NUMERO QUI N'EST PAS UN NOMBRE. Le graveur a
#                     ajoute deux outils apres coup, et plutot que de
#                     renumeroter toute la planche il les a glisses
#                     entre les autres : « 94bis » est grave sur le
#                     ciseau, entre le 94 et le 95, et « 95bis » sur le
#                     maillet. Il y en a deux dans tout l'ouvrage, tous
#                     deux au tableau 5. Leur cle est « 94bis », et le
#                     lecteur automatique ne les lira jamais -- il ne
#                     connait que des chiffres.
#
# Un groupe coupe par une fin de ligne est compose en DEUX exposants,
# « (9, 11, » puis « 12) ». On les recolle avant de lire.
RECOLLE_EXPO = re.compile(
    r'\\textsuperscript\{([^{}]*,)\}\s*(?:\\nl|\\cc)?\s*\n?\s*'
    r'\\textsuperscript\{([^{}]*)\}')
EXPO = re.compile(r'\\textsuperscript\{([^{}]*)\}')
SUITE = re.compile(r'\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*,?'
                   r'(?:\s*(?:\\textit\{)?bis\}?)?\s*\)?\s*$')
CHIFRO = re.compile(r'\d{1,3}')
BIS = re.compile(r'\bbis\b')


def renvoji(texte):
    """Tous les numeros qu'un texte appelle, sous quelque forme que ce
    soit. Rend la liste dans l'ordre du texte, doublons compris."""
    t = texte
    for _ in range(3):
        t = RECOLLE_EXPO.sub(r'\\textsuperscript{\1 \2}', t)
    out = []
    for c in EXPO.findall(t):
        if SUITE.fullmatch(c.strip()):
            ns = [int(x) for x in CHIFRO.findall(c)]
            # « 94 bis » ne vaut pas 94 : c'est un objet a part, glisse
            # entre le 94 et le 95. Le « bis » se rapporte au dernier
            # nombre du renvoi.
            if ns and BIS.search(c):
                ns[-1] = f"{ns[-1]}bis"
            out += ns
    # Les renvois que le fac-simile n'a pas mis en exposant -- il y en a
    # sept, tous du cote ido.
    for c in re.findall(r'\((\d{1,3}(?:\s*,\s*\d{1,3})*)\)', EXPO.sub('', t)):
        out += [int(x) for x in CHIFRO.findall(c)]
    return out


# UNE PLANCHE PEUT PORTER PLUSIEURS SCENES, et chacune recommence sa
# numerotation a 1 : le tableau 6 a cinq vignettes, le 3, le 4, le 7, le
# 8 et le 9 en ont deux. Le meme « 39 » s'y lit donc deux fois, et le
# lecteur, qui croyait chaque numero unique, en jetait l'une des deux ou
# rendait l'autre au hasard. gravuri/ceni.json donne la place de chaque
# scene ; on lit alors vignette par vignette, chacune avec les seuls
# numeros que SON texte appelle.
def ceni(cle):
    """Les scenes d'une planche : [(nom, forme)], dans l'ordre d'essai."""
    f = RACINE / "gravuri" / "ceni.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8")).get(cle)
    return list(d.items()) if d else []


def dedans(forme, x, y):
    """Le point (x, y), en fraction, est-il dans la forme ?"""
    if forme[0] == "elipso":
        _, cx, cy, rx, ry = forme
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
    _, x0, y0, x1, y1 = forme
    return x0 <= x <= x1 and y0 <= y <= y1


def boite(forme):
    """Le cadre englobant d'une forme, en fraction."""
    if forme[0] == "elipso":
        _, cx, cy, rx, ry = forme
        return (max(0.0, cx - rx), max(0.0, cy - ry),
                min(1.0, cx + rx), min(1.0, cy + ry))
    return tuple(forme[1:])


def blokoj(tab):
    """Le texte du tabelo, coupe par cle : [(cle, scene, corps)]."""
    f = list((RACINE / "texto" / "io").glob(f"*-tabelo-{tab}.tex"))
    if not f:
        return []
    parts = re.split(r'^%%K (\S+)', f[0].read_text(encoding="utf-8"),
                     flags=re.M)
    out, sc = [], ""
    for i in range(1, len(parts), 2):
        m = re.match(r't\d\d-(c\d)-', parts[i])
        if m:
            sc = m.group(1)
        # Une note ou un titre suit la scene ou il se trouve.
        out.append((parts[i], sc, parts[i + 1]))
    return out


# LE RENVOI QUI NE MONTRE RIEN. Le livret appelle parfois un numero
# que la planche ne porte pas : au tableau 5, « les plates-bandes
# (150) », alors que la numerotation s'arrete a 146 et que l'objet est
# grave « 50 ». gravuri/korekti.json dit, tableau par tableau, quel
# renvoi lire a la place de quel autre. La source ne bouge pas ; c'est
# la lecture qui se corrige.
_KOREKTI = None


def korekti(tab):
    """Les renvois a corriger pour ce tableau : {lu: a lire}."""
    global _KOREKTI
    if _KOREKTI is None:
        f = RACINE / "gravuri" / "korekti.json"
        _KOREKTI = (json.loads(f.read_text(encoding="utf-8"))
                    if f.exists() else {})
    return _KOREKTI.get(f"t{int(tab):02d}", {})


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
    t = korekti(tab)
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out


def _lire_renvoji(corps, kor):
    for x in renvoji(corps):
        v = kor.get(str(x), x)
        yield int(v) if str(v).isdigit() else v


def attendus(cle):
    """{scene: numeros appeles}. La scene est "" quand il n'y en a qu'une."""
    tab = cle[1:3]
    bl = blokoj(tab)
    if not bl:
        return {}
    if not ceni(cle):
        n = {x for k, _, c in bl
             for x in _lire_renvoji(c, korekti_renvojo(tab, k))}
        return {"": n} if n else {}
    out = {}
    for k, sc, corps in bl:
        for x in _lire_renvoji(corps, korekti_renvojo(tab, k)):
            out.setdefault(sc, set()).add(x)
    return {k: v for k, v in out.items() if k}


def kl(scene, n):
    """La cle d'un numero : « 39 » sur une planche d'une scene, « c1:39 »
    sur une planche qui en porte plusieurs."""
    return f"{scene}:{n}" if scene else str(n)


def descle(k):
    """L'inverse : « c1:39 » -> ("c1", 39), « 94bis » -> ("", "94bis")."""
    s, n = k.split(":", 1) if ":" in k else ("", str(k))
    return s, (int(n) if n.isdigit() else n)


# TRIER DES CLES QUI NE SONT PAS TOUTES DES NOMBRES. « 94bis » se range
# entre 94 et 95, non a la fin ni au debut : on trie sur le nombre, puis
# sur ce qui le suit.
ORDO = re.compile(r'(\d*)(.*)$')


def ordo(k):
    """La cle de tri d'un numero : sa scene, son nombre, son suffixe."""
    s, n = k.split(":", 1) if ":" in str(k) else ("", str(k))
    m = ORDO.match(n)
    return s, int(m.group(1) or 0), m.group(2)


# Le balayage etait trop timide : a 0.55 il ne rendait que ce que les
# ilots voyaient deja. Descendre a 0.42 fait passer la lecture de 60 a
# 70 % sur les quatre planches d'essai. Le bruit qu'il laisse entrer
# est arrete plus loin, par la liste des numeros attendus et par le
# depart entre lectures rivales.
SEUIL_BAL = 0.50
MARGE_BAL = 0.04


def balayer(enc_f, corps, seuil=SEUIL_BAL, marge=MARGE_BAL):
    """Le filtre adapte passe sur la planche entiere, chiffre par chiffre.

    LES ILOTS NE VOIENT QUE CE QUE LE BLANC ISOLE. Des qu'un chiffre
    touche une hachure, sa composante fusionne avec le dessin et il
    disparait — c'est ce qui plafonnait la lecture des planches
    chargees. Le filtre adapte, lui, n'a pas besoin qu'on decoupe le
    chiffre : il lui suffit que le trait soit la et la reserve vide.

    Seul, il est trop bavard — une gravure offre des milliers de pics.
    Il sert donc en RENFORT des ilots, et deux garde-fous le tiennent :
    le score doit etre franc, et le chiffre retenu doit devancer son
    suivant. Ce qui passe quand meme sera elimine plus loin, faute
    d'appartenir aux nombres attendus.
    """
    # LE BALAYAGE N'EMET PAS DE « 1 ». Le chiffre n'est qu'une barre,
    # et le filtre le retrouve dans la hampe d'un 4, le flanc d'un 9,
    # une hachure verticale : sur le tableau 1 il faisait lire « 13 »
    # pour 3, « 16 » pour 26, « 71 » pour 74. Les ilots, eux, le
    # reconnaissent honnetement — ils decoupent la forme au lieu de la
    # correler — et gardent la charge de le trouver.
    noms = [c for c in sorted(_base()) if c != "1"]
    cartes, geo, ref = [], [], None
    for c in noms:
        T, M, L = gabarit(c, corps)
        r = cv2.matchTemplate(enc_f, T, cv2.TM_CCORR)
        if ref is None:
            ref = r.shape
        rr = np.full(ref, -9, np.float32)
        h = min(ref[0], r.shape[0])
        w = min(ref[1], r.shape[1])
        rr[:h, :w] = r[:h, :w]
        cartes.append(rr)
        geo.append((M, L))
    S = np.stack(cartes)
    ordre = np.argsort(-S, axis=0)
    best = np.take_along_axis(S, ordre[:1], 0)[0]
    ecart = best - np.take_along_axis(S, ordre[1:2], 0)[0]
    k = max(3, (corps // 2) | 1)
    pics = ((best >= cv2.dilate(best, np.ones((k, k), np.uint8)) - 1e-6)
            & (best > seuil) & (ecart > marge))
    out = []
    for y, x in zip(*np.where(pics)):
        i = int(ordre[0, y, x])
        M, L = geo[i]
        out.append((x + M, y + M, L, corps, noms[i],
                    float(best[y, x]), "balayage"))
    return out


def fusionner(a, b, corps):
    """b n'apporte que ce que a n'a pas deja vu."""
    out = list(a)
    for g in b:
        if any(abs(g[0] - h[0]) < 0.5 * corps and abs(g[1] - h[1]) < 0.5 * corps
               for h in out):
            continue
        out.append(g)
    return out


def lire(a, att, haut=None):
    """Rend {numero: ((x, y, l, h), force)} en points du tableau donne."""
    enc = (a > 128).astype(np.uint8)
    if haut is None:
        haut = hauteur(enc)
    gl = []
    for x, y, w, h, v in ilots(enc, round(0.68 * haut), round(1.35 * haut),
                               4, 0.16):
        c, s = classer(v)
        if c and s >= (SEUIL_UN if c == '1' else SEUIL):
            gl.append((x, y, w, h, c, s, "ilot"))
    gl = fusionner(gl, balayer(enc.astype(np.float32), haut), haut)
    lus = {}
    ef = enc.astype(np.float32)
    ecart = round(0.13 * haut)
    large = round(0.62 * haut)
    for grp in grouper(gl):
        t = ''.join(g[4] for g in grp)
        if not t.lstrip('0'):
            continue
        x0 = min(g[0] for g in grp)
        y0 = min(g[1] for g in grp)
        x1 = max(g[0] + g[2] for g in grp)
        y1 = max(g[1] + g[3] for g in grp)
        sd, cd, pd, md = voisin(ef, x1 + ecart, y0, haut)
        sg, cg, pg, mg = voisin(ef, x0 - ecart - large, y0, haut)
        force = (sum(g[5] for g in grp) / len(grp)
                 + (0.15 if all(g[6] == "ilot" for g in grp) else 0.0))
        if max(sd, sg) <= SEUIL_VOISIN:
            lus.setdefault(int(t), []).append(((x0, y0, x1 - x0, y1 - y0),
                                               force))
            continue
        if max(md if sd > SEUIL_VOISIN else 0,
               mg if sg > SEUIL_VOISIN else 0) < MARGE_VOISIN:
            continue
        # Le nombre continue : on l'allonge du chiffre voisin, et on ne
        # retient l'allongement que s'il donne un nombre attendu — et un
        # seul. Deux allongements possibles, c'est une ambiguite : on
        # laisse tomber.
        prop = []
        if sd > SEUIL_VOISIN and int(t + cd) in att:
            prop.append((int(t + cd), (x0, y0, pd[0] + pd[2] - x0, y1 - y0)))
        if sg > SEUIL_VOISIN and int(cg + t) in att:
            prop.append((int(cg + t), (pg[0], y0, x1 - pg[0], y1 - y0)))
        if len(prop) == 1:
            lus.setdefault(prop[0][0], []).append((prop[0][1], force))
    # UN NOMBRE LU DEUX FOIS. Chaque numero ne parait qu'une fois par
    # vignette : deux lectures veulent dire qu'au moins l'une est fausse.
    # On les departage par la force de leur preuve : la ressemblance
    # moyenne des chiffres, et une prime a la lecture entierement tiree
    # des ilots, ou le chiffre a ete decoupe et non seulement correle.
    #
    # SI LES DEUX SE VALENT, ON NE TRANCHE PAS. On a essaye le
    # contraire, une fois les vignettes separees : puisque le numero est
    # unique DANS SA VIGNETTE, l'une des deux lectures est fausse a coup
    # sur, et prendre la mieux etayee semblait valoir mieux que perdre
    # les deux. Cela rend soixante et une lectures de plus -- dont
    # quatre bonnes. Le reste est du bruit : un « c. » et un « k. » de
    # la legende du plan, une branche de sapin, un montant de fenetre.
    # La mesure de la preuve ne sait pas departager deux faux ; on s'en
    # tient donc a l'abstention.
    gard = {}
    for n, p in lus.items():
        if n not in att:
            continue
        p.sort(key=lambda q: -q[1])
        if len(p) == 1 or p[0][1] - p[1][1] >= ECART_PREUVE:
            gard[n] = (p[0][0], round(p[0][1], 3))
    return gard


# UN NUMERO SE TIENT PRES DE CEUX QU'ON CITE AVEC LUI. Le texte decrit
# la planche de proche en proche -- « la caissiere (14) [...] la caisse
# (15) » -- et les objets nommes dans une meme phrase sont voisins sur
# le dessin. La mesure le confirme : chez les lectures sures, deux
# numeros co-cites sont de trois a huit fois plus proches que deux
# numeros pris au hasard (0.12 fois la distance moyenne au tableau 13,
# 0.27 au 11, 0.28 au 10).
#
# C'est donc un controle qui ne doit rien a la forme des chiffres, et
# qui attrape ce qu'elle laisse passer : au tableau 13, « 14 » et « 34 »
# tombaient a dix-huit et douze fois la distance ordinaire de leurs
# voisins de phrase. On reste large -- six fois -- pour ne rejeter que
# l'absurde : des lectures justes montent a quatre ou cinq quand le
# texte saute d'un bout de la planche a l'autre.
SEUIL_ELOIGNE = 6.0


def phrases(tab, scene=""):
    """Les groupes de numeros cites dans une meme phrase du tabelo."""
    bl = blokoj(tab)
    if not bl:
        return []
    t = "".join(c for _, sc, c in bl if not scene or sc == scene)
    t = re.sub(r'%.*', '', t)
    t = re.sub(r'\\(?:nl|cc)\b', ' ', t)
    out = []
    for ph in re.split(r'[.;:!?]\s', t):
        ns = sorted(set(_lire_renvoji(ph, korekti_renvojo(tab))),
                    key=lambda q: ordo(str(q)))
        if len(ns) > 1:
            out.append(ns)
    return out


def coherer(cle, trouves, la, ht, scene=""):
    """Ecarte les lectures posees loin de leurs voisines de phrase."""
    from itertools import combinations
    pos = {n: (v[0][0], v[0][1]) for n, v in trouves.items()}
    surs = {n: pos[n] for n, v in trouves.items() if v[1] >= 0.95}
    ph = phrases(cle[1:3], scene)
    ref = [np.hypot(surs[a][0] - surs[b][0], surs[a][1] - surs[b][1])
           for g in ph for a, b in combinations([x for x in g if x in surs], 2)]
    if len(ref) < 8:
        return trouves, 0          # pas de quoi mesurer une echelle
    ech = float(np.median(ref)) or 1.0
    voisins = {}
    for g in ph:
        for a in g:
            voisins.setdefault(a, set()).update(x for x in g if x != a)
    gard, jetes = {}, 0
    for n, v in trouves.items():
        vs = [surs[w] for w in voisins.get(n, ()) if w in surs and w != n]
        if vs:
            x, y = pos[n]
            dm = float(np.median([np.hypot(x - a, y - b) for a, b in vs]))
            if dm / ech > SEUIL_ELOIGNE:
                jetes += 1
                continue
        gard[n] = v
    return gard, jetes


def manuali(cle, la, ht, corps):
    """Les numeros que l'oeil a poses lui-meme sur cette planche.

    Le lecteur automatique plafonne la ou la reserve de blanc se
    referme : le chiffre touche une hachure, ou se cache a demi derriere
    un chapeau, et rien ne l'en distingue plus. Ces numeros-la se
    relevent a la main, avec outils/manuali.py, et gravuri/manuali.json
    les garde. Comme verdikti.json, ce fichier ne s'ecrit pas tout seul.
    """
    f = RACINE / "gravuri" / "manuali.json"
    if not f.exists():
        return {}
    d = json.loads(f.read_text(encoding="utf-8")).get(cle, {})
    return {n: ((round(v[0] * la), round(v[1] * ht),
                 round(v[2] * la), round(v[3] * ht)), v[4])
            for n, v in d.items()}


def verdikti(cle):
    """Les lectures que l'oeil a refusees, pour cette planche.

    LA MACHINE N'ECRIT PAS CE FICHIER. gravuri/verdikti.json se tient a
    la main : chaque decoupe douteuse a ete relue avec, sous elle, le
    nom que le fac-simile donne a l'objet, et l'on y a inscrit celles ou
    le numero annonce ne se trouve pas. Si l'outil pouvait le reecrire,
    le jugement se perdrait au premier relancement -- or c'est la seule
    piece du dispositif qu'aucune mesure ne remplace.
    """
    f = RACINE / "gravuri" / "verdikti.json"
    if not f.exists():
        return set()
    d = json.loads(f.read_text(encoding="utf-8"))
    return {str(x) for x in d.get(cle, [])}


def objekti(cle):
    """Le nom de chaque objet numerote, s'il a ete releve.

    Les cles suivent celles de numeri.json : « 39 » sur une planche d'une
    seule scene, « c1:39 » sur une planche qui en porte plusieurs.
    """
    f = RACINE / "gravuri" / "objekti.json"
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding="utf-8")).get(cle[:3], {})


def controle(chemin, trouves, dest, haut, seuil=None, large=1.1, cols=12):
    """Une planche de controle : chaque numero lu, dans sa decoupe.

    LE NOM DE L'OBJET EST PORTE SOUS LA DECOUPE. La forme du chiffre ne
    suffit pas a juger une lecture douteuse -- une hachure ressemble a
    beaucoup de choses -- mais le fac-simile dit ce que le numero
    designe, et l'oeil tranche alors tout de suite : si « (20) » doit
    montrer une bicyclette et que la decoupe n'en porte pas, la lecture
    est fausse, quel qu'ait ete son score.

    « seuil » ne retient que les lectures au-dessous d'une confiance
    donnee, et « large » elargit la decoupe : c'est la planche des cas
    douteux, ou l'on veut voir l'objet autour du numero, non le seul
    chiffre.
    """
    from PIL import ImageDraw
    cle = cle_de(dest)
    noms = objekti(cle)
    gard = {n: v for n, v in trouves.items()
            if seuil is None or v[1] < seuil}
    if not gard:
        return 0
    # LE DECOUPAGE SE FAIT TOUJOURS DANS LA PLANCHE DE TRAVAIL, et
    # celle-ci porte son encre en sombre : une feuille de controle se
    # lit comme une gravure, non comme un negatif.
    im = planche(cle)
    marge = round(large * haut)
    cell = round(3.2 * haut * max(1.0, large / 1.1))
    lig = (len(gard) + cols - 1) // cols
    bas = 34
    feuille = Image.new('L', (cols * cell, lig * (cell + bas)), 255)
    d = ImageDraw.Draw(feuille)
    for k, n in enumerate(sorted(gard, key=lambda q: ordo(str(q)))):
        (x, y, w, h), f = gard[n]
        cr = im.crop((x - marge, y - marge, x + w + marge, y + h + marge))
        r, c = divmod(k, cols)
        feuille.paste(cr.resize((cell, cell)), (c * cell, r * (cell + bas)))
        d.text((c * cell + 4, r * (cell + bas) + cell + 3),
               f"{n}  ({f:.2f})", fill=0)
        v = noms.get(str(n), {})
        nom = (v.get("fr") or v.get("io") or ["—"])[0]
        d.text((c * cell + 4, r * (cell + bas) + cell + 17), nom[:26], fill=0)
    feuille.save(dest)
    return len(gard)


# LA CLE DE PLANCHE SE TIRE DU NOM DE FICHIER, quel que soit le suffixe
# que la feuille porte -- « -dubita », « -manuali », « -revizo2 ». On la
# lit au motif, plutot que de retrancher une liste de suffixes qu'il
# faudrait tenir a jour.
def cle_de(dest):
    m = re.match(r'(t\d\d-[a-z0-9]+-\d+)', Path(dest).stem)
    return m.group(1) if m else Path(dest).stem


def main(cles=None):
    KONTROLO.mkdir(parents=True, exist_ok=True)
    cat = {}
    fich = RACINE / "gravuri" / "numeri.json"
    if fich.exists():
        cat = json.loads(fich.read_text(encoding="utf-8"))
    # LE COMPTE SE TIENT PAR TABLEAU, non par planche : le tableau 5 a
    # deux gravures — la maison et son plan — qui se partagent une seule
    # numerotation, et compter deux fois ses cent vingt-trois numeros
    # ferait mentir le total.
    par_tab = {}
    for f in sorted(KOVRI.glob("*-trako.png")):
        cle = f.name[:-10]
        if not re.fullmatch(r't\d\d-[a-z0-9]+-\d+', cle):
            continue          # les essais d'antan, restes dans kovri/
        if cles and cle not in cles:
            continue
        att = attendus(cle)
        if not att:
            continue
        # UNE PLANCHE REPRISE SUR SON ORIGINAL NE SE RELIT PAS. Ses
        # numeros ont ete portes par originali.py, verifies un a un, et
        # ils sont enregistres en fraction de la NOUVELLE planche : les
        # relire sur l'ancienne couche de trait, qui n'a plus ni les
        # memes dimensions ni le meme cadrage, ecraserait le travail.
        # ON A ESSAYE DE LUI APPRENDRE LE GRIS, et l'on a mesure ce
        # que cela vaut : mille cinq cents numeros deja places font
        # quatorze cents chiffres etiquetes, de quoi refaire les
        # modeles dans le medium meme (outils/chifri.py). Le lecteur
        # ainsi refait retrouve 442 numeros a leur place, en pose 132
        # AILLEURS, et en propose 45 de neufs. Un sur quatre est faux :
        # c'est trop pour entrer ici tout seul. Il sert donc a
        # PROPOSER, non a decider, et ce que l'oeil garde de ses
        # propositions entre par manuali.json comme le reste.
        if repris(cle) and cle in cat:
            # On garde les LECTURES, mais on continue d'accueillir ce que
            # l'oeil pose : un numero releve a la main sur le fac-simile
            # doit entrer, sans quoi la planche reprise serait figee.
            e = cat[cle]
            la, ht, haut = e["largeur"], e["alteso"], e["corpo"]
            trouves = {n: ((round(v[0] * la), round(v[1] * ht),
                            round(v[2] * la), round(v[3] * ht)), v[4])
                       for n, v in e["numeri"].items()}
            ref = verdikti(cle)
            for n in [n for n in trouves
                      if n in ref or str(descle(n)[1]) in ref]:
                del trouves[n]
            # CE QUE LA MAIN A POSE, LA MAIN PEUT LE REPRENDRE. Les
            # positions relevees a l'oeil entrent ici avec une confiance
            # de 1.0 exactement -- aucune lecture automatique n'y
            # arrive -- et, une fois ecrites dans numeri.json, elles
            # devenaient indiscernables des lectures portees depuis
            # l'ancienne planche : les retirer de manuali.json ne les
            # retirait plus de rien. On les jette donc toutes avant de
            # remettre celles que le fichier tient encore. Un numero
            # pose de travers se corrige alors la ou on l'a pose.
            for n in [n for n, v in trouves.items() if v[1] == 1.0]:
                del trouves[n]
            possibles = {kl(sc, n) for sc, ns in att.items() for n in ns}
            mains = manuali(cle, la, ht, haut)
            trouves.update({n: v for n, v in mains.items() if n in possibles})
            attendu = sum(len(v) for v in att.values())
            e["numeri"] = {str(n): [round(x / la, 6), round(y / ht, 6),
                                    round(w / la, 6), round(h / ht, 6), f]
                           for n, ((x, y, w, h), f)
                           in sorted(trouves.items(),
                                     key=lambda q: ordo(str(q[0])))}
            controle(f, trouves, KONTROLO / f"{cle}.png", haut)
            print(f"  {cle}  {len(trouves):3d}/{attendu:3d} numeros — "
                  f"planche d'origine, lecture conservee"
                  + (f", {len(mains)} poses a la main" if mains else ""))
            t = par_tab.setdefault(cle[:3], [set(), 0])
            t[0].update(e["numeri"])
            t[1] = max(t[1], attendu)
            continue
        a = np.asarray(Image.open(f))
        ht, la = a.shape
        haut = hauteur((a > 128).astype(np.uint8))
        # LA LECTURE SE FAIT VIGNETTE PAR VIGNETTE. Sur une planche a
        # plusieurs scenes, chacune recommence a 1 : chercher « 39 » sur
        # toute la planche, c'est en trouver deux et n'en garder aucun.
        formes = ceni(cle) or [("", ["rekt", 0.0, 0.0, 1.0, 1.0])]
        trouves, jetes = {}, 0
        for sc, forme in formes:
            if sc not in att:
                continue
            fx0, fy0, fx1, fy1 = boite(forme)
            x0, y0 = int(fx0 * la), int(fy0 * ht)
            x1, y1 = min(la, int(fx1 * la) + 1), min(ht, int(fy1 * ht) + 1)
            lus = lire(a[y0:y1, x0:x1], att[sc], haut)
            lus = {n: ((b[0] + x0, b[1] + y0, b[2], b[3]), fo)
                   for n, (b, fo) in lus.items()}
            # Le cadre englobant deborde sur les vignettes voisines --
            # celui de l'ovale du tableau 6 les chevauche toutes quatre,
            # et son « 6 » de faience tombait aussi dans le salon. La
            # PREMIERE forme qui contient le point l'emporte : l'ovale
            # est essaye avant les quatre vignettes, et rien n'est lu
            # deux fois.
            def qui(v):
                x = (v[0][0] + v[0][2] / 2) / la
                y = (v[0][1] + v[0][3] / 2) / ht
                return next((s for s, f in formes if dedans(f, x, y)), None)

            lus = {n: v for n, v in lus.items() if qui(v) == sc}
            lus, jt = coherer(cle, lus, la, ht, sc)
            jetes += jt
            trouves.update({kl(sc, n): v for n, v in lus.items()})
        attendu = sum(len(v) for v in att.values())
        # Un refus ecrit en clair (« 54 ») sur une planche a scenes vaut
        # pour toutes ses vignettes : le jugement date d'avant qu'on sut
        # qu'il y en avait plusieurs, et rien ne dit laquelle il visait.
        ref = verdikti(cle)
        refuses = {n for n in trouves
                   if n in ref or str(descle(n)[1]) in ref}
        for n in refuses:
            del trouves[n]
        # Ce que l'oeil a pose l'emporte sur tout le reste.
        possibles = {kl(sc, n) for sc, ns in att.items() for n in ns}
        mains = manuali(cle, la, ht, haut)
        trouves.update({n: v for n, v in mains.items() if n in possibles})
        t = par_tab.setdefault(cle[:3], [set(), 0])
        t[0].update(trouves)
        t[1] = max(t[1], attendu)
        controle(f, trouves, KONTROLO / f"{cle}.png", haut)
        # LA PLANCHE DES CAS DOUTEUX, decoupee plus large et portant le
        # nom de l'objet : c'est celle qu'on relit pour trancher.
        # Quatre colonnes et non huit : a huit, le chiffre au centre de
        # la decoupe ne fait plus que quelques points a l'ecran, et l'on
        # ne peut pas juger. La planche est plus haute, elle se lit.
        n_d = controle(f, trouves, KONTROLO / f"{cle}-dubita.png", haut,
                       seuil=0.95, large=3.4, cols=4)
        # EN FRACTION, non en points : la page sert la planche a trois
        # definitions, et le gros plan doit tomber juste sur chacune.
        cat[cle] = {"corpo": haut, "largeur": la, "alteso": ht,
                    # LA CONFIANCE EST ENREGISTREE AVEC LA POSITION. Une
                    # lecture entierement decoupee par les ilots est sure ;
                    # une lecture ou le balayage a fourni un chiffre l'est
                    # beaucoup moins, et c'est sur les planches chargees que
                    # la difference se voit. La page pourra donc n'ouvrir un
                    # gros plan que sur les lectures qui la meritent, sans
                    # qu'il faille relancer l'outil.
                    "numeri": {str(n): [round(x / la, 6), round(y / ht, 6),
                                        round(w / la, 6), round(h / ht, 6), f]
                               for n, ((x, y, w, h), f)
                               in sorted(trouves.items(),
                                         key=lambda q: ordo(str(q[0])))}}
        print(f"  {cle}  {len(trouves):3d}/{attendu:3d} numeros lus "
              f"(corps {haut} px), dont {n_d} a verifier"
              + (f", {jetes} ecartes par le voisinage" if jetes else "")
              + (f", {len(refuses)} refuses a l'oeil" if refuses else "")
              + (f", {len(mains)} poses a la main" if mains else ""))
    fich.write_text(json.dumps(cat, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    tot_l = sum(len(v[0]) for v in par_tab.values())
    tot_a = sum(v[1] for v in par_tab.values())
    if tot_a:
        print(f"  TOTAL {tot_l}/{tot_a} = {100 * tot_l // tot_a} %")
    print(f"  planches de controle dans {KONTROLO}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
