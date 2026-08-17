#!/usr/bin/env python3
# ===================================================================
#  manuali.py — les numeros repares a l'oeil, poses au pixel pres.
#
#  Le lecteur automatique plafonne : la reserve de blanc qui porte le
#  chiffre se referme des que la gravure est dense, et le chiffre se
#  perd alors dans les hachures. Le reste se releve donc a la main —
#  mais a la main SEULEMENT POUR CE QUE LA MACHINE NE SAIT PAS FAIRE.
#
#  LE PARTAGE DU TRAVAIL. L'oeil lit la planche par tuiles, sur une
#  grille etiquetee, et dicte « 74 en H4 » : le numero, et sa case. La
#  machine reprend la main et cherche CE nombre-la dans cette case et
#  ses voisines, par le meme filtre adapte qui sert partout ailleurs.
#  Ce filtre, incapable de choisir entre soixante-dix-sept nombres sur
#  une planche entiere, ne se trompe plus quand on lui en donne UN
#  SEUL dans neuf cases : il ne lui reste qu'a trouver ou il est.
#
#  On gagne ainsi la precision sans la peine : une case fait sept
#  hauteurs de chiffre, et dicter une position au pixel pres serait
#  interminable et faux.
#
#  gravuri/manuali.json se tient a la main, comme verdikti.json ;
#  numeri.py le lit et ajoute ce qu'il nomme.
#
#  USAGE
#      python3 outils/manuali.py tuiler t01-apar-1   # fait les tuiles
#      python3 outils/manuali.py poser t01-apar-1 10=C3 11=B3 74=H4
#      python3 outils/manuali.py planche t01-apar-1  # le controle
# ===================================================================

import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numeri as N                                          # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RACINE = N.RACINE
TUILES = RACINE / "gravuri" / "tuili"
LETTRES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PAS = 290
NX = NY = 2
MARGE = 0.02


def police(taille):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", taille)
    except Exception:
        return ImageFont.load_default()


def cadres(cle):
    """Les quatre tuiles d'une planche : (x0, y0) de chacune."""
    im = Image.open(N.KOVRI / f"{cle}-trako.png")
    W, H = im.size
    out = []
    for iy in range(NY):
        for ix in range(NX):
            x0 = max(0, round(W * ix / NX - W * MARGE))
            y0 = max(0, round(H * iy / NY - H * MARGE))
            x1 = min(W, round(W * (ix + 1) / NX + W * MARGE))
            y1 = min(H, round(H * (iy + 1) / NY + H * MARGE))
            out.append((x0, y0, x1, y1))
    return im, out


