# Delmas-Tabeli — transcription LaTeX et page de lecture bilingue

Transcription diplomatique de deux livrets jumeaux :

* **`Expliko-Libreto di la Delmas-Tabeli helpanta`**, J. Guignon,
  Ido-akademiano, Ido-Kontoro, Thaon-les-Vosges (Vosges, France) ;
  imprimerie des Tableaux Auxiliaires Delmas, 6 place Saint-Christoly,
  Bordeaux, **1926**. 116 feuillets numérisés, 112 folios imprimés.
* **`Livret explicatif des Tableaux Auxiliaires Delmas`**, E. Rochelle,
  professeur au lycée de Bordeaux ; G. Delmas, imprimeur-éditeur,
  10 rue Saint-Christoly, Bordeaux. 96 feuillets numérisés, 88 folios
  imprimés plus la table des matières.

Les deux ouvrages sont dans le domaine public. Le livret ido est la
version idiste du livret français : même découpage en **16 tableaux**,
même numérotation d'alinéas, mêmes renvois chiffrés aux objets des
tableaux muraux.

Objectif, comme pour le *Kompleta Gramatiko* : **une ligne du
fac-similé = une ligne du PDF**, même pagination, mêmes folios, mêmes
coupures de mot. Et, en plus ici : **une page de lecture à deux
colonnes**, l'ido à gauche, une autre langue à droite, appariées alinéa
par alinéa.

---

## 1. État d'avancement

