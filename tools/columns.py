#!/usr/bin/env python3
# ===================================================================
#  columns.py — the form and the language of the translated columns
#
#  ONE CHECK PER COLUMN, AND IT DOES NOT CHECK THE SAME THING AS THE
#  OTHERS. cross_refs.py verifies that the cross-references aim at the
#  same objects in the same order; objects.py, that each object of each
#  plate is named; checks.py, the pagination and the pairing of keys.
#  None of them looks at the SUBSTANCE of a translation file: its
#  macros, its breaks, and — for the columns that exist because they are
#  not their neighbour — its language.
#
#  WHAT MADE IT NECESSARY, one fault at a time:
#
#   * « \textuperscript{(74)} », a missing s, on Cantonese table 11.
#     cross_refs.py could NOT see it: it also picks up cross-references
#     set as « (74) » at full size, because the Ido transcription sets
#     them so on table 5. The cross-reference therefore came out right
#     and the file set wrong.
#   * four « \nl » left in the Czech, the Irish and the Galician — a
#     translation follows no line of the facsimile.
#   * a brace opened at the end of a line, which puts a space INSIDE
#     the bold group.
#   * a cross-reference set in bold instead of as a superscript, on
#     Egyptian table 10: the same blind spot as the first.
#   * three Marathi blocks amputated of a fragment of a sentence by a
#     repair made by line number. cross_refs.py signalled only one of
#     them — the one that had lost a cross-reference.
#
#  AND THE LANGUAGE, for three columns that must justify existing
#  beside a neighbour: Cantonese against Chinese, Egyptian Arabic
#  against Standard Arabic, Marathi against Hindi. If one of them wrote
#  its neighbour's language, it would be redundant — and that is the
#  exact reason Wu was set aside. We therefore pick up the forms the
#  column MUST NOT carry.
#
#  A LANGUAGE REPORT IS NOT ALWAYS A FAULT, and two have proved it:
#  the old cobbler of Egyptian table 7 himself sets « صانع أحذية »
#  against « جزمجي », and « طاولة » on table 13 is not a table but
#  backgammon. Both are exempted by their EXACT form, never by the
#  word: a check disarmed wholesale checks nothing any more.
#
#  USAGE
#      python3 tools/columns.py            # every column
#      python3 tools/columns.py yue mr     # just those
# ===================================================================

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cross_refs                                              # noqa: E402

WIDTH_ = 94          # characters, not bytes: Arabic and Devanagari
#                     put a great many into little width.

# THE MACROS A TRANSLATION IS ENTITLED TO WRITE. All the rest is a
# slip — or a TRANSCRIPTION macro, which has no business here: \nl,
# \cc and VUpage follow the lines and the leaves of the facsimile,
# which a translation does not follow.
KNOWN = {"VUgras", "VUnotes", "VUsaut", "VUcentre", "VUfilet", "VUtitre",
           "VUpk", "VUcontinue", "VUblancAlinea", "VUornamento",
           "textsuperscript", "textit", "textsc", "parplein",
           "centering", "par", "fontsize", "selectfont", "textls",
           "scshape"}

# THE TWO COLUMNS THIS TOOL DOES NOT LOOK AT. io and fr are not
# translations but TRANSCRIPTIONS: they follow the lines and the leaves
# of the facsimile, so they legitimately write \nl, \cc and VUpage, and
# their lines are as long as those of 1926. To reproach them with it
# would be to reproach them with being faithful.
TRANSCRIPTIONS = {"io", "fr"}

DEVA = r"[\u0900-\u097F]"


def _deva(*shapes):
    """Word boundary in Devanagari, for want of being able to rely on \\b.

    PYTHON'S \\b IS UNUSABLE IN DEVANAGARI: the virama « ् » and the
    matras are combining marks, which str.isalnum() rejects. Python
    therefore sees a boundary IN THE MIDDLE of « प्रत्येक », and
    « \\bये\\b » finds there a Hindi pronoun that does not exist —
    twelve reports, all false, on the first pass of Marathi table 1.
    """
    return "|".join(f"(?<!{DEVA}){re.escape(f)}(?!{DEVA})" for f in shapes)


GUJ = r"[\u0A80-\u0AFF]"


def _guj(*shapes):
    """Word boundary in Gujarati, for the same reason as in Devanagari.

    Gujarati has the same combining matras as Devanagari and Python's
    \\b is just as unusable there: see _deva, above, and the twelve
    false reports of the first Marathi pass.
    """
    return "|".join(f"(?<!{GUJ}){re.escape(f)}(?!{GUJ})" for f in shapes)


def _word(*shapes):
    return "|".join(rf"\b{re.escape(f)}\b" for f in shapes)


# THE RANGE COVERS THE MARKS AS MUCH AS THE LETTERS, and that is
# the second half of the lesson. Closed on the letters alone, the
# rule « هل » fired INSIDE « هلّق »: the shadda U+0651 is a mark, so
# the \b closes just before it, and the most ordinary Levantine word
# of the transcription cried out like a standard particle. The same
# defect misses a word by its end and invents one in its middle.
ARAB = r"[\u0621-\u065F\u0670-\u06FF]"


def _arb(*shapes):
    """Word boundary in Arabic, when the word ENDS IN A MARK.

    PYTHON'S \\b DOES NOT CLOSE AFTER A TANWIN, and it is the same
    lesson as in Devanagari, on a third alphabet. « اً » is written
    alef then U+064B, which is a combining mark of category Mn:
    str.isalnum() rejects it, so there is no word boundary after it,
    and « \\bأيضاً\\b » NEVER finds anything. Measured before a line of
    Levantine was written: « أيضًا » (tanwin then alef) passed,
    « أيضاً » (alef then tanwin) did not — and the Egyptian column had
    carried the same dead rule from the start, for أيضاً and for جداً.

    AND THE \\b OPENS NO BETTER THAN IT CLOSES. Corrected on one side
    only, the tool held for two tables then cried « فين » INSIDE
    « مجدّفين »: the shadda precedes the ف, so the \\b opens just after
    it, and the word for oarsman passed for the Egyptian
    interrogative. Three manifestations of a single defect — a silence
    by the end, a false one by the middle, a false one by the start —
    before the right form was written.

    We therefore bracket with TWO NEGATIONS, with no \\b at all,
    exactly as _deva and _guj have done from the start. The answer was
    already in the file, two helpers above.
    """
    return "|".join(
        f"(?<!{ARAB}){re.escape(f)}(?!{ARAB})" for f in shapes)


