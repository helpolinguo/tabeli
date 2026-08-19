#!/usr/bin/env python3
# ===================================================================
#  objekti.py — le nom de chaque objet numerote, dans les deux langues.
#
#  « Nous avons imprime en caracteres gras les substantifs qui se
#  trouvent dans le vocabulaire des Tableaux EN LES FAISANT SUIVRE DE
#  LEUR NUMERO » : le liminaire francais donne lui-meme la regle, et
#  c'est elle qu'on lit ici. Chaque « (N) » du texte est precede du
#  substantif en gras qu'il numerote ; on releve donc le couple.
#
#  A QUOI CELA SERT. D'abord a savoir CE QUE montre un gros plan : un
#  clic sur « (15) » du tableau 13 ouvre la caisse, et la page peut le
#  dire. Ensuite, et surtout, a verifier les lectures douteuses du
#  lecteur de numeros : quand la machine hesite, on regarde la decoupe
#  et l'on demande si l'objet nomme s'y trouve. Un « (65) » lu sur une
#  hachure ne montre pas de bureau de tabac ; le nom tranche la ou la
#  forme du chiffre ne suffit plus.
#
#  UN NUMERO EST APPELE PLUSIEURS FOIS. Le texte y revient — « la
#  chambre (2) », puis « cette chambre (2) » — et pas toujours avec le
#  meme mot. On garde toutes les formes rencontrees, la premiere en
#  tete : c'est celle du releve initial, la plus descriptive.
#
#  USAGE
#      python3 outils/objekti.py            # ecrit gravuri/objekti.json
#      python3 outils/objekti.py 13         # montre le tableau 13
# ===================================================================

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Le substantif en gras, puis son numero — avec ou sans exposant, avec
# ou sans blanc entre les deux, le fac-simile hesitant sur les trois.
# TROIS FORMES DE RENVOI, et il a fallu les trois : « (18) », le groupe
# « (9, 11, 12) » qui vaut pour trois objets a la fois, et « 41) » ou la
# parenthese ouvrante manque. Le substantif se range sous chacun des
# numeros du groupe : « les tableaux muraux (9, 11, 12) » nomme les
# trois.
GRAS = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'      # \VUgras{...}
    r'(?:\s|\\nl|\\cc|%|\n)*'                   # coupures de ligne
    r'(?:\\textsuperscript\{'
    r'(\(?\s*\d{1,3}(?:\s*,\s*\d{1,3})*\s*,?'
    r'(?:\s*(?:\\textit\{)?bis\}?)?\s*\)?)\}'
    r'|\((\d{1,3}(?:\s*,\s*\d{1,3})*)\))')
CHIFRO = re.compile(r'\d{1,3}')
BIS = re.compile(r'\bbis\b')

# LES RENVOIS A LETTRE. « rondo (a), quadrato (b) » : la lettre est
# gravee sur l'objet qui la porte -- le tableau noir, la carte -- et
# n'a de sens que rapportee a lui. gravuri/literi.json dit, bloc par
# bloc, sous quel prefixe la ranger : le « a » du tableau noir est
# « 1a », celui de la carte « 10a ».
# LA LETTRE SE PRESENTE DE TROIS FACONS. Le francais la met en
# italique — « \textsuperscript{\textit{(a)}} » — l'ido la laisse nue,
# et six fois dans les deux livrets une des deux parentheses manque :
# « mi-sferi d) ». On accepte les trois, mais on exige AU MOINS UNE
# PARENTHESE : sans elle on rangerait sous « o » les « n° » du texte.
GRAS_LIT = re.compile(
    r'\\VUgras\{((?:[^{}]|\{[^{}]*\})*)\}'
    r'(?:\s|\\nl|\\cc|%|\n)*'
    r'(?:\\textsuperscript\{(?:\\textit\{)?'
    r'(?:\(([a-z]{1,2})\)?|([a-z]{1,2})\))\}?\}'
    r'|\(([a-z]{1,2})\))')


def literi(champo):
    f = RACINE / 'gravuri' / 'literi.json'
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding='utf-8')).get(champo, {})


PATRI = literi('patri')

