#!/bin/sh
# ===================================================================
#  telesargo.sh — aller chercher les planches d'origine chez Gallica.
#
#  A LANCER SUR TA MACHINE, non ici : la politique de sortie de
#  l'environnement de travail refuse gallica.bnf.fr (403 sur le
#  CONNECT), et un refus de politique se signale, il ne se contourne
#  pas. Le script depose les fichiers dans originali/, ou les outils
#  vont les prendre.
#
#  LES FOLIOS. L'album numerise porte les seize planches et, en regard
#  de chacune, sa page de vocabulaire — la liste numerotee en six
#  langues, qui est un temoin independant de ce qu'on a releve. Le PDF
#  de service en donne quarante pages ; le folio se deduit du numero de
#  page par un decalage de 128, verifie sur la planche 1 (page 5,
#  folio 133). Le script ecrit la correspondance en clair : verifie le
#  premier fichier avant de tirer les trente et un autres.
#
#  DEUX FIGURES NE SONT PAS SUR LES PLANCHES mais sur les pages de
#  vocabulaire : le plan de la maison (tableau 5) et la figure du corps
#  humain (tableau 2). Le vocabulaire n'est donc pas un supplement.
# ===================================================================

ARK=https://gallica.bnf.fr/iiif/ark:/12148/bpt6k3410724n
DEST=${1:-originali}
mkdir -p "$DEST"

# tabelo  planche  vocabulaire
for L in "01 133 132" "02 135 134" "03 137 136" "04 139 138" \
         "05 141 140" "06 143 142" "07 149 148" "08 151 150" \
         "09 153 152" "10 155 154" "11 157 156" "12 159 158" \
         "13 161 160" "14 163 162" "15 165 164" "16 167 166"; do
  T=$(echo "$L" | cut -d' ' -f1)
  FP=$(echo "$L" | cut -d' ' -f2)
  FV=$(echo "$L" | cut -d' ' -f3)
  for PAIRE in "t$T:$FP" "v$T:$FV"; do
    NOM=${PAIRE%%:*}
    FOL=${PAIRE##*:}
    if [ -s "$DEST/$NOM.jpg" ]; then
      echo "  $NOM.jpg deja la"
      continue
    fi
    echo "  $NOM.jpg  <-  f$FOL"
    curl -sS --fail -o "$DEST/$NOM.jpg" \
      "$ARK/f$FOL/full/full/0/native.jpg" || echo "  ECHEC sur f$FOL"
    sleep 2                      # on ne bouscule pas la Bibliotheque
  done
done
