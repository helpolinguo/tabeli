#!/usr/bin/env python3
# ===================================================================
#  originali.py — poser une numerisation d'origine sur nos planches.
#
#  POURQUOI. Les gravures que sert la page viennent d'un PDF colorise :
#  la couche de trait y est un POCHOIR — 87 pour cent de ses points sont
#  du noir pur ou du blanc pur — parce qu'elle y servait de masque pour
#  poser l'encre. Le demi-ton du bois grave, qui fait toute la douceur
#  de la planche, n'y est plus, et aucune definition ne le rendra. Il
#  faut donc repartir des numerisations d'origine (Gallica, BnF).
#
#  CE QUI SERAIT PERDU SANS CET OUTIL. Mille cinq cents numeros ont ete
#  releves a la main sur les planches actuelles. Ils sont enregistres EN
#  FRACTION de la planche, non en points : pour les transporter sur une
#  autre numerisation, il suffit de savoir quelle similitude — rotation,
#  echelle, translation — mene de l'une a l'autre. C'est ce que cet
#  outil mesure, et il le mesure sans qu'on lui dise rien : la
#  correlation entre deux rendus tres differents du meme dessin suffit.
#
#  ON A VERIFIE QUE CELA MARCHE MEME DE TRES LOIN. La copie de service
#  de Gallica ne donne a la gravure du tableau 1 que 1250 points de
#  large, contre 5463 a notre couche de trait — quatre fois moins — et
#  le calage tombe juste malgre tout.
#
#  USAGE
#      python3 outils/originali.py caler  t01-apar-1 origine.jpg
#      python3 outils/originali.py compar t01-apar-1 origine.jpg 0.79 0.20
#      python3 outils/originali.py netigar t01-apar-1 originali/t01.jpg
#      python3 outils/originali.py reprendre t02-apar-1 originali/t02.jpg
# ===================================================================

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numeri as N                                          # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
CATALOGO = RACINE / "gravuri" / "originali.json"


def gris(chemin):
    """L'image en gris, l'encre en noir, en flottant normalise."""
    im = Image.open(chemin)
    if im.mode not in ("L", "I;16"):
        im = im.convert("L")
    a = np.asarray(im).astype(np.float32)
    if a.max() > 255:
        a = a / 257.0
    return a


def notre_trait(cle):
    """Notre couche de trait, remise a l'endroit : l'encre en noir."""
    a = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")).astype(np.float32)
    return 255.0 - a


