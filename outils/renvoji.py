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
#  USAGE
#      python3 outils/renvoji.py            # toutes les colonnes
#      python3 outils/renvoji.py hi         # une seule
# ===================================================================

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Le nom que chaque colonne donne a « tableau » dans ses fichiers.
DOSSIER = {"fr": "tableau", "en": "table", "es": "cuadro", "ru": "tablica",
           "zh": "tubiao", "ar": "lawha", "hi": "talika",
           "pt": "quadro", "bn": "sarani", "ja": "zuhyo",
           "pnb": "naqsha", "pa": "sarni", "tr": "tablo",
           "eo": "tabelo", "ia": "tabella",
           "nl": "tabel", "sv": "tabell",
           "fi": "taulukko", "ca": "taula",
           "oc": "taula", "uk": "tablycia",
           "eu": "taula", "ro": "tabelul",
           "ga": "tabla", "gl": "cadro",
           "cs": "tabulka"}

# LE FRANCAIS N'EST PAS UNE TRADUCTION. C'est le releve d'une AUTRE
# edition, et Rochelle ordonne ses phrases comme il l'entend :
# quarante-cinq blocs y divergent de l'ido, et pas un n'est une faute.
# On ne le controle donc pas.
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
    d = RACINE / "texto" / dossier
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
