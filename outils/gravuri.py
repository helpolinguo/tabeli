#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gravuri.py — prepare les tableaux muraux pour la page de lecture.

    python3 outils/gravuri.py 1 gravuri/font/page1.pdf
    python3 outils/gravuri.py --tuto          # ce que fait l'outil, en detail

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
LARGE_VIDO = 1000
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


def separer(chemin):
    """(couleur RGB, trait en alpha) d'un PDF de tableau."""
    couleur = trait = None
    pdf = pikepdf.open(chemin)
    for obj in kovri(pdf):
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


def composer(couleur, trait):
    """La couleur dessous, l'encre noire dessus selon l'alpha du trait."""
    fond = couleur.resize(trait.size, Image.LANCZOS)
    return Image.composite(Image.new("RGB", trait.size, (0, 0, 0)), fond, trait)


def poser(im, chemin, largeur, qualite):
    h = round(largeur * im.height / im.width)
    petite = im.resize((largeur, h), Image.LANCZOS)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    petite.save(chemin, format="WEBP", quality=qualite, method=6)
    return petite.size, chemin.stat().st_size


def preparer(numero, chemin):
    cle = f"t{int(numero):02d}"
    couleur, trait = separer(chemin)
    print(f"  couleur {couleur.size}   trait {trait.size}")

    # Les couches restent a part : c'est sur elles qu'on reprendra les
    # couleurs, la gravure n'ayant pas a en souffrir.
    kov = GRAVURI / "kovri"
    kov.mkdir(parents=True, exist_ok=True)
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
    tout[cle] = {"largeur": plein.width, "alteso": plein.height,
                 "vido": taille["vido"], "detalo": taille["detalo"]}
    cat.write_text(json.dumps(tout, indent=1, sort_keys=True,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    return plein


if __name__ == "__main__":
    if "--tuto" in sys.argv or len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(0)
    preparer(sys.argv[1], Path(sys.argv[2]))
