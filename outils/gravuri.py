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


def recaler(couleur, trait, marge=24):
    """L'etirement et le decalage qui posent la couleur sur le trait.

    LES DEUX COUCHES NE SE SUPERPOSENT PAS. Elles viennent de deux
    chaines differentes -- la gravure vectorisee d'un cote, la couleur
    d'un modele de l'autre -- et l'ecart n'est pas seulement une
    translation : LES DEUX COUCHES N'ONT PAS LE MEME RAPPORT DE COTES.
    La planche 13 donne 1.4902 pour la couleur et 1.4775 pour le trait ;
    etirer l'une au cadre de l'autre, comme on faisait, promene le bord
    de trente et un pixels. Le recalage tombait juste au milieu de
    l'image et faux sur les bords, et c'est exactement ce qu'on voyait :
    des aplats qui debordent du contour, de plus en plus loin qu'on
    s'ecarte du centre.

    On cherche donc quatre nombres et non deux -- deux etirements, deux
    decalages. Le critere ne change pas : les CONTOURS de la couleur
    doivent tomber sur les traits de la gravure, on correle le gradient
    de l'une avec le trait de l'autre. Le calcul se fait sur une
    reduction, ou tout est mille fois plus rapide, puis se rapporte a
    l'echelle d'origine.

    Rend (sx, sy, dx, dy) : la couleur est d'abord portee a
    (sx * largeur, sy * hauteur), puis translatee de (dx, dy).
    """
    import numpy as np

    gris = couleur.convert("L")

    def carte(ech, sx, sy):
        """Le contour de la couleur, etiree de (sx, sy), au cadre reduit."""
        h = round(ech * trait.height / trait.width)
        c = np.asarray(gris.resize((max(2, round(ech * sx)),
                                    max(2, round(h * sy))), Image.LANCZOS),
                       dtype=np.float32)
        # Ramener au cadre commun : on rogne ou l'on complete par le bord,
        # de sorte que le decalage se compte toujours dans le meme repere.
        g = np.zeros((h, ech), np.float32)
        hh, ww = min(h, c.shape[0]), min(ech, c.shape[1])
        g[:hh, :ww] = c[:hh, :ww]
        if hh < h:
            g[hh:] = g[hh - 1]
        if ww < ech:
            g[:, ww:] = g[:, ww - 1:ww]
        gy, gx = np.gradient(g)
        m = np.hypot(gx, gy)
        return m - m.mean()

    def trace(ech):
        h = round(ech * trait.height / trait.width)
        t = np.asarray(trait.resize((ech, h), Image.LANCZOS), dtype=np.float32)
        return t - t.mean()

    def chercher(ech, centre, rayon, echelles):
        t = trace(ech)
        f = trait.width / ech
        cx, cy = round(centre[0] / f), round(centre[1] / f)
        meilleur = None
        for sx, sy in echelles:
            cont = carte(ech, sx, sy)
            for dy in range(cy - rayon, cy + rayon + 1):
                for dx in range(cx - rayon, cx + rayon + 1):
                    a = np.roll(np.roll(cont, dy, 0), dx, 1)
                    s = float((a * t).sum())
                    if meilleur is None or s > meilleur[0]:
                        meilleur = (s, sx, sy, round(dx * f), round(dy * f))
        return meilleur[1], meilleur[2], meilleur[3], meilleur[4]

    # TROIS PASSES. La premiere cherche l'etirement sur une forte
    # reduction, ou une grille de vingt-cinq combinaisons coute peu ; la
    # deuxieme resserre autour d'elle ; la troisieme fixe le decalage au
    # pixel pres, l'etirement etant desormais tenu.
    pas = [1 - 0.010, 1 - 0.005, 1.0, 1 + 0.005, 1 + 0.010]
    sx, sy, dx, dy = chercher(
        520, (0, 0), max(1, round(marge * 520 / trait.width)),
        [(a, b) for a in pas for b in pas])
    fin = [-0.004, -0.002, 0.0, 0.002, 0.004]
    sx, sy, dx, dy = chercher(
        1100, (dx, dy), 3, [(sx + a, sy + b) for a in fin for b in fin])
    sx, sy, dx, dy = chercher(2800, (dx, dy), 4, [(sx, sy)])
    return sx, sy, dx, dy


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
