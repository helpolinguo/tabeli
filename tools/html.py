#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html.py — builds index.html from the LaTeX sources.

    python3 tools/html.py

THE TEXT IS KEYED IN ONLY ONCE. The files in text/ are the sole
source: the PDF and the reading page both come out of them. A
correction of the reading made in the .tex therefore turns up on
screen with nothing to carry over, and it is impossible for the two
states of the text to diverge.

WHAT THE PAGE MAKES OF THE DIPLOMATIC TRANSCRIPTION. The PDF keeps
the line breaks of the facsimile; the reading page cannot -- its
column has no fixed width. The transcription's two marks are
therefore handled thus:
    \\nl  (end of line without a hyphen)  ->  a space
    \\cc  (end of line WITH a hyphen)     ->  nothing: the word glues
          back together, since the hyphen belonged not to the word but
          to the composition.
It is the only way to make the text searchable: « docochambro » broken
as « doco-chambro » would not be found.

THE PAIRING OF THE TWO COLUMNS is done neither by page nor by line --
the two editions have neither the same pagination nor the same number
of lines -- but by the transcription's « %%K » keys, which take up the
AUTHOR'S OWN PARAGRAPH NUMBERING. It is the same in both booklets, and
it is the only anchor they share.
"""
import html as H
import itertools
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


# THE WALL PLATE ABOVE ITS TEXT. The booklet explains an engraving the
# reader does not have before him; the page gives it to him. The
# catalogue is written by tools/plates.py, which prepares the images:
# it carries the dimensions, and it is by them that the page reserves
# the space before the image has even loaded -- failing which the text
# jumps when it arrives.
def gravuri():
    cat = RACINE / "plates" / "plates.json"
    return json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}


# THE CROSS-REFERENCE THE PLATE DOES NOT CARRY. plates/corrections.json
# says, table by table, which cross-reference to read in place of which
# other: on table 5, « les plates-bandes (150) » are engraved « 50 ».
# The source does not move; it is the reading page that shows the right
# number.
_KOREKTI = None


def korekti(tab):
    """The cross-references to correct for this table: {read: to be read}."""
    global _KOREKTI
    if _KOREKTI is None:
        f = RACINE / "plates" / "corrections.json"
        _KOREKTI = (json.loads(f.read_text(encoding="utf-8"))
                    if f.exists() else {})
    return _KOREKTI.get(tab, {})


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
    t = korekti(tab)
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    if cle:
        out.update(t.get(cle, {}))
    return out


def nomo(nm, langue):
    """The object's name IN THE LANGUAGE OF THE COLUMN.

    The close-up carries the name of what it shows, and that name is
    read in the language of the text that called it: « fumeyo » on the
    left, « fumoir » in the middle, « smoking room » on the right. The
    1693 objects are not all named in the three -- the noun must be in
    bold before the cross-reference, and one edition sometimes forgets
    it -- hence the fallback, in order: its own language, Ido, French.
    """
    # AND THE VARIANT READS THE NAME OF ITS COLUMN. plates/objects.json
    # names the objects by column — « en », not « en-GB »: the two English
    # editions draw the same name from it, which the regional overlay then
    # retouches if it must. Without that detour, the variant found nothing
    # under its code and fell back on Ido.
    for k in (TABLO.get(langue, langue), "io", "fr"):
        v = nm.get(k)
        if v:
            return v[0]
    return next((v[0] for v in nm.values() if v), "")


# A PLAN IS NOT A VIEW. Table 5 carries, beside the house in section,
# the plan of its floors: eight numbers are read there, and all eight
# are read on the house as well. The plan engraves them a little more
# cleanly, and it was winning that contest — so that the water closet
# (20) opened on an empty rectangle between two partitions, when the
# house in section shows its door, marked « W. C. 20 ». The sharpness
# of the figure is not what we are after: we are after the thing. The
# plan therefore takes only the numbers the view does not have — and it
# turns out there are none.
PLANOJ = {"t05-apar-2"}


def numeri():
    """{table: {number: (engraving key, x, y, w, h, names)}}.

    The positions are a FRACTION of the plate: the page serves the same
    engraving at three resolutions, and the close-up must fall right on
    each. The name comes from the transcription of the bold nouns.
    """
    f = RACINE / "plates" / "numbers.json"
    if not f.exists():
        return {}
    o = RACINE / "plates" / "objects.json"
    noms = json.loads(o.read_text(encoding="utf-8")) if o.exists() else {}
    out, force = {}, {}
    tout = json.loads(f.read_text(encoding="utf-8"))
    # THE PLANS LAST: they take only what is left.
    for cle in sorted(tout, key=lambda c: c in PLANOJ):
        v = tout[cle]
        tab, plano = cle[:3], cle in PLANOJ
        for n, b in v["numeri"].items():
            # A TABLE MAY HAVE TWO PLATES — table 5 has two, table 12
            # too — and the same number may then be read on both. We
            # keep the better supported reading, not the last to
            # arrive; but a plan takes only what the view does not
            # have, however well supported it may be.
            if plano and (tab, n) in force:
                continue
            if force.get((tab, n), -1) >= b[4]:
                continue
            force[(tab, n)] = b[4]
            out.setdefault(tab, {})[n] = (
                cle, b[0], b[1], b[2], b[3],
                noms.get(tab, {}).get(n, {}))
    return out


# THE CROSS-REFERENCE THAT KNOWS WHERE IT POINTS BECOMES A BUTTON. The
# others stay text: we do not promise a close-up we would not know how
# to show.
# « 94 bis » IS NOT 94. The engraver of table 5 added two tools after
# the fact and slipped them in among the others rather than renumber
# the plate: the chisel carries « 94bis », the mallet « 95bis ». The
# cross-reference keeps the word -- in italic on the French side, bare
# on the Ido side -- and the button aims at the separate object, not at
# its neighbour.
RENVOI_REND = re.compile(
    r'<sup>(\(?)\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)'
    r'(\s*(?:<i>)?bis(?:</i>)?)?\s*(\)?)</sup>')

# The languages of the right-hand column. « fr » is the source text
# (transcribed from the facsimile); the others are translations, and
# carry the appropriate mention.
#
# « differita »: THE TRANSLATION DOES NOT TRAVEL WITH THE PAGE. The
# French is a transcribed facsimile, it is part of the object; the
# English is only a convenience for reading. index.html already weighs
# 1.4 MB for its two columns, and sewing a third language into it would
# make it grow as much again for a reader who, nine times out of ten,
# will not ask for it. The languages marked here therefore come out in a
# separate file, lingui/<kodo>.json, and the browser goes to fetch it
# only when the language is chosen from the menu. The page, for its
# part, keeps the empty cells in their place -- what arrives has only to
# be poured into them.
# THE SIX OFFICIAL LANGUAGES OF THE UN, plus Ido, which is the source.
# The French belongs to the set by the facsimile itself; the English,
# the Spanish, the Russian, the Chinese and the Arabic are translations
# of 2026, made from the Ido and checked against the French.
# -------------------------------------------------------------------
# THE REGIONAL VARIANTS: AN OVERLAY, NOT ONE MORE COLUMN.
# -------------------------------------------------------------------
# Two editions of one language differ, in this booklet, by only a few
# dozen words. Making two columns of sixteen files out of them would
# amount to copying thirty thousand words to change thirty, and above
# all to having to correct TWICE every slip found later. The base column
# therefore does not move, and text/variants.json says what the other
# edition writes in its place.
#
# AND NEITHER OF THE TWO IS PRIVILEGED IN THE MENU. The one that
# carries the files does not appear there under its directory name:
# « English (UK) » is text/en as it stands, « English (US) » is the same
# passed through the table, and the reader does not have to know which
# is which.
def varianti():
    f = RACINE / "text" / "variants.json"
    if not f.exists():
        return {}
    d = json.loads(f.read_text(encoding="utf-8"))
    return {k: v for k, v in d.items() if k != "_"}


VARIANTI = varianti()


LANGUES = [
    {"kodo": "fr", "nomo": "Français", "dir": "ltr", "fonto": "fac-similé"},
    {"kodo": "en", "nomo": "English", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "es", "nomo": "Español", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ru", "nomo": "Русский", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "zh", "nomo": "中文", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ar", "nomo": "العربية", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "hi", "nomo": "हिन्दी", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "pt", "nomo": "Português", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "bn", "nomo": "বাংলা", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ja", "nomo": "日本語", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "pnb", "nomo": "پنجابی", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "pa", "nomo": "ਪੰਜਾਬੀ", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "tr", "nomo": "Türkçe", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "eo", "nomo": "Esperanto", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ia", "nomo": "Interlingua", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "nl", "nomo": "Nederlands", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "sv", "nomo": "Svenska", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "fi", "nomo": "Suomi", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ca", "nomo": "Català", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "oc", "nomo": "Occitan", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "uk", "nomo": "Українська", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "eu", "nomo": "Euskara", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ro", "nomo": "Română", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "ga", "nomo": "Gaeilge", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "gl", "nomo": "Galego", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "cs", "nomo": "Čeština", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "lt", "nomo": "Lietuvių", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "lb", "nomo": "Lëtzebuergesch", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "rm", "nomo": "Rumantsch", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "et", "nomo": "Eesti", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # TWO COLUMNS OUTSIDE BOTH LISTS. Polish is not among Ethnologue's
    # twenty-nine -- it comes well behind Bhojpuri -- and it is not one
    # of Ido's seventeen countries either; Afrikaans is further still.
    # They are there because they were asked for. The menu does not
    # distinguish them from the others: they have a number of speakers,
    # they take their rank by that number, and that is all _order() knows
    # about them.
    {"kodo": "pl", "nomo": "Polski", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "af", "nomo": "Afrikaans", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # THE SEVENTEEN LANGUAGES OF THE IDIST COMMUNITY ARE CLOSED. What
    # follows takes up the programme of Ethnologue's twenty-nine
    # languages, in order of first-language speakers, where it had
    # stopped — after Turkish, and without Wu, set aside for the reason
    # written in « ecartita » of text/languages.json.
    {"kodo": "vi", "nomo": "Tiếng Việt", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # CANTONESE IS WRITTEN, AND THAT IS WHY IT IS HERE. It has no
    # academy, but it has its characters — 嘅, 喺, 唔, 咗, 佢, 睇 — and
    # Hong Kong prints them every day, in its newspapers, its novels and
    # its subtitles. The column is therefore written in WRITTEN
    # Cantonese, not in standard Chinese read the Cantonese way: failing
    # which it would be redundant with « zh » but for the spelling,
    # which is exactly the reason WU was set aside.
    {"kodo": "yue", "nomo": "粵語", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # EGYPTIAN ARABIC IS WRITTEN, AND IT IS PRINTED. It has no academy
    # either, but it has its novels, its theatre, its subtitles, its
    # song lyrics and its encyclopaedia; and it has a grammar that
    # Standard Arabic does not have — ده for هذا, مش for ليس, the
    # negation in ما...ش, the presentative بـ before the imperfective,
    # the future in حـ, and بتاع for the annexation. The column is
    # therefore written in WRITTEN Egyptian, not in Standard Arabic read
    # in Cairo: it is the same condition that made the Cantonese column
    # and that had Wu set aside.
    {"kodo": "arz", "nomo": "مصرى", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "mr", "nomo": "मराठी", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # TELUGU IS DRAVIDIAN, AND IT IS THE FIRST TIME. The sixteen
    # preceding Indian columns — Hindi, Bengali, Punjabi, Marathi — are
    # Indo-European and distant cousins of Ido; this one is not at all.
    # It agglutinates its cases instead of postposing them, it has no
    # grammatical gender but a human / non-human opposition, and its
    # verb ends the sentence without exception. No other column of the
    # transcription is built that way.
    {"kodo": "te", "nomo": "తెలుగు", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # KOREAN IS RELATED TO NO OTHER COLUMN. Japanese resembles it in
    # word order and in nothing else; Chinese and Cantonese lent it its
    # old learned lexicon and not its grammar. It is written, moreover,
    # in an alphabet shared by nobody, which makes the column easy to
    # check: an ideogram in text/ko is a fault, and columns.py reports
    # it.
    {"kodo": "ko", "nomo": "한국어", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # TAMIL IS THE SECOND DRAVIDIAN COLUMN, after Telugu, and the
    # first to have a neighbour that resembles IT: Telugu is of its
    # family, not of its alphabet. The threat is therefore not graphic
    # — each Dravidian column has its own script — but lexical, and
    # columns.py takes it where it shows.
    {"kodo": "ta", "nomo": "தமிழ்", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # URDU IS THE FIRST COLUMN WITH TWO NEIGHBOURS OF DIFFERENT
    # NATURES. It shares its LANGUAGE with Hindi — same grammar, same
    # basic lexicon, two scripts and two learned registers — and its
    # SCRIPT with Shahmukhi Punjabi, which is another language.
    # columns.py therefore defends it on two fronts at once.
    {"kodo": "ur", "nomo": "اردو", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    # INDONESIAN HAS NO NEIGHBOUR IN THE TRANSCRIPTION, AND THAT IS
    # PRECISELY ITS DIFFICULTY. Malaysian Malay is the same language but
    # for a standard, it is in no column, and nothing would signal it to
    # the eye: columns.py therefore holds it by the LEXICON. To which is
    # added a second front, which is a DATE: the spelling before the 1972
    # reform — « boekoe », « djalan », « tjelana » — is exactly the one a
    # booklet of 1926 would have used, and it is the trap peculiar to
    # this column.
    {"kodo": "id", "nomo": "Indonesia", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # JAVANESE IS THE FIRST COLUMN WHOSE NEIGHBOUR HAS JUST BEEN
    # WRITTEN BY THE SAME HAND. Indonesian, which was missing from the
    # transcription when the « id » column was being defended, is now in
    # text/id — and the danger has turned about: it is no longer the
    # neighbour's absence, it is her presence on the line above. To
    # which is added what no column had yet had: grammaticalised SPEECH
    # LEVELS (ngoko, krama), two parallel lexicons within one language.
    {"kodo": "jv", "nomo": "Basa Jawa", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # PERSIAN HAS TWO NEIGHBOURS IN THE TRANSCRIPTION AND BOTH ARE IN
    # ITS ALPHABET: Urdu, which took from it its script and half its
    # learned lexicon, and Arabic, which gave it the alphabet and the
    # other half. The difference is therefore played out at the level of
    # the CHARACTER as much as the word — ی against ي, ک against ك,
    # ۱ against ١ —, and those differences are invisible to the eye.
    {"kodo": "fa", "nomo": "فارسی", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    # HAUSA IS THE FIRST COLUMN OF THE TRANSCRIPTION WRITTEN IN LATIN
    # LETTERS WHOSE DIACRITICS ARE FULL LETTERS IN THEIR OWN RIGHT. ɓ, ɗ,
    # ƙ and ƴ are not b, d, k, y with ornaments: they are four letters of
    # the boko alphabet, and « kofa » is not « ƙofa ». An ordinary
    # keyboard does not give them, and a spell-checker readily returns
    # them to their bare form: the column therefore defends itself
    # against its own typing, which no other has had to do.
    {"kodo": "ha", "nomo": "Hausa", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # GUJARATI HAS THREE NEIGHBOURS IN THE TRANSCRIPTION AND THEY ARE
    # OF THREE NATURES: Hindi, which is the state language and shares
    # with it its whole Sanskrit stock; Marathi, which is the neighbour
    # to the south and shares the same family of script; Urdu and
    # Persian, which left it the lexicon of the Sultanate. But its OWN
    # DIFFICULTY lies elsewhere: the Gujarati script is Devanagari
    # WITHOUT THE BAR, letter for letter or nearly, and a Devanagari
    # character slipped into a Gujarati word is read without anyone
    # noticing.
    {"kodo": "gu", "nomo": "ગુજરાતી", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # THE FIRST COLUMN WHOSE TWO NEIGHBOURS ARE THE SAME LANGUAGE AS
    # ITSELF. Persian defended its alphabet against two foreign
    # languages that had borrowed it; this one defends a REGISTER
    # against two other registers of Arabic, all three already in the
    # transcription: « ar » the standard, « arz » the Egyptian. The
    # danger is not that a foreign word should slip in, it is that the
    # hand should climb of its own accord back towards the written form
    # learnt at school.
    {"kodo": "apc", "nomo": "شامي", "dir": "rtl",
     "fonto": "traduction moderne", "differita": True},
    # THE ONLY COLUMN WHOSE NEIGHBOUR DENIES THAT IT EXISTS. All the
    # others defended themselves against a language that recognised them
    # as distinct; Bhojpuri, for its part, is administered in India as a
    # « dialect of Hindi », though it has more than fifty million
    # speakers. It shares with Hindi the script, the bulk of the lexicon
    # and a good part of the morphology: there is therefore NO defence
    # possible at the character. What separates the two languages is the
    # verb — the copula बा, the negation नइखे, the past in -ल.
    {"kodo": "bho", "nomo": "भोजपुरी", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "de", "nomo": "Deutsch", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    {"kodo": "it", "nomo": "Italiano", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
    # CANADIAN FRENCH IS A TRANSLATION, NOT A VARIANT. The « fr » column
    # is the transcription of a facsimile of 1926 and the source does not
    # move: a regional overlay laid on it would give a booklet of 1926
    # written with the words of today's Quebec, an object that has never
    # existed. This one is therefore translated from the Ido, like the
    # thirty others, and is filed with them.
    {"kodo": "fr-CA", "nomo": "Français (CA)", "dir": "ltr",
     "fonto": "traduction moderne", "differita": True},
]


# THE VARIANT TAKES ITS PLACE IN THE LIST, JUST AFTER ITS BASE: in the
# menu the two editions of a language follow each other, and the base
# appears there under its regional name. All the rest of the page
# treats them like any other column — same « differita » bag, same
# lingui/<kodo>.json, same count of blocks.
def poser_varianti(langues):
    out = []
    for lg in langues:
        v = VARIANTI.get(lg["kodo"])
        if not v:
            out.append(lg)
            continue
        lg = dict(lg, kodo=v["bazo"]["kodo"], nomo=v["bazo"]["nomo"],
                  dosiero=lg["kodo"])
        out.append(lg)
        out.append(dict(lg, kodo=v["kalko"]["kodo"], nomo=v["kalko"]["nomo"],
                        kalko=lg["kodo"]))
    return out


LANGUES = poser_varianti(LANGUES)

# THE HAND-KEPT TABLES KNOW THE COLUMN, NOT THE VARIANT.
# plates/corrections.json corrects « en »: the correction bears on what
# the transcription wrote, and both English editions want it. We
# therefore translate the variant's code into a column code before any
# consultation of a table.
TABLO = {lg["kodo"]: lg.get("dosiero", lg["kodo"]) for lg in LANGUES}
TABLO["io"] = "io"


# THE ORDER OF THE MENU IS NO LONGER KEPT BY HAND. The languages came
# out until now in the order in which they had been written, that is,
# in the order in which they had been translated: the reader could not
# guess where to look for his own, and each new column lengthened the
# list at the bottom. We therefore sort it, and by a rule that can be
# verified:
#
#   1. FRENCH FIRST, because it is not a translation. The French
#      booklet is the other original; its facsimile is in this
#      repository as the Ido's is.
#   2. THEN THE CONSTRUCTED LANGUAGES, in the order Idist usage names
#      them: Esperanto, then Interlingua. They have no first-language
#      speakers to count, and they are the closest kin to the
#      booklet's own language.
#   3. THEN THE COLUMNS THE REGISTER MARKS « off list », that is, those
#      written by people who do not have them as a mother tongue.
#      Standard Arabic is the only one of the menu in that case:
#      Ethnologue gives it no figure because it has almost no
#      first-language speakers — they are counted under its varieties,
#      Egyptian (83) and Levantine (55), which are two columns of this
#      repository. It is therefore NOT a language without a figure by
#      accident, it is a language declared outside the table, and the
#      register says so itself in its preamble.
#   4. THEN THE OTHERS, BY NUMBER OF FIRST-LANGUAGE SPEAKERS, from the
#      largest to the smallest. The figure is not an opinion: it is in
#      text/languages.json, drawn from Ethnologue, and it is that same
#      file that serves as the column's register. A language without a
#      figure goes to the tail rather than the head.
#
# The sort READS the register instead of repeating it: adding a column
# therefore no longer calls for choosing its place, and the place can
# no longer lie about the figure.
#
# RANK 3 WAS ADDED AFTER THE FACT, AND IT REPAIRS A MEASURED DEFECT.
# Standard Arabic came out LAST in the menu, fifty-third of
# fifty-three, below Romansh and its forty thousand speakers. The cause
# was not the register, which is right not to give it a figure, but a
# disagreement between two places in the same file: NO_FIGURE, below,
# declared FOUR columns legitimately without a figure — fr, eo, ia, ar
# — but the sort placed only three. French is taken at rank 1,
# Esperanto and Interlingua at rank 2; Arabic fell under no rule at all
# and therefore ended in the default branch, « a language without a
# figure goes to the tail ».
# AN EXEMPTION THAT IS NOT ALSO A PLACE EXEMPTS FROM NOTHING: it merely
# silences the check while the defect settles in. We therefore read
# « stato » as we read « milioni », in the same register and by the
# same key, and NO_FIGURE is DEDUCED instead of being kept by hand — one
# more rank can no longer be forgotten.
KONSTRUKTITA = ["eo", "ia"]


def _lire_registre(champ):
    """{kodo: value of the field}, from text/languages.json."""
    f = RACINE / "text" / "languages.json"
    if not f.is_file():
        return {}
    reg = json.loads(f.read_text(encoding="utf-8"))
    return {l[0]: l[champ] for l in reg.get("lingui", []) if len(l) > champ}


def _rango_lingui():
    """{kodo: millions of first-language speakers}, from the register."""
    return _lire_registre(2)


def _stato_lingui():
    """{kodo: state of the column}, from the register."""
    return _lire_registre(4)


# THE FIGURE IS LOOKED UP UNDER THE COLUMN'S CODE, NOT UNDER THE
# DISPLAY CODE, and that is the fault that undid the order of the menu
# when the regional variants arrived. apply_variants() replaces the code
# « en » with « en-GB » and « en-US »; the register knows only « en ».
# The lookup therefore failed, both English editions passed for
# languages without speakers, and the rule « a language without a figure
# goes to the tail » sent them there. Six languages out of seven fell
# into it at one stroke — Chinese (988 million), Spanish (487), English
# (372), Portuguese (252), German (76), Dutch (25) — that is, the four
# most spoken of the booklet, filed after Romansh.
#
# We therefore look up in this order:
#   1. « dosiero », which is the COLUMN's code — that of the files and
#      of the register — and which apply_variants() lays on both
#      editions;
#   2. failing that the code itself;
#   3. failing that the language subtag, before the hyphen: « fr-CA »
#      counts with French. A regional column that is not a variant —
#      Quebec French is one — thus finds its place without having to be
#      entered in Ethnologue's register, where it has no business.
def _sub_registre(lg, table):
    for k in (lg.get("dosiero"), lg["kodo"], lg["kodo"].split("-")[0]):
        if k in table:
            return table[k]
    return None


def _milioni(lg, rango):
    return _sub_registre(lg, rango)


def _ordre(lg, milioni, statoj):
    if lg["kodo"] == "fr":
        return (0, 0, "")
    if lg["kodo"] in KONSTRUKTITA:
        return (1, KONSTRUKTITA.index(lg["kodo"]), "")
    if _sub_registre(lg, statoj) == "hors liste":
        return (2, 0, lg["kodo"])
    m = _milioni(lg, milioni)
    # THE TWO EDITIONS OF A LANGUAGE HAVE THE SAME FIGURE and therefore
    # necessarily follow each other. Between them we decide by the code,
    # which is neutral: the column that carries the files has no
    # privilege, as text/variants.json lays down in principle.
    return (3, -(m if m is not None else -1), lg["kodo"])


_RANGO = _rango_lingui()
_STATOJ = _stato_lingui()
LANGUES.sort(key=lambda lg: _ordre(lg, _RANGO, _STATOJ))

# A COLUMN WITHOUT A FIGURE FALLS TO THE TAIL SAYING NOTHING, and that
# is precisely what happened. The sort cannot check itself — it would
# give the same wrong result again — but its MATERIAL can be checked:
# every column must be found in the register. Four have no figure and
# that is intended: French, which goes to the head because it is not a
# translation; Esperanto and Interlingua, which have no first-language
# speakers to count; Standard Arabic, which has almost none and which
# text/languages.json marks « off list ». Any other is a wiring fault.
SEN_NOMBRO = ({"fr"} | set(KONSTRUKTITA)
              | {k for k, v in _STATOJ.items() if v == "hors liste"})
_orfa = [lg["kodo"] for lg in LANGUES
         if lg["kodo"] not in SEN_NOMBRO and _milioni(lg, _RANGO) is None]
if _orfa:
    print("  COLONNES ABSENTES DU REGISTRE, rangees en queue du menu "
          "faute de chiffre : " + ", ".join(_orfa))

TITRO = "Expliko-Libreto di la Delmas-Tabeli helpanta"
SUBTITRO = ("J. Guignon &middot; Ido-Kontoro, Thaon-les-Vosges, 1926 "
            "&middot; E. Rochelle &middot; G. Delmas, Bordeaux")


# -------------------------------------------------------------------
#  1. READING THE LaTeX SOURCES
# -------------------------------------------------------------------
CLE = re.compile(r"^%%K\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$")
PAGE = re.compile(r"\\begin\{VUpage\}(?:\[(\d+)\])?\{([^}]*)\}")


def accolade(s, i):
    """Contents of the brace beginning at s[i] == '{'. Returns
    (contents, index after the closing brace). Nested braces are
    counted: \\VUgras{Ka\\cc rolus} itself contains macros, and a plain
    search for the next '}' would cut them."""
    assert s[i] == "{"
    p = 0
    j = i
    while j < len(s):
        if s[j] == "{":
            p += 1
        elif s[j] == "}":
            p -= 1
            if p == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


# The mark of a word broken by the end of a PAGE. It travels through
# the rendered HTML as far as merge(), which glues the two halves.
# BOLD MARKS A TERM, AND A FUNCTION WORD IS NOT ONE. The compositor
# sometimes set it beside: « il tenas \VUgras{la} vishilo » puts the
# bold on the article and leaves the noun light, « \VUgras{Ica}
# docisto » on the demonstrative. We do not move the bold — the
# facsimile does not say how far it ought to reach —, we take it off:
# the reading page no longer presses on « la », « Ica », « ta »,
# « quale », « e ». The five translations had followed the Ido word for
# word, and said « \VUgras{This} teacher », « \VUgras{Los} viejos
# coches », « \VUgras{Этот} учитель »: the same list corrects them.
#
# THE RULE IS APPLIED AFTER THE TAGS ARE GLUED BACK, and it must be:
# « \VUgras{quadra}\cc \VUgras{to} » ends on a « to » which is an Ido
# pronoun — but it is not a word, it is the tail of « quadrato », and
# the gluing has already returned it to its own.
MOTOJ_VAKA = {
    # Ido
    "la", "l'", "ica", "ta", "ico", "to", "il", "el", "ol", "li", "lu",
    "un", "una", "mea", "sua", "lia", "nia", "via", "quale", "e", "ed",
    "o", "od", "di", "da", "de",
    # French
    "le", "les", "ce", "cet", "cette", "ces", "une", "des", "du", "et",
    "ou", "son", "sa", "ses", "leur", "leurs", "elle", "on",
    # English
    "the", "a", "an", "this", "that", "these", "those", "his", "her",
    "its", "and", "or",
    # Spanish
    "el", "los", "las", "este", "esta", "ese", "esa", "su", "sus", "y",
    "del",
    # Russian
    "этот", "эта", "это", "эти", "тот", "та", "те", "и", "или", "его",
    "её", "их",
    # Arabic
    "هذا", "هذه", "تلك", "ذلك", "و",
    # Chinese: the demonstrative drags its classifier along, and
    # « 这位 » is a word of one piece.
    "这", "那", "这位", "那位", "这个", "那个", "这些", "那些", "和", "或",
}
PONKTO = " .,;:!?»«\u202f\u2019'\u3001\u3002\uff08\uff09"

COUPE = "\x02"


def texte_html(t):
    """Converts a LaTeX fragment of the transcription into HTML."""
    # THE COMMENTS FIRST. A « % » opens a comment to the end of the line,
    # and the transcription uses it: a note's content opens with « {% » so
    # that LaTeX takes no space there, and closes with « .% » for the same
    # reason. Without taking them out, the rendered text began with
    # « % (*) Por la baptonomi... » — and the call marker, preceded by that
    # percent, was no longer recognised: no note attached to its call.
    # The literal percent is written « \% » in the transcription; we
    # protect it before cutting, and give it back afterwards.
    t = t.replace("\\%", "\x00")
    t = re.sub(r"%.*?(?:\n|$)", "\n", t)
    t = t.replace("\x00", "%")

    # THE FACSIMILE SETS IN BOLD ONLY THE SECOND HALF OF A WORD THE LINE
    # HAS BROKEN. « ...e ban\cc \VUgras{doliera vildo-sako} »: the
    # compositor opens his bold at the RESUMPTION, because the word begins
    # on the line before and the line before is already set. The word is
    # one all the same, and the reading page, which does not break in the
    # same place, gave « ban<b>doliera vildo-sako</b> ».
    # It is the same accident as « pesko-\VUgras{barketi} », dealt with
    # below, except that the join falls not on a hyphen but on the end of a
    # line: the left-hand piece bears no mark at all, and must therefore be
    # recognised by the fact that it TOUCHES the \VUgras that follows, with
    # no space between them.
    #
    # TEN PLACES, AND ALL IN THE TWO TRANSCRIPTIONS. « bandoliera »,
    # « damzelo », « portreto », « kulbutas », « buketo », « kabini »,
    # « dolorigas », « generalo » on the Ido side; « precedent » and
    # « baigneurs » on the French. The rule cannot go astray in a
    # translation: « \cc » exists only where a printed line is transcribed,
    # and the sixteen translated columns have not one.
    #
    # WE REQUIRE A SPACE BEFORE THE PIECE, failing which the rule would
    # bite on the « \VUgras{chas}\cc \VUgras{gardisto} » of the same table,
    # where BOTH halves already carry their bold and where it is the
    # reunion of the tags, below, that does the work.
    t = re.sub(r"(?<=\s)([^\s{}\\]{1,20})\\cc\n\\VUgras\{",
               r"\\VUgras{\1", t)

    # The breaks: they carry the logic of the transcription.
    # \ccplein FIRST, AND FOR TWO REASONS. It is \cc and \parplein at once:
    # the page ends on a broken word, and the paragraph resumes on the next
    # leaf. Taken out after \cc, the macro lost its first two letters and
    # left « plein » in the text — the reading page gave « dro plein
    # medaro » for « dromedaro ». It leaves here a mark that merge() will
    # read: the word is broken, the resumption glues back WITHOUT a space.
    t = t.replace("\\ccplein\n", COUPE).replace("\\ccplein", COUPE)
    # AND « \\cc » FOLLOWED BY « \\parplein » IS WORTH « \\ccplein ». The two
    # macros written one after the other do what \\ccplein does at a stroke,
    # and eleven pages of the two booklets are set that way. The PDF sees
    # nothing amiss; the reading page, for its part, did not find the break
    # mark, and merge() glued back WITH a space: « klo vagas » for
    # « klovagas », « ma traco » for « matraco », « tran quila » for
    # « tranquila », « efekti gas » for « efektigas », « par ticioni » for
    # « particioni », « yuni no » for « yunino », « kon servar » for
    # « konservar ». Seven words of the Ido and four of the French, cut in
    # two on screen by the end of a leaf alone.
    t = re.sub(r"\\cc\n(?=\\parplein\b)", COUPE, t)
    t = t.replace("\\cc\n", "").replace("\\cc", "")
    # A HYPHEN AT THE END OF A LINE TAKES NO SPACE AFTER IT. \nl marks an
    # end of line WITHOUT a composed hyphen: the facsimile adds none,
    # because the word already carries one. « mason-\nl servisto »,
    # « pluv-\nl kanali », « lad-(if-)\nl isto » are one word each, and the
    # space cut them in two on screen: « lad-(if-) isto ». We therefore
    # weld when the line ends on a hyphen — the hyphen itself stays:
    # « kroket-partio » is written so, and nothing must weld it.
    t = re.sub(r"(?<=\w)(-\)?\}?)[ \t]*\\nl\s*", r"\1", t)
    t = t.replace("\\nl\n", " ").replace("\\nl", " ")
    # THE COMPOUND TAKES ALL THE BOLD. The facsimile sometimes puts it
    # only on the second member — « pesko-\VUgras{barketi} », « (muton)-
    # \VUgras{trupo} », and « mason-\nl \VUgras{servisto} » when the line
    # breaks the hyphen. The word is one all the same: two lines below, the
    # same facsimile sets « \VUgras{tekto-kanali} » in one piece. The first
    # member carries the sense — the flock is of sheep, the crook is a
    # shepherd's — and the object was named « po », « bastono ». We
    # therefore extend the bold leftwards, after taking out the breaks: the
    # two cases then come down to one.
    t = re.sub(r"(?<![\\{])((?:\(?[\w'\u2019]+\)?-)+)\\VUgras\{",
               r"\\VUgras{\1", t)
    t = t.replace("\\parplein", "").replace("\\VUcontinue", "")
    t = re.sub(r"\\VUblancAlinea\b", "", t)
    t = re.sub(r"\\VUsaut\{[^}]*\}", "", t)
    t = re.sub(r"\\VUblanc\{[^}]*\}", "", t)
    t = re.sub(r"\\VUinterlignePage\{[^}]*\}", "", t)

    out = []
    i = 0
    balises = {"\\VUgras": "b", "\\textit": "i", "\\textsuperscript": "sup",
               "\\emph": "i", "\\textbf": "b"}
    # Macros with SEVERAL arguments: we say how many are to be read and
    # which one carries the text. \VUcentre{body}{letterspacing}{text}:
    # the first two are measurements of the facsimile, they have no
    # business in the reading page, but they must be READ, or their
    # contents fall into the text — that is what gave
    # « 12.6pt{120}{EXPLIKO - LIBRETO} » at the first attempt.
    # The third member is the HTML wrapping of the text kept: the display
    # lines of a table's opening are LINES, and must remain so on screen —
    # failing which « EXPLIKO - LIBRETO DI la Delmas - tabeli helpanta
    # UNESMA SERIO » reads in one breath.
    # \VUpk sets nothing around its text — the block that carries it
    # centres it already — but it is a display LINE, and the table of
    # contents must count it as such: the titles of tables 8, 11, 12, 13
    # and 16 pass through it, and not through \VUtitre. Unmarked, they were
    # invisible to the table, which announced those tables under their
    # number alone. We therefore mark it with a class WITHOUT STYLE,
    # « pk »: the rendering does not change by a pixel, but the line is
    # counted. The class name must stay in agreement with LIGNE_AP, which
    # reads it back.
    # THE TYPE SIZE IS KEPT, HOWEVER. The facsimile's other measurements
    # serve only the printed page, but the size says whether two display
    # lines are one and the same thing: the title of table 6 holds on two
    # lines of 11.4pt, that of table 13 on two lines of 10.2pt, and the
    # table of contents announced them as a title followed by a section. A
    # line of a DIFFERENT size, on the other hand, begins something else
    # — on table 2, « La Korpo homala. » is in 13.2pt beneath a title in
    # 11.4pt. We therefore deposit it in data-korpo, which the table of
    # contents reads back.
    arite = {"\\VUcentre": (3, 2, '<span class="ln" data-korpo="%(korpo)s">'
                                  '%(text)s</span>'),
             "\\VUtitre": (3, 2, '<span class="ln lg" data-korpo="%(korpo)s">'
                                 '%(text)s</span>'),
             "\\VUpk": (3, 2, '<span class="pk" data-korpo="%(korpo)s">'
                              '%(text)s</span>'),
             "\\VUcentreA": (4, 3, '<span class="ln" data-korpo="%(korpo)s">'
                                   '%(text)s</span>'),
             "\\VUfilet": (1, None, '<span class="fil"></span>'),
             "\\VUornamento": (1, None, '<span class="orn">\u2766</span>'),
             "\\VUnotes": (2, 1, "%(text)s"),
             # \fontsize{body}{leading}: two measurements of the facsimile,
             # nothing to keep. Undeclared, it passed for an unknown macro with
             # ONE argument: the size fell into the text and the leading stayed
             # between braces — the title of the Balneyo announced itself as
             # « 10.2pt{10.2pt}[40]{La Balneyo.} ».
             "\\fontsize": (2, None, "")}
    while i < len(t):
        if t[i] == "\\":
            m = re.match(r"\\[A-Za-z]+", t[i:])
            if m:
                nom = m.group(0)
                j = i + len(nom)
                while j < len(t) and t[j] == " ":
                    j += 1
                # THE OPTIONAL ARGUMENT IS READ TOO. \textls[40]{...} carries
                # its letterspacing in brackets; unread, it came out as it
                # stood — « [40]{La Balneyo.} ». It is a measurement of the
                # facsimile: we read it and throw it away.
                while j < len(t) and t[j] == "[":
                    ferme = t.find("]", j)
                    if ferme < 0:
                        break
                    j = ferme + 1
                    while j < len(t) and t[j] == " ":
                        j += 1
                if nom in arite:
                    n, garde, habit = arite[nom]
                    args = []
                    k = j
                    for _ in range(n):
                        while k < len(t) and t[k] in " \n":
                            k += 1
                        if k < len(t) and t[k] == "{":
                            a, k = accolade(t, k)
                            args.append(a)
                        else:
                            args.append("")
                    if garde is None:
                        out.append(habit)
                    elif garde < len(args):
                        out.append(habit % {
                            "text": texte_html(args[garde]),
                            "korpo": args[0] if args else ""})
                    i = k
                    continue
                if nom in balises and j < len(t) and t[j] == "{":
                    dedans, k = accolade(t, j)
                    out.append(f"<{balises[nom]}>{texte_html(dedans)}"
                               f"</{balises[nom]}>")
                    i = k
                    continue
                if nom == "\\textasciitilde":
                    out.append("~")
                    i = j
                    continue
                # Unknown macro: we let it drop with its argument.
                if j < len(t) and t[j] == "{":
                    dedans, k = accolade(t, j)
                    out.append(texte_html(dedans))
                    i = k
                    continue
                i = j
                continue
            # \, \; \: — thin spaces
            if t[i + 1:i + 2] in (",", ";", ":"):
                out.append("\u202f")
                i += 2
                continue
            out.append(t[i + 1:i + 2])
            i += 2
            continue
        # A GROUP IS NOT TEXT. A few places in the transcription set by hand
        # what the \VU macros do elsewhere:
        # « {\centering\textit{(Videz la plano.)}\par} ». The braces there open
        # a LaTeX SCOPE, they do not print; left as they stood, they came out
        # in the page and in the table of contents — « {(Videz la plano.)} ».
        # We read the group and keep only its contents. The literal brace, for
        # its part, is written « \{ » in the transcription, and that case is
        # handled just above.
        if t[i] == "{":
            dedans, k = accolade(t, i)
            out.append(texte_html(dedans))
            i = k
            continue
        out.append(t[i])
        i += 1
    t = "".join(out)

    # A WORD BROKEN BY THE COMPOSITION IS STILL A WORD. When the break
    # falls inside a passage in bold, the transcription carries two
    # \\VUgras — one per line — and the naive conversion made two tags of
    # them: « <b>ar</b><b>moro</b> », that is « armoro » to the eye but two
    # words to the browser's search, which no longer found « armoro ». We
    # therefore glue adjoining tags back together. Two cross-reference
    # calls separated by the break — « (9, 11, » and « 12) » — are the same
    # cross-reference, and are reunited likewise, with the space added.
    # The rule holds for ADJOINING tags only. In its first version it
    # tolerated the space between the two — and « une \\VUgras{armoire}\\nl
    # \\VUgras{vitree} », two bold words on two lines of the French
    # facsimile, became « armoirevitree ». The space distinguishes the two
    # cases: \\cc leaves none, \\nl does.
    for b in ("b", "i"):
        t = re.sub(rf"</{b}><{b}>", "", t)
    t = re.sub(r"<b>([^<>]*)</b>",
               lambda m: (m.group(1)
                          if m.group(1).strip(PONKTO).lower() in MOTOJ_VAKA
                          else m.group(0)), t)
    # The cross-references, for their part, are reunited EVEN when
    # separated: « (9, 11, » and « 12) » are a single call the line has cut
    # in two.
    t = re.sub(r"</sup>\s*<sup>", " ", t)

    # THE HYPHEN HAS NO SPACES. The titles of the Ido booklet are set with
    # letterspacing, and the printer let the hyphen breathe like the rest:
    # « EXPLIKO - LIBRETO », « Matur - evo ed oldeso. », « la Delmas -
    # tabeli », « la 3 - ma ». Those spaces belong to the composition, not
    # to the word; on screen, where nothing is letterspaced, they cut the
    # word in two. The French facsimile carries none. The em dash, which
    # really does separate, is written « --- » in the transcription and
    # already comes out as « — »: neither it nor the short dash of an
    # interval is touched.
    t = re.sub(r"(?<=[^\s\u2013\u2014-]) - (?=[^\s\u2013\u2014-])", "-", t)

    # A LANGUAGE WITHOUT SPACES WANTS NONE FROM THE END OF A LINE. The
    # translation files break their lines for the comfort of whoever edits
    # them, and \nl / the plain return become a space -- which is what the
    # Latin languages need, where the space separates the words. Chinese
    # puts none: « 有八张\n课桌 » came out « 有八张 课桌 », a hole in the
    # middle of the group, and 848 times in the column. A space set BETWEEN
    # TWO IDEOGRAMS is never intended -- no language writes any -- and it
    # is therefore taken out everywhere, whatever the column. The rule is
    # laid on the HTML and not on the bare text: two neighbouring display
    # lines are separated by their tags, and that space must stay.
    # AND THE BOLD DOES NOT BREAK THE GROUP. « 有八张\n\VUgras{课桌} » puts
    # a tag between the two ideograms, and the first version of the rule no
    # longer saw them as neighbours: 403 holes out of 848 remained. We
    # therefore skip the INLINE tags -- b, i, sup, button -- but not
    # « span », which is that of the display lines: two neighbouring title
    # lines are indeed separated by a space, and that one must stay.
    _EL = r"(?:</?(?:b|i|sup|button)\b[^>]*>)*"
    _ID = "[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]"
    t = re.sub(rf"(?<={_ID})({_EL})[ \t\n]+({_EL})(?={_ID})", r"\1\2", t)

    # The apostrophe of both facsimiles is the curved one, not the
    # straight: « l'unesma », « L'Ecole ». The straight one is a keyboard
    # convenience the printed page does not know.
    t = t.replace("'", "\u2019")

    # Punctuation of the facsimile.
    t = t.replace("---", "\u2014").replace("--", "\u2013")
    t = re.sub(r"\s+", " ", t).strip()
    # The em dash sticks to the word that follows when the compositor
    # tightens his line (« 3. ---Ne omna... », folio 5). It is a
    # constraint of justification, not an intention: the reading page,
    # which rejustifies, gives the space back. The PDF, for its part,
    # keeps the facsimile.
    t = re.sub(r"\u2014(?=[^\s\u2014])", "\u2014 ", t)
    # Thin non-breaking space before high punctuation, French and Ido
    # usage of the period — both booklets set it.
    t = re.sub(r" ([;:?!])", "\u202f\\1", t)
    t = t.replace("<b> ", " <b>").replace(" </b>", "</b> ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def lire(chemin):
    """Returns the list of blocks of a transcription file.

    A block = {key, type, folio, leaf, html}. Everything preceding a
    page's first key (the display lines of a table's opening, the
    notes) is attached to the block that follows or carries its own
    key.
    """
    src = chemin.read_text(encoding="utf-8")
    blocs = []
    folio = ""
    feuillet = ""
    courant = None
    notes = []
    dans_note = False
    accolades = 0
    for ligne in src.splitlines():
        mp = PAGE.search(ligne)
        if mp:
            feuillet = mp.group(1) or ""
            folio = mp.group(2) or ""
            continue
        m = CLE.match(ligne.strip())
        if m:
            if courant:
                blocs.append(courant)
            # The third member of a key: « suite » for the resumption of a
            # paragraph broken by a change of page, « pos=<key> » for a
            # block that IS READ elsewhere than it is printed.
            extra = m.group(3) or ""
            courant = {"cle": m.group(1), "tipo": m.group(2),
                       "suite": extra == "suite",
                       "apres": extra[4:] if extra.startswith("pos=") else "",
                       "folio": folio, "feuillet": feuillet, "brut": []}
            continue
        if ligne.startswith("%"):
            continue
        if "\\end{VUpage}" in ligne:
            # The end of an environment is not text. Without this very
            # line, « VUpage » was set at the end of each page's last
            # paragraph: the unknown macro dropped, its name stayed.
            courant = None if courant is None else courant
            if courant is not None:
                courant["brut"].append(
                    ligne.replace("\\end{VUpage}", ""))
            continue
        if courant is not None:
            courant["brut"].append(ligne)
        elif ligne.strip().startswith("\\VUnotes"):
            notes.append(ligne)
    if courant:
        blocs.append(courant)

    # The notes: they are declared at the head of the page, before any
    # key. We find them again in the raw source, extract them and make
    # separate blocks of them, set at the end of their page.
    entier = src
    for mo in re.finditer(r"\\VUnotes\{[^}]*\}\{", entier):
        deb = mo.end() - 1
        dedans, _ = accolade(entier, deb)
        # Which page does it belong to? The last \begin{VUpage}
        # before it.
        avant = entier[:mo.start()]
        pages = list(PAGE.finditer(avant))
        f = pages[-1].group(2) if pages else ""
        fe = pages[-1].group(1) if pages else ""
        blocs.append({"cle": f"noto-f{fe}", "tipo": "noto", "suite": False,
                      "folio": f, "feuillet": fe,
                      "brut": [dedans]})


    for b in blocs:
        b["html"] = texte_html("\n".join(b["brut"]))
        del b["brut"]
    # THE MARKER IS READ ON THE RENDERED TEXT, not on the source. There it
    # is sometimes shut inside a macro — « \textit{(*) Pro ke ta vorto...} »
    # on table 8 — and a regular expression laid on the LaTeX did not see
    # it. The HTML, for its part, has already resolved the macros: only the
    # text is left, and the marker is at its head.
    for b in blocs:
        if b["tipo"] != "noto":
            b["apelo"] = ""
            continue
        nu = re.sub(r"<[^>]+>", "", b["html"]).strip()
        m2 = re.match(r"\(([^)]{1,3})\)", nu)
        b["apelo"] = m2.group(1) if m2 else ""

    # TWO SOURCES FOR ONE NOTE. Some transcriptions declare the note by
    # a « %%K ... noto » key, others let it be carried by \VUnotes alone,
    # which the second pass above gathers up. When the two coexist, the
    # note appeared twice. We discard the duplicate on the first
    # characters of the bare text.
    vus = set()
    net = []
    for b in blocs:
        if b["tipo"] == "noto":
            empreinte = re.sub(r"<[^>]+>|\s+", "", b["html"])[:40]
            if empreinte in vus:
                continue
            vus.add(empreinte)
        net.append(b)
    return [b for b in net if b["html"]]


def fusionner(blocs):
    """Glues « suite » blocks back to the block they came from.

    A paragraph broken by a change of page carries the same key twice,
    the second marked « suite ». In the PDF they are two pages; in the
    reading page it is one paragraph, and it must be, or the facing
    column — which does not break in the same place — would no longer
    answer it.
    """
    out = []
    par_cle = {}
    for b in blocs:
        if b["suite"] and b["cle"] in par_cle:
            a = par_cle[b["cle"]]
            # A WORD BROKEN BY THE PAGE TAKES NO SPACE. \ccplein has
            # left its mark at the end of the left-hand half: « dro »
            # and « medaro » make « dromedaro », not « dro medaro ».
            if a["html"].rstrip().endswith(COUPE):
                joint = (a["html"].rstrip()[:-len(COUPE)]
                         + b["html"].lstrip()).strip()
                # AND IT REMAINS ONE WORD FOR SEARCHING. The two halves
                # are each in their own \VUgras: glued back as they
                # stood, they gave « <b>dro</b><b>meda ro</b> » —
                # « dromedaro » to the eye, two words to the browser.
                # texte_html() reunites adjoining tags within a block;
                # here the break falls between two blocks, and the
                # reunion is done again afterwards.
                for q in ("b", "i"):
                    joint = joint.replace(f"</{q}><{q}>", "")
                a["html"] = joint
            else:
                a["html"] = (a["html"] + " " + b["html"]).strip()
            a["folio2"] = b["folio"]
            continue
        par_cle[b["cle"]] = b
        out.append(b)
    return out


# -------------------------------------------------------------------
#  2. ASSEMBLY
# -------------------------------------------------------------------
DOSSIER = {"fr": "fr", "fr-CA": "fr-CA",
           "en": "en", "es": "es", "ru": "ru", "zh": "zh",
           "ar": "ar", "hi": "hi", "pt": "pt",
           "bn": "bn", "ja": "ja", "pnb": "pnb", "pa": "pa",
           "tr": "tr", "eo": "eo", "ia": "ia",
           "nl": "nl", "sv": "sv", "fi": "fi", "ca": "ca",
           "oc": "oc", "uk": "uk",
           "eu": "eu", "ro": "ro",
           "ga": "ga", "gl": "gl",
           "cs": "cs", "lt": "lt",
           "lb": "lb", "rm": "rm",
           "et": "et", "vi": "vi", "yue": "yue", "arz": "arz",
           "mr": "mr",
           "te": "te", "ko": "ko", "ta": "ta", "ur": "ur",
           "id": "id", "jv": "jv", "fa": "fa", "ha": "ha",
           "gu": "gu", "apc": "apc", "bho": "bho",
           "de": "de", "it": "it",
           "pl": "pl", "af": "af"}   # language -> text/<...>


# THE READING PAGE CARRIES ONLY THE SIXTEEN TABLES. Cover,
# dedication, PREFACO, AVERTISSEMENT, tables of contents, the
# publisher's announcements: all of that is in the two PDFs, which
# reproduce the whole volumes, and has no business in a page whose
# object is to set TWO TEXTS FACE TO FACE. Those pieces do not answer
# each other from one edition to the other -- Guignon's preface is not
# Rochelle's avertissement, it is even its opposite in tone -- and
# displaying them side by side gave two columns looking at each other
# with nothing to say.
#
# The division is read off the filename: « 00- » the front matter,
# « 90- » the end, and between the two the tables.
# « pos= »: WHAT IS PRINTED HERE IS READ THERE. The facsimile
# sometimes sets a subheading in a place the reading page cannot keep.
# On table 2, « LA KAPO. » is printed BEFORE paragraph 1 -- which is
# not the head, but the announcement of the body's three parts -- and
# the French volume puts there, for its part, the section title « I. Le
# Corps Humain. ». The two columns therefore announced different
# things.
#
# Moving the macro in the transcription would correct the reading page
# and FALSIFY THE PDF, which is the diplomatic transcription: the line
# must stay where the printer put it. We therefore note the move beside
# it, and the PDF does not budge by a point.
def deplacer(blocs):
    """Sets the blocks marked « pos= » back behind the block they aim at."""
    fixes = [b for b in blocs if not b.get("apres")]
    for b in [b for b in blocs if b.get("apres")]:
        i = next((k for k, x in enumerate(fixes) if x["cle"] == b["apres"]),
                 None)
        if i is None:
            raise SystemExit(f'%%K {b["cle"]} : pos={b["apres"]} introuvable')
        fixes.insert(i + 1, b)
    return fixes


def lire_langue(sous_dossier):
    """The sixteen tables of a language, in order."""
    d = RACINE / "text" / sous_dossier
    blocs = []
    for f in sorted(d.glob("*.tex")):
        if f.name.startswith(("00-", "90-")):
            continue
        blocs.extend(deplacer(fusionner(lire(f))))
    return blocs


# SUBHEADINGS ARE NOT PAIRED BY THEIR KEY. That is already the rule of
# the transcription, and tools/checks.py says so: « their numbering
# (tit-1, tit-2...) is peculiar to each edition ». The Ido subdivides
# more finely than the French -- seven subheadings on table 2 against
# three -- so that t02-tit-2 does not designate the same thing on both
# sides. The rendering, for its part, paired everything by the key:
# « La Torso. » found itself facing « II. La Gymnastique. », and the two
# columns announced different sections. Seventeen subheadings were
# mispaired that way, across eleven tables.
#
# WHAT PAIRS THEM IS THE PLACE. A subheading opens a paragraph, and the
# paragraph carries the same key in both editions -- that is the pivot
# of the transcription. We therefore group the subheadings by the
# paragraph they precede, and pair them IN ORDER within the group:
# where one edition puts three and the other two, the first two answer
# each other and the third stays alone. As it must.
def apparier_subs(io_blocs, autre_blocs):
    """{Ido subheading key: subheading key of the other edition}"""
    def groupes(blocs):
        g, courant = {}, []
        for b in blocs:
            if b["tipo"] == "sub":
                courant.append(b["cle"])
            elif b["tipo"] == "p" and courant:
                # Paragraph keys carry their table: two groups from two
                # tables cannot be confused.
                g[b["cle"]] = courant
                courant = []
        return g

    ici, la = groupes(io_blocs), groupes(autre_blocs)
    lien = {}
    for alinea, subs_io in ici.items():
        subs_la = la.get(alinea, [])
        for i, cle in enumerate(subs_io):
            if i < len(subs_la):
                lien[cle] = subs_la[i]
    return lien


# THE SUBHEADINGS THE FRENCH BOOKLET DOES NOT HAVE. Rochelle cuts his
# tables into two or three sections, Guignon puts seven: a hundred and
# twenty-eight subheadings on one side, thirty on the other, and
# ninety-eight ranks where the French column stayed empty. The six
# modern translations all have them, translated from the Ido; the
# French could not take them by the same route, text/fr being a
# transcription and not a translation — the PDF reproduces its
# facsimile there, one line for one line, and one more line would
# falsify it.
#
# THEY ARE THEREFORE KEPT ALONGSIDE, in text/fr/intertitroj.json, and
# only the reading page displays them. It marks them « apud »: the same
# size and the same place as the others, but the reader must be able to
# tell what Rochelle wrote from what we add.
def intertitroj_fr():
    f = RACINE / "text" / "fr" / "intertitroj.json"
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(f.read_text(encoding="utf-8")).items()
            if not k.startswith("_")}


APUD_FR = intertitroj_fr()


def paro():
    io = lire_langue("io")
    autres, liens = {}, {}
    for lg in LANGUES:
        # THE VARIANT HAS NO DIRECTORY: it is drawn from its base, below,
        # once the blocks are made. « dosiero » says where the base column
        # writes its files, its own code having taken a suffix.
        sd = DOSSIER.get(lg.get("dosiero", lg["kodo"]))
        if sd and (RACINE / "text" / sd).is_dir():
            bl = lire_langue(sd)
            autres[lg["kodo"]] = {b["cle"]: b for b in bl}
            liens[lg["kodo"]] = apparier_subs(io, bl)
        else:
            autres[lg["kodo"]] = {}
            liens[lg["kodo"]] = {}

    # THE ORDER IS THE IDO'S. It is the Ido booklet that is the object of
    # the site; the right-hand column follows it.
    # On the Ido side, the symmetry: an Ido block with no French
    # counterpart is glued back to the previous one AT RENDERING TIME (see
    # below), and not here, because one must first know which are orphans.
    rangi = []
    for b in io:
        r = {"cle": b["cle"], "tipo": b["tipo"], "io": b["html"],
             "apelo": b.get("apelo", ""),
             "folio": b["folio"], "folio2": b.get("folio2", ""),
             "feuillet": b["feuillet"], "tra": {}}
        for lg in LANGUES:
            # The subheading is looked up by its place, everything else by
            # its key. With no counterpart, the right-hand cell stays
            # empty: it is a subdivision the other edition does not have.
            cible = (liens[lg["kodo"]].get(b["cle"]) if b["tipo"] == "sub"
                     else b["cle"])
            o = autres[lg["kodo"]].get(cible) if cible else None
            if o is None and lg["kodo"] == "fr" and b["tipo"] == "sub":
                # THE SIZE IS TAKEN FROM THE IDO, so that the two
                # columns announce the section at the same strength.
                t = APUD_FR.get(b["cle"])
                if t:
                    korpo = re.search(r'data-korpo="([^"]+)"', b["html"])
                    o = {"html": (f'<span class="apud" data-korpo='
                                  f'"{korpo.group(1) if korpo else "10.2pt"}" '
                                  f'title="Intertitre absent du Livret '
                                  f'français ; traduit de l\u2019ido">'
                                  f'{t}</span>'),
                         "folio": "", "feuillet": ""}
            if o:
                r["tra"][lg["kodo"]] = {"t": o["html"], "f": o["folio"],
                                        "f2": o.get("folio2", ""),
                                        "fe": o["feuillet"],
                                        "apelo": o.get("apelo", "")}
        rangi.append(r)

    # THE DIVISION INTO PARAGRAPHS IS NOT THE SAME ON THE TWO SIDES, and
    # something must be made of it. Rochelle sometimes cuts in two a
    # paragraph Guignon leaves whole, or the reverse: the key
    # « t07-c1-05-2 » then exists on one side only. Rendered as it stands,
    # it makes a row one of whose columns is empty, and the eye reads a
    # gap there -- when the text is in fact right there, two lines above.
    #
    # THE PDF KEEPS THE FACSIMILE; THE READING PAGE REGROUPS. The volume
    # is a diplomatic transcription and must remain one: the paragraph
    # break there is that of the printed page. The reading page, for its
    # part, serves to COMPARE two texts, and a comparison wants rows that
    # answer each other. We therefore glue the orphan block back to the
    # previous one of the same language, with the mark of the line break
    # it carried -- nothing is lost, nothing is moved, and the two columns
    # become parallel again.
    #
    # A SUBHEADING PAIRED BY ITS PLACE IS NOT AN ORPHAN. This gluing judges
    # on the KEY, and subheadings are paired on their place: a translation
    # subheading whose key does not appear on the Ido side already holds
    # its cell all the same, facing the one it translates. Counted as an
    # orphan, it appeared TWICE -- « Deuxième scène. » at its rank, and
    # glued to the end of the previous paragraph.
    par_cle = {r["cle"]: i for i, r in enumerate(rangi)}
    for lg in LANGUES:
        k = lg["kodo"]
        pris = {tra: io for io, tra in liens[k].items()}
        precedent = None
        for cle, o in autres[k].items():
            if cle in par_cle:
                precedent = par_cle[cle]
                continue
            if cle in pris:
                # It has its cell: from now on it is the previous one.
                precedent = par_cle.get(pris[cle], precedent)
                continue
            if precedent is None:
                continue
            cible = rangi[precedent]["tra"].get(k)
            if cible is None:
                continue
            cible["t"] = (cible["t"] + ' <span class="nal"></span> '
                          + o["html"])
    return rangi


# THE FOLIO DOES NOT GIVE THE PDF'S PAGE NUMBER, and the difference is
# not a constant. The PDF sets only the transcribed leaves, and the Ido
# booklet skips two, blank (48 and 76). A fixed subtraction -- what was
# done when table 1 alone existed -- therefore sent the reader two
# pages too far through the whole second third of the volume. We number
# the composed leaves in order, once.
_RANGS = {}


def rang_pdf(langue, feuillet):
    sd = "io" if langue == "io" else DOSSIER.get(langue, langue)
    if sd not in _RANGS:
        table = {}
        for f in sorted((RACINE / "text" / sd).glob("*.tex")):
            for m in PAGE.finditer(f.read_text(encoding="utf-8")):
                if m.group(1):
                    table[m.group(1)] = len(table) + 1
        _RANGS[sd] = table
    return _RANGS[sd].get(str(feuillet), 1)


# WHAT PRECEDES A FIGURE IN PARENTHESES SAYS WHAT IT IS. The French
# foreword lays down the rule itself: « Nous avons imprime en
# caracteres gras les substantifs qui se trouvent dans le vocabulaire
# des Tableaux EN LES FAISANT SUIVRE DE LEUR NUMERO. » An object number
# therefore always follows a bold noun -- « la
# \VUgras{fumee}\textsuperscript{(1)} » -- whereas a note call follows
# ordinary text: « qui nous fut servi \textsuperscript{(1)} ». The
# superscript settles nothing: both volumes set now one, now the other
# as a superscript.
AVANT_OBJET = re.compile(r'</b>\s*(?:<sup>\s*)?$')


def appels_note(texte, marque):
    """Positions of the note calls « (mark) » within a block.

    Discards cross-references to the wall plate, recognised by their
    bold noun. Returns pairs (start, end) on the given text.
    """
    if not texte:
        return []
    # AN ASTERISK IS NEVER AN OBJECT NUMBER: when the note is marked
    # « (*) », there is nothing to decide between, and the bold proves
    # nothing. Ido table 1 sets its call precisely after a bold noun —
    # « esas \VUgras{Henrikus} (*) » — because the note bears on that
    # word. The bold rule holds only for the figured marks, the only
    # ones the two uses share.
    chiffree = marque.isdigit()
    out = []
    for m in re.finditer(re.escape(f"({marque})"), texte):
        if chiffree and AVANT_OBJET.search(texte[:m.start()]):
            continue
        out.append((m.start(), m.end()))
    return out


def ancro(cle):
    return cle


def lier_notes(rangi):
    """Links each note call, in the text, to its note.

    A NOTE IS NOT A BLOCK LIKE ANY OTHER. At the foot of a page of the
    facsimile it has its natural place; in a scrolling column, set
    between two paragraphs, it breaks the reading — and the call, for
    its part, leads nowhere. We therefore fold it away: the call becomes
    a button, the note opens beneath the paragraph that carries it, as
    in the page of the « Kompleta Gramatiko ».

    EACH LANGUAGE HAS ITS NOTES, and they are rarely the same ones: the
    Ido booklet carries a note on the latinisation of first names that
    the French does not have, and Rochelle has some Guignon did not take
    up. We therefore link column by column.

    THE PAIRING IS DONE BY THE PAGE AND BY THE MARKER, both. A note's
    « (1) » and a wall-plate cross-reference's « (1) » are written
    alike; only the page distinguishes them, since the note is at the
    foot of the page where its call is found. When the marker appears
    several times on the same page, we link NOTHING rather than link at
    random: the function says so, and the eye decides.
    """
    rapport = {"lies": 0, "echecs": []}

    def relier(notes, lire_texte, ecrire_texte, page_de, langue):
        # SEVERAL NOTES ON ONE PAGE, ALL MARKED « (*) ». Folio 37 of the
        # Ido booklet carries two. The marker does not distinguish them —
        # but the ORDER does: the page's first call refers to the first
        # note, the second to the second, and that is how the reader of
        # 1926 read them. We therefore count, for each note, its rank among
        # those of its page.
        # THE RANK IS COUNTED ON THE PAGE AND THE MARKER, nothing more.
        # « page_de » serves to read the page of a ROW of the table, not of
        # a note: for the right-hand column it goes looking for r["tra"],
        # which the notes do not have. It stood here at the head of
        # « cle_page », only the last two members of which are read -- a
        # dead call, but one that raised KeyError as soon as a translation
        # note presented itself. None ever did, for want of a paired key;
        # the first one brought it down.
        # A TRANSLATION HAS NO PAGES. The French and the Ido are
        # transcribed facsimiles: each block knows which leaf it comes
        # from, and it is the leaf that brings a note close to its call.
        # The English transcribes nothing -- it has neither page nor leaf,
        # and all its blocks therefore carried the same empty page: the
        # eleven notes looked for a call in the whole book, and quarrelled
        # over it. THE TABLE THEN REPLACES THE PAGE. It is wider than a
        # leaf, but it is enough: no table carries more than two notes, and
        # the counting of ranks, which already parted two notes of one
        # page, parts them likewise.
        def zono(n):
            return (n.get("feuillet") or "").strip() or n["cle"][:3]

        rang = {}
        for n in notes:
            cle_page = (zono(n), n.get("apelo"))
            rang[id(n)] = rang.get(cle_page, 0)
            rang[cle_page] = rang.get(cle_page, 0) + 1
        for n in notes:
            marque = (n.get("apelo") or "").strip()
            if not marque:
                rapport["echecs"].append(
                    (langue, n["cle"], "?", "marqueur illisible en tete"))
                continue
            # A NOTE'S « (1) » AND AN OBJECT'S « (1) » ARE WRITTEN ALIKE.
            # Rochelle marks his notes with the same sign as his object
            # numbers, which run to 150 a plate. On table 13, the paragraph
            # « au deuxieme etage (1), ou j'ai tres bien dormi (1) » carries
            # both, and we linked the first: the button opened on the floor.
            # It is the bold that separates them (see appels_note).
            # THE CALL MAY BE ON THE PREVIOUS PAGE. A paragraph straddling two
            # pages begins on the verso and its note falls at the foot of the
            # recto: the transcription merges the two halves into a single
            # block, which then carries the leaf of its FIRST page. We
            # therefore accept the note's page and the one before it.
            # ITS OWN PAGE FIRST, THE PREVIOUS ONE AFTER, and never the two
            # together. Each page has its own note and its own « (*) »:
            # searching two pages at once therefore returned two calls for one
            # note, and the tool gave up linking what was not ambiguous at
            # all.
            reperer = page_de
            try:
                f = int(n["feuillet"])
                essais = [{str(f)}, {str(f - 1)}]
            except (TypeError, ValueError):
                essais = [{zono(n)}]
                reperer = lambda r: r["cle"][:3]
            cands, total = [], 0
            for pages in essais:
                cands = [r for r in rangi
                         # « apar » too: on table 8, the call is in the very
                         # title of the scene, « La Rekolto (*) », which holds
                         # on the opening page.
                         if r["tipo"] in ("p", "sub", "apar")
                         and reperer(r) in pages
                         and lire_texte(r) is not None]
                total = sum(len(appels_note(lire_texte(r), marque))
                            for r in cands)
                if total:
                    break
            vise = rang.get(id(n), 0)      # the rank of this particular note
            if total == 0 or vise >= total:
                rapport["echecs"].append(
                    (langue, n["cle"], marque,
                     "aucun appel sur la page" if total == 0
                     else f"{total} appels pour {vise + 1} notes"))
                continue
            vu = 0
            for r in cands:
                t = lire_texte(r)
                places = appels_note(t, marque)
                if vu + len(places) <= vise:
                    vu += len(places)
                    continue
                # The call sought is the (aimed - seen)-th of this block.
                a, b = places[vise - vu]
                # ONE SIGN FOR ALL THE NOTES. Guignon marks his « (*) »,
                # Rochelle « (1) ». To keep each his own mark was to give two
                # different signs to the same note set face to face, and above
                # all to take up in French the sign of the wall-plate
                # cross-references. The reading page therefore marks every note
                # « (*) », the sign the Ido already used everywhere; the PDFs,
                # for their part, keep what each workshop composed.
                bouton = (f'<button class="apel" '
                          f'data-noto="{langue}-{n["cle"]}" '
                          f'aria-expanded="false">(*)</button>')
                ecrire_texte(r, t[:a] + bouton + t[b:])
                n["porte"] = r["cle"]
                n["langue"] = langue
                rapport["lies"] += 1
                break

    # Left-hand column.
    relier([r for r in rangi if r["tipo"] == "noto"],
           lambda r: r["io"],
           lambda r, v: r.__setitem__("io", v),
           lambda r: r["feuillet"], "io")

    # Right-hand columns: their notes are not in `rangi`, they have
    # stayed in the translation blocks. We draw them out of them.
    for lg in LANGUES:
        k = lg["kodo"]
        notes = []
        for r in rangi:
            o = r["tra"].get(k)
            if o and o.get("apelo") and r["tipo"] == "noto":
                notes.append({"cle": r["cle"], "apelo": o["apelo"],
                              "feuillet": o["fe"], "html": o["t"]})
        relier(notes,
               lambda r, k=k: (r["tra"].get(k) or {}).get("t"),
               lambda r, v, k=k: r["tra"][k].__setitem__("t", v),
               lambda r, k=k: (r["tra"].get(k) or {}).get("fe"), k)

    uniformiser_notes(rangi)
    uniformiser_renvois(rangi)
    rapport["fermes"] = fermer_renvois(rangi)
    rapport["korektiti"] = korekti_teksto(rangi)
    boutons_renvois(rangi)
    boutons_literi(rangi)
    # AFTER THE BUTTONS, AND NOT BEFORE: the close-up's name is set in
    # the button's « title », and it carried the glued-together word.
    rapport["tratiti"] = retablir_trati(rangi)
    rapport["korektiti"] += korekti_nomi(rangi)
    # LAST, AND DELIBERATELY SO: the variant is drawn from the FINISHED
    # text, once the cross-references are closed, the corrections laid, the
    # hyphens restored and the buttons composed. It therefore inherits
    # everything, and the close-up's name follows the word of its own
    # edition — « vest » and not « waistcoat » when one is reading the
    # English of the United States.
    return rapport


# THE WALL-PLATE CROSS-REFERENCE, ALWAYS SET THE SAME WAY.
# We take the number with what carries it -- the superscript if it has
# one -- and the space before it if there is one.
# THREE FORMS OF CROSS-REFERENCE, and all three were needed: the
# ordinary form, the GROUP — « les tableaux muraux (9, 11, 12) », which
# stands for three objects at once and of which we read none — and
# « 41) », where the opening parenthesis is missing, in three places
# across the two booklets. We keep the parentheses AS WE TRANSCRIBED
# THEM: to say whether that 41) comes from a slip in the transcription
# or from a broken sort at the printer's would call for the facsimile
# before one's eyes. We make the superscript and the space uniform,
# nothing else.
RENVOI = re.compile(
    r'(\s*)'
    r'(?:<sup>\s*(\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*\)?)\s*</sup>'
    r'|\((\d{1,3}(?:\s*,\s*\d{1,3})*)\))')


def boutons_renvois(rangi):
    """The cross-reference becomes a button when we know where it points.

    A CLOSE-UP WE WOULD NOT KNOW HOW TO SHOW IS NOT PROMISED. The
    reading of the numbers on the plates is partial -- the reserve of
    white that carries the figure closes up as soon as the engraving is
    dense, and the figure is lost in the hatching. Cross-references
    whose position is known therefore take a button; the others stay
    ordinary text, exactly as they were. Nothing moves in the line: the
    button keeps the size and the superscript of the cross-reference.

    The button carries the ENGRAVING'S KEY and the frame as fractions of
    it. The page has then only to re-frame the image it already has.
    """
    num = numeri()
    if not num:
        return 0
    pose = 0
    for r in rangi:
        tab = r["cle"][:3]
        par = num.get(tab)
        if not par:
            continue
        # THE BLOCK'S SCENE DECIDES WHICH NUMBER IT IS. Six plates carry
        # several vignettes, and each starts again at 1: the « (39) » of a
        # t06-c3 block does not show the same object as that of a t06-c1
        # block. The block's key says so.
        ms = re.match(r't\d\d-(c\d)-', r["cle"])
        scene = ms.group(1) if ms else ""
        # The cross-reference the plate does not carry: on table 5 the
        # « (150) » of the flower beds, engraved « 50 ». We read the
        # correction, we show it, and the source does not move.
        kor = korekti_renvojo(tab, r["cle"])

        def ouvrir(n, langue, nu):
            """The start of a number's button, or None if we do not know
            where it is: we do not promise a close-up we would not know
            how to show."""
            v = par.get(f"{scene}:{n}" if scene else str(n))
            # TABLE 11 HAS ONLY ONE NUMBERING, BUT ITS KEYS CARRY TWO
            # SCENES — AND IT LOST ITS EIGHTY-EIGHT CLOSE-UPS FOR ALL
            # THAT TIME, ACROSS THE 42 COLUMNS. Its keys say c1 and c2
            # because the NUMBERING OF THE PARAGRAPHS starts again from
            # 1 at « L'Incendio »; the cross-references, for their part,
            # continue the same series — the first part runs from 1 to
            # 43, the second from 44 to 96. plates/numbers.json knows it
            # and therefore files plate 11 under bare numbers, like the
            # plates with a single scene. The lookup « c2:46 » found
            # nothing, no button was set, and nothing cried out:
            # ouvrir() returns None without complaining, by
            # construction. We therefore fall back on the bare number.
            #
            # It is safe: transcription made, no plate mixes the two
            # forms — the numbers of a table are either all prefixed by
            # their scene (3, 4, 6, 7, 8, 9) or all bare (1, 2, 5, 10,
            # 11, 12 to 16). A table with genuine scenes therefore has
            # no bare entry to offer this fallback, and the fallback
            # cannot show the wrong object there.
            if not v and scene:
                v = par.get(str(n))
            if not v:
                return None
            cle, x, y, w, h, nm = v
            # THE NAME FOLLOWS ITS COLUMN (see nomo, above).
            titre = nomo(nm, langue).replace('"', "&quot;")
            return (f'<button class="lupo{chr(32) + "nuda" if nu else ""}" '
                    f'data-g="{cle}" data-c="{x},{y},{w},{h}" data-n="{n}" '
                    f'title="{titre}" aria-expanded="false">')

        def bouton(m, par=par, langue="io", scene=scene):
            nonlocal pose
            ouv, corps, bis, fer = (m.group(1), m.group(2),
                                    m.group(3) or "", m.group(4))
            ns = [int(kor.get(x, x)) for x in re.findall(r"\d+", corps)]
            # A GROUP STANDS FOR SEVERAL OBJECTS AT ONCE. Each number in
            # it becomes clickable separately; the parentheses and the
            # commas stay text, and nothing moves in the line.
            if len(ns) > 1:
                bouts, fait = [], 0
                for n in ns:
                    d = ouvrir(n, langue, True)
                    bouts.append(f"{d}{n}</button>" if d else str(n))
                    fait += 1 if d else 0
                if not fait:
                    return m.group(0)
                pose += fait
                return f"<sup>{ouv}" + ", ".join(bouts) + f"{bis}{fer}</sup>"
            d = ouvrir(f"{ns[0]}bis" if bis else ns[0], langue, False)
            if not d:
                return m.group(0)
            pose += 1
            return f"{d}<sup>{ouv}{ns[0]}{bis}{fer}</sup></button>"

        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            texte = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not texte:
                continue
            neuf = RENVOI_REND.sub(
                lambda m, k=k: bouton(m, langue=k), texte)
            if neuf == texte:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return pose


# -------------------------------------------------------------------
#  CROSS-REFERENCES BY LETTER
# -------------------------------------------------------------------
#  Three tables are not content with numbers. « Ni vidas sur la tabelo
#  la precipua figuri geometriala: rondo (a), quadrato (b) » — those
#  letters are engraved ON the blackboard, which itself carries the
#  number 1, and mean nothing except in relation to it: the « a » of the
#  blackboard is a circle, that of the map America, that of the natural
#  sciences chart a horse.
#
#  plates/letters.json says, block by block, which object the letters
#  depend on — that cannot be guessed, the text not always saying so —
#  and where each is to be found on the plate.
# THE CROSS-REFERENCE BY LETTER IS SET IN ITALIC ON THE FRENCH SIDE,
# and bare on the Ido side. Without that italic in the pattern, the six
# letters of the astronomy table were clickable only in Ido: the reader
# of the French read « les hemispheres (d) » without being able to see
# anything of it.
RENVOI_LIT = re.compile(r'<sup>(<i>)?\(([a-z]{1,2})\)(</i>)?</sup>')


def literi():
    """{plate: {key: place}} and the table of blocks."""
    f = RACINE / "plates" / "letters.json"
    if not f.exists():
        return {}, {}
    d = json.loads(f.read_text(encoding="utf-8"))
    return d, d.get("patri", {})


# ONE FATE FOR TWO SIGNS. On table 5, the bathroom carries a
# cross-reference set as « (1) » — in both booklets. It is not the
# number 1, which is the front of the house: it is the LETTER l, and
# the plan says so itself, its legend reading « l. Balneyo » between the
# k of the children and the m of the landing. In this font the
# lower-case l and the figure 1 have the same design, and the
# compositor's case perhaps held only one of the two: nothing on the
# page separates them.
#
# THE SOURCE DOES NOT MOVE — the two PDFs remain the facsimile — but
# the reading page has no business repeating an ambiguity the plan
# resolves. We therefore read « (l) » there, and the close-up shows the
# bathroom. It is the only place in the book where the reading page
# corrects what the transcription preserves, and that is why it is
# declared in letters.json rather than guessed.
BOUTON_UN = re.compile(
    r'<button class="lupo" data-g="[^"]*" data-c="[^"]*" data-n="1" '
    r'title="[^"]*" aria-expanded="false"><sup>\(1\)</sup></button>')


def sorto_unika(t, regles, planche, places, noms, langue):
    """Redirects to its letter the « (1) » that is not a number."""
    for mot, L in regles:
        i = t.find(f"{mot}</b>")
        v = places.get(L)
        if i < 0 or not v:
            continue
        m = BOUTON_UN.search(t, i, i + 400)
        if not m:
            continue
        nm = noms.get(planche[:3], {}).get(L, {})
        io = (nm.get("io") or nm.get("fr") or [""])[0]
        fr = (nm.get("fr") or nm.get("io") or [""])[0]
        titre = ((io if langue == "io" else fr) or io or fr)
        t = t[:m.start()] + (
            f'<button class="lupo" data-g="{planche}" '
            f'data-c="{v[0]},{v[1]},{v[2]},{v[3]}" data-n="{L}" '
            f'title="{titre.replace(chr(34), "&quot;")}" '
            f'aria-expanded="false"><sup>({L})</sup></button>'
        ) + t[m.end():]
    return t


def boutons_literi(rangi):
    """The cross-reference by letter becomes a button, like the one by number."""
    tout, patri = literi()
    if not patri:
        return 0
    uniq = tout.get("unu-sorto", {})
    o = RACINE / "plates" / "objects.json"
    noms = json.loads(o.read_text(encoding="utf-8")) if o.exists() else {}
    pose = 0
    for r in rangi:
        pa = patri.get(r["cle"])
        if not pa:
            continue
        planche, prefixo = pa
        places = tout.get(planche, {})
        # A LETTER TOO MAY BE WRONG. On table 1 the two booklets swap
        # Europe and Asia; plates/corrections.json says so for that
        # block. The corrected letter is the one looked for on the plate
        # AND the one written: the reading page does not repeat an error
        # the engraving belies.
        # THE READING IS DONE IN A SINGLE PASS — each letter is taken
        # from the original table — failing which the swap « g reads e,
        # e reads g » would undo itself at the second.
        kor = korekti_renvojo(r["cle"][:3], r["cle"])

        def bouton(m, langue="io"):
            nonlocal pose
            bouts, fait = [], 0
            ita = "<i>" if m.group(1) else ""
            for brut in m.group(2):
                L = kor.get(brut, brut)
                v = places.get(prefixo + L)
                if not v:
                    bouts.append(L)
                    continue
                nm = noms.get(planche[:3], {}).get(prefixo + L, {})
                titre = nomo(nm, langue).replace('"', "&quot;")
                nu = "" if len(m.group(2)) == 1 else " nuda"
                bouts.append(
                    f'<button class="lupo{nu}" data-g="{planche}" '
                    f'data-c="{v[0]},{v[1]},{v[2]},{v[3]}" data-n="{L}" '
                    f'title="{titre}" aria-expanded="false">{L}</button>')
                fait += 1
            if not fait:
                return m.group(0)
            pose += fait
            # THE PARENTHESIS BELONGS TO THE CROSS-REFERENCE, AND IS
            # CLICKED WITH IT. A number alone takes its whole group into
            # the button — « (7) » —, and the letter had only its letter:
            # one had to aim at a character three points wide. When the
            # letter is alone, it therefore does as the number does. A
            # group of two — the « (ab) » of table 1, the only one of its
            # kind — keeps its parentheses outside the button: they belong
            # to neither of the two letters.
            if len(bouts) == 1 and fait == 1:
                dedans = bouts[0]
                i = dedans.index(">") + 1
                return (dedans[:i] + f"<sup>{ita}(" + dedans[i:-len("</button>")]
                        + ")" + ("</i>" if ita else "") + "</sup></button>")
            return (f"<sup>{ita}(" + "".join(bouts)
                    + ")" + ("</i>" if ita else "") + "</sup>")

        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = RENVOI_LIT.sub(lambda m, k=k: bouton(m, k), t)
            if uniq.get(r["cle"]):
                neuf = sorto_unika(neuf, uniq[r["cle"]], planche,
                                   places, noms, k)
            if neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return pose


def uniformiser_renvois(rangi):
    """One way of writing « word (N) », across the whole page.

    The two workshops waver: 2884 cross-references are separated from
    the noun by a space, 478 are stuck to it, and seven — all Ido — are
    not even superscript. Nothing distinguishes those cases: it is
    wavering of composition. The reading page therefore writes them all
    alike, superscript and space.

    THE SPACE IS NON-BREAKING. A cross-reference thrown alone onto the
    head of a line no longer means anything; in a narrow column, on a
    telephone, that happened. The number now stays attached to its noun.

    Every number in parentheses in running text is a cross-reference:
    they run from 1 to 150, and note calls carry « (*) ».
    """
    n = 0

    def poser(m):
        # A cross-reference that opens a block — a paragraph broken by a
        # change of page — has no word before it to attach itself to.
        # «   » and not an ordinary space: written out in full,
        # because to the eye nothing would have distinguished it.
        blanc = "\u00a0" if m.start() else ""
        corps = m.group(2)
        if corps is None:                    # transcribed without a superscript
            corps = f"({m.group(3)})"
        return f'{blanc}<sup>{corps.strip()}</sup>'

    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf, combien = RENVOI.subn(poser, t)
            if not combien or neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            n += combien
    return n


# A CROSS-REFERENCE IN PARENTHESES IS CLOSED. Six times across the two
# booklets, a parenthesis is missing: « buvard 41) » and « ballots 61) »
# on the French side, « gobleto 13) » and « mi-sferi d) » on the Ido
# side, a « singe (10 » that was never closed, and the cross-reference
# to the Hotel table, « n° 13) », which the French shows clearly ought
# to have opened. Broken sort at the printer's or slip of the
# transcriber, one cannot say — and it does not matter: the source keeps
# what it reads, the two PDFs with it, and it is the reading page that
# sets cleanly.
#
# THE CHECK THAT FOUND THEM ALL fits in one line: count the parentheses
# of each paragraph and report those that do not answer each other. Six
# paragraphs out of six hundred and eighty-three, and not one more; none
# of those six was a genuine odd parenthesis of the text.
#
# We touch only WHAT IS ALREADY A CROSS-REFERENCE: a superscript
# carrying figures only, or a letter with at least one parenthesis.
# Without that last condition we would write « (o) » on the « n° » of
# the text, which are superscripts too.
FERME_NUM = re.compile(
    r'<sup>\(?\s*(\d{1,3}(?:\s*,\s*\d{1,3})*(?:\s*(?:<i>)?bis(?:</i>)?)?)'
    r'\s*\)?</sup>')
FERME_LIT = re.compile(
    r'<sup>(<i>)?(?:\(([a-z]{1,2})\)?|([a-z]{1,2})\))(</i>)?</sup>')


def fermer_renvois(rangi):
    """Gives each cross-reference back its two parentheses."""
    n = 0

    def num(m):
        nonlocal n
        neuf = f"<sup>({m.group(1)})</sup>"
        n += neuf != m.group(0)
        return neuf

    def lit(m):
        nonlocal n
        ita = "<i>" if m.group(1) or m.group(4) else ""
        neuf = (f"<sup>{ita}({m.group(2) or m.group(3)})"
                + ("</i>" if ita else "") + "</sup>")
        n += neuf != m.group(0)
        return neuf

    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = FERME_LIT.sub(lit, FERME_NUM.sub(num, t))
            if neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# AND WHAT IS NOT A CROSS-REFERENCE IS CORRECTED BY HAND. « La listo
# esos kompletigata sur la du tabeli « La Hotelo » n° 13) e « La
# Merkato » (n° 15) »: the second parenthesis opens, the first does not,
# and the French of the same note opens both. It is not a
# cross-reference to an object on the plate but to another table; no
# general rule catches it, and we are not going to invent one for a
# single case. plates/corrections.json says so in so many words, block
# by block.
def korekti_teksto(rangi):
    """The corrections declared by hand, block by block."""
    tab = korekti("teksto")
    if not tab:
        return 0
    n = 0
    for r in rangi:
        regles = tab.get(r["cle"])
        if not regles:
            continue
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = t
            for lg, avant, apres in regles:
                if lg == TABLO.get(k, k):
                    neuf = neuf.replace(avant, apres)
            if neuf == t:
                continue
            n += 1
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# AND THE HYPHEN THE GLUING USED TO EAT. « \\cc » says the printed line
# breaks here with a hyphen; we take it out and glue back, because
# « ler- » plus « nanti » makes « lernanti ». But when the line breaks
# ON the hyphen of a compound -- « choux- » then « fleurs » -- the same
# gluing gives « chouxfleurs », and the close-up is titled so.
#
# NO RULE SEPARATES THE TWO CASES, and none should be looked for: the
# facsimile sets the same hyphen on both sides, and the transcription
# has nothing to distinguish them by. It is the column that decides, and
# plates/corrections.json carries what it says -- either that it writes
# the uncut compound elsewhere, or that it writes other compounds on the
# same half, all with the hyphen. Where it wavers, we do not decide:
# « vitberi » and « teretajo » are written both ways and stay stuck
# together.
#
# THE RESTORATION IS DONE ON THE RENDERED TEXT, not on the LaTeX, and
# for a reason: the two halves are two \\VUgras{} the page has already
# merged into a single <b>. Laid here, the hyphen goes at the same
# stroke into the button's « title », hence into the close-up's name.
# AND THE CLOSE-UP'S NAME FOLLOWS THE TEXT. The button's « title » comes
# not from the paragraph but from plates/numbers.json, transcribed from
# the plate: the correction laid on the text therefore does not reach
# it, and the button of the « fourneau de cuisuine » kept the slip the
# line no longer had. We pass the text's table over again once the
# buttons are composed.
#
# BUT ONLY THE RULES THAT CAN BE PASSED AGAIN WITHOUT HARM. « (julio od »
# turned into « (<b>julio</b> od » is no longer found: the rule does not
# bite twice. « n<sup>o</sup> 13) » turned into « (n<sup>o</sup> 13) » is
# found ITSELF within its result, and a second pass would open a second
# parenthesis. The parting between the two is read off the rule itself:
# we pass again only those whose replacement does not contain what it
# replaces.
def korekti_nomi(rangi):
    """The text's table, passed again over the names of the close-ups."""
    tab = korekti("teksto")
    if not tab:
        return 0
    n = 0
    for r in rangi:
        regles = tab.get(r["cle"])
        if not regles:
            continue
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = t
            for lg, avant, apres in regles:
                if lg == TABLO.get(k, k) and avant not in apres:
                    neuf = neuf.replace(avant, apres)
            if neuf == t:
                continue
            n += 1
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# AND THE REGIONAL VARIANT IS DRAWN FROM ITS BASE. text/variants.json
# says, column by column, what the other edition writes in its place:
# some sixty words for English, where a twin column would have copied
# thirty thousand.
#
# TWO KINDS OF RULE, and the second is indispensable. « [before,
# after] » holds for the whole column; « [key, before, after] » holds
# only within that block, because a word may have two senses:
# « biscuits » is « crackers » beside the cheese and « cookies » beside
# the gingerbread, « carriage » is a horse-drawn carriage on table 3 and
# a railway carriage on table 12. A global rule would decide for both,
# and would be wrong for one.
#
# THE ORDER OF THE RULES IS THAT OF THE FILE: « luggage van » is dealt
# with before « luggage », failing which the first finds nothing any
# more.
def deriver_varianti(rangi):
    """Each variant, cast on its base."""
    if not VARIANTI:
        return 0
    n = 0
    for r in rangi:
        n += deriver_rango(r, PAROJ)
    return n


