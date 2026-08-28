#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Draws from the Tabeli a GLOSSARY: the Ido term beside its equivalent in
each of the 56 other languages.

WHY. Nothing on this site answers « what is the Ido for X ». The Dicionario
defines Ido in Ido and the Gramatiko is in Ido throughout, so the only place
where Ido stands beside another language is this booklet -- and it stands
there as PROSE. A program that wanted the English for « katedro » had to
fetch two files of 137 kB, find the segment, and align two sentences itself.

WHAT MAKES IT POSSIBLE. The two booklets set the same thing in bold: the
vocabulary word the wall table illustrates. bold_diff.py exists because that
correspondence is checked leaf by leaf. So the n-th bold run of a segment
answers the n-th bold run of the same segment in any language, and the pairs
fall out by POSITION -- no alignment is guessed at, and no gloss is composed
here. Every pair is two passages of a printed parallel text.

WHERE IT REFUSES. Three guards, and each one drops rather than guesses:

  * THE COUNTS MUST ANSWER. Where a segment carries five bold runs in Ido
    and four in the target, the whole segment is dropped -- there is no way
    to know which one is missing. MEASURED on en-GB: 44 segments of 672,
    317 of the 2320 runs.
  * A RUN HOLDING A COMMA IS A LIST, NOT A TERM. « geometrio, aritmetiko,
    kalkulo » is three words the printing bolded in one stroke. Both sides
    are split, and paired only if both split into the same number. That
    guard is what wins the language names of t01-04-1, where the printing
    set « (Germana, Angla, Hispana, Italiana, Rusa » and « Franca) » as two
    runs across a parenthesis.
  * A RUN HOLDING A SENTENCE BREAK IS AN ARTEFACT. « indolenti. Albertus »
    is two things the transcription ran together; it is dropped.

THE PUNCTUATION IS INSIDE THE BOLD, AND THE README SAYS IT SHOULD NOT BE.
§ *A translation is not a transcription* asks that the bold fall on the term
alone. It does not, in the source: 201 of the 2320 runs carry a mark, and
« liceo. », « (liceestro) », « Ludovikus, » are the ordinary case. The marks
are trimmed from the EDGES of a term here, and nowhere else -- the source is
not touched.

    python3 tools/glosaro.py

Run it after tools/machine_readable.py: it reads tabeli.json and teksti/,
which that script writes.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'glosaro'
SITE = 'https://ido.help/tabeli/'

BOLD = re.compile(r'\*\*(.+?)\*\*')

# A SENTENCE BREAK INSIDE A RUN. A full stop followed by a word is the mark
# of two things run together, not of a term that happens to end in a stop.
BREAK = re.compile(r'\.\s+\S')

# What the printing sets AGAINST a term without the term owning it. The
# no-break space is here because the booklet's French sets one before its
# high punctuation, and it survives into the bold.
EDGE = '«»‹›„“”"\'’()[]{}.,;:!?…—–-    '


def term(t):
    """One bold run, with the printing's marks taken off its edges."""
    return re.sub(r'\s+', ' ', t).strip().strip(EDGE).strip()


def terms(run):
    """A bold run as the LIST of terms it holds -- usually one."""
    return [p for p in (term(x) for x in run.split(',')) if p]


def bold(text):
    return BOLD.findall(text or '')


def pair(source, target):
    """The glossary of one language: {ido term: [{t, k}]}, and its reverse.

    Returns the map, the reverse map, and what each guard cost.
    """
    won = {}
    lost = {'nombro': 0, 'listo': 0, 'frazo': 0}
    for key, io_text in source.items():
        a, b = bold(io_text), bold(target.get(key, ''))
        if len(a) != len(b):
            lost['nombro'] += len(a)
            continue
        for x, y in zip(a, b):
            if BREAK.search(x) or BREAK.search(y):
                lost['frazo'] += 1
                continue
            xs, ys = terms(x), terms(y)
            if not xs or len(xs) != len(ys):
                lost['listo'] += 1
                continue
            for p, q in zip(xs, ys):
                got = won.setdefault(p, {})
                got.setdefault(q, [])
                if key not in got[q]:
                    got[q].append(key)

    vorti = {p: [{'t': q, 'k': k} for q, k in sorted(qs.items())]
             for p, qs in sorted(won.items())}

    # THE REVERSE IS THE POINT OF THE EXERCISE, and it carries no keys: the
    # forward map holds them, and a reader who wants the segment goes there.
    back = {}
    for p, qs in won.items():
        for q in qs:
            back.setdefault(q, [])
            if p not in back[q]:
                back[q].append(p)
    inversa = {q: sorted(ps) for q, ps in sorted(back.items())}
    return vorti, inversa, lost


