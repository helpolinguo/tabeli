#!/usr/bin/env python3
# ===================================================================
#  chifri.py — apprendre les chiffres du fac-simile, et s'en servir
#              pour PROPOSER a l'oeil ce qui manque encore.
#
#  LE PROBLEME. tools/ciphers.npz tient dix modeles de chiffres tires
#  de la couche de trait du PDF colorise : un pochoir, deux tons, des
#  contours nets. Les seize planches ayant ete reprises sur leurs
#  fac-similes, cette couche n'est plus ce qu'on regarde ; l'encre y
#  est grise, les pleins bavent, les deliés s'effacent, et le lecteur
#  de numeri.py, qui compare des formes, ne reconnait plus rien : sur
#  le tableau 14 il lisait soixante-seize numeros sur le pochoir, il
#  en lit dix sur le gris.
#
#  CE QU'ON PEUT APPRENDRE SANS RIEN DESSINER. Mille cinq cents
#  numeros sont deja places, verifies un a un, sur les planches
#  grises elles-memes. Chacun est un exemplaire ETIQUETE de la fonte
#  a reconnaitre, dans le medium meme ou il faut la reconnaitre. On
#  les decoupe — sept cent soixante et un se separent proprement en
#  chiffres, ce qui fait quatorze cents exemplaires, quatre-vingt-
#  quatre au moins par classe — on les regroupe par la forme, et les
#  centres des groupes sont les modeles.
#
#  ET CE QUE CELA VAUT, MESURE. Avec ces modeles, le lecteur relit
#  les seize planches : 442 numeros retrouves a leur place, 132 poses
#  AILLEURS, 45 numeros nouveaux. Un sur quatre est faux. C'est trop
#  pour entrer seul dans numbers.json — la regle de la maison est
#  qu'un numero sans gros plan vaut mieux qu'un gros plan sur autre
#  chose — et c'est pourquoi ce lecteur-ci NE TOURNE PAS dans la
#  chaine. Monter le seuil n'y fait rien : a 0.86 la lecture tombe a
#  246 justes pour 173 fautes, la mesure a ete faite.
#
#  D'OU SON EMPLOI : il ne decide pas, il PROPOSE. On ne lui demande
#  que les numeros ENCORE MANQUANTS — le reste est deja juge — on
#  decoupe ce qu'il montre, et l'oeil garde ou jette. Premiere
#  fournee : quarante-cinq propositions, vingt-six bonnes. Les dix-
#  neuf autres etaient soit du dessin pris pour un chiffre, soit un
#  morceau de nombre voisin : « 6 » lu dans le 36, « 5 » dans le 56,
#  « 3 » dans le 31 et dans le 13. Ce qui est garde entre dans
#  plates/manual.json, par la meme porte que ce que l'oeil trouve
#  tout seul.
#
#  USAGE
#      python3 tools/chifri.py aprendar     # refait ciphers-grey.npz
#      python3 tools/chifri.py proponar     # propose, et decoupe
#      python3 tools/chifri.py proponar t14-apar-1
#
#  La feuille de relecture sort dans plates/proponi.png, et les
#  places proposees dans plates/proponi.json — a recopier a la main
#  dans manual.json, celles qu'on garde.
# ===================================================================

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbers as N                                          # noqa: E402

RACINE = N.RACINE
MODELES = RACINE / "tools" / "ciphers-grey.npz"
PROPONI = RACINE / "plates" / "proponi.png"
PLACES = RACINE / "plates" / "proponi.json"
GROUPES = 8            # groupes par classe
RARE = 0.05            # un groupe sous ce poids ne fait pas un modele