def paroj_varianti():
    """(variant, base, rules) for each declared pair.

    THE RULES ARE PREPARED ONCE. For an overlay of words they stay a
    list, applied in order; for an overlay of SCRIPT they become a
    single expression, the longest first, because each character must be
    consumed once only.
    """
    out = []
    for lg in LANGUES:
        if not lg.get("kalko"):
            continue
        v = VARIANTI[lg["dosiero"]]
        regles = v["remplaci"]
        if v.get("unpase"):
            tab = {a: b for a, b in regles}
            rx = re.compile("|".join(re.escape(a) for a in
                                     sorted(tab, key=len, reverse=True)))
            regles = (rx, tab)
        out.append((lg["kodo"], lg["kalko"], regles))
    return out


PAROJ = paroj_varianti()


def deriver_rango(r, paroj):
    """A row, and its variants."""
    n = 0
    if True:
        for kalko, bazo, regles in paroj:
            o = r["tra"].get(bazo)
            if not o or not o.get("t"):
                continue
            t = o["t"]
            if isinstance(regles, tuple):
                # A SINGLE SWEEP, THE LONGEST RULE FIRST. A conversion of
                # SCRIPT is not a list of words: the same character is
                # rendered two ways according to what surrounds it —
                # « 里 » is 裏 in « 屋里 » and stays 里 in « 莫里斯 » — and
                # certain sequences must therefore be PROTECTED. Successive
                # replacement cannot protect: the rule « 莫里斯 » ->
                # « 莫里斯 » does nothing, and a shorter rule comes and
                # bites into it. A single sweep consumes each character
                # once.
                rx, tab = regles
                t = rx.sub(lambda m: tab[m.group(0)], t)
            else:
                for regle in regles:
                    if len(regle) == 3:
                        cle, avant, apres = regle
                        if cle != r["cle"]:
                            continue
                    else:
                        avant, apres = regle
                    t = t.replace(avant, apres)
            r["tra"][kalko] = dict(o, t=t)
            if t != o["t"]:
                n += 1
    return n


