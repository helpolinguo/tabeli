#!/usr/bin/env python3
# ===================================================================
#  objects.py — the name of each numbered object, in both languages.
#
#  « Nous avons imprime en caracteres gras les substantifs qui se
#  trouvent dans le vocabulaire des Tableaux EN LES FAISANT SUIVRE DE
#  LEUR NUMERO »: the French foreword states the rule itself, and it is
#  that rule which is read here. Each « (N) » in the text is preceded by
#  the bold noun it numbers; we therefore pick up the pair.
#
#  WHAT IT IS FOR. First, to know WHAT a close-up shows: a click on
#  « (15) » of table 13 opens the crate, and the page can say so.
#  Second, and above all, to check the number reader's doubtful
#  readings: when the machine hesitates, we look at the cut-out and ask
#  whether the named object is there. A « (65) » read on a hatching does
#  not show a tobacconist's; the name settles it where the shape of the
#  figure no longer suffices.
#
#  A NUMBER IS CALLED SEVERAL TIMES. The text comes back to it — « la
#  chambre (2) », then « cette chambre (2) » — and not always with the
#  same word. We keep every form encountered, the first at the head:
#  it is the one from the initial reading, the most descriptive.
#
#  USAGE
#      python3 tools/objects.py            # writes plates/objects.json
#      python3 tools/objects.py 13         # shows table 13
# ===================================================================

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# The bold noun, then its number — with or without a superscript, with
# or without a space between the two, the facsimile wavering on all
# three. THREE FORMS OF CROSS-REFERENCE, and all three were needed:
# « (18) », the group « (9, 11, 12) » which stands for three objects at
# once, and « 41) » where the opening parenthesis is missing. The noun
# is filed under each of the group's numbers: « les tableaux muraux
# (9, 11, 12) » names all three.
GRAS = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'      # \VUgras{...}
    r'(?:\s|\\nl|\\cc|%|\n)*'                   # line breaks
    r'(?:\\textsuperscript\{'
    r'(\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*,?'
    r'(?:\s*(?:\\textit\{)?bis\}?)?\s*\)?)\}'
    r'|\((\d{1,3}(?:\s*,\s*\d{1,3})*)\))')
CHIFRO = re.compile(r'\d{1,3}')
BIS = re.compile(r'\bbis\b')

# CROSS-REFERENCES BY LETTER. « rondo (a), quadrato (b) »: the letter is
# engraved on the object that carries it -- the blackboard, the map --
# and means nothing except in relation to it. plates/letters.json says,
# block by block, under which prefix to file it: the « a » of the
# blackboard is « 1a », that of the map « 10a ».
# THE LETTER APPEARS IN THREE GUISES. The French sets it in italic
# — « \textsuperscript{\textit{(a)}} » — the Ido leaves it bare, and six
# times across the two booklets one of the two parentheses is missing:
# « mi-sferi d) ». We accept all three, but require AT LEAST ONE
# PARENTHESIS: without it the « n° » of the text would be filed under « o ».
GRAS_LIT = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'
    r'(?:\s|\\nl|\\cc|%|\n)*'
    r'(?:\\textsuperscript\{(?:\\textit\{)?'
    r'(?:\(([a-z]{1,2})\)?|([a-z]{1,2})\))\}?\}'
    r'|\(([a-z]{1,2})\))')


def literi(champo):
    f = RACINE / 'plates' / 'letters.json'
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding='utf-8')).get(champo, {})


PATRI = literi('patri')

# THE « (1) » THAT IS AN l. On table 5, the bathroom carries a
# cross-reference set as « (1) »: in this font the lower-case l and the
# figure 1 have the same design, and the house plan settles it — its
# legend reads « l. Balneyo ». The name would therefore be filed under
# number 1, which is the facade; we file it under the letter.
UNU_SORTO = literi('unu-sorto')


# THE CROSS-REFERENCE THE PLATE DOES NOT CARRY. « les plates-bandes
# (150) », on table 5, are engraved « 50 »: the name must be filed under
# the number that will be shown, not under the one that is read.
# plates/corrections.json keeps the table, and numbering.py reads it the
# same way.
def korekti():
    f = RACINE / 'plates' / 'corrections.json'
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding='utf-8')).items() if not k.startswith('_')}


KOREKTI = korekti()


