#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kalibro.py — ecrit kalibro-io.tex et kalibro-fr.tex a partir de
outils/inv-<langue>.json et d'UNE SEULE constante physique par livret :
la largeur du papier, relevee a la regle sur l'exemplaire.

    python3 outils/kalibro.py io 180      # le livret ido fait 180 mm de haut
    python3 outils/kalibro.py fr 180

POURQUOI UNE CONSTANTE PHYSIQUE. Les deux fac-similes sont des PRISES
DE VUE, non des passages au scanner a plat : le nombre de pixels par
millimetre n'est ecrit nulle part dans le fichier, et la resolution que
declare le PDF (300 dpi pour l'ido, 72 dpi pour le francais) est celle
du rendu, pas celle du papier. Un scan photographie a 40 cm et un scan
photographie a 60 cm donnent le meme nombre de pixels par LIGNE mais
pas le meme nombre par MILLIMETRE.

Tout le reste — justification, hauteur du bloc, pas des lignes, corps —
se deduit de cette seule mesure par une regle de trois, puisque le
rapport de deux longueurs, lui, est dans l'image et ne depend d'aucune
echelle. Se tromper sur la largeur du papier ne deforme donc pas la
page : elle la met a l'echelle, en bloc.

LA MESURE EST LA HAUTEUR, ET NON LA LARGEUR, parce que c'est la
hauteur que donnent les catalogues de bibliotheque : la notice
HathiTrust du « Livret explicatif des tableaux auxiliaires Delmas »
(20e edition, G. Delmas, Bordeaux, 1916) porte « 90 p., 2 l. 18 cm. ».
D'ou 180 mm pour le livret francais, mesure de bibliotheque et non
hypothese.

Pour le livret ido, aucune notice n'a ete trouvee. On lui applique la
meme hauteur : il sort de la meme presse — « Imprimerie des Tableaux
Auxiliaires Delmas, 6 place Saint-Christoly, Bordeaux » — et les deux
editions du meme livret se vendaient ensemble. C'est une inference, pas
une mesure ; une regle posee sur l'exemplaire la confirmera ou la
corrigera, et rien d'autre ne changera alors que l'echelle d'ensemble.
"""
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
MINLIGNES = 35          # pages pleines : celles qui mesurent le pas
MM_PAR_PT = 25.4 / 72.27

LIVRE = {
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


def releve(langue):
    inv = json.loads(
        (RACINE / "outils" / f"inv-{langue}.json").read_text(encoding="utf-8"))
    p = {int(k): v for k, v in inv.items()
         if not v.get("vide") and v.get("lignes", 0) >= MINLIGNES}
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


def ecrire(langue, hauteur_mm):
    r = releve(langue)
    liv = LIVRE[langue]
    # L'ECHELLE SE PREND SUR LA HAUTEUR. Premiere version, elle se
    # prenait sur la largeur, parce que c'est la largeur qui porte la
    # justification ; mais la largeur du papier ne se trouve nulle
    # part, tandis que sa hauteur est dans toutes les notices.
    pxmm = r["page_h"] / hauteur_mm
    papier_mm = r["page_l"] / pxmm

    def mm(px):
        return px / pxmm

    pas_mm = mm(r["pas"])
    pas_pt = pas_mm / MM_PAR_PT
    # Le corps se deduit du pas. L'interlignage courant des impressions
    # de labeur de ce temps vaut 1,20 fois le corps ; le rapport est
    # verifie page par page par le controle 11, qui compare la ligne de
    # base composee a la ligne de base relevee.
    corps_pt = pas_pt / 1.20

    txt = f"""% ===================================================================
%  kalibro-{langue}.tex — TOUTES les mesures du fac-simile « {liv['titre']} ».
%  Fichier PRODUIT par outils/kalibro.py : ne pas le modifier a la main.
%  Une seule constante y est physique — la largeur du papier — et elle
%  est passee en argument. Tout le reste vient de outils/inv-{langue}.json.
%
%  Releve : {r['n']} pages de {MINLIGNES} lignes ou plus.
%    justification  {r['largeur']:.0f} px  (ecart-type {r['largeur_et']:.0f})
%    hauteur bloc   {r['hauteur']:.0f} px
%    pas des lignes {r['pas']:.2f} px  (ecart-type {r['pas_et']:.2f})
%    image de page  {r['page_l']:.0f} x {r['page_h']:.0f} px
%    marge gauche   {r['marge_g']:.0f} px
%    1re ligne a    {r['haut']:.0f} px du bord
%  Echelle retenue : {pxmm:.3f} px/mm, prise sur une hauteur de papier
%  de {hauteur_mm:.0f} mm (notice de bibliotheque) ; la page mesure alors
%  {papier_mm:.1f} mm de large.
% ===================================================================

\\newcommand{{\\VUmarque}}{{{liv['marque']}}}

% 1. GEOMETRIE
\\newcommand{{\\VUpapierLargeur}}{{{papier_mm:.2f}mm}}
\\newcommand{{\\VUpapierHauteur}}{{{mm(r['page_h']):.2f}mm}}
\\newcommand{{\\VUtexteLargeur}}{{{mm(r['largeur']):.2f}mm}}
\\newcommand{{\\VUtexteHauteur}}{{{mm(r['hauteur']):.2f}mm}}
% LE FOLIO EST LA PREMIERE ENCRE DE LA PAGE, LE TEXTE VIENT APRES.
% Premiere version : les deux ordonnees etaient egales, et le folio se
% composait DANS la premiere ligne de texte — « 6 » barrait « esas » au
% folio 6. La mesure de outils/inventaire.py donne le haut du BLOC
% D'ENCRE, c'est-a-dire le folio sur toute page foliotee ; le corps du
% texte commence un rang plus bas. On ajoute donc un pas de ligne, et
% les pages sans folio (ouvertures de tableau) commencent a la meme
% ordonnee que les autres, comme au fac-simile.
\\newcommand{{\\VUmargeSup}}{{{mm(r['haut']) + pas_mm:.2f}mm}}
\\newcommand{{\\VUfolioY}}{{{mm(r['haut']):.2f}mm}}

% 2. CORPS ET INTERLIGNAGE
\\newcommand{{\\VUinterligne}}{{{pas_pt:.2f}pt}}
\\newcommand{{\\VUcorps}}{{{corps_pt:.2f}pt}}
\\newcommand{{\\VUcorpsNote}}{{{corps_pt * 0.77:.2f}pt}}
\\newcommand{{\\VUinterligneNote}}{{{pas_pt * 0.80:.2f}pt}}
% Renfoncement d'alinea : provisoire, a relever (outils/mesures.py).
\\newcommand{{\\VUalinea}}{{{mm(r['largeur']) * 0.05:.2f}mm}}
\\newcommand{{\\VUalineaNote}}{{{mm(r['largeur']) * 0.04:.2f}mm}}
\\newcommand{{\\VUblancAlineaValeur}}{{{pas_pt * 0.19:.2f}pt}}
\\newcommand{{\\VUblancNote}}{{{pas_pt * 0.25:.2f}pt}}
\\newcommand{{\\VUfiletnoteLargeur}}{{{mm(r['largeur']) * 0.27:.2f}mm}}

% 3. ESPACE-MOT
% Largeur proche de celle de la fonte, elasticite large : chaque ligne
% trouve sa mesure sans que TeX ait a couper ailleurs qu'au point releve.
\\newcommand{{\\VUespaceRatio}}{{0.32}}
\\newcommand{{\\VUespaceEtire}}{{0.30}}
\\newcommand{{\\VUespaceSerre}}{{0.14}}

% 4. FONTES
\\newcommand{{\\VUfonte}}{{{liv['fonte']}}}
\\newcommand{{\\VUfonteGras}}{{{liv['gras']}}}
\\newcommand{{\\VUratioGras}}{{0.98}}
"""
    # Le fichier est ecrit tel quel : c'est un produit, pas une source.
    (RACINE / f"kalibro-{langue}.tex").write_text(txt, encoding="utf-8")
    print(f"kalibro-{langue}.tex ecrit  ({pxmm:.3f} px/mm ; "
          f"corps {corps_pt:.2f} pt sur {pas_pt:.2f} pt)")


if __name__ == "__main__":
    langue = sys.argv[1] if len(sys.argv) > 1 else "io"
    papier = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0
    ecrire(langue, papier)
