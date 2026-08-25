#!/usr/bin/env python3
"""Tire des Tabeli leurs versions LISIBLES PAR LES MACHINES.

POURQUOI. La page pese 3,3 Mo pour 257 Ko de texte : treize octets de
balisage pour un de texte. Le tableau porte 683 entrees en 57 langues, et
c'est justement sa richesse qui le rend illisible a la machine — les
53 langues autres que l'ido et le francais sont des cellules VIDES que le
navigateur remplit ensuite depuis lingui/*.json.

LE POINT QUI COMPTE : les cles des rangees (data-cle) sont EXACTEMENT
celles des fichiers de langue. Publier les paires ido/francais sous ces
memes cles rend donc tout le corpus joignable par programme : qui veut le
couple ido-japonais joint tabeli.json et lingui/ja.json sur la cle, sans
avoir a ouvrir la page ni a executer son JavaScript.

  tabeli.json       {cle: {io, fr}} — la charniere du corpus.
  tabeli.md         le tableau a plat, ido et francais en regard.
  lingui/index.json les 57 langues offertes, avec leur code et leur poids.

Engendres, jamais edites a la main. La source reste index.html.

    python3 tools/robotoj.py
"""

import json
import os
import re
import sys
from pathlib import Path

# Ce dossier porte son propre « html.py », qui masquerait le module standard.
sys.path[:] = [d for d in sys.path
               if os.path.abspath(d) != os.path.dirname(os.path.abspath(__file__))]
import html as modul_html  # noqa: E402
from html.parser import HTMLParser  # noqa: E402

RACINO = Path(__file__).resolve().parent.parent
ENTETE = '<!-- Engendre par tools/robotoj.py depuis index.html. Ne pas editer. -->\n'
FONTO = 'Transskribita de https://ido.help/tabeli/\n'


def texto(h: str) -> str:
    """Un fragment de HTML en texte simple.

    Les « ln » sont des LIGNES du livre imprime, non des phrases : le
    tableau original est compose en colonnes etroites, et une phrase y
    tient sur trois ou quatre lignes. On les rejoint par une espace,
    faute de quoi le texte rendu serait hache la ou le livre ne l'est
    pas — un artefact de mise en page, pas du texte.
    """
    h = re.sub(r'<span class="fil"></span>', '', h)
    h = re.sub(r'<i>(.*?)</i>', r'*\1*', h, flags=re.S)
    h = re.sub(r'<b>(.*?)</b>', r'**\1**', h, flags=re.S)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = modul_html.unescape(h)
    return re.sub(r'\s+', ' ', h).strip()


class Rangi(HTMLParser):
    """Ramasse les rangees du tableau, et pour chacune l'ido et le francais.

    On compte la profondeur plutot que de chercher le « /div » fermant :
    une cellule contient des « span », et parfois d'autres « div ».
    """

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.rangi, self.nuna, self.profundo = [], None, 0
        self.celo, self.peci = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        kl = (a.get('class') or '').split()
        if self.nuna is None:
            if tag == 'div' and 'r' in kl and a.get('data-cle'):
                self.nuna = {'cle': a['data-cle'],
                             'speco': next((k for k in kl if k != 'r'), ''),
                             'io': '', 'fr': ''}
                self.profundo = 1
            return
        if tag == 'div':
            self.profundo += 1
            if 'k' in kl and 'vaka' not in kl:
                self.celo = 'io' if 'io' in kl else (
                    'fr' if a.get('data-lg') == 'fr' else None)
                self.peci = []
                return
        if self.celo:
            self.peci.append(self.get_starttag_text() or '')

    def handle_endtag(self, tag):
        if self.nuna is None:
            return
        if tag == 'div':
            self.profundo -= 1
            if self.celo and self.profundo >= 1:
                self.nuna[self.celo] = texto(''.join(self.peci))
                self.celo = None
                return
            if self.profundo == 0:
                self.rangi.append(self.nuna)
                self.nuna = None
                return
        if self.celo:
            self.peci.append('</%s>' % tag)

    def handle_data(self, d):
        if self.celo:
            self.peci.append(d)

    def handle_entityref(self, n):
        if self.celo:
            self.peci.append('&%s;' % n)

    def handle_charref(self, n):
        if self.celo:
            self.peci.append('&#%s;' % n)


def main() -> None:
    s = (RACINO / 'index.html').read_text(encoding='utf-8')
    korpo = re.search(r'<main\b.*?</main>', s, re.S)
    p = Rangi()
    p.feed(korpo.group(0) if korpo else s)
    rangi = [r for r in p.rangi if r['io'] or r['fr']]

    # 1. La charniere du corpus.
    (RACINO / 'tabeli.json').write_text(
        json.dumps({r['cle']: {'io': r['io'], 'fr': r['fr']} for r in rangi},
                   ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    # 2. Le tableau a plat.
    lin = [ENTETE, '# Expliko-Libreto di la Delmas-Tabeli helpanta\n',
           'J. Guignon · Ido-Kontoro, Thaon-les-Vosges, 1926 · '
           'E. Rochelle · G. Delmas, Bordeaux\n', FONTO,
           'Ido e Franca en regardo. La 55 altra lingui esas en lingui/*.json, '
           'kun la sama klefi.\n', '---\n',
           '| klefo | Ido | Franca |', '| --- | --- | --- |']
    for r in rangi:
        io = r['io'].replace('|', '\\|')
        fr = r['fr'].replace('|', '\\|')
        lin.append('| `%s` | %s | %s |' % (r['cle'], io, fr))
    (RACINO / 'tabeli.md').write_text('\n'.join(lin) + '\n', encoding='utf-8')

    # 3. Les langues offertes.
    lingui = RACINO / 'lingui'
    listo = sorted(f.name[:-5] for f in lingui.glob('*.json')
                   if f.name != 'index.json')
    (lingui / 'index.json').write_text(json.dumps(
        {'pri': 'Lingui dil Delmas-Tabeli. La klefi esas ti di tabeli.json.',
         'fonto': 'https://ido.help/tabeli/',
         'enshaltita': {'io': 'en index.html e tabeli.json',
                        'fr': 'en index.html e tabeli.json'},
         'lingui': [{'kodexo': k,
                     'okteti': (lingui / (k + '.json')).stat().st_size}
                    for k in listo]},
        ensure_ascii=False, indent=1), encoding='utf-8')

    print('  %d rangees' % len(rangi))
    for n in ('tabeli.json', 'tabeli.md'):
        print('  %-16s %10s octets' % (n, format((RACINO / n).stat().st_size, ',')))
    print('  lingui/index.json  %d langues' % len(listo))


if __name__ == '__main__':
    main()
