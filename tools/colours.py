#!/usr/bin/env python3
# ===================================================================
#  colours.py — what the text says of colour, and what the plate shows
#  of it.
#
#  The plates were coloured by a machine that had not read the Booklets.
#  It therefore painted plausibly, and the text contradicts it here and
#  there: "la reda lanterno (25)" of table 14 must be red, "la blua robo
#  (42)" of table 4 blue, "nigra fumuro (75)" of table 11 black. This
#  tool surveys every colour the two volumes attach to a numbered object,
#  goes to see what the colour layer carries at that place, and says
#  where the two agree.
#
#  WHERE TO LOOK. The number is not ON the object: it is laid beside it,
#  in a reserve of white. To take the colour at the number would be to
#  take the colour of the reserve. We therefore read a RING around the
#  number — one to three figure-widths — and discard within it what is
#  nearly white (the reserve, the paper) and nearly black (the engraved
#  line, which is not colour but ink).
#
#  WHAT THE TOOL DOES NOT SAY. It does not know whether the colour found
#  belongs to the object named or to its neighbour: a ring of three
#  figure-widths covers several things. Nor does it know that the "(65)"
#  of table 13 is laid on the canopy of a hotel and names a liner out at
#  sea. It reports, therefore; it does not correct.
#
#  WHAT THE EYE HAS DECIDED lives in plates/colours.json, under "vidita",
#  and the tool repeats it under each line: "planche" when the painting
#  contradicts the booklet and will have to be redone, "mesure" when the
#  ring was wrong, "akordo" when the two say the same thing. Of the
#  twenty-five colours the booklets attach to a numbered object, eleven
#  call for redoing.
#
#  USAGE
#      python3 tools/colours.py            # the survey and the comparison
#      python3 tools/colours.py --tabelo 14
# ===================================================================

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RACINE = Path(__file__).resolve().parent.parent

# THE NAMED COLOURS, and the tone asked of them. The tone is given in
# degrees on the hue wheel, with the expected saturation and lightness;
# "blanka" and "nigra" have no hue and are judged on lightness alone.
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

# THE ADJECTIVE INFLECTS — "reda", "rede", "redi" — and it must be
# taken in LOWER CASE: "Blanko" is a person's name (Jacques's father, in
# table 5), "Blank Urso" the sign of an inn.
ADJ = re.compile(
    r'(?<![A-Za-z])(' + '|'.join(sorted(TONS, key=len, reverse=True))
    .replace('a|', '|') + r')(?=\b)')
MOTS = re.compile(r'(?<![\w-])(' +
                  '|'.join(k[:-1] for k in sorted(TONS, key=len, reverse=True)) +
                  r')(?:a|e|i)(?![\w-])')
NUM = re.compile(r'\((\d+)\)')
BALISE = re.compile(r'\\[A-Za-z]+\*?(?:\{[^{}]*\})?|[{}]|%.*')


def texte(t):
    t = re.sub(r'%.*', '', t)
    # \textsuperscript{(12)} must keep its number.
    t = re.sub(r'\\textsuperscript\{(\([0-9]+\))\}', r'\1', t)
    t = re.sub(r'\\VUgras\{([^{}]*)\}', r'\1', t)
    # \cc REJOINS, \nl SEPARATES. Both mark an end of line in the
    # facsimile, but \cc cuts a WORD and \nl cuts a phrase. Treated
    # both as white space, "recou\cc verte" gave "recou verte" and the
    # survey saw a green there -- the dessert table in table 4, the
    # covers in table 6: two colours that do not exist.
    # \ccplein is a \cc falling at the end of a PAGE: it must be taken
    # BEFORE \cc, or one tears off its head and "plein" is left in the
    # middle of the sentence.
    t = t.replace("\\ccplein\n", "").replace("\\ccplein", "")
    t = t.replace("\\cc\n", "").replace("\\cc", "")
    t = re.sub(r'\\nl\b', ' ', t)
    t = BALISE.sub(' ', t)
    return re.sub(r'\s+', ' ', t)


