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
ROOT = Path(__file__).resolve().parent.parent

# THE NAMED COLOURS, and the tone asked of them. The tone is given in
# degrees on the hue wheel, with the expected saturation and lightness;
# "blanka" and "nigra" have no hue and are judged on lightness alone.
TONES = {
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
FRENCH = {
    "reda": "rouge", "oranjea": "orange", "flava": "jaune",
    "verda": "vert", "blua": "bleu", "violea": "violet",
    "purpurea": "pourpre", "rozea": "rose", "bruna": "brun",
    "griza": "gris", "nigra": "noir", "blanka": "blanc",
}

# THE ADJECTIVE INFLECTS — "reda", "rede", "redi" — and it must be
# taken in LOWER CASE: "Blanko" is a person's name (Jacques's father, in
# table 5), "Blank Urso" the sign of an inn.
ADJ = re.compile(
    r'(?<![A-Za-z])(' + '|'.join(sorted(TONES, key=len, reverse=True))
    .replace('a|', '|') + r')(?=\b)')
WORDS = re.compile(r'(?<![\w-])(' +
                  '|'.join(k[:-1] for k in sorted(TONES, key=len, reverse=True)) +
                  r')(?:a|e|i)(?![\w-])')
NUM = re.compile(r'\((\d+)\)')
TAG = re.compile(r'\\[A-Za-z]+\*?(?:\{[^{}]*\})?|[{}]|%.*')


def text_(t):
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
    t = TAG.sub(' ', t)
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
BEFORE_ = re.compile(r"^\s*(?:[\w'\u2019-]+\s+){0,2}[\w'\u2019-]*\s*\((\d+)\)")
AFTER_ = re.compile(r"\((\d+)\)(?:[\s,]*(?:[\w'\u2019-]+[\s,]+){0,3})$")
COORD = re.compile(r"\((\d+)\)(?:[^.()]{0,40}?\b(?:et|ed?)\b[^.()]{0,40}?)$")
COPULA = re.compile(r"\b(?:esas|sont|est|semblas|semble)\b")
# THE RELATIVE PRONOUN CUTS THE COORDINATION. "seglo-navi (64) ed
# enorma paketboto (65) DI QUA la nigra silueto": the black belongs to
# the liner's silhouette, and the coordination preceding it does not
# claim it. Without this barrier, the survey gave the black to the
# sailing ships as well.
RELATIVE = re.compile(r"\b(?:qua|qui|que|quan|dont|donta|kies)\b")

# THE FRENCH PREPOSES TOO, AND ITS DETERMINER SAYS SO. "emportait en
# NOIRS tourbillons la fumée (1)": the adjective looks ahead of itself,
# and the postposed reading gave it the sign (3) that precedes. An
# article or a preposition just before the colour marks the preposed
# form; a noun -- "à la croûte rouge", "nuages (56) noirs" -- marks the
# postposed one. "tout" is not on the list: "deux ramoneurs (91) TOUT
# noirs de suie" is indeed a postposed epithet.
AHEAD = re.compile(
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
END = {"io": r"(?:a|e|i)", "fr": r"(?:e?s?)"}
TO_IO = {"rouge": "reda", "orang": "oranjea", "jaune": "flava",
           "vert": "verda", "bleu": "blua", "violet": "violea",
           "pourpre": "purpurea", "ros": "rozea", "brun": "bruna",
           "gris": "griza", "noir": "nigra", "blanc": "blanka",
           "blanch": "blanka"}
WORDS = {lg: re.compile(r"(?<![\w-])(" +
                       "|".join(sorted(r, key=len, reverse=True)) +
                       r")" + END[lg] + r"(?![\w-])",
                       0 if lg == "io" else re.I)
        for lg, r in RAD.items()}

SOURCES = [("io", "*-tabelo-*.tex"), ("fr", "*-tableau-*.tex")]


# THE REFERENCE THE PLATE DOES NOT CARRY. "les plates-bandes (150)",
# in table 5, are engraved "50": the colour must go and fetch the
# number that will be shown, not the one that is read.
# plates/corrections.json holds the table, and numbering.py reads it the
# same way.
def corrections():
    f = ROOT / "plates" / "corrections.json"
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding="utf-8")).items() if not k.startswith("_")}


CORRECTIONS = corrections()


