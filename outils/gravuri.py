#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gravuri.py — prepare les tableaux muraux pour la page de lecture.

    python3 outils/gravuri.py t01-apar-1 gravuri/font/page1.pdf
    python3 outils/gravuri.py t02-tit-0  gravuri/font/page2.pdf
    python3 outils/gravuri.py --tuto          # ce que fait l'outil, en detail

UNE PLANCHE SE RANGE SOUS UNE CLE DE BLOC, non sous un numero de
tableau. La plupart illustrent l'ouverture -- « t01-apar-1 » -- mais pas
toutes : la figure du corps humain va sous « La Korpo homala. », donc
sous t02-tit-0, et le plan de la maison sous le « (Videz la plano.) »
du tableau 5, donc sous t05-apar-2. C'est la cle qui dit ou la gravure
se pose, et un tableau peut en porter plusieurs.

DEUX ESPECES DE PLANCHES. Les tableaux muraux sont en deux couches (voir
plus bas) ; le plan de la maison et la figure du corps humain, eux, sont
de purs traces vectoriels, sans couleur ni image. On les rastere alors,
a 300 points par pouce, et le reste ne change pas.

CE QU'IL Y A DANS UN PDF DE TABLEAU. Le tableau mural n'est pas une
image plate : c'est un empilement de DEUX COUCHES, et c'est la tout
l'interet.

    dessous   la couleur, en JPEG ~2270x1520
    dessus    le trait grave, dont l'encre est NOIRE PURE et dont tout
              le dessin tient dans un canal alpha de ~5460x3660

La gravure est donc intacte et separee de la couleur : on peut reprendre
l'une sans jamais toucher a l'autre. C'est ce qui rend les corrections
de couleur possibles -- et c'est pourquoi cet outil garde les deux
couches a part dans gravuri/kovri/ avant de les composer.

DEUX SORTIES, PARCE QU'IL Y A DEUX USAGES.

    <cle>-vido.webp     ~1000px   la vue d'ensemble posee au-dessus du
                                  titre du tableau. Elle se charge quand
                                  le tableau entre dans le champ.
    <cle>-detalo.webp   ~2600px   l'image ou l'on decoupe les gros plans.
                                  Elle n'est cherchee qu'au PREMIER clic
                                  sur un numero du tableau, et sert
                                  ensuite a tous les autres : un gros
                                  plan n'est qu'un recadrage de celle-ci,
                                  jamais un nouveau chargement.

POURQUOI COMPOSER ICI, ET NON DANS LE NAVIGATEUR. On pourrait envoyer
les deux couches et les superposer a l'ecran ; ce serait meme commode
pour reprendre la couleur. Mais la mesure tranche : a 2600px, le trait
seul pese 1229 Ko et la couleur 142, quand leur composite pese 868. Le
trait est une gravure sur bois, toute en hachures, et il se comprime
bien mieux une fois la couleur dessous. On compose donc ici.

    gravuri/font/     les PDF d'origine (non versionnes : ~100 Mo)
    gravuri/kovri/    les deux couches extraites (non versionnees)
    gravuri/          les deux WebP par tableau (VERSIONNES, ~1 Mo)