# -------------------------------------------------------------------
#  THE COLUMNS THAT HAVE A LANGUAGE TO DEFEND
# -------------------------------------------------------------------
#  {code: {"word": [(pattern, what should be written)], "exempt": [...],
#          "narration": [(pattern, ...)]}}
#
#  « narration » CARRIES THE RULES THAT HOLD ONLY OUTSIDE DIALOGUE.
#  Only one column needs it, Javanese, and only one reason gives it
#  that need: its speech levels are chosen not by text but by WHO IS
#  SPEAKING TO WHOM. The booklet's narration holds to ngoko; but on
#  table 5, which is a dialogue from end to end, the child addresses
#  his uncle, and a Javanese child speaks krama to his uncle.
#  « kula », « mboten », « sampun » are therefore the RIGHT forms
#  there, and to report them would be to cry out at the very
#  politeness the paragraph describes.
#
#  DIALOGUE IS RECOGNISED BY THE FILE, AND THE MEASUREMENT IS CLEAR.
#  Speech attributions are written « \textsc{...}. --- »: table 5 has
#  THIRTY-SIX of them, table 12 has ONE (and it is « Noto. », not a
#  speaker), the other fourteen have none. The threshold is set at
#  five, where there is nothing to decide between.
#
#  The columns absent from this table undergo only the form check,
#  which holds for all.
REGISTER = {

    # ESPERANTO AGAINST ITS OWN NEOLOGISMS. The column had no check at
    # all: it is the only constructed language of the transcription whose
    # neighbour is not another language but ANOTHER SCHOOL OF THE SAME.
    # « La Bona Lingvo » — Claude Piron's book, 1989, and the site
    # labonalingvo.org — holds that Esperanto already says everything by
    # composition and derivation, and that one more borrowed root is one
    # more word to learn for nothing. We therefore pick up here the
    # neologisms that school replaces with « mal- » or with a compound.
    #
    # THE FORMS ARE WRITTEN WHOLE, ending included, and that is
    # necessary: « kurt- » would catch « kurteno », the curtain, and
    # « led- » would catch « ledo », leather, which are both good words.
    # A root is not looked for by its beginning in an agglutinative
    # language.
    #
    # THE LAST TWO ARE NOT NEOLOGISMS but official learned roots, which
    # the column used once and twice: « hospitalo » and « karcero ». They
    # are replaced by « malsanulejo » and « malliberejo », which call for
    # no new root. The column was already making that choice elsewhere —
    # it writes « lernejo » where Ido writes « skolo ».
    "eo": {"mot": [
        (_word("olda", "oldaj", "oldan", "oldajn", "olde", "oldulo"),
         "maljuna"),
        (_word("kurta", "kurtaj", "kurtan", "kurtajn", "kurte"),
         "mallonga"),
        (_word("povra", "povraj", "povran", "povrajn", "povre"),
         "malricha (kompatinda)"),
        (_word("mava", "mavaj", "mavan", "mavajn", "mave"),
         "malbona"),
        (_word("pigra", "pigraj", "pigran", "pigrajn", "pigre"),
         "maldiligenta"),
        (_word("spita", "spitaj", "spitan", "spitajn", "spite"),
         "malgrau"),
        (_word("hospitalo", "hospitaloj", "hospitalon", "hospitalojn"),
         "malsanulejo"),
        (_word("karcero", "karceroj", "karceron", "karcerojn"),
         "malliberejo"),
    ]},

    # CANTONESE AGAINST STANDARD CHINESE. The fourteen markers are set
    # at the head of text/yue/10-toubiu-01.tex; we pick up here the
    # northern forms that would replace them.
    "yue": {"mot": [
        (_word("是"), "係"), (_word("在"), "喺"), (_word("的"), "嘅"),
        (_word("不"), "唔"), (_word("了"), "咗"), (_word("他"), "佢"),
        (_word("沒有"), "冇"), (_word("看"), "睇"), (_word("拿"), "攞"),
        (_word("給"), "畀"), (_word("很"), "好"), (_word("們"), "哋"),
    ]},

    # EGYPTIAN ARABIC AGAINST STANDARD ARABIC.
    "arz": {"mot": [
        (_arb("هذه"), "دي"), (_arb("هذا"), "ده"), (_arb("هؤلاء"), "دول"),
        (_arb("ذلك"), "ده"), (_arb("تلك"), "دي"),
        (_arb("ليس", "ليست", "ليسوا"), "مش"),
        (_arb("الذي", "التي", "الذين"), "اللي"),
        (_arb("سوف"), "حـ / هـ"),
        (_arb("ماذا"), "إيه"), (_arb("كيف"), "إزاي"), (_arb("أين"), "فين"),
        (_arb("لماذا"), "ليه"), (_arb("متى"), "إمتى"),
        (_arb("الآن"), "دلوقتي"), (_arb("عندما", "حينما"), "لما"),
        (_arb("جدًا", "جداً"), "أوي"),
        (_arb("كثيرًا", "كثيرة", "كثيرون"), "كتير"),
        (_arb("أيضًا", "أيضاً"), "كمان"), (_arb("فقط"), "بس"),
        (_arb("ثلاثة", "ثلاث"), "تلاتة / تلات"),
        (_arb("ثمانية", "ثماني"), "تمانية / تمن"),
        (_arb("سيارة", "سيارات"), "عربية"),
        (_arb("غرفة", "غرف"), "أوضة"),
        (_arb("نافذة", "نوافذ"), "شباك"),
        (_arb("حقيبة", "حقائب"), "شنطة"),
        (_arb("حذاء", "أحذية"), "جزمة"),
        (_arb("طاولة", "طاولات"), "ترابيزة"),
        (_arb("جدار", "جدران"), "حيطة"),
        (_arb("شيء", "أشياء"), "حاجة"),
        (_arb("أسماء"), "أسامي"), (_arb("ملابس"), "هدوم"),
        (_arb("معطف", "معاطف"), "بالطو"),
        (_arb("ممحاة"), "أستيكة"), (_arb("مصباح"), "لمبة"),
    ], "exemptes": [
        # THE OLD COBBLER'S PUNCHLINE, table 7: « in town I was called
        # صانع أحذية and I had no customers; here I am called جزمجي
        # and there is no shortage of work ». The learned word IS the
        # joke, and Ido already has it in the form « shuifisto » /
        # « shureparisto ».
        "(صانع أحذية)",
        # ON TABLE 13, « طاولة » IS NOT A TABLE: it is backgammon, which
        # bears that name in Egyptian and no other. The ordinary report
        # is right PRECISELY because the word is taken elsewhere.
        "طاولة} \\textsuperscript{(81)",
    ], "virgule": True},

    # MARATHI AGAINST HINDI. Two languages, one alphabet. « हो »,
    # « का » and « की » are NOT reported: Marathi says हो for « yes »,
    # का for « why » and की for « that ».
    "mr": {"mot": [
        (_deva("है", "हैं", "हूँ"), "आहे / आहेत"),
        (_deva("था", "थे", "थी"), "होता / होते / होती"),
        (_deva("नहीं"), "नाही"), (_deva("को"), "ला"),
        (_deva("और"), "आणि"), (_deva("लेकिन"), "पण"),
        (_deva("क्योंकि"), "कारण"), (_deva("बहुत"), "खूप"),
        (_deva("यह", "वह", "ये", "वे"), "हा / ही / हे / तो / ती / ते"),
        (_deva("कुछ"), "काही"), (_deva("सब"), "सर्व"),
        (_deva("लोग"), "लोक"), (_deva("भी"), "सुद्धा / पण"),
        (_deva("यहाँ", "वहाँ"), "इथे / तिथे"), (_deva("अब"), "आता"),
        (_deva("क्या"), "काय"), (_deva("कैसे"), "कसे"),
        (_deva("कहाँ"), "कुठे"),
        (_deva("लड़का", "लड़के", "लड़की"), "मुलगा / मुलगी"),
        (_deva("आदमी"), "माणूस"), (_deva("पानी"), "पाणी"),
        (_deva("छोटा", "छोटी", "छोटे"), "लहान"),
        (_deva("बड़ा", "बड़ी", "बड़े"), "मोठा / मोठी / मोठे"),
        (_deva("दरवाज़ा", "दरवाजा"), "दार"),
        (_deva("किताब"), "पुस्तक"),
        (_deva("आँख", "आंख", "आँखें"), "डोळा / डोळे"),
        (_deva("सड़क"), "रस्ता"),
        # THE THREE FORMAL WORDS ARE REPORTED ONLY IN THEIR FORMAL
        # FORM. « दृश्य » is perfectly ordinary Marathi — a view, a
        # spectacle — and table 10 uses it twice by right; what would
        # be at fault is « पहिले दृश्य » in place of « पहिला प्रवेश ». We
        # therefore aim at the word PRECEDED BY ITS ORDINAL, never at
        # the word alone: too broad a check gets itself disarmed, and
        # a disarmed check checks nothing any more.
        (_deva("तालिका क्रमांक"), "तक्ता क्रमांक"),
        (_deva("पहिले दृश्य", "दुसरे दृश्य", "तिसरे दृश्य",
               "चौथे दृश्य"), "पहिला प्रवेश ..."),
        (_deva("पहिली शृंखला", "दुसरी शृंखला", "तिसरी शृंखला",
               "चौथी शृंखला"), "पहिली मालिका ..."),
    ], "exemptes": [
        # « ये » IS ALSO THE MARATHI IMPERATIVE OF « TO COME ». Hindi
        # writes ये for « these »; Marathi conjugates येणे and says
        # « ये रे » — do come. Two languages, one alphabet, and this time
        # the two words are written with exactly the same signs: no
        # boundary, no matra separates them. We exempt the form followed
        # by its particle, never the word alone.
        "ये रे",
        # « ये-जा », THE COMING AND GOING: the same verb येणे, the same
        # two signs as the Hindi pronoun. Table 9 writes it of the
        # roadway that eases communications.
        "ये-जा",
        # « दरवाजा » IS NOT ALWAYS HINDI. Marathi says दार for the
        # door of a house — that is the rule, and the column applies
        # it everywhere — but दरवाजा for the GREAT gate of a fort, the
        # one called महादरवाजा in Maharashtra. Table 11 speaks of the
        # gate of the old fortified castle flanked by its two towers:
        # it is that word and not the other. Exempted by its exact
        # form, with its cross-reference; the Hindi spelling दरवाज़ा,
        # with its nukta, stays reported everywhere, and दरवाजा too
        # anywhere but here.
        r"\VUgras{दरवाजा} \textsuperscript{(8)}",
    ]},

    # TELUGU AGAINST HINDI, AND THE CASE DIFFERS FROM THE OTHER
    # THREE. Cantonese, Egyptian and Marathi had to defend themselves
    # against a CLOSE neighbour; Telugu is Dravidian and has no
    # kinship with the Indian columns of the transcription. The risk
    # is therefore not of drifting into Hindi but of drawing a learned
    # word from it where Telugu has one of its own — which is what
    # hurried translations do. We pick up the Hindi and Sanskrit forms
    # that everyday Telugu does not say.
    "te": {"mot": [
        (_word("है", "हैं", "था", "थे"), "ఉంది / ఉన్నాయి"),
        (_word("नहीं"), "లేదు / కాదు"),
        (_word("और"), "మరియు"), (_word("लेकिन"), "కానీ"),
        (_word("क्योंकि"), "ఎందుకంటే"), (_word("बहुत"), "చాలా"),
        (_word("यह", "वह"), "ఇది / అది"),
        (_word("क्या", "कैसे", "कहाँ"), "ఏమిటి / ఎలా / ఎక్కడ"),
        # THE FORMAL WORDS, AIMED AT ONLY IN THEIR FORMAL FORM,
        # as for Marathi: « దృశ్యం » is perfectly ordinary Telugu
        # for a view.
        (_word("తాలికా", "తాలిక"), "పట్టిక"),
        (_word("మొదటి దృశ్యం", "రెండవ దృశ్యం", "మూడవ దృశ్యం",
              "నాలుగవ దృశ్యం"), "మొదటి రంగం ..."),
    ]},

    # KOREAN AGAINST HANJA. The other columns defend themselves
    # against a NEIGHBOURING language that shares their alphabet —
    # Cantonese against Mandarin, Marathi against Hindi. Korean has no
    # neighbour of that kind: hangul is shared by nobody. What
    # threatens it is something else, and simpler: the Sino-Korean
    # word written in ideograms, as it was still printed in 1926. The
    # Korean of 2026 is written wholly in hangul; a single ideogram in
    # text/ko is therefore a fault, whichever it may be, and the rule
    # fits in one character class.
    "ko": {"mot": [
        (r"[\u4E00-\u9FFF]", "hangul seul — le coreen de 2026 "
                              "n'imprime plus le hanja"),
    ]},

    # TAMIL AGAINST ITSELF. It is the first column of the
    # transcription whose adversary is neither a neighbouring language
    # nor an old script, but a REGISTER. Tamil is diglossic in
    # earnest: the spoken and the written language differ down to the
    # conjugation, and nobody prints the first. A booklet of 1926
    # rendered in spoken Tamil would be as wrong as a booklet rendered
    # in slang — not too modern, but of another use. We therefore pick
    # up the surest marks of the spoken language, those that cannot be
    # anything else.
    #
    # Two of them call for a precaution. « இருக்கு » is the spoken form
    # of « இருக்கிறது », but it is also the end of « கிடைக்கு » and of a
    # few others: we therefore require it preceded by a space.
    # « இல்ல » is the spoken form of « இல்லை » and the beginning of
    # « இல்லாத »: we require the end of a word. A check that fires on an
    # honest word ends up disarmed, and a disarmed check checks nothing
    # any more.
    "ta": {"mot": [
        (r"(?<![\u0B80-\u0BFF])இருக்கு(?![\u0B80-\u0BFF])",
         "இருக்கிறது — la colonne s'imprime, elle ne se parle pas"),
        (r"(?<![\u0B80-\u0BFF])இல்ல(?![\u0B80-\u0BFF])", "இல்லை"),
        (r"(?<![\u0B80-\u0BFF])பண்ண(?:ு|ுது|லாம்)(?![\u0B80-\u0BFF])",
         "செய் / செய்கிறது"),
        (r"(?<![\u0B80-\u0BFF])ஏன்னா(?![\u0B80-\u0BFF])", "ஏனெனில்"),
        (r"(?<![\u0B80-\u0BFF])இப்ப(?![\u0B80-\u0BFF])", "இப்போது"),
        (r"(?<![\u0B80-\u0BFF])அப்ப(?![\u0B80-\u0BFF])", "அப்போது"),
        # TAMIL NUMERALS ARE EPIGRAPHY. The Tamil of 2026 counts in
        # Arabic figures, in prose as in formal matter — « அட்டவணை எண் 1 »
        # and not « எண் ௧ ». The ௰ ௱ ௲ (ten, hundred, thousand) are in
        # the same range and fall under the same rule.
        (r"[\u0BE6-\u0BF2]", "chiffres arabes — les chiffres tamouls "
                              "ne servent plus qu'en epigraphie"),
    ]},

    # URDU AGAINST TWO NEIGHBOURS AT ONCE, AND IT IS A NEW CASE.
    # Every column defended so far was defended on ONE front:
    # Cantonese against Mandarin, Marathi against Hindi, Korean
    # against hanja, Tamil against its own spoken form. Urdu has two,
    # and of different natures:
    #
    #   * it shares its SCRIPT with Shahmukhi Punjabi (pnb), which is
    #     ANOTHER LANGUAGE. The risk is the same as for Cantonese: the
    #     neighbour is written in the same alphabet and would go
    #     unnoticed.
    #   * it shares its LANGUAGE with Hindi — same grammar, same basic
    #     lexicon — and differs from it only by script and by LEARNED
    #     REGISTER: Sanskrit on one side, Persian and Arabic on the
    #     other. Hindi cannot slip in in Devanagari, but its learned
    #     vocabulary TRANSLITERATED can.
    #
    # THE FIRST FRONT IS HELD BY GRAMMAR. The Punjabi genitive « دا »
    # does not exist in Urdu, which says « کا »: it is the most
    # frequent and surest marker of the neighbouring language. We do
    # NOT report « دی » or « دے », which are however the two other
    # forms of the same genitive: they are also ordinary Urdu words —
    # « دی » is the past of to give, « دے » its imperative. A check
    # that took them would cry out on every page, and a check that
    # cries out ends up disarmed.
    #
    # THE SECOND IS HELD BY THE LEXICON, and the words aimed at are
    # tatsama that printed Urdu never uses — not because they would be
    # too learned, but because its learned column is the other one.
    "ur": {"mot": [
        (_word("دا"), "کا — genitif pendjabi"),
        (_word("دوجا", "تیجا"), "دوسرا / تیسرا"),
        # « اوہ » IS THE PUNJABI « اوہ » (« he ») AND THE URDU
        # INTERJECTION (« oh! »): two words for one spelling. We do
        # not report it, and keep « ایہہ », which is Punjabi only.
        (_word("ایہہ"), "یہ"),
        (_word("نئیں"), "نہیں"),
        (_word("کیتا"), "کیا"),
        (_word("توں"), "سے"),
        (_word("کول"), "پاس"),
        (_word("جیہڑا", "جیہڑی"), "جو"),
        (_word("ساڈا", "تہاڈا"), "ہمارا / تمہارا"),
        # THE TATSAMA OF HINDI, AIMED AT IN THEIR TRANSLITERATED FORM.
        (_word("ودیالیہ"), "اسکول / مدرسہ"),
        (_word("ودیارتھی"), "طالب علم"),
        (_word("ادھیاپک"), "استاد"),
        (_word("پستک"), "کتاب"),
        (_word("پرارتھنا"), "دعا"),
        (_word("سمے"), "وقت"),
        (_word("ورش"), "سال"),
        (_word("ناری"), "عورت"),
        (_word("کاریہ"), "کام"),
    ]},
    # INDONESIAN DEFENDS ITSELF ON TWO FRONTS, AND NEITHER IS A
    # NEIGHBOURING COLUMN. Its real neighbour — Malaysian Malay — is in
    # no directory of text/, and nothing would signal it to the eye:
    # the two standards are written in the same alphabet and read each
    # other without difficulty. We cannot compare, therefore; we must
    # REPORT.
    #
    # FIRST FRONT, THE LEXICON. The two standards part company over a
    # short and very well known list of everyday words. We take only
    # those whose Malaysian form does not exist at all in standard
    # Indonesian.
    #
    # SECOND FRONT, A DATE. The spelling before the 1972 reform used
    # « dj », « tj », « oe », « sj » where today one writes j, c, u,
    # sy — and that is exactly the spelling a printer would have used
    # in 1926, the year of the facsimile. It is the one trap of the
    # transcription where the fault would be CONTEMPORARY with the
    # source.
    #
    # MEASUREMENT BEFORE THE RULE, AND IT HAS ALREADY CHANGED THE LIST.
    # Run over the body of the first three tables: zero Malaysian
    # words, zero « dj », zero « tj », zero « oe », zero « sj » — but
    # TWENTY-THREE « nj », all in « menjadi », « menjaga », « menjual »,
    # where the n closes a prefix and the j opens the root. « nj » is
    # therefore excluded, as the danda was from the mixed-script check.
    #
    # ALL THE PATTERNS ARE CASE-INSENSITIVE, and that is no detail: the
    # first attempt did not see « Djalan » at the head of a sentence
    # because « Dj » is not « dj ». Spelling faults from before 1972
    # fall precisely on proper nouns and sentence openings — that is
    # where the old orthography survives longest.
    #
    # AND FIVE WORDS ARE NOT REPORTED, DELIBERATELY, BECAUSE THEY ARE
    # FALSE FRIENDS: « pejabat » is the office over there and the
    # official here; « budak » the child over there and the slave here;
    # « polis » the police over there and the insurance policy here —
    # and table 7 stages precisely an insurance agent; « kedai » and
    # « lori » live on both sides with different uses. A check that
    # cries out at a right word ends up disarmed.
    "id": {"mot": [
        (r"(?i)(?<![A-Za-z])cikgu(?![A-Za-z])", "guru"),
        (r"(?i)(?<![A-Za-z])tandas(?![A-Za-z])", "toilet"),
        (r"(?i)(?<![A-Za-z])stesen(?![A-Za-z])", "stasiun"),
        (r"(?i)(?<![A-Za-z])ubat(?![A-Za-z])", "obat"),
        (r"(?i)(?<![A-Za-z])wang(?![A-Za-z])", "uang"),
        (r"(?i)(?<![A-Za-z])beg(?![A-Za-z])", "tas"),
        (r"(?i)(?<![A-Za-z])kerusi(?![A-Za-z])", "kursi"),
        (r"(?i)(?<![A-Za-z])almari(?![A-Za-z])", "lemari"),
        (r"(?i)(?<![A-Za-z])tingkap(?![A-Za-z])", "jendela"),
        (r"(?i)(?<![A-Za-z])bomba(?![A-Za-z])", "pemadam kebakaran"),
        (r"(?i)(?<![A-Za-z])tarikh(?![A-Za-z])", "tanggal"),
        (r"(?i)(?<![A-Za-z])tayar(?![A-Za-z])", "ban"),
        (r"(?i)(?<![A-Za-z])basikal(?![A-Za-z])", "sepeda"),
        (r"(?i)(?<![A-Za-z])hospital(?![A-Za-z])", "rumah sakit"),
        (r"(?i)[A-Za-z]*dj[A-Za-z]*", "graphie d'avant 1972 — « dj » se "
                                  "note « j » depuis la reforme"),
        (r"(?i)[A-Za-z]*tj[A-Za-z]*", "graphie d'avant 1972 — « tj » se "
                                  "note « c » depuis la reforme"),
        (r"(?i)[A-Za-z]*oe[A-Za-z]*", "graphie d'avant 1972 — « oe » se "
                                  "note « u » depuis la reforme"),
        (r"(?i)[A-Za-z]*sj[A-Za-z]*", "graphie d'avant 1972 — « sj » se "
                                  "note « sy » depuis la reforme"),
    ]},

    # JAVANESE IS THE INVERSE OF INDONESIAN, AND IT IS THE SAME PAIR
    # OF LANGUAGES. When « id » was being defended, the neighbour was
    # in no directory and we had to report without being able to
    # compare. Now it is there, written by the same hand, the line
    # above — and that is precisely what makes the drift easy:
    # Indonesian is the school language of every Javanese speaker, the
    # one in which he writes all the rest of his day. We therefore
    # report the Indonesian function words, which are the ones that
    # slip in first, and never the words for things, which the two
    # languages share by the hundred.
    #
    # AND A SECOND FRONT NO OTHER COLUMN HAS HAD: THE SPEECH LEVELS.
    # Javanese has two parallel lexicons — ngoko and krama — and one
    # must hold to one of them. The column holds to NGOKO ALUS:
    # narration in ngoko, and krama inggil verbs for what the
    # grandfather does. That is what a Javanese child writes and what
    # a Javanese book of 2026 prints.
    #
    # WE THEREFORE REPORT ORDINARY KRAMA — kula, mboten, menika,
    # ingkang, sampun, kaliyan, griya, toya —, which signals a hand
    # gone over to the polite level from end to end. AND WE DO NOT
    # REPORT THE KRAMA INGGIL VERBS — dhahar, tindak, kondur,
    # ngendika, priksa, sare —, which are exactly what the column's
    # rule REQUIRES for the grandfather. A check that cries out at the
    # form the instruction calls for is worse than no check at all:
    # that is the lesson of « دی » and « دے », taken before writing.
    #
    # FALSE FRIENDS SET ASIDE DELIBERATELY: « bisa », « anak »,
    # « sekolah », « meja », « kursi », « jendela », « lawang » live in
    # both languages with the same sense — both often hold them from
    # the same Portuguese or the same Dutch. Reporting them would make
    # the check cry out on every page.
    "jv": {"mot": [
        (r"(?i)(?<![A-Za-z])tidak(?![A-Za-z])", "ora"),
        (r"(?i)(?<![A-Za-z])dan(?![A-Za-z])", "lan"),
        (r"(?i)(?<![A-Za-z])dengan(?![A-Za-z])", "karo"),
        (r"(?i)(?<![A-Za-z])yang(?![A-Za-z])", "sing"),
        (r"(?i)(?<![A-Za-z])ini(?![A-Za-z])", "iki"),
        (r"(?i)(?<![A-Za-z])itu(?![A-Za-z])", "iku"),
        (r"(?i)(?<![A-Za-z])sudah(?![A-Za-z])", "wis"),
        (r"(?i)(?<![A-Za-z])juga(?![A-Za-z])", "uga"),
        (r"(?i)(?<![A-Za-z])tetapi(?![A-Za-z])", "nanging"),
        (r"(?i)(?<![A-Za-z])sangat(?![A-Za-z])", "banget"),
        (r"(?i)(?<![A-Za-z])besar(?![A-Za-z])", "gedhe"),
        (r"(?i)(?<![A-Za-z])kecil(?![A-Za-z])", "cilik"),
        (r"(?i)(?<![A-Za-z])orang(?![A-Za-z])", "wong"),
        # « rumah sakit » IS NOT REPORTED, AND IT IS AN INSTITUTION'S
        # NAME, NOT A WORD. Javanese says omah for the house, and
        # « rumah » is indeed an Indonesianism there — except in the
        # hospital, which Java calls rumah sakit and nothing else. The
        # only other possible form is « griya sakit », which is KRAMA:
        # it would be reported by the level rule. A borrowed word can
        # therefore be the only right form, and the check must know
        # it.
        (r"(?i)(?<![A-Za-z])rumah(?!\s+sakit)(?![A-Za-z])", "omah"),
        # « banyak » WAS REPORTED HERE, THEN WITHDRAWN AT TABLE 3. The
        # Indonesian word means « many » and Javanese says akeh — the
        # rule seemed good. But « banyak » is ALSO a Javanese word, and
        # it is the GOOSE: it appears on table 3, where the village
        # children put the geese to flight (25). The two words are
        # written alike and are not the same word. The check therefore
        # cried out at a right form, and it had to be disarmed — as for
        # « دی » and « دے » in the Urdu column, and for the five false
        # friends set aside in advance in the Indonesian one. Here the
        # lesson served AGAINST a rule we had just written ourselves.
        (r"(?i)(?<![A-Za-z])semua(?![A-Za-z])", "kabeh"),
        (r"(?i)(?<![A-Za-z])atau(?![A-Za-z])", "utawa"),
        (r"(?i)(?<![A-Za-z])hanya(?![A-Za-z])", "mung"),
        (r"(?i)(?<![A-Za-z])karena(?![A-Za-z])", "amarga"),
        (r"(?i)(?<![A-Za-z])kemudian(?![A-Za-z])", "banjur"),
        (r"(?i)(?<![A-Za-z])se(?:buah|orang|ekor)(?![A-Za-z])",
         "le javanais ne compte pas avec le classificateur indonesien"),
        # AND THE TRAP OF THE DATE HOLDS HERE TOO: the 1972 reform
        # remade the Latin orthography of Indonesian AND that of
        # Javanese at one stroke. « djaran », « tjilik », « boekoe » are
        # therefore exactly what a printer would have set in 1926, and
        # this is the second column where the fault would be
        # CONTEMPORARY with the source. We do not report « sj », which
        # has never served Javanese; nor do we touch « dh » and « th »,
        # which are retroflex letters of the language and not remnants
        # of spelling.
        (r"(?i)[A-Za-z]*dj[A-Za-z]*", "graphie d'avant 1972 — « dj » se "
                                  "note « j » depuis la reforme"),
        (r"(?i)[A-Za-z]*tj[A-Za-z]*", "graphie d'avant 1972 — « tj » se "
                                  "note « c » depuis la reforme"),
        (r"(?i)[A-Za-z]*oe[A-Za-z]*", "graphie d'avant 1972 — « oe » se "
                                  "note « u » depuis la reforme"),
    ],
     # THE LEVEL RULES HOLD ONLY OUTSIDE DIALOGUE, and it took table 5
     # to understand it. They were at first in « word », with the
     # others, and that was right as long as the booklet was narrating.
     # Table 5 is one whole dialogue: Ioannes speaks there to his uncle,
     # and a Javanese child speaks KRAMA to his uncle — « kula » is the
     # right form there, and the paragraph even says the child is
     # polite. The rule was therefore moved, not withdrawn: outside
     # dialogue it still holds, and krama there does signal that the
     # whole level has slipped.
     "narracio": [
        (r"(?i)(?<![A-Za-z])kula(?![A-Za-z])",
         "aku — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])mboten(?![A-Za-z])",
         "ora — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])menika(?![A-Za-z])",
         "iki — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])ingkang(?![A-Za-z])",
         "sing — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])sampun(?![A-Za-z])",
         "wis — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])kaliyan(?![A-Za-z])",
         "karo — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])griya(?![A-Za-z])",
         "omah — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])toya(?![A-Za-z])",
         "banyu — la narration tient le ngoko, non le krama"),
    ]},

    # PERSIAN HAS TWO NEIGHBOURS IN THE TRANSCRIPTION AND BOTH ARE IN
    # ITS ALPHABET. Urdu took from it its script and half its learned
    # lexicon; Arabic gave it the alphabet and the other half. It is the
    # first column whose defence is played out at the level of the
    # CHARACTER rather than the word — and that is precisely where the
    # eye sees nothing: ی and ي, ک and ك, ۱ and ١ are drawn almost
    # alike, and the line stays well formed, the LaTeX compiles,
    # html.py publishes.
    #
    # THE LETTERS PERSIAN DOES NOT HAVE. Six are Urdu — the retroflexes
    # ٹ ڈ ڑ, the noon ghunna ں, the bari yeh ے and the do-chashmi heh ھ
    # — and four are Arabic: the yeh ي, the kaf ك, the ta marbuta ة and
    # the alef maqsura ى. Persian writes ی, ک, ه and ی in their place.
    # These are not variants of style: they are other code points, and a
    # Persian text contains none of them.
    #
    # AND THE FIGURES PART COMPANY LIKEWISE. Persian sets ۰۱۲۳۴۵۶۷۸۹
    # (U+06F0..U+06F9), Arabic ٠١٢٣٤٥٦٧٨٩ (U+0660..U+0669). The Arabic
    # transcription writes « اللوحة رقم ١ », the Urdu « جدول نمبر 1 » in
    # Latin figures: three columns of the same alphabet and three series
    # of figures.
    #
    # WE DO NOT REPORT أ OR إ, which appear in a few Arabic borrowings
    # that Persian still prints so, nor ؤ or ئ, which are Persian
    # (مسئله, مؤسسه), nor ۀ (U+06C0), which is the Persian form of he
    # followed by hamza. A check that cries out at a right form ends up
    # disarmed.
    #
    # AND A SECOND FRONT, WHICH IS A DATE AS IN INDONESIAN: THE
    # ZERO-WIDTH NON-JOINER. The Persian orthography of 2026 requires a
    # U+200C after the negative-durative prefix « نمی » — نمی‌رود and not
    # نمیرود. We report ONLY « نمی », and not « می » alone, because می
    # also opens میز, میوه, میان, میدان, میلیون, where there is nothing
    # to break: « نمی » at the head of a word is always the prefix, and
    # never anything else.
    "fa": {"mot": [
        (r"[\u0679\u0688\u0691]", "lettre retroflexe ourdoue — le persan "
                                    "ne les a pas"),
        (r"\u06BA", "ں ourdou — le persan ecrit ن"),
        (r"\u06D2", "ے ourdou — le persan ecrit ی"),
        (r"\u06BE", "ھ ourdou — le persan ecrit ه"),
        (r"\u064A", "ي arabe (U+064A) — le persan ecrit ی (U+06CC)"),
        (r"\u0643", "ك arabe (U+0643) — le persan ecrit ک (U+06A9)"),
        (r"\u0629", "ة arabe — le persan ecrit ه"),
        (r"\u0649", "ى arabe — le persan ecrit ی"),
        (r"[\u0660-\u0669]", "chiffre arabe — le persan compose "
                              "۰۱۲۳۴۵۶۷۸۹ (U+06F0..U+06F9)"),
        (r"نمی(?!\u200c)", "demi-espace manquant — l'orthographe de 2026 "
                           "ecrit نمی\u200cرود"),
    ]},

    # HAUSA TAKES UP PERSIAN'S FRONT — the CHARACTER and not the word
    # — BUT IN LATIN LETTERS, AND IT IS WORSE. Persian was defending
    # itself from two neighbouring languages lodged in its alphabet;
    # this one defends itself from its OWN TYPING. ɓ, ɗ, ƙ and ƴ are
    # four full letters of the boko alphabet, not b, d, k, y with
    # ornaments: « kofa » is not « ƙofa », and the difference is that
    # between a word and nothing at all. Yet no ordinary keyboard
    # gives them, every spell-checker returns them to their bare form,
    # and a line so stripped stays well formed: the LaTeX compiles,
    # html.py publishes.
    #
    # WE REPORT ONLY THE WORDS WHOSE BARE FORM DOES NOT EXIST. kofa,
    # karfe, karshe, kauye, daya, daki, dauka, yan are nothing in
    # Hausa; finding a sense for them calls for supposing a fault. We
    # do NOT report « kasa », which is a word — « below », « to fail »
    # — where « ƙasa » is the country and the ground: the rule would
    # be right about the letter and wrong about the word, and that is
    # exactly the case of the Javanese « rumah sakit », paid for once.
    #
    # AND A SECOND FRONT, WHICH IS A CLOSED ALPHABET: boko has no p,
    # no q, no v, no x. What comes from elsewhere is remade in the
    # Hausa mouth — « bitamin », « fensir », « kwafi » — and a p left
    # in a word is always the trace of a language that has not been
    # translated. The rule aims only at words with a LOWER-CASE
    # INITIAL: proper nouns keep their spelling, Paris stays Paris,
    # and the capital suffices to put them out of reach. The
    # lookbehind likewise sets aside macro names — the letter
    # following a « \\ » or another letter opens no word — and the
    # units of \\VUcentre, where the « pt » follows a figure.
    "ha": {"mot": [
        (r"[\u0600-\u06FF]", "lettre arabe — cette colonne s'ecrit en "
                              "boko, non en ajami"),
        (r"(?<![\\A-Za-z0-9])[a-zɓɗƙƴ’]*[pqvx][a-zɓɗƙƴ’]*",
         "lettre absente de l'alphabet boko (p, q, v, x)"),
        (r"(?<![A-Za-z])kofa(?![A-Za-z])", "ƙofa"),
        (r"(?<![A-Za-z])karfe(?![A-Za-z])", "ƙarfe"),
        (r"(?<![A-Za-z])karshe(?![A-Za-z])", "ƙarshe"),
        (r"(?<![A-Za-z])kauye(?![A-Za-z])", "ƙauye"),
        (r"(?<![A-Za-z])k(?:arami|anana)(?![A-Za-z])", "ƙarami / ƙanana"),
        (r"(?<![A-Za-z])daya(?![A-Za-z])", "ɗaya"),
        # « daki-daki » MADE THIS RULE CRY OUT AT TABLE 2, AND THE
        # RULE WAS WRONG. « ɗaki » is the room; « daki-daki », without a
        # hook and doubled, is the adverb « in detail » — it appears in
        # the N.B. of table 2, where the master is invited to describe
        # each game daki-daki. Two different words, and the hyphen
        # separates them: we therefore no longer open the rule on a word
        # touching a hyphen, on either side.
        (r"(?<![A-Za-z-])daki(?![A-Za-z-])", "ɗaki"),
        (r"(?<![A-Za-z])dauka(?![A-Za-z])", "ɗauka"),
        # HAUSA HAS TWO SPELLINGS FOR A SINGLE LETTER, AND IT IS A
        # BORDER: Niger writes ƴan, Nigeria ’yan. Both are right at
        # home. The column takes ƴ, so that its alphabet holds in four
        # hooks and not in three hooks plus an apostrophe — and the
        # rule holds to that choice, since it opens after an apostrophe
        # as readily as after a space. What it reports then is not a
        # fault, it is a mixture.
        (r"(?<![A-Za-z])yan(?![A-Za-z])", "ƴan (et non ’yan : la "
                                          "colonne ecrit le crochet)"),
        (r"'", "apostrophe droite — le haoussa de 2026 ecrit ’ (U+2019)"),
    ], "exemptes": [
        # THE « Balk-o » NOTE OF TABLE 5 IS THE ONE PLACE IN THE
        # BOOKLET THAT QUOTES OTHER LANGUAGES WORD FOR WORD, and Ido
        # itself sets them in italic to say they are foreign:
        # « Balk-o = D. Balken, E. joist, F. solive, I. travicello, R.
        # balka, S. Port. viga ». The rule of the letters absent from
        # boko therefore cried out four times, and it was right to the
        # letter: solive, poutre and viga are not Hausa, and must
        # above all not become so. We therefore tighten nothing — a
        # quotation is not a spelling fault, it is another text —, we
        # exempt the three lines that carry it, as the Egyptian Arabic
        # column exempts the old cobbler's joke.
        "\\textit{solive}",
        "\\textit{poutre}",
        "\\textit{viga}",
        # AND THE « Lambrequino » NOTE OF TABLE 6 IS OF THE SAME
        # KIND, which confirms the reading made at table 5: it is not
        # the italics that carry the quotations, it is the NOTES. This
        # one glosses the word by its French, Spanish, Portuguese,
        # German and English forms — « lambrequin, lambrequines,
        # lambrequins » —, and Ido does not even set them in italic.
        # The Hausa of the text, for its part, writes « lambarkin »,
        # without a q: the rule therefore goes on biting everywhere
        # else in this file.
        "lambrequin",
    ]},

    # GUJARATI AGAINST HINDI, AND THE DIFFICULTY IS NOT MARATHI'S.
    # Marathi shared Hindi's SCRIPT and parted from it by the lexicon;
    # Gujarati has a script of its own — it is Devanagari without the
    # top bar — and one would therefore think the two languages safe
    # from each other. They are not at all: the Gujarati script
    # transcribes ANY Hindi word effortlessly, and « બહુત » or
    # « લેકિન » set in Gujarati read as well as in their own alphabet.
    # What must be reported is therefore not a foreign letter but a
    # foreign WORD transcribed, which brings us back exactly to the
    # Marathi problem.
    #
    # AND A CHARACTER RULE ALL THE SAME, THE FIRST: a Devanagari sign
    # slipped into the middle of a Gujarati word. The two scripts have
    # the same matras in the same places and almost the same letter
    # forms; only the bar separates them, and it is visible only on the
    # whole line. It is the same trap as ی against ي in the Persian
    # column, in another family of script.
    #
    # WE DO NOT REPORT « નહીં », WHICH IS GUJARATI. Hindi writes it the
    # same way and Gujarati uses it every day — « હું નહીં જાઉં » —,
    # where « નથી » is the negative copula. Two different words, not
    # two languages. Nor do we report « કે », which is the ordinary
    # Gujarati conjunction, or « મેં », which is the ergative subject
    # pronoun: those two are Hindi AND Gujarati, and a rule crying out
    # at them would get itself disarmed at the first paragraph.
    "gu": {"mot": [
        (r"[\u0900-\u097F]", "signe devanagari — cette colonne s'ecrit "
                              "en gujarati (U+0A80..U+0AFF)"),
        (_guj("હૈ", "હૈં"), "છે"),
        (_guj("ઔર"), "અને"),
        (_guj("લેકિન"), "પણ / પરંતુ"),
        (_guj("બહુત"), "ઘણું"),
        (_guj("યહ"), "આ"),
        (_guj("વહ"), "તે"),
        (_guj("ક્યા"), "શું"),
        (_guj("કા", "કી"), "નો / ના / ની"),
        (_guj("કો"), "ને"),
        (_guj("સે"), "થી"),
        (_guj("લડકા", "લડકો"), "છોકરો"),
        (_guj("લડકી"), "છોકરી"),
    ]},

    # LEVANTINE ARABIC AGAINST TWO NEIGHBOURS THAT ARE THE SAME
    # LANGUAGE AS ITSELF. Every previous column defended itself against
    # a foreign language: Marathi against Hindi, Persian against Urdu,
    # Gujarati against Hindi. This one defends itself against Standard
    # Arabic, which is the WRITTEN form of its own language, and
    # against Egyptian Arabic, which is another spoken form of it. The
    # danger is therefore not that a foreign word should slip in: it is
    # that the hand, in writing, should climb of its own accord back
    # towards the register it was taught at school. The rules aim at
    # both sides at once — TWELVE against the standard, SEVEN against
    # the Egyptian, one against the Persian letters, twenty in all.
    # (This comment first announced « eight » and « five »: that was
    # the draft's count, before tables 1 to 16 caused more to be added.
    # Recounted by hand from the list below.)
    #
    # THREE FORMS ARE DELIBERATELY NOT REPORTED, and it must be said
    # here on pain of taking them up again later. « كيف » is Levantine
    # AND standard; « بس » is Levantine AND Egyptian; « في » is the
    # Levantine existential and the standard preposition. A rule on any
    # of the three would cry out at every table, and a check one
    # disarms checks nothing any more — the lesson of Marathi, table
    # 10.
    "apc": {"mot": [
        # THE FOUR LETTERS ARABIC DOES NOT HAVE. پ چ ژ گ are Persian
        # and Urdu; the Persian column of the transcription defended
        # itself against Arabic, this one defends itself against it.
        (r"[\u067E\u0686\u0698\u06AF]", "lettre persane — cette "
                                          "colonne s'ecrit en arabe"),
        (_arb("ليس", "ليست", "ليسوا"), "ما / مش"),
        (_arb("هذا", "هذه", "هؤلاء", "ذلك", "تلك"), "هاد / هاي / هدول"),
        (_arb("الذي", "التي", "الذين"), "يلّي"),
        (_arb("سوف"), "رح"),
        (_arb("ماذا"), "شو"), (_arb("لماذا"), "ليش"),
        (_arb("أين"), "وين"), (_arb("متى"), "إيمتى"),
        (_arb("الآن"), "هلّق"), (_arb("هل"), "— le levantin n'a pas de "
                                            "particule interrogative"),
        (_arb("يوجد", "توجد"), "في"),
        (_arb("أيضًا", "أيضاً"), "كمان"),
        # THE SEVEN EGYPTIAN ONES. « ده » and « دي » are Cairo's
        # demonstratives, « إزاي » its how, « دلوقتي » its now,
        # « عايز » its wanting: none of that is said from Beirut to
        # Amman.
        (_arb("ده", "دي", "دول"), "هاد / هاي / هدول"),
        (_arb("إزاي"), "كيف"), (_arb("فين"), "وين"),
        (_arb("دلوقتي"), "هلّق"), (_arb("كده"), "هيك"),
        (_arb("عايز", "عاوز", "عايزة"), "بدّي / بدّو"),
        (_arb("بتاع", "بتاعة"), "تبع"),
    ], "virgule": True},

    # BHOJPURI AGAINST HINDI, AND IT IS THE ONLY COLUMN OF THE
    # TRANSCRIPTION WHOSE NEIGHBOUR DENIES THAT IT EXISTS. Marathi,
    # Gujarati and Urdu defended themselves against a language that
    # held them to be languages; Bhojpuri is administered in India as a
    # « dialect of Hindi » and is in none of the official schedules,
    # with fifty million speakers.
    #
    # THERE IS THEREFORE NO POSSIBLE DEFENCE AT THE CHARACTER, and it
    # is the first time. Persian watched ی against ي, Hausa its four
    # hooked letters, Gujarati the Devanagari slipped into its
    # alphabet. Here the script is the same, the lexicon is the same
    # for three quarters of it, and the nominal morphology is alike.
    # WHAT SEPARATES THE TWO LANGUAGES IS THE VERB: the copula बा /
    # बानी / बाड़ें against है / हैं, the existential negation नइखे
    # against नहीं है, the past in -ल against the past in -आ. The rules
    # therefore aim first at the conjugation, then at the pronouns, and
    # at the lexicon last.
    #
    # FOUR FORMS ARE DELIBERATELY NOT REPORTED, and it must be said
    # here on pain of taking them up again later. « का » is the Hindi
    # genitive AND the Bhojpuri word for « what »: a rule on it would
    # cry out on every page. « के » is the Bhojpuri genitive AND a
    # Hindi oblique. « पानी » and « हाथ » are the same word in both
    # languages. A check one disarms checks nothing any more — the
    # lesson of Marathi, table 10.
    "bho": {"mot": [
        (_deva("है", "हैं", "हूँ", "हूं"), "बा / बानी / बाड़ें"),
        (_deva("था", "थे", "थी"), "रहे / रहलें / रहली"),
        (_deva("नहीं"), "ना / नइखे"),
        (_deva("मैं"), "हम"), (_deva("मुझे", "मुझको"), "हमरा"),
        (_deva("मेरा", "मेरी", "मेरे"), "हमार"),
        (_deva("तुम", "आप"), "तू / रउआ"),
        (_deva("यह", "वह", "ये", "वे"), "ई / ऊ"),
        (_deva("और"), "आ / अउर"), (_deva("लेकिन"), "बाकिर"),
        (_deva("क्या"), "का"), (_deva("क्यों"), "काहे"),
        (_deva("कैसे"), "कइसे"),
        # « कहाँ » WAS WIRED IN THEN WITHDRAWN BEFORE ITS FIRST USE.
        # Its repair carried the reported form — « कहाँ -> कहाँ /
        # कहवाँ » —, which is an impossible instruction to follow: the
        # word is Bhojpuri as much as Hindi, and a rule whose remedy
        # repeats the fault teaches nothing to whoever reads it.
        (_deva("बहुत"), "बहुते / खूब"),
        (_deva("किया", "किये", "किए"), "कइल / कइलें"),
        (_deva("गया", "गये", "गए"), "गइल / गइलें"),
        (_deva("आया", "आये", "आए"), "आइल / आइलें"),
        (_deva("लड़का", "लड़के", "लड़की"), "लइका / लइकी"),
        (_deva("आदमी"), "मनई / मरद"),
        (_deva("बड़ा", "बड़ी", "बड़े"), "बड़का"),
        (_deva("छोटा", "छोटी", "छोटे"), "छोटका"),
        (_deva("दरवाज़ा", "दरवाजा"), "केवाड़"),
        (_deva("अभी", "अब"), "अबहीं"),
        (_deva("यहाँ", "वहाँ", "यहां", "वहां"), "इहाँ / ओहिजा"),
    ], "exemptes": [
        # « आया » THE NURSEMAID IS NOT « आया » THE PAST OF « TO COME ».
        # The first is a noun, Portuguese (aia), and it is Bhojpuri as
        # much as Hindi; the second is the Hindi form the rule aims at,
        # where Bhojpuri says आइल. The two are written alike. Found on
        # table 14, where cross-reference (98) is the nursemaid — and that
        # is no reason to disarm the rule, which stays right everywhere
        # else: it is a reason to exempt THE WORD IN BOLD, which is the
        # only place the noun appears.
        "\\VUgras{आया}",
    ]},

    # AFRIKAANS AGAINST DUTCH, AND IT IS THE TEXTBOOK CASE.
    # The two neighbours of this transcription are the same language a
    # century and a half apart: Afrikaans comes out of the Dutch of the
    # Cape settlers, and text/nl is in the same directory. A Dutch
    # sentence is read effortlessly by whoever writes Afrikaans, and
    # that is exactly the situation of Bhojpuri before Hindi -- with
    # one difference, and it is decisive: HERE, THE DEFENCE IS ALSO
    # PLAYED OUT AT THE LETTER.
    #
    # THE DIGRAPH « ij » DOES NOT EXIST IN AFRIKAANS. Dutch has it
    # everywhere -- zijn, mijn, wij, tijd, altijd, vrij, kijken --, and
    # Afrikaans writes y: sy, my, ons, tyd, altyd, vry, kyk. A single
    # rule of two characters therefore reports a whole class of calques,
    # as the q of « quince » did for Hausa.
    #
    # NOR THE INITIAL « z ». Dutch says zijn, zitten, zien, zon, zee;
    # Afrikaans says is, sit, sien, son, see. The z is left to it only
    # in proper nouns and a few borrowings.
    #
    # AND « sch » AT THE START OF A WORD IS DUTCH: school, schoen,
    # schrijven give skool, skoen, skryf.
    #
    # WE DO NOT REPORT « het », WHICH IS AFRIKAANS. It is the auxiliary
    # of the past -- « ek het gesien » --, where Dutch uses it as an
    # article. The two are written alike and a rule on it would cry out
    # on every page. Nor do we report « een »: it is the Afrikaans
    # NUMERAL, where the article is « 'n ». Two words the spelling
    # confuses; it is the same reason that exempted « आया » above.
    "af": {"mot": [
        (r"(?<![A-Za-z])[A-Za-z]*ij[A-Za-z]*(?![A-Za-z])",
         "digramme « ij » — l'afrikaans ecrit y (zijn/is, tijd/tyd)"),
        (r"(?<![A-Za-z])z(?=[aeiouy])[A-Za-z]*(?![A-Za-z])",
         "« z » initial — l'afrikaans ecrit s (zien/sien, zon/son)"),
        (r"(?<![A-Za-z])sch[A-Za-z]*(?![A-Za-z])",
         "« sch » initial — l'afrikaans ecrit sk (school/skool)"),
        (r"(?<![A-Za-z])niet(?![A-Za-z])", "nie"),
        (r"(?<![A-Za-z])nu(?![A-Za-z])", "nou"),
        (r"(?<![A-Za-z])(?:heeft|hebben|hebt)(?![A-Za-z])", "het / hê"),
        (r"(?<![A-Za-z])(?:wordt|worden)(?![A-Za-z])", "word"),
        (r"(?<![A-Za-z])(?:de|der|den)(?![A-Za-z])",
         "die — l'afrikaans n'a qu'un article defini"),
        (r"(?<![A-Za-z])jullie(?![A-Za-z])", "julle"),
        (r"(?<![A-Za-z])meisje(?![A-Za-z])", "meisie"),
        (r"(?<![A-Za-z])jongen(?![A-Za-z])", "seun"),
        (r"(?<![A-Za-z])[A-Za-z]+tje(?:s)?(?![A-Za-z])",
         "diminutif neerlandais — l'afrikaans ecrit -tjie / -jie"),
        (r"(?<![A-Za-z])ook(?=\s+niet)", "ook nie"),
    ], "exemptes": [
        # « strooijonker » HAS NO DIGRAPH: IT HAS A JOIN.
        # The « ij » rule cried out at table 4 over the best man — and it
        # was right to the letter and wrong about the word. The compound
        # is « strooi » plus « jonker »: the i closes the first member,
        # the j opens the second, and the two touch only by accident of
        # the join. It is the same kind of trap as « piec » in Polish,
        # except that here the rule stays right everywhere else — it aims
        # at a digraph, and there is none here. We therefore exempt THE
        # FORM, not the rule.
        # « strooimeisie », the bridesmaid, does not raise the question:
        # its join falls between two vowels.
        "strooijonker",
    ]},

    # POLISH, AND ITS DEFENCE IS NOT AFRIKAANS'S.
    # None of its neighbours resembles it enough to contaminate it:
    # Czech is West Slavic as it is, but their alphabets part company to
    # the eye -- ě, ř, ů, č, š, ž, ď, ť, ň on one side; ą, ę, ł, ń, ó,
    # ś, ź, ż, cz, sz, rz on the other. A Czech word in this column
    # would be seen.
    #
    # THE DANGER IS ELSEWHERE, AND IT IS HAUSA'S: THE KEYBOARD.
    # Nine letters of Polish cannot be got without a combination, and a
    # hurried hand writes ksiazka, zolty, dzien, reka, stol where it
    # should be książka, żółty, dzień, ręka, stół. The fault does not
    # show: the word stays legible, it is merely wrong. We therefore
    # report the BARE forms of the words this booklet uses, and the list
    # lengthens table by table -- that is how the Hausa one was made.
    "pl": {"mot": [
        (r"[ěřůďťňĚŘŮ]",
         "lettre tcheque — cette colonne s'ecrit en polonais"),
        (r"(?<![A-Za-z])ksiazk\w*(?![A-Za-z])", "książka"),
        (r"(?<![A-Za-z])zolt\w*(?![A-Za-z])", "żółty"),
        (r"(?<![A-Za-z])dzien(?![A-Za-z])", "dzień"),
        (r"(?<![A-Za-z])rek[aę](?![A-Za-z])", "ręka"),
        (r"(?<![A-Za-z])stol(?![A-Za-z])", "stół"),
        (r"(?<![A-Za-z])krzeslo(?![A-Za-z])", "krzesło"),
        (r"(?<![A-Za-z])sciana(?![A-Za-z])", "ściana"),
        (r"(?<![A-Za-z])swiat\w*(?![A-Za-z])", "świat"),
        (r"(?<![A-Za-z])maly(?![A-Za-z])", "mały"),
        (r"(?<![A-Za-z])bial\w*(?![A-Za-z])", "biały"),
        (r"(?<![A-Za-z])dlug\w*(?![A-Za-z])", "długi"),
        (r"(?<![A-Za-z])glow\w*(?![A-Za-z])", "głowa"),
        (r"(?<![A-Za-z])wiecej(?![A-Za-z])", "więcej"),
        (r"(?<![A-Za-z])czesc(?![A-Za-z])", "część"),
        # « piec » IS NOT « pięć » AMPUTATED: IT IS THE STOVE.
        # The rule cried out at the very first table, over « \VUgras{piec}
        # \textsuperscript{(46)} » — and it was wrong. « piec » is a whole
        # Polish word, the stove and the verb to bake; « pięć » is five.
        # Two words that the loss of accents does not connect, since the
        # first never had any.
        # THE RULE OF LOST ACCENTS IS SURE ONLY WHERE THE BARE FORM IS NOT
        # ALREADY A WORD. That is the case of stol, dzien, reka, ksiazka,
        # czesc, glowa — none of them exists without its accents. It was
        # not the case of piec, and there is nothing to exempt: the rule
        # itself was wrong, we take it out.
    ]},
}