def retablir_trati(rangi):
    """The lexical hyphens the end of a line had eaten."""
    tab = korekti("trati")
    if not tab:
        return 0
    n = 0
    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            regles = tab.get(TABLO.get(k, k))
            if not regles:
                continue
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf = t
            for colle, trait in regles:
                neuf = neuf.replace(colle, trait)
            if neuf == t:
                continue
            n += 1
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
    return n


# THE CHECK THAT FOUND THE SIX. Count the parentheses of each
# paragraph and report those that do not answer each other: six
# paragraphs out of six hundred and eighty-three, and not one more —
# none was a genuine odd parenthesis of the text, all were maimed
# cross-references. We let it run at every build: the day a
# transcription lets one through, it will say so here.
def depareillees(rangi):
    for r in rangi:
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            nu = re.sub(r'<[^>]+>', '', t)
            if nu.count("(") != nu.count(")"):
                yield r["cle"], k, re.sub(r'\s+', ' ', nu)[:110]


TETE_NOTE = re.compile(r'^((?:<[^>]+>)*)\((?:\*+|\d+)\)')


def uniformiser_notes(rangi):
    """Marks the note itself « (*) », as its call is marked.

    The call is already rendered « (*) » for everyone; the note had to
    open on the same sign, failing which the « (*) » button of table 13
    unfolded a note beginning with « (1) ». We touch only the leading
    mark, never the body of the note -- that of table 6 quotes « la E.
    baby, F. bebe », and those parentheses must stay.
    """
    n = 0
    for r in rangi:
        if r["tipo"] != "noto":
            continue
        for k in ["io"] + [lg["kodo"] for lg in LANGUES]:
            t = r["io"] if k == "io" else (r["tra"].get(k) or {}).get("t")
            if not t:
                continue
            neuf, combien = TETE_NOTE.subn(r"\1(*)", t, count=1)
            if not combien or neuf == t:
                continue
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            n += 1
    return n