def correct_xref(tab, key=""):
    """{read: to be read} for ONE BLOCK: the corrections that hold for the
    whole table, plus those this block alone carries.
    """
    t = CORRECTIONS.get(f"t{tab:02d}", {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if key:
        out.update(t.get(key, {}))
    return out


# THE PLATES WITH SEVERAL SCENES. Six tables show two vignettes or
# more, and each restarts its numbering at 1: the "(18)" of the first
# scene and that of the third do not show the same object. Without the
# scene, the twenty-eight colours of tables 3, 4, 6, 7, 8 and 9 found
# no box on the plate, numbers.json filing them under "c1:18".
# plates/scenes.json says which tables are in this case.
def has_scenes():
    f = ROOT / "plates" / "scenes.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


SCENES = has_scenes()

# THE PAGE THAT CUTS A WORD. \ccplein closes the page on a cut word,
# and four service lines come between it and the continuation. We erase
# them first, or the word stays in two pieces -- and a "continuation"
# block would come and cut a sentence that nothing cuts.
JUMP = re.compile(
    r'\\ccplein\s*\n\\end\{VUpage\}.*?'
    r'^%%K\s+\S+\s+\S+\s+suite\s*\n\\VUcontinue\s*\n',
    re.S | re.M)


def colours_():
    f = ROOT / "plates" / "colours.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def set_aside():
    """{table: [(word, fragment)]} — see plates/colours.json."""
    return colours_().get("ecarte", {})


# WHAT THE EYE HAS SEEN PREVAILS OVER WHAT THE RING MEASURES. The
# measurement does not know that the (65) of table 13 is laid on the
# canopy of a hotel and names a liner out at sea; it says "NO" and has
# seen nothing. The verdict held by hand in colours.json decides:
# "planche" when it is the plate that must be redone, "mesure" when the
# plate already says what the booklet says.
VERDICT = {"planche": "A REPEINDRE",
            "mesure": "la mesure a tort",
            "akordo": "vu, et la planche dit vrai"}


def seen_at():
    """{"t13/65": (verdict, what was seen)}."""
    return {k: tuple(v) for k, v in colours_().get("vidita", {}).items()}


def preposed(after):
    """The number the preposed epithet looks ahead to."""
    m = BEFORE_.match(after)
    return [int(m.group(1))] if m else []


def postposed(before, lg="io", word=""):
    """The numbers the postposed epithet claims behind it."""
    m = AFTER_.search(before)
    if not m:
        return []
    if lg == "fr" and AHEAD.search(before):
        return []
    ns = [int(m.group(1))]
    # THE COORDINATION GOES BACK UP: "la robe (42) et à la pèlerine (41)
    # bleues" -- the adjective agrees with both, and both want it. We look
    # after the NUMBER, not after the window: POST being anchored on the
    # end of the preceding text, m.end() designated its end and the slice
    # was always empty -- the relative's barrier never rose, and the
    # sailing ships (64) stayed black.
    if RELATIVE.search(before[m.end(1):]):
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
    if not word.lower().endswith("s"):
        return ns
    left = before[:m.start()]
    while True:
        c = COORD.search(left)
        if not c:
            break
        ns.append(int(c.group(1)))
        left = left[:c.start()]
    return ns


def numbers(t, i, j, lg="io"):
    """The numbers a colour reaches from position (i, j)."""
    before, after = t[max(0, i - 90):i], t[j:j + 90]
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
    for m in COPULA.finditer(t[max(0, i - 40):j + 40]):
        d, g = max(0, i - 40) + m.start(), max(0, i - 40) + m.end()
        between = t[min(g, i):max(d, j)]
        if any(c in between for c in "(;:."):
            continue
        sentence = after.split(".")[0]
        ns = [int(x) for x in re.findall(r"\((\d+)\)", sentence)]
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
    turn = [lambda: preposed(after), lambda: postposed(before, lg, t[i:j])]
    if lg == "fr":
        turn.reverse()
    for f in turn:
        ns = f()
        if ns:
            return ns
    return []


def collect():
    """The (table, number, colour) triples the booklets state.

    WE READ BLOCK BY BLOCK, and not the file at a stroke: it is the
    block's key that gives the scene, and without the scene a number of
    table 3 designates nothing. The division has another merit: a colour
    will not claim a number from the neighbouring paragraph.
    """
    outside_ = set_aside()
    per = {}
    for lg, pattern in SOURCES:
        for f in sorted((ROOT / "text" / lg).glob(pattern)):
            tab = int(re.search(r"-(\d+)\.tex$", f.name).group(1))
            key = f"t{tab:02d}"
            raw = JUMP.sub("\\\\cc\\n", f.read_text(encoding="utf-8"))
            scene_ = ""
            parts = re.split(r"^%%K (\S+)", raw, flags=re.M)
            for i in range(1, len(parts), 2):
                mk = re.match(r"t\d\d-(c\d+)-", parts[i])
                if mk:
                    scene_ = mk.group(1)
                corr = correct_xref(tab, parts[i])
                t = text_(parts[i + 1])
                for m in WORDS[lg].finditer(t):
                    word = m.group(0)
                    kunteksto = re.sub(
                        r"\s+", " ",
                        t[max(0, m.start() - 45):m.end() + 55]).strip()
                    if any(a.lower() == word.lower() and b in kunteksto
                           for a, b in outside_.get(key, [])):
                        continue
                    col_ = (m.group(1) + "a") if lg == "io" \
                        else TO_IO[m.group(1).lower()]
                    for n in numbers(t, m.start(), m.end(), lg):
                        n = corr.get(str(n), str(n))
                        k = f"{scene_}:{n}" if key in SCENES and scene_ else n
                        d = per.setdefault((tab, k, col_),
                                           {"tabelo": tab, "numero": k,
                                            "koloro": col_, "dit": [],
                                            "kunteksto": kunteksto})
                        if lg not in d["dit"]:
                            d["dit"].append(lg)
    return sorted(per.values(),
                  key=lambda r: (r["tabelo"], str(r["numero"])))


def hue(rgb):
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


def read_ring(colour, x, y, w, h, size, inside=1.0, outside=3.0):
    """The dominant colour around a number, the reserve excluded."""
    cx, cy = x + w / 2, y + h / 2
    R = round(outside * size)
    x0, y0 = max(0, round(cx) - R), max(0, round(cy) - R)
    x1 = min(colour.shape[1], round(cx) + R)
    y1 = min(colour.shape[0], round(cy) + R)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return None
    f = colour[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.hypot(xx - cx, yy - cy)
    m = (d >= inside * size) & (d <= outside * size)
    pix = f[m]
    if len(pix) < 40:
        return None
    hh, ss, vv = hue(pix)
    # THE LINE IS NOT COLOUR, nor the paper the reserve.
    good = (vv > 0.14) & (vv < 0.97)
    if good.sum() < 30:
        return None
    hh, ss, vv = hh[good], ss[good], vv[good]
    # The hue is averaged circularly, or red cancels itself out on
    # either side of zero.
    a = np.deg2rad(hh)
    weight = ss
    if weight.sum() < 1e-6:
        weight = np.ones_like(ss)
    hm = np.rad2deg(np.arctan2((np.sin(a) * weight).sum(),
                               (np.cos(a) * weight).sum())) % 360
    return float(hm), float(np.median(ss)), float(np.median(vv))


def agreement(col_, measurement, tol=45):
    """Does the measured tone answer the named tone?"""
    h, s, v = measurement
    t, smin, vmax = TONES[col_]
    if col_ == "nigra":
        return v <= 0.34, f"clarte {v:.2f}"
    if col_ == "blanka":
        return v >= 0.72, f"clarte {v:.2f}"
    if col_ == "griza":
        return s <= 0.16, f"saturation {s:.2f}"
    if s < smin:
        return False, f"trop pale (saturation {s:.2f}, teinte {h:.0f}°)"
    gap = min(abs(h - t), 360 - abs(h - t))
    return gap <= tol, f"teinte {h:.0f}° au lieu de {t}° (ecart {gap:.0f}°)"


def hand(args):
    survey = collect()
    if "--tabelo" in args:
        n = int(args[args.index("--tabelo") + 1])
        survey = [r for r in survey if r["tabelo"] == n]
    num = json.loads((ROOT / "plates" / "numbers.json")
                     .read_text(encoding="utf-8"))
    obj = json.loads((ROOT / "plates" / "objects.json")
                     .read_text(encoding="utf-8"))
    by_table_ = {}
    for key, v in num.items():
        by_table_.setdefault(key[:3], []).append((key, v))
    seen_ = seen_at()
    hidden = {}
    agreements = disagreements = without = 0
    lines = []
    for r in survey:
        tab = f"t{r['tabelo']:02d}"
        found = None
        for key, v in by_table_.get(tab, []):
            b = v["numeri"].get(r["numero"])
            if b:
                found = (key, v, b)
                break
        if not found:
            without += 1
            continue
        key, v, b = found
        if key not in hidden:
            im = Image.open(ROOT / "plates" / "working" /
                            f"{key}-colour.png").convert("RGB")
            hidden[key] = np.asarray(
                im.resize((v["largeur"], v["alteso"]), Image.LANCZOS))
        C = hidden[key]
        m = read_ring(C, b[0] * v["largeur"], b[1] * v["alteso"],
                          b[2] * v["largeur"], b[3] * v["alteso"], v["corpo"])
        if m is None:
            without += 1
            continue
        ok, says = agreement(r["koloro"], m)
        agreements += ok
        disagreements += not ok
        # A NUMBER SOMETIMES CARRIES TWO NAMES. The "(19)" of table 3 is
        # the presbytery in one paragraph and the apricot trees in another;
        # showing only one gave "rose presbytery" to read.
        n_obj = obj.get(tab, {}).get(r["numero"], {})
        name_ = n_obj.get("fr") or n_obj.get("io") or ["—"]
        v = seen_.get(f"{tab}/{r['numero']}")
        lines.append((ok, tab, r["numero"], r["koloro"],
                       " / ".join(name_), says, v))
    for ok, tab, n, c, name_, says, v in sorted(lines,
                                             key=lambda x: (x[0], x[1])):
        print(f"  {'  ' if ok else 'NON'}  {tab} ({str(n):>5})  "
              f"{FRENCH[c]:<8} {name_:<34} {says}")
        if v:
            print(f"        {VERDICT[v[0]]} : {v[1]}")
    to_redo = sum(1 for l in lines if l[6] and l[6][0] == "planche")
    print(f"\n  {agreements} agreements, {disagreements} disagreements, "
          f"{without} with no position on the plate "
          f"(out of {len(survey)} colours stated)")
    print(f"  {to_redo} places where the plate belies the booklet, "
          f"{len(lines) - sum(1 for l in lines if l[6])} not yet looked at")



if __name__ == "__main__":
    hand(sys.argv[1:])
