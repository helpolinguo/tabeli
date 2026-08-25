#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibrate.py — writes calibrate-io.tex and calibrate-fr.tex from
tools/inventory-<language>.json and ONE SINGLE physical constant per
booklet: the width of the paper, measured with a rule on the copy.

    python3 tools/calibrate.py io 180      # the Ido booklet is 180 mm tall
    python3 tools/calibrate.py fr 180

WHY A PHYSICAL CONSTANT. Both facsimiles are PHOTOGRAPHS, not passes
through a flatbed scanner: the number of pixels per millimetre is written
nowhere in the file, and the resolution the PDF declares (300 dpi for the
Ido, 72 dpi for the French) is that of the rendering, not of the paper. A
scan photographed at 40 cm and one photographed at 60 cm give the same
number of pixels per LINE but not the same number per MILLIMETRE.

All the rest -- measure, height of the block, line pitch, size -- follows
from that single measurement by a rule of three, since the ratio of two
lengths is in the image and depends on no scale. Being wrong about the
width of the paper therefore does not deform the page: it scales it, whole.

THE MEASUREMENT IS THE HEIGHT, AND NOT THE WIDTH, because it is the height
that library catalogues give: the HathiTrust record for the "Livret
explicatif des tableaux auxiliaires Delmas" (20th edition, G. Delmas,
Bordeaux, 1916) reads "90 p., 2 l. 18 cm.". Hence 180 mm for the French
booklet, a library measurement and not a hypothesis.

For the Ido booklet, no record has been found. We apply the same height to
it: it comes from the same press -- "Imprimerie des Tableaux Auxiliaires
Delmas, 6 place Saint-Christoly, Bordeaux" -- and the two editions of the
same booklet were sold together. That is an inference, not a measurement; a
rule laid on the copy will confirm or correct it, and nothing else will
change then but the overall scale.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MIN_LINES = 35          # full pages: those that measure the pitch
MM_PER_PT = 25.4 / 72.27

BOOK = {
    "io": {
        "titre": "Expliko-Libreto di la Delmas-Tabeli helpanta",
        "auteur": "J. Guignon",
        "adresso": "Ido-Kontoro, Thaon-les-Vosges, 1926",
        "marque": "Gilles-Philippe Morin kompris, skanis e direktis "
                  "la transskribo di ca libro.",
        "fonte": "XCharter-TLF",
        "gras": "ntxtlf",
    },
    "fr": {
        "titre": "Livret explicatif des Tableaux Auxiliaires Delmas",
        "auteur": "E. Rochelle",
        "adresso": "G. Delmas, Bordeaux",
        "marque": "Gilles-Philippe Morin a concu, numerise et dirige "
                  "la transcription de ce livre.",
        "fonte": "XCharter-TLF",
        "gras": "ntxtlf",
    },
}


def survey(lang):
    inv = json.loads(
        (ROOT / "tools" / f"inv-{lang}.json").read_text(encoding="utf-8"))
    p = {int(k): v for k, v in inv.items()
         if not v.get("vide") and v.get("lignes", 0) >= MIN_LINES}
    L = np.array([v["largeur"] for v in p.values()], float)
    H = np.array([v["hauteur"] for v in p.values()], float)
    P = np.array([v["pas"] for v in p.values() if v.get("pas")], float)
    W = np.array([v["px"][0] for v in p.values()], float)
    PH = np.array([v["px"][1] for v in p.values()], float)
    G = np.array([v["bloc"][0] for v in p.values()], float)
    Y0 = np.array([v["bloc"][1] for v in p.values()], float)
    return {
        "n": len(p),
        "largeur": float(np.median(L)), "largeur_et": float(np.std(L)),
        "hauteur": float(np.median(H)),
        "pas": float(np.median(P)), "pas_et": float(np.std(P)),
        "page_l": float(np.median(W)), "page_h": float(np.median(PH)),
        "marge_g": float(np.median(G)), "haut": float(np.median(Y0)),
    }


