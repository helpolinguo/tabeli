#!/usr/bin/env python3
# ===================================================================
#  cross_refs.py — do a translation's references follow the order of the
#  Ido?
#
#  A REFERENCE IS AN APPOINTMENT. The left column carries the Ido
#  booklet, and each "(n)" there opens the close-up of an object on the
#  plate. A translation must aim at the SAME objects, in the SAME order:
#  the reader following both columns with the eye wants to find the (18)
#  opposite the (18).
#
#  ORDER IS NOT A DETAIL OF FORM. A language that postposes what Ido
#  preposes moves the noun, and the reference follows it: "अध्यापक (7)
#  अपने मंच (6) पर कुर्सी (8) पर" gives 7, 6, 8 where the Ido gives 7, 8,
#  6. The remedy is never to move the reference — it belongs to its word
#  — but to remake the sentence around it. Eleven inversions reported in
#  Hindi alone, ten in the five translations already served.
#
#  A REFERENCE IS NOT ALWAYS SET AS A SUPERSCRIPT. The Ido survey
#  sometimes sets "(80)" at full size — the speaker's name, in table 5 —
#  and html.py renders it as a reference like the others. We therefore
#  survey both forms, without which table 5 came out wrong throughout.
#
#  THE DECLARED DIVERGENCES. Three blocks diverge from the Ido in all six
#  translations at once, and that is intended: the Ido facsimile is wrong
#  there and the French is right. They are named below with their reason,
#  and the check passes them. Everything else is a fault.
#
#  AND THE FRENCH, WHICH WE DO NOT CHECK FOR ORDER, IS CHECKED FOR VALUE.
#  Rochelle orders his sentences as he pleases, but he aims at the SAME
#  OBJECTS: the number engraved on the plate is the same for both
#  editions. When a block carries the same NUMBER of references on either
#  side and not the same ones, that is no longer a different order, it is
#  a SUBSTITUTION — and seven had been sleeping there since the first
#  survey: 24 for 21, 16 for 46, 140 for 146, 11 for 41, 14 for 44, 19
#  for 49, 32 for 82. Five silently opened the close-up of another
#  object; two opened nothing. See substitui().
#
#  USAGE
#      python3 tools/cross_refs.py            # every column
#      python3 tools/cross_refs.py hi         # one only
#      python3 tools/cross_refs.py fr         # the substitutions
# ===================================================================

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_CORR = ROOT / "plates" / "corrections.json"
CORRECTIONS = ({k: v for k, v in
            json.loads(_CORR.read_text(encoding="utf-8")).items()
            if not k.startswith("_")} if _CORR.exists() else {})

