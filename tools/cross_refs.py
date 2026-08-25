#!/usr/bin/env python3
# ===================================================================
#  renvoji.py — les renvois d'une traduction suivent-ils l'ordre de
#  l'ido ?
#
#  LE RENVOI EST UN RENDEZ-VOUS. La colonne de gauche porte le livret
#  ido, et chaque « (n) » y ouvre le gros plan d'un objet de la
#  planche. Une traduction doit viser les MEMES objets, dans le MEME
#  ordre : le lecteur qui suit les deux colonnes du regard veut
#  retrouver le (18) en face du (18).
#
#  L'ORDRE N'EST PAS UN DETAIL DE FORME. Une langue qui postpose ce
#  que l'ido antepose deplace le substantif, et le renvoi le suit :
#  « अध्यापक (7) अपने मंच (6) पर कुर्सी (8) पर » donne 7, 6, 8 la ou
#  l'ido donne 7, 8, 6. Le remede n'est jamais de deplacer le renvoi —
#  il appartient a son mot — mais de refaire la phrase autour. Onze
#  inversions relevees dans le seul hindi, dix dans les cinq
#  traductions deja servies.
#
#  LE RENVOI NE S'ECRIT PAS TOUJOURS EN EXPOSANT. Le releve ido compose
#  parfois « (80) » a plein corps — le nom du parleur, au tableau 5 —
#  et html.py le rend en renvoi comme les autres. On releve donc les
#  deux formes, sans quoi le tableau 5 sortait faux de part en part.
#
#  LES ECARTS DECLARES. Trois blocs divergent de l'ido dans les six
#  traductions a la fois, et c'est voulu : le fac-simile ido s'y trompe
#  et le francais a raison. On les nomme ci-dessous avec leur raison,
#  et le controle les passe. Tout le reste est une faute.
#
#  ET LE FRANCAIS, QU'ON NE CONTROLE PAS EN ORDRE, SE CONTROLE EN
#  VALEUR. Rochelle ordonne ses phrases comme il l'entend, mais il
#  vise les MEMES OBJETS : le numero grave sur la planche est le meme
#  pour les deux editions. Quand un bloc porte de part et d'autre le
#  meme NOMBRE de renvois et pas les memes, ce n'est plus un ordre
#  different, c'est une SUBSTITUTION — et sept dormaient la depuis le
#  premier relevé : 24 pour 21, 16 pour 46, 140 pour 146, 11 pour 41,
#  14 pour 44, 19 pour 49, 32 pour 82. Cinq ouvraient en silence le
#  gros plan d'un autre objet ; deux n'ouvraient rien. Voir
#  substitui().
#
#  USAGE
#      python3 tools/renvoji.py            # toutes les colonnes
#      python3 tools/renvoji.py hi         # une seule
#      python3 tools/renvoji.py fr         # les substitutions
# ===================================================================

import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

_KOR = RACINE / "plates" / "corrections.json"
KOREKTI = ({k: v for k, v in
            json.loads(_KOR.read_text(encoding="utf-8")).items()
            if not k.startswith("_")} if _KOR.exists() else {})

