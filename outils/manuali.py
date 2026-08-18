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
#  grille dont les lignes portent la coordonnee, et dicte « 74 en
#  2286,1326 » : le numero, et sa place. Ce qui est deja trouve est
#  cercle sur la tuile, de sorte qu'on ne relit jamais deux fois.
#
#  ON A D'ABORD ESSAYE DE N'EN DICTER QUE LA MOITIE — la case, l'outil
#  cherchant le nombre dedans par filtre adapte. Cela ne marche pas :
#  « 72 » se posait sur le 71 d'a cote, « 77 » sur le 75, et resserrer
#  la fenetre a une demi-case n'y changeait rien. Sur le tableau 1, le
#  « 7 » de 72 est a demi cache derriere un chapeau, et le filtre ne
#  reconnait pas un chiffre ampute meme quand on lui dit lequel
#  chercher et ou. L'oeil, lui, lit le nombre ET sa place : autant
#  qu'il dicte les deux.
#
#  gravuri/manuali.json se tient a la main, comme verdikti.json ;
#  numeri.py le lit et ajoute ce qu'il nomme.
#
#  USAGE
#      python3 outils/manuali.py tuiler t01-apar-1   # fait les tuiles
#      python3 outils/manuali.py zono   t01-apar-1   # ce qui manque, de pres
#      python3 outils/manuali.py poser t01-apar-1 10=615,868 74=2286,1326
#      python3 outils/manuali.py planche t01-apar-1  # le controle
# ===================================================================

import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

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


def cadres(cle, n=NX):
    """Le decoupage d'une planche en n x n : (x0, y0, x1, y1) de chacune."""
    im = Image.open(N.KOVRI / f"{cle}-trako.png")
    W, H = im.size
    out = []
    for iy in range(n):
        for ix in range(n):
            x0 = max(0, round(W * ix / n - W * MARGE))
            y0 = max(0, round(H * iy / n - H * MARGE))
            x1 = min(W, round(W * (ix + 1) / n + W * MARGE))
            y1 = min(H, round(H * (iy + 1) / n + H * MARGE))
            out.append((x0, y0, x1, y1))
    return im, out


def restant(cle, connus):
    """Ce que le texte appelle et que personne n'a encore trouve."""
    att = {N.kl(sc, n) for sc, ns in N.attendus(cle).items() for n in ns}
    return sorted(att - set(connus), key=N.descle)


def tuiler(cle, n=NX, z=1.0):
    """Ecrit les tuiles, les numeros deja connus cercles."""
    TUILES.mkdir(parents=True, exist_ok=True)
    im, cads = cadres(cle, n)
    W, H = im.size
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    connus = {n: (v[0] * W + v[2] * W / 2, v[1] * H + v[3] * H / 2)
              for n, v in d["numeri"].items()}
    # Ce qu'on vient de poser a la main compte aussi, sans quoi il
    # faudrait relancer tout le lecteur entre deux tuiles pour cesser de
    # relire ce qu'on a deja releve.
    fm = RACINE / "gravuri" / "manuali.json"
    if fm.exists():
        for n, v in json.loads(fm.read_text(encoding="utf-8")) \
                .get(cle, {}).items():
            connus[n] = (v[0] * W + v[2] * W / 2, v[1] * H + v[3] * H / 2)
    F = police(34)
    for k, (x0, y0, x1, y1) in enumerate(cads):
        # LE TRAIT RETOURNE. La couche porte l'encre en blanc sur fond
        # noir ; l'oeil y perd la moitie de ce qu'il saurait lire. On la
        # remet dans son sens, et la tuile redevient une gravure.
        t = ImageOps.invert(im.crop((x0, y0, x1, y1)).convert("L")) \
            .convert("RGB")
        if z != 1.0:
            t = t.resize((round(t.width * z), round(t.height * z)),
                         Image.LANCZOS)
        g = ImageDraw.Draw(t)
        # CE QUI EST DEJA TROUVE EST CERCLE : l'oeil n'a plus qu'a lire
        # ce qui ne l'est pas, et ne relit pas deux fois la meme chose.
        for nu, (cx, cy) in connus.items():
            if x0 <= cx < x1 and y0 <= cy < y1:
                a, b = (cx - x0) * z, (cy - y0) * z
                g.ellipse([a - 34 * z, b - 34 * z, a + 34 * z, b + 34 * z],
                          outline=(255, 60, 0), width=6)
        for gx in range(0, x1 - x0, PAS):
            g.line([gx * z, 0, gx * z, t.height], fill=(0, 130, 255), width=2)
        for gy in range(0, y1 - y0, PAS):
            g.line([0, gy * z, t.width, gy * z], fill=(0, 130, 255), width=2)
        # LES LIGNES PORTENT LA COORDONNEE DE LA PLANCHE, non un nom de
        # case. On a d'abord dicte « 74 en H4 » et laisse la machine
        # chercher dans la case : elle n'y arrive pas. Sur cette
        # planche, le « 7 » de 72 est a demi cache par un chapeau, celui
        # de 77 jouxte un 75 — et le filtre adapte, deja incapable de
        # choisir entre deux nombres de meme longueur, se trompe meme
        # dans une demi-case. L'oeil, lui, lit le nombre ET sa place ;
        # autant qu'il dicte les deux.
        for gx in range(0, x1 - x0, PAS):
            e = f"{x0 + gx}"
            g.rectangle([gx * z + 3, 3, gx * z + 26 + 17 * len(e), 46],
                        fill=(0, 0, 0))
            g.text((gx * z + 8, 2), e, fill=(0, 190, 255), font=F)
        for gy in range(PAS, y1 - y0, PAS):
            e = f"{y0 + gy}"
            g.rectangle([3, gy * z + 3, 26 + 17 * len(e), gy * z + 46],
                        fill=(0, 0, 0))
            g.text((8, gy * z + 2), e, fill=(0, 190, 255), font=F)
        t.save(TUILES / f"{cle}-{k}.png")
    manque = restant(cle, connus)
    print(f"  {cle} : {len(cads)} tuiles, {len(manque)} numeros manquants")
    print(f"  {manque}")