def moissonar():
    """Decoupe, sur les planches grises, les chiffres des numeros surs."""
    cat = json.loads((RACINE / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    rec = {str(c): [] for c in range(10)}
    tot = ok = 0
    for cle in sorted(cat):
        if not N.repris(cle):
            continue
        enc = (N.enko(cle) > 128).astype(np.uint8)
        ht, la = enc.shape
        e = cat[cle]
        h = e["corpo"]
        for q, v in e["numeri"].items():
            txt = str(N.descle(q)[1])
            cx, cy = (v[0] + v[2] / 2) * la, (v[1] + v[3] / 2) * ht
            L, m = v[2] * la, 8
            x0, x1 = max(0, int(cx - L / 2 - m)), min(la, int(cx + L / 2 + m))
            y0, y1 = max(0, int(cy - h * 0.8)), min(ht, int(cy + h * 0.8))
            tot += 1
            n, lab, st, cen = cv2.connectedComponentsWithStats(
                enc[y0:y1, x0:x1], 8)
            # UN CHIFFRE, C'EST UNE COMPOSANTE DE LA TAILLE D'UN CHIFFRE.
            # On n'apprend que des nombres qui se separent d'eux-memes en
            # autant de morceaux qu'ils ont de chiffres, tous poses sur la
            # meme ligne de base : c'est la seule facon d'etre sur de ce
            # qu'on etiquette.
            comp = [i for i in range(1, n)
                    if 0.60 * h <= st[i, 3] <= 1.5 * h
                    and 0.10 * h <= st[i, 2] <= 1.15 * h
                    and st[i, 4] >= 0.15 * st[i, 2] * st[i, 3]]
            if len(comp) != len(txt):
                continue
            comp.sort(key=lambda i: st[i, 0])
            ym = float(np.median([cen[i][1] for i in comp]))
            if any(abs(cen[i][1] - ym) > 0.4 * h for i in comp):
                continue
            for c, i in zip(txt, comp):
                x, y, w, hh, _ = st[i]
                rec[c].append(N.vignette(
                    (lab[y:y + hh, x:x + w] == i).astype(np.uint8) * 255))
            ok += 1
    print(f"  {ok}/{tot} nombres se sont separes proprement")
    return rec


def aprendar():
    """Regroupe la moisson : les centres des groupes sont les modeles."""
    rec = moissonar()
    out = {}
    for c in "0123456789":
        v = np.stack(rec[c]).astype(np.float32)
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        k = min(GROUPES, len(v))
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 1e-4)
        _, lab, cen = cv2.kmeans(v, k, None, crit, 8, cv2.KMEANS_PP_CENTERS)
        lab = lab.ravel()
        gard = [i for i in range(k) if (lab == i).sum() >= RARE * len(v)]
        out[c] = np.stack([cen[i].reshape(N.H, N.W) for i in gard])
        print(f"  {c} : {len(v):4d} exemplaires, {len(gard)} modeles "
              f"{[int((lab == i).sum()) for i in gard]}")
    np.savez_compressed(MODELES, **out)
    print(f"  ecrit dans {MODELES}")


def charger():
    """Met les modeles gris a la place de ceux du pochoir."""
    d = np.load(MODELES)
    noms = [c for c in d.files for _ in range(len(d[c]))]
    pile = np.stack([m for c in d.files for m in d[c]]).reshape(len(noms), -1)
    N.NOMS = noms
    N.PILE = pile / np.linalg.norm(pile, axis=1, keepdims=True)
    N.GRIS = True


def proponar(cles=None):
    """Relit les planches grises, mais ne rend QUE ce qui manque."""
    charger()
    cat = json.loads((RACINE / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    prop = {}
    for cle in sorted(cat):
        if not N.repris(cle) or (cles and cle not in cles):
            continue
        a = N.enko(cle)
        ht, la = a.shape
        haut = cat[cle]["corpo"]
        att = N.attendus(cle)
        if not att:
            continue
        connus = set(cat[cle]["numeri"])
        manque = {N.kl(sc, n) for sc, ns in att.items() for n in ns} - connus
        out = {}
        for sc, forme in (N.ceni(cle) or [("", ["rekt", 0., 0., 1., 1.])]):
            if sc not in att:
                continue
            fx0, fy0, fx1, fy1 = N.boite(forme)
            x0, y0 = int(fx0 * la), int(fy0 * ht)
            x1 = min(la, int(fx1 * la) + 1)
            y1 = min(ht, int(fy1 * ht) + 1)
            for n, (b, fo) in N.lire(a[y0:y1, x0:x1], att[sc], haut).items():
                q = N.kl(sc, n)
                if q in manque:
                    out[q] = [int(b[0] + x0), int(b[1] + y0),
                              int(b[2]), int(b[3]), round(float(fo), 3)]
        if out:
            prop[cle] = out
            print(f"  {cle} : {len(out)} propositions sur "
                  f"{len(manque)} manquants")
    PLACES.write_text(json.dumps(prop, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    feuille(prop, cat)
    print(f"  {sum(len(v) for v in prop.values())} propositions — "
          f"a relire dans {PROPONI}")


def feuille(prop, cat, cols=6, cote=330, pied=66, rayon=62):
    """La feuille de relecture : le decoupe, le nom de l'objet, la place."""
    obj = json.loads((RACINE / "plates" / "objects.json")
                     .read_text(encoding="utf-8"))
    def fonte(f, t):
        try:
            return ImageFont.truetype(
                f"/usr/share/fonts/truetype/dejavu/DejaVuSans{f}.ttf", t)
        except Exception:
            return ImageFont.load_default()
    F, G = fonte("-Bold", 26), fonte("", 19)
    cel = []
    for cle in sorted(prop):
        im = N.planche(cle)
        for q, (x, y, w, h, fo) in sorted(prop[cle].items()):
            cx, cy = x + w / 2, y + h / 2
            t = im.crop((int(cx - rayon), int(cy - rayon),
                         int(cx + rayon), int(cy + rayon))).convert("RGB")
            c = Image.new("RGB", (cote, cote + pied), (255, 255, 255))
            c.paste(t.resize((cote, cote), Image.LANCZOS), (0, 0))
            g = ImageDraw.Draw(c)
            Z = cote / (2 * rayon)
            g.rectangle([cote / 2 - w * Z / 2 - 3, cote / 2 - h * Z / 2 - 3,
                         cote / 2 + w * Z / 2 + 3, cote / 2 + h * Z / 2 + 3],
                        outline=(255, 60, 0), width=3)
            n = N.descle(q)[1]
            nom = (obj.get(cle[:3], {}).get(str(n), {}).get("fr") or ["?"])[0]
            g.text((6, cote + 3), f"{cle[:3]} {q}  ({fo})",
                   fill=(0, 0, 0), font=F)
            g.text((6, cote + 34), nom[:34], fill=(80, 80, 80), font=G)
            cel.append(c)
    if not cel:
        return
    lig = [cel[i:i + cols] for i in range(0, len(cel), cols)]
    out = Image.new("RGB", (cols * cote, len(lig) * (cote + pied)),
                    (255, 255, 255))
    for j, l in enumerate(lig):
        for i, c in enumerate(l):
            out.paste(c, (i * cote, j * (cote + pied)))
    out.save(PROPONI)


def main(args):
    if not args or args[0] == "aprendar":
        aprendar()
    elif args[0] == "proponar":
        proponar(args[1:] or None)
    else:
        raise SystemExit(__doc__ or "aprendar | proponar")


if __name__ == "__main__":
    main(sys.argv[1:])