def korekti_renvojo(tab, cle=""):
    """{read: to be read} for ONE BLOCK: the corrections that hold for the
    whole table, plus those this block alone carries.

    A CORRECTION DOES NOT ALWAYS HOLD EVERYWHERE. The « (150) » of
    table 5 is a number the plate has nowhere: correcting it everywhere
    can break nothing. The « (6) » that table 6 gives the chambermaid,
    on the other hand, is a number that exists elsewhere — it is the
    soap of paragraph 2 — and correcting it everywhere would make the
    soap point at the chambermaid. An entry whose key is that of a
    BLOCK therefore holds only within that block.
    """
    t = KOREKTI.get(f"t{tab:02d}", {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out

# THE NOUN IS NOT ALWAYS BOLD BEFORE A LETTER. « la zoologio (a),
# botaniko (b), geologio (c) »: three bare words, where the foreword's
# rule calls for bold. Both workshops keep to it for the numbers and
# forget it for the letters. We therefore take up the preceding word,
# for want of better: without it the close-up would open saying nothing
# of what it shows.
NUD_LIT = re.compile(
    r"([\w'\u2019-]+)\s*(?:\\nl|\\cc)?\s*"
    r'\\textsuperscript\{\(([a-z]{1,2})\)\}')

# What is left of the markup in the name picked up.
MACROS = re.compile(r'\\(?:textit|textsc|emph|VUgras|nl|cc|hbox|,)\b\{?')


def nettoyer(brut):
    t = MACROS.sub('', brut)
    t = t.replace('\\-', '').replace('~', ' ').replace('{', '').replace('}', '')
    t = re.sub(r'\s+', ' ', t).strip(' .,;:')
    # A noun broken by a change of line keeps its hyphen from the
    # facsimile; it does not belong to the word.
    return re.sub(r'-\s+', '', t)


# A NOUN BROKEN BY THE END OF A LINE IS SET IN TWO PIECES, each in its
# own \VUgras — that is the rule of the transcription, a line of the
# facsimile being a line of the source. « \VUgras{jour}\cc /
# \VUgras{naux} » therefore gave « naux », and « \VUgras{livre}\nl /
# \VUgras{des voyageurs} » gave « des voyageurs ». We glue back together
# before reading: \cc has broken a word, \nl has broken a phrase.
RECOLLE = [
    (re.compile(r'\\VUgras\{([^{}]*)\}\\cc\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    # A HYPHEN AT THE END OF A LINE TAKES NO SPACE: the word goes on.
    # « \VUgras{lad-(if-)}\nl \VUgras{isto} » is the name of the tinsmith-
    # lamplighter, and the close-up was titling it « lad-(if-) isto ».
    (re.compile(r'\\VUgras\{([^{}]*-\)?)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    (re.compile(r'\\VUgras\{([^{}]*)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1 \2}'),
    # A COMPOUND WHOSE HYPHEN THE LINE BREAKS HAS ONLY ITS SECOND HALF
    # IN BOLD. The compositor opens the bold at the start of the next
    # line: « mason-\nl \VUgras{servisto} », « pluv-\nl
    # \VUgras{kanali} », « vitro-\nl \VUgras{kareli} ». The word is one
    # all the same, and the facsimile proves it itself two lines below,
    # where « \VUgras{tekto-kanali} » holds on one line and takes all
    # the bold. The close-up said « servisto » where the French says
    # « aide-macon ».
    (re.compile(r'(?<![\\{])\b((?:[\w\'\u2019]+-)+)\\nl\s*\n\s*\\VUgras\{'),
     r'\\VUgras{\1'),
    # AND ON A SINGLE LINE TOO, when the facsimile opens the bold at
    # the second member: « pesko-\VUgras{barketi} », « (muton)-\VUgras
    # {trupo} », « (pastor)-\VUgras{bastono} ». The first member carries
    # the sense — the flock is of sheep, the crook is a shepherd's — and
    # without it the name says nothing any more: « po », « bastono ».
    (re.compile(r'(?<![\\{])((?:\(?[\w\'\u2019]+\)?-)+)\\VUgras\{'),
     r'\\VUgras{\1'),
    # A GROUP BROKEN BY THE END OF A LINE is set in two superscripts,
    # « (9, 11, » then « 12) ». Without this gluing back, the twelve was
    # left orphaned and the wall charts had only two names out of three.
    (re.compile(r'\\textsuperscript\{([^{}]*,)\}\s*(?:\\nl|\\cc)?\s*\n?\s*'
                r'\\textsuperscript\{([^{}]*)\}'),
     r'\\textsuperscript{\1 \2}'),
]


# A WORD BROKEN BY THE END OF A PAGE, for its part, has the whole
# apparatus of the leaf between its two halves: \ccplein, the closing of
# the page, the leaf's comment, the opening of the next, the « suite »
# key and \VUcontinue. We bring that case back to the previous one — a
# plain \cc — and the rule above does the rest: « \VUgras{dro}\ccplein
# ... \VUgras{medaro} » gives « dromedaro », not « medaro ».
# TWO SPELLINGS FOR THE SAME END OF PAGE. \ccplein says it in one word;
# table 7 writes it \cc then \parplein on two lines, and the break at
# leaf 54 escaped the gluing: the shepherd's flock, « (muton)-\VUgras
# {tru}\cc ... \VUgras{po} », was called « po » in the close-up.
# THE JUMP IS MEASURED, IT IS NOT GUESSED. « .*? » between the end of
# page and the « suite » block was unbounded: where the next page did
# not continue the paragraph, the pattern ran to the next « suite » and
# carried off two whole leaves of table 2 -- the game of skittles lost
# one of its two names there. We therefore name what separates the two
# halves: the closing of a page, a leaf comment, the opening of the next
# page, and nothing else.
SAUT = re.compile(
    r'(?:\\ccplein|\\cc\s*\n\\parplein)\s*\n\\end\{VUpage\}[ \t]*\n'
    r'(?:%[^\n]*\n|[ \t]*\n)*'
    r'\\begin\{VUpage\}[^\n]*\n'
    r'%%K\s+\S+\s+\S+\s+suite[ \t]*\n\\VUcontinue[ \t]*\n')


def recoller(texte):
    texte = SAUT.sub('\\\\cc\n', texte)
    for motif, remplacement in RECOLLE:
        avant = None
        while avant != texte:
            avant = texte
            texte = motif.sub(remplacement, texte)
    return texte


# PLATES WITH SEVERAL SCENES. Six tables show two vignettes or more, and
# each starts its numbering again at 1: the « (39) » of the first scene
# and that of the fourth do not name the same object. The name is
# therefore filed under a key carrying the scene — « c1:39 » —, as in
# numbers.json. plates/scenes.json says which tables are in that case.
def a_ceni():
    f = RACINE / "plates" / "scenes.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


CENI = a_ceni()


def relever(dossier, motif):
    """{table number: {object key: [names]}} for one language."""
    out = {}
    for f in sorted((RACINE / "text" / dossier).glob(motif)):
        m = re.search(r'-(?:tabelo|tableau|table|cuadro|tablica|tubiao|lawha|talika|quadro|sarani|zuhyo|naqsha|sarni|tablo|tabella|tabel|tabell|taulukko|taula|tablycia|tabelul|tabla|cadro|tabulka|lentele)-(\d+)\.tex$', f.name)
        if not m:
            continue
        tab = int(m.group(1))
        par = out.setdefault(tab, {})
        scenes = f"t{tab:02d}" in CENI
        texte = recoller(f.read_text(encoding="utf-8"))
        # We cut by block key, so as to know which scene is meant.
        parts = re.split(r'^%%K (\S+)', texte, flags=re.M)
        for i in range(1, len(parts), 2):
            mk = re.match(r't\d\d-(c\d)-', parts[i])
            if mk:
                relever.scene = mk.group(1)
            sc = getattr(relever, "scene", "") if scenes else ""
            # The block's letters, if it carries any.
            pa = PATRI.get(parts[i])
            if pa:
                # A WRONG LETTER IS CORRECTED LIKE A WRONG NUMBER. On
                # table 1 the two booklets swap Europe and Asia; without
                # this reading, the name was filed under the booklet's
                # letter and the close-up of Europe was titled « Azia ».
                kl = korekti_renvojo(tab, parts[i])
                for g in GRAS_LIT.finditer(parts[i + 1]):
                    nom = nettoyer(g.group(1))
                    if not nom:
                        continue
                    for L in (g.group(2) or g.group(3)
                              or g.group(4) or ""):
                        k = pa[1] + kl.get(L, L)
                        noms = par.setdefault(k, [])
                        if nom not in noms:
                            noms.append(nom)
                for g in NUD_LIT.finditer(parts[i + 1]):
                    for L in g.group(2):
                        k = pa[1] + kl.get(L, L)
                        if par.get(k):
                            continue
                        nom = nettoyer(g.group(1))
                        if nom:
                            par.setdefault(k, []).append(nom)
            uniq = UNU_SORTO.get(parts[i], [])
            for g in GRAS.finditer(parts[i + 1]):
                nom = nettoyer(g.group(1))
                if not nom:
                    continue
                brut = g.group(2) or g.group(3) or ""
                # The bold word is sometimes broken in two by the end of a
                # line — « salle » then « de bains » — and the rule names
                # only the last piece: we accept it at the end of a name as
                # well as as a whole name.
                L = next((L for m, L in uniq
                          if nom == m or nom.endswith(" " + m)), None)
                if L:
                    k = pa[1] + L if pa else L
                    noms = par.setdefault(k, [])
                    if nom not in noms:
                        noms.append(nom)
                    continue
                ns = CHIFRO.findall(brut)
                # « 94 bis » does not name the 94: it is a separate object.
                if ns and BIS.search(brut):
                    ns[-1] = f"{ns[-1]}bis"
                kor = korekti_renvojo(tab, parts[i])
                for n in ns:
                    n = kor.get(str(n), n)
                    k = f"{sc}:{n}" if sc else n
                    noms = par.setdefault(k, [])
                    if nom not in noms:
                        noms.append(nom)
        relever.scene = ""
    return out


def rang(k):
    s, n = k.split(":", 1) if ":" in k else ("", k)
    m = re.match(r'(\d*)([a-z]*)$', n)
    return (s, int(m.group(1) or 0), m.group(2))


# THE OBJECT'S NAME FOLLOWS THE COLUMN THAT CALLS IT. The close-up
# carries the name of what it shows, and that name is read in the
# column's language: « fumeyo » on the left, « fumoir » in the middle,
# « smoking room » on the right. We therefore pick up all three the same
# way -- the bold noun preceding the cross-reference -- and the English
# translation, which keeps exactly the same cross-references as the other
# two, lets itself be picked up by the same code, but for the filename.
SOURCES = [("io", "*-tabelo-*.tex"), ("fr", "*-tableau-*.tex"),
           # Same token as French, another directory: see cross_refs.py.
           ("fr-CA", "*-tableau-*.tex"),
           ("en", "*-table-*.tex"), ("es", "*-cuadro-*.tex"),
           ("ru", "*-tablica-*.tex"), ("zh", "*-tubiao-*.tex"),
           ("ar", "*-lawha-*.tex"),
           # Same token as Standard Arabic, another directory: see
           # cross_refs.py.
           ("arz", "*-lawha-*.tex"), ("hi", "*-talika-*.tex"),
           ("mr", "*-takta-*.tex"),
           ("te", "*-pattika-*.tex"),
           ("ko", "*-dopyo-*.tex"),
           ("ta", "*-attavanai-*.tex"),
           ("ur", "*-jadval-*.tex"),
           ("id", "*-bagan-*.tex"),
           ("jv", "*-gambar-*.tex"),
           ("fa", "*-tablo-*.tex"),
           ("ha", "*-hoto-*.tex"),
           ("gu", "*-kostak-*.tex"),
           ("apc", "*-lawha-*.tex"),
           ("bho", "*-nakasa-*.tex"),
           ("pt", "*-quadro-*.tex"), ("bn", "*-sarani-*.tex"),
           ("ja", "*-zuhyo-*.tex"), ("pnb", "*-naqsha-*.tex"),
           ("pa", "*-sarni-*.tex"),
           ("tr", "*-tablo-*.tex"),
           ("eo", "*-tabelo-*.tex"),
           ("ia", "*-tabella-*.tex"),
           ("nl", "*-tabel-*.tex"),
           ("sv", "*-tabell-*.tex"),
           ("fi", "*-taulukko-*.tex"),
           ("ca", "*-taula-*.tex"),
           ("oc", "*-taula-*.tex"),
    ("uk", "*-tablycia-*.tex"),
    ("eu", "*-taula-*.tex"),
    ("ro", "*-tabelul-*.tex"),
    ("ga", "*-tabla-*.tex"),
    ("gl", "*-cadro-*.tex"),
    ("cs", "*-tabulka-*.tex"),
    ("lt", "*-lentele-*.tex"),
    # LUXEMBOURGISH TAKES UP SWEDISH'S TOKEN, « tabell », because it
    # writes the word the same way. The filename pattern therefore
    # already knows it; only this pair was missing. Three languages
    # already share « taula » — Catalan, Occitan and Basque — and the
    # glob is rooted in text/<language>/: two different directories do
    # not mix.
    ("lb", "*-tabell-*.tex"),
    # ROMANSH TAKES UP INTERLINGUA'S TOKEN, « tabella ». The filename
    # pattern therefore already knows it, as it knew « tabell » when
    # Luxembourgish arrived. Fourth shared token of the series; the
    # glob remaining rooted in text/<language>/, two directories do
    # not mix.
    ("rm", "*-tabella-*.tex"),
    # ESTONIAN TAKES UP DUTCH'S TOKEN, « tabel ». Fifth and last shared
    # token of the series of seventeen; the glob remaining rooted in
    # text/<language>/, text/nl and text/et do not mix.
    ("et", "*-tabel-*.tex"),
    # VIETNAMESE OPENS THE REST OF THE ETHNOLOGUE PROGRAMME. Its token,
    # « bang », is the word « bảng » stripped of its marks, as « talika »
    # is of « तालिका » and « naqsha » of « نقشہ »: filenames stay in
    # ASCII, and it is the directory — text/vi — that carries the
    # language. The token is new; none of the seventeen before it comes
    # close.
    ("vi", "*-bang-*.tex"),
    # CANTONESE takes « toubiu », the Jyutping of « 圖表 » without its
    # tones. Mandarin has « tubiao »: same word, two readings, two
    # columns.
    ("yue", "*-toubiu-*.tex"),
    # GERMAN takes « tafel », which is nobody's token: it resembles the
    # Dutch « tabel » and the Swedish « tabell » without equalling them
    # — an F where they have a B.
    ("de", "*-tafel-*.tex"),
    # ITALIAN takes « tavola », which is nobody's token. It resembles
    # the « taula » shared by Catalan, Occitan and Basque — one V more —
    # and the « tabella » of Interlingua and Romansh — a V instead of a B.
    ("it", "*-tavola-*.tex"),
           # Same token as Russian and Dutch, other directories: see
           # cross_refs.py.
           ("pl", "*-tablica-*.tex"), ("af", "*-tabel-*.tex")]


def construire():
    par_langue = {k: (relever(k, m) if (RACINE / "text" / k).is_dir() else {})
                  for k, m in SOURCES}
    tabs = sorted({t for d in par_langue.values() for t in d})
    tout = {}
    for tab in tabs:
        cles = sorted({k for d in par_langue.values()
                       for k in d.get(tab, {})}, key=rang)
        tout[f"t{tab:02d}"] = {
            k: {lg: d.get(tab, {}).get(k, []) for lg, d in par_langue.items()}
            for k in cles}
    return tout


def attendus(tab):
    return set(relever("io", f"*-tabelo-{tab:02d}.tex").get(tab, {}))


def main(args):
    tout = construire()
    if args:
        tab = f"t{int(args[0]):02d}"
        for n, v in sorted(tout[tab].items(), key=lambda kv: rang(kv[0])):
            print("  " + f"{n:>6}  " + "  ".join(
                f"{' / '.join(v.get(k, [])) or '—':28s}" for k, _ in SOURCES))
        return
    (RACINE / "plates" / "objects.json").write_text(
        json.dumps(tout, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    for tab, par in sorted(tout.items()):
        att = attendus(int(tab[1:]))
        tout_ = sum(1 for v in par.values() if all(v.get(k) for k, _ in SOURCES))
        print(f"  {tab}  {len(par):3d}/{len(att):3d} objets nommes, "
              f"dont {tout_:3d} dans les {len(SOURCES)} langues")
    n = sum(len(p) for p in tout.values())
    a = sum(len(attendus(int(t[1:]))) for t in tout)
    print(f"  TOTAL {n}/{a} = {100 * n // a} %")


if __name__ == "__main__":
    main(sys.argv[1:])