def tuiler(cle):
    """Ecrit les tuiles, les numeros deja connus cercles."""
    TUILES.mkdir(parents=True, exist_ok=True)
    im, cads = cadres(cle)
    W, H = im.size
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    connus = {int(n): (v[0] * W + v[2] * W / 2, v[1] * H + v[3] * H / 2)
              for n, v in d["numeri"].items()}
    F = police(34)
    for k, (x0, y0, x1, y1) in enumerate(cads):
        t = im.crop((x0, y0, x1, y1)).convert("RGB")
        g = ImageDraw.Draw(t)
        # CE QUI EST DEJA TROUVE EST CERCLE : l'oeil n'a plus qu'a lire
        # ce qui ne l'est pas, et ne relit pas deux fois la meme chose.
        for n, (cx, cy) in connus.items():
            if x0 <= cx < x1 and y0 <= cy < y1:
                g.ellipse([cx - x0 - 34, cy - y0 - 34,
                           cx - x0 + 34, cy - y0 + 34],
                          outline=(255, 110, 0), width=6)
        for gx in range(0, t.width, PAS):
            g.line([gx, 0, gx, t.height], fill=(0, 150, 255), width=2)
        for gy in range(0, t.height, PAS):
            g.line([0, gy, t.width, gy], fill=(0, 150, 255), width=2)
        # LES LIGNES PORTENT LA COORDONNEE DE LA PLANCHE, non un nom de
        # case. On a d'abord dicte « 74 en H4 » et laisse la machine
        # chercher dans la case : elle n'y arrive pas. Sur cette
        # planche, le « 7 » de 72 est a demi cache par un chapeau, celui
        # de 77 jouxte un 75 — et le filtre adapte, deja incapable de
        # choisir entre deux nombres de meme longueur, se trompe meme
        # dans une demi-case. L'oeil, lui, lit le nombre ET sa place ;
        # autant qu'il dicte les deux.
        for gx in range(0, t.width, PAS):
            e = f"{x0 + gx}"
            g.rectangle([gx + 3, 3, gx + 26 + 17 * len(e), 46], fill=(0, 0, 0))
            g.text((gx + 8, 2), e, fill=(0, 190, 255), font=F)
        for gy in range(PAS, t.height, PAS):
            e = f"{y0 + gy}"
            g.rectangle([3, gy + 3, 26 + 17 * len(e), gy + 46], fill=(0, 0, 0))
            g.text((8, gy + 2), e, fill=(0, 190, 255), font=F)
        t.save(TUILES / f"{cle}-{k}.png")
    att = N.attendus(cle)
    manque = sorted(att - {int(n) for n in d["numeri"]})
    print(f"  {cle} : {len(cads)} tuiles, {len(manque)} numeros manquants")
    print(f"  {manque}")


def case(cle, tuile, ref):
    """« H4 » sur la tuile k -> (x, y) au centre de la case, en planche."""
    m = re.fullmatch(r'([A-Z])(\d+)', ref.upper())
    if not m:
        raise SystemExit(f"case illisible : {ref}")
    _, cads = cadres(cle)
    x0, y0, _, _ = cads[tuile]
    cx = x0 + LETTRES.index(m.group(1)) * PAS + PAS / 2
    cy = y0 + int(m.group(2)) * PAS + PAS / 2
    return cx, cy


def gabarit(n, corps, marge=12, ecart=0.13):
    parts = []
    for c in str(n):
        m = N._base()[c]
        parts.append(cv2.resize(m, (max(1, round(m.shape[1] * corps / N.H)),
                                    corps), interpolation=cv2.INTER_AREA))
    e = max(1, round(ecart * corps))
    L = sum(p.shape[1] for p in parts) + e * (len(parts) - 1)
    g = np.zeros((corps, L), np.float32)
    x = 0
    for p in parts:
        g[:, x:x + p.shape[1]] = p
        x += p.shape[1] + e
    q = np.zeros((corps + 2 * marge, L + 2 * marge), np.float32)
    q[marge:marge + corps, marge:marge + L] = g
    pos = (q >= 0.5).astype(np.float32)
    neg = 1.0 - pos
    return pos / pos.sum() - neg / neg.sum(), marge, L


