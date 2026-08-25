#!/usr/bin/env python3
# ===================================================================
#  pair_up.py — the pairs of references a head-final language will bring
#  out reversed if one is not careful
#
#  THIS IS NOT A CHECK, IT IS A SHOPPING LIST. cross_refs.py says AFTER
#  THE FACT that two references came out in the wrong order; this one
#  says so BEFORE, by reading the Ido alone. It is used on opening the
#  file, not on closing it.
#
#  WHERE IT COMES FROM. The Telugu column cost 2, 0, 9 then 7 inversions
#  on tables 1 to 4, and table 4 finally gave the exact cause: it is not
#  agglutination, it is MODIFIER-HEAD ORDER. In Telugu — as in Tamil,
#  Korean, Japanese, Urdu, Persian, Gujarati — EVERYTHING that qualifies
#  precedes what is qualified: the adjective, the genitive, the relative
#  clause, the participle, the instrumental phrase. So as soon as one
#  reference falls on a modifier and another on its head, the two come out
#  reversed, mechanically, whatever the sentence.
#
#  WHAT IT SURVEYS. In each block of the Ido, the couples of references
#  separated by a word of ATTACHMENT — di, dil, de, kun, qua, quan, por,
#  sur, en, an, proxim — that is, those in which the second term qualifies
#  the first. Those are exactly the pairs to be reversed: lay the HEAD
#  first, throw the modifier behind, in apposition or in a detached
#  relative.
#
#  WHAT IT DOES NOT SURVEY, and that is intended: enumerations. Two
#  references separated by "e" or a comma are not in a relation of
#  dependence, and a head-final language renders them in order. That is
#  why the tables that enumerate — the market, the street — cost less than
#  those that attach, in ALL the languages of the survey: the observation
#  holds for Cantonese as for Marathi.
#
#  WHAT IT IS WORTH: table 5 in Telugu, the longest in the booklet, was
#  written with its list in hand and cost NO inversion at the first draft,
#  where the four preceding ones had cost eighteen.
#
#  USAGE
#      python3 tools/pair_up.py 5          # the pairs of table 5
#      python3 tools/pair_up.py            # every table
# ===================================================================

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cross_refs                                              # noqa: E402

# THE WORDS THAT ATTACH. "di / dil" is the genitive, "de" origin or
# material, "kun" accompaniment, "qua / quan / di qua" the relative, and
# the prepositions of place make the second term the setting of the
# first. All produce, in a head-final language, a modifier BEFORE its
# head.
LINK_TPL = (r"\b(?:di|dil|de|kun|qua|quan|quin|qui|por|sur|en|an|sub|"
         r"super|proxim|avan|dop|inter|tra|per"
         # AND "ube", THE RELATIVE ADVERB OF PLACE, which is of the same
         # family as "qua" and which the first draft had forgotten: "la
         # planajo (39) ube flugeskas la alaudi (41)" is a relative
         # qualifying the plain, exactly like "qua". One inversion in table
         # 8 in Telugu hung on that word alone.
         # We do NOT add "kande" or "dum": those introduce an adverbial
         # clause, not a modifier of a noun, and the second inversion of the
         # same table — "the fish takes the hook as soon as they cast their
         # line" — was not a modifier-head relation but a choice of wording.
         r"|ube)\b"
         # AND THE PARTICIPLE, WHICH ATTACHES WITHOUT A PREPOSITION. "bubi (35)
         # preiranta la muzikisti (36)" has no function word between the two
         # references, and yet it is the same relation: what precedes is the
         # head, what follows qualifies it. Three inversions in the survey hung
         # on this form alone.
         #
         # THE PASSIVE PARTICIPLE ATTACHES EXACTLY AS THE ACTIVE DOES, and the
         # first draft had taken only half the paradigm. "porto-triciklo (80)
         # duktata da grumo (79)", "tamburestro (42) sequata da la tamburisti
         # (43)", "kontoristo (22) komisita pri la ponder-aparato (21)": same
         # relation, same inversion, and the list said nothing of it.
         # Measurement: the booklet goes from 386 to 408 pairs — six per cent
         # more lines for twenty-two attachments of which eighteen are
         # attributive. Compare with the REACH threshold below, which we
         # REFUSED to widen: there it was twenty per cent more lines for two
         # pairs. It is not the principle that differs, it is the ratio.
         #
         # THE MINIMUM OF TWO LETTERS before the ending is not ornament:
         # without it the pattern takes "tota", "tote", "poti", "pinti" — an
         # adjective, an adverb and two nouns that end like participles. Four
         # named noises, four noises removed, no attachment lost.
         r"|\b\w{2,}(?:ant|int|ont|at|it|ot)[aei]\b")