# Le nom que chaque colonne donne a « tableau » dans ses fichiers.
DOSSIER = {"fr": "tableau",
           # LE MEME JETON QUE LE FRANCAIS : le mot est le meme des deux
           # cotes de l'Atlantique, et le glob se fait DANS le dossier de
           # la langue — text/fr et text/fr-CA ne se melent pas.
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
           # LE CANTONAIS prend « toubiu », qui est « 圖表 » en
           # jyutping depouille de ses tons — tou4 biu2. Il ne se
           # confond pas avec le « tubiao » du mandarin : ce sont
           # les deux lectures du meme mot, et deux colonnes.
           "yue": "toubiu",
           # MEME JETON QUE L'ARABE STANDARD : « لوحة » s'ecrit et se
           # dit de la meme facon au Caire, et le glob se fait DANS le
           # dossier de la langue — text/ar et text/arz ne se melent
           # pas, comme text/fr et text/fr-CA.
           "arz": "lawha",
           # LE MARATHI dit « तक्ता », non « तालिका » : le jeton
           # est donc « takta » et non celui du hindi.
           "mr": "takta",
           # LE TELOUGOU DIT « పట్టిక » pour un tableau.
           "te": "pattika",
           # LE COREEN DIT « 도표 » — dopyo. Le « 표 » seul serait le
           # mot le plus banal de la langue ; le compose ne l'est pas.
           "ko": "dopyo",
           # LE TAMOUL DIT « அட்டவணை » — attavanai. Le telougou
           # voisin dit « పట్టిక » : deux langues dravidiennes, deux
           # mots, et c'est encore une raison de traduire chaque
           # colonne pour elle-meme.
           "ta": "attavanai",
           # L'OURDOU DIT « جدول » — jadval. Le pendjabi chahmoukhi,
           # qui partage son alphabet, dit « نقشہ » : meme ecriture,
           # deux langues, deux mots d'apparat.
           "ur": "jadval",
           # L'INDONESIEN DIT « bagan » pour un tableau figure. Le
           # « tabel » qu'on aurait pris d'abord est celui du
           # neerlandais, deja dans cette table — et l'indonesien l'a
           # justement emprunte au neerlandais. On garde donc le mot
           # malais de fond, qui ne doit rien a personne.
           "id": "bagan", "jv": "gambar", "fa": "tablo",
           "ha": "hoto",
           "gu": "kostak",
           "apc": "lawha",
           "bho": "nakasa",
           "de": "tafel",
           "it": "tavola",
           # LE POLONAIS DIT « tablica », comme le russe transcrit --
           # et le glob se fait DANS le dossier de la langue, si bien
           # que text/pl et text/ru ne se melent pas, comme text/fr
           # et text/fr-CA.
           "pl": "tablica",
           # L'AFRIKAANS DIT « tabel », comme le neerlandais. Meme
           # jeton, autre dossier : c'est deja le cas de l'arabe
           # standard et de l'egyptien.
           "af": "tabel"}

# LE FRANCAIS N'EST PAS UNE TRADUCTION. C'est le releve d'une AUTRE
# edition, et Rochelle ordonne ses phrases comme il l'entend :
# quarante-cinq blocs y divergent de l'ido, et pas un n'est une faute.
# On ne lui applique donc pas le controle d'ordre — mais « pas celui-ci »
# n'a jamais voulu dire « aucun », et c'est pourtant ce que cette ligne
# a fini par signifier : le francais est reste seul non controle, et
# sept substitutions y ont vecu jusqu'a la tache 3. Il a le sien,
# substitui(), et main() le passe avec les autres.
TRADUKTI = [k for k in DOSSIER if k != "fr"]