"""
import io
import json
import sys
from pathlib import Path

import pikepdf
from PIL import Image
from pikepdf import PdfImage

Image.MAX_IMAGE_PIXELS = None
RACINE = Path(__file__).resolve().parent.parent
GRAVURI = RACINE / "gravuri"

# La vue d'ensemble n'a pas besoin d'etre grande : elle tient dans la
# largeur d'une colonne. L'image de detail, elle, porte les gros plans,
# et c'est elle qui decide de leur nettete. 2600px donne un gros plan de
# 400px de source dans une boite de 700 : un peu doux, mais lisible, et
# elle ne pese que 868 Ko la ou 3200px en pese 1165.
# 1200 et non 1000 : un ecran de bureau ordinaire affiche la gravure sur
# environ 1090 points, et une vue d'ensemble de 1000 passait donc juste
# au-dessous -- le navigateur allait alors chercher l'image de detail,
# huit fois plus lourde, pour un ecran qui n'en avait pas besoin. A 1200
# elle couvre aussi les telephones, dont l'ecran triple densite reclame
# un millier de points ; seul un grand ecran Retina monte au detail.
LARGE_VIDO = 1200
LARGE_DETALO = 2600
QUAL_VIDO = 72
QUAL_DETALO = 72


def kovri(pdf):
    """Les images d'un PDF de tableau, y compris dans les Form XObject.

    Le document doit rester OUVERT tant qu'on se sert des objets rendus :
    pikepdf les detruit avec lui, et l'on recolte alors un « object of
    type destroyed » a la premiere lecture.
    """
    # Le trait est enferme dans un Form ; une lecture qui ne descend pas
    # dedans ne trouve que la couleur, et l'on croit le fichier plat.
    trouve = []
    vus = set()

    def descendre(res):
        for nom, obj in dict(res.get("/XObject", {})).items():
            if obj.objgen in vus:
                continue
            vus.add(obj.objgen)
            if obj.get("/Subtype") == "/Image":
                trouve.append(obj)
            elif obj.get("/Subtype") == "/Form":
                descendre(obj.get("/Resources", {}))

    for page in pdf.pages:
        descendre(page.get("/Resources", {}))
    return trouve


def rasterer(chemin, dpi=300):
    """Une planche vectorielle, rendue en un masque de trait."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile",
                        str(chemin), str(base)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(str(base) + ".png").convert("L")
        im.load()
    # Le rendu est noir sur blanc ; le reste de l'outil attend un ALPHA,
    # ou le blanc est l'encre. On retourne donc, et les deux especes de
    # planches se composent ensuite de la meme facon.
    return Image.eval(im, lambda v: 255 - v)


def separer(chemin):
    """(couleur RGB, trait en alpha) d'un PDF de tableau."""
    couleur = trait = None
    pdf = pikepdf.open(chemin)
    images = kovri(pdf)
    if not images:
        # UNE PLANCHE PUREMENT VECTORIELLE. Le plan de la maison et la
        # figure du corps humain n'ont ni couleur ni image : tout y est
        # trace. On les rastere, et le trait sort noir sur blanc.
        return None, rasterer(chemin)
    for obj in images:
        if "/SMask" in obj:
            # L'ENCRE EST NOIRE PURE : on l'a verifiee, son canal de gris
            # vaut 0 partout. Tout le dessin est donc dans le masque, et
            # c'est LUI qu'il faut garder -- en pleine resolution, alors
            # que l'encre elle-meme n'est qu'une nappe noire basse
            # definition.
            trait = PdfImage(obj.SMask).as_pil_image().convert("L")
        else:
            couleur = PdfImage(obj).as_pil_image().convert("RGB")
    if trait is None or couleur is None:
        raise SystemExit(f"{chemin} : couche manquante "
                         f"(trait={trait is not None}, "
                         f"couleur={couleur is not None})")
    return couleur, trait