# THE THRESHOLD BEYOND WHICH A FILE IS A DIALOGUE. Measured on the
# sixteen Ido tables: 36 speech attributions on table 5, 1 on table
# 12 — and it is « Noto. » —, 0 everywhere else. Five therefore
# leaves the two cases on either side without pinching anything.
SPEECH = 5


# THE SCRIPTS THAT DO NOT MIX WITHIN A WORD. Two letters of two
# non-Latin scripts never meet inside one word: nobody writes a word
# half Arabic and half Tamil. When it happens, it is a typing fault
# that no other check can see — the line stays well formed, the
# LaTeX compiles, and the eye that does not read both scripts passes
# over it.
#
# MEASUREMENT BEFORE THE RULE: run over the 42 columns of text/, the
# check reports ZERO words, once the danda « । » is made neutral.
# That sign lives in the Devanagari block but serves Bengali,
# Gujarati, Telugu and Marathi: without this exception the check
# cried out at almost every Bengali sentence. The joiners U+200C and
# U+200D are neutral for the same reason.
SCRIPTS = [
    ("arabe", 0x0600, 0x06FF), ("devanagari", 0x0900, 0x097F),
    ("bengali", 0x0980, 0x09FF), ("gourmoukhi", 0x0A00, 0x0A7F),
    ("gujarati", 0x0A80, 0x0AFF), ("tamoul", 0x0B80, 0x0BFF),
    ("telougou", 0x0C00, 0x0C7F), ("kannada", 0x0C80, 0x0CFF),
    ("malayalam", 0x0D00, 0x0D7F), ("grec", 0x0370, 0x03FF),
    ("cyrillique", 0x0400, 0x04FF), ("hebreu", 0x0590, 0x05FF),
    ("han", 0x4E00, 0x9FFF), ("hangul", 0xAC00, 0xD7AF),
]
NEUTRAL = {0x0964, 0x0965, 0x200C, 0x200D}