# THE THREE WAYS OF SAYING COLOUR, and all three are needed.
#
#  * THE PREPOSED EPITHET, Ido's: "blua cielo (1)", "nigra redingoto
#    (57)". At most two words between the adjective and the number --
#    a wider window took the first number that came, and gave the
#    black to the clouds in "la nigra silueto salias sur la blanka
#    nubi (67)", where the black belongs to the silhouette.
#
#  * THE POSTPOSED EPITHET, French's: "le ciel (1) bleu", "la lanterne
#    (25) rouge", "les fromages de Hollande (9) à la croûte rouge".
#    The number then PRECEDES the adjective. Three words at most, and
#    we go back up the coordination: "la robe (42) et à la pèlerine
#    (41) bleues" gives the blue to both.
#
#  * THE PREDICATE, in both languages: "Tote rozea e blanka esas ta
#    persikieri (18) ed abrikotieri (19)", "Ils sont tout roses et
#    tout blancs ces pêchers (18) et ces abricotiers (19)". The colour
#    then bears on EVERYTHING the sentence enumerates, and we read to
#    the full stop.
#
# The French is not a duplicate of the Ido: it names colours the Ido
# passes over -- "De gros nuages (56) noirs" in table 8, "une teinte
# verte" for the stand of trees (25) in table 9 -- and the Ido names
# some the French passes over. We survey both, therefore, and say which
# one speaks.
ANTE = re.compile(r"^\s*(?:[\w'\u2019-]+\s+){0,2}[\w'\u2019-]*\s*\((\d+)\)")
POST = re.compile(r"\((\d+)\)(?:[\s,]*(?:[\w'\u2019-]+[\s,]+){0,3})$")
COORD = re.compile(r"\((\d+)\)(?:[^.()]{0,40}?\b(?:et|ed?)\b[^.()]{0,40}?)$")
ETRE = re.compile(r"\b(?:esas|sont|est|semblas|semble)\b")
# THE RELATIVE PRONOUN CUTS THE COORDINATION. "seglo-navi (64) ed
# enorma paketboto (65) DI QUA la nigra silueto": the black belongs to
# the liner's silhouette, and the coordination preceding it does not
# claim it. Without this barrier, the survey gave the black to the
# sailing ships as well.
RELATIF = re.compile(r"\b(?:qua|qui|que|quan|dont|donta|kies)\b")

# THE FRENCH PREPOSES TOO, AND ITS DETERMINER SAYS SO. "emportait en
# NOIRS tourbillons la fumée (1)": the adjective looks ahead of itself,
# and the postposed reading gave it the sign (3) that precedes. An
# article or a preposition just before the colour marks the preposed
# form; a noun -- "à la croûte rouge", "nuages (56) noirs" -- marks the
# postposed one. "tout" is not on the list: "deux ramoneurs (91) TOUT
# noirs de suie" is indeed a postposed epithet.
DEVANT = re.compile(
    r"\b(?:de|du|des|en|par|avec|sans|au|aux|le|la|les|l|d|un|une|ce|ces"
    r"|cet|cette|son|sa|ses|leur|leurs|mon|ma|mes|nos|vos|deux|trois"
    r"|quelques|plusieurs|gros|grosse|petits?|petites?)['\u2019\s]+$",
    re.I)

RAD = {
    "io": ["red", "oranje", "flav", "verd", "blu", "viole", "purpure",
           "roze", "brun", "griz", "nigr", "blank"],
    "fr": ["rouge", "orang", "jaune", "vert", "bleu", "violet", "pourpre",
           "ros", "brun", "gris", "noir", "blanc", "blanch"],
}
FIN = {"io": r"(?:a|e|i)", "fr": r"(?:e?s?)"}
VERS_IO = {"rouge": "reda", "orang": "oranjea", "jaune": "flava",
           "vert": "verda", "bleu": "blua", "violet": "violea",
           "pourpre": "purpurea", "ros": "rozea", "brun": "bruna",
           "gris": "griza", "noir": "nigra", "blanc": "blanka",
           "blanch": "blanka"}
MOTS = {lg: re.compile(r"(?<![\w-])(" +
                       "|".join(sorted(r, key=len, reverse=True)) +
                       r")" + FIN[lg] + r"(?![\w-])",
                       0 if lg == "io" else re.I)
        for lg, r in RAD.items()}