# THE DISPLAY LINES, AND THE SAME LIST FOR EVERYONE.
# \VUcentre and \VUtitre carry « ln », \VUpk carries « pk »: all three
# set a LINE of the facsimile. Two places read them back -- the table of
# contents, which draws its entries from them, and the anchoring, which
# lays a « -lN » on each -- and they must count THE SAME ONES, or the
# table's references fall beside the line announced. Hence a single list
# of classes, read by both.
CLASSE_AP = r'ln[^"]*|pk'
ATTRS_AP = r'(?: [a-z-]+="[^"]*")*'
LIGNE_AP = re.compile(
    rf'<span class="(?:{CLASSE_AP})"({ATTRS_AP})>(.*?)</span>', re.S)
OUVRE_AP = re.compile(rf'<span class="({CLASSE_AP})"({ATTRS_AP})>')
KORPO = re.compile(r'data-korpo="([^"]*)"')


def net_tdm(x):
    """The bare text of a line, for the table of contents."""
    # The note call is a button in the page; in the table of contents it
    # leads nowhere. We take it out, and sew back up: « La Rekolto (*). »
    # without its marker would leave « La Rekolto . ».
    x = re.sub(r'<button class="apel".*?</button>', "", x, flags=re.S)
    x = re.sub(r"<[^>]+>", "", x)
    x = re.sub(r"\s+", " ", x)
    return re.sub(r" +([.,;:])", r"\1", x).strip()