def centrer(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 1e-6 else a


# LA PLANCHE PEUT ETRE COUCHEE DANS LA NUMERISATION. Les feuillets sont
# relies dans le sens de la hauteur et la gravure y est de travers ; on
# essaie donc les quatre quarts de tour, et l'on garde celui qui accroche.
def orientations(a):
    for k in range(4):
        yield k, np.rot90(a, k)


def caler(cle, chemin, large=1100, verbeux=True):
    """La similitude qui mene de notre planche a la numerisation.

    Rend (M, score, tour) : M est la matrice 2x3 qui envoie un point de
    NOTRE planche, en points, sur la numerisation, en points.
    """
    src = notre_trait(cle)
    HS, LS = src.shape
    dst0 = gris(chemin)
    petit_src = cv2.resize(src, (large, round(large * HS / LS)),
                           interpolation=cv2.INTER_AREA)
    ech_src = LS / large
    best = None
    for tour, dst in orientations(dst0):
        HD, LD = dst.shape
        if LD < 200 or HD < 200:
            continue
        f = large / max(LD, HD)
        petit_dst = cv2.resize(dst, (max(1, round(LD * f)),
                                     max(1, round(HD * f))),
                               interpolation=cv2.INTER_AREA)
        ech_dst = 1 / f
        # La gravure n'occupe qu'une partie du feuillet : on cherche
        # notre planche DANS la page, a plusieurs echelles.
        g = centrer(petit_dst)
        for r in np.arange(0.45, 1.02, 0.025):
            w = round(petit_src.shape[1] * r)
            h = round(petit_src.shape[0] * r)
            if w < 80 or h < 80 or w > g.shape[1] or h > g.shape[0]:
                continue
            s = centrer(cv2.resize(petit_src, (w, h),
                                   interpolation=cv2.INTER_AREA))
            m = cv2.matchTemplate(g, s, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(m)
            if best is None or mx > best[0]:
                best = (mx, tour, r, loc, ech_dst, w, h)
    if best is None:
        raise SystemExit("  rien a caler")
    score, tour, r, (x0, y0), ech_dst, w, h = best
    # De notre planche (points) vers la numerisation TOURNEE (points).
    k = r / ech_src * ech_dst
    M = np.array([[k, 0.0, x0 * ech_dst],
                  [0.0, k, y0 * ech_dst]], np.float32)
    if verbeux:
        print(f"  {cle} : quart de tour {tour}, echelle {k:.4f}, "
              f"coin ({round(x0 * ech_dst)}, {round(y0 * ech_dst)}), "
              f"correlation {score:.3f}")
        print(f"  la gravure y mesure {round(LS * k)} x {round(HS * k)} "
              f"points (nous : {LS} x {HS})")
    return M, score, tour


def charger_tournee(chemin, tour):
    a = gris(chemin)
    return np.rot90(a, tour)


def compar(cle, chemin, cx=0.5, cy=0.5, w=0.115, h=0.095, sortie=None):
    """Le meme detail dans les trois etats, cote a cote."""
    M, score, tour = caler(cle, chemin)
    ori = charger_tournee(chemin, tour)
    HS, LS = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")).shape
    x0f, y0f = cx - w / 2, cy - h / 2

    def coupe_ori():
        p = np.array([[x0f * LS, y0f * HS, 1.0],
                      [(x0f + w) * LS, (y0f + h) * HS, 1.0]]).T
        q = M @ p
        return Image.fromarray(ori.astype(np.uint8)).crop(
            (round(q[0, 0]), round(q[1, 0]), round(q[0, 1]), round(q[1, 1])))

    vues = [(coupe_ori(), "la numerisation d'origine")]
    for nom, im, quoi in (
            ("detalo", Image.open(RACINE / "gravuri" / f"{cle}-detalo.webp")
             .convert("L"), "ce que la page sert"),
            ("trako", ImageOps.invert(Image.open(N.KOVRI / f"{cle}-trako.png")
                                      .convert("L")), "notre couche de trait")):
        W_, H_ = im.size
        vues.append((im.crop((round(x0f * W_), round(y0f * H_),
                              round((x0f + w) * W_), round((y0f + h) * H_))),
                     quoi))
    OUT = (1000, round(1000 * h / w * (HS / LS) / 1.0))
    F = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
    F2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
    pl = Image.new("RGB", (3 * (OUT[0] + 16) + 16, OUT[1] + 90),
                   (255, 255, 255))
    d = ImageDraw.Draw(pl)
    for i, (c, t) in enumerate(vues):
        n = f"{c.width} x {c.height} points pour ce detail"
        c = c.resize(OUT, Image.LANCZOS).convert("RGB")
        X = 16 + i * (OUT[0] + 16)
        pl.paste(c, (X, 16))
        d.rectangle([X, 16, X + OUT[0], 16 + OUT[1]], outline=(190, 0, 0),
                    width=2)
        d.text((X, OUT[1] + 26), t, fill=(0, 0, 0), font=F)
        d.text((X, OUT[1] + 54), n, fill=(90, 90, 90), font=F2)
    sortie = Path(sortie or (RACINE / "gravuri" / "kontrolo" /
                             f"{cle}-origino.png"))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    pl.save(sortie)
    print(f"  comparaison dans {sortie}")


# -------------------------------------------------------------------
#  LE NETTOYAGE, ET CE QU'IL S'INTERDIT
# -------------------------------------------------------------------
#  On redresse et l'on rogne, RIEN DE PLUS, et EN UN SEUL
#  REECHANTILLONNAGE : la rotation et le rognage sont composes en une
#  matrice, appliquee une fois. Deux passes a la file — tourner, puis
#  couper — coutent une interpolation de trop, et cela se voit sur une
#  hachure de deux points de large.
#
#  L'ANGLE SE MESURE SUR LE FILET DU CADRE, non sur le dessin. On
#  prend les deux filets horizontaux, qui courent sur quatre mille
#  points et donnent l'angle a un vingtieme de degre pres ; les filets
#  verticaux servent de controle. Au tableau 1 les deux horizontaux
#  s'accordent sur 0.30 degre, et une fois redresses ils tombent
#  exactement a zero.
#
#  ON NE REDRESSE PAS LES VERTICALES. Apres redressement elles gardent
#  un tiers de degre : la feuille a gondole, ou la planche a ete
#  imprimee de biais. Corriger cela demanderait un cisaillement, c'est
#  a dire d'inventer une geometrie que le fac-simile n'a pas. On
#  l'enregistre et on la laisse.
#
#  ET L'ON NE TOUCHE PAS AU TON. Le papier est creme — son mode est a
#  235, l'encre la plus noire a 66 — et c'est ainsi qu'il faut le
#  garder : l'edition est diplomatique, l'eclaircissement se fera a
#  l'affichage si on le veut, et restera reversible.
MARGE_FILET = 8


def _tourner(a, th, centre):
    return cv2.getRotationMatrix2D(centre, th, 1.0)


def angle_filet(enc, bande, axe, ampl=1.2, pas=0.025):
    """L'angle qui rend une droite du cadre la plus franche."""
    best = None
    y0, y1, x0, x1 = bande
    b = enc[y0:y1, x0:x1]
    for th in np.arange(-ampl, ampl + 1e-9, pas):
        M = _tourner(b, th, (b.shape[1] / 2, b.shape[0] / 2))
        r = cv2.warpAffine(b, M, (b.shape[1], b.shape[0]),
                           flags=cv2.INTER_LINEAR, borderValue=0)
        p = r.mean(axis=axe)
        v = float(p.max() - np.median(p))
        if best is None or v > best[0]:
            best = (v, float(th), int(np.argmax(p)))
    return best


# ON N'ESSAIE PAS DE RECONNAITRE LE FILET : ON ESSAIE TOUTES LES LIGNES
# CANDIDATES, ET L'ON GARDE CELLE QU'ON SUIT LE MIEUX.
#
# Deux fausses pistes ont ete parcourues avant celle-ci. Prendre la
# rangee la plus encree : elle tombe sur le titre de la collection, qui
# court en haut de chaque feuillet — « Tableaux Auxiliaires Delmas pour
# l'Enseignement pratique des Langues vivantes par l'Image » — et qui
# est bien plus noir que le filet ; l'ecart d'ajustement montait alors a
# dix ou douze points sur neuf planches. Prendre le sommet le plus FIN :
# on attrape alors une hachure du dessin, et l'on perd les trois quarts
# des colonnes.
#
# Ce qui distingue le filet n'est ni sa noirceur ni sa finesse, c'est
# qu'il COURT D'UN BORD A L'AUTRE, tout droit. Cela ne se devine pas sur
# un profil : cela se verifie en le suivant. On prend donc les huit
# meilleurs sommets de la bande, on suit chacun, et l'on garde
# l'ajustement le plus serre parmi ceux qui gardent assez de colonnes.
def meilleur_filet(enc, a0, a1, x0, x1, cand=8):
    """Le filet d'une bande : le candidat qu'on suit le mieux."""
    prof = enc[a0:a1, round(0.20 * enc.shape[1]):
               round(0.80 * enc.shape[1])].mean(1)
    ordre = np.argsort(prof)[::-1]
    pris = []
    for i in ordre:
        if all(abs(int(i) - j) > 25 for j in pris):
            pris.append(int(i))
        if len(pris) >= cand:
            break
    best = None
    for i in pris:
        y = a0 + i
        m = suivre_filet(enc, max(0, y - 22), min(enc.shape[0], y + 23),
                         x0, x1)
        if not m or m[2] < 40:
            continue
        if best is None or m[1] < best[0][1]:
            best = (m, y)
    return best


# LE BORD LATERAL SE MESURE DE DEUX FACONS, ET L'ON GARDE LA PLUS
# LARGE.
#
# Les filets verticaux ne sont pas les horizontaux. Ceux-ci courent
# d'un bord a l'autre et se suivent ; ceux-la sont parfois graves d'un
# trait franc, parfois a peine, parfois pas du tout — au tableau 8 il
# n'y a rien a gauche que la hachure de l'etang qui vient mourir au
# bord. Chercher un sommet dans un profil ou la mediane est celle du
# DESSIN, et non du papier, ne pouvait donner qu'un accident du
# dessin : le rognage tombait alors cent points trop avant et coupait
# les numeros 16, 18, 19 du tableau 8, cent trente points trop court a
# droite du tableau 12, quatre-vingts au tableau 11 — le 76 s'y
# retrouvait dehors.
#
# On mesure donc deux choses, en partant de la marge :
#
#   le FILET — le premier sommet fin qui se leve nettement au-dessus du
#   PAPIER (et non au-dessus de la mediane du profil) ;
#
#   l'ENTREE DU DESSIN — l'endroit ou l'encre passe a mi-chemin entre
#   le papier et le plein du dessin, et n'en redescend plus.
#
# Puis l'on garde CELLE DES DEUX QUI EST LA PLUS EXTERIEURE. Un peu de
# marge blanche ne coute rien ; un trait de gravure coupe ne se
# rattrape pas. Verifie sur les seize planches : les deux mesures
# tombent l'une sur l'autre douze fois, et les quatre fois qu'elles
# different c'est la plus exterieure qui est sur le filet.
def _paper(q, marge):
    m = round(marge * len(q))
    return float(np.percentile(q[:m], 20)), float(np.median(q[m:]))


def filet_lateral(q, marge=0.30, large=20):
    """Le premier sommet fin qui se leve au-dessus du papier."""
    fond, plein = _paper(q, marge)
    haut = max(6.0, 0.25 * (plein - fond))
    for i in range(2, len(q) - 2):
        if q[i] >= q[i - 1] and q[i] > q[i + 1] and q[i] - fond >= haut:
            mi = fond + (q[i] - fond) / 2
            a, b = i, i
            while a > 0 and q[a] > mi:
                a -= 1
            while b < len(q) - 1 and q[b] > mi:
                b += 1
            if b - a <= large:
                return i
    return None


def entree_dessin(q, marge=0.30, tenue=20):
    """L'endroit ou l'encre monte a mi-plein et n'en redescend plus."""
    fond, plein = _paper(q, marge)
    if plein - fond < 4:
        return None
    seuil = fond + 0.40 * (plein - fond)
    for i in range(len(q) - tenue):
        if (q[i:i + tenue] > seuil).all():
            return i
    return None


def bord_lateral(prof, sens):
    """Le bord d'un cote : la plus exterieure des deux mesures."""
    q = np.asarray(prof, dtype=float)
    if sens < 0:
        q = q[::-1]
    duo = [i for i in (filet_lateral(q), entree_dessin(q)) if i is not None]
    if not duo:
        return None
    i = min(duo)
    return i if sens > 0 else len(q) - 1 - i


# MESURER LE FILET, PLUTOT QUE DE CHERCHER SON ANGLE. On tournait la
# bande d'essai par pas d'un quarantieme de degre et l'on gardait
# l'angle qui rendait le pic le plus franc. Au tableau 1 les deux filets
# horizontaux s'accordaient a +0.300 ; au tableau 2 ils donnaient -0.275
# et +0.225, un demi-degre d'ecart -- l'un des deux avait accroche autre
# chose que le filet.
#
# On mesure donc le filet LUI-MEME : pour une centaine de colonnes
# reparties sur la largeur, la ligne la plus encree dans une fenetre
# etroite ; puis une droite ajustee par moindres carres, en rejetant
# d'une passe a l'autre ce qui s'ecarte trop de la precedente. La
# pente donne l'angle, et l'ecart residuel dit si l'on a bien suivi un
# filet ou couru apres une branche d'arbre.
def suivre_filet(enc, y0, y1, x0, x1, pas=40, fenetre=14):
    """Suit une droite presque horizontale et rend (angle, ecart, n).

    ON NE GARDE QUE LES COLONNES OU LE FILET SE VOIT. Sur une planche
    dont le ciel ou le sol est hachure, une colonne sur trois n'offre
    aucun pic franc, et le barycentre s'y pose n'importe ou : l'ecart
    d'ajustement montait alors a dix ou onze points, et l'angle ne
    valait plus rien. On mesure donc la FORCE de chaque pic -- sa
    hauteur au-dessus du fond de la fenetre -- et l'on jette les
    colonnes qui n'atteignent pas la moitie de la force mediane.
    Ensuite seulement on ajuste, quatre fois, en resserrant sur l'ecart
    absolu median.
    """
    xs, ys, fs = [], [], []
    for x in range(x0, x1 - pas, pas):
        col = enc[y0:y1, x:x + pas].mean(1)
        if col.max() < 8:
            continue
        i = int(np.argmax(col))
        a0, b0 = max(0, i - fenetre), min(len(col), i + fenetre + 1)
        w = col[a0:b0]
        if w.sum() <= 0:
            continue
        xs.append(x + pas / 2)
        ys.append(y0 + a0 + float((w * np.arange(len(w))).sum() / w.sum()))
        fs.append(float(w.max() - np.median(col)))
    if len(xs) < 8:
        return None
    X, Y, F = np.array(xs), np.array(ys), np.array(fs)
    garde = F >= 0.5 * float(np.median(F))
    if garde.sum() >= 8:
        X, Y = X[garde], Y[garde]
    m = c = 0.0
    for _ in range(4):
        A = np.vstack([X, np.ones_like(X)]).T
        (m, c), *_ = np.linalg.lstsq(A, Y, rcond=None)
        r = np.abs(Y - (m * X + c))
        seuil = max(2.0, 3.0 * float(np.median(r)))
        g = r <= seuil
        if g.sum() < 8 or g.all():
            break
        X, Y = X[g], Y[g]
    return (float(np.degrees(np.arctan(m))),
            float(np.sqrt(((Y - (m * X + c)) ** 2).mean())), int(len(X)))


# LE CADRE : les horizontales sont donnees, les verticales se mesurent.
#
# On ne recherche plus les filets du haut et du bas : ils ont deja ete
# SUIVIS, colonne par colonne, pour trouver l'angle de la feuille, et
# meilleur_filet a rendu la rangee ou chacun passe. La redresser ne la
# deplace pas — le point (W/2, y) tourne autour de (W/2, H/2), donc le
# long de l'axe meme de la rotation. On la reprend telle quelle, avec un
# dernier calage a vingt points pres.
def cadre(enc, yh, yb):
    """Le cadre d'une image deja redressee, les horizontales connues."""
    H, W = enc.shape
    mh, mv = round(0.045 * H), round(0.035 * W)

    def caler(y, r=20):
        a, b = max(0, y - r), min(H, y + r + 1)
        p = enc[a:b, mv:W - mv].mean(1)
        return a + int(np.argmax(p)), float(p.max() - np.median(p))

    haut, fh = caler(yh) if yh is not None else (round(0.055 * H), 0.0)
    bas, fb = caler(yb) if yb is not None else (round(0.905 * H), 0.0)
    pg = enc[mh:H - mh, 0:round(0.12 * W)].mean(0)
    pd = enc[mh:H - mh, round(0.88 * W):W].mean(0)
    g = bord_lateral(pg, +1)
    d = bord_lateral(pd, -1)
    gau = 0 if g is None else g
    dro = W - 1 if d is None else round(0.88 * W) + d
    return (gau, haut, dro, bas), (0.0, fh, 0.0, fb)


def netigar(chemin, dest=None, verbeux=True):
    """Redresse et rogne une numerisation, en un seul rechantillonnage."""
    im = Image.open(chemin)
    a = np.asarray(im.convert("L"))
    # LA FEUILLE EST RELIEE EN HAUTEUR, la gravure y est couchee.
    tour = 3 if a.shape[0] > a.shape[1] else 0
    a = np.rot90(a, tour)
    H, W = a.shape
    enc = np.clip(200.0 - a.astype(np.float32), 0, None)
    # 1. l'angle, sur les deux filets horizontaux, suivis point par point.
    #    ON RESSERRE D'ABORD LA BANDE AUTOUR DU FILET. Au tableau 2 le sol
    #    est hachure horizontalement jusqu'au bas de la gravure, et le
    #    suiveur accrochait une hachure au lieu du filet : les deux
    #    mesures se contredisaient alors d'un demi-degre. On repere donc
    #    la ligne la plus encree de la moitie exterieure, et l'on ne suit
    #    le filet qu'a vingt-cinq points de part et d'autre.
    # LA BANDE OU LE FILET SE TROUVE, et nulle part ailleurs. Les seize
    # feuillets sont imprimes de la meme facon : le filet du haut tombe
    # entre le vingt-troisieme et le vingt-septieme centieme du feuillet,
    # celui du bas entre le quatre-vingt-neuvieme et le quatre-vingt-
    # onzieme. Chercher plus large, c'est attraper le bord de la feuille
    # — plus droit que le filet, et faux.
    X0, X1 = round(0.08 * W), round(0.92 * W)
    rh = meilleur_filet(enc, round(0.045 * H), round(0.100 * H), X0, X1)
    rb = meilleur_filet(enc, round(0.875 * H), round(0.925 * H), X0, X1)
    mh, yh = rh if rh else (None, None)
    mb, yb = rb if rb else (None, None)
    # QUAND LES DEUX FILETS SE CONTREDISENT, ON CROIT LE MIEUX MESURE.
    # Ils s'accordent a un dixieme de degre pres sur onze planches ; sur
    # les cinq autres l'un des deux a ete suivi sur moitie moins de
    # colonnes, et c'est lui qui s'ecarte. Le poids d'une mesure, c'est
    # le nombre de colonnes gardees divise par son ecart d'ajustement.
    def poids(m):
        return m[2] / (m[1] + 0.5) if m else 0.0

    duo = [m for m in (mh, mb) if m]
    if len(duo) == 2 and abs(mh[0] - mb[0]) > 0.35:
        th = max(duo, key=poids)[0]
    elif duo:
        pt = sum(poids(m) for m in duo)
        th = sum(m[0] * poids(m) for m in duo) / pt
    else:
        th = 0.0
    # 2. le cadre, mesure sur une copie redressee (jetee ensuite)
    Mr = _tourner(a, th, (W / 2, H / 2))
    droit = cv2.warpAffine(enc, Mr, (W, H), flags=cv2.INTER_LINEAR,
                           borderValue=0)
    (x0, y0, x1, y1), forces = cadre(droit, yh, yb)
    x0, y0 = x0 - MARGE_FILET, y0 - MARGE_FILET
    x1, y1 = x1 + MARGE_FILET, y1 + MARGE_FILET
    # 3. rotation ET rognage en une seule matrice, une seule passe
    M = Mr.copy()
    M[0, 2] -= x0
    M[1, 2] -= y0
    LG, HT = x1 - x0, y1 - y0
    src = np.rot90(np.asarray(im.convert("L")), tour)
    out = cv2.warpAffine(src, M, (LG, HT), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    # controle : ce qui reste de biais aux verticales
    e2 = np.clip(200.0 - out.astype(np.float32), 0, None)
    vg = angle_filet(e2, (round(.05*HT), round(.95*HT), 0, 40), 0, 1.0)[1]
    vd = angle_filet(e2, (round(.05*HT), round(.95*HT), LG-40, LG), 0, 1.0)[1]
    if verbeux:
        def dire(m):
            return (f"{m[0]:+.3f} (ecart {m[1]:.2f} sur {m[2]} points)"
                    if m else "introuvable")
        print(f"  quart de tour {tour}, redressement {th:+.3f} deg")
        print(f"    filet du haut : {dire(mh)}")
        print(f"    filet du bas  : {dire(mb)}")
        print(f"  cadre en ({x0}, {y0})-({x1}, {y1}) : {LG} x {HT} points")
        print(f"  verticales laissees de biais : {vg:+.3f} et {vd:+.3f} deg")
    if dest:
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(out).save(dest)
        if verbeux:
            print(f"  ecrit dans {dest}")
    return out, {"tour": tour, "angulo": round(th, 4),
                 "kadro": [int(x0), int(y0), int(x1), int(y1)],
                 # LES DEUX FILETS SEPAREMENT, avec l'ecart de leur
                 # ajustement : c'est la seule facon de savoir plus tard
                 # si l'on a bien suivi le cadre, et si la feuille etait
                 # droite. Au tableau 2 ils convergent de quatre dixiemes
                 # de degre -- la gravure y est en trapeze, et l'on ne
                 # corrige pas cela sans inventer une geometrie.
                 "filetoj": [[round(m[0], 3), round(m[1], 2), m[2]]
                             if m else None for m in (mh, mb)],
                 "vertikali": [round(vg, 3), round(vd, 3)]}


# -------------------------------------------------------------------
#  LE TRANSPORT DES NUMEROS
# -------------------------------------------------------------------
#  Mille cinq cents numeros ont ete releves a la main sur les planches
#  colorisees. Ils sont enregistres EN FRACTION de la planche : pour les
#  porter sur la numerisation d'origine, il suffit de la similitude qui
#  mene de l'une a l'autre.
#
#  ELLE SE MESURE PAR CORRELATION, sur une carte de densite d'encre —
#  les deux images floutees, centrees, reduites. Le pochoir et le
#  fac-simile ne se ressemblent pas trait pour trait, mais leurs masses
#  d'encre, oui : au tableau 1 la correlation monte a 0.95.
#
#  ATTENTION AU SENS DE L'ENCRE. Dans la couche de trait l'encre vaut
#  255, dans une numerisation elle est sombre. Les avoir prises dans le
#  meme sens faisait tomber la correlation de 0.95 a 0.10, et l'on
#  cherchait la faute ailleurs.
def densito(a, W, sigma=1.6):
    """Une carte de densite d'encre, comparable d'un rendu a l'autre."""
    h = round(W * a.shape[0] / a.shape[1])
    s = cv2.resize(a.astype(np.float32), (W, h), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), sigma)
    return (s - s.mean()) / (s.std() + 1e-6)


def mezuri(cle, neta, W=1000, verbeux=True):
    """La matrice qui mene de l'ancienne planche a la nouvelle."""
    # LA REFERENCE EST LA PLANCHE PRECEDENTE, quelle qu'elle soit. La
    # premiere fois c'est la couche de trait du PDF colorise, ou l'encre
    # vaut 255 ; ensuite, si l'on renettoie, c'est le fac-simile deja
    # nettoye, ou l'encre est sombre. Sans cela un second nettoyage
    # ferait repartir les numeros du pochoir, qu'ils ont quitte.
    ancienne = RACINE / "originali" / "kovri" / f"{cle}-neta-antaua.png"
    if ancienne.exists():
        vieux = 255.0 - np.asarray(Image.open(ancienne).convert("L")
                                   ).astype(np.float32)
    else:
        vieux = np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png")
                           ).astype(np.float32)      # l'encre y vaut 255
    neuf = 255.0 - np.asarray(Image.open(neta).convert("L")).astype(np.float32)
    LO, HO = vieux.shape[1], vieux.shape[0]
    LN, HN = neuf.shape[1], neuf.shape[0]
    sO, sN = W / LO, W / LN
    A, B = densito(vieux, W), densito(neuf, W)

    def essai(k, th, m=0.14):
        hA, wA = A.shape
        M = cv2.getRotationMatrix2D((wA / 2, hA / 2), th, k)
        r = cv2.warpAffine(A, M, (wA, hA), flags=cv2.INTER_LINEAR,
                           borderValue=0)
        y0, y1 = round(m * hA), round((1 - m) * hA)
        x0, x1 = round(m * wA), round((1 - m) * wA)
        g = r[y0:y1, x0:x1]
        if g.shape[0] >= B.shape[0] or g.shape[1] >= B.shape[1]:
            return None
        res = cv2.matchTemplate(B, g, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(res)
        return float(mx), float(k), float(th), loc, (x0, y0)

    best = None
    for k in np.arange(0.90, 1.101, 0.005):
        for th in np.arange(-1.0, 1.01, 0.1):
            e = essai(k, th)
            if e and (best is None or e[0] > best[0]):
                best = e
    for k in np.arange(best[1] - 0.006, best[1] + 0.0061, 0.0005):
        for th in np.arange(best[2] - 0.12, best[2] + 0.121, 0.01):
            e = essai(k, th)
            if e and e[0] > best[0]:
                best = e
    mx, k, th, loc, (gx, gy) = best
    hA, wA = A.shape
    M3 = np.vstack([cv2.getRotationMatrix2D((wA / 2, hA / 2), th, k), [0, 0, 1]])
    D = np.array([[1, 0, loc[0] - gx], [0, 1, loc[1] - gy], [0, 0, 1]], float)
    T = np.diag([1 / sN, 1 / sN, 1.0]) @ D @ M3 @ np.diag([sO, sO, 1.0])
    if verbeux:
        print(f"  {cle} : correlation {mx:.4f}, echelle {T[0, 0]:.5f}, "
              f"rotation {th:+.2f} deg")
        print(f"  l'ancienne planche ({LO} x {HO}) se pose en "
              f"({T[0, 2]:.0f}, {T[1, 2]:.0f}) de la nouvelle ({LN} x {HN})")
    return T, float(mx), (LO, HO), (LN, HN)


def _pt(T, x, y):
    q = T @ np.array([x, y, 1.0])
    return float(q[0]), float(q[1])


def deja_porte(cle):
    """Ce tableau a-t-il deja ete porte sur son original ?"""
    if not CATALOGO.exists():
        return False
    return "transporto" in json.loads(
        CATALOGO.read_text(encoding="utf-8")).get(cle, {})


# LE TRANSPORT NE SE FAIT QU'UNE FOIS. Le refaire appliquerait la
# similitude a des positions qui l'ont deja subie, et les mille cinq
# cents numeros partiraient de travers sans que rien ne le signale.
# L'outil refuse donc de recommencer, a moins qu'on ne le lui dise.
def transporti(cle, neta, verbeux=True, force=False):
    """Porte les numeros, les scenes et les tailles sur la nouvelle planche."""
    if deja_porte(cle) and not force:
        raise SystemExit(
            f"  {cle} : deja porte sur son original. Recommencer "
            f"deplacerait les numeros une seconde fois.\n"
            f"  Si c'est bien ce qu'on veut : ajouter « force ».")
    T, korelo, (LO, HO), (LN, HN) = mezuri(cle, neta, verbeux=verbeux)
    k = float(np.hypot(T[0, 0], T[1, 0]))

    # CE QUI SORT DE LA PLANCHE NE SE GARDE PAS. Le rognage ne tombe pas
    # au meme endroit d'une reprise a l'autre — il suit les filets, et
    # les filets se mesurent — de sorte qu'un numero pose tout au bord
    # peut se retrouver dehors. Le garder, c'est promettre un gros plan
    # sur du vide. On le dit, et on le laisse tomber : il sera a
    # rechercher sur la nouvelle planche.
    perdus = []

    def boite(v, nom=""):
        """(x, y, l, h) en fraction de l'ancienne -> de la nouvelle."""
        x, y = _pt(T, v[0] * LO, v[1] * HO)
        cx, cy = x + v[2] * LO * k / 2, y + v[3] * HO * k / 2
        if not (0 <= cx < LN and 0 <= cy < HN):
            perdus.append(nom)
            return None
        return [round(x / LN, 6), round(y / HN, 6),
                round(v[2] * LO * k / LN, 6), round(v[3] * HO * k / HN, 6)] \
            + list(v[4:])

    n = 0
    f = RACINE / "gravuri" / "numeri.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    if cle in d:
        e = d[cle]
        e["numeri"] = {q: b for q, v in e["numeri"].items()
                       if (b := boite(v, q)) is not None}
        e["largeur"], e["alteso"] = LN, HN
        e["corpo"] = max(1, round(e["corpo"] * k))
        n += len(e["numeri"])
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    m = 0
    f = RACINE / "gravuri" / "manuali.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if cle in d:
            d[cle] = {q: b for q, v in d[cle].items()
                      if (b := boite(v, q)) is not None}
            m = len(d[cle])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    c = 0
    f = RACINE / "gravuri" / "ceni.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if cle in d:
            for sc, forme in d[cle].items():
                if forme[0] == "elipso":
                    x, y = _pt(T, forme[1] * LO, forme[2] * HO)
                    d[cle][sc] = ["elipso", round(x / LN, 6), round(y / HN, 6),
                                  round(forme[3] * LO * k / LN, 6),
                                  round(forme[4] * HO * k / HN, 6)]
                else:
                    x0, y0 = _pt(T, forme[1] * LO, forme[2] * HO)
                    x1, y1 = _pt(T, forme[3] * LO, forme[4] * HO)
                    d[cle][sc] = ["rekt", round(max(0.0, x0 / LN), 6),
                                  round(max(0.0, y0 / HN), 6),
                                  round(min(1.0, x1 / LN), 6),
                                  round(min(1.0, y1 / HN), 6)]
                c += 1
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    lt = 0
    f = RACINE / "gravuri" / "literi.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get(cle):
            d[cle] = {q: b for q, v in d[cle].items()
                      if (b := boite(v, q)) is not None}
            lt = len(d[cle])
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
           if CATALOGO.exists() else {})
    e = cat.setdefault(cle, {})
    e["transporto"] = {"matrico": [[float(v) for v in r] for r in T[:2]],
                       "korelo": round(korelo, 4),
                       "de": [LO, HO], "a": [LN, HN]}
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    if verbeux:
        print(f"  {n} numeros portes, dont {m} poses a la main"
              + (f", {c} scenes" if c else "")
              + (f", {lt} lettres" if lt else ""))
        if perdus:
            print(f"  ATTENTION : {len(perdus)} sortis de la planche au "
                  f"rognage, a rechercher — {', '.join(sorted(perdus))}")
    return T


# -------------------------------------------------------------------
#  SERVIR LA PLANCHE
# -------------------------------------------------------------------
#  Deux tailles, comme avant : la vue d'ensemble posee au-dessus du
#  titre, et l'image ou l'on decoupe les gros plans. Mais celle-ci n'est
#  plus rabotee a 2600 points : ON SERT LA PLANCHE ENTIERE.
#
#  La mesure le demande. Le gros plan montre neuf hauteurs de chiffre,
#  soit deux cent quatre-vingt-dix points de planche, sur deux cent
#  cinquante points d'ecran — cinq cents sur un ecran a double densite.
#  Meme a pleine definition on est donc en dessous du compte : rogner
#  encore n'aurait aucun sens. A 2600 points, en outre, la hachure fine
#  moire, ce qui ne pardonne pas sur une gravure sur bois.
#
#  L'image ne coute qu'au PREMIER clic sur un numero du tableau, et sert
#  ensuite a tous les autres.
LARGE_VIDO = 1200
QUAL_VIDO = 74
QUAL_DETALO = 74


# LA QUALITE DU DETAIL SE REGLE PAR PLANCHE. Le fac-simile a quatre
# mille cinq cents points de large : a soixante-quatorze, le WebP a de
# la place et n'y perd rien de visible. L'original en couleur n'en a
# que deux mille deux cents, et la meme qualite le grumelait — le
# « PIANOS » du batiment (10) du tableau 14 s'y lisait moins bien que
# sur le PDF d'origine. Moins de points, plus de qualite : le fichier
# reste plus leger que celui d'un fac-simile.
# -------------------------------------------------------------------
#  LE TON : RENDRE SON NOIR A LA PLANCHE
# -------------------------------------------------------------------
#  LES QUATORZE PLANCHES EN GRIS N'AVAIENT PAS DE NOIR. Leur encre la
#  plus sombre s'arretait entre 45 et 65 sur 255, et au plus un point
#  sur dix mille descendait sous 40 -- quand les deux planches en
#  couleur, servies a cote d'elles dans la meme galerie, descendent a
#  11 et 13 avec trois a quatre points sur cent vraiment noirs. C'est
#  ce voisinage que l'oeil lisait comme de la paleur.
#
#  CE N'ETAIT PAS NOTRE TRAITEMENT : netigar redresse et rogne, il ne
#  touchait pas au ton. La paleur vient des numerisations d'origine.
#
#  ON ETIRE DONC ENTRE DEUX CENTILES, planche par planche -- les
#  numerisations different trop pour un reglage commun. Le point noir
#  au centile 0,05, le point blanc au centile 99,5.
#
#  LE POINT BLANC A ETE LE POINT DISCUTE, et la mesure a tranche contre
#  l'intuition. Le deplacer ecrase six points sur mille au blanc, contre
#  trois avant : on a d'abord cru que c'etait le grain du papier qui
#  partait. Le releve dit autre chose. Le gradient moyen la ou l'on
#  ecrase vaut 16 a 18, soit celui du reste de la planche ; deux points
#  sur mille seulement de ces points-la n'ont aucun voisin different
#  d'eux. Ce ne sont pas des aplats de papier : c'est le bord CLAIR des
#  traits. Les blanchir ne supprime aucune ligne, cela detache la ligne
#  de son papier. Le compte des gradients faibles en zone claire --
#  la hachure fine, ce qu'on risquait de perdre -- le confirme : il
#  monte a 107-111 pour cent apres etirement, exactement comme si l'on
#  gardait le blanc a 255.
#
#  ET GARDER LE BLANC A 255 COUTAIT PLUS QUE CELA N'EPARGNAIT. Le
#  papier median tombait alors de 227 a 217, quand le fond de la page
#  de lecture vaut 250 : la planche se posait sur la page comme un
#  rectangle plus gris qu'avant. Au centile 99,5 il reste a 224.
#
#  APPROCHE ESSAYEE ET ABANDONNEE : un raccord souple au lieu d'un
#  ecretage franc, pour ne rien ecraser du tout. C'est la seule des
#  quatre variantes qui abime le trace -- la hachure fine tombe a
#  86-93 pour cent, parce que la courbe tasse justement le haut du
#  signal, la ou vit le trait clair. Retiree.
#
#  ON NE VA PAS PLUS LOIN QUE LE CENTILE 99,5, et cela s'est mesure
#  aussi : au centile 98 la hachure fine tient encore (103-108 %), au
#  centile 96 elle commence a tomber (91 % au tableau 7), au centile 92
#  elle s'effondre (63 %). Le gain d'ecart-type entre 99,5 et 98 ne vaut
#  que deux pour cent. On s'arrete ou le gain cesse de payer.
#
#  LES DEUX PLANCHES EN COULEUR NE PASSENT PAS PAR LA : kolorigo.py
#  appelle servir() avec tono=False. Elles ont deja leur noir.
TONO_NOIR = 0.05
TONO_BLANC = 99.5


def tonigar(im):
    """Etire le ton entre deux centiles. Rend l'image et les bornes."""
    a = np.asarray(im.convert("L")).astype(np.float32)
    noir = float(np.percentile(a, TONO_NOIR))
    blanc = float(np.percentile(a, TONO_BLANC))
    if blanc - noir < 1.0:
        return im, None
    b = np.clip((np.asarray(im).astype(np.float32) - noir) / (blanc - noir),
                0, 1) * 255.0
    return (Image.fromarray(np.round(b).astype(np.uint8), mode=im.mode),
            {"noir": round(noir, 1), "blanc": round(blanc, 1),
             "faktoro": round(255.0 / (blanc - noir), 4)})


def servir(cle, neta, verbeux=True, qual_detalo=None, tono=True):
    """Les deux WebP, tires de la planche d'origine nettoyee."""
    im = Image.open(neta).convert("RGB")
    par_tono = None
    if tono:
        im, par_tono = tonigar(im)
        if verbeux and par_tono:
            print(f"  ton : noir {par_tono['noir']:.0f}, "
                  f"blanc {par_tono['blanc']:.0f}, "
                  f"facteur x{par_tono['faktoro']:.3f}")
    GRAVURI = RACINE / "gravuri"
    taille = {}
    for nom, largeur, qualite in (("vido", LARGE_VIDO, QUAL_VIDO),
                                  ("detalo", im.width,
                                   qual_detalo or QUAL_DETALO)):
        h = round(largeur * im.height / im.width)
        petite = im if largeur == im.width else im.resize((largeur, h),
                                                          Image.LANCZOS)
        dest = GRAVURI / f"{cle}-{nom}.webp"
        petite.save(dest, format="WEBP", quality=qualite, method=6)
        o = dest.stat().st_size
        taille[nom] = {"largeur": petite.width, "alteso": petite.height,
                       "okteti": o}
        if verbeux:
            print(f"  {cle}-{nom}.webp  {petite.width}x{petite.height}  "
                  f"{o / 1024:.0f} Ko")
    cat = GRAVURI / "gravuri.json"
    tout = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    tout[cle] = {"largeur": im.width, "alteso": im.height,
                 "koloro": False, "fonto": Path(neta).name,
                 "origino": True,
                 "vido": taille["vido"], "detalo": taille["detalo"]}
    if par_tono:
        tout[cle]["tono"] = par_tono
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")


# -------------------------------------------------------------------
#  LA REPRISE ENTIERE, EN UNE COMMANDE
# -------------------------------------------------------------------
#  Nettoyer, porter les numeros, servir les deux images : trois gestes
#  qui vont toujours ensemble et dans cet ordre. Quinze planches
#  restent a reprendre ; autant ne pas les taper trois fois chacune.
#
#      python3 outils/originali.py reprendre t02-apar-1 originali/t02.jpg
def reprendre(cle, chemin, force=False):
    dest = RACINE / "originali" / "kovri" / f"{cle}-neta.png"
    # On met de cote la planche precedente : c'est sur ELLE que les
    # numeros sont poses, et c'est d'elle qu'il faudra les porter.
    if dest.exists():
        dest.replace(dest.with_name(f"{cle}-neta-antaua.png"))
    out, par = netigar(chemin, dest)
    cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
           if CATALOGO.exists() else {})
    e = cat.setdefault(cle, {})
    e["fonto"] = str(chemin)
    e["netigo"] = par
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    transporti(cle, dest, force=force)
    servir(cle, dest)
    print(f"  {cle} : repris. Verifier la planche de controle, "
          f"puis relancer numeri.py et html.py.")