# The distance beyond which two references no longer attach.
# CALIBRATED ON THE INVERSIONS ACTUALLY COMMITTED in tables 3 and 4 in
# Telugu, reported by cross_refs.py and then corrected — eighteen pairs
# whose truth we know:
#
#     threshold 30: 13 of 18 found, 29 lines to read
#     threshold 45: 16 of 18 found, 55 lines to read
#     threshold 80: 16 of 18 found, 88 lines to read
#
# We take 45: beyond that one pays sixty per cent more lines without
# finding anything new. THE TWO THAT ESCAPE ARE NAMED, because a figure
# without its exceptions means nothing:
#
#   * "la avulo (33) obliviis, ke il esis malada, ke lua reumatismo
#     fixigas lu an sua stulego (34)" — seventy-seven characters and two
#     subordinate clauses between the two references. Beyond the reach
#     of any honest window.
#   * "sua granda mantelo (4) e ledra zono (5)" — and that one is NOT a
#     modifier-head relation: it is a coordination, which Telugu renders
#     in order. If it came out reversed, that is my fault of wording,
#     not the language's, and the tool is right not to report it.
#
# Of the SEVENTEEN pairs that really are modifier-head relations, it
# therefore finds sixteen.
#
# SECOND MEASUREMENT, TAKEN AFTERWARDS ON TABLES 10 AND 11 IN TELUGU.
# Eleven tables written with the list in hand produced exactly TWO
# inversions it had not seen, and both for the same reason: distance.
#
#     "ponteto (20), qua komunikigas la parad-esplanado kun
#       l'arsenalo (21)"            54 characters  (table 10)
#     "Tribunalo (22) avan qua extensas su agreabla gardeno
#       publika (26)"               47 characters  (table 11)
#
# The pattern itself let nothing through: in both cases the word of
# attachment is "qua", already in LINKERS. Raising REACH to 55 would
# catch them both — and would take the whole booklet from 408 pairs to
# 490, that is twenty per cent more lines. We do not do it:
# cross_refs.py caught them both at the first draft, and a shopping list
# that doubles in length ceases to be a shopping list. The threshold
# stays at 45, but both distances are written here so that whoever
# hesitates next has the figure.
#
# THIS IS THEREFORE NOT AN EXHAUSTIVE CHECK, and it does not claim to be:
# cross_refs.py remains the authority. This one saves time, not
# certainty.

SCOPE = 45


# "\cc" IS NOT A BREAK, IT IS A WELD. The facsimile breaks its words at
# the end of a line, and the transcription notes it "\cc" followed by a
# newline: "ku\cc\nranta" is ONE word, not two. The first draft stripped
# the macros one by one and therefore left "ku ranta" — hence six pairs
# of the survey held by FRAGMENTS that looked like participles: ranta,
# sante, mante, vinta, dante, danta. They were right by accident; we now
# hold them for good reasons — ekiranta, impulsante, arivinta, fumante,
# ludante, sidanta. The rejoining must be done BEFORE the general
# stripping, or the macro has already become a space.
#
# AND THE BREAK OFTEN FALLS IN THE MIDDLE OF A BOLD PASSAGE, which the
# first rejoining did not cross: "\VUgras{voya}\cc\n\VUgras{jonti}"
# still gave "voya jonti", because the closing brace and the reopened
# macro separated the two halves. We therefore eat the group boundary
# too, and "voyajonti" becomes one word again. (Table 12 had concluded
# that this remnant was irreducible for a morphological reason; the
# reason was good but it was not the only one, and this one could be
# corrected.)
_BYTES = re.compile(r"\}?\\cc(?:plein)?(?![A-Za-z])[ \t\n]*"
                    r"(?:\\(?:VUgras|textit|textbf)\{)?")


def _nu(t):
    """The text without its macros, to measure a real distance."""
    t = _BYTES.sub("", t)
    t = re.sub(r"\\textsuperscript\{\(([^)]*)\)\}", r" ⟨\1⟩ ", t)
    t = re.sub(r"(?<!\w)\((\d{1,3}(?: bis)?|[a-z]{1,2})\)", r" ⟨\1⟩ ", t)
    t = re.sub(r"\\[A-Za-z]+", " ", t)
    t = t.replace("{", " ").replace("}", " ")
    return re.sub(r"[ \t\n]+", " ", t)


def pairs(size):
    """[(a, b, the word that attaches them)] for a block of Ido."""
    t = _nu(size)
    marks = [(m.start(), m.end(), m.group(1))
               for m in re.finditer(r"⟨([^⟩]*)⟩", t)]
    out = []
    for (_a, end_, a), (beg, _b, b) in zip(marks, marks[1:]):
        between = t[end_:beg]
        if len(between) > SCOPE:
            continue
        link_ = re.search(LINK_TPL, between)
        if link_:
            out.append((a, b, link_.group(0)))
    return out


def hand(args):
    io = cross_refs.blocks("io", "tabelo")
    aimed_ = set(args)
    total = 0
    for key in sorted(io):
        num = key[1:3]
        if aimed_ and num.lstrip("0") not in aimed_:
            continue
        p = pairs(io[key])
        if not p:
            continue
        print(f"  {key}")
        for a, b, link_ in p:
            print(f"      ({a}) ← {link_} ← ({b})"
                  f"      poser ({a}) d'abord, rejeter ({b}) derriere")
        total += len(p)
    print(f"\n  {total} paires a retourner"
          f"{' pour le tableau ' + ', '.join(sorted(aimed_)) if aimed_ else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(hand(sys.argv[1:]))
