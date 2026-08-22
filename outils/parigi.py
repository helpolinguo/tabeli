#!/usr/bin/env python3
# ===================================================================
#  parigi.py — les paires de renvois qu'une langue a tete finale
#  sortira a l'envers si l'on n'y prend pas garde
#
#  CE N'EST PAS UN CONTROLE, C'EST UNE LISTE DE COURSES. renvoji.py
#  dit APRES COUP que deux renvois sont sortis dans le mauvais
#  ordre ; celui-ci le dit AVANT, en lisant l'ido seul. On s'en sert
#  en ouvrant le fichier, pas en le fermant.
#
#  D'OU IL VIENT. La colonne telougou a coute 2, 0, 9 puis 7
#  inversions aux tableaux 1 a 4, et le tableau 4 a fini par en
#  donner la cause exacte : ce n'est pas l'agglutination, c'est
#  l'ORDRE MODIFICATEUR-TETE. En telougou — comme en tamoul, en
#  coreen, en japonais, en ourdou, en persan, en goudjarati —, TOUT
#  ce qui qualifie precede ce qui est qualifie : l'adjectif, le
#  complement de nom, la relative, le participe, le groupe
#  instrumental. Donc des qu'un renvoi tombe sur un modificateur et
#  un autre sur sa tete, les deux sortent a l'envers, mecaniquement,
#  quelle que soit la phrase.
#
#  CE QU'IL RELEVE. Dans chaque bloc de l'ido, les couples de renvois
#  separes par un mot de RATTACHEMENT — di, dil, de, kun, qua, quan,
#  por, sur, en, an, proxim — c'est-a-dire ceux ou le second terme
#  qualifie le premier. Ce sont exactement les paires qu'il faut
#  retourner : poser la TETE d'abord, rejeter le modificateur
#  derriere, en apposition ou en relative detachee.
#
#  CE QU'IL NE RELEVE PAS, et c'est voulu : les enumerations. Deux
#  renvois separes par « e » ou une virgule ne sont pas en rapport
#  de dependance, et une langue a tete finale les rend dans l'ordre.
#  C'est pourquoi les tableaux qui enumerent — le marche, la rue —
#  coutent moins que ceux qui rattachent, dans TOUTES les langues du
#  releve : le constat vaut pour le cantonais comme pour le marathi.
#
#  CE QU'IL VAUT : le tableau 5 telougou, le plus long du livret, a
#  ete ecrit avec sa liste en main et n'a coute AUCUNE inversion au
#  premier jet, la ou les quatre precedents en avaient coute dix-huit.
#
#  USAGE
#      python3 outils/parigi.py 5          # les paires du tableau 5
#      python3 outils/parigi.py            # tous les tableaux
# ===================================================================

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
import renvoji                                              # noqa: E402

# LES MOTS QUI RATTACHENT. « di / dil » est le genitif, « de »
# l'origine ou la matiere, « kun » l'accompagnement, « qua / quan /
# di qua » la relative, et les prepositions de lieu font du second
# terme le cadre du premier. Tous produisent, en langue a tete
# finale, un modificateur AVANT sa tete.
LIENO = (r"\b(?:di|dil|de|kun|qua|quan|quin|qui|por|sur|en|an|sub|"
         r"super|proxim|avan|dop|inter|tra|per)\b"
         # ET LE PARTICIPE, QUI RATTACHE SANS PREPOSITION. « bubi (35)
         # preiranta la muzikisti (36) » n'a aucun mot-outil entre les
         # deux renvois, et c'est pourtant le meme rapport : ce qui
         # precede est la tete, ce qui suit la qualifie. Trois
         # inversions du releve tenaient a cette seule forme.
         r"|\b\w+(?:ant|int|ont)[aei]\b")

# La distance au-dela de laquelle deux renvois ne se rattachent plus.
# CALIBRE SUR LES INVERSIONS REELLEMENT COMMISES aux tableaux 3 et 4
# telougous, relevees par renvoji.py puis corrigees — dix-huit paires
# dont on connait la verite :
#
#     seuil 30 : 13 sur 18 trouvees, 29 lignes a lire
#     seuil 45 : 16 sur 18 trouvees, 55 lignes a lire
#     seuil 80 : 16 sur 18 trouvees, 88 lignes a lire
#
# On prend 45 : au-dela on paie soixante pour cent de lignes en plus
# sans rien trouver de neuf. LES DEUX QUI ECHAPPENT SONT NOMMEES,
# parce qu'un chiffre sans ses exceptions ne veut rien dire :
#
#   * « la avulo (33) obliviis, ke il esis malada, ke lua reumatismo
#     fixigas lu an sua stulego (34) » — soixante-dix-sept caracteres
#     et deux subordonnees entre les deux renvois. Hors d'atteinte de
#     toute fenetre honnete.
#   * « sua granda mantelo (4) e ledra zono (5) » — et celle-la n'est
#     PAS un rapport modificateur-tete : c'est une coordination, que
#     le telougou rend dans l'ordre. Si elle est sortie a l'envers,
#     c'est ma faute de redaction, pas celle de la langue, et l'outil
#     a raison de ne pas la signaler.
#
# Sur les DIX-SEPT paires qui sont vraiment des rapports
# modificateur-tete, il en trouve donc seize.
#
# CE N'EST DONC PAS UN CONTROLE EXHAUSTIF, et il ne pretend pas
# l'etre : renvoji.py reste l'autorite. Celui-ci fait gagner du
# temps, pas de la certitude.

PORTEO = 45


def _nu(t):
    """Le texte sans ses macros, pour mesurer une vraie distance."""
    t = re.sub(r"\\textsuperscript\{\(([^)]*)\)\}", r" ⟨\1⟩ ", t)
    t = re.sub(r"(?<!\w)\((\d{1,3}(?: bis)?|[a-z]{1,2})\)", r" ⟨\1⟩ ", t)
    t = re.sub(r"\\[A-Za-z]+", " ", t)
    t = t.replace("{", " ").replace("}", " ").replace("\\cc", " ")
    return re.sub(r"[ \t\n]+", " ", t)


def paires(corps):
    """[(a, b, le mot qui les rattache)] pour un bloc d'ido."""
    t = _nu(corps)
    marques = [(m.start(), m.end(), m.group(1))
               for m in re.finditer(r"⟨([^⟩]*)⟩", t)]
    out = []
    for (_a, fin, a), (deb, _b, b) in zip(marques, marques[1:]):
        entre = t[fin:deb]
        if len(entre) > PORTEO:
            continue
        lien = re.search(LIENO, entre)
        if lien:
            out.append((a, b, lien.group(0)))
    return out


def main(args):
    io = renvoji.blocs("io", "tabelo")
    vises = set(args)
    total = 0
    for cle in sorted(io):
        num = cle[1:3]
        if vises and num.lstrip("0") not in vises:
            continue
        p = paires(io[cle])
        if not p:
            continue
        print(f"  {cle}")
        for a, b, lien in p:
            print(f"      ({a}) ← {lien} ← ({b})"
                  f"      poser ({a}) d'abord, rejeter ({b}) derriere")
        total += len(p)
    print(f"\n  {total} paires a retourner"
          f"{' pour le tableau ' + ', '.join(sorted(vises)) if vises else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