def markdown(code, vorti, inversa):
    """The same glossary flat: the cheapest complete form there is.

    MEASURED on en-GB: 84 kB against 139 kB for the JSON. It drops the
    segment keys -- a reader who wants to check a pair against the printing
    goes to the JSON, which keeps them.
    """
    out = ['<!-- Generated by tools/glosaro.py from tabeli.json and '
           'teksti/. Do not edit. -->', '',
           f'# Glosaro Ido–{code} — Delmas-Tabeli', '',
           'J. Guignon, *Expliko-Libreto di la Delmas-Tabeli helpanta*, '
           'Ido-Kontoro, Thaon-les-Vosges, 1926.', '',
           f'Transskribita de {SITE}', '',
           'La termini grasa dil du texti, parigita per lia rango. '
           'Nula tradukuro esas kompozita hike : omna paro esas du pasaji '
           'dil libro. La klefi dil segmenti esas en '
           f'`{code}.json`.', '',
           f'## Ido → {code}', '']
    out += [f'{p} — {", ".join(q["t"] for q in v)}' for p, v in vorti.items()]
    out += ['', f'## {code} → Ido', '']
    out += [f'{q} — {", ".join(v)}' for q, v in inversa.items()]
    return '\n'.join(out) + '\n'


def main():
    tabeli = json.loads((ROOT / 'tabeli.json').read_text('utf-8'))
    source = {k: v['io'] for k, v in tabeli.items()}
    runs = sum(len(bold(t)) for t in source.values())

    # fr is in tabeli.json, not in teksti/; the other 55 are in teksti/.
    targets = {'fr': {k: v.get('fr', '') for k, v in tabeli.items()}}
    for p in sorted((ROOT / 'teksti').glob('*.json')):
        if p.stem != 'index':
            targets[p.stem] = json.loads(p.read_text('utf-8'))

    OUT.mkdir(exist_ok=True)
    for old in list(OUT.glob('*.json')) + list(OUT.glob('*.md')):
        old.unlink()

    listo = []
    for code, target in sorted(targets.items()):
        vorti, inversa, lost = pair(source, target)
        got = sum(len(v) for v in vorti.values())
        body = {
            'pri': 'Glosaro dil Delmas-Tabeli: la termini grasa, parigita '
                   'per lia rango en la sama rango. La klefi esas ti di '
                   'tabeli.json.',
            'fonto': SITE,
            'kodexo': code,
            'pari': got,
            'perdita': lost,
            'vorti': vorti,
            'inversa': inversa,
        }
        # COMPACT, NOT INDENTED. The whole point of this directory is a
        # cheap fetch, and indent=1 cost 232 kB against 139 kB for the same
        # records -- 40 % of the file was leading spaces.
        text = json.dumps(body, ensure_ascii=False,
                          separators=(',', ':')) + '\n'
        (OUT / f'{code}.json').write_text(text, 'utf-8')
        flat = markdown(code, vorti, inversa)
        (OUT / f'{code}.md').write_text(flat, 'utf-8')
        listo.append({'kodexo': code, 'pari': got,
                      'okteti': len(text.encode('utf-8')),
                      'okteti-md': len(flat.encode('utf-8'))})
        print(f'  {code:9s} {got:5d} pari  '
              f'(perdita: {lost["nombro"]} nombro, {lost["listo"]} listo, '
              f'{lost["frazo"]} frazo)')

    index = {
        'pri': 'La glosari dil Delmas-Tabeli. Singla arkivo donas «vorti», '
               'de Ido a la lingvo, e «inversa», de la lingvo ad Ido.',
        'fonto': SITE,
        'termini grasa en Ido': runs,
        'lingui': listo,
    }
    (OUT / 'index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=1) + '\n', 'utf-8')

    # THE TABLE, so that a crawler finds the 56 files without fetching one.
    # The sizes are printed for the same reason chapitri/index.md prints
    # them: to be chosen between BEFORE anything is downloaded.
    table = ['<!-- Generated by tools/glosaro.py from tabeli.json and '
             'teksti/. Do not edit. -->', '',
             '# Glosaro — Delmas-Tabeli', '',
             'J. Guignon, *Expliko-Libreto di la Delmas-Tabeli helpanta*, '
             'Ido-Kontoro, Thaon-les-Vosges, 1926.', '',
             f'Transskribita de {SITE}', '',
             f'La {runs} termini grasa dil texto Idala, parigita kun lia '
             'ekivalanto en singla altra lingvo per lia rango en la sama '
             'segmento. Nula tradukuro esas kompozita hike : omna paro '
             'esas du pasaji dil libro.', '',
             'La `.md` donas la du direcioni, plata. La `.json` adjuntas '
             'la klefi dil segmenti, por ke on povez verifikar singla paro '
             'en la libro.', '',
             '| lingvo | pari | .md | .json |',
             '| --- | ---: | ---: | ---: |']
    for r in listo:
        c = r['kodexo']
        table.append(f'| {c} | {r["pari"]} | [{c}.md]({c}.md) — '
                     f'{r["okteti-md"] // 1024} Ko | [{c}.json]({c}.json) — '
                     f'{r["okteti"] // 1024} Ko |')
    (OUT / 'index.md').write_text('\n'.join(table) + '\n', 'utf-8')

    best = max(listo, key=lambda r: r['pari'])
    print(f'\n{len(listo)} lingui, de {runs} termini grasa en Ido.')
    print(f'La maxim kompleta: {best["kodexo"]}, {best["pari"]} pari.')


if __name__ == '__main__':
    main()