# LE « (1) » QUI EST UN l. Au tableau 5, la salle de bains porte un
# renvoi compose « (1) » : dans cette fonte le l bas de casse et le
# chiffre 1 ont le meme dessin, et le plan de la maison tranche — sa
# legende porte « l. Balneyo ». Le nom irait donc se ranger sous le
# numero 1, qui est la facade ; on le range sous la lettre.
UNU_SORTO = literi('unu-sorto')


# LE RENVOI QUE LA PLANCHE NE PORTE PAS. « les plates-bandes (150) »,
# au tableau 5, sont gravees « 50 » : le nom doit se ranger sous le
# numero qu'on montrera, non sous celui qu'on lit. gravuri/korekti.json
# tient la table, et numeri.py la lit de meme.
def korekti():
    f = RACINE / 'gravuri' / 'korekti.json'
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(
        f.read_text(encoding='utf-8')).items() if not k.startswith('_')}


KOREKTI = korekti()

# LE SUBSTANTIF N'EST PAS TOUJOURS EN GRAS DEVANT UNE LETTRE. « la
# zoologio (a), botaniko (b), geologio (c) » : trois mots nus, alors
# que la regle du liminaire veut le gras. Les deux ateliers s'y
# tiennent pour les numeros et l'oublient pour les lettres. On
# reprend donc le mot qui precede, faute de mieux : sans lui le gros
# plan s'ouvrirait sans rien dire de ce qu'il montre.
NUD_LIT = re.compile(
    r"([\w'\u2019-]+)\s*(?:\\nl|\\cc)?\s*"
    r'\\textsuperscript\{\(([a-z]{1,2})\)\}')

# Ce qui reste de balisage dans le nom releve.
MACROS = re.compile(r'\\(?:textit|textsc|emph|VUgras|nl|cc|hbox|,)\b\{?')


def nettoyer(brut):
    t = MACROS.sub('', brut)
    t = t.replace('\\-', '').replace('~', ' ').replace('{', '').replace('}', '')
    t = re.sub(r'\s+', ' ', t).strip(' .,;:')
    # Un substantif coupe par un changement de ligne garde son trait
    # d'union du fac-simile ; il n'appartient pas au mot.
    return re.sub(r'-\s+', '', t)


