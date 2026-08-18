#!/bin/sh
# ===================================================================
#  telesargo.sh — aller chercher les planches d'origine chez Gallica.
#
#  A LANCER SUR TA MACHINE, non dans l'environnement de travail : sa
#  politique de sortie refuse gallica.bnf.fr (403 sur le CONNECT), et un
#  refus de politique se signale, il ne se contourne pas.
#
#  GALLICA COMPTE LES REQUETES. A deux secondes d'intervalle elle en
#  laisse passer cinq, puis rend 429 — « trop de requetes » — et s'y
#  tient. On attend donc quinze secondes entre deux planches, et sur un
#  429 on double l'attente a chaque essai : trente, soixante, cent
#  vingt, deux cent quarante. Le fichier deja tire n'est jamais
#  redemande, de sorte qu'on relance le script autant de fois qu'il faut
#  sans rien reprendre.
#
#  ON VERIFIE CE QU'ON RECOIT. Une page d'erreur pese quelques
#  centaines d'octets et ne commence pas par les deux octets d'un JPEG ;
#  elle serait passee pour une planche. Le fichier n'est mis en place
#  qu'apres cette verification.
#
#  LES FOLIOS. L'album porte les seize planches et, en regard de
#  chacune, sa page de vocabulaire — la liste numerotee en six langues,
#  temoin independant de ce qu'on a releve, et ou se trouvent aussi le
#  plan de la maison (tableau 5) et la figure du corps humain
#  (tableau 2), qui ne sont pas sur les planches. Le folio se deduit du
#  numero de page du PDF de service par un decalage de 128, verifie sur
#  la planche 1 (page 5, folio 133).
#
#  USAGE
#      sh outils/telesargo.sh                 # les 32, dans originali/
#      sh outils/telesargo.sh originali tabeli    # les 16 planches d'abord
#      sh outils/telesargo.sh originali vortari   # les 16 vocabulaires
#      sh outils/telesargo.sh originali tout 30   # en patientant plus
# ===================================================================

ARK=https://gallica.bnf.fr/iiif/ark:/12148/bpt6k3410724n
DEST=${1:-originali}
QUOI=${2:-tout}
PAUSO=${3:-15}
mkdir -p "$DEST" || exit 1

MANQUE=""

# Un JPEG commence par 0xFF 0xD8. Une page d'erreur, non.
verifier() {
  [ -s "$1" ] || return 1
  [ "$(od -An -N2 -tx1 "$1" | tr -d ' \n')" = "ffd8" ] || return 1
  # une planche de 400 dpi pese des centaines de kilo-octets ; pas une
  # vignette ni un message d'erreur
  T=$(wc -c < "$1" | tr -d ' ')
  [ "$T" -gt 200000 ] || return 1
  return 0
}

tirar() {
  NOM=$1
  FOL=$2
  if verifier "$DEST/$NOM.jpg"; then
    echo "  $NOM.jpg deja la"
    return 0
  fi
  ATTENDRE=30
  ESSAI=1
  while [ "$ESSAI" -le 5 ]; do
    CODE=$(curl -sS -o "$DEST/.$NOM.part" -w '%{http_code}' \
           -A 'tabeli/1.0 (edition diplomatique ; usage personnel)' \
           "$ARK/f$FOL/full/full/0/native.jpg" 2>/dev/null)
    if [ "$CODE" = "200" ] && verifier "$DEST/.$NOM.part"; then
      mv "$DEST/.$NOM.part" "$DEST/$NOM.jpg"
      echo "  $NOM.jpg  <-  f$FOL  ($(wc -c < "$DEST/$NOM.jpg" | tr -d ' ') octets)"
      return 0
    fi
    rm -f "$DEST/.$NOM.part"
    if [ "$CODE" = "429" ]; then
      echo "  $NOM.jpg : Gallica dit d'attendre — ${ATTENDRE}s (essai $ESSAI)"
    else
      echo "  $NOM.jpg : reponse $CODE — ${ATTENDRE}s (essai $ESSAI)"
    fi
    sleep "$ATTENDRE"
    ATTENDRE=$((ATTENDRE * 2))
    ESSAI=$((ESSAI + 1))
  done
  echo "  $NOM.jpg : ABANDON (f$FOL)"
  MANQUE="$MANQUE $NOM"
  return 1
}

for L in "01 133 132" "02 135 134" "03 137 136" "04 139 138" \
         "05 141 140" "06 143 142" "07 149 148" "08 151 150" \
         "09 153 152" "10 155 154" "11 157 156" "12 159 158" \
         "13 161 160" "14 163 162" "15 165 164" "16 167 166"; do
  T=$(echo "$L" | cut -d' ' -f1)
  FP=$(echo "$L" | cut -d' ' -f2)
  FV=$(echo "$L" | cut -d' ' -f3)
  case "$QUOI" in
    tabeli)  PAIRES="t$T:$FP" ;;
    vortari) PAIRES="v$T:$FV" ;;
    *)       PAIRES="t$T:$FP v$T:$FV" ;;
  esac
  for PAIRE in $PAIRES; do
    NOM=${PAIRE%%:*}
    FOL=${PAIRE##*:}
    DEJA=0
    verifier "$DEST/$NOM.jpg" && DEJA=1
    tirar "$NOM" "$FOL"
    [ "$DEJA" = "1" ] || sleep "$PAUSO"
  done
done

echo
if [ -n "$MANQUE" ]; then
  echo "  manquent encore :$MANQUE"
  echo "  relance le script : ce qui est deja tire ne sera pas redemande."
else
  echo "  tout est la, dans $DEST/"
fi