# -------------------------------------------------------------------
#  REPRENDRE LE TON DES PLANCHES EN GRIS
# -------------------------------------------------------------------
#  Le ton se calcule a chaque service, depuis le PNG sans perte : ce
#  verbe ne fait donc que re-servir. Il est idempotent -- on peut le
#  relancer sans empiler deux etirements l'un sur l'autre, parce que
#  rien n'est jamais ecrit dans le PNG d'origine.
#
#      python3 outils/originali.py toni
def toni():
    cat = json.loads((RACINE / "gravuri" / "gravuri.json")
                     .read_text(encoding="utf-8"))
    kovri = RACINE / "originali" / "kovri"
    n = 0
    for cle in sorted(cat):
        if cat[cle].get("koloro"):
            print(f"{cle} : en couleur, laissee telle quelle")
            continue
        neta = kovri / f"{cle}-neta.png"
        if not neta.exists():
            print(f"{cle} : {neta.name} introuvable, passee")
            continue
        print(f"{cle} :")
        servir(cle, neta)
        n += 1
    print(f"\n{n} planches re-servies avec leur ton redresse.")


def main(args):
    if args and args[0] == "toni":
        return toni()
    if len(args) < 2:
        raise SystemExit(__doc__)
    verbe, cle, chemin = args[0], args[1], args[2]
    if verbe == "reprendre":
        reprendre(cle, chemin, force="force" in args)
    elif verbe == "netigar":
        cle_ = cle
        out, par = netigar(chemin, RACINE / "originali" / "kovri" /
                           f"{cle_}-neta.png")
        cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
               if CATALOGO.exists() else {})
        e = cat.setdefault(cle_, {})
        e["fonto"] = str(chemin)
        e["netigo"] = par
        CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verbe == "servir":
        servir(cle, chemin)
    elif verbe == "toni":
        toni()
    elif verbe == "transporti":
        transporti(cle, chemin, force="force" in args)
    elif verbe == "caler":
        M, score, tour = caler(cle, chemin)
        cat = (json.loads(CATALOGO.read_text(encoding="utf-8"))
               if CATALOGO.exists() else {})
        cat[cle] = {"fonto": str(chemin), "tour": tour,
                    "matrico": [[float(v) for v in r] for r in M],
                    "korelo": round(float(score), 4)}
        CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1)
                            + "\n", encoding="utf-8")
    elif verbe == "compar":
        cx = float(args[3]) if len(args) > 3 else 0.5
        cy = float(args[4]) if len(args) > 4 else 0.5
        compar(cle, chemin, cx, cy)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
