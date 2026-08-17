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
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
KOVRI = RACINE / "gravuri" / "kovri"
KONTROLO = RACINE / "gravuri" / "kontrolo"

H, W = 40, 32
# Un « 1 » sans empattement est une barre, et une planche gravee en
# est pleine. On lui demande donc davantage qu'aux autres.
SEUIL = 0.80
SEUIL_UN = 0.86


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
BASE = None


def _base():
    global BASE
    if BASE is None:
        d = np.load(RACINE / "outils" / "chifri.npz")
        BASE = {}
        for c in d.files:
            m = d[c].mean(0)
            col = m.max(0) > 0.15
            BASE[c] = m[:, col.argmax(): len(col) - col[::-1].argmax()]
    return BASE


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


def attendus(cle):
    """Les numeros que le texte du tabelo appelle."""
    n = cle[1:3]
    f = list((RACINE / "texto" / "io").glob(f"*-tabelo-{n}.tex"))
    if not f:
        return set()
    return {int(x) for x in
            re.findall(r'\((\d+)\)', f[0].read_text(encoding="utf-8"))}


def lire(chemin, att):
    """Rend {numero: (x, y, largeur, hauteur)} en points de la planche."""
    a = np.asarray(Image.open(chemin))
    enc = (a > 128).astype(np.uint8)
    haut = hauteur(enc)
    gl = []
    for x, y, w, h, v in ilots(enc, round(0.68 * haut), round(1.35 * haut),
                               4, 0.16):
        c, s = classer(v)
        if c and s >= (SEUIL_UN if c == '1' else SEUIL):
            gl.append((x, y, w, h, c, s))
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
        if max(sd, sg) <= SEUIL_VOISIN:
            lus.setdefault(int(t), []).append((x0, y0, x1 - x0, y1 - y0))
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
            lus.setdefault(prop[0][0], []).append(prop[0][1])
    # UN NOMBRE LU DEUX FOIS EST UN NOMBRE DONT ON NE SAIT RIEN : chaque
    # numero ne parait qu'une fois sur la planche, deux lectures veulent
    # dire qu'au moins l'une est fausse, et rien ne dit laquelle.
    return ({n: p[0] for n, p in lus.items() if len(p) == 1 and n in att},
            haut, enc.shape)


def controle(chemin, trouves, dest, haut):
    """Une planche de controle : chaque numero lu, dans sa decoupe."""
    im = Image.open(chemin)
    marge = round(1.1 * haut)
    cell = round(3.2 * haut)
    cols = 12
    lig = (len(trouves) + cols - 1) // cols
    if not lig:
        return
    feuille = Image.new('L', (cols * cell, lig * (cell + 22)), 255)
    from PIL import ImageDraw
    d = ImageDraw.Draw(feuille)
    for k, n in enumerate(sorted(trouves)):
        x, y, w, h = trouves[n]
        cr = im.crop((x - marge, y - marge, x + w + marge, y + h + marge))
        cr = cr.resize((cell, cell))
        r, c = divmod(k, cols)
        feuille.paste(cr, (c * cell, r * (cell + 22)))
        d.text((c * cell + 4, r * (cell + 22) + cell + 4), str(n), fill=0)
    feuille.save(dest)


def main(cles=None):
    KONTROLO.mkdir(parents=True, exist_ok=True)
    cat = {}
    fich = RACINE / "gravuri" / "numeri.json"
    if fich.exists():
        cat = json.loads(fich.read_text(encoding="utf-8"))
    tot_l = tot_a = 0
    for f in sorted(KOVRI.glob("*-trako.png")):
        cle = f.name[:-10]
        if not re.fullmatch(r't\d\d-[a-z0-9]+-\d+', cle):
            continue          # les essais d'antan, restes dans kovri/
        if cles and cle not in cles:
            continue
        att = attendus(cle)
        if not att:
            continue
        trouves, haut, (ht, la) = lire(f, att)
        tot_l += len(trouves)
        tot_a += len(att)
        controle(f, trouves, KONTROLO / f"{cle}.png", haut)
        # EN FRACTION, non en points : la page sert la planche a trois
        # definitions, et le gros plan doit tomber juste sur chacune.
        cat[cle] = {"corpo": haut, "largeur": la, "alteso": ht,
                    "numeri": {str(n): [round(x / la, 6), round(y / ht, 6),
                                        round(w / la, 6), round(h / ht, 6)]
                               for n, (x, y, w, h) in sorted(trouves.items())}}
        print(f"  {cle}  {len(trouves):3d}/{len(att):3d} numeros lus "
              f"(corps {haut} px)")
    fich.write_text(json.dumps(cat, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    if tot_a:
        print(f"  TOTAL {tot_l}/{tot_a} = {100 * tot_l // tot_a} %")
    print(f"  planches de controle dans {KONTROLO}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