def est_ceno(x):
    """A scene marker -- « Unesma ceno. », « Duesma ceno. »."""
    # THE FACSIMILE SETS THEM IN ITALIC, and that is how they are
    # recognised: the word itself changes from one language to another. We
    # accept the bare line as well as the line still in its span.
    x = re.sub(rf'^\s*<span class="(?:{CLASSE_AP})"{ATTRS_AP}>', "", x)
    return bool(re.match(r"\s*<i>", x))


# THE ROLE IS READ OFF THE WORD, AND THE WORD CHANGES WITH THE
# LANGUAGE. Three display lines are recognised by their wording and not
# by their macro: the table number, the series, the scene. As long as
# there were only Ido and French, two lists of words sufficed; the
# English column was not among them, and its three lines all fell back
# on the role « sekc » -- « CHART No. 7 » was set like a subheading,
# facing a « TABELO No 7 » in large and bold, and « First scene. » in
# small capitals facing an « Unesma ceno. » in italic. One more
# language is one more word in each of the three lists.
#
# THE TABLE NUMBER. The comparison is CASE-SENSITIVE: the facsimile
# sets those three words in capitals, and « Charts 3 and 4 are
# arranged... » — the opening paragraph of table 3 — must not pass for
# a table title.
NUMERO_TAB = re.compile(r"TABELO|TABLEAU|CHART|CUADRO|QUADRO|ТАБЛИЦА"
                        r"|图表|لوحة"
                        # CANTONESE IS WRITTEN IN TRADITIONAL
                        # CHARACTERS: « 圖表 » is the same word as
                        # Chinese's « 图表 », in the other spelling.
                        # Both members are necessary, since the
                        # comparison is made on the character.
                        r"|圖表"
                        # HINDI HAS NO CAPITALS to distinguish the title
                        # from the prose, and « तालिका » is read also in
                        # « देल्मास सहायक तालिकाओं से », which is the
                        # title of the volume and not that of a table. We
                        # therefore require the « सं. » that follows the
                        # word in the numbering line alone.
                        r"|तालिका\s+सं"
                        # MARATHI SAYS « तक्ता », which is not Hindi's
                        # « तालिका »: two neighbouring languages, two
                        # words, and that is why the column translates
                        # for itself. The same reason as for Gurmukhi
                        # and Shahmukhi.
                        r"|तक्ता\s+क्रमांक"
                        # TELUGU SAYS « పట్టిక ». As for Hindi and
                        # Marathi, we require the word of the number
                        # that follows, for want of capitals.
                        r"|పట్టిక\s+సంఖ్య"
                        # KOREAN writes « 도표 제 9 호 », built on the
                        # same mould as the Japanese « 図表第 9 号 »:
                        # the word, then the « 제 » that numbers.
                        r"|도표\s*제"
                        # TAMIL SAYS « அட்டவணை எண் 1 »: the word,
                        # then « எண் », the number. The same reason as
                        # for Hindi, Marathi and Telugu — no capitals,
                        # so we require the word of the number that
                        # follows.
                        r"|அட்டவணை\s+எண்"
                        # URDU SAYS « جدول نمبر 1 ». Shahmukhi Punjabi
                        # says « نقشہ نمبر » in the same alphabet: two
                        # words, two columns.
                        r"|جدول\s+نمبر"
                        # INDONESIAN writes « BAGAN No. 1 ». The word
                        # is read in no other member — the Dutch
                        # « TABEL » and the Ido « TABELO » do not share
                        # a single letter of it in sequence — and the
                        # volume's title, « Tabel Bantu Delmas », is
                        # set in lower case as in Portuguese and
                        # Turkish.
                        r"|BAGAN"
                        # JAVANESE writes « GAMBAR No. 1 ».
                        # The word is that of the picture, not that of
                        # the chart: Javanese has no word of its own
                        # for the wall plate, and « bagan » would come
                        # to it from Indonesian — that is, from the
                        # neighbour this whole column defends itself
                        # against.
                        r"|GAMBAR"
                        # HAUSA writes « HOTO Na 1 ». The word is that
                        # of the picture, as « GAMBAR » in Javanese and
                        # for the same reason: Hausa has no word of its
                        # own for the wall plate, and « tebur »
                        # designates only the piece of furniture. The
                        # volume's title, « Hotunan taimako na Delmas »,
                        # is set in lower case and does not pass.
                        r"|HOTO"
                        # GUJARATI writes « કોષ્ટક નં. ૧ ».
                        # « કોષ્ટક » alone would be read in the volume's
                        # title, which speaks of the « ડેલ્માસ સહાયક
                        # કોષ્ટકો »; we therefore require the « નં »
                        # that follows the word only in the numbering
                        # line, as for Hindi and Bengali.
                        r"|કોષ્ટક\s+નં"
                        # PERSIAN writes « تابلوی شمارهٔ ۱ ».
                        # « تابلو » alone would be read in the volume's
                        # title, which speaks of the « تابلوهای کمکی »;
                        # we therefore require the « شماره » that
                        # follows the word only in the numbering line.
                        r"|تابلوی\s+شماره"
                        # THE SAME REASON FOR BENGALI: « সারণি » without
                        # its « নং » would be read in the volume's title.
                        r"|সারণি\s+নং"
                        # JAPANESE writes « 図表第 1 号 » as Chinese
                        # writes « 图表第 1 号 », but with its own
                        # characters: 図 is not 图.
                        r"|図表\s*第"
                        # SHAHMUKHI PUNJABI writes « نقشہ », which is
                        # also the ordinary map; we require the
                        # « نمبر » that follows the word only in the
                        # numbering line.
                        r"|نقشہ\s+نمبر"
                        # GURMUKHI writes « ਸਾਰਣੀ », which is read also
                        # in the volume's title: we require the « ਨੰ. »
                        # of the numbering line, as for Hindi and
                        # Bengali.
                        r"|ਸਾਰਣੀ\s+ਨੰ"
                        # TURKISH writes « TABLO No 1 », and the word
                        # is read also in the volume's title;
                        # but the latter is set in lower case
                        # — « Delmas Yardimci Tablolarina » — and the
                        # comparison is case-sensitive, as for
                        # Portuguese and Spanish.
                        r"|TABLO"
                        # INTERLINGUA writes « TABELLA N-o 1 ». The
                        # word resembles the Ido « TABELO » without
                        # equalling it — two l's, an a — and it
                        # therefore needs its own member. The same
                        # course as for Portuguese: the volume's
                        # title, « Tabellas Auxiliar Delmas », is set
                        # in lower case and does not pass.
                        r"|TABELLA"
                        # DUTCH writes « TABEL Nr. 1 », and « TABEL »
                        # is a piece of the Ido « TABELO »: the member
                        # alone would catch both. We therefore require
                        # the « Nr » that follows the word only in the
                        # numbering line, as for Hindi and Bengali.
                        r"|TABEL\s+Nr"
                        # SWEDISH writes « TABELL Nr 1 ». The same
                        # difficulty as Dutch — the word contains the
                        # Ido « TABEL » — and the same remedy: we
                        # require the « Nr » of the numbering line.
                        r"|TABELL\s+Nr"
                        # FINNISH writes « TAULUKKO N:o 1 ». The word
                        # resembles no other and needs no precaution:
                        # the volume's title, « Delmas-aputaulukot »,
                        # is set in lower case, and the comparison is
                        # case-sensitive.
                        r"|TAULUKKO"
                        # CATALAN writes « TAULA n.º 1 ». The word is
                        # confused with no other — the Finnish
                        # « TAULUKKO » has a U where this one has an A
                        # — and the volume's title, « Taules auxiliars
                        # Delmas », is set in lower case.
                        r"|TAULA"
                        # UKRAINIAN writes « ТАБЛИЦЯ № 1 ». The word
                        # differs from the Russian « ТАБЛИЦА » only in
                        # its last letter — Я against А — and therefore
                        # needs its own member. No precaution to take:
                        # the volume's title, « Допоміжні таблиці
                        # Дельма », is set in lower case.
                        r"|ТАБЛИЦЯ"
                        # ROMANIAN writes « TABELUL Nr. 1 », the
                        # definite article welded to the noun as it does
                        # everywhere. The word resembles the Dutch
                        # « TABEL » without equalling it, and the Dutch
                        # member requires an « Nr » separated by a
                        # space, which Romanian also places: we could
                        # therefore have done without. We give it its
                        # member all the same, because « TABELUL »
                        # suffices on its own and needs no precaution —
                        # the volume's title, « Tabelele auxiliare
                        # Delmas », is in lower case.
                        r"|TABELUL"
                        # IRISH writes « TÁBLA Uimh. 1 ». The word
                        # carries an acute accent on its A, and is
                        # therefore confused with no other member of
                        # this list. The volume's title is in lower case.
                        r"|TÁBLA"
                        # GALICIAN writes « CADRO n.º 1 ». The word is
                        # the Spanish one less its U — CADRO against
                        # CUADRO — and is therefore confused with no
                        # other member. The volume's title, « Cadros
                        # auxiliares Delmas », is in lower case.
                        r"|CADRO"
                        # CZECH writes « TABULKA č. 1 ». The word
                        # begins like the Dutch « TABEL » but parts
                        # from it at the fourth letter — TABU against
                        # TABE — and is therefore confused with no
                        # other member. The volume's title,
                        # « Delmasovy pomocné tabulky », is in lower
                        # case.
                        r"|TABULKA"
                        # LITHUANIAN writes « LENTELĖ Nr. 1 ». The word
                        # carries an E with a dot above, a letter no
                        # other column uses, and is therefore confused
                        # with nothing. The volume's title is in lower
                        # case.
                        r"|LENTELĖ"
                        # ESTONIAN ADDS NOTHING EITHER, but for a reason
                        # of composition and not of chance: it writes
                        # « TABEL », which is a piece of the Ido
                        # « TABELO », and it therefore needs the « Nr »
                        # of Dutch and Swedish. The column accordingly
                        # sets « TABEL Nr. 1 » with a capital N, like
                        # the other two, and the member « TABEL\s+Nr »
                        # below takes it with nothing to touch. It is a
                        # decision of composition, not an omission: it
                        # is written in the header of text/et.
                        # ROMANSH ADDS NOTHING EITHER. It writes
                        # « TABELLA nr. 1 », word for word the
                        # Interlingua member above. The third case of
                        # the series after Galician and Luxembourgish:
                        # a language that comes in with the pattern
                        # untouched. We note it here so that nobody
                        # looks later for the missing member.
                        # LUXEMBOURGISH ADDS NOTHING TO THIS LIST, and it
                        # is the second case of the kind after Galician.
                        # It writes « TABELL Nr. 1 », that is, exactly
                        # what Swedish writes, and the Swedish member —
                        # which requires the « Nr » so as not to catch
                        # the Ido « TABELO » — covers it word for word.
                        # Two Germanic languages, two countries with no
                        # common border, and the same title line.
                        # VIETNAMESE writes « BẢNG Số 1 ». The word is
                        # confused with no other member of this list —
                        # no other column writes an A with a hook —
                        # but it has another use at home: « bảng » is
                        # also THE BLACKBOARD of the classroom, the
                        # one on table 1, and the volume's title says
                        # « Bảng trợ giúp Delmas ». Neither passes:
                        # the comparison is case-sensitive, and only
                        # the display titles are set in capitals.
                        r"|BẢNG"
                        # GERMAN writes « TAFEL Nr. 1 ». « Tabelle »
                        # exists in German, but it is the table of
                        # FIGURES; what Delmas sells is a wall picture,
                        # and German calls it « Tafel », as it calls
                        # « Tafel » the blackboard of the classroom. The
                        # word is confused with no other member — none
                        # begins with TAF — and the volume's title,
                        # « Delmas-Hilfstafeln », is set in lower case.
                        r"|TAFEL"
                        # ITALIAN writes « TAVOLA N. 1 ». The word is
                        # that of the table and of the chart at once,
                        # and it is confused with no other member of
                        # this list: the « TABELLA » of Interlingua
                        # and Romansh has a B where this one has a V.
                        # The volume's title, « Tavole ausiliarie
                        # Delmas », is in lower case, and the
                        # comparison is case-sensitive.
                        r"|TAVOLA"
                        # POLISH SAYS « TABLICA », in the Latin
                        # alphabet: the Cyrillic member « ТАБЛИЦА »,
                        # laid for Russian, does not cover it.
                        r"|TABLICA"
                        )
