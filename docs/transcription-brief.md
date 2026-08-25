# Consigne de relevé — transcription diplomatique

À lire intégralement avant de relever un seul feuillet.

## 0. Ce qu'on fait

On transcrit **ligne à ligne** un livret imprimé en 1926, à partir de
son fac-similé. La règle unique :

> **UNE LIGNE DU FAC-SIMILÉ = UNE LIGNE DU PDF.**

Le texte n'est pas remis en forme, pas modernisé, pas corrigé. Les
coquilles de l'imprimeur sont conservées. On ne « comprend » pas le
texte pour le récrire : on le **relève**.

## 1. Préparer les images

    python3 outils/lekto.py io 13 18 --moitie
    python3 outils/lekto.py fr 14 18 --moitie

produit `outils/.lekto/io-013a.png` (haut de page) et `io-013b.png`
(bas de page), avec deux lignes de recouvrement entre les deux. Les
lire avec l'outil `Read`, une image à la fois, et transcrire au fur et
à mesure. **Ne jamais transcrire de mémoire ni par déduction : chaque
ligne doit avoir été vue.**

Si une image est illisible, la regénérer plus grande :

    python3 -c "import sys; sys.path.insert(0,'outils'); \
      from lekto import prepare; print(prepare('io', 13, True, 2200))"

## 2. Les deux marques de coupure

À la fin de chaque ligne du fac-similé, sauf la dernière d'un alinéa :

| marque | quand | rend |
|---|---|---|
| `\nl` | la ligne finit sur un mot entier | rien de visible |
| `\cc` | la ligne finit sur un mot **coupé** | le trait d'union |

Le trait d'union d'une coupure **ne s'écrit pas** : `\cc` le compose.
Écrire `ler\cc nanti` et non `ler-\cc nanti`.

On n'utilise **jamais** `\\`.

La dernière ligne d'un alinéa ne porte aucune marque — sauf si
l'alinéa continue sur la page suivante : elle porte alors `\parplein`
sur sa propre ligne, et la reprise commence par `\VUcontinue`.

## 3. Les enrichissements

| fac-similé | source |
|---|---|
| gras (demi-gras étroit) | `\VUgras{...}` |
| italique | `\textit{...}` |
| renvoi entre parenthèses en exposant, ex. `⁽¹⁸⁾` | `\textsuperscript{(18)}` |
| petites capitales d'intertitre | voir § 4 |

**Un mot coupé au milieu d'un passage gras porte deux `\VUgras`**, un
par ligne :

    ar\cc
    moro

devient

    \VUgras{ar}\cc
    \VUgras{moro}

Respecter **exactement** l'étendue du gras : dans « la **nigra tabelo**
(1) », le renvoi n'est pas gras ; dans « **liceo.** », le point l'est.
Regarder, ne pas supposer.

Attention à l'espace **avant** le renvoi : le livret ido met le plus
souvent une espace (`\VUgras{tabli} \textsuperscript{(18)}`), le livret
français le plus souvent pas (`\VUgras{tables}\textsuperscript{(18)}`).
Suivre le fac-similé page par page.

## 4. Les rangs de titre

    \VUpk{10.2pt}{40}{Deskripto generala.}      intertitre en petites
                                                capitales, centré
    \VUtitre{15.0pt}{60}{TABELO N\textsuperscript{o} 2}   titre de tableau
    \VUcentre{13.2pt}{90}{DUESMA SERIO}         ligne d'apparat
    \VUfilet{20mm}                              filet centré
    \VUornamento{9pt}                           fleuron
    \VUsaut{3.0mm}                              blanc vertical

Les corps et interlettrages passés en argument sont **provisoires** :
reprendre ceux du tableau 1 (`texto/io/10-tabelo-01.tex`) plutôt que
d'en inventer. Ils seront relevés plus tard par `outils/apparat.py`.

## 5. La structure de page

    \begin{VUpage}[13]{11}
    ...
    \end{VUpage}

`[13]` = numéro de **feuillet** du scan ; `{11}` = **folio imprimé**,
laissé vide `{}` si la page n'en porte pas (ouverture de tableau).

Rappel : **folio imprimé = numéro de feuillet − 2**, dans les deux
livrets.

Entre deux alinéas, écrire `\VUblancAlinea` avant le premier mot.

### Notes de bas de page

    \VUnotes{143.2mm}{%
    (*) Por la \textit{baptonomi} on konsilas anke transskribar li\nl
    segun la formo Latina.%
    }