SOURCES = [("io", "*-tabelo-*.tex"), ("fr", "*-tableau-*.tex")]


# THE REFERENCE THE PLATE DOES NOT CARRY. "les plates-bandes (150)",
# in table 5, are engraved "50": the colour must go and fetch the
# number that will be shown, not the one that is read.
# plates/corrections.json holds the table, and numbers.py reads it the
# same way.
def korekti():
    f = RACINE / "plates" / "corrections.json"
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding="utf-8")).items() if not k.startswith("_")}


KOREKTI = korekti()


def korekti_renvojo(tab, cle=""):
    """{read: to be read} for ONE BLOCK: the corrections that hold for the
    whole table, plus those this block alone carries.
    """
    t = KOREKTI.get(f"t{tab:02d}", {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out


# THE PLATES WITH SEVERAL SCENES. Six tables show two vignettes or
# more, and each restarts its numbering at 1: the "(18)" of the first
# scene and that of the third do not show the same object. Without the
# scene, the twenty-eight colours of tables 3, 4, 6, 7, 8 and 9 found
# no box on the plate, numbers.json filing them under "c1:18".
# plates/scenes.json says which tables are in this case.
def a_ceni():
    f = RACINE / "plates" / "scenes.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


CENI = a_ceni()

# THE PAGE THAT CUTS A WORD. \ccplein closes the page on a cut word,
# and four service lines come between it and the continuation. We erase
# them first, or the word stays in two pieces -- and a "continuation"
# block would come and cut a sentence that nothing cuts.
SAUT = re.compile(
    r'\\ccplein\s*\n\\end\{VUpage\}.*?'
    r'^%%K\s+\S+\s+\S+\s+suite\s*\n\\VUcontinue\s*\n',
    re.S | re.M)


def koloroj():
    f = RACINE / "plates" / "colours.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def ecartes():
    """{table: [(word, fragment)]} — see plates/colours.json."""
    return koloroj().get("ecarte", {})


# WHAT THE EYE HAS SEEN PREVAILS OVER WHAT THE RING MEASURES. The
# measurement does not know that the (65) of table 13 is laid on the
# canopy of a hotel and names a liner out at sea; it says "NO" and has
# seen nothing. The verdict held by hand in colours.json decides:
# "planche" when it is the plate that must be redone, "mesure" when the
# plate already says what the booklet says.
VERDIKTO = {"planche": "A REPEINDRE",
            "mesure": "la mesure a tort",
            "akordo": "vu, et la planche dit vrai"}


def vidita():
    """{"t13/65": (verdict, what was seen)}."""
    return {k: tuple(v) for k, v in koloroj().get("vidita", {}).items()}


def anteposee(apres):
    """The number the preposed epithet looks ahead to."""
    m = ANTE.match(apres)
    return [int(m.group(1))] if m else []


def postposee(avant, lg="io", mot=""):
    """The numbers the postposed epithet claims behind it."""
    m = POST.search(avant)
    if not m:
        return []
    if lg == "fr" and DEVANT.search(avant):
        return []
    ns = [int(m.group(1))]
    # THE COORDINATION GOES BACK UP: "la robe (42) et à la pèlerine (41)
    # bleues" -- the adjective agrees with both, and both want it. We look
    # after the NUMBER, not after the window: POST being anchored on the
    # end of the preceding text, m.end() designated its end and the slice
    # was always empty -- the relative's barrier never rose, and the
    # sailing ships (64) stayed black.
    if RELATIF.search(avant[m.end(1):]):
        return ns
    # IN IDO, THE POSTPOSED FORM EXISTS ONLY BEHIND A RELATIVE. The
    # language preposes its epithet: when the adjective follows a number
    # with no relative between the two, it qualifies another, and that
    # other is not always numbered. "nigra redingoto (57) e blanka jileto"
    # -- the waistcoat has no reference, and the white went to the
    # frock-coat; "brancho de filiko (55) e bela rozea brancheto di eriko
    # (57)" -- the pink belongs to the heather, and it went to the fern. In
    # Ido, therefore, we keep only the subordinate construction:
    # "paketboto (65) di qua la nigra silueto".
    if lg == "io":
        return []
    # THE COORDINATION IS READ FROM THE ADJECTIVE'S PLURAL. "la robe (42)
    # et à la pèlerine (41) BLEUES" takes both; "un brin de fougère (55)
    # très curieuse et un brin de bruyère (57) ROSE" takes only one, and
    # the pink does not belong to the fern. The agreement alone says how
    # far the epithet reaches -- "gris", invariable, is the only word that
    # lies, and it appears nowhere.
    if not mot.lower().endswith("s"):
        return ns
    reste = avant[:m.start()]
    while True:
        c = COORD.search(reste)
        if not c:
            break
        ns.append(int(c.group(1)))
        reste = reste[:c.start()]
    return ns


def numeros(t, i, j, lg="io"):
    """The numbers a colour reaches from position (i, j)."""
    avant, apres = t[max(0, i - 90):i], t[j:j + 90]
    # THE PREDICATE FIRST: if there is a copula close by, the colour
    # bears on the whole enumeration, and not on the first noun that
    # comes.
    #
    # THE VERB MUST STILL BE ITS OWN. "l'étalage EST garni de fromages de
    # Hollande (9) à la croûte rouge" does have an "est" in the window, but
    # it belongs to the display, not to the rind: a number separates it
    # from the adjective. Strong punctuation separates them likewise: "De
    # gros nuages (56) NOIRS montent dans le ciel ; ils SONT sillonnés par
    # les zigzags de l'éclair (55)" -- the verb belongs to the following
    # clause, and the black went to the lightning. We therefore require
    # that nothing fall between the adjective and its verb, neither
    # reference nor semicolon -- and "la reda lanterno (25) e la grosa pipo
    # qua ESAS uzata kom insigno (26)" stops painting the sign.
    for m in ETRE.finditer(t[max(0, i - 40):j + 40]):
        d, g = max(0, i - 40) + m.start(), max(0, i - 40) + m.end()
        entre = t[min(g, i):max(d, j)]
        if any(c in entre for c in "(;:."):
            continue
        phrase = apres.split(".")[0]
        ns = [int(x) for x in re.findall(r"\((\d+)\)", phrase)]
        if ns:
            return ns
        break
    # THE ORDER OF THE TWO CONSTRUCTIONS FOLLOWS THE LANGUAGE. Ido
    # preposes its epithet, French postposes it; trying the preposed form
    # first on both sides gave the red rind to the camemberts, "à la croûte
    # rouge, de camemberts (10)" -- the adjective looked ahead of itself
    # when it belongs to what precedes it. Each language therefore begins
    # with its own construction, and falls back on the other: the French
    # also says "en noirs tourbillons la fumée (1)".
    tour = [lambda: anteposee(apres), lambda: postposee(avant, lg, t[i:j])]
    if lg == "fr":
        tour.reverse()
    for f in tour:
        ns = f()
        if ns:
            return ns
    return []


def relever():
    """The (table, number, colour) triples the booklets state.

    WE READ BLOCK BY BLOCK, and not the file at a stroke: it is the
    block's key that gives the scene, and without the scene a number of
    table 3 designates nothing. The division has another merit: a colour
    will not claim a number from the neighbouring paragraph.
    """
    hors = ecartes()
    par = {}
    for lg, motif in SOURCES:
        for f in sorted((RACINE / "text" / lg).glob(motif)):
            tab = int(re.search(r"-(\d+)\.tex$", f.name).group(1))
            cle = f"t{tab:02d}"
            brut = SAUT.sub("\\\\cc\\n", f.read_text(encoding="utf-8"))
            sceno = ""
            parts = re.split(r"^%%K (\S+)", brut, flags=re.M)
            for i in range(1, len(parts), 2):
                mk = re.match(r"t\d\d-(c\d+)-", parts[i])
                if mk:
                    sceno = mk.group(1)
                kor = korekti_renvojo(tab, parts[i])
                t = texte(parts[i + 1])
                for m in MOTS[lg].finditer(t):
                    mot = m.group(0)
                    kunteksto = re.sub(
                        r"\s+", " ",
                        t[max(0, m.start() - 45):m.end() + 55]).strip()
                    if any(a.lower() == mot.lower() and b in kunteksto
                           for a, b in hors.get(cle, [])):
                        continue
                    coul = (m.group(1) + "a") if lg == "io" \
                        else VERS_IO[m.group(1).lower()]
                    for n in numeros(t, m.start(), m.end(), lg):
                        n = kor.get(str(n), str(n))
                        k = f"{sceno}:{n}" if cle in CENI and sceno else n
                        d = par.setdefault((tab, k, coul),
                                           {"tabelo": tab, "numero": k,
                                            "koloro": coul, "dit": [],
                                            "kunteksto": kunteksto})
                        if lg not in d["dit"]:
                            d["dit"].append(lg)
    return sorted(par.values(),
                  key=lambda r: (r["tabelo"], str(r["numero"])))


def teinte(rgb):
    """(hue in degrees, saturation, lightness) of an RGB 0-255 array."""
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
    """The dominant colour around a number, the reserve excluded."""
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
    # THE LINE IS NOT COLOUR, nor the paper the reserve.
    bon = (vv > 0.14) & (vv < 0.97)
    if bon.sum() < 30:
        return None
    hh, ss, vv = hh[bon], ss[bon], vv[bon]
    # The hue is averaged circularly, or red cancels itself out on
    # either side of zero.
    a = np.deg2rad(hh)
    poids = ss
    if poids.sum() < 1e-6:
        poids = np.ones_like(ss)
    hm = np.rad2deg(np.arctan2((np.sin(a) * poids).sum(),
                               (np.cos(a) * poids).sum())) % 360
    return float(hm), float(np.median(ss)), float(np.median(vv))


def accord(coul, mesure, tol=45):
    """Does the measured tone answer the named tone?"""
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
    num = json.loads((RACINE / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    obj = json.loads((RACINE / "plates" / "objects.json")
                     .read_text(encoding="utf-8"))
    par_tab = {}
    for cle, v in num.items():
        par_tab.setdefault(cle[:3], []).append((cle, v))
    vu = vidita()
    caches = {}
    accords = desaccords = sans = 0
    lignes = []
    for r in releve:
        tab = f"t{r['tabelo']:02d}"
        trouve = None
        for cle, v in par_tab.get(tab, []):
            b = v["numeri"].get(r["numero"])
            if b:
                trouve = (cle, v, b)
                break
        if not trouve:
            sans += 1
            continue
        cle, v, b = trouve
        if cle not in caches:
            im = Image.open(RACINE / "plates" / "kovri" /
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
        # A NUMBER SOMETIMES CARRIES TWO NAMES. The "(19)" of table 3 is
        # the presbytery in one paragraph and the apricot trees in another;
        # showing only one gave "rose presbytery" to read.
        n_obj = obj.get(tab, {}).get(r["numero"], {})
        nom = n_obj.get("fr") or n_obj.get("io") or ["—"]
        v = vu.get(f"{tab}/{r['numero']}")
        lignes.append((ok, tab, r["numero"], r["koloro"],
                       " / ".join(nom), dit, v))
    for ok, tab, n, c, nom, dit, v in sorted(lignes,
                                             key=lambda x: (x[0], x[1])):
        print(f"  {'  ' if ok else 'NON'}  {tab} ({str(n):>5})  "
              f"{FRANCAIS[c]:<8} {nom:<34} {dit}")
        if v:
            print(f"        {VERDIKTO[v[0]]} : {v[1]}")
    a_reprendre = sum(1 for l in lignes if l[6] and l[6][0] == "planche")
    print(f"\n  {accords} accords, {desaccords} desaccords, "
          f"{sans} sans position sur la planche "
          f"(sur {len(releve)} couleurs enoncees)")
    print(f"  {a_reprendre} endroits ou la planche dement le livret, "
          f"{len(lignes) - sum(1 for l in lignes if l[6])} pas encore regardes")



if __name__ == "__main__":
    main(sys.argv[1:])