# BASQUE WRITES « 1. TAULA », the ordinal before the noun as it places
# every determiner. The word is the same as the Catalan and the Occitan,
# and the member « TAULA » catches it already: nothing to add. What
# separates the three columns is the directory — text/ca, text/oc,
# text/eu — and not the title.
# OCCITAN WRITES « TAULA » AS CATALAN DOES, and it is the same word:
# the member above catches both, and there is nothing to add. The two
# columns are not confused for all that: what separates them is the
# directory — text/ca and text/oc — and not the title.

# The ordinals of the three languages, for the series and for the scene.
ORDINALO = (r"(?:unesma|duesma|triesma|quaresma"
            # ESPERANTO IS SO CLOSE TO IDO that it needs no member of
            # its own: its ordinals go into the common list, and
            # « serio » like « sceno » calls for only one more word in
            # each of the two groups below.
            r"|unua|dua|tria|kvara"
            # INTERLINGUA likewise: its ordinals are close enough to
            # the French to go into the common list, and « serie » is
            # already there by « s[eé]rie ».
            r"|prime|secunde|tertie|quarte"
            # DUTCH: its ordinals go into the common list, and it
            # calls for only one more word in each of the two groups
            # — « reeks » and « tafereel ».
            r"|eerste|tweede|derde|vierde"
            # SWEDISH: ordinals in the common list, and one more word
            # in each of the two groups — « serien » and « scenen »,
            # which carry their suffixed article.
            r"|f[öo]rsta|andra|tredje|fj[äa]rde"
            # FINNISH DECLINES ITS ORDINAL like the noun that follows,
            # but the series and the scene are in the nominative: one
            # form therefore suffices, and two more words in the
            # groups — « sarja » and « kohtaus ».
            r"|ensimm[äa]inen|toinen|kolmas|nelj[äa]s"
            # CATALAN: « primera », « tercera » and « quarta » are
            # already in the list by way of Spanish; only « segona »
            # is missing, and the four masculine forms, which the
            # Catalan escena does not need but which the series uses.
            r"|segona|primer|segon|tercer|quart"
            # OCCITAN: « primiera » and « segonda » are not in the
            # list, nor are « tresena » and « quatrena ».
            r"|primi[eè]ra|segonda|tresena|quatrena"
            # ROMANSH (rumantsch grischun): « quart » is already in
            # the list by way of Catalan, and « emprim », « segund »
            # and « terz » are not. Each takes its final a in the
            # feminine — la seria and la scena are feminine — but we
            # leave the masculine form open, as for Catalan, because
            # the pattern serves elsewhere too.
            r"|emprim[ao]?|segund[ao]?|terz[ao]?"
            # ESTONIAN: its four ordinals resemble nothing that
            # precedes. It does not decline them here — the series and
            # the scene are in the nominative — and one form therefore
            # suffices for each, as in Finnish.
            r"|esimene|teine|kolmas|neljas"
            # GERMAN: « erste » resembles the Dutch « eerste »
            # without equalling it, and « zweite », « dritte » and
            # « vierte » have no equivalent in the list. All four are
            # to be added, with « Reihe » in the series group and
            # « Szene » in the scene group.
            r"|erste|zweite|dritte|vierte"
            # ITALIAN: « prima », « seconda », « terza » and
            # « quarta ». « terza » is already in the list by way of
            # Romansh — « terz[ao]? » — and « prima » is not:
            # Spanish gives « primera », Catalan « primer ». All four
            # are therefore written out in full, in the feminine,
            # which is the gender of « serie » as of « scena ».
            r"|prima|seconda|quarta"
            # UKRAINIAN: none of its four ordinals goes into the
            # Russian list. « перша » is not « первая », « третя » is
            # not « третья », and « четверта » has not the final Я of
            # « четвёртая ». All four are to be added, with « серія »
            # in the series group; the scene is written « сцена » as
            # in Russian and is already there.
            r"|перша|друга|третя|четверта"
            # BASQUE, the only non-Indo-European language of this
            # group. Its ordinals are all built on the same suffix
            # « -garren », except the first; they are placed BEFORE the
            # noun, as everywhere else here, so that « \b...\s+... »
            # suffices and no separate member is needed. Two more words
            # in the groups below — « saila » and « agerraldia ».
            r"|lehen|bigarren|hirugarren|laugarren"
            # ROMANIAN agrees its ordinal in gender and has it
            # preceded by the article « a » or « al »: « prima serie »,
            # « a doua scena ». Only the feminine forms serve here, the
            # series and the scene being both feminine; « prima » is
            # missing from the list, and so are « doua », « treia » and
            # « patra ».
            r"|prima|doua|treia|patra"
            # IRISH places its ordinal before the noun like any
            # determiner, but it LENITES the initial after the article:
            # « an chéad shraith » — the first of the series, with an h
            # inserted into the word itself. We therefore write both
            # states of the first ordinal, « céad » and « chéad », and
            # do the same for the series below.
            r"|ch?[eé]ad|dara|tr[ií][uú]|ceathr[uú]"
            # GALICIAN ADDS NOTHING TO THIS LIST, and it is the first
            # case of the kind since Esperanto: its four feminine
            # ordinals are already there, « primeira » and
            # « terceira » by way of Portuguese, « segunda » and
            # « cuarta » by way of Spanish. It calls for nothing more in
            # the two groups below: its series is written « serie » and
            # its scene « escena », both already present.
            # CZECH declines its ordinal like the noun that follows,
            # but the series and the scene are both in the feminine
            # nominative: one form therefore suffices for each of the
            # four. « první » holds for both genders, the other three
            # take their feminine -á.
            r"|prvn[ií]|druh[aá]|tře[tť][ií]|čtvrt[aá]"
            # LITHUANIAN has a SIMPLE and a DEFINITE form of each
            # ordinal — « pirma serija » and « pirmoji serija » — and
            # usage prefers the second before a definite noun. We write
            # both states, as we had written both states of the first
            # Irish ordinal.
            # THE THIRD LITHUANIAN ORDINAL IS NOT FORMED LIKE THE OTHER
            # THREE: « pirma / pirmoji », « antra / antroji »,
            # « ketvirta / ketvirtoji » keep their stem, but « trečia »
            # makes « trečioji » and not « trečiaji ». Written first on
            # the model of its neighbours, the pattern let the TREČIOJI
            # SERIJA of table 11 through: the check on the roles
            # reported it, and it is that check that caught the fault.
            r"|pirm(?:a|oji)|antr(?:a|oji)|treči(?:a|oji)|ketvirt(?:a|oji)"
            # LUXEMBOURGISH declines its ordinal as German does, but
            # writes it as itself: « éischt », « zweet », « drëtt »,
            # « véiert », with the acute accent and the e-diaeresis
            # that are its own. We accept the accent absent for the
            # first and the fourth, which usage writes both ways, and
            # the ordinary E for the third.
            r"|[eé]ischt|zweet|dr[ëe]tt|v[ée]iert"
            r"|premi[eè]re|deuxi[eè]me|troisi[eè]me|quatri[eè]me"
            r"|first|second|third|fourth"
            r"|primera|segunda|tercera|cuarta"
            r"|primeira|terceira|quarta"
            r"|перва[яй]|втора[яй]|треть[яе]|четв[её]рта[яй])")

# THE SERIES. The book has three, and the facsimile announces it at
# the head of the table that opens it: « UNESMA SERIO » at 1, « DUESMA
# SERIO » at 7, « TRIESMA SERIO » at 11. The panel carried only one,
# written hard into the template, so that all sixteen tables appeared
# under the first series.
# THREE LANGUAGES WHERE THE ORDINAL IS NOT PLACED AS ELSEWHERE, and
# where « \b...\s+... » therefore cannot serve. Chinese welds the
# ordinal to the noun and has no space: « 第一组 ». Arabic puts the
# ordinal AFTER the noun: « السلسلة الأولى ». Each therefore has its
# own member, and not one more word in the common list.
SERIO = re.compile(rf"\b{ORDINALO}\s+(?:serio|s[eéè]ri[ae]|serija|series|reeks|serien|sarja|seeria|reihe|серия|серія|saila|sh?raith)\b"
                   r"|第[一二三四]组"
                   # CANTONESE, the same word, another spelling.
                   r"|第[一二三四]組"
                   r"|السلسلة\s+(?:الأولى|الثانية|الثالثة|الرابعة)"
                   # POLISH PUTS ITS ORDINAL AFTER THE NOUN:
                   # « SERIA PIERWSZA ». The common group places the
                   # ordinal in front, and no Polish ordinal is in it;
                   # so it is a member of its own, as Arabic has one
                   # for the same reason of placement.
                   r"|seria\s+(?:pierwsza|druga|trzecia|czwarta)"
                   # EGYPTIAN ARABIC CARRIES ITS PHONOLOGY RIGHT INTO
                   # THE DISPLAY MATTER: the ث becomes ت, and
                   # « الثانية » is written « التانية », « الثالثة »
                   # « التالتة ». The standard member does not take
                   # them — it is the first time a rule of
                   # pronunciation has forced a change to the marking
                   # of the roles.
                   r"|السلسلة\s+(?:التانية|التالتة)"
                   r"|(?:पहली|दूसरी|तीसरी|चौथी)\s+शृंखला"
                   # MARATHI: « पहिली मालिका ».
                   r"|(?:पहिली|दुसरी|तिसरी|चौथी)\s+मालिका"
                   r"|(?:మొదటి|రెండవ|మూడవ|నాలుగవ)\s+శ్రేణి"
                   # KOREAN says « 첫째 계열 ».
                   r"|(?:첫째|둘째|셋째|넷째)\s+계열"
                   # TAMIL says « முதல் தொடர் ».
                   r"|(?:முதல்|இரண்டாம்|மூன்றாம்|நான்காம்)\s+தொடர்"
                   r"|(?:প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ)\s+পর্যায়"
                   r"|第[一二三四]部"
                   r"|(?:پہلا|دوجا|تیجا|چوتھا)\s+سلسلہ"
                   # URDU SAYS « سلسلہ » AS SHAHMUKHI PUNJABI DOES —
                   # it is the same Arabic word in the same alphabet
                   # —, but their ORDINALS differ: دوسرا, تیسرا
                   # against دوجا, تیجا. It is the first time two
                   # columns of the transcription share the name of a
                   # role and part company over the word that counts
                   # it.
                   r"|(?:پہلا|دوسرا|تیسرا|چوتھا)\s+سلسلہ"
                   # INDONESIAN PUTS ITS ORDINAL AFTER THE NOUN, like
                   # Arabic: « Seri Pertama ». It therefore needs its
                   # own member and not one more word in the common
                   # list, which « \b...\s+... » governs the other way
                   # round.
                   r"|[Ss]eri\s+(?:[Pp]ertama|[Kk]edua|[Kk]etiga"
                   r"|[Kk]eempat)"
                   # JAVANESE SHARES « seri » WITH INDONESIAN and
                   # parts from it over the ordinals, exactly as Urdu
                   # and Shahmukhi parted over « سلسلہ »: kapisan,
                   # kapindho, katelu, kapat against pertama, kedua,
                   # ketiga, keempat.
                   r"|[Ss]eri\s+(?:[Kk]apisan|[Kk]apindho"
                   r"|[Kk]atelu|[Kk]apat)"
                   # PERSIAN says « سری اول ». Its ordinals are
                   # neither Urdu's (پہلا) nor Arabic's (الأولى):
                   # اول، دوم، سوم، چهارم.
                   r"|سری\s+(?:اول|دوم|سوم|چهارم)"
                   # HAUSA PUTS ITS ORDINAL AFTER THE NOUN and
                   # introduces it with « na »: « Jeri na Farko ». The
                   # particle is obligatory — « jeri farko » is not
                   # said —, and it is what makes the member sure
                   # rather than the word alone, which also means an
                   # ordinary queue.
                   r"|[Jj]eri\s+na\s+(?:[Ff]arko|[Bb]iyu|[Uu]ku"
                   r"|[Hh]u[ɗd]u)"
                   # GUJARATI SAYS « શ્રેણી » WHERE MARATHI SAYS
                   # « मालिका » and Hindi « शृंखला »: three languages of
                   # the same Sanskrit stock and three words, which is
                   # precisely why each column translates for itself.
                   r"|(?:પ્રથમ|બીજી|ત્રીજી|ચોથી)\s+શ્રેણી"
                   # GURMUKHI SAYS « ਲੜੀ » WHERE SHAHMUKHI SAYS
                   # « سلسلہ »: the same language, two lexicons, and
                   # that is precisely why the two columns each
                   # translate for themselves.
                   r"|(?:ਪਹਿਲੀ|ਦੂਜੀ|ਤੀਜੀ|ਚੌਥੀ)\s+ਲੜੀ"
                   # TURKISH CANNOT BE LOWER-CASED WITHOUT DAMAGE.
                   # Python's « re.I » folds « İ » onto « i » followed
                   # by a combining dot below, and « İKİNCİ » then
                   # ceases to equal « ikinci ». We therefore write
                   # both cases by hand, in the exact form in which
                   # the files set them: capitals for the series,
                   # lower case for the scene.
                   r"|(?:B[İi]R[İi]NC[İi]|[İi]K[İi]NC[İi]"
                   r"|[ÜüU]Ç[ÜüU]NC[ÜüU]|D[ÖöO]RD[ÜüU]NC[ÜüU])"
                   r"\s+D[İi]Z[İi]\b"
                   # VIETNAMESE PUTS ITS ORDINAL AFTER THE NOUN —
                   # « LOẠT THỨ NHẤT », the series order first — and
                   # therefore cannot go into the common group, which
                   # expects the ordinal in front. It needs a member
                   # of its own, as do Hindi, Bengali and Punjabi,
                   # which do the same. The « re.I » above takes it in
                   # both cases: the display matter sets in capitals,
                   # this comment in lower case.
                   r"|loạt\s+thứ\s+(?:nhất|hai|ba|tư)", re.I)