# The name each column gives to "table" in its files.
FOLDER = {"fr": "tableau",
           # THE SAME TOKEN AS THE FRENCH: the word is the same on both
           # sides of the Atlantic, and the glob is done WITHIN the
           # language's directory — text/fr and text/fr-CA do not mix.
           "fr-CA": "tableau",
           "en": "table", "es": "cuadro", "ru": "tablica",
           "zh": "tubiao", "ar": "lawha", "hi": "talika",
           "pt": "quadro", "bn": "sarani", "ja": "zuhyo",
           "pnb": "naqsha", "pa": "sarni", "tr": "tablo",
           "eo": "tabelo", "ia": "tabella",
           "nl": "tabel", "sv": "tabell",
           "fi": "taulukko", "ca": "taula",
           "oc": "taula", "uk": "tablycia",
           "eu": "taula", "ro": "tabelul",
           "ga": "tabla", "gl": "cadro",
           "cs": "tabulka", "lt": "lentele",
           "lb": "tabell", "rm": "tabella",
           "et": "tabel",
           "vi": "bang",
           # CANTONESE takes "toubiu", which is "圖表" in jyutping
           # stripped of its tones — tou4 biu2. It is not confused with
           # Mandarin's "tubiao": these are the two readings of the same
           # word, and two columns.
           "yue": "toubiu",
           # SAME TOKEN AS STANDARD ARABIC: "لوحة" is written and said
           # the same way in Cairo, and the glob is done WITHIN the
           # language's directory — text/ar and text/arz do not mix, as
           # text/fr and text/fr-CA do not.
           "arz": "lawha",
           # MARATHI says "तक्ता", not "तालिका": the token is
           # therefore "takta" and not Hindi's.
           "mr": "takta",
           # TELUGU SAYS "పట్టిక" for a table.
           "te": "pattika",
           # KOREAN SAYS "도표" — dopyo. "표" alone would be the most
           # ordinary word in the language; the compound is not.
           "ko": "dopyo",
           # TAMIL SAYS "அட்டவணை" — attavanai. Neighbouring Telugu
           # says "పట్టిక": two Dravidian languages, two words, and that
           # is one more reason to translate each column for itself.
           "ta": "attavanai",
           # URDU SAYS "جدول" — jadval. Shahmukhi Punjabi, which
           # shares its alphabet, says "نقشہ": same script, two
           # languages, two words of apparatus.
           "ur": "jadval",
           # INDONESIAN SAYS "bagan" for a figured table. The "tabel"
           # one might have taken first is the Dutch word, already in
           # this table — and Indonesian borrowed it precisely from
           # Dutch. We therefore keep the underlying Malay word, which
           # owes nothing to anyone.
           "id": "bagan", "jv": "gambar", "fa": "tablo",
           "ha": "hoto",
           "gu": "kostak",
           "apc": "lawha",
           "bho": "nakasa",
           "de": "tafel",
           "it": "tavola",
           # POLISH SAYS "tablica", like transliterated Russian --
           # and the glob is done WITHIN the language's directory, so
           # that text/pl and text/ru do not mix, as text/fr and
           # text/fr-CA do not.
           "pl": "tablica",
           # AFRIKAANS SAYS "tabel", like Dutch. Same token, another
           # directory: that is already the case for standard Arabic
           # and Egyptian.
           "af": "tabel"}

# THE FRENCH IS NOT A TRANSLATION. It is the survey of ANOTHER
# edition, and Rochelle orders his sentences as he pleases: forty-five
# blocks diverge from the Ido there, and not one is a fault. We
# therefore do not apply the order check to it — but "not this one" has
# never meant "none", and that is nevertheless what this line ended up
# meaning: the French stayed the only one unchecked, and seven
# substitutions lived there until task 3. It has its own,
# substitui(), and main() runs it with the others.
TRANSLATED = [k for k in FOLDER if k != "fr"]

# DECLARED DIVERGENCES: {block key: reason}
APART = {
    "t06-c1-06-1":
        "le fac-simile ido ouvre sur « (6) », qui est le savon ; c'est la "
        "femme de chambre « (16) », comme le porte le francais",
    "t08-c2-03-1":
        "l'ido oublie le renvoi « (13) » de la faux, que le francais "
        "donne ; les traductions le rendent",
    "t16-15-1":
        "l'ido saute la lettre « (d) » dans l'enumeration des cartes ; "
        "le fac-simile la grave pourtant",
}

XREF_ = re.compile(r"\\textsuperscript\{\(([^)]*)\)\}"
                     r"|\((\d{1,3}(?:\s*(?:\\textit\{)?bis\}?)?)\)")


def xrefs(t):
    return [re.sub(r"\\[a-z]+|[{}\s]", "", m.group(1) or m.group(2))
            for m in XREF_.finditer(t)]


def blocks(folder, word):
    """{block key: body}, the "continuation" blocks rejoined to the first."""
    out = {}
    d = ROOT / "text" / folder
    if not d.is_dir():
        return out
    for f in sorted(d.glob(f"*-{word}-*.tex")):
        # The comment is stripped, but "%%K" is a key, not a comment:
        # removing it erased the whole division.
        t = re.sub(r"^%(?!%K).*\n", "", f.read_text(encoding="utf-8"),
                   flags=re.M)
        parts = re.split(r"^%%K (\S+)[^\n]*\n", t, flags=re.M)
        for i in range(1, len(parts), 2):
            out.setdefault(parts[i], []).append(parts[i + 1])
    return {k: "\n".join(v) for k, v in out.items()}