# LES ZONES. Les derniers numeros d'une planche dense sont ceux que
# l'oeil n'a pas su voir sur une tuile de demi-planche : a cette
# reduction le chiffre ne fait plus que vingt-sept points. On regarde
# donc de plus pres, mais seulement OU IL FAUT. Le numero n se trouve,
# neuf fois sur dix, a moins de trois cent cinquante points du milieu
# du segment qui joint n-1 a n+1 — mesure faite sur les trente-huit
# numeros du tableau 14 dont les deux voisins sont connus. On decoupe
# donc autour de ce milieu, et les fenetres qui se recouvrent se
# fondent en une seule, de sorte qu'une image serve souvent a plusieurs.
ZONE_L, ZONE_H = 950, 680
ZONE_Z = 2.1                     # le chiffre y fait quatre-vingts points


def zono(cle, rayon=None):
    """Decoupe, autour de la place presumee, ce qui manque encore."""
    TUILES.mkdir(parents=True, exist_ok=True)
    im = Image.open(N.KOVRI / f"{cle}-trako.png")
    W, H = im.size
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    connus = {n: ((v[0] + v[2] / 2) * W, (v[1] + v[3] / 2) * H)
              for n, v in d["numeri"].items()}
    fm = RACINE / "gravuri" / "manuali.json"
    if fm.exists():
        for n, v in json.loads(fm.read_text(encoding="utf-8")) \
                .get(cle, {}).items():
            connus[n] = ((v[0] + v[2] / 2) * W, (v[1] + v[3] / 2) * H)
    manque = restant(cle, connus)
    if not manque:
        print(f"  {cle} : rien ne manque")
        return
    # La place presumee : le milieu des deux voisins connus les plus
    # proches en rang, ou le voisin unique quand il n'y en a qu'un.
    def presume(k):
        sc, n = N.descle(k)
        frat = {N.descle(q)[1]: v for q, v in connus.items()
                if N.descle(q)[0] == sc}
        bas = max((k for k in frat if k < n), default=None)
        haut = min((k for k in frat if k > n), default=None)
        if bas is not None and haut is not None:
            return ((frat[bas][0] + frat[haut][0]) / 2,
                    (frat[bas][1] + frat[haut][1]) / 2)
        if bas is not None:
            return frat[bas]
        if haut is not None:
            return frat[haut]
        return (W / 2, H / 2)

    zones = []                                  # (x0, y0, [numeros])
    for n in manque:
        cx, cy = presume(n)
        for z in zones:
            if abs(z[0] + ZONE_L / 2 - cx) < ZONE_L * 0.35 and \
               abs(z[1] + ZONE_H / 2 - cy) < ZONE_H * 0.35:
                z[2].append(n)
                break
        else:
            x0 = min(max(0, round(cx - ZONE_L / 2)), max(0, W - ZONE_L))
            y0 = min(max(0, round(cy - ZONE_H / 2)), max(0, H - ZONE_H))
            zones.append([x0, y0, [n]])
    F = police(30)
    for k, (x0, y0, ns) in enumerate(zones):
        x1, y1 = min(W, x0 + ZONE_L), min(H, y0 + ZONE_H)
        # LE TRAIT EN NOIR SUR BLANC. La couche de trait porte l'encre en
        # blanc sur fond noir ; a l'oeil, cela se lit mal — on la retourne,
        # et la planche redevient ce qu'elle est, une gravure.
        t = ImageOps.invert(im.crop((x0, y0, x1, y1)).convert("L")) \
            .convert("RGB")
        t = t.resize((round(t.width * ZONE_Z), round(t.height * ZONE_Z)),
                     Image.LANCZOS)
        g = ImageDraw.Draw(t)
        Z = ZONE_Z
        for n, (cx, cy) in connus.items():
            if x0 <= cx < x1 and y0 <= cy < y1:
                a, b = (cx - x0) * Z, (cy - y0) * Z
                g.ellipse([a - 34 * Z, b - 34 * Z, a + 34 * Z, b + 34 * Z],
                          outline=(255, 60, 0), width=6)
        pas = 100
        dx = (-x0) % pas
        dy = (-y0) % pas
        for gx in range(dx, x1 - x0, pas):
            fort = (x0 + gx) % 500 == 0
            g.line([gx * Z, 0, gx * Z, t.height],
                   fill=(0, 130, 255) if fort else (120, 190, 235),
                   width=3 if fort else 1)
            if fort:
                e = f"{x0 + gx}"
                g.rectangle([gx * Z + 3, 3, gx * Z + 22 + 15 * len(e), 40],
                            fill=(0, 0, 0))
                g.text((gx * Z + 7, 2), e, fill=(0, 190, 255), font=F)
        for gy in range(dy, y1 - y0, pas):
            fort = (y0 + gy) % 500 == 0
            g.line([0, gy * Z, t.width, gy * Z],
                   fill=(0, 130, 255) if fort else (120, 190, 235),
                   width=3 if fort else 1)
            if fort:
                e = f"{y0 + gy}"
                g.rectangle([3, gy * Z + 3, 22 + 15 * len(e), gy * Z + 40],
                            fill=(0, 0, 0))
                g.text((7, gy * Z + 2), e, fill=(0, 190, 255), font=F)
        t.save(TUILES / f"{cle}-z{k}.png")
        print(f"  z{k} ({x0},{y0}) : {ns}")
    print(f"  {cle} : {len(zones)} zones, {len(manque)} numeros manquants")


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
    """Trouve chaque nombre dicte dans sa case et ses voisines.

    Sur une planche a plusieurs scenes le numero se dicte avec la sienne
    — « c3:12=1840,2210 » —, sans quoi on ne saurait pas de quel douze
    il s'agit.
    """
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
    for k, tuile, ref in refs:
        n = N.descle(k)[1]
        if ref.count(",") == 2:
            # L'oeil a vu le nombre, mais l'a montre du doigt : on cherche
            # dans le rayon dicte, et le filtre pose le cadre au chiffre
            # pres. Rayon court -- c'est ce qui interdit les glissements.
            cx, cy, ray = (int(v) for v in ref.split(","))
            T, M, L = gabarit(n, corps)
            x0, y0 = int(cx - L / 2) - ray, int(cy - corps / 2) - ray
            x1 = int(cx - L / 2) + ray + T.shape[1]
            y1 = int(cy - corps / 2) + ray + T.shape[0]
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(LA, x1), min(HT, y1)
            r = cv2.matchTemplate(enc[y0:y1, x0:x1], T, cv2.TM_CCORR)
            _, mx, _, loc = cv2.minMaxLoc(r)
            px, py = x0 + loc[0] + M, y0 + loc[1] + M
            par[k] = [round(px / LA, 6), round(py / HT, 6),
                      round(L / LA, 6), round(corps / HT, 6), 1.0]
            print(f"  {k:>7} cale sur ({px}, {py})  score {mx:.3f}")
            continue
        if "," in ref:
            # L'oeil a lu la place sur la grille : on la prend telle
            # quelle, sans rien chercher. C'est le cas le plus sur.
            px, py = (int(v) for v in ref.split(","))
            T, M, L = gabarit(n, corps)
            par[k] = [round((px - L / 2) / LA, 6),
                      round((py - corps / 2) / HT, 6),
                      round(L / LA, 6), round(corps / HT, 6), 1.0]
            print(f"  {k:>7} pose a l'oeil en ({px}, {py})")
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
        par[k] = [round(px / LA, 6), round(py / HT, 6),
                  round(L / LA, 6), round(corps / HT, 6), round(mx, 3)]
        print(f"  {k:>7} en {ref} (tuile {tuile}) -> "
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
    trouves = {n: ((round(v[0] * LA), round(v[1] * HT),
                    round(v[2] * LA), round(v[3] * HT)), v[4])
               for n, v in par.items()}
    N.KONTROLO.mkdir(parents=True, exist_ok=True)
    n = N.controle(N.KOVRI / f"{cle}-trako.png", trouves,
                   N.KONTROLO / f"{cle}-manuali.png", corps,
                   large=1.5, cols=10)
    print(f"  {cle} : {n} decoupes dans "
          f"{N.KONTROLO / (cle + '-manuali.png')}")


# LA RELECTURE DES LECTURES AUTOMATIQUES. Le score ne dit pas tout : le
# filtre qui cherche « 14 » le trouve dans le « 144 » d'a cote, et rien
# ne l'en avertit -- le morceau est parfaitement forme. Il faut donc
# passer les lectures sous l'oeil, une planche a la fois, chacune
# decoupee large et portant le nom que le fac-simile donne a l'objet.
# Ce qui a ete pose a la main n'y figure pas : c'est deja juge.
def revizo(cle, page=0, par=24, cols=6, Z=3):
    """Les lectures automatiques d'une planche, a relire une a une."""
    d = json.loads((RACINE / "gravuri" / "numeri.json")
                   .read_text(encoding="utf-8"))[cle]
    LA, HT, corps = d["largeur"], d["alteso"], d["corpo"]
    fm = RACINE / "gravuri" / "manuali.json"
    mains = (json.loads(fm.read_text(encoding="utf-8")).get(cle, {})
             if fm.exists() else {})
    noms = N.objekti(cle)
    tout = [(n, v) for n, v in d["numeri"].items() if n not in mains]
    tout.sort(key=lambda q: N.descle(q[0]))
    lot = tout[page * par:(page + 1) * par]
    if not lot:
        print(f"  {cle} : plus rien a relire")
        return 0
    im = ImageOps.invert(Image.open(N.KOVRI / f"{cle}-trako.png")
                         .convert("L"))
    w, h = round(corps * 4.4), round(corps * 3.0)
    F = police(20)
    F2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    lig = (len(lot) + cols - 1) // cols
    pl = Image.new("RGB", (cols * (w * Z + 10) + 10,
                           lig * (h * Z + 52) + 10), (255, 255, 255))
    g = ImageDraw.Draw(pl)
    for i, (n, v) in enumerate(lot):
        cx, cy = (v[0] + v[2] / 2) * LA, (v[1] + v[3] / 2) * HT
        c = im.crop((round(cx - w / 2), round(cy - h / 2),
                     round(cx + w / 2), round(cy + h / 2))).convert("RGB")
        c = c.resize((w * Z, h * Z), Image.LANCZOS)
        X, Y = 10 + (i % cols) * (w * Z + 10), 10 + (i // cols) * (h * Z + 52)
        pl.paste(c, (X, Y))
        g.rectangle([X, Y, X + w * Z, Y + h * Z], outline=(200, 0, 0))
        nm = noms.get(str(n), {})
        nom = (nm.get("fr") or nm.get("io") or [""])[0]
        g.text((X + 2, Y + h * Z + 3), f"{n} — {nom[:24]}",
               fill=(0, 0, 0), font=F)
        g.text((X + 2, Y + h * Z + 26),
               f"{v[4]:.2f}   {round(cx)},{round(cy)}",
               fill=(90, 90, 90), font=F2)
    N.KONTROLO.mkdir(parents=True, exist_ok=True)
    dest = N.KONTROLO / f"{cle}-revizo{page}.png"
    pl.save(dest)
    print(f"  {cle} : page {page}, {len(lot)} lectures sur {len(tout)} "
          f"-> {dest}")
    return len(tout)


def main(args):
    if not args:
        raise SystemExit(__doc__)
    verbe, cle = args[0], args[1]
    if verbe == "tuiler":
        tuiler(cle, int(args[2]) if len(args) > 2 else NX,
               float(args[3]) if len(args) > 3 else 1.0)
    elif verbe == "zono":
        zono(cle)
    elif verbe == "revizo":
        revizo(cle, int(args[2]) if len(args) > 2 else 0)
    elif verbe == "planche":
        planche(cle)
    elif verbe == "poser":
        refs = []
        tuile = 0
        for a in args[2:]:
            if a.startswith("t="):
                tuile = int(a[2:])
                continue
            k, ref = a.split("=")
            refs.append((k, tuile, ref))
        poser(cle, refs)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