# CZECH WRITES « scéna » WITH A LONG E, and the group provided only
# for « e » and « è ». One more accent in the class, and the Romanian
# « scena » and the Czech « scéna » both go in.
# THE SCENE, IN EVERY LANGUAGE. We used to recognise it by the
# facsimile's italic; but the italic is precisely what differs --
# Guignon sets « Unesma ceno. » in italic where Rochelle leaves
# « Première scène. » in roman. The word, for its part, is sure. It is
# the same course as for the series, just above.
# LUXEMBOURGISH SAYS « Zeen », which resembles none of the words of
# this group: neither the German « Szene » it comes from, nor the
# Romance « scena ». One more member, therefore, and not a widened
# class.
CENO = re.compile(rf"\b{ORDINALO}\s+(?:ceno|sceno|scena|scenen|sc[eè]ne|escena|cena|tafereel|kohtaus|stseen|szene|sc[eèé]n[aă]|сцена|agerraldia|radharc|zeen)\b"
                  r"|第[一二三四]场"
                  # CANTONESE writes « 第一場 », which Japanese
                  # already writes below: the member exists, we do
                  # not duplicate it.
                  r"|المشهد\s+(?:الأول|الثاني|الثالث|الرابع)"
                  # POLISH, THE SAME REASON AS AT THE SERIES: its
                  # ordinal follows the noun. « scena » is already in
                  # the common group, but it expects an ordinal
                  # BEFORE it there, and Polish puts it behind.
                  r"|scena\s+(?:pierwsza|druga|trzecia|czwarta)"
                  # THE SAME REASON AS AT THE SERIES: the Egyptian
                  # writes « المشهد التاني » and « المشهد التالت ».
                  r"|المشهد\s+(?:التاني|التالت)"
                  r"|(?:पहला|दूसरा|तीसरा|चौथा)\s+दृश्य"
                  # MARATHI CALLS A SCENE « प्रवेश », the word of its
                  # theatre, where Hindi says « दृश्य ».
                  r"|(?:पहिला|दुसरा|तिसरा|चौथा)\s+प्रवेश"
                  # TELUGU CALLS A SCENE « రంగం », the word of its
                  # theatre, as Marathi says प्रवेश: neither of them
                  # calques the learned « దృశ్యం ».
                  r"|(?:మొదటి|రెండవ|మూడవ|నాలుగవ)\s+రంగం"
                  # KOREAN CALLS A SCENE « 마당 », the word of its
                  # theatre — that of 판소리 and 마당놀이 — where the
                  # Sino-Korean calque would say « 장 ». The third
                  # column in a row to prefer its own word for scene,
                  # after the Marathi प्रवेश and the Telugu రంగం.
                  r"|(?:첫째|둘째|셋째|넷째)\s+마당"
                  # TAMIL SAYS « காட்சி », the word of its theatre.
                  # The fourth column in a row to prefer its own,
                  # after the Marathi प्रवेश, the Telugu రంగం and the
                  # Korean 마당: the scene is precisely what none of
                  # these languages borrows.
                  r"|(?:முதல்|இரண்டாம்|மூன்றாம்|நான்காம்)\s+காட்சி"
                  r"|(?:প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ)\s+দৃশ্য"
                  r"|第[一二三四]場"
                  r"|(?:پہلا|دوجا|تیجا|چوتھا)\s+منظر"
                  # THE SAME CASE FOR THE SCENE: « منظر » is the word
                  # of both columns, and only the ordinals separate
                  # them.
                  r"|(?:پہلا|دوسرا|تیسرا|چوتھا)\s+منظر"
                  # THE SAME PLACEMENT OF THE ORDINAL FOR THE
                  # INDONESIAN SCENE: « Adegan Pertama ».
                  r"|[Aa]degan\s+(?:[Pp]ertama|[Kk]edua|[Kk]etiga"
                  r"|[Kk]eempat)"
                  # AND « adegan » IS A JAVANESE WORD INDONESIAN HAS
                  # BORROWED — here the neighbour holds her word from
                  # the column that defends itself against her. Only
                  # the ordinals separate the two members.
                  r"|[Aa]degan\s+(?:[Kk]apisan|[Kk]apindho"
                  r"|[Kk]atelu|[Kk]apat)"
                  # THE SAME CASE FOR THE PERSIAN SCENE: « صحنهٔ
                  # اول ». Urdu says منظر, Arabic المشهد; صحنه is
                  # neither one nor the other.
                  r"|صحنهٔ?\s+(?:اول|دوم|سوم|چهارم)"
                  # THE SAME TURN FOR THE HAUSA SCENE: « Fage na
                  # Farko ». « fage » is the ground where one plays —
                  # the wrestler's arena, the theatre's stage — and
                  # the ordinal follows, preceded by its « na ».
                  r"|[Ff]age\s+na\s+(?:[Ff]arko|[Bb]iyu|[Uu]ku"
                  r"|[Hh]u[ɗd]u)"
                  # GUJARATI SAYS « દૃશ્ય » as Marathi says « दृश्य »
                  # — it is the same Sanskrit word —, but in its own
                  # script, and with its own ordinals: પ્રથમ, બીજું,
                  # ત્રીજું, ચોથું.
                  r"|(?:પ્રથમ|બીજું|ત્રીજું|ચોથું)\s+દૃશ્ય"
                  r"|(?:ਪਹਿਲਾ|ਦੂਜਾ|ਤੀਜਾ|ਚੌਥਾ)\s+ਦ੍ਰਿਸ਼"
                  # TURKISH, in both cases written by hand, for the
                  # reason given above at the series.
                  r"|(?:B[İi]r[İi]nc[İi]|[İi]k[İi]nc[İi]"
                  r"|[ÜüU]ç[ÜüU]nc[ÜüU]|D[ÖöO]rd[ÜüU]nc[ÜüU])"
                  r"\s+sahne\b"
                  # VIETNAMESE, the same inverted order as at the
                  # series: « Cảnh thứ nhất », scene order first.
                  r"|cảnh\s+thứ\s+(?:nhất|hai|ba|tư)", re.I)

# THE SUBTITLE IN PARENTHESES. The full stop is not on the same side
# from one volume to the other -- « (Simpla leciono pri naturcienco.) »
# in Guignon, « (Simple leçon d'histoire naturelle). » in Rochelle --
# and a test on the last letter therefore left the French out.
# The Chinese parenthesis is full-width -- « （...） » -- and so is its
# full stop: « 。 ». Keeping them costs only one more character in each
# of the two classes, and the Chinese then sets as it should; replacing
# them with the Latin signs would have made, in a line of full-width
# characters, two holes where the eye stumbles.
SUBT = re.compile(r"[(（].*[)）][\s\u3000]*[.,;:!?。、；：！？]?")


def korpo_de(attrs):
    """The type size of a display line, or nothing."""
    m = KORPO.search(attrs)
    return m.group(1) if m else ""


# THE ROLE PREVAILS OVER THE MACRO. The two volumes do not set in the
# same way what plays the same role: the title of table 8 goes through
# \VUpk on the Ido side and through \VUtitre on the French, so that the
# page gave « La Rekolto. » in text size facing a « La Moisson. --- Les
# aspects de la campagne. » in large and bold. The same for the scene:
# italic on one side, roman on the other. The PDF must keep each
# facsimile as it is; the reading page, for its part, serves to COMPARE,
# and two things that answer each other must look alike.
#
# We therefore mark each display line with its ROLE -- number, title,
# series, scene, section, subtitle -- and it is the role, not the macro,
# that the style sheet dresses. The role is read off the place and off
# the word, the only two things the two editions share.
def roles_ap(html, porte_titre=False, apres_ceno=False):
    """Marks each display line with a data-rolo.

    « porte_titre »: this block is not an opening, but it carries the
    table's title -- on tables 14 and 15 the facsimile puts nothing
    under the number and the title opens the first subheading. Without
    this it was set in the small capitals of a SECTION, so that the
    title of table 14 did not look like that of table 2.

    « apres_ceno »: the previous block was only a scene marker, and this
    one therefore carries that scene's title. On tables 3, 7 and 9 the
    scene and its title are two blocks; on 4 and 8, a single one.
    """
    trouves = list(LIGNE_AP.finditer(html))
    lignes = [(m.group(1), m.group(2)) for m in trouves]
    # AN ORNAMENT OR A RULE SEPARATES. Two lines of the same size are the
    # continuation of one title -- unless the printer has put a vignette or
    # a rule between them, which gives them as two things. The six cases in
    # the edition are the series openings: « la Delmas-tabeli helpanta »
    # then a fleuron then « UNESMA SERIO », and likewise at the second and
    # third series, where the mention of the series precedes the table's
    # number. Without this rule we would glue the volume's title and the
    # name of the series into a single line.
    coupe = [False] * len(trouves)
    for k in range(1, len(trouves)):
        entre = html[trouves[k - 1].end():trouves[k].start()]
        coupe[k] = 'class="orn"' in entre or 'class="fil"' in entre
    if not lignes:
        # A few titles are set by hand, without a \VU macro, and therefore
        # have no line to mark: we take the whole block.
        nu = net_tdm(html)
        if not nu:
            return html
        return f'<span class="pk" data-rolo="sekc">{html}</span>'

    role = [None] * len(lignes)
    numero = next((k for k, (_, t) in enumerate(lignes)
                   if NUMERO_TAB.search(t)), None)
    for k, (_, t) in enumerate(lignes):
        nu = net_tdm(t)
        if k == numero:
            role[k] = "nom"
        elif SERIO.search(nu):
            role[k] = "serio"
        elif CENO.search(nu):
            role[k] = "ceno"
        elif SUBT.fullmatch(nu):
            role[k] = "subt"

    # WHERE THE TITLE BEGINS, AND WHICH TITLE. Under the number comes the
    # table's title; but if a scene comes between -- « Unesma ceno. » on
    # table 8 -- what follows titles the SCENE, not the table. A scene
    # title must be set the same way everywhere, whether the table has one
    # or several, and larger than a mere subheading.
    depart, ceno_avant = None, apres_ceno
    if numero is not None:
        depart = numero + 1
        ceno_avant = False
    elif any(r == "ceno" for r in role):
        depart = max(k for k, r in enumerate(role) if r == "ceno") + 1
        ceno_avant = True
    elif porte_titre or apres_ceno:
        depart = 0
    if depart is not None:
        ti = next((k for k in range(depart, len(lignes))
                   if role[k] is None and net_tdm(lignes[k][1])), None)
        if ti is not None and (numero is not None or porte_titre or ceno_avant):
            if numero is not None:
                ceno_avant = any(role[k] == "ceno"
                                 for k in range(numero + 1, ti))
            quel = "titceno" if ceno_avant else "tit"
            role[ti] = quel
            # The lines of the SAME SIZE that follow are the continuation of
            # the same title (see the table of contents, which glues them so).
            for k in range(ti + 1, len(lignes)):
                if not net_tdm(lignes[k][1]):
                    continue
                # The ornament does not change the NATURE of the line: « Les
                # Bateaux. » remains a piece of the title of table 12, as
                # « La Navi. » does on the Ido side. It only prevents them
                # from being glued onto one line, below.
                if role[k] is not None or \
                        korpo_de(lignes[k][0]) != korpo_de(lignes[ti][0]):
                    break
                role[k] = quel

    for k in range(len(lignes)):
        if role[k] is None:
            # Above the number it is the display matter of the volume itself --
            # « EXPLIKO - LIBRETO », « DI »; below it, a section.
            role[k] = "avan" if (numero is not None and k < numero) else "sekc"

    # A TITLE BROKEN BY THE COMPOSITION IS READ AGAIN IN ONE BREATH. The
    # Ido facsimile breaks « La Homala Korpo. --- La Amuztempo. » and
    # « La Ludi. » over two lines where the French joins them with a dash.
    # We therefore put them back on one line, with the dash when the first
    # ends on a full stop -- and without it when it ends on a comma, where
    # the sentence carries on of itself (table 6).
    joint = [False] * len(lignes)
    k = 0
    while k < len(lignes):
        if role[k] in ("tit", "titceno"):
            fin = k
            while fin + 1 < len(lignes) and role[fin + 1] == role[k] \
                    and not coupe[fin + 1]:
                fin += 1
            if fin > k:
                for j in range(k, fin + 1):
                    joint[j] = True
            k = fin + 1
        else:
            k += 1

    n = [0]

    def poser(m):
        k = n[0]
        n[0] += 1
        att = f' data-rolo="{role[k]}"'
        if joint[k]:
            att += ' data-kunligita="1"'
        return f'{m.group(0)[:-1]}{att}>'
    html = OUVRE_AP.sub(poser, html)

    # The joiner is laid IN the following line, so that the line keeps its
    # own anchor: the table of contents counts the same lines.
    n = [0]

    def lier(m):
        k = n[0]
        n[0] += 1
        if k == 0 or not (joint[k] and joint[k - 1]):
            return m.group(0)
        avant = net_tdm(lignes[k - 1][1])
        liant = " — " if avant.endswith((".", ")", "!", "?")) else " "
        return f'{m.group(0)}{liant}'
    return OUVRE_AP.sub(lier, html)


def joindre(morceaux):
    """Glues the lines of one title back together, as the page does."""
    # The same joiner as on screen: a dash when the previous line ends on
    # a full stop, nothing when it ends on a comma and the sentence carries
    # on of itself.
    out = ""
    for m in morceaux:
        if not out:
            out = m
        elif out.endswith((".", ")", "!", "?")):
            out = f"{out} — {m}"
        else:
            out = f"{out} {m}"
    return out


def libelle_bloc(brut):
    """A block's text for the panel, glued as it is on screen."""
    # Two lines of the SAME SIZE are one title broken by the composition,
    # and are rejoined with the joiner -- as in the page. A change of size,
    # or a scene marker, separates two distinct things: « Unesma ceno. »
    # and its title keep their space.
    paires = [(korpo_de(m.group(1)), net_tdm(m.group(2)))
              for m in LIGNE_AP.finditer(brut)]
    paires = [(c, t) for c, t in paires if t]
    if not paires:
        return net_tdm(brut)
    out = paires[0][1]
    for (corps, texte), (corps_av, texte_av) in zip(paires[1:], paires):
        # A SUBTITLE IN PARENTHESES IS NOT THE CONTINUATION OF THE TITLE,
        # even set at the same size. « Gimnastiko. » and « (Naraco da un
        # de la lernanti.) » are both in 10.2pt: the panel therefore joined
        # them with a dash, then took the parenthesis off -- and the dash
        # was left all alone, « Gimnastiko. — ».
        if corps == corps_av and not CENO.search(texte_av) \
                and not CENO.search(texte) and not SUBT.fullmatch(texte):
            out = joindre([out, texte])
        else:
            out = f"{out} {texte}"
    return out


def sen_subtitro(t):
    """The subtitle in parentheses does not go into the panel."""
    # The facsimile qualifies certain titles with a parenthesis --
    # « (Naraco da un de la lernanti.) » under « Gimnastiko. »,
    # « (Simpla leciono pri naturcienco.) » under « La Korpo homala. »,
    # « (Balno-chambro.) » under « La Balneyo. ». That has its place in the
    # page, which reproduces the layout; in the panel, where one looks for
    # a title out of the corner of one's eye, it doubles the length of the
    # entry without teaching anything. We take it off only if it FOLLOWS a
    # title: an entry that would be nothing but a parenthesis is kept
    # whole, for want of anything better than nothing.
    court = re.sub(r"\s*\([^()]*\)\s*$", "", t).strip()
    # And the joiner that preceded it goes with it: nothing must be left
    # hanging at the end of the entry.
    court = re.sub(r"\s*[—–-]\s*$", "", court).strip()
    return court or t


FILET = '<span class="fil"></span>'


# THE TWO COLUMNS MUST ANNOUNCE THE SAME THING IN THE SAME WAY.
# The role of a display line is read off its wording -- « TABELO »,
# « UNESMA SERIO », « Unesma ceno. » -- and the wording changes with the
# language. When the English arrived, its three words were in none of
# the lists: « CHART No. 7 » was set like a subheading facing a
# « TABELO No 7 » in large and bold, and nobody noticed at build time.
# We therefore compare, at every build, the SEQUENCE OF ROLES of the
# columns.
#
# REPETITIONS ARE FOLDED BEFORE THE COMPARISON. A title broken into two
# lines by one workshop and set whole by the other gives
# « nom, tit, tit » against « nom, tit »: it is the same announcement,
# in two pieces, and six openings are in that case. What counts is the
# SEQUENCE of roles, not the count of lines.
def suito_rolo(t):
    """The sequence of a block's roles, repetitions folded."""
    return [k for k, _ in itertools.groupby(
        re.findall(r'data-rolo="([^"]+)"', t or ""))]


def uniformiser_filets(rangi):
    """Puts the same rule in both columns.

    The rule is a printer's fancy, and the two workshops did not lay it
    in the same places: the French closes table 2 with a rule the Ido
    has not, opens table 13 with a rule the Ido has not either, while
    only tables 1, 7 and 11 carry a rule beneath their title in BOTH
    volumes. Face to face, that gave a line in one column and nothing
    opposite, at the same height -- and a table that opens otherwise
    than the previous one.

    The reading page is not the facsimile: the PDFs keep what the
    printer composed, the page harmonises. Two rules suffice: every
    table opens on a rule beneath its title, and every rule present in
    one column is found in the other. We touch only the END of the
    blocks, where all these rules already are.
    """
    pose = 0
    for r in rangi:
        if r["tipo"] == "noto":
            continue
        cels = [("io", r)] + [(lg["kodo"], r["tra"].get(lg["kodo"]))
                              for lg in LANGUES]
        textes = {k: (o["io"] if k == "io" else o["t"])
                  for k, o in cels if o}
        pleins = {k: t for k, t in textes.items() if t and t.strip()}
        if not pleins:
            continue
        ouverture = r["tipo"] == "apar" and any(
            NUMERO_TAB.search(t) for t in pleins.values())
        veut = ouverture or any(t.rstrip().endswith(FILET)
                                for t in pleins.values())
        if not veut:
            continue
        for k, t in pleins.items():
            if t.rstrip().endswith(FILET):
                continue
            neuf = t.rstrip() + FILET
            if k == "io":
                r["io"] = neuf
            else:
                r["tra"][k]["t"] = neuf
            pose += 1
    return pose


# -------------------------------------------------------------------
#  WHAT WE WOULD ERASE WITHOUT SAYING SO
# -------------------------------------------------------------------
#  THREE TIMES IN ONE DAY, A CHANGE WRITTEN BY HAND INTO index.html
#  NEARLY DISAPPEARED: the button back to ido.help, then
#  « autocapitalize » on the search field, then the script of that same
#  button — the last added JUST BENEATH the comment that says not to do
#  it. Each time the page went on displaying, and the change was no
#  longer there. A produced file does not warn when it forgets.
#
#  THE SEAM IS CLEAN, AND IT IS WHAT MAKES THE CHECK EXACT. The page is
#  the template with six substitutions, no more: everything that is not
#  one of the six values comes VERBATIM from the template. We therefore
#  cut the template on its six marks, and look for each of the literal
#  pieces, IN ORDER, in the page we are about to replace. What separates
#  two pieces found is generated content, and is no business of this
#  check.
#
#  A PIECE THAT CANNOT BE FOUND MEANS THE FRAME HAS DIVERGED, one way or
#  the other: either the template has changed — that is normal, we have
#  perhaps just edited it —, or the page has been retouched by hand. We
#  therefore do not report the divergence itself, but only the lines
#  that exist NEITHER in the template NOR in the page we are about to
#  write: those, and those alone, are about to be lost.
#
#  APPROACH TRIED AND ABANDONED: simply comparing the old page and the
#  new, line by line, and reporting those that had gone. The report is
#  unusable — the slightest correction in text/ makes dozens appear, all
#  legitimate. It is the cutting on the marks that separates the frame
#  from the content; without it the check cries out at every pass, and
#  one stops reading it.
#
#  IT WARNS, IT DOES NOT INTERRUPT, and that is deliberate. A line that
#  disappears is not always a loss: erasing a line from the template
#  makes it disappear from the page too, and the report signals it the
#  same way since it cannot know which of the two hands has moved.
#  Stopping the generation in that case would prevent the deliberate
#  removal of an element. We therefore write the page, and say what we
#  have carried off — it is for the reader to recognise whether he
#  wanted it.
MARQUES = ("TITRO", "SUBTITRO", "NAV", "LINGUI", "KONTENO", "LINGUIJSON")


def perdues(gabarito, ancienne, nouvelle):
    """The lines of the old page the new one will no longer have."""
    morceaux = [m for m in re.split(
        r"\{\{(?:" + "|".join(MARQUES) + r")\}\}", gabarito) if m]
    pos = 0
    for m in morceaux:
        i = ancienne.find(m, pos)
        if i < 0:
            break
        pos = i + len(m)
    else:
        return []
    return [l for l in dict.fromkeys(ancienne.splitlines())
            if l.strip() and l not in gabarito and l not in nouvelle]