| Étape | État |
|---|---|
| Découpage des scans en feuillets | fait (116 + 96 ; les deux PDF sont déjà en pages simples) |
| Relevé de géométrie (`outils/inventaire.py`) | fait sur les 212 feuillets |
| Calibration (`outils/kalibro.py`) | faite ; corps mesuré par la chasse (§ 4) |
| Transcription ido | **les 16 tableaux** (feuillets 7 à 108) ; reste : liminaires et table |
| Transcription française | **les 16 tableaux** (feuillets 9 à 92) ; reste : l'*Avertissement* et la table |
| Page de lecture (`index.html`) | faite, complète pour ce qui est transcrit |
| Traduction anglaise (`texto/en/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction espagnole (`texto/es/`) | **les 16 tableaux**, faite en 2026 d'après l'ido, contrôlée sur le français et l'anglais |
| Traduction russe (`texto/ru/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction chinoise (`texto/zh/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction arabe (`texto/ar/`) | **les 16 tableaux**, faite en 2026 d'après l'ido ; colonne de droite à gauche |
| Les 16 tableaux muraux | **absents** — voir § 7 |
| Contrôles automatiques | huit contrôles (`outils/controles.py`) |

Le projet compile en permanence :

    make -f tab.mk           # tabeli.pdf, tableaux.pdf, index.html

Le fichier de compilation s'appelle `tab.mk` et non `Makefile` : le pont
vers le disque refuse d'écrire un fichier portant ce dernier nom.

---

## 2. Les deux fac-similés

**Ils ne sont pas de même nature, et cela commande tout le reste.**

`Expliko-Libreto.pdf` — 116 pages, images JPEG en niveaux de gris,
passage au scanner : le cadrage est constant d'une page à l'autre, la
justification mesure 1456 px sur toutes les pages pleines (écart-type
faible une fois les pages d'apparat écartées). C'est un fac-similé
qu'on peut mesurer.

`Livret explicatif.pdf` — 96 pages, **prise de vue** : chaque feuillet
a été photographié séparément, le livre était gondolé, l'éclairage
inégal. La justification du même bloc imprimé y mesure de **990 à
1550 px** selon la page. Une mesure prise sur une page ne vaut donc
que pour elle. Toute mesure globale sur ce fac-similé doit d'abord
**normaliser chaque page sur sa propre largeur de bloc** ; c'est ce que
devra faire le contrôle 11.

Correspondance, vérifiée par lecture directe des folios :

    folio imprimé = numéro de feuillet − 2      (dans les DEUX livrets)

Feuillets : `skan/io/f-001.jpg` … `f-116.jpg`, `skan/fr/f-001.jpg` …
`f-096.jpg`. Ils ne sont pas versionnés (170 Mo) ; ils se régénèrent
depuis les deux PDF d'origine :

    pdftoppm -jpeg -r 300 Expliko-Libreto.pdf   skan/io/f
    pdfimages -j "Livret explicatif.pdf"        skan/fr/f   # puis renumérotation en base 1

---

## 3. Structure des deux livrets

Chaque tableau se compose ainsi :

    TABELO N° n            /  TABLEAU N° n
      titre du tableau
      Deskripto generala.  /  I. Description générale.
        alinéas 1 … 8
      Detaloza deskripto.  /  II. Description détaillée.
        alinéas 9 … 19

**L'édition ido ajoute des intertitres que le français ne connaît
pas** : au tableau 1, `La ludo-korto`, `La bona lernanti`, `La mala
lernanti`, `Desegno e muziko`, `La doceyo pri la cienci`. Guignon
découpe en sections un texte que Rochelle laisse courir. Elle ajoute
aussi une note de bas de page sur la latinisation des prénoms, absente
du français.

Ces écarts sont **réels** et la page de lecture les montre : la case
d'en face reste vide plutôt que de recevoir un texte déplacé pour faire
joli. C'est le seul rendu honnête d'une édition qui n'est pas une
traduction ligne à ligne.

Table des 16 tableaux (d'après la table des matières française) :

| n° | français | folio fr |
|---|---|---|
| 1 | L'École. — Le Lycée. — La Classe | 7 |
| 2 | Le Corps humain. — La Récréation. — Les Jeux | 12 |
| 3 | L'Enfance (Un Baptême au village) ; La Jeunesse (Une Fête publique) | 17 ; 20 |
| 4 | L'Âge mûr (Le Repas de noce) ; La Vieillesse (L'Anniversaire) | 23 ; 26 |
| 5 | La Maison et sa construction | 29 |
| 6 | La Maison intérieure. — Les Meubles | 35 |
| 7 | Le Village (en hiver) ; La Maison rustique (au printemps) | 43 ; 46 |
| 8 | La Moisson (en été) ; La Vendange (en automne) | 49 ; 51 |
| 9 | La Montagne. — La Ville d'eaux ; La Forêt. — La Chasse | 54 ; 57 |
| 10 | La Mer. — Le Port | 60 |
| 11 | La Ville et ses monuments. — Un incendie | 65 |
| 12 | La Gare. — Les Chemins de fer | 69 |
| 13 | L'Hôtel. — Le Restaurant. — Le Café | 73 |
| 14 | La Rue. — Les Commerçants | 76 |
| 15 | Le Marché. — Les Comestibles | 82 |
| 16 | Un Grand Magasin. — Les Jouets | 86 |

---

## 4. Calibration — trois instruments, dont un seul tient

`outils/inventaire.py` relève, feuillet par feuillet : boîte d'encre,
lignes de base, pas des lignes. `outils/kalibro.py` en tire les
constantes du préambule.

### L'échelle : une notice de bibliothèque

Les deux fac-similés sont des prises de vue ; rien dans l'image ne dit
combien de pixels font un millimètre. La notice HathiTrust du *Livret
explicatif* (20ᵉ éd., G. Delmas, 1916) porte **« 90 p., 2 l. 18 cm. »** :
la hauteur du papier est donc **180 mm**, mesure de bibliothèque et non
hypothèse. `kalibro.py` prend l'échelle sur la hauteur, ce que donnent
toutes les notices, et non sur la largeur, qu'aucune ne donne.

Le livret ido n'a pas de notice trouvée. On lui applique la même
hauteur : même presse — « Imprimerie des Tableaux Auxiliaires Delmas,
6 place Saint-Christoly » — et les deux éditions se vendaient ensemble.
C'est une inférence, pas une mesure. Elle donne un papier de
**104,6 × 180 mm** pour l'ido, **109,1 × 180 mm** pour le français : le
second tombe pile sur un in-16 courant, ce qui est rassurant.

### Le corps : le rapport 1,20 était faux

Le corps était d'abord déduit du pas des lignes par le rapport d'usage
`corps = pas / 1,20`. Résultat à la compilation : **294 lignes trop
courtes sur 100 pages** pour l'ido, **1179 sur 84** pour le français —
une ligne sur trois n'atteignait pas la marge, et TeX écartait les mots
pour combler. Un rapport n'est pas une mesure.

Deuxième instrument, `outils/altox.py` : la **hauteur d'x**, mesurée du
plateau de densité de chaque ligne. Elle réclamait 12,8 pt pour l'ido —
sous un interlignage de 11,68 pt, c'est-à-dire un interlignage négatif.
Impossible. Mesurer ma propre composition avec le même code n'annule
pas le biais : le fac-similé est de l'encre sur du papier, elle s'étale,
le grain et le JPEG épaississent, et le plateau est lu deux à trois
pixels trop haut de chaque côté — les 18 % d'écart constatés.
**L'outil est conservé, et son verdict aussi : il dit ce qu'il mesure et
pourquoi on ne le suit pas.**

Troisième instrument, celui qu'on retient : `outils/chaso.py`. Il
n'existe que parce que le relevé est diplomatique. **On possède le texte
exact de chaque ligne du fac-similé.** Le bon corps est donc celui pour
lequel ces lignes-là, dans la justification mesurée, remplissent leur
mesure comme elles la remplissent sur le papier. On balaie, on compile,
on compte :

| corps | ido : courtes / longues | | corps | français : courtes / longues |
|---|---|---|---|---|
| 9,73 | 294 / 0 | | 8,90 | 1179 / 0 |
| 10,33 | 48 / 0 | | 9,80 | 261 / 0 |
| **10,93** | **21 / 0** | | **10,70** | **41 / 1** |
| 11,23 | 20 / 1 | | 10,85 | 23 / 11 |
| 11,53 | 18 / 24 | | 11,30 | 13 / 113 |

Le minimum est net des deux côtés : 21 lignes lâches sur ~3 700 pour
l'ido (0,6 %), 42 sur ~3 400 pour le français (1,2 %), et aucune ligne
qui déborde côté ido. Ce n'est pas un réglage à l'œil : c'est une mesure
prise sur plusieurs milliers de lignes dont le fac-similé est l'étalon.

Les corps retenus, **10,93 pt sur 11,68 pt** (ido) et **10,70 pt sur
10,68 pt** (français), donnent un interlignage presque nul — composition
« au fer », normale pour un livret bon marché de cette époque, et très
loin du 1,20 qu'on avait supposé.

### Ce qui reste faux, et pourquoi on le sait

Le **contrôle 6** signale que la boîte d'encre du fac-similé français
couvre **96,5 % de la hauteur de l'image**, contre 83,7 % pour l'ido.
Un livre imprimé a des marges : ce chiffre ne dit pas que le français
n'en a pas, il dit que **le cadre de la prise de vue tombe à l'intérieur
du papier**. La hauteur d'image ne vaut donc pas la hauteur du papier,
et l'échelle qu'on en tire est fausse de quelques pour cent.

Ce que cela abîme, et ce que cela n'abîme pas :

* les **rapports internes** — pas sur justification, hauteur d'x sur
  justification, corps trouvé par la chasse — sont pris dans l'image et
  ne dépendent d'aucune échelle : ils sont justes ;
* seule **l'échelle d'ensemble** du volume français est incertaine. La
  page composée est juste de forme et approximative de taille.

> **À FAIRE, et cela prend trente secondes :** poser une règle sur les
> deux exemplaires, mesurer la hauteur du papier, puis
>
>     python3 outils/kalibro.py io <mm>
>     python3 outils/kalibro.py fr <mm>
>     python3 outils/chaso.py io && python3 outils/chaso.py fr

## 5. Le relevé LaTeX

Fichiers dans `texto/io/` et `texto/fr/`. Deux marques portent tout :

    \nl     fin de ligne SANS trait d'union
    \cc     fin de ligne AVEC trait d'union (le trait est composé)

On n'utilise jamais `\\` : il annule la justification de la ligne.
Aucune césure n'est décidée par TeX ; toutes sont relevées sur le scan.

**Une traduction n'est pas un relevé.** `texto/en/` contient les mêmes
clés `%%K`, le même apparat macro pour macro et les mêmes renvois
`\textsuperscript{(n)}` — ce sont eux qui ouvrent les gros plans, et un
numéro déplacé ouvrirait sur autre chose. Mais elle ne porte ni `\nl`
ni `\cc`, qui n'ont de sens que pour un fac-similé, ni
`\begin{VUpage}`, puisqu'elle n'a ni feuillet ni folio. Elle traduit
l'**ido**, que porte la colonne de gauche, en contrôlant sur le
français ; là où l'ido subdivise et pas le français, elle subdivise
aussi.

**La source est de 1926 ; la traduction est de 2026.** Ce sont deux
dates, et la seconde n'est pas négociable : une colonne doit se lire
comme si un être humain l'avait écrite cette année-ci. Le monde décrit,
lui, reste celui du livret — on ne modernise pas le lycée, le pion ni la
diligence ; on modernise la **langue**, jamais les choses. Trois fautes
en découlent, et il faut les traquer une par une :

1. **La tournure vieillie.** Le « for » explicatif anglais — *his
   satchel is torn, for he is very careless* — que plus personne
   n'écrit ; le « shall » de futur ; le « one » impersonnel ; « Nor do
   I care for… » ; « so kind a daughter-in-law » pour « such a kind
   daughter-in-law ». Elles ne sont pas fausses : elles sont datées, et
   c'est pire, parce qu'elles font croire que la traduction est
   d'époque.

2. **Le calque de la source.** « here is the milkwoman » pour *voici la
   laitière*, « to take advantage of his mother being busy » pour *il
   profite de ce que sa mère est occupée*, « they serve us to digest »
   pour *ils nous servent à digérer*. La phrase est grammaticale et
   n'est d'aucune langue.

3. **La contraction absente.** Dans un dialogue — le tableau 5 en est
   plein — un enfant de 2026 dit *I can't see him*, non *I cannot see
   him*. L'absence totale de contractions dans une colonne entière est
   la marque la plus sûre d'une traduction faite il y a cent ans, ou
   par une machine.

Le contrôle se fait au balayage, langue par langue, sur une liste de
marques établie pour cette langue-là : `grep` de la tournure suspecte,
puis lecture de chaque occurrence — aucune de ces marques n'est fautive
à tous les coups, et « for instance » n'est pas le « for » explicatif.

**Et une variante régionale est une colonne à part.** Là où deux états
d'une même langue diffèrent et sont l'un et l'autre bien connus —
l'anglais britannique et l'américain, le portugais européen et le
brésilien —, on ne choisit pas : on écrit les deux. Le pendjabi l'a
déjà fait, mais pour l'alphabet et non pour le lexique ; c'est la même
décision, prise pour une autre raison.

**Et un calque n'est pas toujours un mot.** Le fac-similé français met une
espace devant les deux-points, le point-virgule, le point d'exclamation et
le point d'interrogation. C'est le français ; ce n'est presque aucune autre
langue. Cette espace était passée, avec le texte, dans dix colonnes —
néerlandais 51, suédois 51, espéranto 51, finnois 51, interlingua 48,
hindi 56, pendjabi 56 et 56, turc 57, irlandais 2 — et dans aucune des
autres. Un balayage de registre se fait donc sur les **signes** autant que
sur les mots : on ne relit pas un blanc, et c'est pour cela qu'il traverse.
Les deux PDF, eux, gardent la leur : **la source ne bouge pas.**

Les espaces-mots sont rendus insécables : le seul point de coupure légal
d'une ligne est celui que le relevé a placé, et une ligne trop large
devient un « Overfull \hbox » que les contrôles inventorient — la faute
passe du silence au bruit.

Chaque page est composée dans une `minipage` de hauteur fixe : une
retouche dans un alinéa ne peut pas faire migrer du texte vers la page
suivante.

**Les clés `%%K`.** Chaque bloc du relevé porte une ligne

    %%K t01-09-3 p

soit `t<tableau>-<numéro d'alinéa>-<rang dans l'alinéa>` puis le type
(`p` alinéa, `sub` intertitre, `apar` page d'apparat, `noto` note). Un
alinéa coupé par un changement de page porte deux fois la même clé, la
seconde suivie de `suite`.

C'est par ces clés que la page de lecture apparie les deux colonnes.
Elles reprennent **la numérotation d'alinéas de l'auteur**, la seule
chose que les deux éditions partagent : elles n'ont ni la même
pagination, ni le même nombre de lignes, ni le même découpage en
sections.

---

## 6. La page de lecture

`outils/html.py` construit `index.html` à partir des mêmes sources
LaTeX. **Le texte n'est saisi qu'une fois** : le PDF et la page en
sortent tous deux, et il est donc impossible que les deux états du
texte divergent.

### Ce qu'elle porte, et ce qu'elle ne porte pas

**Les seize tableaux, et rien d'autre.** Couverture, dédicace,
PREFACO, AVERTISSEMENT, tables des matières, annonces de l'éditeur :
tout cela est dans les deux PDF, qui reproduisent les volumes entiers,
et reste hors de la page de lecture. Ces pièces ne se répondent pas
d'une édition à l'autre — la préface de Guignon n'est pas
l'avertissement de Rochelle, elle en est même le contraire par le ton —
et les afficher côte à côte donnait deux colonnes qui se regardaient
sans rien avoir à se dire. Le partage se lit sur le nom du fichier :
`00-` les liminaires, `90-` la fin, entre les deux les tableaux.

### Du relevé diplomatique à l'écran

* `\nl` devient une espace ; `\cc` **ne laisse rien** — le mot se
  recolle. C'est la seule manière de rendre le texte cherchable :
  `docochambro` coupé en `doco-chambro` ne se trouverait pas.
* Un mot coupé au milieu d'un passage gras porte deux `\VUgras` ; les
  balises **jointives** se recollent, celles que sépare une espace non.
* Deux appels de renvoi séparés par la coupure — `(9, 11,` et `12)` —
  sont un seul renvoi et se réunissent.
* Le `%` de fin de ligne LaTeX est retiré. Sans cela le texte des notes
  commençait par un pourcent, et leur marqueur d'appel n'était plus
  reconnu.

### Les notes se replient

Au bas d'une page imprimée la note a sa place ; dans une colonne qui
défile, posée entre deux alinéas, elle coupe la lecture. L'appel
devient donc un bouton et la note s'ouvre sous l'alinéa qui la porte,
comme dans la page du *Kompleta Gramatiko*.

L'appariement se fait **par la page et par le marqueur**, les deux : un
`(1)` de note et un `(1)` de renvoi au tableau mural s'écrivent pareil,
seule la page les distingue. Trois cas ont demandé un traitement
propre : deux notes sur une même page portant toutes deux `(*)` se
départagent par l'ordre ; un appel peut se trouver sur la page
précédente, quand l'alinéa est à cheval ; et la note du tableau 8 est
appelée depuis le titre d'une scène, pas depuis un alinéa.

### La synchronisation des deux colonnes

Les clés `%%K` apparient les rangs. Là où une édition coupe en deux ce
que l'autre laisse d'un tenant, le PDF garde chaque édition telle
quelle — il est diplomatique — et la page de lecture recolle les deux
moitiés dans leur colonne, en marquant d'un filet l'endroit où l'autre
édition allait à la ligne. Les rangs restent ainsi parallèles.

Cela ne suffisait pas. Le **tableau 5** est un dialogue sans numéros
d'alinéa imprimés : les deux relevés ont dû compter eux-mêmes, ils
n'ont pas compté pareil, et la page mettait en regard une réplique et
la réponse à la précédente. Vingt-quatre rangs sur les trente et un
mal appariés du volume venaient de là. Les clés françaises du tableau 5
ont été renumérotées sur la numérotation ido, prise comme référence ;
six autres cas isolés (tableaux 1, 2, 6, 7, 9, 11) ont été repris au
fac-similé. Il reste **un** rang mal apparié sur 524 — une *Nota*
pédagogique propre au français.

### Disposition

**Deux panneaux, pas trois.** Le *Kompleta Gramatiko* a un volet droit
pour les mots-clés ; ce livre n'en a pas, et la place qui reste sert
aux deux colonnes de texte. À gauche la table des matières, au centre
les deux colonnes, rien à droite, **et pas de pied de page**.

La table des matières a **trois rangs**, parce que le livre en a trois :
le tableau, la scène, l'intertitre. Les tableaux à plusieurs parties
portent « Unesma ceno » et « Duesma ceno », composés en italique et non
en petites capitales — c'est ce qui les distingue, et c'est au
fac-similé qu'on le lit.

Sous 900 px de largeur, les colonnes s'empilent — l'ido d'abord, la
traduction dessous avec un filet à gauche — et la table devient un
tiroir.

Le sélecteur de langue ne recharge rien **une fois la langue venue** :
elle reste dans la page, et la bascule est instantanée. Le français y
est d'emblée — c'est un fac-similé transcrit, il fait partie de
l'objet ; les traductions, marquées `differita` dans `LANGUES`, vivent
dans `lingui/<kodo>.json` et ne se téléchargent qu'au moment où le
menu les nomme. La page ne porte que leurs cases vides. Mesuré : zéro
requête vers `lingui/` tant qu'on n'a pas choisi English, une seule
ensuite, jamais reprise.

La recherche traverse toutes les langues présentes, et elle porte sur
**les colonnes à la fois** : un mot ido trouve l'alinéa, et sa
traduction reste en face même si elle ne contient pas le mot. Ce qui
arrive en cours de route entre dans la copie non surlignée dont la
recherche repart, puis la relance — sans quoi un mot déjà tapé ne
serait pas surligné dans la langue qui vient d'arriver.

L'infobulle d'un renvoi porte le nom de l'objet **dans la langue de sa
colonne** : « fumeyo » à gauche, « fumoir » au milieu, « smoking
room » à droite. `outils/objekti.py` les relève des trois sources du
même geste — le substantif en gras devant le renvoi — et 1610 objets
sur 1693 sont nommés dans les trois.

Le folio de chaque bloc se pose dans le blanc extérieur de sa colonne
et renvoie à la page correspondante du PDF. Ce n'est pas une
soustraction fixe : le volume ido saute deux feuillets vierges, et les
pages composées sont donc numérotées dans l'ordre, une fois pour
toutes.

## 7. Les 16 tableaux muraux — ce qui manque

Tout le texte des deux livrets renvoie par des chiffres — `(18)`,
`(32)`, `(a)`, `(ab)` — aux objets **numérotés sur les tableaux muraux
Delmas**, seize planches en couleurs de 90 × 120 cm. Sans elles, les
renvois du texte ne mènent nulle part.

Ce qu'on a : **une seule réduction**, en trait, au feuillet 111 du
livret ido — le tableau mural n° 12, « Les Voyages ». Les quinze autres
sont à retrouver.

Une fois les planches en main, le travail est balisé :

1. relever, sur chaque planche, la position de chaque numéro ;
2. en faire une carte cliquable (`<area>` ou SVG en surimpression) ;
3. relier chaque `<sup>(18)</sup>` du texte à sa zone, dans les deux
   sens : cliquer le renvoi éclaire l'objet, survoler l'objet donne le
   mot en ido, en français et dans la langue affichée.

C'est là que « des versions améliorées des tableaux originaux » prend
son sens : un tableau mural dont chaque objet porte son nom dans six
langues, ce que l'imprimé de 1926 ne pouvait pas faire.

---

## 8. Arborescence

    LISEZ-MOI.md
    tab.mk                    compilation
    main-io.tex               -> tabeli.pdf
    main-fr.tex               -> tableaux.pdf
    preambule.tex             macros, communes aux deux volumes
    kalibro-io.tex            mesures du fac-similé ido      (PRODUIT)
    kalibro-fr.tex            mesures du fac-similé français (PRODUIT)
    index.html                page de lecture                (PRODUIT)
    texto/io/10-tabelo-01.tex … 25-tabelo-16.tex
    texto/fr/10-tableau-01.tex … 25-tableau-16.tex
    outils/inventaire.py      relevé de géométrie, feuillet par feuillet
    outils/mesures.py         médianes et échelles possibles
    outils/kalibro.py         écrit kalibro-*.tex
    outils/altox.py           hauteur d'x (mesure écartée, § 4)
    outils/chaso.py           corps par la chasse (mesure retenue, § 4)
    outils/ceni.py            indice de scène dans les clés %%K
    outils/controles.py       les six contrôles
    outils/CONSIGNE-RELEVE.md consigne de transcription
    outils/lekto.py           prépare un feuillet pour la lecture à l'œil
    outils/html.py            écrit index.html
    outils/gabarito.html      gabarit de la page de lecture
    outils/inv-io.json        relevé brut (PRODUIT)
    outils/inv-fr.json        relevé brut (PRODUIT)
    skan/io/, skan/fr/        feuillets (non versionnés)

---

## 9. Les huit contrôles

    python3 outils/controles.py

1. **Pagination** — folio imprimé = feuillet − 2, sur toutes les pages.
2. **Feuillets** — aucun oublié, aucun relevé deux fois. Les deux
   versos vierges du livret ido (48, 76) sont reconnus comme tels.
3. **Appariement** — quelles clés n'existent que d'un côté.
4. **Unicité** — aucune clé posée deux fois dans une même langue.
5. **Coupures** — chaque fin d'alinéa à cheval a sa reprise.
6. **Géométrie** — la boîte d'encre occupe-t-elle une part
   vraisemblable de la page ?
7. **Gras** — les deux colonnes mettent-elles en gras le même nombre de
   passages ? L'une témoigne pour l'autre.
8. **Synchronie** — les deux colonnes d'un rang portent-elles le même
   alinéa ? Une différence de longueur énorme dit que le compteur de
   clés a dérivé.

État actuel : contrôle 8 à 1 rang sur 524 ; contrôle 3 à 10 clés
orphelines sur 572 ; contrôle 6 signale l'échelle du fac-similé
français (§ 4) ; **contrôle 7 à 187 alinéas sur 562**, soit un tiers —
c'est le chantier ouvert.

---

## 10. Prochaines étapes, dans l'ordre

1. **Le gras.** Le contrôle 7 signale 187 alinéas où les deux colonnes
   ne mettent pas en gras le même nombre de passages. Les tableaux 16 et
   5, les deux pires, ont été repris au fac-similé ; quatorze restent.
   Une part des écarts est réelle — « jenio-soldato » contre « soldat du
   génie » ne fait pas le même compte — mais pas toute.
   Outil : `python3 outils/grasdiff.py t08`.
2. **Mesurer à la règle la hauteur du papier** des deux exemplaires
   (§ 4), puis `kalibro.py`, puis `korpo.py`.
3. Traduire le français vers les cinq autres langues de l'ONU :
   ajouter les entrées dans `LANGUES` et `DOSSIER`, en tête de
   `outils/html.py`, et un fichier par langue et par tableau dans
   `texto/<code>/`. Prévoir `dir="rtl"` pour l'arabe.
4. Retrouver les seize tableaux muraux et les rendre cliquables (§ 7).