# LA FENETRE DE RECHERCHE RESTE ETROITE. A une case et demie, le filtre
# allait chercher le numero VOISIN : « 72 » dicte en I5 se posait sur le
# 71 d'a cote, « 73 » sur le 75. Une demi-case suffit des lors que
# l'oeil a bien lu la grille, et elle interdit ces glissements.
def poser(cle, refs, rayon=0.62):
    """Trouve chaque nombre dicte dans sa case et ses voisines."""
    enc = (np.asarray(Image.open(N.KOVRI / f"{cle}-trako.png"))
           > 128).astype(np.float32)
    HT, LA = enc.shape
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    corps = d["corpo"]
    f = RACINE / "gravuri" / "manuali.json"
    tout = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    par = tout.setdefault(cle, {})
    occupe = [(round(v[0] * LA), round(v[1] * HT))
              for v in d["numeri"].values()]
    occupe += [(round(v[0] * LA), round(v[1] * HT)) for v in par.values()]
    for n, tuile, ref in refs:
        if "," in ref:
            # L'oeil a lu la place sur la grille : on la prend telle
            # quelle, sans rien chercher. C'est le cas le plus sur.
            px, py = (int(v) for v in ref.split(","))
            T, M, L = gabarit(n, corps)
            par[str(n)] = [round((px - L / 2) / LA, 6),
                           round((py - corps / 2) / HT, 6),
                           round(L / LA, 6), round(corps / HT, 6), 1.0]
            print(f"  {n:>4} pose a l'oeil en ({px}, {py})")
            continue
        cx, cy = case(cle, tuile, ref)
        T, M, L = gabarit(n, corps)
        R = round(rayon * PAS)
        x0, y0 = int(cx) - R, int(cy) - R
        x1, y1 = int(cx) + R + T.shape[1], int(cy) + R + T.shape[0]
        if x0 < 0 or y0 < 0 or x1 > LA or y1 > HT:
            print(f"  {n} en {ref} : hors planche")
            continue
        r = cv2.matchTemplate(enc[y0:y1, x0:x1], T, cv2.TM_CCORR)
        # LES PLACES DEJA PRISES SONT INTERDITES. « 77 » dicte en G5 se
        # posait sur le 75 d'a cote — meme premier chiffre, cent trente
        # points plus loin — et « 72 » sur le 71. Or on sait ou sont les
        # numeros deja trouves : on efface ces places de la carte, et le
        # filtre doit chercher ailleurs.
        for b2 in occupe:
            ox, oy = b2[0] - x0 - M, b2[1] - y0 - M
            if -corps < ox < r.shape[1] + corps and \
               -corps < oy < r.shape[0] + corps:
                a0 = max(0, int(oy - 0.7 * corps))
                a1 = min(r.shape[0], int(oy + 0.7 * corps) + 1)
                b0 = max(0, int(ox - 0.7 * corps))
                b1 = min(r.shape[1], int(ox + 0.7 * corps) + 1)
                if a1 > a0 and b1 > b0:
                    r[a0:a1, b0:b1] = -9
        _, mx, _, loc = cv2.minMaxLoc(r)
        px, py = x0 + loc[0] + M, y0 + loc[1] + M
        par[str(n)] = [round(px / LA, 6), round(py / HT, 6),
                       round(L / LA, 6), round(corps / HT, 6), round(mx, 3)]
        print(f"  {n:>4} en {ref} (tuile {tuile}) -> "
              f"({px}, {py})  score {mx:.3f}")
    f.write_text(json.dumps(tout, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")


def planche(cle):
    """La planche de controle des numeros poses a la main."""
    f = RACINE / "gravuri" / "manuali.json"
    if not f.exists():
        return
    par = json.loads(f.read_text(encoding="utf-8")).get(cle, {})
    if not par:
        print(f"  {cle} : rien de pose a la main")
        return
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    LA, HT, corps = d["largeur"], d["alteso"], d["corpo"]
    trouves = {int(n): ((round(v[0] * LA), round(v[1] * HT),
                         round(v[2] * LA), round(v[3] * HT)), v[4])
               for n, v in par.items()}
    N.KONTROLO.mkdir(parents=True, exist_ok=True)
    n = N.controle(N.KOVRI / f"{cle}-trako.png", trouves,
                   N.KONTROLO / f"{cle}-manuali.png", corps,
                   large=1.5, cols=10)
    print(f"  {cle} : {n} decoupes dans "
          f"{N.KONTROLO / (cle + '-manuali.png')}")


def main(args):
    if not args:
        raise SystemExit(__doc__)
    verbe, cle = args[0], args[1]
    if verbe == "tuiler":
        tuiler(cle)
    elif verbe == "planche":
        planche(cle)
    elif verbe == "poser":
        refs = []
        tuile = 0
        for a in args[2:]:
            if a.startswith("t="):
                tuile = int(a[2:])
                continue
            n, ref = a.split("=")
            refs.append((int(n), tuile, ref))
        poser(cle, refs)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