def rendre(rangi):
    # THE DEFERRED LANGUAGES ARE FILED HERE RATHER THAN IN THE PAGE.
    # Everything is computed as for the others -- display roles, note
    # calls, cross-reference buttons -- and only the last motion changes:
    # instead of writing the text into the cell, we put it in this bag,
    # which will go off into lingui/<kodo>.json, and the cell stays
    # empty.
    differe = {lg["kodo"]: {"k": {}, "noto": {}}
               for lg in LANGUES if lg.get("differita")}
    diskordi = []

    # The table of contents is drawn from the title blocks.
    # THE TABLE OF CONTENTS HAS THREE RANKS, because the book has
    # three: the table, the scene, the subheading. The tables with
    # several parts -- 3, 4, 7, 8, 9... -- carry « Unesma ceno »
    # and « Duesma ceno », set in italic and not in small capitals;
    # that is what distinguishes them, and it is read off the
    # facsimile, not off logic.
    def texte_de(r):
        return r["io"] or next(iter(r["tra"].values()), {}).get("t", "")

    tdm = []
    # THE SHORT WORDING OF EACH TABLE OPENING. The search masks
    # everything that does not answer, titles included; but a result
    # without its table cannot be placed, and the whole opening would make
    # four display lines above two paragraphs. We therefore keep here the
    # number and the title, already computed for the table of contents, and
    # the page uses it as a running head for its results.
    tetes = {}
    # A subheading taken up as a table title is not announced twice
    # (see below).
    empruntes = set()
    # A scene title announced with its scene is not announced twice.
    fusionnes = set()
    net = net_tdm
    for idx, r in enumerate(rangi):
        if r["tipo"] not in ("sub", "apar"):
            continue
        brut = texte_de(r)
        paires = [(m.group(2), korpo_de(m.group(1)))
                  for m in LIGNE_AP.finditer(brut)]
        lignes_ap = [texte for texte, _ in paires]
        corps = [c for _, c in paires]

        if r["tipo"] == "apar":
            i = next((k for k, l in enumerate(lignes_ap)
                      if NUMERO_TAB.search(l)), None)
            if i is None:
                # NOT A TABLE OPENING, THEREFORE NOT AN ENTRY.
                # Three display blocks fall in mid-table: the publisher's
                # note on tables 3 and 4, the « (Videz la plano.) » of
                # table 5, the linking paragraph of table 6. These are
                # indications for reading, not titles, and the table of
                # contents announced them at the rank of the tables --
                # « (La 3 - ma e 4 - ma tabeli esas tale kombinita ke li
                # prizent ». The original branch aimed at the cover and the
                # dedication; but those never reach here, since lire_langue
                # discards « 00- » and « 90- ». It was picking up only these
                # three.
                continue
            num = net(lignes_ap[i])
            # THE TITLE DOES NOT ALWAYS FOLLOW THE NUMBER. The tables with
            # several scenes slip « Unesma ceno. » between the two: we skip
            # the scene markers. And neither is it the LAST line of the
            # block -- on table 2 the last is « (Simpla leciono pri
            # naturcienco.) », the subtitle of a lesson, under which the
            # table of contents announced the whole table.
            # A SCENE BEFORE THE TITLE, AND THE TABLE HAS NONE. On tables
            # 7, 8 and 9 the number is followed by an « Unesma ceno. »:
            # what comes next titles the SCENE, not the table, and the two
            # volumes say so alike -- the French of table 8 carries
            # « Première scène. » then « La Moisson. --- Les aspects de la
            # campagne. ». The table of contents nevertheless announced
            # that scene title as the table's, which has none.
            premiere = next((k for k in range(i + 1, len(lignes_ap))
                             if net(lignes_ap[k])), None)
            ceno_dabord = premiere is not None and \
                bool(CENO.search(net(lignes_ap[premiere])))
            ti = None if ceno_dabord else premiere
            # A TITLE MAY RUN TO SEVERAL LINES, and it is the SIZE that
            # says so: the lines of the same size as the first are the
            # continuation of the same title, a line of another size begins
            # something else. The title of table 6 holds on two lines of
            # 11.4pt, that of table 13 on two of 10.2pt, that of table 16
            # on two of 13.2pt; the table of contents cut after the first
            # and announced « la Lumizado. », « La Kafeerio. », « La
            # Ludili. » as separate sections -- in italic, at the rank of
            # the scenes, when they finish the table's title.
            suites = []
            if ti is not None:
                for k in range(ti + 1, len(lignes_ap)):
                    if not net(lignes_ap[k]):
                        continue
                    if corps[k] != corps[ti] or est_ceno(lignes_ap[k]):
                        break
                    suites.append(k)
            titre = joindre([net(lignes_ap[ti])] +
                            [net(lignes_ap[k]) for k in suites]) \
                if ti is not None else ""
            if not titre and not ceno_dabord:
                # THE TITLE IS SOMETIMES OUTSIDE THE OPENING BLOCK. On
                # tables 14 and 15, the Ido facsimile puts nothing but a
                # blank under the number, and the title opens the first
                # subheading that follows -- where the French volume keeps
                # it in the opening. The table of contents therefore
                # announced those five tables under their number alone,
                # « TABELO No 10 » and nothing more. We go and fetch it at
                # the first subheading that is not a scene, without
                # crossing into the next table.
                for q in rangi[idx + 1:]:
                    if q["tipo"] == "apar":
                        break
                    if q["tipo"] != "sub":
                        continue
                    suite = texte_de(q)
                    if est_ceno(suite) or CENO.search(net(suite)):
                        # A scene opens the table: what follows titles
                        # it, and the table is left without a title.
                        # That is the case of tables 7 and 9.
                        break
                    titre = net(suite)
                    # AND IT IS NOT ANNOUNCED TWICE. Borrowed from the
                    # first subheading, the title reappeared just
                    # below as a sub-entry: the panel read
                    # « TABELO No 10 La Maro. --- La Portuo. » then
                    # « La Maro. --- La Portuo. ».
                    empruntes.add(q["cle"])
                    break
            # THE SERIES IS ANNOUNCED BEFORE THE TABLE THAT OPENS IT, and
            # sometimes in the PREVIOUS block: the opening of table 1 is
            # cut in two to make room for the engraving, and « UNESMA
            # SERIO » stayed with the volume's display matter. We
            # therefore look also where it may have fallen.
            avant = lignes_ap[:i]
            if idx and rangi[idx - 1]["tipo"] == "apar":
                avant = [m.group(2) for m in
                         LIGNE_AP.finditer(texte_de(rangi[idx - 1]))] + avant
            serie = next((SERIO.search(net(l)) for l in avant
                          if SERIO.search(net(l))), None)
            if serie:
                tdm.append((None, serie.group(0).capitalize(), "parto"))
            tdm.append((r["cle"], f"<b>{num}</b> {titre}".strip(), "tt"))
            # The middle dot, as in the page's byline: the titles
            # already carry em dashes, and one more dash would not be
            # distinguished from them.
            tetes[r["cle"]] = f"{num} · {titre}" if titre else num
            # What is left of the block -- scene, subheading -- is worth
            # an entry of its own. The title is taken out of it: it is
            # already announced above. What PRECEDES the number does not
            # count: it is the series display matter, « EXPLIKO -
            # LIBRETO », « UNESMA SERIO ».
            absorbe = set()
            for j in range(i + 1, len(lignes_ap)):
                if j == ti or j in suites or j in absorbe \
                        or not net(lignes_ap[j]):
                    continue
                lib = net(lignes_ap[j])
                # THE OPENING'S SCENE CARRIES ITS TITLE WITH IT, like those
                # that have a block of their own: on table 8 the scene and
                # its title are both in the opening, and the panel
                # announced « Unesma ceno. », « La Rekolto. » and « La
                # Aspekti di la Ruro. » as three entries.
                if CENO.search(lib):
                    parts, k, base = [], j + 1, None
                    while k < len(lignes_ap):
                        if not net(lignes_ap[k]):
                            k += 1
                            continue
                        if k in (ti,) or k in suites \
                                or CENO.search(net(lignes_ap[k])):
                            break
                        if base is None:
                            base = corps[k]
                        elif corps[k] != base:
                            break
                        parts.append(net(lignes_ap[k]))
                        absorbe.add(k)
                        k += 1
                    if parts:
                        # A space, not the joiner: the dash is worth
                        # something only between the lines of ONE title,
                        # and the scene is not one of them.
                        lib = f"{lib} {joindre(parts)}"
                tdm.append((f'{r["cle"]}-l{j}', lib, "sc"))
            continue

        # A subheading: scene, or section.
        if r["cle"] in fusionnes:
            continue
        nues = [net(t) for t in lignes_ap if net(t)] or [net(brut)]
        if est_ceno(brut):
            # THE SCENE'S TITLE IS ANNOUNCED WITH IT. On tables 3, 7, 8
            # and 9 the scene and its title are two blocks; on 4, a
            # single one. The panel therefore gave « Unesma ceno. » all
            # alone here and « Unesma ceno. La Mariaj-festino. » there,
            # for the same thing. When the marker is alone in its block,
            # we attach to it the following block, which carries its
            # title.
            libelle = libelle_bloc(brut)
            if all(CENO.search(x) for x in nues):
                for q in rangi[idx + 1:]:
                    if q["tipo"] == "p":
                        break
                    if q["tipo"] != "sub":
                        continue
                    suite = texte_de(q)
                    if not est_ceno(suite):
                        libelle = f"{libelle} {libelle_bloc(suite)}"
                        fusionnes.add(q["cle"])
                    break
            tdm.append((r["cle"], libelle, "sc"))
            continue
        if r["cle"] in empruntes:
            continue
        tdm.append((r["cle"], libelle_bloc(brut), "st"))

    lignes = []
    apres_ceno = False
    gravo = gravuri()
    for r in rangi:
        cl = ["r", r["tipo"]]
        io = r["io"]
        # THE ENGRAVING PRECEDES THE BLOCK IT ILLUSTRATES, and it is the
        # KEY that says so -- not the table's number. Most plates open
        # their table, but not all: the figure of the human body is set
        # under « La Korpo homala. », the house plan under the
        # « (Videz la plano.) » of table 5, and table 1 between the
        # volume's display matter and its own title -- which is why its
        # opening is cut in two in the transcription.
        g = gravo.get(r["cle"])
        if g:
            v, d = g["vido"], g["detalo"]
            # THE FILENAME DOES NOT CHANGE WHEN THE PLATE CHANGES.
            # We are redoing the sixteen engravings one by one from their
            # facsimile; the file keeps its name, and the browser that has
            # already seen it serves the old one — the colour one — again
            # without asking. The reader then believes nothing has moved.
            # We therefore hang on the address the SIZE of the file, which
            # plates.json already notes: it changes as soon as the image
            # changes, and does not move as long as it does not.
            qv, qd = f"?v={v['okteti']}", f"?v={d['okteti']}"
            lignes.append(
                f'<figure class="gravuro" data-cle="{r["cle"]}" '
                f'data-detalo="plates/{r["cle"]}-detalo.webp{qd}" '
                f'data-dl="{d["largeur"]}" data-dh="{d["alteso"]}">'
                # TWO RESOLUTIONS, AND THE BROWSER CHOOSES. On an
                # ordinary screen the general view suffices; on a
                # Retina, where each point of the page is worth two
                # points of the screen, it looked blurred. « sizes »
                # gives the real display width: a telephone therefore
                # takes the small one, and only a large dense screen
                # goes for the detail image -- the very one that will
                # serve for full screen and for close-ups, hence never
                # loaded twice.
                f'<img src="plates/{r["cle"]}-vido.webp{qv}" alt="" '
                f'srcset="plates/{r["cle"]}-vido.webp{qv} {v["largeur"]}w, '
                f'plates/{r["cle"]}-detalo.webp{qd} {d["largeur"]}w" '
                f'sizes="(max-width:900px) calc(100vw - 64px), '
                f'min(calc(100vw - 314px), 1246px)" '
                f'loading="lazy" decoding="async" '
                f'width="{v["largeur"]}" height="{v["alteso"]}">'
                f'</figure>')
        att = f' id="{ancro(r["cle"])}" data-cle="{r["cle"]}"'
        if r["cle"] in tetes:
            tete = (tetes[r["cle"]].replace("&", "&amp;")
                    .replace('"', "&quot;").replace("<", "&lt;"))
            att += f' data-tete="{tete}"'
        fol = ""
        if r["folio"]:
            pg = rang_pdf("io", r["feuillet"])
            fol = (f'<a class="fol" href="tabeli.pdf#page={pg}" '
                   f'title="Folio {r["folio"]} en la PDF">{r["folio"]}</a>')
        # AND THE VARIANT IS DRAWN AFTER THE ROLES, so as to inherit
        # them. The display roles are read off the TEXT, by expressions
        # tied to the language — « TABELO », « TABLEAU », « 图表 ». A
        # variant of SCRIPT no longer carries them: traditional Chinese
        # writes 圖表, which no rule recognised, and the seventeen
        # openings lost their role. The variant must not be read again:
        # it must RECEIVE what its base has understood.
        # THE ROLE IS MARKED BEFORE THE ANCHORING, and on both columns:
        # it is what makes them look alike. Only the openings and the
        # subheadings carry any; running text has no display matter.
        if r["tipo"] in ("apar", "sub"):
            porte = r["cle"] in empruntes
            io = roles_ap(io, porte, apres_ceno)
            for lg in LANGUES:
                if lg.get("kalko"):
                    continue        # the variant inherits, it is not read again
                o = r["tra"].get(lg["kodo"])
                if o and o["t"]:
                    o["t"] = roles_ap(o["t"], porte, apres_ceno)
                    # The check is done HERE, where both columns are
                    # marked: the Ido's role is laid only in a local
                    # variable, and does not survive the rendering.
                    a, b = suito_rolo(io), suito_rolo(o["t"])
                    if a and b and a != b:
                        diskordi.append((r["cle"], lg["kodo"], a, b))
            # Does the following block carry this scene's title? Yes if
            # this one ends on a scene marker. It is the Ido that
            # decides: the right-hand column follows it.
            derniers = re.findall(r'data-rolo="([^"]*)"', io)
            apres_ceno = bool(derniers) and derniers[-1] == "ceno"
        elif r["tipo"] == "p":
            apres_ceno = False
        # AND THE VARIANT IS DRAWN AFTER THE ROLES, so as to inherit
        # them. The display roles are read off the TEXT, by expressions
        # tied to the language — « TABELO », « TABLEAU », « 图表 ». A
        # variant of SCRIPT no longer carries them: traditional Chinese
        # writes 圖表, which no rule recognises, and the seventeen
        # openings lost their role. The variant must not be read again:
        # it must RECEIVE what its base has understood.
        deriver_rango(r, PAROJ)
        # The display lines each receive an anchor: the table of
        # contents refers to the scene, not only to the table.
        if r["tipo"] == "apar":
            n = [0]

            def ancrer(m):
                n[0] += 1
                # The line's attributes are copied over: data-korpo
                # must survive the anchoring.
                return (f'<span id="{r["cle"]}-l{n[0]-1}" '
                        f'class="{m.group(1)}"{m.group(2)}>')
            # OUVRE_AP, and not « ln » alone: the table of contents also
            # counts the « pk » lines, and the two numberings must coincide.
            io = OUVRE_AP.sub(ancrer, io)
        cel_io = f'<div class="k io" lang="io">{fol}{io}</div>' if io else \
                 '<div class="k io vaka" lang="io"></div>'
        cel = [cel_io]
        for lg in LANGUES:
            k = lg["kodo"]
            # ARABIC IS WRITTEN FROM RIGHT TO LEFT, and the browser must
            # be told: without « dir », the cross-references in
            # parentheses and the final punctuation were filed on the
            # wrong side of the line — « (13) » went to the left of the
            # word it numbers. The cell is marked, not the page: the
            # other columns keep their direction, and the mark holds on
            # the one language that needs it.
            sens = "" if lg["dir"] == "ltr" else f' dir="{lg["dir"]}"'
            o = r["tra"].get(k)
            if o:
                f2 = ""
                if o["f"]:
                    pg2 = rang_pdf(k, o["fe"])
                    f2 = (f'<a class="fol fd" href="tableaux.pdf#page={pg2}" '
                          f'title="Folio {o["f"]} dans le PDF">{o["f"]}</a>')
                if k in differe:
                    # The cell is empty in the file AND marked « dif »: it is
                    # by that mark that the CSS knows not to put in it the
                    # dash of the real gaps, and that the script knows it has
                    # something to pour into it.
                    differe[k]["k"][r["cle"]] = f2 + o["t"]
                    cel.append(f'<div class="k tra vaka dif" '
                               f'data-lg="{k}" lang="{k}"{sens}></div>')
                else:
                    cel.append(f'<div class="k tra" data-lg="{k}" '
                               f'lang="{k}"{sens}>{f2}{o["t"]}</div>')
            else:
                cel.append(f'<div class="k tra vaka" data-lg="{k}" '
                           f'lang="{k}"{sens}></div>')
        if r["tipo"] == "noto":
            # The note is rendered apart: it is not a two-column row but
            # a fold-out attached to the paragraph that calls it.
            # ONE NOTE PER LANGUAGE, and the identifier carries the
            # language: the call button is set in a column, it must open
            # the note of THAT column. Without the language in the
            # identifier, the French button opened the Ido note — or,
            # more often, opened nothing at all.
            for k, txt in [("io", r["io"])] + [
                    (lg["kodo"], (r["tra"].get(lg["kodo"]) or {}).get("t"))
                    for lg in LANGUES]:
                # The row's cell was built above, before we knew this
                # block was a note: it will not be rendered, and what we
                # had set aside for it would be redundant with the note
                # itself.
                if k in differe:
                    differe[k]["k"].pop(r["cle"], None)
                if txt:
                    if k in differe:
                        differe[k]["noto"][r["cle"]] = txt
                        txt = ""
                    lignes.append(
                        f'<div class="noto" id="noto-{k}-{r["cle"]}" '
                        f'data-lg="{k}" lang="{k}" hidden>{txt}</div>')
            continue
        lignes.append(f'<div class="{" ".join(cl)}"{att}>' +
                      "".join(cel) + "</div>")

    nav = "".join(
        f'<div class="parto">{t}</div>' if k == "parto"
        else f'<a href="#{c}" data-ch="{c}" class="{k}">{sen_subtitro(t)}</a>'
        for c, t, k in tdm)
    opcioni = "".join(
        f'<option value="{lg["kodo"]}">{lg["nomo"]}</option>'
        for lg in LANGUES)

    # THE ADDRESS CARRIES THE FILE'S SIZE, like that of the engravings:
    # the browser that has already read one version of the translation must
    # not serve it again when it has changed.
    dos = RACINE / "lingui"
    dos.mkdir(exist_ok=True)
    for lg in LANGUES:
        d = differe.get(lg["kodo"])
        if d is None:
            continue
        f = dos / f'{lg["kodo"]}.json'
        f.write_text(json.dumps(d, ensure_ascii=False,
                                separators=(",", ":")) + "\n",
                     encoding="utf-8")
        lg["adreso"] = f'lingui/{lg["kodo"]}.json?v={f.stat().st_size}'
        print(f'  {f.relative_to(RACINE)} : {len(d["k"])} bloki, '
              f'{f.stat().st_size // 1024} Ko')

    gabarito = (RACINE / "tools" / "template.html").read_text(encoding="utf-8")
    page = (gabarito
            .replace("{{TITRO}}", TITRO)
            .replace("{{SUBTITRO}}", SUBTITRO)
            .replace("{{NAV}}", nav)
            .replace("{{LINGUI}}", opcioni)
            .replace("{{KONTENO}}", "\n".join(lignes))
            .replace("{{LINGUIJSON}}", json.dumps(LANGUES, ensure_ascii=False)))
    cible = RACINE / "index.html"
    if cible.exists():
        perdu = perdues(gabarito, cible.read_text(encoding="utf-8"), page)
        if perdu:
            print("\n" + "=" * 64)
            print("  CE QUI DISPARAIT DE index.html, ET N'EST PAS DANS LE GABARIT")
            print("=" * 64)
            for l in perdu[:20]:
                print("  " + l.strip()[:98])
            if len(perdu) > 20:
                print(f"  ... et {len(perdu) - 20} autres")
            print("  Si l'une de ces lignes a ete ecrite a la main dans")
            print("  index.html, elle est perdue : sa place est dans")
            print("  tools/gabarito.html, qui seul survit a la generation.")
            print("=" * 64 + "\n")
    cible.write_text(page, encoding="utf-8")
    for cle, lg, a, b in diskordi:
        print(f"  ROLES DISCORDANTS {cle} : io {a} / {lg} {b}")
    print(f"index.html ecrit : {len(rangi)} bloki, "
          f"{sum(1 for r in rangi if r['tipo'] == 'p')} alinei")


if __name__ == "__main__":
    r = paro()
    rap = lier_notes(r)
    print(f"  filets ajoutes pour egaliser les colonnes : "
          f"{uniformiser_filets(r)}")
    rendre(r)
    print(f"  notes reliees a leur appel : {rap['lies']}")
    if rap.get("fermes") or rap.get("korektiti"):
        print(f"  parentheses rendues a des renvois : {rap['fermes']}"
              f", corrections declarees : {rap['korektiti']}")
    if rap.get("tratiti"):
        print(f"  traits d'union lexicaux retablis : {rap['tratiti']}")
    for cle, lg, t in depareillees(r):
        print(f"  PARENTHESE DEPAREILLEE [{lg}] {cle} : {t}")
    for langue, cle, marque, pourquoi in rap["echecs"]:
        print(f"  NON RELIEE [{langue}] {cle} « ({marque}) » : {pourquoi}")