# UN SUBSTANTIF COUPE PAR LA FIN DE LIGNE EST COMPOSE EN DEUX MORCEAUX,
# chacun dans son \VUgras — c'est la regle du releve, une ligne du
# fac-simile etant une ligne de la source. « \VUgras{jour}\cc /
# \VUgras{naux} » donnait donc « naux », et « \VUgras{livre}\nl /
# \VUgras{des voyageurs} » donnait « des voyageurs ». On recolle avant
# de lire : \cc a coupe un mot, \nl a coupe une locution.
RECOLLE = [
    (re.compile(r'\\VUgras\{([^{}]*)\}\\cc\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1\2}'),
    (re.compile(r'\\VUgras\{([^{}]*)\}\\nl\s*\n\s*\\VUgras\{([^{}]*)\}'),
     r'\\VUgras{\1 \2}'),
    # UN GROUPE COUPE PAR UNE FIN DE LIGNE est compose en deux exposants,
    # « (9, 11, » puis « 12) ». Sans ce recollage, le douze restait
    # orphelin et les tableaux muraux n'avaient que deux noms sur trois.
    (re.compile(r'\\textsuperscript\{([^{}]*,)\}\s*(?:\\nl|\\cc)?\s*\n?\s*'
                r'\\textsuperscript\{([^{}]*)\}'),
     r'\\textsuperscript{\1 \2}'),
]


def recoller(texte):
    for motif, remplacement in RECOLLE:
        avant = None
        while avant != texte:
            avant = texte
            texte = motif.sub(remplacement, texte)
    return texte


# LES PLANCHES A PLUSIEURS SCENES. Six tableaux montrent deux vignettes
# ou davantage, et chacune recommence sa numerotation a 1 : le « (39) »
# de la premiere scene et celui de la quatrieme ne nomment pas le meme
# objet. Le nom se range donc sous une cle qui porte la scene —
# « c1:39 » —, comme dans numeri.json. gravuri/ceni.json dit quels
# tableaux sont dans ce cas.
def a_ceni():
    f = RACINE / "gravuri" / "ceni.json"
    if not f.exists():
        return set()
    return {c[:3] for c in json.loads(f.read_text(encoding="utf-8"))
            if not c.startswith("_")}


CENI = a_ceni()


def relever(dossier, motif):
    """{numero de tableau: {cle d'objet: [noms]}} pour une langue."""
    out = {}
    for f in sorted((RACINE / "texto" / dossier).glob(motif)):
        m = re.search(r'-(?:tabelo|tableau)-(\d+)\.tex$', f.name)
        if not m:
            continue
        tab = int(m.group(1))
        par = out.setdefault(tab, {})
        scenes = f"t{tab:02d}" in CENI
        texte = recoller(f.read_text(encoding="utf-8"))
        # On coupe par cle de bloc, pour savoir de quelle scene on parle.
        parts = re.split(r'^%%K (\S+)', texte, flags=re.M)
        for i in range(1, len(parts), 2):
            mk = re.match(r't\d\d-(c\d)-', parts[i])
            if mk:
                relever.scene = mk.group(1)
            sc = getattr(relever, "scene", "") if scenes else ""
            # Les lettres du bloc, s'il en porte.
            pa = PATRI.get(parts[i])
            if pa:
                for g in GRAS_LIT.finditer(parts[i + 1]):
                    nom = nettoyer(g.group(1))
                    if not nom:
                        continue
                    for L in (g.group(2) or g.group(3)
                              or g.group(4) or ""):
                        k = pa[1] + L
                        noms = par.setdefault(k, [])
                        if nom not in noms:
                            noms.append(nom)
                for g in NUD_LIT.finditer(parts[i + 1]):
                    for L in g.group(2):
                        k = pa[1] + L
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
                # Le mot gras est parfois coupe en deux par la fin de
                # ligne — « salle » puis « de bains » — et la regle ne
                # nomme que le dernier morceau : on l'accepte en fin de
                # nom comme en nom entier.
                L = next((L for m, L in uniq
                          if nom == m or nom.endswith(" " + m)), None)
                if L:
                    k = pa[1] + L if pa else L
                    noms = par.setdefault(k, [])
                    if nom not in noms:
                        noms.append(nom)
                    continue
                ns = CHIFRO.findall(brut)
                # « 94 bis » ne nomme pas le 94 : c'est un objet a part.
                if ns and BIS.search(brut):
                    ns[-1] = f"{ns[-1]}bis"
                kor = KOREKTI.get(f"t{tab:02d}", {})
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


def construire():
    io = relever("io", "*-tabelo-*.tex")
    fr = relever("fr", "*-tableau-*.tex")
    tout = {}
    for tab in sorted(set(io) | set(fr)):
        par = {}
        for k in sorted(set(io.get(tab, {})) | set(fr.get(tab, {})), key=rang):
            par[k] = {"io": io.get(tab, {}).get(k, []),
                      "fr": fr.get(tab, {}).get(k, [])}
        tout[f"t{tab:02d}"] = par
    return tout


def attendus(tab):
    return set(relever("io", f"*-tabelo-{tab:02d}.tex").get(tab, {}))


def main(args):
    tout = construire()
    if args:
        tab = f"t{int(args[0]):02d}"
        for n, v in sorted(tout[tab].items(), key=lambda kv: rang(kv[0])):
            print(f"  {n:>6}  {' / '.join(v['io']) or '—':40s}  "
                  f"{' / '.join(v['fr']) or '—'}")
        return
    (RACINE / "gravuri" / "objekti.json").write_text(
        json.dumps(tout, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    for tab, par in sorted(tout.items()):
        att = attendus(int(tab[1:]))
        deux = sum(1 for v in par.values() if v["io"] and v["fr"])
        print(f"  {tab}  {len(par):3d}/{len(att):3d} objets nommes, "
              f"dont {deux:3d} dans les deux langues")
    n = sum(len(p) for p in tout.values())
    a = sum(len(attendus(int(t[1:]))) for t in tout)
    print(f"  TOTAL {n}/{a} = {100 * n // a} %")


if __name__ == "__main__":
    main(sys.argv[1:])