def script_(c):
    o = ord(c)
    if o in NEUTRAL:
        return None
    for name_, start_, end_ in SCRIPTS:
        if start_ <= o <= end_:
            return name_
    return None


def byte(f, i, l, bad):
    """What cannot be text, headers included."""
    # THE REPLACEMENT CHARACTER. A U+FFFD slipped into block c4-08-1
    # of text/ur/15-jadval-06.tex, in place of an Urdu full stop.
    # None of the five tools saw it: cross_refs.py reads only the
    # order of the cross-references, columns.py read only the macros
    # and the words, html.py would have published it as it stood. A
    # replacement character is never intended: it is the trace of a
    # byte lost in passing from one encoding to another. We report
    # with it the C0 control characters, except the tab.
    for m in re.finditer(r"[\ufffd\x00-\x08\x0b-\x1f\x7f]", l):
        bad.append(f"{f}:{i} caractere impossible "
                       f"U+{ord(m.group(0)):04X} — octet perdu"
                       f" a la conversion")
    for word in l.split():
        views = {script_(c) for c in word}
        views.discard(None)
        if len(views) > 1:
            bad.append(f"{f}:{i} « {word} » mele "
                           f"{' et '.join(sorted(views))} dans un seul "
                           f"mot — faute de frappe")


def form(f, lg, bad):
    """The form checks, which hold for every column."""
    rule = REGISTER.get(lg, {})
    words = rule.get("mot", [])
    exempt = rule.get("exemptes", [])
    lines = f.read_text(encoding="utf-8").split("\n")
    # A FILE THAT SPEAKS IS NOT A FILE THAT NARRATES. The
    # « narration » rules apply only to the narrated tables: see
    # SPEECH, above, and the header of LANGUAGES.
    dialogue = sum(x.count("\\textsc{") for x in lines
                  if not x.startswith("%")) >= SPEECH
    if not dialogue:
        words = words + rule.get("narracio", [])
    # THE DRAFT WORD LEFT IN THE TEXT. Three times in the Urdu column
    # alone, twice in the Tamil, a French word was typed alone on its
    # line — « Wait », « Ordre » — while looking for its sentence, and
    # was not erased. cross_refs.py sees it only if the draft carried a
    # cross-reference; columns.py did not see it at all; html.py would
    # have published it in the middle of an Urdu paragraph.
    #
    # A wholly Latin line, alone, with neither macro nor punctuation,
    # cannot be text in a column that is not written in Latin letters.
    # We say so not from a list of languages but from the FILE: if it
    # has fewer than a tenth Latin letters, it is not Latin. Run over
    # the 42 columns, the check returns ZERO reports — the proper nouns
    # and the quotations of the facsimile are always inside a sentence,
    # never alone on their line.
    #  Macro names are Latin and there are some everywhere: we take
    #  them out before counting, failing which no file would be judged
    #  non-Latin. The first attempt at this check fell into that trap
    #  and reported nothing at all.
    size = "\n".join(x for x in lines if not x.startswith("%"))
    size = re.sub(r"\\[A-Za-z]+", "", size)
    letters = [c for c in size if c.isalpha()]
    latin = sum(1 for c in letters if ord(c) < 0x250)
    non_latin = bool(letters) and latin < len(letters) // 10
    for i, l in enumerate(lines, 1):
        # THE TWO CHECKS THAT FOLLOW LOOK AT THE BYTE, NOT THE
        # LANGUAGE, AND THEY THEREFORE PASS OVER THE COMMENTS TOO.
        # It is the only difference with all the rest of the file, and
        # it has been paid for twice: a U+FFFD in the body of
        # text/ur/15-jadval-06.tex, then an Arabic ک slipped into the
        # middle of a Tamil word quoted in the HEADER of
        # text/ur/17-jadval-08.tex. A header is read; it must
        # therefore be checked.
        byte(f, i, l, bad)
        if l.startswith("%"):
            continue
        for m in re.finditer(r"\\([A-Za-z]+)", l):
            if m.group(1) not in KNOWN:
                bad.append(f"{f}:{i} macro inconnue : \\{m.group(1)}")
        if "\\VUgras{}" in l:
            bad.append(f"{f}:{i} \\VUgras vide")
        if non_latin and re.fullmatch(r"[A-Za-z\u00c0-\u024f'\u2019-]+",
                                     l.rstrip()):
            bad.append(f"{f}:{i} « {l.strip()} » seul sur sa "
                           f"ligne dans une colonne non latine — "
                           f"mot de brouillon oublie ?")
        # A BRACE OPENED AT THE END OF A LINE: the line break is rendered
        # as a space, and the space then falls INSIDE the group.
        if re.search(r"\{\s*$", l):
            bad.append(f"{f}:{i} accolade ouverte en fin de ligne")
        # A CROSS-REFERENCE SET IN BOLD INSTEAD OF AS A SUPERSCRIPT. We
        # aim only at the CROSS-REFERENCE parenthesis: table 1 legitimately
        # sets « (ألماني وإنجليزي...) » in bold, parenthesis included.
        if re.search(r"\\VUgras\{\((?:\d{1,3}|[a-z])\)", l):
            bad.append(f"{f}:{i} renvoi en gras au lieu d'exposant")
        for pat, good in words:
            m = re.search(pat, l)
            if m and not any(e in l for e in exempt):
                bad.append(f"{f}:{i} forme etrangere « {m.group(0)} »"
                               f" -> {good}")
        # THE LATIN COMMA IN ARABIC PROSE: it cannot be seen by eye in a
        # text turned from right to left.
        if rule.get("virgule") and re.search(r"\}\s*,\s*$", l):
            bad.append(f"{f}:{i} virgule latine en arabe -> ،")
        if l.lstrip().startswith(("\\", "{")):
            continue
        if re.search(r"[^-]-$", l):
            bad.append(f"{f}:{i} trait d'union en fin de ligne")
        if len(l) > WIDTH_:
            bad.append(f"{f}:{i} ligne de {len(l)} caracteres")