Elles se déclarent **en tête de page**, juste après `\begin{VUpage}`,
quelle que soit leur place réelle : elles sont posées à une ordonnée
absolue, en hauteur nulle. L'ordonnée est provisoire — mettre
`143.2mm` si la note est en bas d'une page pleine.

## 6. Les clés d'appariement `%%K`

**C'est la partie la plus importante et la plus facile à rater.**

Avant chaque bloc de texte, une ligne :

    %%K t02-09-3 p

* `t02` — numéro du tableau, sur deux chiffres.
* `09` — **le numéro d'alinéa imprimé par l'auteur** (`9. —`), sur
  deux chiffres. Les blocs qui ne portent pas de numéro (les alinéas
  qui suivent, sans chiffre) gardent celui de l'alinéa numéroté qui les
  précède.
* `3` — rang du bloc **à l'intérieur** de cet alinéa numéroté : `1`
  pour celui qui porte le chiffre, `2` pour le suivant, etc.
* `p` — le type : `p` alinéa courant, `sub` intertitre, `apar` page
  d'apparat (ouverture de tableau), `noto` note.

Les intertitres et les pages d'apparat se numérotent à part :
`t02-tit-1`, `t02-tit-2`, … dans l'ordre, et `t02-apar-1`.

### Les scènes : ne t'en occupe pas

Plusieurs tableaux sont découpés en scènes (« Unesma ceno », « Duesma
ceno »), et **l'auteur remet la numérotation des alinéas à 1 à chaque
scène**. La même clé `t04-01-1` désigne alors deux alinéas différents.

**Ce n'est pas ton problème.** Note ce que tu vois : l'imprimé porte
« 1. — », tu écris `01`. Une passe déterministe (`outils/ceni.py`),
appliquée après coup et à l'identique aux deux langues, insère l'indice
de scène (`t04-c2-01-1`) en détectant la décroissance du numéro. Si tu
le fais toi-même, ta numérotation de scènes et celle de l'autre langue
risquent de diverger, et l'appariement sera faux.

Un alinéa coupé par un changement de page porte **deux fois la même
clé**, la seconde suivie de `suite` :

    %%K t01-13-1 p suite

**Pourquoi cela compte.** Ces clés apparient la colonne ido et la
colonne française dans la page de lecture. Les deux éditions n'ont ni
la même pagination, ni le même nombre de lignes, ni le même découpage
en sections — mais elles numérotent les mêmes alinéas, et c'est le seul
ancrage qu'elles partagent. Une clé fausse fait mentir la mise en
regard.

Si un bloc n'existe que dans une édition (l'ido ajoute des intertitres
que le français ne connaît pas), il garde sa clé et n'aura simplement
pas de vis-à-vis. **Ne jamais forcer une correspondance qui n'existe
pas, ne jamais fusionner deux alinéas pour qu'ils « tombent en
face ».**

## 7. Orthographe et ponctuation

* Écrire les accents en UTF-8 direct (`é`, `à`, `ô`), pas en macros.
* Apostrophe : la saisir droite (`'`) ; la conversion la courbe.
* Tiret cadratin de l'imprimé : `---`. Demi-cadratin : `--`.
* Espace avant `;` `:` `?` `!` : la saisir normalement, une espace.
* Guillemets français du fac-similé : `«~...~»` → écrire simplement
  `« ... »`.
* **Ne pas corriger le texte.** Si l'imprimé porte `et` là où l'ido
  attend `e`, écrire `et`. Si un point manque, ne pas l'ajouter.

## 8. Vérifier avant de rendre

1. Compter les lignes : le nombre de `\nl` + `\cc` + fins d'alinéa
   d'une page doit égaler le nombre de lignes imprimées de cette page.
2. Compiler :

       pdflatex -interaction=nonstopmode -jobname=essai main-io.tex

   **Aucun « Overfull \hbox » ne doit apparaître.** S'il y en a, la
   ligne relevée est trop longue : c'est presque toujours une coupure
   oubliée.
3. Relire les clés `%%K` : suite de numéros d'alinéa sans trou.

## 9. Où écrire

    texto/io/<NN>-tabelo-<NN>.tex        ex. texto/io/11-tabelo-02.tex
    texto/fr/<NN>-tableau-<NN>.tex       ex. texto/fr/11-tableau-02.tex

Le préfixe numérique donne l'ordre d'inclusion : `10` pour le
tableau 1, `11` pour le 2, … `25` pour le 16.

Modèle à imiter dans le détail : `texto/io/10-tabelo-01.tex` et
`texto/fr/10-tableau-01.tex`.