def write_(lang, height_mm):
    r = survey(lang)
    bk = BOOK[lang]
    # THE SCALE IS TAKEN FROM THE HEIGHT. In the first version it was taken
    # from the width, because it is the width that carries the measure; but
    # the width of the paper is nowhere to be found, whereas its height is in
    # every record.
    pxmm = r["page_h"] / height_mm
    paper_mm = r["page_l"] / pxmm

    def mm(px):
        return px / pxmm

    step_mm = mm(r["pas"])
    step_pt = step_mm / MM_PER_PT
    # The size follows from the pitch. The current leading of the bookwork
    # printing of that period is 1.20 times the size; the ratio is verified
    # page by page by check 11, which compares the composed baseline with the
    # surveyed baseline.
    size_pt = step_pt / 1.20

    txt = f"""% ===================================================================
%  kalibro-{lang}.tex — TOUTES les mesures du fac-simile « {bk['titre']} ».
%  Fichier PRODUIT par tools/kalibro.py : ne pas le modifier a la main.
%  Une seule constante y est physique — la largeur du papier — et elle
%  est passee en argument. Tout le reste vient de tools/inv-{lang}.json.
%
%  Releve : {r['n']} pages de {MIN_LINES} lignes ou plus.
%    justification  {r['largeur']:.0f} px  (ecart-type {r['largeur_et']:.0f})
%    hauteur bloc   {r['hauteur']:.0f} px
%    pas des lignes {r['pas']:.2f} px  (ecart-type {r['pas_et']:.2f})
%    image de page  {r['page_l']:.0f} x {r['page_h']:.0f} px
%    marge gauche   {r['marge_g']:.0f} px
%    1re ligne a    {r['haut']:.0f} px du bord
%  Echelle retenue : {pxmm:.3f} px/mm, prise sur une hauteur de papier
%  de {height_mm:.0f} mm (notice de bibliotheque) ; la page mesure alors
%  {paper_mm:.1f} mm de large.
% ===================================================================

\\newcommand{{\\VUmarque}}{{{bk['marque']}}}

% 1. GEOMETRIE
\\newcommand{{\\VUpapierLargeur}}{{{paper_mm:.2f}mm}}
\\newcommand{{\\VUpapierHauteur}}{{{mm(r['page_h']):.2f}mm}}
\\newcommand{{\\VUtexteLargeur}}{{{mm(r['largeur']):.2f}mm}}
\\newcommand{{\\VUtexteHauteur}}{{{mm(r['hauteur']):.2f}mm}}
% LE FOLIO EST LA PREMIERE ENCRE DE LA PAGE, LE TEXTE VIENT APRES.
% Premiere version : les deux ordonnees etaient egales, et le folio se
% composait DANS la premiere ligne de texte — « 6 » barrait « esas » au
% folio 6. La mesure de tools/inventaire.py donne le haut du BLOC
% D'ENCRE, c'est-a-dire le folio sur toute page foliotee ; le corps du
% texte commence un rang plus bas. On ajoute donc un pas de ligne, et
% les pages sans folio (ouvertures de tableau) commencent a la meme
% ordonnee que les autres, comme au fac-simile.
\\newcommand{{\\VUmargeSup}}{{{mm(r['haut']) + step_mm:.2f}mm}}
\\newcommand{{\\VUfolioY}}{{{mm(r['haut']):.2f}mm}}

% 2. CORPS ET INTERLIGNAGE
\\newcommand{{\\VUinterligne}}{{{step_pt:.2f}pt}}
\\newcommand{{\\VUcorps}}{{{size_pt:.2f}pt}}
\\newcommand{{\\VUcorpsNote}}{{{size_pt * 0.77:.2f}pt}}
\\newcommand{{\\VUinterligneNote}}{{{step_pt * 0.80:.2f}pt}}
% Renfoncement d'alinea : provisoire, a relever (tools/mesures.py).
\\newcommand{{\\VUalinea}}{{{mm(r['largeur']) * 0.05:.2f}mm}}
\\newcommand{{\\VUalineaNote}}{{{mm(r['largeur']) * 0.04:.2f}mm}}
\\newcommand{{\\VUblancAlineaValeur}}{{{step_pt * 0.19:.2f}pt}}
\\newcommand{{\\VUblancNote}}{{{step_pt * 0.25:.2f}pt}}
\\newcommand{{\\VUfiletnoteLargeur}}{{{mm(r['largeur']) * 0.27:.2f}mm}}

% 3. ESPACE-MOT
% Largeur proche de celle de la fonte, elasticite large : chaque ligne
% trouve sa mesure sans que TeX ait a couper ailleurs qu'au point releve.
\\newcommand{{\\VUespaceRatio}}{{0.32}}
\\newcommand{{\\VUespaceEtire}}{{0.30}}
\\newcommand{{\\VUespaceSerre}}{{0.14}}

% 4. FONTES
\\newcommand{{\\VUfonte}}{{{bk['fonte']}}}
\\newcommand{{\\VUfonteGras}}{{{bk['gras']}}}
\\newcommand{{\\VUratioGras}}{{0.98}}
"""
    # The file is written as it stands: it is a product, not a source.
    (ROOT / f"kalibro-{lang}.tex").write_text(txt, encoding="utf-8")
    print(f"kalibro-{lang}.tex ecrit  ({pxmm:.3f} px/mm ; "
          f"corps {size_pt:.2f} pt sur {step_pt:.2f} pt)")


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "io"
    paper = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0
    write_(lang, paper)