def recaler(couleur, trait):
    """L'etirement et le decalage qui posent la couleur sur le trait.

    LES DEUX COUCHES NE SE SUPERPOSENT PAS, et l'ecart n'est pas une
    simple translation : elles n'ont pas le meme rapport de cotes -- la
    planche 13 donne 1.4902 pour la couleur et 1.4775 pour le trait.
    Porter l'une au cadre de l'autre promene donc le bord : la couleur
    tombe juste au milieu de l'image et de plus en plus a cote qu'on
    s'en ecarte. C'est ce que l'oeil voit comme un debordement des
    aplats hors du contour.

    ON MESURE LE DEPLACEMENT, ON NE LE CHERCHE PAS A TATONS. Une grille
    d'etirements essayes un a un ne convergeait pas : le score global de
    correlation est plat, la couleur ayant ete peinte a la main sur le
    trait et non decalquee. Mais un deplacement mesure ZONE PAR ZONE dit
    tout : s'il croit regulierement avec x, sa pente EST l'etirement qui
    manque, et son ordonnee le decalage.

    Chaque zone est recalee par correlation normalisee de son trait avec
    le contour de la couleur, et l'on ne garde que la moitie des zones
    dont le pic domine nettement le reste de la surface -- un aplat de
    ciel ou un mur nu ne dit rien de l'alignement. Une droite robuste
    passe ensuite dans le nuage, les points aberrants rejetes ; trois a
    cinq tours suffisent, et l'on retient le tour ou la derive residuelle
    et l'ecart median sont les plus faibles.

    Rend (sx, sy, dx, dy) : la couleur est portee a (sx * largeur,
    sy * hauteur), puis translatee de (dx, dy).
    """
    import cv2
    import numpy as np

    W, HT = trait.width, trait.height
    T = np.asarray(trait, np.float32)
    gris = couleur.convert("L")

    def champ(sx, sy, dx, dy, nx=12, ny=8, cote=430, ray=24, garde=0.5):
        """Le deplacement qui reste, zone par zone, avec sa confiance."""
        g = np.asarray(gris.resize((max(2, round(W * sx)),
                                    max(2, round(HT * sy))), Image.LANCZOS),
                       np.float32)
        a = np.zeros((HT, W), np.float32)
        hh, ww = min(HT, g.shape[0]), min(W, g.shape[1])
        a[:hh, :ww] = g[:hh, :ww]
        if hh < HT:
            a[hh:] = a[hh - 1]
        if ww < W:
            a[:, ww:] = a[:, ww - 1:ww]
        a = np.roll(a, (dy, dx), (0, 1))
        gy, gx = np.gradient(a)
        cont = np.hypot(gx, gy)
        pts = []
        for iy in range(ny):
            for ix in range(nx):
                x0 = max(ray, min(W - cote - ray,
                                  round(W * (ix + .5) / nx) - cote // 2))
                y0 = max(ray, min(HT - cote - ray,
                                  round(HT * (iy + .5) / ny) - cote // 2))
                tt = T[y0:y0 + cote, x0:x0 + cote]
                if tt.std() < 1:
                    continue
                r = cv2.matchTemplate(
                    cont[y0 - ray:y0 + cote + ray, x0 - ray:x0 + cote + ray],
                    tt - tt.mean(), cv2.TM_CCOEFF_NORMED)
                _, mx, _, loc = cv2.minMaxLoc(r)
                # La confiance est l'avance du pic sur le reste de la
                # surface : un pic large et mou ne situe rien.
                m = r.copy()
                cv2.circle(m, loc, 6, -1, -1)
                pts.append((x0 + cote / 2, y0 + cote / 2,
                            loc[0] - ray, loc[1] - ray, mx - m.max()))
        p = np.array(pts, float)
        if not len(p):
            return p
        return p[p[:, 4] >= np.quantile(p[:, 4], 1 - garde)]

    def droite(v, d):
        for _ in range(3):
            a, b = np.polyfit(v, d, 1)
            r = d - (a * v + b)
            bons = np.abs(r) <= max(1.2, 2.2 * r.std())
            if bons.all() or bons.sum() < 4:
                break
            v, d = v[bons], d[bons]
        return a, b

    sx = sy = 1.0
    dx = dy = 0
    meilleur = None
    for _ in range(5):
        p = champ(sx, sy, dx, dy)
        if len(p) < 6:
            break
        ax, bx = droite(p[:, 0], p[:, 2])
        ay, by = droite(p[:, 1], p[:, 3])
        cout = (abs(ax * W) + abs(ay * HT)
                + np.median(np.abs(p[:, 2])) + np.median(np.abs(p[:, 3])))
        if meilleur is None or cout < meilleur[0]:
            meilleur = (cout, sx, sy, dx, dy)
        sx, sy = sx * (1 - ax), sy * (1 - ay)
        dx, dy = round(dx * (1 - ax) - bx), round(dy * (1 - ay) - by)
    if meilleur is None:
        return 1.0, 1.0, 0, 0
    print(f"  alignement : derive residuelle et ecart median, "
          f"somme {meilleur[0]:.1f} px")
    return meilleur[1], meilleur[2], meilleur[3], meilleur[4]


def composer(couleur, trait):
    """La couleur dessous, l'encre noire dessus selon l'alpha du trait.

    Sans couche de couleur -- une planche vectorielle --, le fond est le
    papier.
    """
    import numpy as np

    if couleur is None:
        fond = Image.new("RGB", trait.size, (255, 255, 255))
    else:
        sx, sy, dx, dy = recaler(couleur, trait)
        print(f"  recalage de la couleur : etirement {sx:.4f} x {sy:.4f}, "
              f"decalage {dx:+d}, {dy:+d} px")
        etire = couleur.resize((max(2, round(trait.width * sx)),
                                max(2, round(trait.height * sy))),
                               Image.LANCZOS)
        # Le bord decouvert reprend la couleur voisine plutot que du
        # blanc, qui trancherait sous la gravure.
        a = np.asarray(etire.convert("RGB"))
        g = np.zeros((trait.height, trait.width, 3), a.dtype)
        hh = min(trait.height, a.shape[0])
        ww = min(trait.width, a.shape[1])
        g[:hh, :ww] = a[:hh, :ww]
        if hh < trait.height:
            g[hh:] = g[hh - 1]
        if ww < trait.width:
            g[:, ww:] = g[:, ww - 1:ww]
        if dx or dy:
            g = np.roll(g, (dy, dx), (0, 1))
        fond = Image.fromarray(g)
    return Image.composite(Image.new("RGB", trait.size, (0, 0, 0)), fond, trait)


def poser(im, chemin, largeur, qualite):
    h = round(largeur * im.height / im.width)
    petite = im.resize((largeur, h), Image.LANCZOS)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    petite.save(chemin, format="WEBP", quality=qualite, method=6)
    return petite.size, chemin.stat().st_size


def preparer(cle, chemin):
    couleur, trait = separer(chemin)
    print(f"  couleur {couleur.size if couleur else '(aucune)'}"
          f"   trait {trait.size}")

    # Les couches restent a part : c'est sur elles qu'on reprendra les
    # couleurs, la gravure n'ayant pas a en souffrir.
    kov = GRAVURI / "kovri"
    kov.mkdir(parents=True, exist_ok=True)
    if couleur is not None:
        couleur.save(kov / f"{cle}-koloro.png")
    trait.save(kov / f"{cle}-trako.png")

    plein = composer(couleur, trait)
    taille = {}
    for nom, largeur, qualite in (("vido", LARGE_VIDO, QUAL_VIDO),
                                  ("detalo", LARGE_DETALO, QUAL_DETALO)):
        dim, octets = poser(plein, GRAVURI / f"{cle}-{nom}.webp", largeur, qualite)
        taille[nom] = {"largeur": dim[0], "alteso": dim[1], "okteti": octets}
        print(f"  {cle}-{nom}.webp  {dim[0]}x{dim[1]}  {octets/1024:.0f} Ko")

    # Le catalogue dit a la page quels tableaux ont une gravure, et dans
    # quelles proportions -- de quoi reserver la place avant meme que
    # l'image soit chargee, sans quoi la page sursaute au chargement.
    cat = GRAVURI / "gravuri.json"
    tout = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    # La source est notee : sans elle, on ne savait plus quelle planche
    # venait de quel fichier, et refaire la serie demandait de comparer
    # des dimensions.
    tout[cle] = {"largeur": plein.width, "alteso": plein.height,
                 "koloro": couleur is not None, "fonto": Path(chemin).name,
                 "vido": taille["vido"], "detalo": taille["detalo"]}
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    return plein


if __name__ == "__main__":
    if "--tuto" in sys.argv or len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(0)
    preparer(sys.argv[1], Path(sys.argv[2]))
