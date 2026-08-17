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
#  corps de chiffre couvre plusieurs choses. Il signale donc, il ne
#  corrige pas — et c'est a la planche de controle de trancher.
#
#  USAGE
#      python3 outils/kolori.py            # le releve et la comparaison
#      python3 outils/kolori.py --tabelo 14
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


def texte(f):
    t = f.read_text(encoding="utf-8")
    t = re.sub(r'%.*', '', t)
    # \textsuperscript{(12)} doit garder son numero.
    t = re.sub(r'\\textsuperscript\{(\([0-9]+\))\}', r'\1', t)
    t = re.sub(r'\\VUgras\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\(?:nl|cc)\b', ' ', t)
    t = BALISE.sub(' ', t)
    return re.sub(r'\s+', ' ', t)


# L'ADJECTIF, SON SUBSTANTIF, PUIS LE NUMERO — et rien de plus entre.
# L'ido place l'adjectif devant le nom, et le numero suit le nom : « la
# reda lanterno (25) », « nigra fumuro (75) », « blua robo (42) ». Une
# fenetre large prenait le premier numero venu, et donnait le noir aux
# nuages : « la nigra silueto salias sur la blanka nubi (67) » — le noir
# est a la silhouette, le blanc aux nuages. On n'accepte donc qu'un ou
# deux mots entre l'adjectif et le numero.
PORTEE = re.compile(r'^\s+[\w\'’-]+(?:\s+[\w\'’-]+)?\s*\((\d+)\)')


def relever():
    """Les couples (tableau, numero, couleur) que le texte ido enonce."""
    out = []
    for f in sorted((RACINE / "texto" / "io").glob("*-tabelo-*.tex")):
        tab = int(re.search(r'-(\d+)\.tex$', f.name).group(1))
        t = texte(f)
        for m in MOTS.finditer(t):
            coul = m.group(1) + "a"
            n = PORTEE.match(t[m.end():m.end() + 60])
            if not n:
                continue
            out.append({"tabelo": tab, "numero": int(n.group(1)),
                        "koloro": coul,
                        "kunteksto": re.sub(r'\s+', ' ',
                                            t[max(0, m.start() - 40):
                                              m.end() + 60]).strip()})
    return out


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
    num = json.loads((RACINE / "gravuri" / "numeri.json")
                     .read_text(encoding="utf-8"))
    obj = json.loads((RACINE / "gravuri" / "objekti.json")
                     .read_text(encoding="utf-8"))
    par_tab = {}
    for cle, v in num.items():
        par_tab.setdefault(cle[:3], []).append((cle, v))
    caches = {}
    accords = desaccords = sans = 0
    lignes = []
    for r in releve:
        tab = f"t{r['tabelo']:02d}"
        trouve = None
        for cle, v in par_tab.get(tab, []):
            b = v["numeri"].get(str(r["numero"]))
            if b:
                trouve = (cle, v, b)
                break
        if not trouve:
            sans += 1
            continue
        cle, v, b = trouve
        if cle not in caches:
            im = Image.open(RACINE / "gravuri" / "kovri" /
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
        nom = (obj.get(tab, {}).get(str(r["numero"]), {}).get("fr")
               or obj.get(tab, {}).get(str(r["numero"]), {}).get("io") or ["—"])
        lignes.append((ok, tab, r["numero"], r["koloro"], nom[0], dit))
    for ok, tab, n, c, nom, dit in sorted(lignes, key=lambda x: (x[0], x[1])):
        print(f"  {'  ' if ok else 'NON'}  {tab} ({n:>3})  "
              f"{FRANCAIS[c]:<8} {nom:<26} {dit}")
    print(f"\n  {accords} accords, {desaccords} desaccords, "
          f"{sans} sans position sur la planche "
          f"(sur {len(releve)} couleurs enoncees)")


if __name__ == "__main__":
    main(sys.argv[1:])