# ECARTS DECLARES : {cle de bloc: raison}
APARTA = {
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

RENVOJO = re.compile(r"\\textsuperscript\{\(([^)]*)\)\}"
                     r"|\((\d{1,3}(?:\s*(?:\\textit\{)?bis\}?)?)\)")


def renvois(t):
    return [re.sub(r"\\[a-z]+|[{}\s]", "", m.group(1) or m.group(2))
            for m in RENVOJO.finditer(t)]


def blocs(dossier, mot):
    """{cle de bloc: corps}, les blocs « suite » recolles au premier."""
    out = {}
    d = RACINE / "text" / dossier
    if not d.is_dir():
        return out
    for f in sorted(d.glob(f"*-{mot}-*.tex")):
        # Le commentaire s'ote, mais « %%K » est une cle, non un
        # commentaire : le retirer effacait tout le decoupage.
        t = re.sub(r"^%(?!%K).*\n", "", f.read_text(encoding="utf-8"),
                   flags=re.M)
        parts = re.split(r"^%%K (\S+)[^\n]*\n", t, flags=re.M)
        for i in range(1, len(parts), 2):
            out.setdefault(parts[i], []).append(parts[i + 1])
    return {k: "\n".join(v) for k, v in out.items()}


def korekti_renvojo(cle):
    """{lu: a lire} pour UN BLOC — la meme lecture que html.py fait de
    plates/corrections.json : les corrections du tableau entier, plus
    celles que ce bloc-ci porte seul."""
    t = KOREKTI.get(cle[:3], {})
    out = {k: v for k, v in t.items() if isinstance(v, str)}
    out.update(t.get(cle, {}))
    return out


def substitui(verbeux=True):
    """Les numeros ou le francais et l'ido ne montrent pas le meme objet.

    LE MEME COMPTE ET PAS LES MEMES VALEURS, c'est une substitution.
    C'est tout le controle, et sa force tient a ce qu'il ne demande
    rien d'autre. Comparer les SUITES aurait signale les quarante-cinq
    blocs que Rochelle reordonne ; comparer les ENSEMBLES par planche
    n'en voyait que deux sur sept, parce qu'un « 24 » mis pour « 21 »
    existe ailleurs sur la meme planche et se fond dans l'ensemble.
    L'egalite des comptes ecarte d'un coup tout le bruit — le bloc que
    le francais coupe en deux quand l'ido le coupe en « suite », l'appel
    de note « (1) » qu'une seule des deux editions porte — sans qu'on
    ait rien a declarer : ces cas-la changent le compte.

    ON CORRIGE LES DEUX COLONNES, non la seule qu'on soupconne. Le
    « (150) » du tableau 5 est une faute de l'IDO, et corrections.json la
    repare ; ne passer la correction que sur le francais faisait
    reapparaitre en substitution ce qui venait d'etre corrige.
    """
    io = blocs("io", "tabelo")
    fr = blocs("fr", "tableau")
    faux = []
    for k, v in fr.items():
        if k in APARTA or k not in io:
            continue
        m = korekti_renvojo(k)
        a = Counter(m.get(x, x) for x in renvois(io[k]))
        b = Counter(m.get(x, x) for x in renvois(v))
        if sum(a.values()) == sum(b.values()) and a != b:
            faux.append((k, sorted(a - b), sorted(b - a)))
    if verbeux:
        for k, a, b in faux:
            print(f"  {k}\n     io {a}\n     fr {b}")
    return len(fr), len(faux)


def controlar(lg, verbeux=True):
    io = blocs("io", "tabelo")
    tr = blocs(lg, DOSSIER[lg])
    if not tr:
        return None
    faux = []
    for k, v in tr.items():
        if k in APARTA:
            continue
        if k not in io:
            faux.append((k, None, renvois(v)))
            continue
        a, b = renvois(io[k]), renvois(v)
        if a != b:
            faux.append((k, a, b))
    faits = {k[:3] for k in tr}
    manq = [k for k in io if k[:3] in faits and k not in tr]
    if verbeux:
        for k, a, b in faux:
            print(f"  {k}\n     io {a if a is not None else '— cle inconnue'}"
                  f"\n     {lg} {b}")
        for k in manq:
            print(f"  {k} : bloc absent de la colonne {lg}")
    return len(tr), len(faux) + len(manq), len(faits)


def main(args):
    lgs = args or TRADUKTI
    total = 0
    # LE FRANCAIS PASSE EN PREMIER ET PAR UN AUTRE CONTROLE. On le
    # nomme comme les autres — « renvoji.py fr » — mais ce qu'on lui
    # demande n'est pas l'ordre : c'est que les deux editions montrent
    # le meme objet.
    if not args or "fr" in args:
        n, f = substitui()
        print(f"  fr : {n:4d} blocs, {f} substitution{'s' if f > 1 else ''}")
        total += f
        lgs = [lg for lg in lgs if lg != "fr"]
        if args and not lgs:
            print(f"\n  {len(APARTA)} ecarts declares, passes sans rien dire.")
            return 1 if total else 0
    for lg in lgs:
        if lg not in DOSSIER:
            raise SystemExit(f"  langue inconnue : {lg}")
        r = controlar(lg)
        if r is None:
            print(f"  {lg} : rien a controler")
            continue
        n, f, tab = r
        total += f
        print(f"  {lg} : {n:4d} blocs sur {tab:2d} tableaux, "
              f"{f} divergence{'s' if f > 1 else ''}")
    print(f"\n  {len(APARTA)} ecarts declares, passes sans rien dire.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