def correct_xref(key):
    """{read: to be read} for ONE BLOCK — the same reading html.py makes of
    plates/corrections.json: the corrections for the whole table, plus
    those this block alone carries."""
    t = CORRECTIONS.get(key[:3], {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    out.update(t.get(key, {}))
    return out


def substitute(verbose=True):
    """The numbers where the French and the Ido do not show the same object.

    THE SAME COUNT AND NOT THE SAME VALUES is a substitution. That is the
    whole check, and its strength lies in its asking for nothing else.
    Comparing the RUNS would have reported the forty-five blocks Rochelle
    reorders; comparing the SETS by plate saw only two of the seven,
    because a "24" put for "21" exists elsewhere on the same plate and
    melts into the set. The equality of the counts discards all the noise
    at a stroke — the block the French cuts in two where the Ido cuts it
    with "suite", the note call "(1)" that only one of the two editions
    carries — without anything having to be declared: those cases change
    the count.

    WE CORRECT BOTH COLUMNS, not only the one under suspicion. The "(150)"
    of table 5 is a fault of the IDO, and corrections.json repairs it;
    passing the correction over the French alone made what had just been
    corrected reappear as a substitution.
    """
    io = blocks("io", "tabelo")
    fr = blocks("fr", "tableau")
    false_ = []
    for k, v in fr.items():
        if k in APART or k not in io:
            continue
        m = correct_xref(k)
        a = Counter(m.get(x, x) for x in xrefs(io[k]))
        b = Counter(m.get(x, x) for x in xrefs(v))
        if sum(a.values()) == sum(b.values()) and a != b:
            false_.append((k, sorted(a - b), sorted(b - a)))
    if verbose:
        for k, a, b in false_:
            print(f"  {k}\n     io {a}\n     fr {b}")
    return len(fr), len(false_)


def check_(lg, verbose=True):
    io = blocks("io", "tabelo")
    tr = blocks(lg, FOLDER[lg])
    if not tr:
        return None
    false_ = []
    for k, v in tr.items():
        if k in APART:
            continue
        if k not in io:
            false_.append((k, None, xrefs(v)))
            continue
        a, b = xrefs(io[k]), xrefs(v)
        if a != b:
            false_.append((k, a, b))
    dones = {k[:3] for k in tr}
    miss = [k for k in io if k[:3] in dones and k not in tr]
    if verbose:
        for k, a, b in false_:
            print(f"  {k}\n     io {a if a is not None else '— key unknown'}"
                   f"\n     {lg} {b}")
        for k in miss:
            print(f"  {k} : block absent from column {lg}")
    return len(tr), len(false_) + len(miss), len(dones)


def hand(args):
    lgs = args or TRANSLATED
    total = 0
    # THE FRENCH GOES FIRST AND BY ANOTHER CHECK. We name it like the
    # others — "cross_refs.py fr" — but what we ask of it is not order:
    # it is that the two editions show the same object.
    if not args or "fr" in args:
        n, f = substitute()
        print(f"  fr : {n:4d} blocks, {f} substitution{'s' if f > 1 else ''}")
        total += f
        lgs = [lg for lg in lgs if lg != "fr"]
        if args and not lgs:
            print(f"\n  {len(APART)} declared exceptions, passed in silence.")
            return 1 if total else 0
    for lg in lgs:
        if lg not in FOLDER:
            raise SystemExit(f"  langue inconnue : {lg}")
        r = check_(lg)
        if r is None:
            print(f"  {lg} : rien a controler")
            continue
        n, f, tab = r
        total += f
        print(f"  {lg} : {n:4d} blocks over {tab:2d} tables, "
              f"{f} divergence{'s' if f > 1 else ''}")
    print(f"\n  {len(APART)} declared exceptions, passed in silence.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(hand(sys.argv[1:]))