def report_column(lg, word, bad):
    """Has a block lost text?

    SURGERY BY LINE NUMBER IS WHAT MADE THIS CHECK NECESSARY: three
    Marathi blocks lost a fragment of a sentence to it, and
    cross_refs.py saw only one of them — the one that had lost a
    cross-reference. We therefore compare the LENGTH of each block with
    that of its Ido counterpart, in characters, and take our bearings
    from the column's median: the ratio varies a great deal from one
    script to another — Chinese says in a hundred signs what Marathi
    says in three hundred — but it varies little from one block to
    another WITHIN one column. A block fallen below half the median has
    lost something.
    """
    io = cross_refs.blocks("io", "tabelo")
    tr = cross_refs.blocks(lg, word)
    if not tr:
        return
    def clean(t):
        return len(re.sub(r"\\[A-Za-z]+|[{}\s]|---", "", t))
    rap = {k: clean(v) / clean(io[k]) for k, v in tr.items()
           if k in io and clean(io[k]) > 60}
    if len(rap) < 20:
        return
    med = sorted(rap.values())[len(rap) // 2]
    for k, r in sorted(rap.items()):
        if r < med / 2:
            bad.append(f"  {k} : bloc a {r / med:.0%} de la longueur "
                           f"mediane de la colonne — texte perdu ?")


def hand(args):
    lgs = args or sorted(set(cross_refs.FOLDER) - TRANSCRIPTIONS)
    total = 0
    for lg in lgs:
        if lg not in cross_refs.FOLDER:
            raise SystemExit(f"  langue inconnue : {lg}")
        if lg in TRANSCRIPTIONS:
            raise SystemExit(f"  {lg} est une transcription, pas une "
                             f"traduction : elle suit le fac-simile.")
        d = ROOT / "text" / lg
        files_ = sorted(d.glob(f"*-{cross_refs.FOLDER[lg]}-*.tex"))
        if not files_:
            continue
        bad = []
        for f in files_:
            form(f, lg, bad)
        report_column(lg, cross_refs.FOLDER[lg], bad)
        for m in bad:
            print(m)
        total += len(bad)
        print(f"  {lg} : {len(files_):2d} fichiers, "
              f"{len(bad)} signalement{'s' if len(bad) > 1 else ''}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(hand(sys.argv[1:]))
